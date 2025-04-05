# To see how votes need to be look at the bottom of the file. You likely also need to install the condorcet package.

import argparse

import condorcet

from ipho_poll.models import CastedVote, Voting, VotingChoice, VotingRight


def get_votings():
    sc_votings = Voting.objects.filter(title__startswith="Steering committee election:")
    rights = VotingRight.objects.all()
    votings_list = []
    for right in rights:
        votings_dict = {}
        for voting in sc_votings:
            candidate = voting.title.split(": ")[1]
            casted_votes = CastedVote.objects.filter(voting=voting, voting_right=right)
            for casted_vote in casted_votes:
                if not casted_vote.choice.label == "A":
                    votings_dict[candidate] = int(casted_vote.choice.label)
        votings_list.append(votings_dict)
    return votings_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate the Steering Committee votes."
    )
    parser.add_argument(
        "--num_winners", type=int, help="Number of winners to select (int)."
    )
    parser.add_argument(
        "--rank_of_empty_preference", type=int, help="Rank of empty preference (int)."
    )
    args = parser.parse_args()

    votings_list = get_votings()

    candidates = list(votings_list[1].keys())

    # For the empty votings put len(candidates)+1
    empty_preference = len(candidates) + 1
    for i, voting in enumerate(votings_list):
        for candidate in candidates:
            if not candidate in voting:
                voting[candidate] = args.rank_of_empty_preference

    evaluator = condorcet.CondorcetEvaluator(candidates=candidates, votes=votings_list)
    winners, rest_of_table = evaluator.get_n_winners(args.num_winners)

    print(f"FROM CANDIDATES:\n{candidates}")
    print(f"WINNERS:\n{winners}\n\n")
    print(f"REST OF TABLE:\n{rest_of_table}")


# EXCEPTION FROM REGULATIONS:
# A vote for each country with the options below and the abstain option.

# Should <CountryName> be allowed to participate as a full delegation with students at IChO 2025?

# IChO regulations state that a delegation has to observe for two consecutive years before participating with students. <CountryName> has requested an exception in order to participate next year (2025) after just one observation (2024).

# We support the participation of <CountryName> with students at IChO 2025

# We think a second year of observation would be better


# STEERING COMMITTEE VOTE:
# A vote for each candidate with the number of ranks to choose from. Wording:

# Select a rank for <PersonName>.

# Select a rank for <PersonName> where a smaller numbered rank indicates a higher preference for <PersonName>. For example if <PersonName> is your top candidate, select rank 1. Select the same rank for candidates if you have no preference between them. You do not have to use all possible ranks and you do not have to select a rank for all candidates.

# 1. Top
# 2. Second
# 3. Third
# 4. Fourth
# 5. Fifth
# A. Abstain

# (For context: Abstain does not mean "I do not want this person", but results in an exclusion of your vote and it will result in as if you chose the mean rank of all votes for this person. For details: https://en.wikipedia.org/wiki/Condorcet_method)

# TO EVALUATE THE VOTE:
# There is a script in scripts/export_votes_delegations.py, which generates the input csv for a script Gabor has ready. Alternatively it can be evaluated directly on the server with the script scripts/evaluate_icho_steering_committee_votes.py
