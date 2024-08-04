"""
EfficientVoter class for the efficient variant of the e-voting protocol.

This class represents a voter and includes methods to generate a masking value,
mask votes, and interact with the final voter and tallier.
"""

import secrets
from src.helpers import prf


class EfficientVoter:
    """
    A class to represent a voter in the secure voting protocol.

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
        self.key = key
        self.voter_id = voter_id
        self.voter_index = voter_index
        self.vote = vote
        self.offset = offset
        self.final_voter_port = final_voter_port
        self.tallier_port = tallier_port

    def generate_masking_value(self) -> int:
        """
        Generates the masking value for the voter.

        Returns:
            int: The masking value.
        """
        return prf(self.key, f'{self.offset}{self.voter_index}{self.voter_id}')

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
            vote: int = secrets.randbelow(2**256)  # Random value in F_p
        return vote ^ masking_value
