import socket
import secrets
from hashlib import sha256

class Voter:
    def __init__(self, key, ID, voter_index, vote, offset, final_voter_port, tallier_port):
        self.key = key
        self.ID = ID
        self.voter_index = voter_index
        self.vote = vote
        self.offset = offset
        self.final_voter_port = final_voter_port
        self.tallier_port = tallier_port

    def PRF(self, k, val):
        """Pseudo Random Function (PRF) implementation using SHA-256."""
        return int(sha256((str(k) + str(val)).encode()).hexdigest(), 16) % 2**256

    def generate_masking_value(self):
        return self.PRF(self.key, f'{self.offset}{self.voter_index}{self.ID}')

    def mask_vote(self, masking_value):
        if self.vote == 0:
            vote = 0
        else:
            vote = secrets.randbelow(2**256)  # Random value in F_p
        return vote ^ masking_value

    def run(self):
        masking_value = self.generate_masking_value()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.final_voter_port))
        client_socket.sendall(str(masking_value).encode())
        client_socket.close()

        encoded_vote = self.mask_vote(masking_value)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        client_socket.sendall(str(encoded_vote).encode())
        client_socket.close()
