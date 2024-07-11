
# Initialize the last user index used for swapping
last_user_index = 0
def distribute_and_swap_matches(user_matches):
    # Define the swap_matches function
    def swap_matches(matches_list):
        global last_user_index
        all_matches = set()
        for matches in matches_list:
            all_matches.update(match[0] for match in matches)

        for i, matches in enumerate(matches_list):
            for match in matches:
                match_number, _ = match
                if sum(1 for m in matches if m[0] == match_number) > 1:
                    duplicate_match = match
                    # Start searching for other valid users to swap with from the next index onwards
                    # other_users = list(range(last_user_index + 1, len(matches_list))) + list(range(last_user_index))
                    other_users = [j for j in range(last_user_index,len(matches_list)) if j != i]
                    for other_user in other_users:
                        if duplicate_match not in matches_list[other_user]:
                            last_user_index+=1
                            matches_list[other_user].append(duplicate_match)
                            matches.remove(duplicate_match)
                            break
        return matches_list

    # Perform the initial swapping to resolve duplicates
    user_matches = swap_matches(user_matches)

    # Count the total number of matches and the average matches per user
    total_matches = sum(len(matches) for matches in user_matches)
    average_matches_per_user = total_matches // len(user_matches)

    # Find the users with fewer matches than average
    users_below_average = [i for i, matches in enumerate(user_matches) if len(matches) < average_matches_per_user]

    # Find the users with more matches than average
    users_above_average = [i for i, matches in enumerate(user_matches) if len(matches) > average_matches_per_user]

    # Calculate the total number of unique teams across all users
    all_unique_teams = set()
    for matches in user_matches:
        all_unique_teams.update(match[1] for match in matches)

    # Calculate the average number of unique teams per user
    len(all_unique_teams) / len(user_matches)

    # Distribute excess unique teams from users_above_average to users_below_average
    for user_id in users_below_average:
        while len(user_matches[user_id]) < average_matches_per_user:
            for user_above in users_above_average:
                if len(user_matches[user_above]) > average_matches_per_user:
                    # Find a match from the user_above with a unique team not present in user_id's matches
                    match_to_move = next(
                        (match for match in user_matches[user_above] if match[1] not in {m[1] for m in user_matches[user_id]}),
                        None,
                    )
                    if match_to_move:
                        user_matches[user_above].remove(match_to_move)
                        user_matches[user_id].append(match_to_move)
                        print(f"Distributed match {match_to_move} from user {user_above} to user {user_id}")
                    else:
                        break  # Break the loop if no match is found to distribute
            else:
                break  # Break the loop if no more matches can be distributed

    # Perform swapping again after distribution to ensure no duplicates
    return swap_matches(user_matches)


