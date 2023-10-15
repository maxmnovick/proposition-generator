#writer.py
# display data

import re # see if string contains stat and player of interest to display
import numpy # mean, median to display over time
import csv # save player and game espn ID's so we do not have to request each run
import sorter # sort players outcomes so we see conditions grouped by type and other useful visuals

from tabulate import tabulate # display output, eg consistent stat vals

import converter # convert dicts to lists

import determiner # determine matching key

def display_game_data(all_valid_streaks_list):
    print("\n===Game Data===\n")
    # all_player_pre_dicts = [{'prediction':val,'overall record':[],..},{},..]
    # get headers
    # header_row = ['Prediction']
    # for pre_dict in all_player_pre_dicts.values():
    #     for key in pre_dict:
    #         header_row.append(key.title())
    #     break
    # game_data = [header_row]

    # print("all_player_pre_dicts: " + str(all_player_pre_dicts))
    # for prediction, pre_dict in all_player_pre_dicts.items():
    #     prediction_row = [prediction]
    #     for val in pre_dict.values():
    #         prediction_row.append(val)
    #     game_data.append(prediction_row)



    # get headers
    header_row = []
    header_string = '' # separate by semicolons and delimit in spreadsheet
    if len(all_valid_streaks_list) > 0:
        streak1 = all_valid_streaks_list[0]
        for key in streak1.keys():
            header_row.append(key.title())
            header_string += key.title() + ";"

        game_data = [header_row]
        game_data_strings = []
        for streak in all_valid_streaks_list:
            streak_row = []
            streak_string = ''
            for val in streak.values():
                streak_row.append(val)
                streak_string += str(val) + ";"
            game_data.append(streak_row)
            game_data_strings.append(streak_string)
    else:
        print('Warning: no valid streaks!')


    #print(tabulate(game_data))

    print("Export")
    print(header_string)
    for game_data in game_data_strings:
        print(game_data)



