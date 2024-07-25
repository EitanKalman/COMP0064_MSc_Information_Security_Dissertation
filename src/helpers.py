"""Provides various functions used in the program"""
from hashlib import sha256

import sympy


def prf(k: bytes, val: str) -> int:
    """
    Pseudo Random Function (PRF) implementation using SHA-256.

    Parameters:
    -----------
    k : bytes
        The key for the PRF.
    val : str
        The value to be hashed with the key.

    Returns:
    --------
    int
        The PRF output as an integer.
    """
    return int(sha256((str(k) + str(val)).encode()).hexdigest(), 16) % 2**256


def _generate_prime(bits: int) -> int:
    """
    Generates a prime number of specified bit length using the sympy library.

    Parameters:
    -----------
    bits : int
        The desired bit length of the prime number.

    Returns:
    --------
    int
        A prime number with the specified bit length.
    """
    return sympy.randprime(2**(bits-1), 2**bits)

def generate_modulus(bits: int) -> tuple:
    """
    Generates a modulus by computing the product of two prime numbers, each half of the specified bit length, suitable for cryptographic operations.

    Parameters:
    -----------
    bits : int
        The total bit length for the modulus (n). The function will generate two primes each of half this bit size.

    Returns:
    --------
    tuple: (n, phi_n)
        n is the RSA modulus and phi_n is Euler's totient function value for n.
    """
    p = _generate_prime(bits // 2)
    q = _generate_prime(bits // 2)
    n = p * q
    phi_n = (p - 1) * (q - 1)
    return n, phi_n