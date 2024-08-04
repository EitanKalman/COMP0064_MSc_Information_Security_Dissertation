"""
NewGenericTallier class for the dropout resilient generic variant of the e-voting protocol.

This class represents the tallier and includes methods to start a server,
receive encoded votes, process time-locked votes, and compute the final verdict.
"""

import json
import multiprocessing
import socket
import time
from Crypto.Cipher import ChaCha20
from src.bloom_filter import BloomFilter
from src.generic_protocols.generic_tallier import GenericTallier


def unlock(n: int, a: int, t: int, key: int, message_ciphertext: int, nonce: int) -> int:
    """
    Decrypts and computes the unlocked vote from the time-locked vote parameters.

    Args:
        n (int): The modulus used in the vote encryption.
        a (int): The base number used in the encryption process.
        t (int): The exponent to which the base is raised in the decryption process.
        key (int): The combined key derived from private keys of the authorities.
        message_ciphertext (int): The combined encrypted vote message.
        nonce (int): The nonce value used for symmetric decryption.

    Returns:
        int: The decrypted and computed vote as an integer.
    """
    first_time: float = time.perf_counter()
    nonce_bytes: bytes = int.to_bytes(nonce, length=8, byteorder='big')
    ciphertext: bytes = int.to_bytes(message_ciphertext, length=32, byteorder='big')
    x: int = a
    for _ in range(1, t + 1):
        x = (x ** 2) % n
    b: int = x
    second_time: float = time.perf_counter()
    print(f"time taken: {second_time - first_time}")
    K: bytes = int.to_bytes(key - b, length=32, byteorder='big')
    cipher: ChaCha20.ChaCha20Cipher = ChaCha20.new(key=K, nonce=nonce_bytes)
    plaintext: bytes = cipher.decrypt(ciphertext)
    return int.from_bytes(plaintext, byteorder='big')


def unlock_message(message: dict, encoded_votes: list) -> None:
    """
    Initiates the unlocking of a single encoded vote and appends it to the list of encoded votes.

    Args:
        message (dict): A dictionary containing the details required to unlock the time-locked vote
        including the parameters n, a, t, CK, CM, and nonce.
        encoded_votes (list): A shared list (from multiprocessing.Manager) to which the unlocked
        vote is appended.
    """
    n: int = message['n']
    a: int = message['a']
    t: int = message['t']
    key: int = message['CK']
    message_ciphertext: int = message['CM']
    nonce: int = message['nonce']
    unlocked_vote: int = unlock(n, a, t, key, message_ciphertext, nonce)
    encoded_votes.append(unlocked_vote)


class NewGenericTallier(GenericTallier):
    """
    A class to represent the tallier in the secure voting protocol.

    Attributes:
        number_of_voters (int): The total number of voters.
        port (int): The port number for the tallier server.
        encoded_votes (list): A list to store encoded votes received from voters.
        lock (threading.Lock): A lock to ensure thread-safe operations on encoded_votes.
        final_verdict (int or None): The final verdict computed after receiving all encoded votes.
        unlocking_processes (list): A list to store processes for unlocking time-locked votes.

    Methods:
        process_message(message: dict) -> None:
            Processes incoming messages and initiates unlocking of time-locked votes or directly
            appends non-time-locked votes.

        start_server() -> None:
            Starts the server to receive encoded votes from voters.

        run() -> None:
            Runs the tallier's operations including starting the server and computing the
            final verdict.
    """

    def __init__(self, number_of_voters: int, port: int) -> None:
        """
        Constructs all the necessary attributes for the Tallier object.

        Args:
            number_of_voters (int): The total number of voters.
            port (int): The port number for the tallier server.
        """
        super().__init__(number_of_voters, port)
        manager: multiprocessing.Manager = multiprocessing.Manager()
        self.encoded_votes = manager.list()
        self.unlocking_processes: list[multiprocessing.Process] = []

    def process_message(self, message: dict) -> None:
        """
        Processes each incoming message based on its type and initiates unlocking of time-locked
        votes or directly appends non-time-locked votes.

        Args:
            message (dict): The message received from a voter, which could be a time-locked vote
            or a direct vote.
        """
        if message['type'] == 'time_locked':
            # Create a process for the time locked vote and start it
            p = multiprocessing.Process(target=unlock_message, args=(message, self.encoded_votes,))
            p.start()
            self.unlocking_processes.append(p)
        elif message['type'] == 'not_time_locked':
            self.encoded_votes.append(message['vote'])
        elif message['type'] == 'vote_bf':
            self.encoded_votes.append(message['vote'])
            self.bloom_filter = BloomFilter.from_dict(message['bf'])

    def start_server(self) -> None:
        """
        Starts the server to receive encoded votes from voters.
        """
        server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)

        received_votes: int = 0

        while received_votes < self.number_of_voters:
            client_socket, _ = server_socket.accept()
            data: bytes = client_socket.recv(1024)
            with self.lock:
                message: dict = json.loads(data.decode('utf-8'))
                self.process_message(message)
                received_votes += 1
            client_socket.close()

    def run(self) -> None:
        """
        Runs the tallier's operations including starting the server and computing the final vote.
        """
        start: float = time.perf_counter()
        self.start_server()

        for process in self.unlocking_processes:
            process.join()

        end: float = time.perf_counter()

        print(f"total time {end - start}")

        self.gfvd()
