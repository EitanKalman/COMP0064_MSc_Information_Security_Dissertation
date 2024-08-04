import json
import socket

from src.bloom_filter import BloomFilter
from src.generic_protocols.generic_tallier import GenericTallier


class OriginalGenericTallier(GenericTallier):
    """
    A class to represent the tallier in the secure voting protocol.

    Attributes:
    -----------
    number_of_voters : int
        The total number of voters.
    port : int
        The port number for the tallier server.
    encoded_votes : list
        A list to store encoded votes received from voters.
    lock : threading.Lock
        A lock to ensure thread-safe operations on encoded_verdicts.
    final_verdict : int or None
        The final verdict computed after receiving all encoded votes.

    Methods:
    --------
    start_server():
        Starts the server to receive encoded votes from voters.
    FVD():
        Combines all encoded votes and determines the final verdict.
    run():
        Runs the tallier's operations including starting the server and computing the final verdict.
    get_final_verdict():
        Returns the final verdict after all votes have been processed.
    """

    def process_message(self, message):
        if message['type'] == 'vote':
            self.encoded_votes.append(message['content'])
        elif message['type'] == 'vote_bf':
            self.encoded_votes.append(message['vote'])
            self.bloom_filter = BloomFilter.from_dict(message['bf'])

    def start_server(self) -> None:
        """
        Starts the server to receive encoded votes from voters.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.encoded_votes) < self.number_of_voters:
            client_socket, _ = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
            client_socket.close()


    def run(self) -> None:
        """
        Runs the tallier's operations including starting the server and computing the final verdict.
        """
        self.start_server()
        self.gfvd()