def display_stat_plot(all_valid_streaks_list, all_players_stats_dicts, stat_of_interest, player_of_interest):
    print('\n===Plot Stats===\n')
    #Three lines to make our compiler able to draw:
    import matplotlib.pyplot as plt

    #display player stat values so we can see plot
    #columns: game num, stat val, over average record
    #print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
    for valid_streak in all_valid_streaks_list:

        
        
        if re.search(stat_of_interest, valid_streak['prediction'].lower()) and re.search(player_of_interest, valid_streak['prediction'].lower()):

            print('valid_streak: ' + str(valid_streak))
            player_name = ' '.join(valid_streak['prediction'].split()[:-2]).lower() # anthony davis 12+ pts
            print("player_name from prediction: " + player_name)

            stat_name = valid_streak['prediction'].split()[-1].lower()
            condition = 'all'
            season_year = 2023
            stat_vals_dict = all_players_stats_dicts[player_name][season_year][stat_name][condition]
            print('stat_vals_dict: ' + str(stat_vals_dict))

            game_nums = list(stat_vals_dict.keys())
            #print('game_nums: ' + str(game_nums))
            stat_vals = list(stat_vals_dict.values())
            stat_vals.reverse()
            print('stat_vals: ' + str(stat_vals))

            stat_line = int(valid_streak['prediction'].split()[-2][:-1])
            print('stat_line: ' + str(stat_line))

            plot_stat_line = [stat_line] * len(game_nums)
            print('plot_stat_line: ' + str(plot_stat_line))

            # x = np.array(game_nums)
            # y = np.array(stat_vals)

            plt.plot(game_nums, stat_vals, label = "Stat Vals") # reverse bc input from recent to distant but we plot left to right
            plt.plot(game_nums, plot_stat_line,  label = "Stat Line")

            # also plot avg over time to compare trend of avg
            # bc just seeing season avg is barely useful almost useless unless we see either avg in last few games (and multiple subset) or we can simply see if avg is increasing or decreasing
            # the avg for the first game must be based on previous seasons
            # but for now arbitrary number
            #init_mean_stat_val
            prev_stat_vals = []
            mean_stat_vals = [] # how mean changes over time
            past_ten_stat_vals = []
            past_ten_mean_stat_vals = [] # mean over last 10 games to get more recent relevant picture
            past_three_stat_vals = []
            past_three_mean_stat_vals = []
            for stat_val_idx in range(len(stat_vals)):
                stat_val = stat_vals[stat_val_idx]
                #print('prev_stat_vals: ' + str(prev_stat_vals))
                #print('past_ten_stat_vals: ' + str(past_ten_stat_vals))
                # compute avg of this and previous vals
                if stat_val_idx == 0:
                    mean_stat_val = stat_val
                    past_ten_mean_stat_val = stat_val
                    past_three_mean_stat_val = stat_val

                else:
                    mean_stat_val = round(numpy.mean(prev_stat_vals), 1)
                    #print('mean_stat_val: ' + str(mean_stat_val))
                    past_ten_mean_stat_val = round(numpy.mean(past_ten_stat_vals), 1)
                    #print('past_ten_mean_stat_val: ' + str(past_ten_mean_stat_val))
                    past_three_mean_stat_val = round(numpy.mean(past_three_stat_vals), 1)
                    #print('past_three_mean_stat_val: ' + str(past_three_mean_stat_val))

                mean_stat_vals.append(mean_stat_val)
                past_ten_mean_stat_vals.append(past_ten_mean_stat_val)
                past_three_mean_stat_vals.append(past_three_mean_stat_val)

                prev_stat_vals.append(stat_val)

                if stat_val_idx < 10: # add vals to list until we reach 10 bc we only want past 10 games
                    past_ten_stat_vals.append(stat_val)
                else: # replace in list instead of adding
                    past_ten_stat_vals.pop(0)
                    past_ten_stat_vals.append(stat_val)
                if stat_val_idx < 3: # add vals to list until we reach 10 bc we only want past 10 games
                    past_three_stat_vals.append(stat_val)
                else: # replace in list instead of adding
                    past_three_stat_vals.pop(0)
                    past_three_stat_vals.append(stat_val)
                

            #print('mean_stat_vals: ' + str(mean_stat_vals))
            #print('past_ten_mean_stat_vals: ' + str(past_ten_mean_stat_vals))
            #print('past_three_mean_stat_vals: ' + str(past_three_mean_stat_vals))

            plt.plot(game_nums, mean_stat_vals,  label = "Overall Mean")
            plt.plot(game_nums, past_ten_mean_stat_vals,  label = "Past 10 Mean")
            plt.plot(game_nums, past_three_mean_stat_vals,  label = "Past 3 Mean")


            plt.title(player_name.title() + " " + stat_name.upper() + " over Time")
            plt.xlabel("Game Num")
            plt.ylabel(stat_name.upper())

            plt.legend()
            plt.show()

            # display table so we can export to files and view graphs in spreadsheet

            #Two  lines to make our compiler able to draw:
            # plt.savefig(sys.stdout.buffer)
            # sys.stdout.flush()


