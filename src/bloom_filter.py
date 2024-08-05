"""
Bloom Filter implementation for use in the generic variants of the e-voting protocol.

A Bloom Filter is a space-efficient probabilistic data structure used to test whether 
an element is a member of a set. False positives are possible, but false negatives are not.
This implementation uses MurmurHash3 (mmh3) for hash function calculations.

Classes:
    BloomFilter: Implements a Bloom Filter with methods to add and check for elements.
"""

from math import ceil, log
import mmh3
from bitarray import bitarray


class BloomFilter:
    """
    Bloom Filter class for managing a set of elements with a probabilistic approach.
    
    Attributes:
        size (int): The size of the bit array.
        hash_count (int): The number of hash functions to use.
        bit_array (bitarray): A bitarray of size `size`, initialized to all False.

    Methods:
        add(item: int) -> None:
            Adds an item to the Bloom Filter.

        check(item: int) -> bool:
            Checks if an item is possibly in the Bloom Filter.

        to_dict() -> dict:
            Converts the BloomFilter instance into a dictionary for serialization.

        from_dict(data_dict: dict) -> 'BloomFilter':
            Creates a BloomFilter instance from a dictionary.
    """

    def __init__(self, number_of_elements: int) -> None:
        """
        Initialize a new Bloom Filter with a specified number of elements.

        Args:
            number_of_elements (int): The expected number of elements to store without
                                      exceeding the error rate.
        """
        self.size: int = ceil(-(number_of_elements * log(0.01)) / (log(2) ** 2))
        self.hash_count: int = ceil((self.size / number_of_elements) * log(2))
        self.bit_array: bitarray = bitarray(self.size)
        self.bit_array.setall(0)

    def _to_bytes(self, item: int) -> bytes:
        """
        Convert an integer item to bytes, which can be hashed.

        Args:
            item (int): The item to convert.

        Returns:
            bytes: The byte representation of the item.
        """
        return item.to_bytes((item.bit_length() + 7) // 8, byteorder='little', signed=False)

    def add(self, item: int) -> None:
        """
        Add an item to the Bloom Filter.

        Args:
            item (int): The item to add to the filter.
        """
        bytes_item: bytes = self._to_bytes(item)
        for i in range(self.hash_count):
            index: int = mmh3.hash(bytes_item, i) % self.size
            self.bit_array[index] = True

    def check(self, item: int) -> bool:
        """
        Check if an item is possibly in the Bloom Filter.

        Args:
            item (int): The item to check.

        Returns:
            bool: True if the item might be in the filter, False if it is definitely not.
        """
        bytes_item: bytes = self._to_bytes(item)
        for i in range(self.hash_count):
            index: int = mmh3.hash(bytes_item, i) % self.size
            if not self.bit_array[index]:
                return False
        return True

    def to_dict(self) -> dict:
        """
        Convert the BloomFilter instance into a dictionary for serialization.

        Returns:
            dict: A dictionary containing the size, hash count, and bit array as a hex string.
        """
        return {
            'size': self.size,
            'hash_count': self.hash_count,
            'bit_array': self.bit_array.tobytes().hex()
        }

    @classmethod
    def from_dict(cls, data_dict: dict) -> 'BloomFilter':
        """
        Create a BloomFilter instance from a dictionary.

        Args:
            data_dict (dict): The dictionary containing the size, hash count, and bit array data.

        Returns:
            BloomFilter: A new instance of BloomFilter initialized from the dictionary data.
        """
        size: int = data_dict['size']
        hash_count: int = data_dict['hash_count']
        bit_array: bitarray = bitarray()
        bit_array.frombytes(bytes.fromhex(data_dict['bit_array']))

        instance = cls(len(bit_array))  # Initialize with an estimated number of elements
        instance.size = size
        instance.hash_count = hash_count
        instance.bit_array = bit_array
        return instance
