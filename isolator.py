# isolator.py
# isolate data elements of the same type or with matching features
# eg isolate one game from all games and isolate all games with certain scores

import re
from tabulate import tabulate # display output

def isolate_games(raw_data):
    print("\n===Isolate Games===\n")
    print("raw_data: " + str(raw_data))
    all_games = []
    game = []
    existing_game = False
    for line in raw_data:
        print("line: " + str(line))
        # if first element has game label or date consider it a new game
        if line[0] == 'Game' or re.search('/',line[0]): # we tell date by slash (/)
            print("New Game")
            existing_game = True
            # new game
            if len(game) != 0: # if no game data yet, do not add game to all games until adding lines to game
                all_games.append(game)
            game = [line]

        # continue to append lines to the current game until we encounter another game or date label
        if existing_game == True:
            game.append(line)

    print("all_games: " + str(all_games))
    return all_games


# game data has headers and each month is separated by monthly averages
# which happen to be differentiated by uppercase letters
def isolate_player_game_data(player_data, player_name=''):
    player_game_data = []

    if len(player_data) > 0:
        for row in player_data:
            if not row[0].isupper():
                player_game_data.append(row)

        # display player game data in formatted table for observation
        #print("player_game_data: " + str(player_game_data))

        header_row = player_data[0]

        table = [header_row]
        for row in player_game_data:
            table.append(row)

        print("\n===" + player_name + "===\n")
        print(tabulate(table))
    else:
        print("Warning: No Player Data from file.")

    return player_game_data

# assuming header row to find keyword to find idx of desired field
def isolate_data_field(desired_field_name, data_table):
    data_field = []

    # given header row find keyword to find idx
    header_row = data_table[0]

    desired_field_idx = 0
    for field_idx in range(len(header_row)):
        field_name = header_row[field_idx]
        if re.search(desired_field_name.lower(), field_name.lower()):
            desired_field_idx = field_idx

    for row in data_table[1:]:
        data_field.append(row[desired_field_idx])


    return data_field

# assuming header row to find keyword to find idx of desired field
# def isolate_data_element(desired_field_name, header, data_row):
#     data_field = []

#     # given header row find keyword to find idx
#     header_row = data_table[0]

#     desired_field_idx = 0
#     for field_idx in range(len(header_row)):
#         field_name = header_row[field_idx]
#         if re.search(desired_field_name.lower(), field_name.lower()):
#             desired_field_idx = field_idx

#     for row in data_table[1:]:
#         data_field.append(row[desired_field_idx])


#     return data_field


# isolate likely outcomes using stats to find consistent streaks
# ie isolate consistent streaks
# stats_counts = [ pts_counts, rebs_counts, ... ]
# pts_counts = [ 1/1, 2/2, 2/3, ... ]
# make rules to eliminate bad options and isolate good options
# eg dont always rule out 0/1 if they are 9/10
# and dont rule out 0/2 if they are 10/12?
# if unclear, it is better to keep for review
# start by isolating positive streaks
# start from most to least recent
def isolate_consistent_streaks(all_stats_counts_dict):

    # did they hit last game?
    # either way, continue to next game to assess streak but conditions for passing have changed
    # if hit most recent, then 2/2 will increase likelihood
    # if missed most recent, then 1/2 will need to check next 2 games at least to see if 3/4 bc 2/3 is not likely enough

    consistent_streaks = []

    # start simple, create group of 7/10 streaks
    for stats_counts in stats_counts.values():
        print("stats_counts: " + str(stats_counts))
        for stat_counts in stats_counts:
            print("stat_counts: " + str(stat_counts))

            pt_counts = stat_counts[0]
            if stat_counts[9] >= 7:
                consistent_streaks.append(streak)



    return consistent_streaks


# isolate all keys with 'out' or list of names
# see sort keys bc we may want to see all keys sorted rather than exclude potentially relevant keys
def isolate_keys_in_dict(regex, dict):
    print('isolate keys')
