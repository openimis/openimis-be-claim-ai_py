from claim_ai.evaluation.converters import AiConverter


class FHIRConverter:
    converter = AiConverter()

    def bundle_ai_input(self, claim_bundle):
        claims = [entry['resource'] for entry in claim_bundle['entry']]
        output = []
        for claim in claims:
            output.extend(self.claim_ai_input(claim))
        return output

    def claim_ai_input(self, fhir_claim_repr):
        input_models = self.converter.to_ai_input(fhir_claim_repr)
        return [model.to_representation() for model in input_models]
