from fhir.resources.activitydefinition import ActivityDefinition as ActivityDefinitionFHIR
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import MedicalProvision
from claim_ai.evaluation.input_models import ActivityDefinition as ActivityDefinitionAI


class ActivityDefinitionConverter(MedicalProvision):
    category = 'service'
    _FHIR_RESOURCE = ActivityDefinitionFHIR
    _AI_MODEL = ActivityDefinitionAI

    def _get_context(self, use_context, context_url):
        return next((context.valueCodeableConcept for context in use_context
                     if context.code.code.lower() == context_url.lower()), None)

    def _get_codes(self, use_context):
        return [coding.code for coding in use_context.coding]

    def _get_use_context_ext(self, provided):
        return provided.useContext

    def _get_frequency(self, fhir_repr):
        return fhir_repr.timingTiming.repeat.frequency

