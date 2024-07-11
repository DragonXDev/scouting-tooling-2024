import itertools
import random
from collections import defaultdict

import requests


def distribute_teams(matches, users):
    """Distributes teams to users for scouting qualification matches, optimizing for
    conflict avoidance, match chunking, and even distribution.

    Args:
    ----
        matches (list): A list of match dictionaries from the TBA API.
        users (list): A list of user names.

    Returns:
    -------
        dict: A dictionary mapping users to lists of assigned teams.

    """
    # Filter for qualification matches only
    qm_matches = [match for match in matches if match["comp_level"] == "qm"]

    all_teams = set(itertools.chain.from_iterable(
        match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]
        for match in qm_matches
    ))
    team_pool = list(all_teams)

    num_teams = len(team_pool)
    num_users = len(users)
    teams_per_user = [num_teams // num_users] * num_users
    for i in range(num_teams % num_users):
        teams_per_user[i] += 1

    # Create a conflict graph to track teams that have played each other
    conflict_graph = {team: set() for team in team_pool}
    for match in qm_matches:  # Use qm_matches here
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
        team_matches = [match["match_number"] for match in qm_matches  # Use qm_matches here
                        if team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]]
        user_matches = list(itertools.chain.from_iterable(
            [match["match_number"] for match in qm_matches  # Use qm_matches here
             if assigned_team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]]
            for assigned_team in assignments[user]
        ))
        combined_matches = sorted(team_matches + user_matches)
        gaps = [m2 - m1 for m1, m2 in zip(combined_matches, combined_matches[1:])]
        return sum(g > 4 for g in gaps)  # Penalize gaps larger than 4 matches

    while team_pool:
        for user, team_count in zip(users, teams_per_user):
            if team_count == 0:
                continue

            valid_teams = [team for team in team_pool if is_valid_assignment(user, team)]

            if valid_teams:
                # Prioritize conflict avoidance and chunking
                team_scores = {team: get_chunking_score(user, team) for team in valid_teams}
                best_team = min(team_scores, key=team_scores.get)
            else:
                # If no valid teams, just pick one from the pool (conflict is unavoidable)
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

def create_scouting_schedule(assignments, matches):
    """Creates a scouting schedule with qualification match details for each user.

    Args:
    ----
        assignments (dict): A dictionary mapping users to lists of assigned teams.
        matches (list): A list of match dictionaries from the TBA API.

    Returns:
    -------
        dict: A dictionary mapping users to lists of match details (tuples of
               comp_level and match_number).

    """
    schedule = defaultdict(list)
    for user, teams in assignments.items():
        for team in teams:
            for match in matches:
                if match["comp_level"] == "qm" and team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]:
                    comp_level, match_number = get_match_details(match["key"], matches)
                    schedule[user].append((comp_level, match_number))
    return schedule

if __name__ == "__main__":
    event_key = "2024cabe"
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
        print(f"  Schedule: {schedule[user]}, LEN: {len(schedule[user])}, DUPLICATES: {len(teams) - len(set(teams))}")
        c += len(schedule[user])
    print(f"Total matches: {c}")
