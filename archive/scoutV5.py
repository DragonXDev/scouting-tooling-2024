import itertools
import os
import random
import sys

import requests
from dotenv import load_dotenv


def distribute_teams(matches, users):
    all_teams = set(itertools.chain.from_iterable(match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"] for match in matches if match["comp_level"] == "qm"))
    team_pool = list(all_teams)

    num_teams = len(team_pool)
    num_users = len(users)
    teams_per_user = [num_teams // num_users] * num_users
    for i in range(num_teams % num_users):
        teams_per_user[i] += 1

    d = 0
    conflict_graph = {team: set() for team in team_pool}
    for match in matches:
        if match["comp_level"] == "qm":
            d += 1
            blue_teams = match["alliances"]["blue"]["team_keys"]
            red_teams = match["alliances"]["red"]["team_keys"]
            for blue_team in blue_teams:
                conflict_graph[blue_team].update(red_teams)
            for red_team in red_teams:
                conflict_graph[red_team].update(blue_teams)
    print(f"Total matches: {len(conflict_graph)}")
    assignments = {user: [] for user in users}
    while team_pool:
        for user, team_count in zip(users, teams_per_user):
            if team_count == 0:
                continue

            valid_teams = [team for team in team_pool if not conflict_graph[team].intersection(assignments[user])]

            if valid_teams:
                team_match_numbers = {team: [match["match_number"] for match in matches if team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]] for team in valid_teams}
                team_scores = {team: sum(abs(m1 - m2) for m1, m2 in zip(numbers, numbers[1:])) for team, numbers in team_match_numbers.items()}
                best_team = min(team_scores, key=team_scores.get)
            else:
                if not team_pool:
                    break
                best_team = random.choice(team_pool)

            assignments[user].append(best_team)
            team_pool.remove(best_team)
            team_count -= 1

    return assignments

def distribute_duplicates_evenly(user_matches, duplicate_matches):
    while duplicate_matches:
        sorted_users = sorted(user_matches.keys(), key=lambda user: len(user_matches[user]))
        duplicate_info = duplicate_matches.pop(0)
        match_number, _ = duplicate_info.split(" + ")

        for user in sorted_users:
            if match_number not in user_matches[user]:
                user_matches[user].append(duplicate_info)
                break
        else:
            print(f"Could not assign duplicate match: {duplicate_info}")

    return user_matches

if __name__ == "__main__":
    load_dotenv()

    users = ["User_" + str(i) for i in range(30)]

    event_key = "2024casj"
    api_key = os.getenv("TBA_API_KEY")
    if not api_key:
        print("Error: TBA_API_KEY environment variable not set.")
        sys.exit(1)

    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
    headers = {"X-TBA-Auth-Key": api_key}
    response = requests.get(url, headers=headers)
    matches = response.json()

    assignments = distribute_teams(matches, users)

    if assignments:
        user_matches = {user: [] for user in users}
        user_match_counts = {user: 0 for user in users}

        for match in matches:
            if match["comp_level"] == "qm":
                teams_involved = set(itertools.chain.from_iterable([match["alliances"]["blue"]["team_keys"], match["alliances"]["red"]["team_keys"]]))
                for user, assigned_teams in assignments.items():
                    for alliance in ["blue", "red"]:
                        assigned_teams_in_alliance = set(assigned_teams).intersection(match["alliances"][alliance]["team_keys"])
                        if len(assigned_teams_in_alliance) == 1:
                            user_matches[user].append(match["match_number"])
                            user_match_counts[user] += 1
                        elif len(assigned_teams_in_alliance) > 1:
                            potential_users = [(user2, count) for user2, count in user_match_counts.items()
                                               if user2 != user and not set(assignments[user2]).intersection(teams_involved)
                                               and match["match_number"] not in user_matches[user2]]
                            if potential_users:
                                least_busy_user = min(potential_users, key=lambda item: item[1])[0]
                                user_matches[least_busy_user].append(match["match_number"])
                                user_match_counts[least_busy_user] += 1
                            else:
                                print(f"Unresolved conflict in match {match['match_number']}")

        duplicate_matches = []
        for user, matches in user_matches.items():
            seen_matches = set()
            unique_matches = []
            for match in matches:
                if match in seen_matches:
                    duplicate_matches.append(f"{match} + {assignments[user][0]}")
                else:
                    seen_matches.add(match)
                    unique_matches.append(match)
            user_matches[user] = unique_matches

        # Redistribute duplicates evenly
        user_matches = distribute_duplicates_evenly(user_matches, duplicate_matches)

        # Final output
        for user, teams in assignments.items():
            print(f"{user}: {teams}")
            print(f"  Observing Matches: {user_matches[user]}, LEN: {len(user_matches[user])}, DUPLICATES: {len(user_matches[user]) != len(set(user_matches[user]))}")

    else:
        print("No valid team distribution found.")

