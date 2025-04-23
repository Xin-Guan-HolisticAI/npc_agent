from string import Template
from ._utils import (
    _clean_parentheses,
    _safe_eval,
    _format_bullet_points,
    _replace_placeholders_with_values,
    _prompt_template_dynamic_substitution
)
from ._cognition import _recollect_nested

def _cognition_llm_prompt_two_replacement(to_cognitize_name, prompt_template, variable_definitions,
                                            cognitized_llm, memory_location, to_cognitize_concept_name = None, perception_concept_name = None, index_dict=None, recollection=None):
    """Create a cognitized function that processes perceptions using the given template and definitions."""

    memory = eval(open(memory_location).read())

    base_values_dict = {}

    # Get to_cognitize_value with location awareness using nested recollection
    concept_name_list = [to_cognitize_concept_name] if to_cognitize_concept_name else []
    to_cognitize_value = _recollect_nested(memory, to_cognitize_name, concept_name_list, index_dict, recollection)
    if to_cognitize_value is None:
        to_cognitize_value = to_cognitize_name

    def cognitized_func(input_perception):
        perception_name = _clean_parentheses(str(input_perception[0]))
        perception_value = str(input_perception[1])
        
        base_values_dict["cog_v"] = to_cognitize_value
        base_values_dict["cog_n"] = to_cognitize_name
        base_values_dict["cog_cn"] = to_cognitize_concept_name if to_cognitize_concept_name is not None else "cog_cn"
        base_values_dict["perc_cn"] = perception_concept_name if perception_concept_name is not None else "perc_cn"
        base_values_dict["perc_n"] = perception_name
        base_values_dict["perc_v"] = perception_value

        # Define helper functions to pass to template substitution
        helper_functions = {
            '_safe_eval': _safe_eval,
            '_format_bullet_points': _format_bullet_points,
            '_replace_placeholders_with_values': _replace_placeholders_with_values,
            '_clean_parentheses': _clean_parentheses
        }

        cognitized_prompt = _prompt_template_dynamic_substitution(
            prompt_template, 
            variable_definitions, 
            base_values_dict,
            helper_functions
        )

        return eval(cognitized_llm.invoke(cognitized_prompt))

    return cognitized_func 