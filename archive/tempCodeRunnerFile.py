def distribute_and_swap_matches(user_matches):
    # Define the swap_matches function
    def swap_matches(matches_list):
        all_matches = set()
        for matches in matches_list:
            all_matches.update(match[0] for match in matches)

        for i, matches in enumerate(matches_list):
            for match in matches:
                print(type(match))
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

