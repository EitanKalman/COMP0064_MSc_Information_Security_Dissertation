import secrets
import socket
import threading

class FinalVoter():
    def __init__(self, number_of_voters, vote, port, tallier_port):
        self.number_of_voters = number_of_voters
        self.vote = vote
        self.port = port
        self.tallier_port = tallier_port
        self.masking_values = []
        self.lock = threading.Lock()

    def generate_masking_value(self):
        masking_value = 0
        for value in self.masking_values:
            masking_value ^= value
        return masking_value

    def mask_vote(self, masking_value):
        if self.vote == 0:
            vote = 0
        else:
            vote = secrets.randbelow(2**256)  # Random value in F_p
        return vote ^ masking_value

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.masking_values) < self.number_of_voters-1:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                self.masking_values.append(int(data.decode()))
            client_socket.close()

    def run(self):
        self.start_server()
        masking_value = self.generate_masking_value()

        encoded_vote = self.mask_vote(masking_value)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        client_socket.sendall(str(encoded_vote).encode())
        client_socket.close()
