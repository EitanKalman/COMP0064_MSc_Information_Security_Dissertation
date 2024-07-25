import socket

from src.efficient_protocols.efficient_tallier import EfficientTallier


class OriginalEfficientTallier(EfficientTallier):
    """
    A class to represent the tallier in the secure voting protocol.

    Attributes:
    -----------
    number_of_voters : int
        The total number of voters.
    port : int
        The port number for the tallier server.
    encoded_verdicts : list
        A list to store encoded verdicts received from voters.
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
        super().__init__(number_of_voters, port)
        

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
                self.encoded_votes.append(int(data.decode()))
            client_socket.close()

    def run(self) -> None:
        """
        Runs the tallier's operations including starting the server and computing the final verdict.
        """
        self.start_server()
        self.fvd()

    def get_final_verdict(self) -> int:
        """
        Returns the final verdict after all votes have been processed.

        Returns:
        --------
        int or None
            The final verdict if it has been computed, otherwise None.
        """
        return self.final_verdict
