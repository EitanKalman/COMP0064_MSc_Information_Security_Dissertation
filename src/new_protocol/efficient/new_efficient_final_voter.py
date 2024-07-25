import json
import socket

from src.efficient_final_voter import EfficientFinalVoter


class NewEfficientFinalVoter(EfficientFinalVoter):
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

    def run(self) -> None:
        """
        Runs the final voter.
        """
        self.start_server()
        masking_value = self.generate_masking_value()

        encoded_vote = self.mask_vote(masking_value)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))

        message = {'type': 'not_time_locked', 'vote': encoded_vote}

        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()
