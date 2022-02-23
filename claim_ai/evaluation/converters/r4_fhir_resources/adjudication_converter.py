from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import AdjudicationBuilderFactory
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders.adjudication_builders import \
    BaseAdjudicationBuilder


class AdjudicationConverter:
    builder_factory = AdjudicationBuilderFactory()

    @classmethod
    def build_claim_response_item_adjudication(cls, evaluation_result, adjudication, sequence=1):
        builder = cls.builder_factory.get_builder(type(evaluation_result).__name__)
        return builder.build_claim_response_item_adjudication(evaluation_result, adjudication, sequence)

    @classmethod
    def build_adjudication(cls, price, quantity, evaluation_result):
        return BaseAdjudicationBuilder().build_adjudication(price, quantity, evaluation_result)
