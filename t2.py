def distribute_and_swap_matches(user_matches):
    # Define the swap_matches function
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
                    for other_user in other_users:
                        if duplicate_match not in matches_list[other_user]:
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

    # Distribute excess matches from users_above_average to users_below_average
    for user_id in users_below_average:
        while len(user_matches[user_id]) < average_matches_per_user:
            for user_above in users_above_average:
                if len(user_matches[user_above]) > average_matches_per_user:
                    match_to_move = user_matches[user_above].pop(0)
                    user_matches[user_id].append(match_to_move)
                    print(f"Distributed match {match_to_move} from user {user_above} to user {user_id}")
                    break
            else:
                break  # Break the loop if no more matches can be distributed

    # Perform swapping again after distribution to ensure no duplicates
    return swap_matches(user_matches)


# Example usage:
user_matches = [
    [(15, "frc668"), (26, "frc668"), (3, "frc668"), (30, "frc668"), (40, "frc668"), (45, "frc668"), (54, "frc668"), (57, "frc668"), (65, "frc668"), (77, "frc668"), (8, "frc668"), (11, "frc670"), (19, "frc670"), (22, "frc670"), (30, "frc670"), (36, "frc670"), (46, "frc670"), (5, "frc670"), (51, "frc670"), (61, "frc670"), (69, "frc670"), (74, "frc670")],
    [(1, "frc6918"), (14, "frc6918"), (20, "frc6918"), (27, "frc6918"), (32, "frc6918"), (36, "frc6918"), (43, "frc6918"), (51, "frc6918"), (57, "frc6918"), (68, "frc6918"), (72, "frc6918"), (11, "frc7419"), (16, "frc7419"), (2, "frc7419"), (23, "frc7419"), (29, "frc7419"), (39, "frc7419"), (44, "frc7419"), (54, "frc7419"), (60, "frc7419"), (67, "frc7419"), (77, "frc7419")],
    [(12, "frc1678"), (20, "frc1678"), (26, "frc1678"), (35, "frc1678"), (39, "frc1678"), (46, "frc1678"), (53, "frc1678"), (57, "frc1678"), (69, "frc1678"), (7, "frc1678"), (76, "frc1678"), (15, "frc2288"), (22, "frc2288"), (32, "frc2288"), (39, "frc2288"), (4, "frc2288"), (43, "frc2288"), (52, "frc2288"), (60, "frc2288"), (65, "frc2288"), (75, "frc2288"), (9, "frc2288")],
    [(12, "frc3309"), (16, "frc3309"), (27, "frc3309"), (30, "frc3309"), (37, "frc3309"), (4, "frc3309"), (43, "frc3309"), (50, "frc3309"), (58, "frc3309"), (67, "frc3309"), (74, "frc3309"), (13, "frc9470"), (18, "frc9470"), (28, "frc9470"), (32, "frc9470"), (37, "frc9470"), (46, "frc9470"), (53, "frc9470"), (60, "frc9470"), (66, "frc9470"), (7, "frc9470"), (72, "frc9470")],
    [(21, "frc3256"), (26, "frc3256"), (34, "frc3256"), (38, "frc3256"), (46, "frc3256"), (55, "frc3256"), (6, "frc3256"), (62, "frc3256"), (67, "frc3256"), (72, "frc3256"), (9, "frc3256"), (12, "frc2035"), (18, "frc2035"), (2, "frc2035"), (28, "frc2035"), (31, "frc2035"), (40, "frc2035"), (47, "frc2035"), (56, "frc2035"), (63, "frc2035"), (68, "frc2035"), (76, "frc2035")],
    [(10, "frc2367"), (15, "frc2367"), (2, "frc2367"), (24, "frc2367"), (32, "frc2367"), (42, "frc2367"), (49, "frc2367"), (55, "frc2367"), (59, "frc2367"), (69, "frc2367"), (73, "frc2367"), (1, "frc253"), (18, "frc253"), (25, "frc253"), (33, "frc253"), (42, "frc253"), (47, "frc253"), (53, "frc253"), (62, "frc253"), (67, "frc253"), (71, "frc253"), (8, "frc253")],
    [(16, "frc5027"), (28, "frc5027"), (34, "frc5027"), (39, "frc5027"), (49, "frc5027"), (5, "frc5027"), (53, "frc5027"), (58, "frc5027"), (64, "frc5027"), (71, "frc5027"), (8, "frc5027"), (12, "frc987"), (21, "frc987"), (25, "frc987"), (31, "frc987"), (37, "frc987"), (45, "frc987"), (51, "frc987"), (59, "frc987"), (6, "frc987"), (66, "frc987"), (71, "frc987")],
    [(1, "frc841"), (13, "frc841"), (16, "frc841"), (22, "frc841"), (35, "frc841"), (41, "frc841"), (47, "frc841"), (55, "frc841"), (63, "frc841"), (66, "frc841"), (75, "frc841"), (12, "frc7413"), (15, "frc7413"), (22, "frc7413"), (33, "frc7413"), (38, "frc7413"), (49, "frc7413"), (56, "frc7413"), (61, "frc7413"), (65, "frc7413"), (7, "frc7413"), (72, "frc7413")],
    [(14, "frc6238"), (21, "frc6238"), (24, "frc6238"), (35, "frc6238"), (40, "frc6238"), (48, "frc6238"), (54, "frc6238"), (60, "frc6238"), (64, "frc6238"), (7, "frc6238"), (74, "frc6238"), (11, "frc3859"), (18, "frc3859"), (22, "frc3859"), (29, "frc3859"), (36, "frc3859"), (45, "frc3859"), (50, "frc3859"), (58, "frc3859"), (6, "frc3859"), (65, "frc3859"), (71, "frc3859")],
    [(14, "frc100"), (18, "frc100"), (23, "frc100"), (33, "frc100"), (40, "frc100"), (43, "frc100"), (55, "frc100"), (6, "frc100"), (61, "frc100"), (70, "frc100"), (76, "frc100"), (10, "frc4990"), (15, "frc4990"), (23, "frc4990"), (3, "frc4990"), (34, "frc4990"), (37, "frc4990"), (47, "frc4990"), (52, "frc4990"), (57, "frc4990"), (64, "frc4990"), (74, "frc4990")],
    [(16, "frc2073"), (25, "frc2073"), (29, "frc2073"), (3, "frc2073"), (38, "frc2073"), (43, "frc2073"), (50, "frc2073"), (63, "frc2073"), (69, "frc2073"), (73, "frc2073"), (9, "frc2073"), (12, "frc8048"), (18, "frc8048"), (24, "frc8048"), (29, "frc8048"), (41, "frc8048"), (48, "frc8048"), (5, "frc8048"), (52, "frc8048"), (62, "frc8048"), (66, "frc8048"), (77, "frc8048")],
    [(11, "frc3008"), (19, "frc3008"), (26, "frc3008"), (33, "frc3008"), (37, "frc3008"), (44, "frc3008"), (5, "frc3008"), (56, "frc3008"), (60, "frc3008"), (68, "frc3008"), (73, "frc3008"), (2, "frc9125"), (21, "frc9125"), (27, "frc9125"), (35, "frc9125"), (41, "frc9125"), (46, "frc9125"), (52, "frc9125"), (61, "frc9125"), (70, "frc9125"), (73, "frc9125"), (8, "frc9125")],
    [(1, "frc8546"), (14, "frc8546"), (17, "frc8546"), (26, "frc8546"), (31, "frc8546"), (41, "frc8546"), (45, "frc8546"), (56, "frc8546"), (60, "frc8546"), (69, "frc8546"), (74, "frc8546"), (13, "frc6348"), (21, "frc6348"), (28, "frc6348"), (3, "frc6348"), (33, "frc6348"), (39, "frc6348"), (49, "frc6348"), (55, "frc6348"), (58, "frc6348"), (68, "frc6348"), (77, "frc6348")],
    [(19, "frc581"), (24, "frc581"), (29, "frc581"), (4, "frc581"), (42, "frc581"), (47, "frc581"), (51, "frc581"), (58, "frc581"), (69, "frc581"), (72, "frc581"), (8, "frc581"), (1, "frc5104"), (20, "frc5104"), (28, "frc5104"), (33, "frc5104"), (36, "frc5104"), (44, "frc5104"), (54, "frc5104"), (59, "frc5104"), (64, "frc5104"), (71, "frc5104"), (9, "frc5104")],
    [(10, "frc9504"), (17, "frc9504"), (23, "frc9504"), (31, "frc9504"), (42, "frc9504"), (46, "frc9504"), (50, "frc9504"), (58, "frc9504"), (68, "frc9504"), (7, "frc9504"), (75, "frc9504"), (13, "frc1351"), (19, "frc1351"), (27, "frc1351"), (3, "frc1351"), (34, "frc1351"), (42, "frc1351"), (45, "frc1351"), (54, "frc1351"), (61, "frc1351"), (66, "frc1351"), (76, "frc1351")],
    [(10, "frc1868"), (17, "frc1868"), (24, "frc1868"), (30, "frc1868"), (39, "frc1868"), (43, "frc1868"), (56, "frc1868"), (6, "frc1868"), (62, "frc1868"), (66, "frc1868"), (73, "frc1868"), (10, "frc192"), (21, "frc192"), (27, "frc192"), (31, "frc192"), (36, "frc192"), (4, "frc192"), (44, "frc192"), (53, "frc192"), (63, "frc192"), (70, "frc192"), (77, "frc192")],
    [(13, "frc604"), (20, "frc604"), (24, "frc604"), (34, "frc604"), (40, "frc604"), (44, "frc604"), (5, "frc604"), (50, "frc604"), (62, "frc604"), (65, "frc604"), (73, "frc604"), (17, "frc972"), (25, "frc972"), (31, "frc972"), (4, "frc972"), (41, "frc972"), (49, "frc972"), (54, "frc972"), (57, "frc972"), (64, "frc972"), (72, "frc972"), (9, "frc972")],
    [(13, "frc1967"), (19, "frc1967"), (23, "frc1967"), (30, "frc1967"), (38, "frc1967"), (4, "frc1967"), (48, "frc1967"), (52, "frc1967"), (59, "frc1967"), (68, "frc1967"), (71, "frc1967"), (2, "frc8404"), (20, "frc8404"), (25, "frc8404"), (29, "frc8404"), (36, "frc8404"), (48, "frc8404"), (55, "frc8404"), (61, "frc8404"), (64, "frc8404"), (75, "frc8404"), (8, "frc8404")],
    [(14, "frc5026"), (17, "frc5026"), (2, "frc5026"), (22, "frc5026"), (34, "frc5026"), (37, "frc5026"), (48, "frc5026"), (51, "frc5026"), (63, "frc5026"), (67, "frc5026"), (77, "frc5026"), (14, "frc3189"), (19, "frc3189"), (28, "frc3189"), (32, "frc3189"), (38, "frc3189"), (44, "frc3189"), (50, "frc3189"), (57, "frc3189"), (6, "frc3189"), (70, "frc3189"), (75, "frc3189"), (1, "frc6884"), (11, "frc6884"), (15, "frc6884"), (25, "frc6884"), (30, "frc6884"), (38, "frc6884"), (48, "frc6884"), (53, "frc6884"), (62, "frc6884"), (70, "frc6884"), (76, "frc6884")],
    [(20, "frc2813"), (23, "frc2813"), (35, "frc2813"), (42, "frc2813"), (45, "frc2813"), (5, "frc2813"), (56, "frc2813"), (63, "frc2813"), (70, "frc2813"), (74, "frc2813"), (9, "frc2813"), (11, "frc2473"), (17, "frc2473"), (27, "frc2473"), (3, "frc2473"), (35, "frc2473"), (40, "frc2473"), (49, "frc2473"), (52, "frc2473"), (59, "frc2473"), (67, "frc2473"), (75, "frc2473"), (10, "frc9114"), (16, "frc9114"), (26, "frc9114"), (32, "frc9114"), (41, "frc9114"), (47, "frc9114"), (51, "frc9114"), (59, "frc9114"), (65, "frc9114"), (7, "frc9114"), (76, "frc9114")],
]

# user_matches = [[(15, 'frc668'), (26, 'frc668'), (3, 'frc668')],[(4, 'frc668'), (26, 'frc668'), (4, 'frc668')]]
# Print original matches
print("Original matches:")
d = 0
for user_id, matches in enumerate(user_matches):
    print(f"\nuser {user_id}: {matches}\nDUPLICATES: {sum(1 for match in matches if sum(1 for m in matches if m[0] == match[0]) > 1)}")
    d += sum(1 for match in matches if sum(1 for m in matches if m[0] == match[0]) > 1)
print("D: ", d)
swapped_matches = distribute_and_swap_matches(user_matches)

# Print swapped matches
print("\nSwapped matches:")
d2 = 0
for user_id, matches in enumerate(swapped_matches):
    print(f"user {user_id}: {matches}\nDUPLICATES: {sum(1 for match in matches if sum(1 for m in matches if m[0] == match[0]) > 1)} LEN: {len(matches)} ")
    d2 += sum(1 for match in matches if sum(1 for m in matches if m[0] == match[0]) > 1)
print("D2: ", d2)
