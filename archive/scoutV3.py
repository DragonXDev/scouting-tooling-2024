import collections
import csv

import requests

event_key = "2024cabe"  # Replace with your event key
api_key = "U3magfm5xr9Sc7mzWuxKfDJYYD1jMtUqWiVuNbMmxdDURf7M2vHbSpxkuMjYnn4H"  # Replace with your TBA API key

url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches"
headers = {"X-TBA-Auth-Key": api_key}
response = requests.get(url, headers=headers)
matches = response.json()

people = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Emily",
    "Frank",
    "Grace",
    "Henry",
    "Isabella",
    "Jack",
    "Katie",
    "Liam",
    "Mia",
    "Noah",
    "Olivia",
    "Ethan",
    "Ava",
    "Sophia",
]  # Replace with your list of people


def sort_key(match):
    comp_level_order = {"qm": 1, "ef": 2, "qf": 3, "sf": 4, "f": 5}
    return (comp_level_order.get(match["comp_level"], 6), match["match_number"])


matches = [match for match in matches if match["comp_level"] == "qm"]
sorted_matches = sorted(matches, key=sort_key)

formatted_matches = []
for match in sorted_matches:
    red_teams = match["alliances"]["red"]["team_keys"]
    blue_teams = match["alliances"]["blue"]["team_keys"]
    formatted_match = (tuple(red_teams), tuple(blue_teams))
    formatted_matches.append(formatted_match)

print("Pulled ", len(formatted_matches), " matches")


def assign_scouting(formatted_matches, people):
    """Assigns people to scout teams in matches, optimizing for spaced-out assignments."""
    num_people = len(people)
    teams_per_person = (
        len(
            {
                team
                for match in formatted_matches
                for alliance in match
                for team in alliance
            },
        )
        // num_people
    )

    assignments = {person: [] for person in people}
    slots_remaining = {person: teams_per_person for person in people}
    team_assignments = {}

    def is_valid_assignment(person, team, match_index, formatted_matches) -> bool:
        """Checks if assigning a team to a person for a specific match is valid."""
        if team in assignments[person]:
            return False
        for future_match_index in range(match_index, len(formatted_matches)):
            future_match = formatted_matches[future_match_index]
            for existing_team in assignments[person]:
                if any(existing_team in alliance for alliance in future_match) or any(
                    team in alliance for alliance in future_match
                ):
                    return False
        return True

    for match_index, match in enumerate(formatted_matches):
        assigned_people_in_match = set()
        for alliance in match:
            for team in alliance:
                if team not in team_assignments:
                    for person in people:
                        if (
                            person not in assigned_people_in_match
                            and slots_remaining[person] > 0
                            and is_valid_assignment(
                                person, team, match_index, formatted_matches,
                            )
                        ):
                            assignments[person].append(team)
                            slots_remaining[person] -= 1
                            assigned_people_in_match.add(person)
                            team_assignments[team] = person
                            break

    unassigned_teams = [
        team
        for team in {
            team
            for match in formatted_matches
            for alliance in match
            for team in alliance
        }
        if team not in team_assignments
    ]
    for team in unassigned_teams:
        conflicting_people = set()
        for person, assigned_teams in assignments.items():
            for match in formatted_matches:
                if team in match[0] or team in match[1]:
                    for assigned_team in assigned_teams:
                        if assigned_team in match[0] or assigned_team in match[1]:
                            conflicting_people.add(person)
                            break
        best_person = None
        for person in people:
            if person not in conflicting_people and slots_remaining[person] > 0:
                best_person = person
                break
        if best_person is None:
            min_conflicts = float("inf")
            for person, assigned_teams in assignments.items():
                conflicts = 0
                for match in formatted_matches:
                    if team in match[0] or team in match[1]:
                        for assigned_team in assigned_teams:
                            if assigned_team in match[0] or assigned_team in match[1]:
                                conflicts += 1
                if conflicts < min_conflicts and slots_remaining[person] > 0:
                    min_conflicts = conflicts
                    best_person = person
        if best_person is not None:
            assignments[best_person].append(team)
            slots_remaining[best_person] -= 1
            team_assignments[team] = best_person
            if best_person in conflicting_people:
                for conflicting_team in list(
                    assignments[best_person],
                ):  # Iterate over a copy
                    if any(
                        conflicting_team in alliance and team in alliance
                        for match in formatted_matches
                        for alliance in match
                    ):
                        for other_person in people:
                            if (
                                other_person != best_person
                                and slots_remaining[other_person] > 0
                                and is_valid_assignment(
                                    other_person, conflicting_team, 0, formatted_matches,
                                )
                            ):
                                assignments[other_person].append(conflicting_team)
                                assignments[best_person].remove(conflicting_team)
                                slots_remaining[other_person] -= 1
                                slots_remaining[best_person] += 1
                                team_assignments[conflicting_team] = other_person
                                break

    return assignments


