import json
import socket
import threading

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

    def process_message(self, message):
        if message['type'] == 'vote':
            self.encoded_votes.append(message['content'])
        else:
            print("Received something other than a vote")

    def start_server(self) -> None:
        """
        Starts the server to receive encoded votes from voters.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.encoded_votes) < self.number_of_voters:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
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

        # If combined_votes=0 or combined_votes not in bloom filter: self.final_verdict = 0; else: self.final_verdict = 1

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
