import secrets
import threading

from tallier import Tallier
from voter import Voter
from final_voter import FinalVoter

def main():

    k_0 = secrets.token_bytes(32)  # Random key for PRF
    final_voter_port = 65433
    tallier_port = 65432

    voter1 = Voter(k_0, "voter1", 1, 0, 0, final_voter_port, tallier_port)
    voter2 = Voter(k_0, "voter2", 2, 1, 0, final_voter_port, tallier_port)
    voter3 = Voter(k_0, "voter3", 3, 1, 0, final_voter_port, tallier_port)

    voters = [voter1, voter2, voter3]
    number_of_voters = len(voters)

    # Create the Tallier
    tallier = Tallier(number_of_voters, tallier_port)
    tallier_thread = threading.Thread(target=tallier.run)

    # Create the FinalVoter
    final_voter = FinalVoter(number_of_voters, 0, final_voter_port, tallier_port)
    final_voter_thread= threading.Thread(target=final_voter.run)

    # Start the Tallier and FinalVoter servers in separate threads
    tallier_thread.start()
    final_voter_thread.start()

    # Start the Voters in separate threads
    voter_threads = []
    for voter in voters:
        voter_thread = threading.Thread(target=voter.run)
        voter_threads.append(voter_thread)
        voter_thread.start()

    # Wait for all voter threads to finish
    for thread in voter_threads:
        thread.join()

    # Wait for the Tallier to collect all encoded verdicts
    tallier_thread.join()
    # final_verdict = tallier.FVD()
    # print(f"Final verdict: {final_verdict}")

if __name__ == "__main__":
    main()
