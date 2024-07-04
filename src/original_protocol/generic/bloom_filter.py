from bitarray import bitarray
import mmh3
from math import log, ceil

class BloomFilter:
    def __init__(self, number_of_elements: int) -> None:
        """
        Initialize a new Bloom Filter with a specified number of elements.

        Args:
            number_of_elements (int): The expected number of elements to store without exceeding the error rate.

        Attributes:
            size (int): The size of the bit array, calculated based on the desired error rate and the number of elements.
            hash_count (int): The number of hash functions to use, derived from the size of the bit array and the number of elements.
            bit_array (bitarray): A bitarray of the calculated size initialized to all False (0).
        """
        self.size = ceil(-(number_of_elements*log(0.01))/(log(2)**2))
        self.hash_count = ceil((self.size/number_of_elements)*log(2))
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

    def _to_bytes(self, item):
        """
        Convert an integer item to bytes, which can be hashed.

        Args:
            item (int): The item to convert.

        Returns:
            bytes: The byte representation of the item.
        """
        return item.to_bytes((item.bit_length() + 7) // 8, byteorder='little', signed=False)

    def add(self, item):
        """
        Add an item to the Bloom Filter.

        Args:
            item (int): The item to add to the filter.
        """
        bytes_item = self._to_bytes(item)
        for i in range(self.hash_count):
            index = mmh3.hash(bytes_item, i) % self.size
            self.bit_array[index] = True

    def check(self, item):
        """
        Check if an item is possibly in the Bloom Filter.

        Args:
            item (int): The item to check.

        Returns:
            bool: True if the item might be in the filter, False if it is definitely not.
        """
        bytes_item = self._to_bytes(item)
        for i in range(self.hash_count):
            index = mmh3.hash(bytes_item, i) % self.size
            if not self.bit_array[index]:
                return False
        return True

    def to_dict(self):
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
    def from_dict(cls, data_dict):
        """
        Create a BloomFilter instance from a dictionary.

        Args:
            data_dict (dict): The dictionary containing the size, hash count, and bit array data.

        Returns:
            BloomFilter: A new instance of BloomFilter initialized from the dictionary data.
        """
        size = data_dict['size']
        hash_count = data_dict['hash_count']
        bit_array = bitarray()
        bit_array.frombytes(bytes.fromhex(data_dict['bit_array']))

        instance = cls(len(bit_array))  # Initialize with an estimated number of elements
        instance.size = size
        instance.hash_count = hash_count
        instance.bit_array = bit_array
        return instance
