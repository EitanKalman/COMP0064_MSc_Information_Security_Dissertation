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

    Parameters:
    -----------
    n : int
        The modulus used in the vote encryption.
    a : int
        The base number used in the encryption process.
    t : int
        The exponent to which the base is raised in the decryption process.
    key : int
        The combined key derived from private keys of the authorities.
    message_ciphertext : int
        The combined encrypted vote message.
    nonce : int
        The nonce value used for symmetric decryption.

    Returns:
    --------
    int
        The decrypted and computed vote as an integer.
    """
    first_time = time.perf_counter()
    nonce = int.to_bytes(nonce, length=8)
    ciphertext = int.to_bytes(message_ciphertext, length=32)
    x = a
    for _ in range(1, t+1):
        x = (x**2) % n
    b = x
    second_time = time.perf_counter()
    print(f"time taken: {second_time-first_time}")
    K = int.to_bytes(key - b, length=32)
    cipher = ChaCha20.new(key=K, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return int.from_bytes(plaintext)

def unlock_message(message: dict, encoded_votes: list) -> None:
    """
    Initiates the unlocking of a single encoded vote and appends it to the list of encoded votes.

    Parameters:
    -----------
    message : dict
        A dictionary containing the details required to unlock the time-locked vote including the parameters n, a, t, CK, CM, and nonce.
    encoded_votes : list
        A shared list (from multiprocessing.Manager) to which the unlocked vote is appended.
    """
    n = message['n']
    a = message['a']
    t = message['t']
    key = message['CK']
    message_ciphertext = message['CM']
    nonce = message['nonce']
    unlocked_vote = unlock(n, a, t, key, message_ciphertext, nonce)
    encoded_votes.append(unlocked_vote)


class NewGenericTallier(GenericTallier):
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
        A lock to ensure thread-safe operations on encoded_votes.
    final_vote : int or None
        The final vote computed after receiving all encoded votes.

    Methods:
    --------
    start_server():
        Starts the server to receive encoded votes from voters.
    FVD():
        Combines all encoded votes and determines the final vote.
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
        manager = multiprocessing.Manager()
        self.encoded_votes = manager.list()
        self.unlocking_processes = []

    def process_message(self, message: dict) -> None:
        """
        Processes each incoming message based on its type and initiates unlocking of time-locked votes or directly appends non-time-locked votes.

        Parameters:
        -----------
        message : dict
            The message received from a voter, which could be a time-locked vote or a direct vote.
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
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(self.number_of_voters)
        
        received_votes = 0

        while received_votes < self.number_of_voters:
            client_socket, _ = server_socket.accept()
            data = client_socket.recv(1024)
            with self.lock:
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
                received_votes += 1
            client_socket.close()

    def run(self) -> None:
        """
        Runs the tallier's operations including starting the server and computing the final vote.
        """
        start = time.perf_counter()
        self.start_server()

        for process in self.unlocking_processes:
            process.join()

        end = time.perf_counter()

        print(f"total time {end-start}")

        self.gfvd()
