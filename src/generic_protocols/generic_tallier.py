from src.tallier import Tallier


class GenericTallier(Tallier):
    def __init__(self, number_of_voters: int, port: int) -> None:
        """
        Constructs all the necessary attributes for the Tallier object.

        Parameters:
        -----------
        number_of_voters : int
            The total number of voters.
        port : int
            The port number for the tallier server.
        """
        super().__init__(number_of_voters, port)
        self.bloom_filter = None

    def gfvd(self) -> int:
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

        #If the combined vote is in the bloom filter, set the final verdict to 1, otherwise 0
        if self.bloom_filter.check(combined_votes):
            self.final_verdict = 1
        else:
            self.final_verdict = 0
