from src.helpers import prf


class GenericVoter:
    def __init__(self, key: bytes, voter_id: str, voter_index: int, vote: int, offset: int, final_voter_port: int, tallier_port: int) -> None:
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
        --------
        int
            The masking value.
        """
        return prf(self.key, f'1{self.offset}{self.voter_index}{self.voter_id}')

    def mask_vote(self, masking_value: int) -> int:
        """
        Masks the voter's vote using the masking value.

        Parameters:
        -----------
        masking_value : int
            The masking value.

        Returns:
        --------
        int
            The masked vote.
        """
        if self.vote == 0:
            vote = 0
        else:
            vote = prf(self.key, f"2{self.offset}{self.voter_index}{self.voter_id}")
        return vote ^ masking_value