def display_all_players_records_dicts(all_players_records_dicts, all_player_season_logs_dict):
    print('\n===Display All Players Records Dicts===\n')

    # player_stat_dict = { year: .. }
    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        print('\n===' + player_name.title() + '===\n')

        #season_year = 2023

        # player_season_stat_dict = { stat name: .. }
        for season_year, player_season_stat_dict in player_stat_dict.items():

            print("\n===Year " + str(season_year) + "===\n")
            #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
            #player_name = player_names[player_idx] # player names must be aligned with player game logs

            # all_pts_dicts = {'all':{idx:val,..},..}
            all_pts_dicts = player_season_stat_dict['pts']
            all_rebs_dicts = player_season_stat_dict['reb']
            all_asts_dicts = player_season_stat_dict['ast']
            all_threes_made_dicts = player_season_stat_dict['3pm']
            all_bs_dicts = player_season_stat_dict['blk']
            all_ss_dicts = player_season_stat_dict['stl']
            all_tos_dicts = player_season_stat_dict['to']
            if len(all_pts_dicts['all'].keys()) > 0:
                # no matter how we get data, 
                # next we compute relevant results

                # first for all then for subsets like home/away
                # all_pts_dict = { 'all':[] }
                # all_pts_means_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_medians_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_modes_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_min_dict = { 'all':0, 'home':0, 'away':0 }
                # all_pts_max_dict = { 'all':0, 'home':0, 'away':0 }

                all_stats_counts_dict = { 'all': [], 'home': [], 'away': [] }

                # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
                #print("all_pts_dict: " + str(all_pts_dict))
                print("all_pts_dicts: " + str(all_pts_dicts))
                # all_pts_dicts = {'all':{1:20}}
                # key=condition, val={idx:stat}

                
                #compute stats from data
                # key represents set of conditions of interest eg home/away
                for conditions in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    # reset for each set of conditions

                    # for same set of conditions, count streaks for stats
                    min_line_hits = 7
                    game_sample = 10
                    current_line_hits = 10 # player reached 0+ stats in all 10/10 games. current hits is for current level of points line

                    pts_count = 0
                    r_count = 0
                    a_count = 0

                    threes_count = 0
                    b_count = 0
                    s_count = 0
                    to_count = 0

                    all_pts_counts = []
                    all_rebs_counts = []
                    all_asts_counts = []

                    all_threes_counts = []
                    all_blks_counts = []
                    all_stls_counts = []
                    all_tos_counts = []

                    # prob = 1.0
                    # while(prob > 0.7):
                    #if set_sample_size = True: # if we set a sample size only consider those settings. else take all games
                    #while(current_line_hits > min_line_hits) # min line hits is considered good odds. increase current line hits count out of 10
                        # if count after 10 games is greater than min line hits then check next level up
                    for game_idx in range(len(all_pts_dicts[conditions].values())):
                        pts = list(all_pts_dicts[conditions].values())[game_idx]
                        rebs = list(all_rebs_dicts[conditions].values())[game_idx]
                        asts = list(all_asts_dicts[conditions].values())[game_idx]

                        threes = list(all_threes_made_dicts[conditions].values())[game_idx]
                        blks = list(all_bs_dicts[conditions].values())[game_idx]
                        stls = list(all_ss_dicts[conditions].values())[game_idx]
                        tos = list(all_tos_dicts[conditions].values())[game_idx]

                        player_projected_lines = projected_lines_dict[player_name]
                        if pts >= int(player_projected_lines['PTS']):
                            pts_count += 1
                        if rebs >= int(player_projected_lines['REB']):
                            r_count += 1
                        if asts >= int(player_projected_lines['AST']):
                            a_count += 1

                        if threes >= int(player_projected_lines['3PT']):
                            threes_count += 1
                        if blks >= int(player_projected_lines['BLK']):
                            b_count += 1
                        if stls >= int(player_projected_lines['STL']):
                            s_count += 1
                        if tos >= int(player_projected_lines['TO']):
                            to_count += 1

                        all_pts_counts.append(pts_count)
                        all_rebs_counts.append(r_count)
                        all_asts_counts.append(a_count)

                        all_threes_counts.append(threes_count)
                        all_blks_counts.append(b_count)
                        all_stls_counts.append(s_count)
                        all_tos_counts.append(to_count)

                    # make stats counts to find consistent streaks
                    all_stats_counts_dict[conditions] = [ all_pts_counts, all_rebs_counts, all_asts_counts, all_threes_counts, all_blks_counts, all_stls_counts, all_tos_counts ]

                    stats_counts = [ all_pts_counts, all_rebs_counts, all_asts_counts, all_threes_counts, all_blks_counts, all_stls_counts, all_tos_counts ]

                    header_row = ['Games']
                    over_pts_line = 'PTS ' + str(player_projected_lines['PTS']) + "+"
                    over_rebs_line = 'REB ' + str(player_projected_lines['REB']) + "+"
                    over_asts_line = 'AST ' + str(player_projected_lines['AST']) + "+"
                    
                    over_threes_line = '3PM ' + str(player_projected_lines['3PT']) + "+"
                    over_blks_line = 'BLK ' + str(player_projected_lines['BLK']) + "+"
                    over_stls_line = 'STL ' + str(player_projected_lines['STL']) + "+"
                    over_tos_line = 'TO ' + str(player_projected_lines['TO']) + "+"
                    
                    prob_pts_row = [over_pts_line]
                    prob_rebs_row = [over_rebs_line]
                    prob_asts_row = [over_asts_line]

                    prob_threes_row = [over_threes_line]
                    prob_blks_row = [over_blks_line]
                    prob_stls_row = [over_stls_line]
                    prob_tos_row = [over_tos_line]

                    

                    for game_idx in range(len(all_pts_dicts[conditions].values())):
                        p_count = all_pts_counts[game_idx]
                        r_count = all_rebs_counts[game_idx]
                        a_count = all_asts_counts[game_idx]

                        threes_count = all_threes_counts[game_idx]
                        b_count = all_blks_counts[game_idx]
                        s_count = all_stls_counts[game_idx]
                        to_count = all_tos_counts[game_idx]

                        current_total = str(game_idx + 1)
                        current_total_games = current_total# + ' Games'
                        header_row.append(current_total_games)

                        prob_over_pts_line = str(p_count) + "/" + current_total
                        prob_pts_row.append(prob_over_pts_line)
                        
                        prob_over_rebs_line = str(r_count) + "/" + current_total
                        prob_rebs_row.append(prob_over_rebs_line)
                        prob_over_asts_line = str(a_count) + "/" + current_total
                        prob_asts_row.append(prob_over_asts_line)

                        prob_over_threes_line = str(threes_count) + "/" + current_total
                        prob_threes_row.append(prob_over_threes_line)
                        prob_over_blks_line = str(b_count) + "/" + current_total
                        prob_blks_row.append(prob_over_blks_line)
                        prob_over_stls_line = str(s_count) + "/" + current_total
                        prob_stls_row.append(prob_over_stls_line)
                        prob_over_tos_line = str(to_count) + "/" + current_total
                        prob_tos_row.append(prob_over_tos_line)

                    # display game info for reference based on game idx
                    game_num_header = 'Games Ago'
                    game_num_row = [game_num_header]
                    game_day_header = 'DoW'
                    game_day_row = [game_day_header]
                    game_date_header = 'Date'
                    game_date_row = [game_date_header]

                    for game_num in all_pts_dicts[conditions].keys():
                        #game_num = all_pts_dicts[key]
                        game_num_row.append(game_num)
                        game_day_date = player_game_log.loc[game_num,'Date']
                        game_day = game_day_date.split()[0]
                        game_day_row.append(game_day)
                        game_date = game_day_date.split()[1]
                        game_date_row.append(game_date)
                    

                    #total = str(len(all_pts))
                    #probability_over_line = str(count) + "/" + total
                    #total_games = total + " Games"
                    #header_row = ['Points', total_games]
                    #print(probability_over_line)

                    #prob_row = [over_line, probability_over_line]

                    print("\n===" + player_name.title() + " Probabilities===\n")

                    game_num_table = [game_num_row, game_day_row, game_date_row]
                    print(tabulate(game_num_table))

                    prob_pts_table = [prob_pts_row]
                    print(tabulate(prob_pts_table))

                    prob_rebs_table = [prob_rebs_row]
                    print(tabulate(prob_rebs_table))

                    prob_asts_table = [prob_asts_row]
                    print(tabulate(prob_asts_table))

                    prob_threes_table = [prob_threes_row]
                    print(tabulate(prob_threes_table))

                    prob_blks_table = [prob_blks_row]
                    print(tabulate(prob_blks_table))

                    prob_stls_table = [prob_stls_row]
                    print(tabulate(prob_stls_table))

                    prob_tos_table = [prob_tos_row]
                    print(tabulate(prob_tos_table))

            season_year -= 1

