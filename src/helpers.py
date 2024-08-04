"""
Provides various utility functions used in the e-voting protocol.

This module includes cryptographic functions such as a Pseudo Random Function (PRF) 
and modulus generation suitable for cryptographic operations.

Functions:
    prf(k: bytes, val: str) -> int: Computes a pseudo-random function using SHA-256.
    generate_modulus(bits: int) -> tuple[int, int]: Generates an RSA modulus and Euler's totient.
"""

from hashlib import sha256
import sympy


def prf(k: bytes, val: str) -> int:
    """
    Pseudo Random Function (PRF) implementation using SHA-256.

    Args:
        k (bytes): The key for the PRF.
        val (str): The value to be hashed with the key.

    Returns:
        int: The PRF output as an integer, reduced modulo 2^256.
    """
    return int(sha256((str(k) + str(val)).encode()).hexdigest(), 16) % 2**256


def _generate_prime(bits: int) -> int:
    """
    Generate a prime number of a specified bit length using the sympy library.

    Args:
        bits (int): The desired bit length of the prime number.

    Returns:
        int: A prime number with the specified bit length.
    """
    return sympy.randprime(2**(bits-1), 2**bits)


def generate_modulus(bits: int) -> tuple[int, int]:
    """
    Generate a modulus by computing the product of two prime numbers.

    Each prime is half of the specified bit length, suitable for cryptographic operations.

    Args:
        bits (int): The total bit length for the modulus (n).

    Returns:
        tuple[int, int]: A tuple containing the RSA modulus and Euler's totient function value.
    """
    p: int = _generate_prime(bits // 2)
    q: int = _generate_prime(bits // 2)
    n: int = p * q
    phi_n: int = (p - 1) * (q - 1)
    return n, phi_n
