import secrets
import socket

from src.final_voter import FinalVoter


class EfficientFinalVoter(FinalVoter):

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