# players_outcomes = {player: stat name: outcome dict}
def display_players_outcomes(players_outcomes):

    print("\n===Player Outcomes===\n")
    #print('players_outcomes: ' + str(players_outcomes))

    # sort so we see all instances of teammates out grouped together instead of game order bc we are interested to see by type of condition not by game at this point
    # we do want to see ordered by games as well so we have game idx and need way to switch bt views
    
    #todo: sorted_players_outcomes = sorter.sort_players_outcomes(players_outcomes) 


    # convert player outcomes dict into list
    player_outcomes_list = []
    # stat_outcome_dict = stat:outcome_dict
    for stat_outcome_dict in players_outcomes.values():

        for season_part_outcome_dict in stat_outcome_dict.values():

            for outcome_dict in season_part_outcome_dict.values():

                player_outcomes_list.append(outcome_dict) # outcome_dict = prediction:stats

    # get headers
    header_row = []
    header_string = '' # separate by semicolons and delimit in spreadsheet
    if len(player_outcomes_list) > 0:
        # print header row
        outcome1 = player_outcomes_list[0]
        for key in outcome1.keys():
            header_row.append(key.title())
            header_string += key.title() + ";"

        # print data rows
        game_data = [header_row]
        game_data_strings = []
        for outcome in player_outcomes_list:
            outcome_row = []
            outcome_string = ''
            for val in outcome.values():
                outcome_row.append(val)
                outcome_string += str(val) + ";"
            game_data.append(outcome_row)
            game_data_strings.append(outcome_string)
    else:
        print('Warning: no valid streaks!')


    #print(tabulate(game_data))

    print("Export")
    print(header_string)
    for game_data in game_data_strings:
        print(game_data)

    #print("\n===End Player Outcomes===\n")


