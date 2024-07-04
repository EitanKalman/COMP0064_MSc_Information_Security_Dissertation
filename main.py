import sys

from src.original_protocol.efficient.original_efficient import original_efficient
from src.original_protocol.generic.original_generic import original_generic


n = len(sys.argv)

if sys.argv[1] == "original_efficient":
    number_of_voters = sys.argv[2]
    original_efficient(int(number_of_voters))


if sys.argv[1] == "original_generic":
    number_of_voters = sys.argv[2]
    threshold = sys.argv[3]
    original_generic(int(number_of_voters), int(threshold))