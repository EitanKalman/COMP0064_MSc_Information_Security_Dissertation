"""
GenericTallier class for the generic variant of the e-voting protocol.

This class inherits from the Tallier base class and implements specific
functionality for determining the final verdict using a bloom filter.
"""

from src.tallier import Tallier
from src.bloom_filter import BloomFilter


class GenericTallier(Tallier):
    """
    GenericTallier class for combining votes and determining the final verdict.

    Attributes:
        bloom_filter (BloomFilter): The bloom filter used to check combined votes.

    Methods:
        gfvd() -> int:
            Combines all encoded votes and determines the final verdict using the bloom filter.
    """

    def __init__(self, number_of_voters: int, port: int) -> None:
        """
        Constructs all the necessary attributes for the Tallier object.

        Args:
            number_of_voters (int): The total number of voters.
            port (int): The port number for the tallier server.
        """
        super().__init__(number_of_voters, port)
        self.bloom_filter: BloomFilter = None

    def gfvd(self) -> int:
        """
        Combines all encoded votes and determines the final verdict.

        Returns:
            int: The final verdict (0 or 1).
        """
        combined_votes: int = 0
        for encoded_vote in self.encoded_votes:
            combined_votes ^= encoded_vote

        # If the combined vote is in the bloom filter, set the final verdict to 1, otherwise 0
        self.final_verdict = 1 if self.bloom_filter.check(combined_votes) else 0
        return self.final_verdict
