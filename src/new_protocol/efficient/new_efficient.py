import datetime as dt
import secrets
import threading
from random import randint
from typing import List

from src.new_protocol.efficient.final_voter import FinalVoter
from src.new_protocol.efficient.new_efficient_voter import NewEfficientVoter
from src.new_protocol.efficient.tallier import Tallier


def new_efficient(number_of_voters: int) -> None:
    """Run the new efficient protocol"""
    k_0: bytes = secrets.token_bytes(32)  # Random shared key for PRF
    final_voter_port: int = 65433
    tallier_port: int = 65432

    squarings_per_second = 900000

    now = dt.datetime.now()

    vote_time = now + dt.timedelta(0, 10)

    # Create the desired number of Voters
    # number_of_voters = 10
    voters: List[NewEfficientVoter] = []
    votes: List[int] = []
    for i in range(number_of_voters-1):
        vote: int = randint(0,1)
        votes.append(vote)
        voter = NewEfficientVoter(k_0, f"voter{i}", i, vote, 0, final_voter_port, tallier_port, vote_time, squarings_per_second)
        voters.append(voter)


    # Create the Tallier
    tallier = Tallier(number_of_voters, tallier_port)
    tallier_thread = threading.Thread(target=tallier.run)

    # Create the FinalVoter
    final_voter_vote: int = randint(0,1)
    votes.append(final_voter_vote)
    final_voter = FinalVoter(number_of_voters, final_voter_vote, final_voter_port, tallier_port)
    final_voter_thread= threading.Thread(target=final_voter.run)


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
    combined_votes = 1 if 1 in votes else 0
    print(f"Combined votes: {combined_votes}")
    print(f"Votes: {votes}")
