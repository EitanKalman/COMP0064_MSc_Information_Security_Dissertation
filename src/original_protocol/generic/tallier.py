import json
import socket
import threading

from src.original_protocol.generic.bloom_filter import BloomFilter


class Tallier:
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
        self.bloom_filter = None

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

        received_msg = 0

        while received_msg < self.number_of_voters:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
                received_msg +=1
            client_socket.close()

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


    def run(self) -> None:
        """
        Runs the tallier's operations including starting the server and computing the final verdict.
        """
        self.start_server()
        self.gfvd()

    def get_final_verdict(self) -> int:
        """
        Returns the final verdict after all votes have been processed.

        Returns:
        --------
        int or None
            The final verdict if it has been computed, otherwise None.
        """
        return self.final_verdict
