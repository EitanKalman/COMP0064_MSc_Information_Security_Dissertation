from src.tallier import Tallier


class EfficientTallier(Tallier):

    def fvd(self) -> int:
        """
        Combines all encoded votes and determines the final verdict.

        Returns:
        --------
        int
            The final verdict (0 or 1).
        """
        combined_votes = 0
        for encoded_vote in self.encoded_votes:
            combined_votes ^= encoded_vote
        self.final_verdict = 0 if combined_votes == 0 else 1 
