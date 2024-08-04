"""
NewEfficientVoter class for the dropout resilient efficient variant of the e-voting protocol.

This class represents a voter and includes methods to generate a masking value,
mask votes, apply time-locks, and interact with the final voter and tallier.
"""

import datetime
import json
import random
import socket
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from src.efficient_protocols.efficient_voter import EfficientVoter
from src.helpers import generate_modulus


class NewEfficientVoter(EfficientVoter):
    """
    A class to represent a voter in the secure voting protocol.

    Attributes:
        key (bytes): The key for the pseudo-random function.
        ID (str): A unique identifier for the voter.
        voter_index (int): The index of the voter.
        vote (int): The voter's vote (0 or 1).
        offset (int): An offset value used in generating the masking value.
        final_voter_port (int): The port number for connecting to the final voter.
        tallier_port (int): The port number for connecting to the tallier.
        vote_time (datetime.datetime): The time when the vote should be cast.
        squarings (int): The number of squarings used for the time-lock puzzle.

    Methods:
        time_lock(message: int, time_for_lock: int, squarings: int) -> tuple:
            Applies a time-lock puzzle to the message, encrypting it with specified parameters.

        run() -> None:
            Runs the voter's operations including sending the masking value and encoded vote.
    """

    def __init__(
        self, key: bytes, voter_id: str, voter_index: int, vote: int, offset: int,
        final_voter_port: int, tallier_port: int, vote_time: datetime.datetime, squarings: int
    ) -> None:
        super().__init__(key, voter_id, voter_index, vote, offset, final_voter_port, tallier_port)
        self.vote_time: datetime.datetime = vote_time
        self.squarings: int = squarings

    def time_lock(self, message: int, time_for_lock: int, squarings: int) -> tuple:
        """
        Applies a time-lock puzzle to the message by encrypting it and requiring computational
        work to decrypt that scales with specified parameters.

        Args:
            message (int): The message (typically a masked vote) to be time-locked.
            time_for_lock (int): The approximate amount of real-time, in seconds, that should
            elapse before the message can be decrypted.
            squarings (int): The number of squarings used in the time-lock puzzle, defining the
            difficulty of the puzzle.

        Returns:
            tuple: A tuple containing parameters (n, a, t, key, message_ciphertext, nonce) necessary
            solving the time-lock puzzle and decrypting the message.
        """
        n, phi_n = generate_modulus(128)
        t: int = time_for_lock * squarings

        K: bytes = get_random_bytes(32)
        cipher: ChaCha20.ChaCha20Cipher = ChaCha20.new(key=K)
        ciphertext: bytes = cipher.encrypt(int.to_bytes(message, length=32))
        message_ciphertext: int = int.from_bytes(ciphertext, byteorder='big')
        nonce: int = int.from_bytes(cipher.nonce, byteorder='big')

        a: int = random.randint(2, n - 1)
        e: int = pow(2, t, phi_n)
        b: int = pow(a, e, n)
        key: int = int.from_bytes(K, byteorder='big') + b

        return n, a, t, key, message_ciphertext, nonce

    def run(self) -> None:
        """
        Runs the voter's operations including sending the masking value and encoded vote.
        """
        masking_value: int = self.generate_masking_value()

        client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.final_voter_port))
        client_socket.sendall(str(masking_value).encode())
        client_socket.close()

        encoded_vote: int = self.mask_vote(masking_value)
        print(f"Sending masked vote: {encoded_vote}")

        now: datetime.datetime = datetime.datetime.now()
        time_to_vote: int = int((self.vote_time - now).total_seconds())

        n, a, t, key, message_ciphertext, nonce = self.time_lock(encoded_vote, time_to_vote,
                                                                 self.squarings)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        message = {
            'type': 'time_locked',
            'n': n,
            'a': a,
            't': t,
            'CK': key,
            'CM': message_ciphertext,
            'nonce': nonce
        }
        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()
