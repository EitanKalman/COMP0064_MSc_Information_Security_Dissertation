import threading


class FinalVoter:
    def __init__(self, number_of_voters: int, vote: int, port: int, tallier_port: int) -> None:
        self.number_of_voters = number_of_voters
        self.vote = vote
        self.port = port
        self.tallier_port = tallier_port
        self.masking_values = []
        self.lock = threading.Lock()


    def generate_masking_value(self) -> int:
        """
        Generates the masking value by XORing all received masking values.

        Returns:
        --------
        int
            The combined masking value.
        """
        masking_value = 0
        for value in self.masking_values:
            masking_value ^= value
        return masking_value