scouting_assignments = assign_scouting(formatted_matches, people)


def get_match_details(match_key, matches_data):
    """Retrieves match details (level, number) for a given match key."""
    for match in matches_data:
        if match["key"] == match_key:
            return match["comp_level"], match["match_number"]
    return None, None


def resolve_duplicates(scouting_assignments, matches) -> None:
    """Resolves duplicate assignments by reassigning matches with team context."""
    # print("I ESSSSSSSSSSSSSSSSS", team_counts)
    team_counts = collections.defaultdict(int)
    for person, teams in scouting_assignments.items():
        for team in teams:
            team_counts[team] += 1

    reassignments = []
    for person, teams in scouting_assignments.items():
        match_details = []
        for team in teams:
            for match in matches:
                if (
                    team in match["alliances"]["red"]["team_keys"]
                    or team in match["alliances"]["blue"]["team_keys"]
                ):
                    comp_level, match_number = get_match_details(match["key"], matches)
                    match_detail = (
                        f"{comp_level}{match_number} + {team}"  # Add team context
                    )
                    match_details.append(match_detail)
                    if team_counts[team] > 1:
                        reassignments.append((person, match_detail, team))
                        team_counts[team] -= 1  # Reduce count after reassignment

        print(f"{person}: {sorted(teams)}")
        print("  Matches:", sorted(match_details))
        print()

    reassignments.sort(key=lambda x: len(scouting_assignments[x[0]]))
    print("REEEEEEEEASSSIGNEMNTS: ", reassignments)
    for person, match_detail, team in reassignments:
        for other_person, other_teams in scouting_assignments.items():
            if other_person != person and team not in other_teams:
                scouting_assignments[other_person].append(team)
                print(f"Reassigned {match_detail} from {person} to {other_person}")
                break


def export_to_csv(scouting_assignments, matches, filename="scouting_assignments.csv") -> None:
    """Exports scouting assignments and match details to a CSV file."""
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Person", "Teams", "Matches"])
        for person, teams in scouting_assignments.items():
            match_details = []
            for team in teams:
                for match in matches:
                    if (
                        team in match["alliances"]["red"]["team_keys"]
                        or team in match["alliances"]["blue"]["team_keys"]
                    ):
                        comp_level, match_number = get_match_details(
                            match["key"], matches,
                        )
                        {
                            "qm": "QM",
                        }.get(comp_level, "Unknown Match Type")
                        match_details.append(f"{team}")
            writer.writerow(
                [person, ", ".join(teams), ", ".join(sorted(match_details))],
            )


def generate_google_sheets_script(scouting_assignments, matches):
    """Generates Google Sheets script to populate a sheet with scouting assignments."""
    script = """
function populateSheet() {
  var scoutingAssignments = [
"""
    for person, teams in scouting_assignments.items():
        match_details = []
        for team in teams:
            for match in matches:
                if (
                    team in match["alliances"]["red"]["team_keys"]
                    or team in match["alliances"]["blue"]["team_keys"]
                ):
                    comp_level, match_number = get_match_details(match["key"], matches)
                    match_type = {
                        "qm": "QM",
                    }.get(comp_level, "Unknown Match Type")
                    match_details.append(f"{match_type} {match_number} + {team}")
        script += f"    ['{person}', '{', '.join(teams)}', '{', '.join(sorted(match_details))}'],\n"

    script += """
  ];

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.clear(); // Clear existing data

  // Set headers
  var headers = ["Person", "Teams", "Matches"];
  sheet.appendRow(headers);

  // Paste data
  for (var i = 0; i < scoutingAssignments.length; i++) {
    sheet.appendRow(scoutingAssignments[i]);
  }
}
"""
    return script


google_sheets_script = generate_google_sheets_script(scouting_assignments, matches)

# Save the script to a file
with open("google_sheets_script.gs", "w") as script_file:
    script_file.write(google_sheets_script)

print("Google Sheets script generated successfully!")


resolve_duplicates(scouting_assignments, matches)
export_to_csv(scouting_assignments, matches)

if any(
    len(details) != len(set(details))
    for details in [details for _, details in scouting_assignments.items()]
):
    print("-" * 20, "DUPLICATES FOUND (after resolution attempt)", "-" * 20)

print("HERE")
