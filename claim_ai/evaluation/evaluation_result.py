from claim_ai.evaluation.input_models import AiInputModel


class EvaluationResult:

    def __init__(self, evaluated_claim: dict, evaluation_input: AiInputModel, evaluation_result: int):
        self.claim = evaluated_claim
        self.input = evaluation_input
        self.result = evaluation_result
