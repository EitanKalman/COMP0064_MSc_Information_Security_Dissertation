"""
GenericFinalVoter class for the generic variant of the e-voting protocol.

This class inherits from the FinalVoter base class and implements specific
functionality for masking the voter's vote, creating a bloom filter, and
running the final voter operations.
"""

import itertools
import json
import math
import socket
import time
from typing import List
from src.bloom_filter import BloomFilter
from src.final_voter import FinalVoter
from src.helpers import prf


class GenericFinalVoter(FinalVoter):
    """
    GenericFinalVoter class for masking votes and handling bloom filter operations.

    Attributes:
        key (bytes): The key for the pseudo-random function.
        voter_id (str): A unique identifier for the voter.
        voter_index (int): The index of the voter.
        offset (int): An offset value used in generating the masking value.
        threshold (int): The threshold for creating combinations in the bloom filter.

    Methods:
        mask_vote(masking_value: int) -> int:
            Masks the voter's vote using the masking value.

        create_bloom_filter() -> BloomFilter:
            Creates a bloom filter with all valid vote combinations.

        start_server() -> None:
            Starts the server to receive masking values from other voters.

        run() -> None:
            Runs the final voter operations, including sending the vote and bloom filter to the
            tallier.
    """

    def __init__(self, key: bytes, voter_id: str, voter_index: int, vote: int, offset: int,
                 threshold: int, number_of_voters: int, port: int, tallier_port: int) -> None:
        super().__init__(number_of_voters, vote, port, tallier_port)
        self.key: bytes = key
        self.voter_id: str = voter_id
        self.voter_index: int = voter_index
        self.offset: int = offset
        self.threshold: int = threshold

    def mask_vote(self, masking_value: int) -> int:
        """
        Masks the voter's vote using the masking value.

        Args:
            masking_value (int): The masking value.

        Returns:
            int: The masked vote.
        """
        if self.vote == 0:
            vote: int = 0
        else:
            vote: int = prf(self.key, f"2{self.offset}{self.voter_index}{self.voter_id}")
        return vote ^ masking_value

    def create_bloom_filter(self) -> BloomFilter:
        """
        Create a bloom filter with all valid vote combinations based on the threshold.

        Returns:
            BloomFilter: The created bloom filter.
        """
        elements: int = 0
        for i in range(self.threshold, self.number_of_voters + 1):
            elements += math.comb(self.number_of_voters, i)
        bloom_filter = BloomFilter(elements)
        vote_representations: List[int] = []

        for i in range(0, self.number_of_voters):
            vote_rep: int = prf(self.key, f"2{self.offset}{i}voter{i}")
            vote_representations.append(vote_rep)

        for i in range(self.threshold, self.number_of_voters + 1):
            for comb in itertools.combinations(vote_representations, i):
                xor: int = 0
                for rep in comb:
                    xor ^= rep
                bloom_filter.add(xor)
        return bloom_filter

    def start_server(self) -> None:
        """
        Starts the server to receive masking values from other voters.
        """
        server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.masking_values) < self.number_of_voters - 1:
            client_socket, _ = server_socket.accept()
            data: bytes = client_socket.recv(1024)
            with self.lock:
                self.masking_values.append(int(data.decode()))
            client_socket.close()

    def run(self) -> None:
        """
        Runs the final voter operations, including sending the vote and bloom filter to the tallier.
        """
        print("FinalVoter started")
        start: float = time.perf_counter()

        self.start_server()

        time1: float = time.perf_counter()
        masking_value: int = self.generate_masking_value()
        time2: float = time.perf_counter()
        print(f"Time taken for FinalVoter to generate masking value: {time2-time1}")

        time1: float = time.perf_counter()
        encoded_vote: int = self.mask_vote(masking_value)
        time2: float = time.perf_counter()
        print(f"Time taken for FinalVoter to mask vote: {time2-time1}")

        time1: float = time.perf_counter()
        bloom_filter: BloomFilter = self.create_bloom_filter()
        time2: float = time.perf_counter()
        print(f"Time taken for FinalVoter to create and fill Bloom Filter: {time2-time1}")

        client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))

        message = {
            'type': 'vote_bf',
            'vote': encoded_vote,
            'bf': bloom_filter.to_dict()
        }

        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()

        end: float = time.perf_counter()

        print(f"FinalVoter total time: {end - start}")
