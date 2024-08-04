import datetime
import json
import random
import socket

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

from src.generic_protocols.generic_voter import GenericVoter
from src.helpers import generate_modulus


class NewGenericVoter(GenericVoter):
    """
    A class to represent a voter in the secure voting protocol.

    Attributes:
    -----------
    key : bytes
        The key for the pseudo-random function.
    ID : str
        A unique identifier for the voter.
    voter_index : int
        The index of the voter.
    vote : int
        The voter's vote (0 or 1).
    offset : int
        An offset value used in generating the masking value.
    final_voter_port : int
        The port number for connecting to the final voter.
    tallier_port : int
        The port number for connecting to the tallier.

    Methods:
    --------
    PRF(k, val):
        Pseudo Random Function (PRF) implementation using SHA-256.
    generate_masking_value():
        Generates the masking value for the voter.
    mask_vote(masking_value):
        Masks the voter's vote using the masking value.
    run():
        Runs the voter's operations including sending the masking value and encoded vote.
    """

    def __init__(self, key: bytes, voter_id: str, voter_index: int, vote: int, offset: int, final_voter_port: int, tallier_port: int, vote_time: int, squarings: int) -> None:
        super().__init__(key, voter_id, voter_index, vote, offset, final_voter_port, tallier_port)
        self.vote_time = vote_time
        self.squarings = squarings

    def time_lock(self, message: int, time_for_lock: int, squarings: int) -> tuple:
        """
        Applies a time-lock puzzle to the message by encrypting it and requiring computational work to decrypt that scales with specified parameters.

        Parameters:
        -----------
        message : int
            The message (typically a masked vote) to be time-locked.
        time_for_lock : int
            The approximate amount of real-time, in seconds, that should elapse before the message can be decrypted.
        squarings : int
            The number of squarings used in the time-lock puzzle, defining the difficulty of the puzzle.

        Returns:
        --------
        tuple
            A tuple containing parameters (n, a, t, key, message_ciphertext, nonce) necessary for solving the time-lock puzzle and decrypting the message.
        """
        n, phi_n,= generate_modulus(128)
        t = time_for_lock*squarings

        K = get_random_bytes(32)
        cipher = ChaCha20.new(key=K)
        ciphertext = cipher.encrypt(int.to_bytes(message, length=32))
        message_ciphertext = int.from_bytes(ciphertext)
        nonce = int.from_bytes(cipher.nonce)

        a = random.randint(2, n-1)
        e = pow(2, t, phi_n)
        b = pow(a, e, n)
        key = int.from_bytes(K) + b

        return n, a, t, key, message_ciphertext, nonce

    def run(self)  -> None:
        """
        Runs the voter's operations including sending the masking value and encoded vote.
        """
        masking_value = self.generate_masking_value()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.final_voter_port))
        client_socket.sendall(str(masking_value).encode())
        client_socket.close()

        encoded_vote = self.mask_vote(masking_value)
        print(f"Sending masked vote: {encoded_vote}")

        now = datetime.datetime.now()

        time = int((self.vote_time-now).total_seconds())

        n, a, t, key, message_ciphertext, nonce = self.time_lock(encoded_vote, time, self.squarings)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        message = {'type': 'time_locked',
                   'n': n,
                   'a': a,
                   't': t,
                   'CK': key,
                   'CM': message_ciphertext,
                   'nonce': nonce
        }
        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()