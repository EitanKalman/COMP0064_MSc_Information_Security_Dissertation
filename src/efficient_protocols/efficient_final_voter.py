import secrets
import socket
import threading


class EfficientFinalVoter:
    def __init__(self, number_of_voters: int, vote: int, port: int, tallier_port: int) -> None:
        self.number_of_voters = number_of_voters
        self.vote = vote
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
        Masks the final voter's vote using the masking value.

        Parameters:
        -----------
        masking_value : int
            The combined masking value.

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