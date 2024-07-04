import json
import socket

from src.helpers import prf

class Voter:
    """
    A class to represent a voter in the secure voting protocol.

    Attributes:
    -----------
    key : bytes
        The key for the pseudo-random function.
    ID : str
        A unique identifier for the voter.
    voter_index : int
        The index of the voter.
    vote : int
        The voter's vote (0 or 1).
    offset : int
        An offset value used in generating the masking value.
    final_voter_port : int
        The port number for connecting to the final voter.
    tallier_port : int
        The port number for connecting to the tallier.

    Methods:
    --------
    PRF(k, val):
        Pseudo Random Function (PRF) implementation using SHA-256.
    generate_masking_value():
        Generates the masking value for the voter.
    mask_vote(masking_value):
        Masks the voter's vote using the masking value.
    run():
        Runs the voter's operations including sending the masking value and encoded vote.
    """

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

    def run(self)  -> None:
        """
        Runs the voter's operations including sending the masking value and encoded vote.
        """
        masking_value = self.generate_masking_value()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.final_voter_port))
        client_socket.sendall(str(masking_value).encode())
        client_socket.close()

        encoded_vote = self.mask_vote(masking_value)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        message = {'type': 'vote', 'content': encoded_vote}
        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()