# we have saved lessons from experience and logic that must be accounted for when deciding so display prominently and constantly reference
# lessons = [outcome, lesson]
def display_lessons(lessons):

    print("\n===Display Lessons===\n")

    header_string = 'Outcome;Lesson'

    lesson_strings = []
    for lesson in lessons:
        lesson_string = lesson[0] + ';' + lesson[1]
        lesson_strings.append(lesson_string)

    #print("Export")
    print(header_string)
    for lesson in lesson_strings:
        print(lesson)

    print("\n===End Lessons===\n")


# data = [[name,id],..]
# for espn id we only want to append new ids bc they do not change
# write_param = create (error if exists), overwrite, or append
def write_data_to_file(data, filepath, write_param, extension='csv'):

    print('\n===Write Data to File: ' + filepath + '===\n')

    if extension == 'csv':

        with open(filepath, write_param) as csvfile:

            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(data)

    else:
        print('Warning: Unknown file extension! ')
    


# data = [[name,id],..]
# for espn id we only want to append new ids bc they do not change
# def append_data_to_file(data, filepath):

#     print('\n===Write Data to File===\n')


# init record condition_record format ['1/1',..]
# desired format 1/1,..
# remove brackets and quotes
def convert_list_to_string(init_list):
    print('init_list: ' + str(init_list))

    final_string = re.sub('[\\[\\]\']','',str(init_list))

    print('final_string: ' + final_string)
    return final_string

# moved to generator
# all_player_consistent_stats = {} same format as stat records, 
# condition, year, stat name
# def display_consistent_stats(all_player_consistent_stats, all_player_stat_records):
#     print("\n===Display Consistent Stats===\n")
#     print('all_player_consistent_stats: ' + str(all_player_consistent_stats))
#     print('all_player_stat_records: ' + str(all_player_stat_records))

#     player_consistent_stat_data_headers = ['Player', 'S Name', 'Stat', 'Prob', '2nd Stat', '2nd Prob', 'PS', 'PP', '2nd PS', '2nd PP', 'OK Val', 'OK P', 'OK PP']
#     final_consistent_stats = [player_consistent_stat_data_headers] # player name, stat name, consistent stat, consistent stat prob

#     # so we can sort from high to low prob
#     all_consistent_stat_dicts = [] 
#     consistent_stat_dict = {}

#     for player_name, player_consistent_stats in all_player_consistent_stats.items():
#         #print(player_name)
        

