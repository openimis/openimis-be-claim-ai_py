from fhir.resources.medication import Medication as MedicationFHIR
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import MedicalProvision
from claim_ai.evaluation.input_models import Medication as MedicationAI


class MedicationConverter(MedicalProvision):
    category = 'item'
    _FHIR_RESOURCE = MedicationFHIR
    _AI_MODEL = MedicationAI

    def _get_context(self, use_context, context_url):
        return next(
            (context.valueUsageContext for context in use_context.extension if context.url == context_url), None
        )

    def _get_codes(self, use_context):
        return [coding.code for coding in use_context.valueCodeableConcept.coding]

    def _get_use_context_ext(self, provided):
        return next((ext for ext in provided.extension if ext.url.endswith('usage-context')), None)

    def _get_frequency(self, fhir_repr):
        return next(
            (ext.valueTiming.repeat.frequency for ext in fhir_repr.extension if ext.url.endswith('frequency')), None
        )
