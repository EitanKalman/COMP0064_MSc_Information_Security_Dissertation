"""
EfficientTallier class for the efficient variant of the e-voting protocol.

This class inherits from the Tallier base class and implements specific
functionality for determining the final verdict for the efficient variants.
"""

from src.tallier import Tallier


class EfficientTallier(Tallier):
    """
    EfficientTallier class for combining votes and determining the final verdict.

    Methods:
        fvd() -> int:
            Combines all encoded votes and determines the final verdict.
    """

    def fvd(self) -> int:
        """
        Combines all encoded votes and determines the final verdict.

        Returns:
            int: The final verdict (0 or 1).
        """
        combined_votes: int = 0
        for encoded_vote in self.encoded_votes:
            combined_votes ^= encoded_vote
        self.final_verdict = 0 if combined_votes == 0 else 1
