"""
GenericVoter class for the generic variant of the e-voting protocol.

This class represents a voter and includes methods to generate a masking value
and mask votes.
"""

from src.helpers import prf


class GenericVoter:
    """
    GenericVoter class for participating in the voting protocol.

    Attributes:
        key (bytes): The key for the pseudo-random function.
        voter_id (str): A unique identifier for the voter.
        voter_index (int): The index of the voter.
        vote (int): The voter's vote (0 or 1).
        offset (int): An offset value used in generating the masking value.
        final_voter_port (int): The port number for connecting to the final voter.
        tallier_port (int): The port number for connecting to the tallier.

    Methods:
        generate_masking_value() -> int:
            Generates the masking value for the voter.

        mask_vote(masking_value: int) -> int:
            Masks the voter's vote using the masking value.
    """

    def __init__(self, key: bytes, voter_id: str, voter_index: int, vote: int, offset: int,
                 final_voter_port: int, tallier_port: int) -> None:
        self.key: bytes = key
        self.voter_id: str = voter_id
        self.voter_index: int = voter_index
        self.vote: int = vote
        self.offset: int = offset
        self.final_voter_port: int = final_voter_port
        self.tallier_port: int = tallier_port

    def generate_masking_value(self) -> int:
        """
        Generates the masking value for the voter.

        Returns:
            int: The masking value.
        """
        return prf(self.key, f'1{self.offset}{self.voter_index}{self.voter_id}')

    def mask_vote(self, masking_value: int) -> int:
        """
        Masks the voter's vote using the masking value.

        Args:
            masking_value (int): The masking value.

        Returns:
            int: The masked vote.
        """
        if self.vote == 0:
            vote: int = 0
        else:
            vote: int = prf(self.key, f"2{self.offset}{self.voter_index}{self.voter_id}")
        return vote ^ masking_value
