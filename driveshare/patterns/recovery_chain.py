from driveshare.database import hash_answer


class SecurityQuestionHandler:
    def __init__(self, expected_hash):
        self.expected_hash = expected_hash
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def handle(self, answers, index=0):
        if index >= len(answers):
            return False

        # check answer
        if hash_answer(answers[index]) != self.expected_hash:
            return False

        if self.next_handler is None:
            return True

        return self.next_handler.handle(answers, index + 1)


def build_recovery_chain(user):
    first = SecurityQuestionHandler(user["answer_one_hash"])
    second = SecurityQuestionHandler(user["answer_two_hash"])
    third = SecurityQuestionHandler(user["answer_three_hash"])

    # link chain
    first.set_next(second).set_next(third)
    return first
