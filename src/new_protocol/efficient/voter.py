import datetime
import json
import random
import socket
import secrets
import sympy

from base64 import b64encode

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

# from src.helpers import prf

class Voter:
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
        self.key = key
        self.voter_id = voter_id
        self.voter_index = voter_index
        self.vote = vote
        self.offset = offset
        self.final_voter_port = final_voter_port
        self.tallier_port = tallier_port
        self.vote_time = vote_time
        self.squarings = squarings

    def generate_masking_value(self) -> int:
        """
        Generates the masking value for the voter.

        Returns:
        --------
        int
            The masking value.
        """
        return 0
        # return prf(self.key, f'{self.offset}{self.voter_index}{self.voter_id}')

    def mask_vote(self, masking_value: int) -> int:
        """
        Masks the voter's vote using the masking value.

        Parameters:
        -----------
        masking_value : int
            The masking value.

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
    

    def generate_prime(self, bits):
        return sympy.randprime(2**(bits-1), 2**bits)

    def generate_modulus(self, bits):
        p = self.generate_prime(bits // 2)
        q = self.generate_prime(bits // 2)
        n = p * q
        phi_n = (p - 1) * (q - 1)
        return n, phi_n

    def time_lock(self, message, T, S):
        n, phi_n,= self.generate_modulus(128)
        t = T*S

        K = get_random_bytes(32)
        cipher = ChaCha20.new(key=K)
        ciphertext = cipher.encrypt(int.to_bytes(message, length=32))
        CM = int.from_bytes(ciphertext)
        nonce = int.from_bytes(cipher.nonce)

        a = random.randint(2, n-1)
        e = pow(2, t, phi_n)
        b = pow(a, e, n)
        CK = int.from_bytes(K) + b

        return n, a, t, CK, CM, nonce

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

        n, a, t, CK, CM, nonce = self.time_lock(encoded_vote, time, self.squarings)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', self.tallier_port))
        message = {'type': 'time_locked',
                   'n': n,
                   'a': a,
                   't': t,
                   'CK': CK,
                   'CM': CM,
                   'nonce': nonce
        }
        client_socket.sendall(json.dumps(message).encode('utf-8'))
        client_socket.close()