#         # for now, show only conditon=all
#         # give option to set condition and sort by condition
#         conditions_of_interest = ['all']
#         for condition, condition_consistent_stats in player_consistent_stats.items():
#             #print(condition)

#             if condition in conditions_of_interest:

#                 years_of_interest = [2023]
#                 for year, year_consistent_stats in condition_consistent_stats.items():
#                     #print(year)

#                     if year in years_of_interest:

#                         # for season_part, season_part_consistent_stats in year_consistent_stats.items():
#                         #     print(season_part)

#                         #     player_season_consistent_stat_data = []

#                         # first look at full season, then postseason
#                         season_part_consistent_stats = year_consistent_stats['full'] 

#                         for stat_name in season_part_consistent_stats.keys():
#                             #print(stat_name)

#                             # use consistent_stat_dict to sort
#                             consistent_stat_dict = {'player name':player_name, 'stat name':stat_name}
                            

#                             #player_consistent_stat_data = [player_name, stat_name]

#                             prob_stat_dict = year_consistent_stats['full'][stat_name]
#                             print('prob_stat_dict: ' + str(prob_stat_dict))

#                             full_consistent_stat = prob_stat_dict['prob val']
#                             full_consistent_stat_prob = prob_stat_dict['prob']

#                             full_second_consistent_stat = prob_stat_dict['second prob val']
#                             full_second_consistent_stat_prob = prob_stat_dict['second prob']

#                             consistent_stat_dict['prob val'] = full_consistent_stat
#                             consistent_stat_dict['prob'] = full_consistent_stat_prob
#                             consistent_stat_dict['second prob val'] = full_second_consistent_stat
#                             consistent_stat_dict['second prob'] = full_second_consistent_stat_prob

#                             # add postseason stat probs separately
#                             post_consistent_stat = 0
#                             post_consistent_stat_prob = 0

#                             post_second_consistent_stat = 0
#                             post_second_consistent_stat_prob = 0

#                             if 'postseason' in year_consistent_stats.keys():
#                                 prob_stat_dict = year_consistent_stats['postseason'][stat_name]
#                                 print('prob_stat_dict: ' + str(prob_stat_dict))

#                                 post_consistent_stat = prob_stat_dict['prob val']
#                                 post_consistent_stat_prob = prob_stat_dict['prob']

#                                 post_second_consistent_stat = prob_stat_dict['second prob val']
#                                 post_second_consistent_stat_prob = prob_stat_dict['second prob']

#                                 consistent_stat_dict['post prob val'] = post_consistent_stat
#                                 consistent_stat_dict['post prob'] = post_consistent_stat_prob
#                                 consistent_stat_dict['post second prob val'] = post_second_consistent_stat
#                                 consistent_stat_dict['post second prob'] = post_second_consistent_stat_prob

#                             # add another column to classify if postseason stat < regseason stat so we can group those together

#                             # player name, stat name, consistent stat, consistent stat prob
#                             player_consistent_stat_data = [player_name, stat_name, full_consistent_stat, full_consistent_stat_prob, full_second_consistent_stat, full_second_consistent_stat_prob, post_consistent_stat, post_consistent_stat_prob, post_second_consistent_stat, post_second_consistent_stat_prob]
#                             #consistent_stat_dict = {'player name':player_name, 'stat name':stat_name, 'prob val': full_consistent_stat, 'prob': full_consistent_stat_prob, 'second prob val':full_second_consistent_stat, 'second prob':full_second_consistent_stat_prob}

#                             #player_season_consistent_stat_data = player_season_consistent_stat_data + player_consistent_stat_data

#                             final_consistent_stats.append(player_consistent_stat_data)

#                             all_consistent_stat_dicts.append(consistent_stat_dict)
                            


#     print('all_consistent_stat_dicts: ' + str(all_consistent_stat_dicts))

#     # determine which keys in dict to sort dicts by
#     sort_key1 = 'ok val post prob' # default
#     sort_key2 = 'ok val prob' # default

#     # check if regseason stat is available
#     ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
#     #year_of_interest = 2023
#     #regseason_stats = consistent_stat_vals['all'][year_of_interest]['regular']
#     for stat_dict in all_consistent_stat_dicts:

