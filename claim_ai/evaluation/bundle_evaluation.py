from ..test_response_bundle import adjudication_bundle


class ClaimBundleEvaluation:

    @classmethod
    def evaluate_bundle(cls, claim_bundle):
        entries = claim_bundle['entry']
        evaluation_result = []
        for next_claim in entries:
            evaluation_result.append(cls._evaluate(next_claim))

        return cls._build_response_bundle(evaluation_result)

    @classmethod
    def _build_response_bundle(cls, evaluation_resutl):
        # TODO: Add real build here
        return adjudication_bundle

    @classmethod
    def _evaluate(cls, claim):
        # TODO: Call AI Evaluation here
        return True

