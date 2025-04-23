import os
import logging

from ._reference import Reference, cross_action, cross_product, element_action
from ._concept import Concept
from typing import Optional, List, Union


class Inference:
    def __init__(
        self, 
        concept_to_infer: Concept,
        perception_concepts: Union[List[Concept], Concept],
        cognition_concept: Concept,
        view: Optional[List[str]] = None,
    ):
        """Initialize an Inference instance with all necessary components.
        
        Args:
            concept_to_infer: The concept to be inferred
            perception_concepts: List of Concept objects for perception
            cognition_concept: Single Concept object for cognition
            view: Optional list of axes to keep in the view
        """
        self.concept_to_infer: Concept = concept_to_infer
        self.agent = None
        self.view = view or []  # Direct list of axes to keep
        self.post_actuation_pre_perception_concepts: List[Concept] = perception_concepts
        self.post_actuation_pre_cognition_concept: Concept = cognition_concept
        self.combined_pre_perception_concept: Optional[Concept] = None

        # Validate perception concept
        if not isinstance(perception_concepts, (list, tuple)):
            perception_concepts = [perception_concepts]

        if not all(isinstance(c, Concept) for c in perception_concepts):
            raise TypeError("All perception inputs must be Concept instances")

    def execute(self, agent, actuation=True, perception_config_to_give=None, cognition_config_to_give=None, shape_view=True):
        from normalign_stereotype.core._agent_frame._agent_main import AgentFrame
        if not isinstance(agent, AgentFrame):
            raise ValueError("Agent must be an instance of AgentFrame")
        """Execute pipeline with direct axis selection and optional custom configuration.
        
        Args:
            agent: AgentFrame instance required for execution
            actuation: Whether to apply actuation to the reference
            perception_config_to_give: Optional custom perception configuration
            cognition_config_to_give: Optional custom cognition configuration
            shape_view: Whether to apply view shaping to the reference
        """
        self.agent = agent  # Set the agent for this execution

        # Combine perception concepts using the utility function
        self.combined_pre_perception_concept = agent.perception_combination(self.post_actuation_pre_perception_concepts, agent)

        perception_ref = agent.perception(self.combined_pre_perception_concept)
        cognition_ref = agent.cognition(self.post_actuation_pre_cognition_concept)

        if agent.debug:
            logging.debug("===========================")
            logging.debug("Now processing inference execution: %s", self)
            logging.debug("     concept to infer %s", self.concept_to_infer.comprehension["name"])
            logging.debug("     perception %s", self.combined_pre_perception_concept.comprehension["name"])
            logging.debug("     cognition %s", self.post_actuation_pre_cognition_concept.comprehension["name"])

            logging.debug("!! cross-actioning references:")
            logging.debug("     cog: %s %s", cognition_ref.axes, cognition_ref.tensor)
            logging.debug("     perc %s %s", perception_ref.axes, perception_ref.tensor)

        self.concept_to_infer.reference = cross_action(
            cognition_ref,
            perception_ref,
            self.concept_to_infer.comprehension["name"]
        )

        if agent.debug:
            logging.debug(" raw_result %s %s", self.concept_to_infer.reference.axes, self.concept_to_infer.reference.tensor)

        if actuation:
            configs = {}
            if perception_config_to_give:
                configs["perception_working_config"] = perception_config_to_give
            if cognition_config_to_give:
                configs["cognition_working_config"] = cognition_config_to_give

            self.concept_to_infer.reference = self.agent.actuation(
                self.concept_to_infer,
                **configs
            )

        if shape_view:
            self.concept_to_infer.reference = self.concept_to_infer.reference.shape_view(self.view)

        return self.concept_to_infer
