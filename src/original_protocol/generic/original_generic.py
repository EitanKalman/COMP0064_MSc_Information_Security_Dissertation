"""
Script to set up and run a protocol instance of the original generic variant.

This script initializes the voters, tallier, and final voter, and runs the protocol
to compute the final verdict.
"""

import secrets
import threading
from random import randint
from typing import List

from src.generic_protocols.generic_final_voter import GenericFinalVoter
from src.original_protocol.generic.original_generic_tallier import OriginalGenericTallier
from src.original_protocol.generic.original_generic_voter import OriginalGenericVoter


def original_generic(number_of_voters: int, threshold: int) -> None:
    """
    Run the original generic protocol.

    Args:
        number_of_voters (int): The total number of voters.
        threshold (int): The threshold for computing the final verdict.
    """
    k_0: bytes = secrets.token_bytes(32)  # Random shared key for PRF
    final_voter_port: int = 65433
    tallier_port: int = 65432

    # Create the desired number of Voters
    voters: List[OriginalGenericVoter] = []
    votes: List[int] = []
    for i in range(number_of_voters - 1):
        vote: int = randint(0, 1)
        votes.append(vote)
        voter = OriginalGenericVoter(k_0, f"voter{i}", i, vote, 0, final_voter_port, tallier_port)
        voters.append(voter)

    # Create the Tallier
    tallier = OriginalGenericTallier(number_of_voters, tallier_port)
    tallier_thread = threading.Thread(target=tallier.run)

    # Create the FinalVoter
    final_voter_vote: int = randint(0, 1)
    votes.append(final_voter_vote)
    final_voter = GenericFinalVoter(
        k_0,
        f"voter{number_of_voters - 1}",
        number_of_voters - 1,
        final_voter_vote,
        0,
        threshold,
        number_of_voters,
        final_voter_port,
        tallier_port
    )
    final_voter_thread = threading.Thread(target=final_voter.run)

    # Start the Tallier and FinalVoter servers in separate threads
    tallier_thread.start()
    final_voter_thread.start()

    # Start the Voters in separate threads
    voter_threads: List[threading.Thread] = []
    for voter in voters:
        voter_thread = threading.Thread(target=voter.run)
        voter_threads.append(voter_thread)
        voter_thread.start()

    # Wait for all voter threads to finish
    for thread in voter_threads:
        thread.join()

    # Wait for the Tallier to collect all encoded verdicts and get the final verdict
    tallier_thread.join()
    final_verdict: int = tallier.get_final_verdict()
    print(f"Final verdict: {final_verdict}")

    # Calculate the correct final verdict to verify that the Tallier is correct
    one_votes: int = votes.count(1)
    print(f"Above threshold? {one_votes >= threshold}")
    print(f"Votes: {votes}")
