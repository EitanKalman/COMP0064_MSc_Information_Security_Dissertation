import socket
import secrets
from hashlib import sha256

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

    def __init__(self, key, ID, voter_index, vote, offset, final_voter_port, tallier_port):
        self.key = key
        self.ID = ID
        self.voter_index = voter_index
        self.vote = vote
        self.offset = offset
        self.final_voter_port = final_voter_port
        self.tallier_port = tallier_port

    def PRF(self, k, val):
        """
        Pseudo Random Function (PRF) implementation using SHA-256.

        Parameters:
        -----------
        k : bytes
            The key for the PRF.
        val : str
            The value to be hashed with the key.

        Returns:
        --------
        int
            The PRF output as an integer.
        """
        return int(sha256((str(k) + str(val)).encode()).hexdigest(), 16) % 2**256

    def generate_masking_value(self):
        """
        Generates the masking value for the voter.

        Returns:
        --------
        int
            The masking value.
        """
        return self.PRF(self.key, f'{self.offset}{self.voter_index}{self.ID}')

    def mask_vote(self, masking_value):
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
            vote = secrets.randbelow(2**256)  # Random value in F_p
        return vote ^ masking_value

    def run(self):
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
        client_socket.sendall(str(encoded_vote).encode())
        client_socket.close()
