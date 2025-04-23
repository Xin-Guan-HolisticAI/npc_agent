import json
import re
import logging
import ast
from string import Template
import copy

# Configure logging
logger = logging.getLogger(__name__)

def _safe_eval(s):
    """Safely evaluate a string representation of a list or other Python literal."""
    try:
        return ast.literal_eval(s)
    except:
        return s

def _format_bullet_points(cn_list, n_list, v_list):
    """Format lists into bullet points."""
    bullets = []
    for cn, n, v in zip(cn_list, n_list, v_list):
        bullets.append(f" - {cn}: {n} (context: {v})")
    return "\n".join(bullets)

def _replace_placeholders_with_values(template, values):
    """Replace numbered placeholders in a template with values."""
    for i, value in enumerate(values, 1):
        template = template.replace(f"{{{i}}}", str(value))
        template = template.replace("_", " ")
    return template

def _clean_parentheses(text):
    """Remove parentheses content then clean up spaces."""
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _prompt_template_dynamic_substitution(
    prompt_template: str | Template,
    template_variable_definition_dict: dict[str, str],
    base_values_dict: dict,
    helper_functions: dict,
    debug: bool = False
) -> str:
    """
    Substitutes only variables that can be resolved with available locals.
    Leaves unresolved variables in the template unchanged.
    
    Args:
        prompt_template: The template string or Template object
        template_variable_definition_dict: Dictionary mapping variable names to code snippets
        base_values_dict: Dictionary of base values available for substitution
        helper_functions: Dictionary of helper functions available for substitution
        debug: If True, prints detailed debug information about the substitution process
    """
    func_name = "_prompt_template_dynamic_substitution"
    substitutions = {}
    
    if debug:
        logger.debug(f"\n{'='*50}")
        logger.debug(f"DEBUG: {func_name}")
        logger.debug(f"{'='*50}")
        logger.debug(f"\n[{func_name}] Template Variables:")
        logger.debug(f"[{func_name}] Base values available: {list(base_values_dict.keys())}")
        logger.debug(f"[{func_name}] Helper functions available: {list(helper_functions.keys())}")
    
    # Convert string to Template if needed
    if isinstance(prompt_template, str):
        template = Template(prompt_template)
        if debug:
            logger.debug(f"\n[{func_name}] Original template string:")
            logger.debug(f"[{func_name}] {prompt_template}")
    else:
        template = prompt_template
        if debug:
            logger.debug(f"\n[{func_name}] Original template object:")
            logger.debug(f"[{func_name}] {template.template}")
    
    # Get all variables present in the template
    template_variables = template.get_identifiers()
    if debug:
        logger.debug(f"\n[{func_name}] Variables found in template:")
        for var in template_variables:
            logger.debug(f"[{func_name}]   - {var}")
    
    for var in template_variables:
        if var not in template_variable_definition_dict:
            if debug:
                logger.debug(f"\n[{func_name}] Skipping {var}: No code snippet defined")
            continue  # No code snippet for this variable
            
        code = template_variable_definition_dict[var]
        if debug:
            logger.debug(f"\n[{func_name}] Processing variable: {var}")
            logger.debug(f"[{func_name}] Code snippet: {code}")
        
        # Create execution environment with both base values and helper functions
        exec_env = copy.deepcopy(base_values_dict)
        exec_env.update(helper_functions)
        
        try:
            # Execute code in isolated environment with helper functions available
            exec(code, {}, exec_env)
            
            # Use the variable name itself as the key
            if var in exec_env:
                substitutions[var] = exec_env[var]
                if debug:
                    logger.debug(f"[{func_name}] Successfully substituted {var} = {exec_env[var]}")
            else:
                if debug:
                    logger.warning(f"[{func_name}] {var} not found in execution environment after code execution")
        except Exception as e:
            if debug:
                logger.error(f"[{func_name}] Error processing {var}: {str(e)}")
            # Skip substitution if any error occurs
            continue
            
    # Use safe_substitute to leave unresolved variables unchanged
    result = template.safe_substitute(substitutions)
    
    if debug:
        logger.debug(f"\n[{func_name}] Final substitutions:")
        for var, value in substitutions.items():
            logger.debug(f"[{func_name}]   {var} = {value}")
        logger.debug(f"\n[{func_name}] Final result:")
        logger.debug(f"[{func_name}] {result}")
        logger.debug(f"\n[{func_name}] {'='*50}")
    
    return result

def _get_default_working_config(concept_type):
    """Get default actuation configuration based on concept type."""
    func_name = "_get_default_working_config"
    logger.debug(f"[{func_name}] Getting default config for concept type: {concept_type}")
    
    perception_config = {
        "mode": "memory_retrieval"
    }
    cognition_config = {}

    default_variable_definition_dict = {
        "cog_n": "cog_n",
        "cog_cn": "cog_cn",
        "cog_cn_classification_base": "cog_cn[:-1]",
        "cog_v": "cog_v",
        "perc_n": "perc_n",
        "perc_cn": "perc_cn",
        "perc_v": "perc_v",
        "perc_cn_n_v_bullets": "cn_list, n_list, v_list = _safe_eval(perc_cn), _safe_eval(perc_n), _safe_eval(perc_v); perc_cn_n_v_bullets = _format_bullet_points(cn_list, n_list, v_list)",
        "cog_n_with_perc_n": "name_elements = _safe_eval(perc_n); cog_n_with_perc_n = _replace_placeholders_with_values(cog_n, name_elements)",
        "cog_v_with_perc_n": "name_elements = _safe_eval(perc_n); cog_v_with_perc_n = _replace_placeholders_with_values(cog_v, name_elements)"
    }

    if concept_type == "?":
        logger.debug(f"[{func_name}] Creating classification prompt template")
        classification_prompt = Template("""Your task is to find instances of "$cog_cn_classification_base" from a specific text about an instance of "$perc_cn".
    
What finding "$cog_cn_classification_base" means: "$cog_v"

**Find from "$perc_cn": "$perc_n"**

(context for "$perc_n": "$perc_v")

Your output should start with some context, reasonings and explanations of the existence of the instance. Your summary key should be an instance of "$cog_n".""")
        
        cognition_config = {
            "mode": "llm_prompt_two_replacement",
            "llm": "structured_llm",
            "prompt_template": classification_prompt,
            "template_variable_definition_dict": default_variable_definition_dict,
        }
        
    elif concept_type == "<>":
        logger.debug(f"[{func_name}] Creating judgement prompt template")
        judgement_prompt = Template("""Your task is to judge if "$cog_n_with_perc_n" is true or false.

What each of the component in "$cog_n_with_perc_n" refers to: 
$perc_cn_n_v_bullets
                            
**Truth conditions to judge if it is true or false that "$cog_n_with_perc_n":** 
    "$cog_v_with_perc_n"

When judging **quote** the specific part of the Truth conditions you mentioned to make the judgement in your output, this is to make sure you are not cheating and the answer is intelligible without the Truth conditions.
                            
Now, judge if "$cog_n_with_perc_n" is true or false based **strictly** on the above Truth conditions, and quote the specific part of the Truth conditions you mentioned to make the judgement in your output.

Your output should be a JSON object with Explanation and Summary_Key fields. The Explanation should contain your reasoning and the specific part of the Truth conditions you mentioned. The Summary_Key should be either "TRUE", "FALSE", or "N/A" (if not applicable).""")

        cognition_config = {
            "mode": "llm_prompt_two_replacement",
            "llm": "bullet_llm",
            "prompt_template": judgement_prompt,
            "template_variable_definition_dict": default_variable_definition_dict
        }

    return perception_config, cognition_config
