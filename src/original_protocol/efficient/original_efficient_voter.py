"""
OriginalEfficientVoter class for the original efficient variant of the e-voting protocol.

This class represents a voter and includes methods to generate a masking value,
mask votes, and interact with the final voter and tallier.
"""

import socket
import time
from src.efficient_protocols.efficient_voter import EfficientVoter


class OriginalEfficientVoter(EfficientVoter):
    """
    A class to represent a voter in the secure voting protocol.

    Attributes:
        key (bytes): The key for the pseudo-random function.
        ID (str): A unique identifier for the voter.
        voter_index (int): The index of the voter.
        vote (int): The voter's vote (0 or 1).
        offset (int): An offset value used in generating the masking value.
        final_voter_port (int): The port number for connecting to the final voter.
        tallier_port (int): The port number for connecting to the tallier.

    Methods:
        run() -> None:
            Runs the voter's operations including sending the masking value and encoded vote.
    """

    def run(self) -> None:
        """
        Runs the voter's operations including sending the masking value and encoded vote.
        """
        print(f"{self.voter_id} started")
        start: float = time.perf_counter()

        time1: float = time.perf_counter()
        masking_value: int = self.generate_masking_value()
        time2: float = time.perf_counter()
        print(f"Time taken for {self.voter_id} to generate masking value: {time2-time1}")

        client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.final_voter_port))
        client_socket.sendall(str(masking_value).encode())
        client_socket.close()

        time1: float = time.perf_counter()
        encoded_vote: int = self.mask_vote(masking_value)
        time2: float = time.perf_counter()
        print(f"Time taken for {self.voter_id} to mask vote: {time2-time1}")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        client_socket.sendall(str(encoded_vote).encode())
        client_socket.close()

        end: float = time.perf_counter()

        print(f"{self.voter_id} total time: {end - start}")
