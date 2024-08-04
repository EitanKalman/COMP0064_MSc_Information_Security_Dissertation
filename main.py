import argparse

from src.new_protocol.efficient.new_efficient import new_efficient
from src.new_protocol.generic.new_generic import new_generic
from src.original_protocol.efficient.original_efficient import \
    original_efficient
from src.original_protocol.generic.original_generic import original_generic

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("-o", action="store_true", help="Run original protocol")
    group1.add_argument("-dr", action="store_true", help="Run dropout resilient protocol")

    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-e", action="store_true", help="Run the efficient variant with a threshold of 1")
    group2.add_argument("-g", action="store_true", help="Run the generic variant with a variable threshold")

    parser.add_argument('-n', type=int, required=True, help="Set the number of voters (default is 10)")
    parser.add_argument('-t', type=int, required=False, help="Set the threshold- only for generic variants (default is simple majority)")

    args = parser.parse_args()

    threshold: int = args.t if args.t else (args.n // 2) + 1

    if args.o and args.e:
        original_efficient(args.n)
    elif args.o and args.g:
        original_generic(args.n, threshold)
    elif args.dr and args.e:
        new_efficient(args.n)
    elif args.dr and args.g:
        new_generic(args.n, threshold)
    else:
        print("Invalid combination of flags")