# Example usage:
user_matches = [
[(78, "frc6619"), (79, "frc9609"), (63, "frc766"), (82, "frc7137"), (8, "frc4669"), (60, "frc8159"), (83, "frc8852"), (35, "frc9038"), (69, "frc6418"), (67, "frc8793"), (2, "frc5985"), (13, "frc972"), (22, "frc7401"), (41, "frc5419"), (84, "frc5419"), (14, "frc1678"), (4, "frc7667"), (81, "frc4159"), (24, "frc7419"), (85, "frc3256"), (34, "frc4990"), (30, "frc1700"), (58, "frc9634"), (85, "frc4186"), (25, "frc4669"), (88, "frc841"), (22, "frc5985"), (15, "frc7729"), (40, "frc972"), (58, "frc6059")],

[(19, "frc9609"), (29, "frc9609"), (40, "frc9609"), (50, "frc9609"), (59, "frc9609"), (69, "frc9609"), (8, "frc9609"), (87, "frc9609"), (12, "frc766"), (21, "frc766"), (31, "frc766"), (4, "frc766"), (49, "frc766"), (56, "frc766"), (73, "frc766"), (83, "frc766"), (1, "frc3045"), (18, "frc3045"), (25, "frc3045"), (33, "frc3045"), (41, "frc3045"), (54, "frc3045"), (63, "frc3045"), (79, "frc3045"), (89, "frc3045"), (66, "frc9545"), (85, "frc6619"), (30, "frc751"), (14, "frc841"), (67, "frc1700")],

[(20, "frc9781"), (30, "frc9781"), (37, "frc9781"), (49, "frc9781"), (60, "frc9781"), (70, "frc9781"), (78, "frc9781"), (8, "frc9781"), (88, "frc9781"), (19, "frc7137"), (26, "frc7137"), (34, "frc7137"), (42, "frc7137"), (51, "frc7137"), (63, "frc7137"), (74, "frc7137"), (9, "frc7137"), (12, "frc9470"), (2, "frc9470"), (24, "frc9470"), (38, "frc9470"), (46, "frc9470"), (54, "frc9470"), (61, "frc9470"), (72, "frc9470"), (82, "frc9470"), (17, "frc9545")],

[(18, "frc4669"), (32, "frc4669"), (48, "frc4669"), (56, "frc4669"), (68, "frc4669"), (76, "frc4669"), (84, "frc4669"), (19, "frc581"), (28, "frc581"), (37, "frc581"), (44, "frc581"), (52, "frc581"), (64, "frc581"), (7, "frc581"), (72, "frc581"), (86, "frc581"), (16, "frc9202"), (23, "frc9202"), (31, "frc9202"), (42, "frc9202"), (57, "frc9202"), (70, "frc9202"), (8, "frc9202"), (80, "frc9202"), (90, "frc9202"), (25, "frc9545")],

[(17, "frc8159"), (27, "frc8159"), (39, "frc8159"), (49, "frc8159"), (69, "frc8159"), (79, "frc8159"), (86, "frc8159"), (9, "frc8159"), (13, "frc5940"), (29, "frc5940"), (37, "frc5940"), (48, "frc5940"), (5, "frc5940"), (56, "frc5940"), (63, "frc5940"), (71, "frc5940"), (81, "frc5940"), (10, "frc8045"), (19, "frc8045"), (28, "frc8045"), (38, "frc8045"), (47, "frc8045"), (60, "frc8045"), (67, "frc8045"), (76, "frc8045"), (90, "frc8045"), (36, "frc9545")],

[(15, "frc6884"), (26, "frc6884"), (33, "frc6884"), (48, "frc6884"), (57, "frc6884"), (67, "frc6884"), (7, "frc6884"), (78, "frc6884"), (87, "frc6884"), (11, "frc751"), (2, "frc751"), (37, "frc751"), (47, "frc751"), (55, "frc751"), (62, "frc751"), (71, "frc751"), (84, "frc751"), (18, "frc4904"), (30, "frc4904"), (38, "frc4904"), (45, "frc4904"), (52, "frc4904"), (66, "frc4904"), (73, "frc4904"), (81, "frc4904"), (9, "frc4904"), (46, "frc9545")],

[(10, "frc8852"), (17, "frc8852"), (25, "frc8852"), (32, "frc8852"), (45, "frc8852"), (52, "frc8852"), (61, "frc8852"), (71, "frc8852"), (15, "frc9038"), (22, "frc9038"), (44, "frc9038"), (54, "frc9038"), (62, "frc9038"), (74, "frc9038"), (8, "frc9038"), (83, "frc9038"), (20, "frc1458"), (28, "frc1458"), (35, "frc1458"), (43, "frc1458"), (58, "frc1458"), (68, "frc1458"), (77, "frc1458"), (87, "frc1458"), (9, "frc1458"), (5, "frc9545"), (59, "frc9545")],

[(10, "frc199"), (18, "frc199"), (26, "frc199"), (37, "frc199"), (49, "frc199"), (58, "frc199"), (68, "frc199"), (80, "frc199"), (90, "frc199"), (14, "frc114"), (21, "frc114"), (39, "frc114"), (47, "frc114"), (54, "frc114"), (61, "frc114"), (7, "frc114"), (71, "frc114"), (81, "frc114"), (1, "frc4255"), (11, "frc4255"), (23, "frc4255"), (35, "frc4255"), (45, "frc4255"), (56, "frc4255"), (64, "frc4255"), (75, "frc4255"), (88, "frc4255")],

[(19, "frc7245"), (27, "frc7245"), (35, "frc7245"), (42, "frc7245"), (5, "frc7245"), (51, "frc7245"), (61, "frc7245"), (78, "frc7245"), (89, "frc7245"), (16, "frc5274"), (24, "frc5274"), (31, "frc5274"), (41, "frc5274"), (52, "frc5274"), (62, "frc5274"), (76, "frc5274"), (88, "frc5274"), (9, "frc5274"), (20, "frc5507"), (28, "frc5507"), (3, "frc5507"), (39, "frc5507"), (47, "frc5507"), (56, "frc5507"), (66, "frc5507"), (73, "frc5507"), (82, "frc5507")],

[(11, "frc6418"), (29, "frc6418"), (3, "frc6418"), (38, "frc6418"), (48, "frc6418"), (59, "frc6418"), (77, "frc6418"), (90, "frc6418"), (2, "frc841"), (26, "frc841"), (40, "frc841"), (50, "frc841"), (58, "frc841"), (65, "frc841"), (73, "frc841"), (14, "frc3482"), (21, "frc3482"), (37, "frc3482"), (46, "frc3482"), (57, "frc3482"), (6, "frc3482"), (69, "frc3482"), (76, "frc3482"), (89, "frc3482"), (74, "frc9545"), (88, "frc9545")],

[(18, "frc8793"), (29, "frc8793"), (39, "frc8793"), (46, "frc8793"), (55, "frc8793"), (75, "frc8793"), (83, "frc8793"), (9, "frc8793"), (12, "frc5985"), (32, "frc5985"), (42, "frc5985"), (53, "frc5985"), (67, "frc5985"), (79, "frc5985"), (86, "frc5985"), (2, "frc7729"), (28, "frc7729"), (35, "frc7729"), (50, "frc7729"), (59, "frc7729"), (70, "frc7729"), (80, "frc7729"), (89, "frc7729"), (15, "frc4186"), (22, "frc4186")],

[(1, "frc972"), (23, "frc972"), (49, "frc972"), (59, "frc972"), (66, "frc972"), (76, "frc972"), (84, "frc972"), (13, "frc7401"), (33, "frc7401"), (4, "frc7401"), (43, "frc7401"), (51, "frc7401"), (69, "frc7401"), (80, "frc7401"), (88, "frc7401"), (14, "frc7840"), (22, "frc7840"), (3, "frc7840"), (31, "frc7840"), (42, "frc7840"), (55, "frc7840"), (63, "frc7840"), (72, "frc7840"), (87, "frc7840"), (40, "frc4186"), (47, "frc4186")],

[(11, "frc5419"), (21, "frc5419"), (3, "frc5419"), (33, "frc5419"), (53, "frc5419"), (61, "frc5419"), (74, "frc5419"), (15, "frc2204"), (23, "frc2204"), (32, "frc2204"), (41, "frc2204"), (51, "frc2204"), (65, "frc2204"), (7, "frc2204"), (72, "frc2204"), (81, "frc2204"), (16, "frc649"), (28, "frc649"), (36, "frc649"), (4, "frc649"), (45, "frc649"), (54, "frc649"), (69, "frc649"), (77, "frc649"), (84, "frc649"), (56, "frc4186"), (6, "frc4186")],

[(25, "frc1678"), (38, "frc1678"), (49, "frc1678"), (5, "frc1678"), (57, "frc1678"), (65, "frc1678"), (75, "frc1678"), (82, "frc1678"), (14, "frc7667"), (24, "frc7667"), (34, "frc7667"), (45, "frc7667"), (59, "frc7667"), (68, "frc7667"), (78, "frc7667"), (86, "frc7667"), (13, "frc6238"), (26, "frc6238"), (35, "frc6238"), (4, "frc6238"), (46, "frc6238"), (53, "frc6238"), (62, "frc6238"), (72, "frc6238"), (85, "frc6238"), (70, "frc4186"), (77, "frc4186")],

[(12, "frc9519"), (23, "frc9519"), (3, "frc9519"), (36, "frc9519"), (44, "frc9519"), (52, "frc9519"), (68, "frc9519"), (75, "frc9519"), (89, "frc9519"), (10, "frc4159"), (20, "frc4159"), (27, "frc4159"), (40, "frc4159"), (48, "frc4159"), (55, "frc4159"), (64, "frc4159"), (74, "frc4159"), (16, "frc4698"), (25, "frc4698"), (34, "frc4698"), (43, "frc4698"), (54, "frc4698"), (6, "frc4698"), (62, "frc4698"), (73, "frc4698"), (81, "frc4698"), (11, "frc6619")],

[(20, "frc2854"), (27, "frc2854"), (36, "frc2854"), (43, "frc2854"), (53, "frc2854"), (63, "frc2854"), (7, "frc2854"), (76, "frc2854"), (83, "frc2854"), (10, "frc7419"), (17, "frc7419"), (33, "frc7419"), (42, "frc7419"), (52, "frc7419"), (65, "frc7419"), (77, "frc7419"), (85, "frc7419"), (11, "frc2288"), (24, "frc2288"), (32, "frc2288"), (4, "frc2288"), (44, "frc2288"), (60, "frc2288"), (70, "frc2288"), (79, "frc2288"), (87, "frc2288"), (2, "frc6619")],

[(1, "frc3256"), (20, "frc3256"), (29, "frc3256"), (36, "frc3256"), (44, "frc3256"), (51, "frc3256"), (61, "frc3256"), (73, "frc3256"), (18, "frc4990"), (27, "frc4990"), (3, "frc4990"), (50, "frc4990"), (57, "frc4990"), (64, "frc4990"), (71, "frc4990"), (85, "frc4990"), (12, "frc1160"), (26, "frc1160"), (34, "frc1160"), (41, "frc1160"), (5, "frc1160"), (55, "frc1160"), (70, "frc1160"), (77, "frc1160"), (86, "frc1160"), (21, "frc6619"), (31, "frc6619")],

[(10, "frc5430"), (19, "frc5430"), (30, "frc5430"), (39, "frc5430"), (46, "frc5430"), (53, "frc5430"), (62, "frc5430"), (80, "frc5430"), (87, "frc5430"), (15, "frc4973"), (24, "frc4973"), (31, "frc4973"), (43, "frc4973"), (51, "frc4973"), (6, "frc4973"), (64, "frc4973"), (75, "frc4973"), (84, "frc4973"), (1, "frc6814"), (12, "frc6814"), (22, "frc6814"), (32, "frc6814"), (50, "frc6814"), (57, "frc6814"), (66, "frc6814"), (78, "frc6814"), (90, "frc6814")],

[(16, "frc9111"), (23, "frc9111"), (33, "frc9111"), (44, "frc9111"), (5, "frc9111"), (53, "frc9111"), (64, "frc9111"), (71, "frc9111"), (82, "frc9111"), (17, "frc2637"), (29, "frc2637"), (40, "frc2637"), (47, "frc2637"), (60, "frc2637"), (68, "frc2637"), (7, "frc2637"), (80, "frc2637"), (89, "frc2637"), (13, "frc254"), (21, "frc254"), (36, "frc254"), (45, "frc254"), (55, "frc254"), (6, "frc254"), (65, "frc254"), (79, "frc254"), (90, "frc254")],

[(13, "frc1700"), (38, "frc1700"), (50, "frc1700"), (6, "frc1700"), (60, "frc1700"), (74, "frc1700"), (86, "frc1700"), (17, "frc9634"), (27, "frc9634"), (34, "frc9634"), (41, "frc9634"), (67, "frc9634"), (75, "frc9634"), (8, "frc9634"), (82, "frc9634"), (1, "frc6059"), (16, "frc6059"), (30, "frc6059"), (39, "frc6059"), (48, "frc6059"), (65, "frc6059"), (72, "frc6059"), (83, "frc6059"), (43, "frc6619"), (58, "frc6619"), (66, "frc6619")],
]
# Print original matches
print("Original matches:")
for user_id, matches in enumerate(user_matches):
    unique_teams = {match[1] for match in matches}
    print(f"user {user_id}: {matches}\nTotal Matches: {len(matches)}, "
          f"\nUnique Teams: {len(unique_teams)}")

updated_user_matches = distribute_and_swap_matches(user_matches)
for user_id, matches in enumerate(updated_user_matches):
    unique_teams = {match[1] for match in matches}
    print(f"user {user_id}: {matches}\nTotal Matches: {len(matches)}, "
          f"\nUnique Teams: {len(unique_teams)}")
