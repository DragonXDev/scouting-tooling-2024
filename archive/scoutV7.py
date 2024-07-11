import itertools
import random
from collections import defaultdict

import requests


def distribute(general_number, distributive_number):
    base = general_number // distributive_number
    remainder = general_number % distributive_number
    distribution = [base] * distributive_number
    for i in range(remainder):
        distribution[i] += 1
    return distribution

def distribute_teams(matches, users):

    qm_matches = [match for match in matches if match["comp_level"] == "qm"]
    all_teams = set(itertools.chain.from_iterable(
        match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]
        for match in qm_matches
    ))
    team_pool = list(all_teams)

    num_teams = len(team_pool)
    num_users = len(users)

    teams_per_user = distribute(num_teams, num_users)  # Use the distribute function

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
        return not conflict_graph[team].intersection(assignments[user])

    def get_chunking_score(user, team):
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
    for match in matches_data:
        if match["key"] == match_key:
            return match["comp_level"], match["match_number"]
    return None, None

def create_scouting_schedule(assignments, matches):
    """Creates a scouting schedule with qualification match details for each user and
    balances the schedule by transferring matches from users with significantly
    more assignments to those with fewer.

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
    schedule_lengths.sort(key=lambda x: x[1])  # Sort by number of assignments

    while True:
        user_with_most, max_length = schedule_lengths[-1]
        user_with_least, min_length = schedule_lengths[0]

        if max_length - min_length <= 1:
            break  # Schedule is balanced enough

        # Find a user to transfer a match to
        for i in range(1, len(schedule_lengths)):  # Start from the second least busy
            transfer_user, transfer_length = schedule_lengths[i]
            if transfer_length < max_length - 1:
                break  # Found a suitable user
        else:
            break  # No suitable user found, can't balance further

        # Transfer a match
        match_to_transfer = schedule[user_with_most].pop()
        schedule[transfer_user].append(match_to_transfer)

        # Update lengths
        schedule_lengths[-1] = (user_with_most, max_length - 1)
        schedule_lengths[i] = (transfer_user, transfer_length + 1)
        schedule_lengths.sort(key=lambda x: x[1])

    return schedule

def handle_duplicates(schedule):
    """Handles duplicate matches in the scouting schedule by transferring them to other users.

    Args:
    ----
        schedule (dict): A dictionary mapping users to lists of match details.

    Returns:
    -------
        dict: The updated schedule with duplicates removed.

    """
    duplicates = defaultdict(list)
    for user, matches in schedule.items():
        seen = set()
        for match in matches:
            if match in seen:
                duplicates[user].append(match)
            seen.add(match)

    for user, duplicate_matches in duplicates.items():
        for match in duplicate_matches:
            for other_user, other_matches in schedule.items():
                if other_user != user and match not in other_matches:
                    other_matches.append(match)
                    break

    return schedule

def are_duplicates(schedule):
    """Checks if there are any duplicate matches in the scouting schedule.

    Args:
    ----
        schedule (dict): A dictionary mapping users to lists of match details.

    Returns:
    -------
        bool: True if there are duplicates, False otherwise.

    """
    seen = set()
    for match,_ in schedule:
        if match in seen:
            return match
        seen.add(match)

    return -1

if __name__ == "__main__":
    event_key = "2024casj"
    api_key = "U3magfm5xr9Sc7mzWuxKfDJYYD1jMtUqWiVuNbMmxdDURf7M2vHbSpxkuMjYnn4H"

    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
    headers = {"X-TBA-Auth-Key": api_key}
    response = requests.get(url, headers=headers)
    matches = response.json()

    users = ["User_" + str(i) for i in range(20)]  # Replace with your list of users

    assignments = distribute_teams(matches, users)  # Pass the original 'matches' list
    schedule = create_scouting_schedule(assignments, matches)  # Use 'matches' to get all match details

    c = 0
    for user, teams in assignments.items():
        print(f"{user}: {teams}")
        print(f"  Schedule: {schedule[user]}, LEN: {len(schedule[user])}, DUPLICATES: {are_duplicates(schedule[user])}")
        c += len(schedule[user])
    print(f"Total matches: {c}")
