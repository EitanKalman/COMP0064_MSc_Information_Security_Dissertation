import socket
import threading

class Tallier:
    def __init__(self, number_of_voters, port):
        self.number_of_voters = number_of_voters
        self.port = port
        self.encoded_verdicts = []
        self.lock = threading.Lock()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.encoded_verdicts) < self.number_of_voters:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                self.encoded_verdicts.append(int(data.decode()))
            client_socket.close()

    def FVD(self):
        combined_votes = 0
        for encoded_vote in self.encoded_verdicts:
            combined_votes ^= encoded_vote
        final_verdict = 0 if combined_votes == 0 else 1
        return final_verdict

    def run(self):
        self.start_server()
        final_verdict = self.FVD()
        print(f"Final Verdict is: {final_verdict}")
