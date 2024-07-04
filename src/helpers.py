"""Provides various functions used in the program"""
from hashlib import sha256

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