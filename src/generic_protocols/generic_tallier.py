import threading


class GenericTallier:
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
        self.number_of_voters = number_of_voters
        self.port = port
        self.encoded_votes = []
        self.lock = threading.Lock()
        self.bloom_filter = None
        self.final_verdict = None

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

    def get_final_verdict(self) -> int:
        """
        Returns the final verdict after all votes have been processed.

        Returns:
        --------
        int or None
            The final verdict if it has been computed, otherwise None.
        """
        return self.final_verdict