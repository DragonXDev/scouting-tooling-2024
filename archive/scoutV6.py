import csv
import itertools
import random
from collections import defaultdict

import requests


def distribute(general_number, distributive_number):
    """Distributes a general number among a distributive number as evenly as possible."""
    base = general_number // distributive_number
    remainder = general_number % distributive_number
    distribution = [base] * distributive_number
    for i in range(remainder):
        distribution[i] += 1
    return distribution

def distribute_teams(matches, users):
    """Distributes teams to users for scouting qualification matches, optimizing for
    conflict avoidance, match chunking, and even distribution using the
    provided `distribute` function.

    Args:
    ----
        matches (list): A list of match dictionaries from the TBA API.
        users (list): A list of user names.

    Returns:
    -------
        dict: A dictionary mapping users to lists of assigned teams.

    """
    qm_matches = [match for match in matches if match["comp_level"] == "qm"]
    all_teams = set(itertools.chain.from_iterable(
        match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]
        for match in qm_matches
    ))
    team_pool = list(all_teams)

    num_teams = len(team_pool)
    num_users = len(users)

    teams_per_user = distribute(num_teams, num_users)

    conflict_graph = {team: set() for team in team_pool}
    for match in qm_matches:
        blue_teams = match["alliances"]["blue"]["team_keys"]
        red_teams = match["alliances"]["red"]["team_keys"]
        for blue_team in blue_teams:
            conflict_graph[blue_team].update(red_teams)
        for red_team in red_teams:
            conflict_graph[red_team].update(blue_teams)

    assignments = {user: [] for user in users}

    def is_valid_assignment(user, team) -> bool:
        """Checks if assigning a team to a user is valid based on the conflict graph."""
        return not conflict_graph[team].intersection(assignments[user])

    def get_chunking_score(user, team):
        """Calculates a chunking score based on the match numbers of the team and
        the user's currently assigned teams. Lower scores are better.
        """
        team_matches = [match["match_number"] for match in qm_matches
                        if team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]]
        user_matches = list(itertools.chain.from_iterable(
            [match["match_number"] for match in qm_matches
             if assigned_team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]]
            for assigned_team in assignments[user]
        ))
        combined_matches = sorted(team_matches + user_matches)
        gaps = [m2 - m1 for m1, m2 in zip(combined_matches, combined_matches[1:])]
        return sum(g > 4 for g in gaps)

    while team_pool:
        for user, team_count in zip(users, teams_per_user):
            if team_count == 0:
                continue

            valid_teams = [team for team in team_pool if is_valid_assignment(user, team)]

            if valid_teams:
                team_scores = {team: get_chunking_score(user, team) for team in valid_teams}
                best_team = min(team_scores, key=team_scores.get)
            else:
                if not team_pool:
                    break
                best_team = random.choice(team_pool)

            assignments[user].append(best_team)
            team_pool.remove(best_team)
            team_count -= 1

    return assignments

def get_match_details(match_key, matches_data):
    """Retrieves match details (level, number) for a given match key."""
    for match in matches_data:
        if match["key"] == match_key:
            return match["comp_level"], match["match_number"]
    return None, None

def has_duplicate_match_numbers(match_details) -> bool:
    """Checks if there are duplicate match numbers in the list of match details."""
    seen_match_numbers = set()
    for match_number, _ in match_details:
        if match_number in seen_match_numbers:
            return True
        seen_match_numbers.add(match_number)
    return False

def create_scouting_schedule(assignments, matches):
    """Creates a scouting schedule with qualification match details for each user and
    balances the schedule by transferring matches from users with significantly
    more assignments to those with fewer, while respecting the conflict constraint.

    Args:
    ----
        assignments (dict): A dictionary mapping users to lists of assigned teams.
        matches (list): A list of match dictionaries from the TBA API.

    Returns:
    -------
        dict: A dictionary mapping users to lists of match details (tuples of
               match_number and team).

    """
    schedule = defaultdict(list)
    for user, teams in assignments.items():
        for team in teams:
            for match in matches:
                if match["comp_level"] == "qm" and team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]:
                    comp_level, match_number = get_match_details(match["key"], matches)
                    schedule[user].append((match_number, team))

    # Balance the schedule
    schedule_lengths = [(user, len(matches)) for user, matches in schedule.items()]
    schedule_lengths.sort(key=lambda x: x[1])

    while True:
        user_with_most, max_length = schedule_lengths[-1]
        user_with_least, min_length = schedule_lengths[0]

        if max_length - min_length <= 1:
            break

        # Find a match to transfer and a suitable user to transfer it to
        match_transferred = False
        for match_num, team in schedule[user_with_most]:
            for i in range(1, len(schedule_lengths)):  # Start from the second least busy
                transfer_user, _ = schedule_lengths[i]

                # Check for conflicts and match number duplication
                if (match_num, team) not in schedule[transfer_user] and \
                   not any(match_num == mn for mn, _ in schedule[transfer_user]) and \
                   not any(team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]
                           for mn, t in schedule[transfer_user]
                           for match in matches if mn == match["match_number"]):

                    # Transfer the match
                    schedule[user_with_most].remove((match_num, team))
                    schedule[transfer_user].append((match_num, team))
                    match_transferred = True
                    break  # Move on to the next iteration of the outer loop
            if match_transferred:
                break  # A match was transferred, so update lengths and continue

        if not match_transferred:
            break  # No match could be transferred without conflict, so stop

        # Update lengths
        schedule_lengths[-1] = (user_with_most, max_length - 1)
        schedule_lengths[i] = (transfer_user, schedule_lengths[i][1] + 1)
        schedule_lengths.sort(key=lambda x: x[1])

    return schedule


def export_schedule_to_csv(schedule, filename="scouting_schedule.csv") -> None:
    """Exports the scouting schedule to a CSV file with user, team assignments,
    and match columns indicating which team each user scouts in each match.

    Args:
    ----
        schedule (dict): The scouting schedule as a dictionary mapping users
                         to lists of match details (match_number, team).
        filename (str, optional): The name of the CSV file to create.
                                  Defaults to "scouting_schedule.csv".

    """
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Write header row
        header = ["User", "Teams"] + [f"Match {i+1}" for i in range(90)]
        writer.writerow(header)

        for user, match_details in schedule.items():
            teams = sorted({team for _, team in match_details})
            row = [user, ", ".join(teams)]

            # Create a dictionary to quickly look up the team for each match
            match_assignments = dict(match_details)

            # Fill in match columns
            for match_num in range(1, 91):
                row.append(match_assignments.get(match_num, "-"))

            writer.writerow(row)
if __name__ == "__main__":
    event_key = "2024casj"
    api_key = "U3magfm5xr9Sc7mzWuxKfDJYYD1jMtUqWiVuNbMmxdDURf7M2vHbSpxkuMjYnn4H"

    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
    headers = {"X-TBA-Auth-Key": api_key}
    response = requests.get(url, headers=headers)
    matches = response.json()

    users = ["User_" + str(i) for i in range(20)]

    assignments = distribute_teams(matches, users)
    schedule = create_scouting_schedule(assignments, matches)

    for user, teams in assignments.items():
        print(f"{user}: {teams}")

    for user, match_details in schedule.items():
        teams = sorted({team for _, team in match_details})
        print(f"{user}: {teams}")
        print(f"  Schedule: {match_details}, LEN: {len(match_details)}, DUPLICATES: {has_duplicate_match_numbers(match_details)}")


    export_schedule_to_csv(schedule)
