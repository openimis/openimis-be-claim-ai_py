from abc import ABC


class AbstractConverter(ABC):

    def to_ai_input(self, input_item):
        raise NotImplementedError("to_ai_input not implemented")

    def to_ai_output(self, ai_item):
        raise NotImplementedError("to_ai_input not implemented")
