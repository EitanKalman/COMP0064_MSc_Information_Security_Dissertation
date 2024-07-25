import argparse

from src.new_protocol.efficient.new_efficient import new_efficient
from src.new_protocol.generic.new_generic import new_generic
from src.original_protocol.efficient.original_efficient import \
    original_efficient
from src.original_protocol.generic.original_generic import original_generic

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("-o", action="store_true")
    group1.add_argument("-dr", action="store_true")

    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-e", action="store_true")
    group2.add_argument("-g", action="store_true")

    parser.add_argument('-n', type=int, required=True)
    parser.add_argument('-t', type=int, required=False)

    args = parser.parse_args()

    if args.o and args.e:
        original_efficient(args.n)
    elif args.o and args.g:
        original_generic(args.n, args.t)
    elif args.dr and args.e:
        new_efficient(args.n)
    elif args.dr and args.g:
        # print("Not yet implemented")
        new_generic(args.n, args.t)
    else:
        print("Invalid combination of flags")
    