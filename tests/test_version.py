import csv
import itertools
import os
import random
from collections import defaultdict

import requests
from diskcache import Cache

SCHEDULE_FINE_TUNING = 5
DEBUG_MODE = False
EVENT_CODE = "2023arc"

cache = Cache("./api_cache")

def fetch_matches(event_key, api_key):
    url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
    headers = {"X-TBA-Auth-Key": api_key}

    cache_key = (url, tuple(headers.items()))

    if cache_key in cache:
        return cache[cache_key]
    else:
        response = requests.get(url, headers=headers)
        matches = response.json()
        cache.set(cache_key, matches, expire=86400)
        print("Fetching new data and caching.")
        return matches

def distribute(general_number, distributive_number):
    base = general_number // distributive_number
    remainder = general_number % distributive_number
    distribution = [base] * distributive_number
    for i in range(remainder):
        distribution[i] += 1
    return distribution


def distribute_teams(matches, users):
    qm_matches = [match for match in matches if match["comp_level"] == "qm"]
    all_teams = set(
        itertools.chain.from_iterable(
            match["alliances"]["blue"]["team_keys"]
            + match["alliances"]["red"]["team_keys"]
            for match in qm_matches
        ),
    )
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
        return not conflict_graph[team].intersection(assignments[user])

    def get_chunking_score(user, team):
        team_matches = [
            match["match_number"]
            for match in qm_matches
            if team
            in match["alliances"]["blue"]["team_keys"]
            + match["alliances"]["red"]["team_keys"]
        ]
        user_matches = list(
            itertools.chain.from_iterable(
                [
                    match["match_number"]
                    for match in qm_matches
                    if assigned_team
                    in match["alliances"]["blue"]["team_keys"]
                    + match["alliances"]["red"]["team_keys"]
                ]
                for assigned_team in assignments[user]
            ),
        )
        combined_matches = sorted(team_matches + user_matches)
        gaps = [m2 - m1 for m1, m2 in zip(combined_matches, combined_matches[1:])]
        return sum(g > 4 for g in gaps)

    while team_pool:
        for user, team_count in zip(users, teams_per_user):
            if team_count == 0:
                continue

            valid_teams = [
                team for team in team_pool if is_valid_assignment(user, team)
            ]

            if valid_teams:
                team_scores = {
                    team: get_chunking_score(user, team) for team in valid_teams
                }
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


def has_duplicate_match_numbers(match_details) -> bool:
    seen_match_numbers = set()
    for match_number, _ in match_details:
        if match_number in seen_match_numbers:
            return True
        seen_match_numbers.add(match_number)
    return False


def create_scouting_schedule(assignments, matches, abnormal_users):
    schedule = defaultdict(list)
    for user, teams in assignments.items():
        for team in teams:
            for match in matches:
                if (
                    match["comp_level"] == "qm"
                    and team
                    in match["alliances"]["blue"]["team_keys"]
                    + match["alliances"]["red"]["team_keys"]
                ):
                    _, match_number = get_match_details(match["key"], matches)
                    schedule[user].append((match_number, team))

    schedule_lengths = [(user, len(matches)) for user, matches in schedule.items()]
    schedule_lengths.sort(key=lambda x: x[1])

    while True:
        user_with_most, max_length = schedule_lengths[-1]
        _, min_length = schedule_lengths[0]

        if max_length - min_length <= 1:
            break

        match_transferred = False
        for match_num, team in schedule[user_with_most]:
            for i in range(
                1, len(schedule_lengths),
            ):
                transfer_user, _ = schedule_lengths[i]

                if (
                    (match_num, team) not in schedule[transfer_user]
                    and not any(match_num == mn for mn, _ in schedule[transfer_user])
                    and not any(
                        team
                        in match["alliances"]["blue"]["team_keys"]
                        + match["alliances"]["red"]["team_keys"]
                        for mn, t in schedule[transfer_user]
                        for match in matches
                        if mn == match["match_number"]
                    )
                ):
                    schedule[user_with_most].remove((match_num, team))
                    schedule[transfer_user].append((match_num, team))
                    match_transferred = True
                    break
            if match_transferred:
                break

        if not match_transferred:
            break

        schedule_lengths[-1] = (user_with_most, max_length - 1)
        schedule_lengths[i] = (transfer_user, schedule_lengths[i][1] + 1)
        schedule_lengths.sort(key=lambda x: x[1])

    # Integrate abnormal users into the schedule and assignments
    for arrival_match, user in abnormal_users.items():
        assignments[user] = []  # Initialize assignments for the abnormal user
        available_teams = set(itertools.chain.from_iterable(assignments.values()))
        for match_num, team in schedule[user]:
            if match_num >= arrival_match and team in available_teams:
                available_teams.remove(team)
                continue  # Keep existing assignments after arrival

            # Find a suitable team to assign from available pool
            for other_user, other_matches in schedule.items():
                for other_match_num, other_team in other_matches:
                    if other_match_num >= arrival_match and other_team in available_teams:
                        # Swap teams between user and other_user
                        schedule[user].remove((match_num, team))
                        schedule[user].append((other_match_num, other_team))
                        schedule[other_user].remove((other_match_num, other_team))
                        schedule[other_user].append((match_num, team))
                        available_teams.remove(other_team)
                        break
                if other_team not in available_teams:
                    break

    return schedule


