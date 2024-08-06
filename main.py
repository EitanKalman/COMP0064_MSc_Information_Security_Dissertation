"""
Main entry point for the private threshold e-voting protocol.

This script allows the execution of different variants of the e-voting protocol. 
There are two primary types of protocols: the original protocol and the dropout 
resilient protocol. Each of these protocols can be executed in an efficient variant 
(with a threshold of 1) or a generic variant (with a variable threshold).

Arguments:
    -o : Run the original protocol
    -dr : Run the dropout resilient protocol
    -e : Run the efficient variant with a threshold of 1
    -g : Run the generic variant with a variable threshold
    -n : Set the number of voters (required)
    -t : Set the threshold (only for generic variants; defaults to simple majority)

Usage examples:
    Run original efficient variant:
        python main.py -o -e -n 10

    Run dropout resilient generic variant with custom threshold:
        python main.py -dr -g -n 10 -t 7
"""

import argparse

from src.new_protocol.efficient.new_efficient import new_efficient
from src.new_protocol.generic.new_generic import new_generic
from src.original_protocol.efficient.original_efficient import \
    original_efficient
from src.original_protocol.generic.original_generic import original_generic


def main() -> None:
    """
    Parse command-line arguments and execute the appropriate e-voting protocol variant.

    Raises:
        SystemExit: If an invalid combination of flags is provided.
    """

    # Set the number of squarings per second the Tallier system can do here
    squarings_per_second: int = 3000000

    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    group1: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("-o",
                        action="store_true",
                        help="Run original protocol"
                        )
    group1.add_argument("-dr",
                        action="store_true",
                        help="Run dropout resilient protocol"
                        )

    group2: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-e",
                        action="store_true",
                        help="Run the efficient variant with a threshold of 1"
                        )
    group2.add_argument("-g",
                        action="store_true",
                        help="Run the generic variant with a variable threshold"
                        )

    parser.add_argument('-n',
                        type=int,
                        required=True,
                        help="Set the number of voters (default is 10)"
                        )
    parser.add_argument('-t',
                        type=int,
                        required=False,
                        help="Set the threshold- only for generic variants (default is simple majority)"
                        )

    args: argparse.Namespace = parser.parse_args()

    threshold: int = args.t if args.t else (args.n // 2) + 1

    if args.o and args.e:
        original_efficient(args.n)
    elif args.o and args.g:
        original_generic(args.n, threshold)
    elif args.dr and args.e:
        new_efficient(args.n, squarings_per_second)
    elif args.dr and args.g:
        new_generic(args.n, threshold, squarings_per_second)
    else:
        print("Invalid combination of flags")


if __name__ == "__main__":
    main()
