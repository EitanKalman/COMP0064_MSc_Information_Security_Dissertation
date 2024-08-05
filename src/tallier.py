"""
Base class for the Tallier in the e-voting protocol.

The Tallier is responsible for receiving votes from voters, computing the final verdict,
and ensuring that the process is secure and accurate. This base class can be extended
by specific protocol implementations.
"""

import threading
from typing import List, Optional


class Tallier:
    """
    Represents a Tallier in the e-voting protocol.

    Attributes:
        number_of_voters (int): The total number of voters.
        port (int): The port number for the Tallier server.
        lock (threading.Lock): A lock to ensure thread-safe operations.
        encoded_votes (List[int]): A list to store encoded votes received from voters.
        final_verdict (Optional[int]): The computed final verdict, initially None.

    Methods:
        get_final_verdict() -> Optional[int]:
            Return the final verdict after all votes have been processed.
    """

    def __init__(self, number_of_voters: int, port: int) -> None:
        """
        Construct all the necessary attributes for the Tallier object.

        Args:
            number_of_voters (int): The total number of voters.
            port (int): The port number for the Tallier server.
        """
        self.number_of_voters: int = number_of_voters
        self.port: int = port
        self.lock: threading.Lock = threading.Lock()
        self.encoded_votes: List[int] = []
        self.final_verdict: Optional[int] = None

    def get_final_verdict(self) -> Optional[int]:
        """
        Return the final verdict after all votes have been processed.

        Returns:
            Optional[int]: The final verdict if it has been computed, otherwise None.
        """
        return self.final_verdict