def export_schedule_to_csv(schedule, assignments, filename="./scouting_tools/scouting_schedule.csv") -> None:
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        header = ["User", "Teams"] + [f"Match {i+1}" for i in range(150)]
        writer.writerow(header)

        qualitative_matches = {}
        for match_details in schedule.values():
            for _, team in match_details:
                if team not in qualitative_matches:
                    qualitative_matches[team] = 0
        for user, match_details in schedule.items():
            row = [user, ", ".join(assignments[user])]

            match_assignments = dict(match_details)
            team_qualitative_matches = defaultdict(list)
            team_non_qualitative_matches = defaultdict(list)

            for match_num in range(1, 150):
                if (team := match_assignments.get(match_num)) is not None:
                    qualitative_matches[team] += 1
                    if qualitative_matches[team] in [2, 9]:
                        row.append(team + " QUAL")
                        team_qualitative_matches[team].append(match_num)
                    else:
                        if qualitative_matches[team] > 9:
                            team_non_qualitative_matches[team].append(match_num)
                        row.append(team)
                else:
                    row.append("-")

            writer.writerow(row)
        if DEBUG_MODE:
            print("\n",qualitative_matches, len(qualitative_matches), len(list(set(qualitative_matches.values()))) == 1)


def distribute_and_swap_matches(user_matches):
    def swap_matches(matches_list):
        all_matches = set()
        for matches in matches_list:
            all_matches.update(match[0] for match in matches)

        for i, matches in enumerate(matches_list):
            for match in matches:
                match_number, _ = match
                if sum(1 for m in matches if m[0] == match_number) > 1:
                    duplicate_match = match
                    other_users = [j for j in range(len(matches_list)) if j != i]
                    random.shuffle(other_users)
                    for other_user in other_users:
                        if duplicate_match[0] not in [
                            m[0] for m in matches_list[other_user]
                        ]:
                            matches_list[other_user].append(duplicate_match)
                            matches.remove(duplicate_match)
                            break
        return matches_list

    user_matches = swap_matches(user_matches)
    total_matches = sum(len(matches) for matches in user_matches)
    average_matches_per_user = total_matches // len(user_matches)

    users_below_average = [
        i
        for i, matches in enumerate(user_matches)
        if len(matches) < average_matches_per_user
    ]

    users_above_average = [
        i
        for i, matches in enumerate(user_matches)
        if len(matches) > average_matches_per_user
    ]

    for user_id in users_below_average:
        while len(user_matches[user_id]) < average_matches_per_user:
            for user_above in users_above_average:
                if len(user_matches[user_above]) > average_matches_per_user:
                    match_to_move = user_matches[user_above].pop(0)
                    user_matches[user_id].append(match_to_move)
                    break
            else:
                break

    return swap_matches(user_matches)



if __name__ == "__main__":
    event_key = EVENT_CODE
    api_key = os.environ.get("TBA_API_KEY")

    matches = fetch_matches(event_key, api_key)

    # users = ["User_" + str(i + 1) for i in range(20)]
    users = []
    print("EEE: ",len(users))
    random.shuffle(users)

    abnormal_users = {
        25:"USER_LATE1",
        50:"USER_LATE2"
    }

    assignments = distribute_teams(matches, users)  # Distribute among normal users
    schedule = create_scouting_schedule(assignments, matches, abnormal_users)

    for i in range(SCHEDULE_FINE_TUNING):
        updated_schedule = distribute_and_swap_matches(list(schedule.values()))
        index = 0
        for user, match_details in schedule.items():
            if index < len(updated_schedule):
                schedule[user] = updated_schedule[index]
                index += 1

    for user, md in schedule.items():
        for i in range(len(assignments[user])):
            if assignments[user][i] not in [j for _, j in md]:
                assignments[user][i] += " N.S."

    flag = False
    for user, match_details in schedule.items():
        print(f"\n{user}: {assignments[user]}")
        print(f"Schedule: \n{match_details}, \nMatch Assignments: {len(match_details)}")
        if DEBUG_MODE:
            print(f"\nDUPLICATES: {has_duplicate_match_numbers(match_details)}")
        if has_duplicate_match_numbers(match_details):
            flag = True
    if flag:
        print("-"*15+"Duplicate Match Numbers Found"+"-"*15)
    export_schedule_to_csv(schedule, assignments)