#         player_stat_records = all_player_stat_records[stat_dict['player name']]

#         stat_name = stat_dict['stat name']
#         season_part = 'postseason' # we want to see postseason prob of regseason stat

#         reg_season_stat_val = stat_dict['prob val']
#         reg_season_second_stat_val = stat_dict['second prob val']
#         reg_season_stat_prob = stat_dict['prob']
#         reg_season_second_stat_prob = stat_dict['second prob']

#         post_season_stat_val = stat_dict['post prob val']
#         post_season_stat_prob = stat_dict['post prob']

#         if reg_season_stat_val in ok_stat_vals: #is available (ie in ok stat vals list)
#             stat_dict['ok val'] = reg_season_stat_val # default, ok=available
#             stat_dict['ok val prob'] = reg_season_stat_prob 
#             # determine which key has the same stat val in post as reg, bc we earlier made sure there would be one
#             # can be generalized to fcn called determine matching key
#             stat_dict['ok val post prob'] = determiner.determine_ok_val_prob(stat_dict, stat_dict['ok val'], player_stat_records, season_part, stat_name) #post_season_stat_prob 
#             # post_season_stat_val_key = determiner.determine_matching_key(stat_dict, stat_dict['ok val']) #'post prob val'
#             # # for key, val in stat_dict.items():
#             # #     if key != 'ok val':
#             # #         if val == stat_dict['ok val'] and not re.search('prob',key):
#             # #             post_season_stat_val_key = key

#             # post_season_stat_prob_key = re.sub('val','',post_season_stat_val_key)
#             # post_season_stat_prob = stat_dict[post_season_stat_prob_key]
#             # stat_dict['ok val post prob'] = post_season_stat_prob 

#             # if reg_season_stat_val != post_season_stat_val:
#             #     stat_dict['ok val post prob'] = post_season_stat_val_prob 

#         # if default reg season stat na,
#         # first check next lowest val, called second val
#         else:
#             stat_dict['ok val'] = reg_season_second_stat_val # ok=available
#             stat_dict['ok val prob'] = reg_season_second_stat_prob 
#             stat_dict['ok val post prob'] = determiner.determine_ok_val_prob(stat_dict, stat_dict['ok val'], player_stat_records, season_part, stat_name) #post_season_stat_prob 


#     # determine final available stat val out of possible consistent stat vals
#     # eg if horford reb in playoffs higher than regseason, use regseason stat val's prob in postseason
#     # bc that will show highest prob
#     #available_stat_val


#     sort_keys = [sort_key1, sort_key2]
#     sorted_consistent_stat_dicts = sorter.sort_dicts_by_keys(all_consistent_stat_dicts, sort_keys)
#     # desired_order = ['player name','stat name','ok val','ok pp','ok p']
#     sorted_consistent_stats = converter.convert_dicts_to_lists(sorted_consistent_stat_dicts)

#     print('sorted_consistent_stats')
#     print(tabulate(player_consistent_stat_data_headers + sorted_consistent_stats))

#     # export
#     for row in sorted_consistent_stats:
#         export_row = ''
#         for cell in row:
#             export_row += str(cell) + ';'

#         print(export_row)

#desired_order=list  headers
def list_dicts(dicts, desired_order=[]):
    # desired_order = ['player name','stat name','ok val','ok pp','ok p']
    dict_list = converter.convert_dicts_to_lists(dicts, desired_order)

    print('dict_list')
    print(tabulate(dict_list))

    headers = []#[list(dicts[0].keys())]
    for key in desired_order:
        headers.append(key)
    for key in dicts[0].keys():
        if key not in desired_order:
            headers.append(key)


    dict_list = [headers] + dict_list

    # export
    for row in dict_list:
        export_row = ''
        for cell in row:
            # stop Sheets autoformatting 3pm as 3:00 PM
            # by adding apostrophe to the front
            #print('cell: ' + str(cell))
            if str(cell) == '3pm':
                cell = '\'3pm'
            export_row += str(cell) + ';'

        print(export_row)