import itertools
import json
import math
import socket
import threading

from src.bloom_filter import BloomFilter
from src.helpers import prf


class FinalVoter:
    """
    A class to represent the final voter in the secure voting protocol.

    Attributes:
    -----------
    number_of_voters : int
        The total number of voters.
    vote : int
        The final voter's vote (0 or 1).
    port : int
        The port number for the final voter server.
    tallier_port : int
        The port number for connecting to the tallier.
    masking_values : list
        A list to store masking values received from other voters.
    lock : threading.Lock
        A lock to ensure thread-safe operations on masking_values.

    Methods:
    --------
    generate_masking_value():
        Generates the masking value by XORing all received masking values.
    mask_vote(masking_value):
        Masks the final voter's vote using the masking value.
    start_server():
        Starts the server to receive masking values from other voters.
    run():
        Runs the final voter
    """

    def __init__(self, key: bytes, voter_id: str, voter_index: int, vote: int, offset: int, threshold: int, number_of_voters: int, port: int, tallier_port: int) -> None:
        self.key = key
        self.voter_id = voter_id
        self.voter_index = voter_index
        self.vote = vote
        self.offset = offset
        self.threshold = threshold
        self.number_of_voters = number_of_voters
        self.port = port
        self.tallier_port = tallier_port
        self.masking_values = []
        self.lock = threading.Lock()

    def generate_masking_value(self) -> int:
        """
        Generates the masking value by XORing all received masking values.

        Returns:
        --------
        int
            The combined masking value.
        """
        masking_value = 0
        for value in self.masking_values:
            masking_value ^= value
        return masking_value

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

    def create_bloom_filter(self):
        elements = 0
        for i in range(self.threshold, self.number_of_voters+1):
            elements += math.comb(self.number_of_voters, i)
        bloom_filter = BloomFilter(elements)
        vote_representations=[]

        for i in range(0, self.number_of_voters):
            vote_rep = prf(self.key, f"2{self.offset}{i}voter{i}")
            vote_representations.append(vote_rep)

        for i in range(self.threshold, self.number_of_voters+1):
            for comb in itertools.combinations(vote_representations, i):
                xor = 0
                for rep in comb:
                    xor ^= rep
                bloom_filter.add(xor)
        return bloom_filter

    def start_server(self) -> None:
        """
        Starts the server to receive masking values from other voters.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.masking_values) < self.number_of_voters - 1:
            client_socket, _ = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                self.masking_values.append(int(data.decode()))
            client_socket.close()

    def run(self) -> None:
        """
        Runs the final voter.
        """
        self.start_server()
        masking_value = self.generate_masking_value()

        encoded_vote = self.mask_vote(masking_value)
        bloom_filter = self.create_bloom_filter()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))

        message = {'type': 'vote_bf',
                    'vote': encoded_vote,
                    'bf': bloom_filter.to_dict()
                    }
        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()
