import json
import socket
import threading
import multiprocessing
import time

from Crypto.Cipher import ChaCha20

class Tallier:
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
        self.number_of_voters = number_of_voters
        self.port = port
        self.encoded_verdicts = []
        self.lock = threading.Lock()
        self.unlocking_processes = []
        self.final_verdict = None

    def unlock(self, n, a, t, CK, CM, nonce):
        first_time = time.perf_counter()
        nonce = int.to_bytes(nonce, length=8)
        ciphertext = int.to_bytes(CM, length=32)
        x = a
        for _ in range(1, t+1):
            x = (x**2) % n
        b = x
        second_time = time.perf_counter()
        print(f"time taken: {second_time-first_time}")
        K = int.to_bytes(CK - b, length=32)
        cipher = ChaCha20.new(key=K, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return int.from_bytes(plaintext)

    def unlock_message(self, message):
        n = message['n']
        a = message['a']
        t = message['t']
        CK = message['CK']
        CM = message['CM']
        nonce = message['nonce']
        unlocked_verdict = self.unlock(n, a, t, CK, CM, nonce)
        print(f"unlocked vote: {unlocked_verdict}")
        self.encoded_verdicts.append(unlocked_verdict)


    def process_message(self, message):
        if message['type'] == 'time_locked':
            # process = multiprocessing.Process(target=self.unlock_message, args=(message))
            # process.start()
            # self.unlocking_processes.append(process)
            self.unlock_message(message)
        elif message['type'] == 'not_time_locked':
            self.encoded_verdicts.append(message['vote'])

    def start_server(self) -> None:
        """
        Starts the server to receive encoded votes from voters.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        while len(self.encoded_verdicts) < self.number_of_voters:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
            client_socket.close()

    def fvd(self) -> int:
        """
        Combines all encoded votes and determines the final verdict.

        Returns:
        --------
        int
            The final verdict (0 or 1).
        """
        combined_votes = 0
        for encoded_vote in self.encoded_verdicts:
            combined_votes ^= encoded_vote
        self.final_verdict = 0 if combined_votes == 0 else 1

    def run(self) -> None:
        """
        Runs the tallier's operations including starting the server and computing the final verdict.
        """
        self.start_server()
        # for process in self.unlocking_processes:
        #     process.join()
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
