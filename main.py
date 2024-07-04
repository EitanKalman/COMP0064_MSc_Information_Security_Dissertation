import sys

from src.original_protocol.efficient.original_efficient import original_efficient

n = len(sys.argv)

if sys.argv[1] == "original_efficient":
    number_of_voters = sys.argv[2]
    original_efficient(int(number_of_voters))
