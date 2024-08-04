"""
Base class for the Final Voter in the e-voting protocol.

The Final Voter is responsible for receiving masking values from voters and combining them
to maintain privacy. This base class can be extended by specific protocol implementations.
"""

import threading
from typing import List


class FinalVoter:
    """
    Represents a Final Voter in the e-voting protocol.

    Attributes:
        number_of_voters (int): The total number of voters in the protocol.
        vote (int): The vote cast by the Final Voter.
        port (int): The port number used for communication.
        tallier_port (int): The port number for communication with the Tallier.
        masking_values (List[int]): A list of masking values received from voters.
        lock (threading.Lock): A lock to ensure thread-safe operations.

    Methods:
        generate_masking_value() -> int:
            Generate the combined masking value by XORing all received masking values.
    """

    def __init__(self, number_of_voters: int, vote: int, port: int, tallier_port: int) -> None:
        """
        Initialize a Final Voter with the specified number of voters, vote, and ports.

        Args:
            number_of_voters (int): The total number of voters.
            vote (int): The vote cast by this Final Voter.
            port (int): The port number for communication.
            tallier_port (int): The port number for communication with the Tallier.
        """
        self.number_of_voters: int = number_of_voters
        self.vote: int = vote
        self.port: int = port
        self.tallier_port: int = tallier_port
        self.masking_values: List[int] = []
        self.lock: threading.Lock = threading.Lock()

    def generate_masking_value(self) -> int:
        """
        Generate the combined masking value by XORing all received masking values.

        Returns:
            int: The combined masking value.
        """
        masking_value: int = 0
        for value in self.masking_values:
            masking_value ^= value
        return masking_value
