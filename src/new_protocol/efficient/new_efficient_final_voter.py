"""
NewEfficientFinalVoter class for the dropout resilient efficient variant of the e-voting protocol.

This class represents the final voter and includes methods to start a server,
receive masking values, and run the final voter operations.
"""

import json
import socket
import time
from src.efficient_protocols.efficient_final_voter import EfficientFinalVoter


class NewEfficientFinalVoter(EfficientFinalVoter):
    """
    A class to represent the final voter in the secure voting protocol.

    Attributes:
        number_of_voters (int): The total number of voters.
        vote (int): The final voter's vote (0 or 1).
        port (int): The port number for the final voter server.
        tallier_port (int): The port number for connecting to the tallier.
        masking_values (list): A list to store masking values received from other voters.
        lock (threading.Lock): A lock to ensure thread-safe operations on masking_values.

    Methods:
        run() -> None:
            Runs the final voter operations including receiving masking values and sending the
            encoded vote.
    """

    def run(self) -> None:
        """
        Runs the final voter operations including receiving masking values and sending the
        encoded vote.
        """
        print("FinalVoter started")
        start: float = time.perf_counter()

        self.start_server()
        time1: int = time.perf_counter()
        masking_value: int = self.generate_masking_value()
        time2: int = time.perf_counter()
        print(f"Time taken for FinalVoter to generate masking value: {time2-time1}")

        time1: int = time.perf_counter()
        encoded_vote: int = self.mask_vote(masking_value)
        time2: int = time.perf_counter()
        print(f"Time taken for FinalVoter to mask vote: {time2-time1}")

        client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))

        message = {'type': 'not_time_locked', 'vote': encoded_vote}

        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()

        end: float = time.perf_counter()

        print(f"FinalVoter total time: {end - start}")
