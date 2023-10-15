# generator.py
# generate data structures so we can reference info to make decisions
# and generate decisions based on data structures

import re
from datetime import datetime # convert date str to date so we can see if games 1 day apart and how many games apart

import determiner # determine regular season games, etc

import numpy # mean, median
from scipy import stats # calculate mode

import reader # read game log from file if needed
import writer # format record and other game data for readability

from tabulate import tabulate # display output

import sorter 

# sort alphabetical and lower for comparison to other games
def generate_players_string(players_list):

    players_list = sorted(players_list)

    p_string = ''

    for p_idx in range(len(players_list)):

        p = players_list[p_idx] # j. brown sg
        # last 2 letters are position which we want uppercase
        #n=2
        # pos = p[len(p) - n:]
        # p = p[:-n] + pos

        if p_idx == 0:
            p_string += p
        else:
            p_string += ', ' + p
            
    p_string = p_string.lower() # lowercase and possibly remove period after first initial?
    
    print('p_string: ' + p_string)
    return p_string

# each player has a stat dict for each stat so gen all of them for a given player
# run separately for each part of each season
def generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_team, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part):

    # get no. games played this season
    # so we can compare game with the same idx bt seasons
    current_season_log = player_game_log
    current_reg_season_log = determiner.determine_regular_season_games(current_season_log)
    num_games_played = len(current_reg_season_log.index) # see performance at this point in previous seasons

    # all_pts_dicts = {'all':{idx:val,..},..}
    all_pts_dicts = { 'all':{}, 'home':{}, 'away':{} } # 'opp eg okc':{}, 'day of week eg tue':{}
    all_rebs_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_asts_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_winning_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_losing_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_minutes_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fgms_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fgas_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fg_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_threes_made_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_threes_attempts_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_threes_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ftms_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ftas_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ft_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_bs_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_ss_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_fs_dicts = { 'all':{}, 'home':{}, 'away':{} }
    all_tos_dicts = { 'all':{}, 'home':{}, 'away':{} }

    all_stats_dicts = {'pts':all_pts_dicts, 'reb':all_rebs_dicts, 'ast':all_asts_dicts, 'w score':all_winning_scores_dicts, 'l score':all_losing_scores_dicts, 'min':all_minutes_dicts, 'fgm':all_fgms_dicts, 'fga':all_fgas_dicts, 'fg%':all_fg_rates_dicts, '3pm':all_threes_made_dicts, '3pa':all_threes_attempts_dicts, '3p%':all_threes_rates_dicts, 'ftm':all_ftms_dicts, 'fta':all_ftas_dicts, 'ft%':all_ft_rates_dicts, 'blk':all_bs_dicts, 'stl':all_ss_dicts, 'pf':all_fs_dicts, 'to':all_tos_dicts} # loop through to add all new stats with 1 fcn


    # if getting data from player game logs read from internet
    # for game log for particular given season/year
    # for season in all seasons
    if len(player_game_log) > 0:
        #season_year = '23'
        #print("player_game_log:\n" + str(player_game_log))
        # we pulled game log from internet

        
        
        # first loop thru all regular season games, then thru subset of games such as home/away
        # or just append to subset array predefined such as all_home_pts = []
        next_game_date_obj = datetime.today() # need to see if back to back games 1 day apart

        # do 1 loop for reg season and 1 loop for post season
        # default full season
        season_part_game_log = determiner.determine_season_part_games(player_game_log, season_part)
        # if season_part == 'regular':
        #     season_part_game_log = determiner.determine_season_part_games(player_game_log, season_part)
        # elif season_part == 'full':

        total_season_games = len(season_part_game_log.index) # so we can get game num from game idx
        
        for game_idx, row in season_part_game_log.iterrows():

            # get game type so we can add stat to reg or post season game
            game_type = player_game_log.loc[game_idx, 'Type']
            print('game_type: ' + str(game_type))

            # make list to loop through so we can add all stats to dicts with 1 fcn
            game_stats = determiner.determine_game_stats(player_game_log, game_idx) #[pts,rebs,asts,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,bs,ss,fs,tos] 


            # === Add Stats to Dict ===

            # now that we have game stats add them to dict by condition

            # values is list of dicts
            for stat_idx in range(len(all_stats_dicts.values())):
                stat_dict = list(all_stats_dicts.values())[stat_idx]
                stat = game_stats[stat_idx]
                stat_dict['all'][game_idx] = stat


            # define away/home team so we can determine teammates/opponents in players in game
            away_abbrev = player_team

            game_opp_str = player_game_log.loc[game_idx, 'OPP']
            game_opp_abbrev = reader.read_team_abbrev(game_opp_str) # remove leading characters and change irregular abbrevs
            home_abbrev = game_opp_abbrev

            if re.search('vs',game_opp_str):

                # values is list of dicts
                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    stat_dict['home'][game_idx] = stat

                
                away_abbrev = game_opp_abbrev
                home_abbrev = player_team

                
            else: # if not home then away
                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    stat_dict['away'][game_idx] = stat

                
            print('away_abbrev: ' + away_abbrev)
            print('home_abbrev: ' + home_abbrev)

            # matchup against opponent
            # only add key for current opp bc we dont need to see all opps here
            # look for irregular abbrevs like NO and NY
            # opponent in form 'gsw' but game log in form 'gs'
            # if we do not know the current opponent then show all opps
            #game_log_team_abbrev = re.sub('vs|@','',player_game_log.loc[game_idx, 'OPP'].lower()) # eg 'gs'
            game_log_team_abbrev = reader.read_team_abbrev(player_game_log.loc[game_idx, 'OPP'])
            #print('game_log_team_abbrev: ' + game_log_team_abbrev)
            #opp_abbrev = opponent # default if regular
            #print('opp_abbrev: ' + opp_abbrev)

            # irregular_abbrevs = {'nop':'no', 'nyk':'ny', 'sas': 'sa', 'gsw':'gs' } # for these match the first 3 letters of team name instead
            # if opp_abbrev in irregular_abbrevs.keys():
            #     #print("irregular abbrev: " + team_abbrev)
            #     opp_abbrev = irregular_abbrevs[opp_abbrev]

            # if we do not know the current opponent 
            # or if we are not given a specific opponent (bc we may want to compare opps)
            # then show all opps
            if opponent == game_log_team_abbrev or opponent == '':
                #print('opp_abbrev == game_log_team_abbrev')
                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not game_log_team_abbrev in stat_dict.keys():
                        stat_dict[game_log_team_abbrev] = {}
                    stat_dict[game_log_team_abbrev][game_idx] = stat

                


            # see if this game is 1st or 2nd night of back to back bc we want to see if pattern for those conditions
            init_game_date_string = player_game_log.loc[game_idx, 'Date'].lower().split()[1] # 'wed 2/15'[1]='2/15'
            game_mth = init_game_date_string.split('/')[0]
            final_season_year = str(season_year)
            if int(game_mth) in range(10,13):
                final_season_year = str(season_year - 1)
            game_date_string = init_game_date_string + "/" + final_season_year
            #print("game_date_string: " + str(game_date_string))
            game_date_obj = datetime.strptime(game_date_string, '%m/%d/%Y')
            #print("game_date_obj: " + str(game_date_obj))

            # if current loop is most recent game (idx 0) then today's game is the next game, if current season
            # if last game of prev season then next game after idx 0 (bc from recent to distant) is next season game 1
            if game_idx == 0: # see how many days after prev game is date of today's projected lines
                # already defined or passed todays_games_date_obj
                # todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
                # print("todays_games_date_obj: " + str(todays_games_date_obj))
                current_year = 2023
                if season_year == current_year: # current year
                    next_game_date_obj = todays_games_date_obj # today's game is the next game relative to the previous game
                else:
                    next_game_date_obj = game_date_obj # should be 0 unless we want to get date of next season game
            #print("next_game_date_obj: " + str(next_game_date_obj))
            # no need to get next game date like this bc we can see last loop
            # else: # if not most recent game then we can see the following game in the game log at prev idx
            #     next_game_date_string = player_game_log.loc[game_idx-1, 'Date'].lower().split()[1] + "/" + season_year
            #     print("next_game_date_string: " + str(next_game_date_string))
            #     next_game_date_obj = datetime.strptime(next_game_date_string, '%m/%d/%y')
            #     print("next_game_date_obj: " + str(next_game_date_obj))

            days_before_next_game_int = (next_game_date_obj - game_date_obj).days
            days_before_next_game = str(days_before_next_game_int) + ' before'
            #print("days_before_next_game: " + days_before_next_game)

            for stat_idx in range(len(all_stats_dicts.values())):
                stat_dict = list(all_stats_dicts.values())[stat_idx]
                stat = game_stats[stat_idx]
                if not days_before_next_game in stat_dict.keys():
                    stat_dict[days_before_next_game] = {}
                stat_dict[days_before_next_game][game_idx] = stat

            init_prev_game_date_string = ''
            if len(player_game_log.index) > game_idx+1:
                init_prev_game_date_string = player_game_log.loc[game_idx+1, 'Date'].lower().split()[1]
            
                prev_game_mth = init_prev_game_date_string.split('/')[0]
                final_season_year = str(season_year)
                if int(prev_game_mth) in range(10,13):
                    final_season_year = str(season_year - 1)
                prev_game_date_string = init_prev_game_date_string + "/" + final_season_year
                #print("prev_game_date_string: " + str(prev_game_date_string))
                prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%Y')
                #print("prev_game_date_obj: " + str(prev_game_date_obj))

                days_after_prev_game_int = (game_date_obj - prev_game_date_obj).days
                days_after_prev_game = str(days_after_prev_game_int) + ' after'
                #print("days_after_prev_game: " + days_after_prev_game)

                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not days_after_prev_game in stat_dict.keys():
                        stat_dict[days_after_prev_game] = {}
                    stat_dict[days_after_prev_game][game_idx] = stat

            

            


            # add keys for each day of the week so we can see performance by day of week
            # only add key for current dow bc we dont need to see all dows here
            
            game_dow = player_game_log.loc[game_idx, 'Date'].lower().split()[0].lower() # 'wed 2/15'[0]='wed'
            current_dow = todays_games_date_obj.strftime('%a').lower()
            #print('current_dow: ' + str(current_dow))
            if current_dow == game_dow:
                #print("found same game day of week: " + game_dow)
                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not game_dow in stat_dict.keys():
                        stat_dict[game_dow] = {}
                    stat_dict[game_dow][game_idx] = stat
                #print("stat_dict: " + str(stat_dict))



            #====Players in Game stats
            # get game players from all game players dict
            #game_players = []
            #teammates = []
            #opponents = []
            #print('game_players: ' + str(game_players))
            # get current players from roster minus inactive players
            # we get current players when we know about the current game 
            
            current_players = { 'away': [], 'home': [] } # we get current players from team rosters
            #print('current_players: ' + str(current_players))
            current_teammates = [] # if blank then show all possible combos/lineups
            #print('current_teammates: ' + str(current_teammates))

            # we need to get the game key so that we can determine the players in this game
            # we got away/home team from vs|@ in opp field in game log
            game_key = away_abbrev + ' ' + home_abbrev + ' ' + game_date_string
            print('game_key: ' + str(game_key))
            # if we do not have the game box score bc it does not exist yet then pass to the next game
            # the order we fill the stats dict depends on the order of games played bc we are going game by game
            if game_key in all_players_in_games_dict.keys():
                game_players = all_players_in_games_dict[game_key] # {away:[],home:[]}
                print('game_players: ' + str(game_players))

                game_teammates = game_players['away']
                if player_team == home_abbrev:
                    game_teammates = game_players['home']

                # we need players in alphabetical string so we can compare to other games
                game_teammates_str = generate_players_string(game_teammates)

                # only add key for current teammates bc we dont need to see all teammates here
                # if no inactive players given then we can see all previous games with any (even 1) of current teammates
                # but what if a prev game has a player that is not playing in current game?
                # then that player completely changes the composition of stats
                # does the prev game have to have all the current teammates to pass the check?
                # or can it be missing a current player? 
                # if prev game is missing current player then that will completely change the comp also
                # if we are not sure who is playing in current game then show all possible teammates
                # once we get current roster, we can narrow it down to those possible players
                # then we can narrow it down further when we get inactive players list for the current game
                #current_teammates_in_prev_game = determiner.determine_current_teammates_in_game(game_teammates, current_teammates)
                #if len(current_teammates_in_prev_game) > 0: # if any of the current teammates are in the prev game of interest, then add to stats dict for review
                    #print("found same game teammates: " + game_teammates)


                for stat_idx in range(len(all_stats_dicts.values())):
                    stat_dict = list(all_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not game_teammates_str in stat_dict.keys():
                        stat_dict[game_teammates_str] = {}
                    stat_dict[game_teammates_str][game_idx] = stat
                #print("stat_dict: " + str(stat_dict))


                # for each player/teammate in game, make a new record or add to existing record
                for teammate in game_teammates:
                    print('teammate: ' + teammate)

                    for stat_idx in range(len(all_stats_dicts.values())):
                        stat_dict = list(all_stats_dicts.values())[stat_idx]
                        stat = game_stats[stat_idx]
                        if not teammate in stat_dict.keys():
                            stat_dict[teammate] = {}
                        stat_dict[teammate][game_idx] = stat
                    #print("stat_dict: " + str(stat_dict))


                # for each teammate out of game (dnp inactive injured), make a new record or add to existing record
                # we need to know all possible teammates, which we get above, once per player
                for teammate in all_teammates:
                    if teammate not in game_teammates: # teammate out
                        teammate_out_key = teammate + ' out'
                        for stat_idx in range(len(all_stats_dicts.values())):
                            stat_dict = list(all_stats_dicts.values())[stat_idx]
                            stat = game_stats[stat_idx]
                            if not teammate_out_key in stat_dict.keys():
                                stat_dict[teammate_out_key] = {}
                            stat_dict[teammate_out_key][game_idx] = stat
                        #print("stat_dict: " + str(stat_dict))

            else:
                print('Warning: Game key not in players in games dict so box score not available!')







            # ====Career/All Seasons Stats
            # if we find a game played on the same day/mth previous seasons, add a key for this/today's day/mth
            #today_date_data = todays_games_date.split('/')
            today_mth_day = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day) #today_date_data[0] + '/' + today_date_data[1]
            if init_game_date_string == today_mth_day:
                #print("found same game day/mth in previous season")
                for stat_idx in range(len(all_seasons_stats_dicts.values())):
                    stat_dict = list(all_seasons_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not game_date_string in stat_dict.keys():
                        stat_dict[game_date_string] = {}
                        stat_dict[game_date_string][game_idx] = [stat] # we cant use game idx as key bc it gets replaced instead of adding vals
                    else:
                        if game_idx in stat_dict[game_date_string].keys():
                            stat_dict[game_date_string][game_idx].append(stat)
                        else:
                            stat_dict[game_date_string][game_idx] = [stat]
                #print("all_seasons_stats_dicts: " + str(all_seasons_stats_dicts))
            # add key for the current game number for this season and add games played from previous seasons (1 per season)
            game_num = total_season_games - game_idx # bc going from recent to past
            if game_num == num_games_played:
                #print("found same game num in previous season")
                for stat_idx in range(len(all_seasons_stats_dicts.values())):
                    stat_dict = list(all_seasons_stats_dicts.values())[stat_idx]
                    stat = game_stats[stat_idx]
                    if not num_games_played in stat_dict.keys():
                        stat_dict[num_games_played] = {}
                        stat_dict[num_games_played][game_idx] = [stat] # we cant use game idx as key bc it gets replaced instead of adding vals
                    else:
                        if game_idx in stat_dict[num_games_played].keys():
                            stat_dict[num_games_played][game_idx].append(stat)
                        else:
                            stat_dict[num_games_played][game_idx] = [stat]
                #print("all_seasons_stats_dicts: " + str(all_seasons_stats_dicts))


            # after all keys are set, set next game as current game for next loop
            next_game_date_obj = game_date_obj # next game bc we loop from most to least recent

    else:
        # if getting data from file, may not have game log from internet source
        # data_type = "Game Log"
        # player_season_log = reader.read_season_log_from_file(data_type, player_name, 'tsv')
        print('Warning: No game log for player: ' + player_name)

    print('all_stats_dicts: ' + str(all_stats_dicts))
    return all_stats_dicts

# at this point we have reg season and postseason separately so get avg of them
# for a single season at a time
def generate_full_season_stat_dict(player_stat_dict):

    print('\n===Generate Full Season Stats===\n')

    full_season_stat_dict = {}

    full_season_stats = [] # get avg of all parts

    # for season_part, part_stat_dict in player_stat_dict.items():
    #     for stat_name, stat_dict in part_stat_dict.items():

    return full_season_stat_dict

# use player_team to get away/home team to get game key to get players in game
def generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, all_players_in_games_dict={}, player_team=''):

    print('\n===Generate Player Stat Dict===\n')

    print('===' + player_name.title() + '===')
    print('===' + player_team.upper() + '===\n')

    player_stat_dict = {}


    # for each teammate out of game (dnp inactive injured), make a new record or add to existing record
    # we need to know all possible teammates
    # which we can get from roster
    # https://www.espn.com/nba/team/roster/_/name/bos/boston-celtics
    # or we could get from box scores we already saved locally
    all_teammates = reader.read_all_teammates(player_name, all_players_in_games_dict, player_team)


    # get current opponent if available so we can focus on current conditions
    # if we do not know current opponent then show for all opps
    opponent = ''
    print('projected_lines_dict: ' + str(projected_lines_dict))
    if player_name in projected_lines_dict.keys():
        opponent = projected_lines_dict[player_name]['opp'].lower() # collect data against opponent to see previous matchups


    season_year = 2023


    all_seasons_pts_dicts = {}
    all_seasons_rebs_dicts = {}
    all_seasons_asts_dicts = {}
    all_seasons_winning_scores_dicts = {}
    all_seasons_losing_scores_dicts = {}
    all_seasons_minutes_dicts = {}
    all_seasons_fgms_dicts = {}
    all_seasons_fgas_dicts = {}
    all_seasons_fg_rates_dicts = {}
    all_seasons_threes_made_dicts = {}
    all_seasons_threes_attempts_dicts = {}
    all_seasons_threes_rates_dicts = {}
    all_seasons_ftms_dicts = {}
    all_seasons_ftas_dicts = {}
    all_seasons_ft_rates_dicts = {}
    all_seasons_bs_dicts = {}
    all_seasons_ss_dicts = {}
    all_seasons_fs_dicts = {}
    all_seasons_tos_dicts = {}

    all_seasons_stats_dicts = {'pts':all_seasons_pts_dicts, 'reb':all_seasons_rebs_dicts, 'ast':all_seasons_asts_dicts, 'w score':all_seasons_winning_scores_dicts, 'l score':all_seasons_losing_scores_dicts, 'min':all_seasons_minutes_dicts, 'fgm':all_seasons_fgms_dicts, 'fga':all_seasons_fgas_dicts, 'fg%':all_seasons_fg_rates_dicts, '3pm':all_seasons_threes_made_dicts, '3pa':all_seasons_threes_attempts_dicts, '3p%':all_seasons_threes_rates_dicts, 'ftm':all_seasons_ftms_dicts, 'fta':all_seasons_ftas_dicts, 'ft%':all_seasons_ft_rates_dicts, 'blk':all_seasons_bs_dicts, 'stl':all_seasons_ss_dicts, 'pf':all_seasons_fs_dicts, 'to':all_seasons_tos_dicts} # loop through to add all new stats with 1 fcn

    for player_game_log in player_season_logs:

        print("\n===Year " + str(season_year) + "===\n")
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        # for each part of season, reg and post:
        # first get stats for reg season
        season_part = 'regular'

        # all_pts_dicts = {'all':{idx:val,..},..}
        # all_pts_dicts = { 'all':{}, 'home':{}, 'away':{} } # 'opp eg okc':{}, 'day of week eg tue':{}
        # all_rebs_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_asts_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_winning_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_losing_scores_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_minutes_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_fgms_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_fgas_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_fg_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_threes_made_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_threes_attempts_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_threes_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_ftms_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_ftas_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_ft_rates_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_bs_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_ss_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_fs_dicts = { 'all':{}, 'home':{}, 'away':{} }
        # all_tos_dicts = { 'all':{}, 'home':{}, 'away':{} }

        # all_stats_dicts = {'pts':all_pts_dicts, 'reb':all_rebs_dicts, 'ast':all_asts_dicts, 'w score':all_winning_scores_dicts, 'l score':all_losing_scores_dicts, 'min':all_minutes_dicts, 'fgm':all_fgms_dicts, 'fga':all_fgas_dicts, 'fg%':all_fg_rates_dicts, '3pm':all_threes_made_dicts, '3pa':all_threes_attempts_dicts, '3p%':all_threes_rates_dicts, 'ftm':all_ftms_dicts, 'fta':all_ftas_dicts, 'ft%':all_ft_rates_dicts, 'blk':all_bs_dicts, 'stl':all_ss_dicts, 'pf':all_fs_dicts, 'to':all_tos_dicts} # loop through to add all new stats with 1 fcn


        # # if getting data from player game logs read from internet
        # # for game log for particular given season/year
        # # for season in all seasons
        # if len(player_game_log) > 0:
        #     #season_year = '23'
        #     #print("player_game_log:\n" + str(player_game_log))
        #     # we pulled game log from internet

        #     # if we do not know current opponent then show for all opps
        #     opponent = ''
        #     print('projected_lines_dict: ' + str(projected_lines_dict))
        #     if player_name in projected_lines_dict.keys():
        #         opponent = projected_lines_dict[player_name]['opp'].lower() # collect data against opponent to see previous matchups
            
        #     # first loop thru all regular season games, then thru subset of games such as home/away
        #     # or just append to subset array predefined such as all_home_pts = []
        #     next_game_date_obj = datetime.today() # need to see if back to back games 1 day apart

        #     # do 1 loop for reg season and 1 loop for post season
        #     reg_season_game_log = determiner.determine_regular_season_games(player_game_log)

        #     total_season_games = len(reg_season_game_log.index) # so we can get game num from game idx
            
        #     for game_idx, row in reg_season_game_log.iterrows():

        #         # get game type so we can add stat to reg or post season game
        #         game_type = player_game_log.loc[game_idx, 'Type']
        #         print('game_type: ' + str(game_type))
                
        #         #game = player_game_log[game_idx, row]
        #         #print("game:\n" + str(game))
        #         #print("player_game_log.loc[game_idx, 'Type']: " + player_game_log.loc[game_idx, 'Type'])  

        #         # === Collect Stats for Current Game ===

        #         # pts = int(player_game_log.loc[game_idx, 'PTS'])
        #         # rebs = int(player_game_log.loc[game_idx, 'REB'])
        #         # asts = int(player_game_log.loc[game_idx, 'AST'])

        #         # results = player_game_log.loc[game_idx, 'Result']
        #         # #print("results: " + results)
        #         # results = re.sub('[a-zA-Z]', '', results)
        #         # # remove #OT from result string
        #         # results = re.split("\\s+", results)[0]
        #         # #print("results_data: " + str(results_data))
        #         # score_data = results.split('-')
        #         # #print("score_data: " + str(score_data))
        #         # winning_score = int(score_data[0])
        #         # losing_score = int(score_data[1])

        #         # minutes = int(player_game_log.loc[game_idx, 'MIN'])

        #         # fgs = player_game_log.loc[game_idx, 'FG']
        #         # fg_data = fgs.split('-')
        #         # fgm = int(fg_data[0])
        #         # fga = int(fg_data[1])
        #         # fg_rate = round(float(player_game_log.loc[game_idx, 'FG%']), 1)

        #         # #threes = game[three_idx]
        #         # #threes_data = threes.split('-')
        #         # #print("threes_data: " + str(threes_data))
        #         # threes_made = int(player_game_log.loc[game_idx, '3PT_SA'])
        #         # threes_attempts = int(player_game_log.loc[game_idx, '3PT_A'])
        #         # three_rate = round(float(player_game_log.loc[game_idx, '3P%']), 1)

        #         # fts = player_game_log.loc[game_idx, 'FT']
        #         # ft_data = fts.split('-')
        #         # ftm = int(ft_data[0])
        #         # fta = int(ft_data[1])
        #         # ft_rate = round(float(player_game_log.loc[game_idx, 'FT%']), 1)

        #         # bs = int(player_game_log.loc[game_idx, 'BLK'])
        #         # ss = int(player_game_log.loc[game_idx, 'STL'])
        #         # fs = int(player_game_log.loc[game_idx, 'PF'])
        #         # tos = int(player_game_log.loc[game_idx, 'TO'])

        #         # make list to loop through so we can add all stats to dicts with 1 fcn
        #         game_stats = determiner.determine_game_stats(player_game_log, game_idx) #[pts,rebs,asts,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,bs,ss,fs,tos] 


        #         # === Add Stats to Dict ===

        #         # now that we have game stats add them to dict by condition

        #         # values is list of dicts
        #         for stat_idx in range(len(all_stats_dicts.values())):
        #             stat_dict = list(all_stats_dicts.values())[stat_idx]
        #             stat = game_stats[stat_idx]
        #             stat_dict['all'][game_idx] = stat


        #         # define away/home team so we can determine teammates/opponents in players in game
        #         away_abbrev = player_team

        #         game_opp_str = player_game_log.loc[game_idx, 'OPP']
        #         game_opp_abbrev = reader.read_team_abbrev(game_opp_str) # remove leading characters and change irregular abbrevs
        #         home_abbrev = game_opp_abbrev

        #         if re.search('vs',game_opp_str):

        #             # values is list of dicts
        #             for stat_idx in range(len(all_stats_dicts.values())):
        #                 stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 stat_dict['home'][game_idx] = stat

                    
        #             away_abbrev = game_opp_abbrev
        #             home_abbrev = player_team

                    
        #         else: # if not home then away
        #             for stat_idx in range(len(all_stats_dicts.values())):
        #                 stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 stat_dict['away'][game_idx] = stat

                    
        #         print('away_abbrev: ' + away_abbrev)
        #         print('home_abbrev: ' + home_abbrev)

        #         # matchup against opponent
        #         # only add key for current opp bc we dont need to see all opps here
        #         # look for irregular abbrevs like NO and NY
        #         # opponent in form 'gsw' but game log in form 'gs'
        #         # if we do not know the current opponent then show all opps
        #         #game_log_team_abbrev = re.sub('vs|@','',player_game_log.loc[game_idx, 'OPP'].lower()) # eg 'gs'
        #         game_log_team_abbrev = reader.read_team_abbrev(player_game_log.loc[game_idx, 'OPP'])
        #         #print('game_log_team_abbrev: ' + game_log_team_abbrev)
        #         #opp_abbrev = opponent # default if regular
        #         #print('opp_abbrev: ' + opp_abbrev)

        #         # irregular_abbrevs = {'nop':'no', 'nyk':'ny', 'sas': 'sa', 'gsw':'gs' } # for these match the first 3 letters of team name instead
        #         # if opp_abbrev in irregular_abbrevs.keys():
        #         #     #print("irregular abbrev: " + team_abbrev)
        #         #     opp_abbrev = irregular_abbrevs[opp_abbrev]

        #         # if we do not know the current opponent 
        #         # or if we are not given a specific opponent (bc we may want to compare opps)
        #         # then show all opps
        #         if opponent == game_log_team_abbrev or opponent == '':
        #             #print('opp_abbrev == game_log_team_abbrev')
        #             for stat_idx in range(len(all_stats_dicts.values())):
        #                 stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 if not game_log_team_abbrev in stat_dict.keys():
        #                     stat_dict[game_log_team_abbrev] = {}
        #                 stat_dict[game_log_team_abbrev][game_idx] = stat

                    


        #         # see if this game is 1st or 2nd night of back to back bc we want to see if pattern for those conditions
        #         init_game_date_string = player_game_log.loc[game_idx, 'Date'].lower().split()[1] # 'wed 2/15'[1]='2/15'
        #         game_mth = init_game_date_string.split('/')[0]
        #         final_season_year = str(season_year)
        #         if int(game_mth) in range(10,13):
        #             final_season_year = str(season_year - 1)
        #         game_date_string = init_game_date_string + "/" + final_season_year
        #         #print("game_date_string: " + str(game_date_string))
        #         game_date_obj = datetime.strptime(game_date_string, '%m/%d/%Y')
        #         #print("game_date_obj: " + str(game_date_obj))

        #         # if current loop is most recent game (idx 0) then today's game is the next game, if current season
        #         # if last game of prev season then next game after idx 0 (bc from recent to distant) is next season game 1
        #         if game_idx == 0: # see how many days after prev game is date of today's projected lines
        #             # already defined or passed todays_games_date_obj
        #             # todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
        #             # print("todays_games_date_obj: " + str(todays_games_date_obj))
        #             current_year = 2023
        #             if season_year == current_year: # current year
        #                 next_game_date_obj = todays_games_date_obj # today's game is the next game relative to the previous game
        #             else:
        #                 next_game_date_obj = game_date_obj # should be 0 unless we want to get date of next season game
        #         #print("next_game_date_obj: " + str(next_game_date_obj))
        #         # no need to get next game date like this bc we can see last loop
        #         # else: # if not most recent game then we can see the following game in the game log at prev idx
        #         #     next_game_date_string = player_game_log.loc[game_idx-1, 'Date'].lower().split()[1] + "/" + season_year
        #         #     print("next_game_date_string: " + str(next_game_date_string))
        #         #     next_game_date_obj = datetime.strptime(next_game_date_string, '%m/%d/%y')
        #         #     print("next_game_date_obj: " + str(next_game_date_obj))

        #         days_before_next_game_int = (next_game_date_obj - game_date_obj).days
        #         days_before_next_game = str(days_before_next_game_int) + ' before'
        #         #print("days_before_next_game: " + days_before_next_game)

        #         for stat_idx in range(len(all_stats_dicts.values())):
        #             stat_dict = list(all_stats_dicts.values())[stat_idx]
        #             stat = game_stats[stat_idx]
        #             if not days_before_next_game in stat_dict.keys():
        #                 stat_dict[days_before_next_game] = {}
        #             stat_dict[days_before_next_game][game_idx] = stat

        #         init_prev_game_date_string = ''
        #         if len(player_game_log.index) > game_idx+1:
        #             init_prev_game_date_string = player_game_log.loc[game_idx+1, 'Date'].lower().split()[1]
                
        #             prev_game_mth = init_prev_game_date_string.split('/')[0]
        #             final_season_year = str(season_year)
        #             if int(prev_game_mth) in range(10,13):
        #                 final_season_year = str(season_year - 1)
        #             prev_game_date_string = init_prev_game_date_string + "/" + final_season_year
        #             #print("prev_game_date_string: " + str(prev_game_date_string))
        #             prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%Y')
        #             #print("prev_game_date_obj: " + str(prev_game_date_obj))

        #             days_after_prev_game_int = (game_date_obj - prev_game_date_obj).days
        #             days_after_prev_game = str(days_after_prev_game_int) + ' after'
        #             #print("days_after_prev_game: " + days_after_prev_game)

        #             for stat_idx in range(len(all_stats_dicts.values())):
        #                 stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 if not days_after_prev_game in stat_dict.keys():
        #                     stat_dict[days_after_prev_game] = {}
        #                 stat_dict[days_after_prev_game][game_idx] = stat

                

                


        #         # add keys for each day of the week so we can see performance by day of week
        #         # only add key for current dow bc we dont need to see all dows here
                
        #         game_dow = player_game_log.loc[game_idx, 'Date'].lower().split()[0].lower() # 'wed 2/15'[0]='wed'
        #         current_dow = todays_games_date_obj.strftime('%a').lower()
        #         #print('current_dow: ' + str(current_dow))
        #         if current_dow == game_dow:
        #             #print("found same game day of week: " + game_dow)
        #             for stat_idx in range(len(all_stats_dicts.values())):
        #                 stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 if not game_dow in stat_dict.keys():
        #                     stat_dict[game_dow] = {}
        #                 stat_dict[game_dow][game_idx] = stat
        #             #print("stat_dict: " + str(stat_dict))



        #         #====Players in Game stats
        #         # get game players from all game players dict
        #         #game_players = []
        #         #teammates = []
        #         #opponents = []
        #         #print('game_players: ' + str(game_players))
        #         # get current players from roster minus inactive players
        #         # we get current players when we know about the current game 
                
        #         current_players = { 'away': [], 'home': [] } # we get current players from team rosters
        #         #print('current_players: ' + str(current_players))
        #         current_teammates = [] # if blank then show all possible combos/lineups
        #         #print('current_teammates: ' + str(current_teammates))

        #         # we need to get the game key so that we can determine the players in this game
        #         # we got away/home team from vs|@ in opp field in game log
        #         game_key = away_abbrev + ' ' + home_abbrev + ' ' + game_date_string
        #         print('game_key: ' + str(game_key))
        #         # if we do not have the game box score bc it does not exist yet then pass to the next game
        #         # the order we fill the stats dict depends on the order of games played bc we are going game by game
        #         if game_key in all_players_in_games_dict.keys():
        #             game_players = all_players_in_games_dict[game_key] # {away:[],home:[]}
        #             print('game_players: ' + str(game_players))

        #             game_teammates = game_players['away']
        #             if player_team == home_abbrev:
        #                 game_teammates = game_players['home']

        #             # we need players in alphabetical string so we can compare to other games
        #             game_teammates_str = generate_players_string(game_teammates)

        #             # only add key for current teammates bc we dont need to see all teammates here
        #             # if no inactive players given then we can see all previous games with any (even 1) of current teammates
        #             # but what if a prev game has a player that is not playing in current game?
        #             # then that player completely changes the composition of stats
        #             # does the prev game have to have all the current teammates to pass the check?
        #             # or can it be missing a current player? 
        #             # if prev game is missing current player then that will completely change the comp also
        #             # if we are not sure who is playing in current game then show all possible teammates
        #             # once we get current roster, we can narrow it down to those possible players
        #             # then we can narrow it down further when we get inactive players list for the current game
        #             #current_teammates_in_prev_game = determiner.determine_current_teammates_in_game(game_teammates, current_teammates)
        #             #if len(current_teammates_in_prev_game) > 0: # if any of the current teammates are in the prev game of interest, then add to stats dict for review
        #                 #print("found same game teammates: " + game_teammates)


        #             for stat_idx in range(len(all_stats_dicts.values())):
        #                 stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 if not game_teammates_str in stat_dict.keys():
        #                     stat_dict[game_teammates_str] = {}
        #                 stat_dict[game_teammates_str][game_idx] = stat
        #             #print("stat_dict: " + str(stat_dict))


        #             # for each player/teammate in game, make a new record or add to existing record
        #             for teammate in game_teammates:
        #                 print('teammate: ' + teammate)

        #                 for stat_idx in range(len(all_stats_dicts.values())):
        #                     stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                     stat = game_stats[stat_idx]
        #                     if not teammate in stat_dict.keys():
        #                         stat_dict[teammate] = {}
        #                     stat_dict[teammate][game_idx] = stat
        #                 #print("stat_dict: " + str(stat_dict))


        #             # for each teammate out of game (dnp inactive injured), make a new record or add to existing record
        #             # we need to know all possible teammates, which we get above, once per player
        #             for teammate in all_teammates:
        #                 if teammate not in game_teammates: # teammate out
        #                     teammate_out_key = teammate + ' out'
        #                     for stat_idx in range(len(all_stats_dicts.values())):
        #                         stat_dict = list(all_stats_dicts.values())[stat_idx]
        #                         stat = game_stats[stat_idx]
        #                         if not teammate_out_key in stat_dict.keys():
        #                             stat_dict[teammate_out_key] = {}
        #                         stat_dict[teammate_out_key][game_idx] = stat
        #                     #print("stat_dict: " + str(stat_dict))

        #         else:
        #             print('Warning: Game key not in players in games dict so box score not available!')







        #         # ====Career/All Seasons Stats
        #         # if we find a game played on the same day/mth previous seasons, add a key for this/today's day/mth
        #         #today_date_data = todays_games_date.split('/')
        #         today_mth_day = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day) #today_date_data[0] + '/' + today_date_data[1]
        #         if init_game_date_string == today_mth_day:
        #             #print("found same game day/mth in previous season")
        #             for stat_idx in range(len(all_seasons_stats_dicts.values())):
        #                 stat_dict = list(all_seasons_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 if not game_date_string in stat_dict.keys():
        #                     stat_dict[game_date_string] = {}
        #                     stat_dict[game_date_string][game_idx] = [stat] # we cant use game idx as key bc it gets replaced instead of adding vals
        #                 else:
        #                     if game_idx in stat_dict[game_date_string].keys():
        #                         stat_dict[game_date_string][game_idx].append(stat)
        #                     else:
        #                         stat_dict[game_date_string][game_idx] = [stat]
        #             #print("all_seasons_stats_dicts: " + str(all_seasons_stats_dicts))
        #         # add key for the current game number for this season and add games played from previous seasons (1 per season)
        #         game_num = total_season_games - game_idx # bc going from recent to past
        #         if game_num == num_games_played:
        #             #print("found same game num in previous season")
        #             for stat_idx in range(len(all_seasons_stats_dicts.values())):
        #                 stat_dict = list(all_seasons_stats_dicts.values())[stat_idx]
        #                 stat = game_stats[stat_idx]
        #                 if not num_games_played in stat_dict.keys():
        #                     stat_dict[num_games_played] = {}
        #                     stat_dict[num_games_played][game_idx] = [stat] # we cant use game idx as key bc it gets replaced instead of adding vals
        #                 else:
        #                     if game_idx in stat_dict[num_games_played].keys():
        #                         stat_dict[num_games_played][game_idx].append(stat)
        #                     else:
        #                         stat_dict[num_games_played][game_idx] = [stat]
        #             #print("all_seasons_stats_dicts: " + str(all_seasons_stats_dicts))


        #         # after all keys are set, set next game as current game for next loop
        #         next_game_date_obj = game_date_obj # next game bc we loop from most to least recent

        # else:
        #     # if getting data from file, may not have game log from internet source
        #     # data_type = "Game Log"
        #     # player_season_log = reader.read_season_log_from_file(data_type, player_name, 'tsv')
        #     print('Warning: No game log for player: ' + player_name)

        # at this point we have fully populated all stats dicts for this player's season
        # add all stats for this player's season to all players stats dicts
        # if player_name not in all_players_stats_dicts.keys():
        #     all_players_stats_dicts[player_name] = {}
        # all_players_stats_dicts[player_name][season_year] = all_stats_dicts
        # print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
        
        # gen all stats dicts for this part of this season
        if season_year not in player_stat_dict.keys():
            player_stat_dict[season_year] = {}
        
        player_stat_dict[season_year][season_part] = generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_team, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part) 
        # test
        #player_stat_dict[season_year] = generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_team, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part) 

        # after adding reg season stats, add postseason stats
        season_part = 'postseason'
        player_stat_dict[season_year][season_part] = generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_team, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part) 
        
        # combine reg and postseason
        season_part = 'full'
        player_stat_dict[season_year][season_part] = generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_team, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part) #generate_full_season_stat_dict(player_stat_dict)

        season_year -= 1

    print('player_stat_dict: ' + str(player_stat_dict))
    return player_stat_dict

# we use all_players_stats_dicts = {player name:{stat name:{}}}
# to reference stats 
# all_player_season_logs_dict = {player name:{year:{condition:{stat:[]}}}}
# projected_lines_dict = {player name:{stat:value,..,loc:val,opp:val}}
# use projected lines input param to get opponent
# use today game date to get day and break conditions
def generate_all_players_stats_dicts(all_player_season_logs_dict, projected_lines_dict, todays_games_date_obj):
    print('\n===Generate All Players Stats Dicts===\n')
    all_players_stats_dicts = {}

    for player_name, player_season_logs in all_player_season_logs_dict.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj)
        all_players_stats_dicts[player_name] = player_stat_dict


    print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
    return all_players_stats_dicts

# we are looking for the stat val reached at least 90% of games
# so from 0 to max stat val, get record reached games over total games
# player_stat_records = []
# no need to make dict because stat val = idx bc going from 0 to N
#player_stat_records: {'all': {2023: {'regular': {'pts': 
def generate_player_stat_records(player_name, player_stat_dict):
    print('\n===Generate Player Stat Record===\n')
    print('===' + player_name.title() + '===\n')

    player_stat_records = {}

    # first show reg season, then post, then combined

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_full_season_stat_dict in player_stat_dict.items():
        print("\n===Year " + str(season_year) + "===\n")

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            print("\n===Season Part " + str(season_part) + "===\n")

            # all_pts_dicts = {'all':{idx:val,..},..}
            # all_pts_dicts = {'all':{1:20}}
            # key=condition, val={idx:stat}
            all_pts_dicts = player_season_stat_dict['pts']
            # all_rebs_dicts = player_season_stat_dict['reb']
            # all_asts_dicts = player_season_stat_dict['ast']
            # all_threes_made_dicts = player_season_stat_dict['3pm']
            # all_bs_dicts = player_season_stat_dict['blk']
            # all_ss_dicts = player_season_stat_dict['stl']
            # all_tos_dicts = player_season_stat_dict['to']
            if len(all_pts_dicts['all'].keys()) > 0:

                #all_stats_counts_dict = { 'all': [], 'home': [], 'away': [] }

                # key represents set of conditions of interest eg home/away
                for condition in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    print("\n===Condition " + str(condition) + "===\n")

                    # reset for each condition
                    stat_names = ['pts','reb','ast','3pm']

                    # for each stat type/name (eg pts, reb, etc)
                    # loop from 0 to max stat val to get record over stat val for period of all games
                    for stat_name in stat_names:

                        print("\n===Stat name " + str(stat_name) + "===\n")

                        # reset for each stat name/type
                        all_games_reached = [] # all_stat_counts = []
                        all_probs_stat_reached = []

                        stat_vals = list(player_season_stat_dict[stat_name][condition].values())
                        print('stat_vals: ' + str(stat_vals))
                        num_games_played = len(stat_vals)
                        print('num games played ' + condition + ': ' + str(num_games_played))
                        if num_games_played > 0:
                            # max(stat_vals)+1 bc we want to include 0 and max stat val
                            for stat_val in range(0,max(stat_vals)+1):
                                num_games_reached = 0 # stat count, reset for each check stat val bc new count
                                # loop through games to get count stat val >= game stat val
                                for game_idx in range(num_games_played):
                                    game_stat_val = stat_vals[game_idx]
                                    if game_stat_val >= int(stat_val):
                                        num_games_reached += 1

                                    all_games_reached.append(num_games_reached) # one count for each game

                                print('num_games_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(num_games_reached)) 
                                

                                prob_stat_reached = str(num_games_reached) + '/' + str(num_games_played)
                                print('prob_stat_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(prob_stat_reached)) 

                                all_probs_stat_reached.append(prob_stat_reached)


                        if condition in player_stat_records.keys():
                            #print("conditions " + conditions + " in streak tables")
                            player_condition_records_dicts = player_stat_records[condition]
                            if season_year in player_condition_records_dicts.keys():
                                #player_condition_records_dicts[season_year][stat_name] = all_probs_stat_reached

                                player_season_condition_records_dicts = player_condition_records_dicts[season_year]
                                if season_part in player_season_condition_records_dicts.keys():
                                    player_season_condition_records_dicts[season_part][stat_name] = all_probs_stat_reached
                                else:
                                    player_season_condition_records_dicts[season_part] = { stat_name: all_probs_stat_reached }
                            
                            else:
                                #player_condition_records_dicts[season_year] = { stat_name: all_probs_stat_reached }

                                player_condition_records_dicts[season_year] = {}
                                player_season_condition_records_dicts = player_condition_records_dicts[season_year]
                                player_season_condition_records_dicts[season_part] = { stat_name: all_probs_stat_reached }

                            #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                        else:
                            #print("conditions " + conditions + " not in streak tables")
                            player_stat_records[condition] = {}
                            player_condition_records_dicts = player_stat_records[condition]

                            #player_condition_records_dicts[season_year] = { stat_name: all_probs_stat_reached }

                            player_condition_records_dicts[season_year] = {}
                            player_season_condition_records_dicts = player_condition_records_dicts[season_year]
                            player_season_condition_records_dicts[season_part] = { stat_name: all_probs_stat_reached }

    #player_stat_records: {'all': {2023: {'regular': {'pts': 
    print('player_stat_records: ' + str(player_stat_records))
    return player_stat_records








# at this point we should have projected_lines_dict either by external source or player averages
# the record we are generating is a measure of determining consistency but there may be better ways
# current_year needed to determine avg line if no projected line given
def generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts={}, current_year=2023):

    print('\n===Generate Player Records Dict===\n')
    print('===' + player_name.title() + '===\n')

    player_records_dicts = {}


    # if we do not have projected lines then we can use player means as lines
    # we pass in projected lines as param so at this point we already have actual projected lines or averages to determine record above and below line
    # we could get avgs from stats but we already compute avgs so we can get it from that source before running this fcn
    player_projected_lines = {}
    if player_name in projected_lines_dict.keys():
        player_projected_lines = projected_lines_dict[player_name]
    else:
        print('Warning: Player ' + player_name + ' not in projected lines!')
        projected_lines_dict[player_name] = player_medians_dicts['all'][current_year]

        player_avg_lines = player_medians_dicts['all'][current_year]
        print('player_avg_lines: ' + str(player_avg_lines))

        stats_of_interest = ['pts','reb','ast','3pm','blk','stl','to'] # we decided to focus on these stats to begin
        season_part_of_interest = 'regular' # reg or post season
        for stat in stats_of_interest:
            player_projected_lines[stat] = player_avg_lines[season_part_of_interest][stat]
        
        print('player_projected_lines: ' + str(player_projected_lines))

    #season_year = 2023

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_full_season_stat_dict in player_stat_dict.items():

        print("\n===Year " + str(season_year) + "===\n")
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

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
                #print("all_pts_dicts: " + str(all_pts_dicts))
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

                        
                        if pts >= int(player_projected_lines['pts']):
                            pts_count += 1
                        if rebs >= int(player_projected_lines['reb']):
                            r_count += 1
                        if asts >= int(player_projected_lines['ast']):
                            a_count += 1

                        if threes >= int(player_projected_lines['3pm']):
                            threes_count += 1
                        if blks >= int(player_projected_lines['blk']):
                            b_count += 1
                        if stls >= int(player_projected_lines['stl']):
                            s_count += 1
                        if tos >= int(player_projected_lines['to']):
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
                    over_pts_line = 'PTS ' + str(player_projected_lines['pts']) + "+"
                    over_rebs_line = 'REB ' + str(player_projected_lines['reb']) + "+"
                    over_asts_line = 'AST ' + str(player_projected_lines['ast']) + "+"
                    
                    over_threes_line = '3PM ' + str(player_projected_lines['3pm']) + "+"
                    over_blks_line = 'BLK ' + str(player_projected_lines['blk']) + "+"
                    over_stls_line = 'STL ' + str(player_projected_lines['stl']) + "+"
                    over_tos_line = 'TO ' + str(player_projected_lines['to']) + "+"
                    
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
                        # v2 add game idx for ref and deconstruct later
                        # or could get game idx from player stat dict
                        #prob_over_pts_line = str(game_idx) + ": " + str(p_count) + "/" + current_total
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


                    prob_pts_table = [prob_pts_row]
                    prob_rebs_table = [prob_rebs_row]
                    prob_asts_table = [prob_asts_row]
                    prob_threes_table = [prob_threes_row]
                    prob_blks_table = [prob_blks_row]
                    prob_stls_table = [prob_stls_row]
                    prob_tos_table = [prob_tos_row]
                    
                    all_prob_stat_tables = [prob_pts_table, prob_rebs_table, prob_asts_table, prob_threes_table, prob_blks_table, prob_stls_table, prob_tos_table]

                    all_prob_stat_rows = [prob_pts_row,prob_rebs_row,prob_asts_row,prob_threes_row,prob_blks_row,prob_stls_row,prob_tos_row]

                    # stats counts should include all stats
                    # so we save in dict for reference
                    for stat_idx in range(len(stats_counts)):
                        #stat_counts = stats_counts[stat_idx]
                        prob_row = all_prob_stat_rows[stat_idx] #[0] # only needed first element bc previously formatted for table display
                        #print('prob_row: ' + str(prob_row))
                        # if blk, stl, or to look for 2+
                        # for all, check to see if 1+ or not worth predicting bc too risky
                        #stat_line = prob_table[0].split
                        #stat_line = int(prob_row[0].split()[1][:-1]) # [pts 16+, 1/1, 2/2, ..] -> 16
                        #print('stat_line: ' + str(stat_line))
                        stats_of_interest = ['pts','reb','ast','3pm']
                        # if stat_line < 2: # may need to change for 3 pointers if really strong likelihood to get 1
                        #     continue
                        stat_name = prob_row[0].split()[0].lower() # [pts 16+, 1/1, 2/2, ..] -> pts
                        if stat_name not in stats_of_interest:
                            continue



                        # save player stats in dict for reference
                        # save for all stats, not just streaks
                        # at first there will not be this player name in the dict so we add it
                        streak = prob_row[1:] # [pts 16+, 1/1, 2/2, ..] -> [1/1,2/2,...] or v2 [0:1/1,1:2/2,...]
                        streak_dict = {} # {game idx:streak}

                        # if not player_name in all_records_dicts.keys():
                        #     all_records_dicts[player_name] = {} # init bc player name key not in dict so if we attempt to set its val it is error

                        #     player_records_dicts = all_records_dicts[player_name] # {player name: { condition: { year: { stat: [1/1,2/2,...],.. },.. },.. },.. }

                        #     player_records_dicts[conditions] = {}
                        #     player_all_records_dicts = player_records_dicts[conditions]
                            
                        #     player_all_records_dicts[season_year] = { stat_name: streak }

                        # else: # player already in list

                        #player_records_dicts = all_records_dicts[player_name]
                        if conditions in player_records_dicts.keys():
                            #print("conditions " + conditions + " in streak tables")
                            player_all_records_dicts = player_records_dicts[conditions]
                            if season_year in player_all_records_dicts.keys():
                                #player_all_records_dicts[season_year][stat_name] = streak

                                player_season_records_dicts = player_all_records_dicts[season_year]
                                if season_part in player_season_records_dicts.keys():
                                    player_season_records_dicts[season_part][stat_name] = streak
                                else:
                                    player_season_records_dicts[season_part] = { stat_name: streak }
                            
                            else:
                                #player_all_records_dicts[season_year] = { stat_name: streak }

                                player_all_records_dicts[season_year] = {}
                                player_season_records_dicts = player_all_records_dicts[season_year]
                                player_season_records_dicts[season_part] = { stat_name: streak }

                            #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                        else:
                            #print("conditions " + conditions + " not in streak tables")
                            player_records_dicts[conditions] = {}
                            player_all_records_dicts = player_records_dicts[conditions]

                            #player_all_records_dicts[season_year] = { stat_name: streak }

                            player_all_records_dicts[season_year] = {}
                            player_season_records_dicts = player_all_records_dicts[season_year]
                            player_season_records_dicts[season_part] = { stat_name: streak }

                    # given how many of recent games we care about
                    # later we will take subsection of games with certain settings like home/away
                    # first we get all stats and then we can analyze subsections of stats
                    # eg last 10 games

    print('player_records_dicts: ' + str(player_records_dicts))
    return player_records_dicts

# all players stats dicts = { player: year: stat name: condition: game idx: stat val }
def generate_all_players_records_dicts(all_players_stats_dicts, projected_lines_dict):
    print('\n===Generate All Players Records Dicts===\n')
    all_records_dicts = {}

    # player_stat_dict = { year: .. }
    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_records_dict = generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict)
        all_records_dicts[player_name] = player_records_dict

                
    print('all_records_dicts: ' + str(all_records_dicts))
    return all_records_dicts


def generate_player_avg_range_dict(player_name, player_stat_dict, key):

    print('\n===Generate Player Average Range Dict: ' + key.title() + '===\n')

    player_avg_range_dict = {}

    print('\n===' + player_name.title() + '===\n')

    #season_year = 2023

    for season_year, player_full_season_stat_dict in player_stat_dict.items():

        print("\n===Year " + str(season_year) + "===\n")
        print('player_full_season_stat_dict: ' + str(player_full_season_stat_dict))
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            print("\n===Season Part " + str(season_part) + "===\n")
            print('player_season_stat_dict: ' + str(player_season_stat_dict))

            all_pts_dicts = player_season_stat_dict['pts']
            if len(all_pts_dicts['all'].keys()) > 0:
                # no matter how we get data, 
                # next we compute relevant results

                # first for all then for subsets like home/away
                # all_pts_dict = { 'all':[] }
                # all_pts_means_dict = { 'all':0, 'home':0, 'away':0 }

                # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
                #print("all_pts_dict: " + str(all_pts_dict))
                print("all_pts_dicts: " + str(all_pts_dicts))
                # all_pts_dicts = {'all':{1:20}}
                # key=condition, val={idx:stat}

                
                #compute stats from data
                # key represents set of conditions of interest eg home/away
                for conditions in all_pts_dicts.keys(): # all stats dicts have same keys so we use first 1 as reference

                    #print('conditions: ' + conditions)
                    # reset for each set of conditions
                    header_row = ['Output']
                    stat_avg_ranges = [key.title()] #{pts:'',reb...}
                    # stat_medians = ['Median']
                    # stat_modes = ['Mode']
                    # stat_mins = ['Min']
                    # stat_maxes = ['Max']

                    for stat_key, stat_dict in player_season_stat_dict.items(): # stat key eg pts
                        #print('stat_key: ' + stat_key)
                        header_row.append(stat_key.upper())

                        stat_vals = list(stat_dict[conditions].values())
                        #print("stat_vals: " + str(stat_vals))

                        stat_avg_range = 0
                        if len(stat_vals) > 0:
                            if key == 'mean':
                                stat_avg_range = round(numpy.mean(stat_vals), 1)
                            elif key == 'median':
                                stat_avg_range = int(numpy.median(stat_vals))
                            elif key == 'mode':
                                stat_avg_range = stats.mode(stat_vals, keepdims=False)[0]
                            elif key == 'min':
                                stat_avg_range = numpy.min(stat_vals)
                            elif key == 'max':
                                stat_avg_range = numpy.max(stat_vals)
                            else:
                                print('Warning: No Avg Range Key Given! ')

                        stat_avg_ranges.append(stat_avg_range)

                        # stat_medians.append(stat_median)
                        # stat_modes.append(stat_mode)
                        # stat_mins.append(stat_min)
                        # stat_maxes.append(stat_max)



                        # save player stats in dict for reference
                        # save for all stats, not just streaks
                        # at first there will not be this player name in the dict so we add it
                        stat_name = stat_key
                        if stat_name == '3p':
                            stat_name = '3pm'

                        # for now assume if all means dicts is populated then median, mode, min and max are as well
                        # if not player_name in player_avg_range_dict.keys():
                        #     player_avg_range_dict[player_name] = {} # init bc player name key not in dict so if we attempt to set its val it is error
                        #     # all_medians_dicts[player_name] = {}
                        #     # all_modes_dicts[player_name] = {}
                        #     # all_mins_dicts[player_name] = {}
                        #     # all_maxes_dicts[player_name] = {}

                        #     player_means_dicts = all_means_dicts[player_name] # {player name: { condition: { year: { stat: [1/1,2/2,...],.. },.. },.. },.. }
                        #     player_medians_dicts = all_medians_dicts[player_name]
                        #     player_modes_dicts = all_modes_dicts[player_name]
                        #     player_mins_dicts = all_mins_dicts[player_name]
                        #     player_maxes_dicts = all_maxes_dicts[player_name]

                        #     player_means_dicts[conditions] = {}
                        #     player_medians_dicts[conditions] = {}
                        #     player_modes_dicts[conditions] = {}
                        #     player_mins_dicts[conditions] = {}
                        #     player_maxes_dicts[conditions] = {}
                        #     player_all_means_dicts = player_means_dicts[conditions]
                        #     player_all_medians_dicts = player_medians_dicts[conditions]
                        #     player_all_modes_dicts = player_modes_dicts[conditions]
                        #     player_all_mins_dicts = player_mins_dicts[conditions]
                        #     player_all_maxes_dicts = player_maxes_dicts[conditions]
                            
                        #     player_all_means_dicts[season_year] = { stat_name: stat_mean }
                        #     player_all_medians_dicts[season_year] = { stat_name: stat_median }
                        #     player_all_modes_dicts[season_year] = { stat_name: stat_mode }
                        #     player_all_mins_dicts[season_year] = { stat_name: stat_min }
                        #     player_all_maxes_dicts[season_year] = { stat_name: stat_max }

                        # else: # player already in list

                        if conditions in player_avg_range_dict.keys():
                            #print("conditions " + conditions + " in streak tables")
                            player_all_avg_range_dicts = player_avg_range_dict[conditions]

                            if season_year in player_all_avg_range_dicts.keys():
                                #player_all_avg_range_dicts[season_year][stat_name] = stat_avg_range

                                player_season_avg_range_dicts = player_all_avg_range_dicts[season_year]
                                if season_part in player_season_avg_range_dicts.keys():
                                    player_season_avg_range_dicts[season_part][stat_name] = stat_avg_range
                                else:
                                    player_season_avg_range_dicts[season_part] = { stat_name: stat_avg_range }

                            else:
                                #player_all_avg_range_dicts[season_year] = { stat_name: stat_avg_range }

                                player_all_avg_range_dicts[season_year] = {}
                                player_season_avg_range_dicts = player_all_avg_range_dicts[season_year]
                                player_season_avg_range_dicts[season_part] = { stat_name: stat_avg_range }

                            #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                        else:
                            #print("conditions " + conditions + " not in streak tables")
                            player_avg_range_dict[conditions] = {}

                            player_all_avg_range_dicts = player_avg_range_dict[conditions]
                            
                            #player_all_avg_range_dicts[season_year] = { stat_name: stat_avg_range }
                        
                            player_all_avg_range_dicts[season_year] = {}
                            player_season_avg_range_dicts = player_all_avg_range_dicts[season_year]
                            player_season_avg_range_dicts[season_part] = { stat_name: stat_avg_range }



                    # output_table = [header_row, stat_means, stat_medians, stat_modes, stat_mins, stat_maxes]

                    # output_title = str(conditions).title() + ", " + str(season_year)
                    # if re.search('before',conditions):
                    #     output_title = re.sub('Before','days before next game', output_title).title()
                    # elif re.search('after',conditions):
                    #     output_title = re.sub('After','days after previous game', output_title).title()
                    
                    # print("\n===" + player_name.title() + " Average and Range===\n")
                    # print(output_title)
                    # print(tabulate(output_table))

    print('player_avg_range_dict: ' + str(player_avg_range_dict))
    return player_avg_range_dict


def generate_all_players_avg_range_dicts(all_players_stats_dicts):

    print('\n===Generate All Players Averages===\n')

    all_means_dicts = {}
    all_medians_dicts = {}
    all_modes_dicts = {}
    all_mins_dicts = {}
    all_maxes_dicts = {}

    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_all_avg_range_dicts = {'mean':{},'median':{},'mode':{},'min':{},'max':{}}
        for key in player_all_avg_range_dicts.keys():
            player_all_avg_range_dicts[key] = generate_player_avg_range_dict(player_name, player_stat_dict, key)
        
        player_avg_range_dict = generate_player_avg_range_dict(player_name, player_stat_dict)
        # todo: reorganize
        all_means_dicts[player_name] = generate_player_avg_range_dict(player_name, player_stat_dict)
        all_medians_dicts[player_name] = player_avg_range_dict['median']
        all_modes_dicts[player_name] = player_avg_range_dict['mode']
        all_mins_dicts[player_name] = player_avg_range_dict['min']
        all_maxes_dicts[player_name] = player_avg_range_dict['max']

        


    # print('all_means_dicts: ' + str(all_means_dicts))
    # print('all_medians_dicts: ' + str(all_medians_dicts))
    # print('all_modes_dicts: ' + str(all_modes_dicts))

    all_avgs_dicts = { 'mean': all_means_dicts, 'median': all_medians_dicts, 'mode': all_modes_dicts, 'min': all_mins_dicts, 'max': all_maxes_dicts }
    print('all_avgs_dicts: ' + str(all_avgs_dicts))
    return all_avgs_dicts

# if player names is blank, use all players found in raw projected lines
# use player_espn_ids_dict to get teams
def generate_projected_lines_dict(raw_projected_lines, player_espn_ids_dict={}, player_teams={}, player_names=[]):

    # need data type and input type to get file name
    # data_type = "Player Lines"

    # # optional setting game date if processing a day in advance
    # todays_games_date_str = '' # format: m/d/y, like 3/14/23. set if we want to look at games in advance
    # todays_games_date_obj = datetime.today() # by default assume todays game is actually today and we are not analyzing in advance
    # if todays_games_date_str != '':
    #     todays_games_date_obj = datetime.strptime(todays_games_date_str, '%m/%d/%y')
    
    # input_type = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day)

    # # raw projected lines in format: [['Player Name', 'O 10 +100', 'U 10 +100', 'Player Name', 'O 10 +100', 'U 10 +100', Name', 'O 10 +100', 'U 10 +100']]
    # raw_projected_lines = reader.extract_data(data_type, input_type, extension='tsv', header=True) # tsv no header
    # print("raw_projected_lines: " + str(raw_projected_lines))

    # if len(player_names) == 0:
    #     player_names = determiner.determine_all_player_names(raw_projected_lines)

    if len(player_teams.keys()) == 0:
        player_teams = reader.read_all_players_teams(player_espn_ids_dict, read_new_teams=False) # only read team from internet if not saved

    # convert raw projected lines to projected lines
    projected_lines = reader.read_projected_lines(raw_projected_lines, player_teams)

    projected_lines_dict = {}
    header_row = projected_lines[0]
    for player_lines in projected_lines[1:]:
        player_name = player_lines[0].lower()
        projected_lines_dict[player_name] = dict(zip(header_row[1:],player_lines[1:]))
    print("projected_lines_dict: " + str(projected_lines_dict))

    return projected_lines_dict


# show data in columns for viewing
# we use player_stat_dicts to get game idxs for reference to records/streaks
def generate_player_outcome_data(condition, year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dicts={}):

    print('\n===Generate Player Outcome Data===\n')
    #print('condition: ' + str(condition))
    #print('player_records_dict: ' + str(player_records_dict))

    record_key = condition + ' record'
    player_outcome_dict[record_key] = ''

    if condition in player_records_dict.keys():
        #print("current_teammates_str " + current_teammates_str + " in all records dicts")
        # init record condition_record format ['1/1',..]
        # desired format 1/1,..
        # remove brackets and quotes
        season_part = 'regular'
        condition_year_record = player_records_dict[condition][year][season_part]
        condition_record = ''
        if stat_name in condition_year_record.keys():
            condition_record = player_records_dict[condition][year][season_part][stat_name]
            condition_record = determiner.determine_record_outline(condition_record)
            condition_record = writer.convert_list_to_string(condition_record)
            player_outcome_dict[record_key] = str(condition_record) #condition + ': ' + str(teammates_record)
        else:
            print('Warning: stat_name ' + stat_name + ' not in condition record ' + str(condition_year_record) + '!')

        # print game idxs beside record bc simplest
        game_idxs = list(player_stat_dicts[year][season_part][stat_name][condition].keys())
        record_idx_key = condition + ' record idx'
        player_outcome_dict[record_idx_key] = str(game_idxs)
    else:
        print("condition " + condition + " NOT in all records dicts")

    #print("pre_dict: " + str(pre_dict))
    # mean_key = condition + ' mean'
    # player_outcome_dict[mean_key] = ''
    # median_key = condition + ' median'
    # player_outcome_dict[median_key] = ''
    # mode_key = condition + ' mode'
    # player_outcome_dict[mode_key] = ''
    # min_key = condition + ' min'
    # player_outcome_dict[min_key] = ''
    # max_key = condition + ' max'
    # player_outcome_dict[max_key] = ''

    
    #print("all_means_dicts: " + str(all_means_dicts))
    # if condition in player_means_dicts.keys():
    #     condition_mean = player_means_dicts[condition][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
    #     player_outcome_dict[mean_key] = condition_mean

    # if condition in player_medians_dicts.keys():
    #     condition_median = player_medians_dicts[condition][year][stat_name]
    #     player_outcome_dict[median_key] = condition_median

    # if condition in player_modes_dicts.keys():
    #     condition_mode = player_modes_dicts[condition][year][stat_name]
    #     player_outcome_dict[mode_key] = condition_mode

    # if condition in player_mins_dicts.keys():
    #     condition_min = player_mins_dicts[condition][year][stat_name]
    #     player_outcome_dict[min_key] = condition_min

    # if condition in player_maxes_dicts.keys():
    #     condition_max = player_maxes_dicts[condition][year][stat_name]
    #     player_outcome_dict[max_key] = condition_max


# prediction is really a list of features that we must assess to determine the probability of both/all outcomes
#def generate_player_prediction(player_name, player_season_logs):
def generate_player_all_outcomes_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, player_position='', all_matchup_data=[], all_players_in_games_dict={}, player_team='', player_stat_dict={}):

    print('\n===Generate Player Outcome===\n')

    print('===' + player_name.title() + '===')
    print('===' + player_team.upper() + '===\n')

    player_all_outcomes_dict = {} # {stat name:{outcome,record,avg,range,matchup}}

    # organize external data into internal structure
    if len(player_stat_dict.keys()) == 0: # use given stat dict if available, else get from logs
        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, all_players_in_games_dict, player_team)

    


    player_all_avg_range_dicts = {'mean':{},'median':{},'mode':{},'min':{},'max':{}}
    for key in player_all_avg_range_dicts.keys():
        player_all_avg_range_dicts[key] = generate_player_avg_range_dict(player_name, player_stat_dict, key)
    #player_avg_range_dict = generate_player_all_avg_range_dicts(player_name, player_stat_dict)
    print('player_all_avg_range_dicts: ' + str(player_all_avg_range_dicts))
    player_means_dicts = player_all_avg_range_dicts['mean']
    player_medians_dicts = player_all_avg_range_dicts['median']
    player_modes_dicts = player_all_avg_range_dicts['mode']
    player_mins_dicts = player_all_avg_range_dicts['min']
    player_maxes_dicts = player_all_avg_range_dicts['max']

    # determine the record over projected line or avg stat val
    print('projected_lines_dict before records: ' + str(projected_lines_dict))
    player_records_dict = generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts)


    # determine the stat val with record above 90%
    # player_consistent_stat_vals = {} same format as player stat records but with single max. consistent val for each stat for each condition
    #player_consistent_stat_vals = generate_consistent_stat_vals(player_name, player_stat_dict)
    #player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
    #writer.display_consistent_stats(all_player_consistent_stats)



    current_season_log = player_season_logs[0]
    season_year = 2023
    prev_game_date_obj = determiner.determine_prev_game_date(current_season_log, season_year) # exclude all star and other special games
    # prev_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] + "/" + season_year # eg 'wed 2/15' to '2/15/23'
    # prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%y')
    days_after_prev_game = (todays_games_date_obj - prev_game_date_obj).days

    player_lines = {}
    loc_of_interest = '' # if we want to see both locations we know only home/away
    opponent = '' # if we want to see all opponents we need all opp keys to follow unique format or list of all possible opponents to find keys
    if player_name in projected_lines_dict.keys():
        print('projected_lines_dict: ' + str(projected_lines_dict))
        player_lines['regular'] = projected_lines_dict[player_name]
        reg_player_lines = player_lines['regular']
        if 'loc' in reg_player_lines.keys():
            loc_of_interest = reg_player_lines['loc'].lower()
        if 'opp' in reg_player_lines.keys():
            opponent = reg_player_lines['opp'].lower()
    print('player_lines: ' + str(player_lines))

    time_after = str(days_after_prev_game) + ' after'
    current_dow = todays_games_date_obj.strftime('%a').lower()

    current_teammates_str = '' # if we are given current teamates of interest then we can focus on these, else show all


    all_matchups_dicts = {} # store all matchup data (avg and rank) for each opponent/team


    # make an outcome for each stat
    print('player_stat_dict: ' + str(player_stat_dict))
    stats_of_interest = ['pts','reb','ast','3pm'] # this is if we have all the lines available but we only want subset. but if some of the lines are unavailable then print out their outcomes using their median as the line but only if they are a stat of interest
    year = 2023
    for season_part, season_part_lines in player_lines.items():

        print('\n===Season Part: ' + season_part + '===\n')
        print('season_part_lines: ' + str(season_part_lines))

        for stat_name in stats_of_interest:
            player_outcome_dict = {} # fields: 'outcome', 'streak', 'record', 'avg', 'range', 'matchup'

            stat_line = season_part_lines[season_part][stat_name]
            player_outcome = player_name.title() + ' ' + str(stat_line) + '+ ' + stat_name # initially express over/under as over+ with assumption that under=100-over bc we are displaying possibility before assessing probability
            print('player_outcome: ' + player_outcome)
            player_outcome_dict['outcome'] = player_outcome

            overall_record = ''
            if season_part in player_records_dict['all'][year].keys():
                overall_record = player_records_dict['all'][year][season_part][stat_name] # { 'player name': { 'all': {year: { pts: '1/1,2/2..', stat: record, .. },...}, 'home':{year:{ stat: record, .. },.. }, 'away':{year:{ stat: record, .. }} } }
                #print('overall_record: ' + str(overall_record))
                overall_record = determiner.determine_record_outline(overall_record)
                player_outcome_dict['overall record'] = overall_record

            # # add avg and range in prediction, for current condition, all
            # player_outcome_dict['overall mean'] = ''
            # player_outcome_dict['overall median'] = ''
            # player_outcome_dict['overall mode'] = ''
            # player_outcome_dict['overall min'] = ''
            # player_outcome_dict['overall max'] = ''

            # #print("all_means_dicts: " + str(all_means_dicts))
            # overall_mean = player_means_dicts['all'][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
            # player_outcome_dict['overall mean'] = overall_mean
            
            # overall_median = player_medians_dicts['all'][year][stat_name]
            # player_outcome_dict['overall median'] = overall_median
        
            # overall_mode = player_modes_dicts['all'][year][stat_name]
            # player_outcome_dict['overall mode'] = overall_mode
        
            # overall_min = player_mins_dicts['all'][year][stat_name]
            # player_outcome_dict['overall min'] = overall_min
        
            # overall_max = player_maxes_dicts['all'][year][stat_name]
            # player_outcome_dict['overall max'] = overall_max



            # if location is blank bc we do not have future game
            # if we want to see all locations we can look in player stats dict
            # but here we only show the location for the game of interest
            # what if we want to show all locations, opponents, lineups, etc?
            # we should have a separate function 
            # show all locs unless we have loc of interest
            locs = ['away','home']
            if loc_of_interest != '':
                locs = [loc_of_interest]

            for location in locs:
                location_record = ''
                if season_part in player_records_dict[location][year].keys():
                    location_record = player_records_dict[location][year][season_part][stat_name]
                    location_record = determiner.determine_record_outline(location_record)
                    record_key = location + ' record'
                    player_outcome_dict[record_key] = str(location_record) #v1: location + ': ' + str(location_record)

                # add avg and range in prediction, for current condition, all
                # mean_key = location + ' mean'
                # player_outcome_dict[mean_key] = ''
                # median_key = location + ' median'
                # player_outcome_dict[median_key] = ''
                # mode_key = location + ' mode'
                # player_outcome_dict[mode_key] = ''
                # min_key = location + ' min'
                # player_outcome_dict[min_key] = ''
                # max_key = location + ' max'
                # player_outcome_dict[max_key] = ''

                
                # #print("all_means_dicts: " + str(all_means_dicts))
                # location_mean = player_means_dicts[location][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
                # player_outcome_dict[mean_key] = location_mean
            
                # location_median = player_medians_dicts[location][year][stat_name]
                # player_outcome_dict[median_key] = location_median
            
                # location_mode = player_modes_dicts[location][year][stat_name]
                # player_outcome_dict[mode_key] = location_mode
            
                # location_min = player_mins_dicts[location][year][stat_name]
                # player_outcome_dict[min_key] = location_min
            
                # location_max = player_maxes_dicts[location][year][stat_name]
                # player_outcome_dict[max_key] = location_max




            player_outcome_dict['opponent record'] = ''
            #print('Add opponent ' + opponent + ' record. ')
            #print("all_records_dicts: " + str(all_records_dicts))
            if opponent in player_records_dict.keys():
                opp_record = ''
                if season_part in player_records_dict[opponent][year].keys():
                    opp_record = player_records_dict[opponent][year][season_part][stat_name]
                    player_outcome_dict['opponent record'] = opponent + ': ' + str(opp_record)

            # add avg and range in prediction, for current condition, all
            # player_outcome_dict['opponent mean'] = ''
            # player_outcome_dict['opponent median'] = ''
            # player_outcome_dict['opponent mode'] = ''
            # player_outcome_dict['opponent min'] = ''
            # player_outcome_dict['opponent max'] = ''

            
            # #print("all_means_dicts: " + str(all_means_dicts))
            # if opponent in player_means_dicts.keys():
            #     opponent_mean = player_means_dicts[opponent][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
            #     player_outcome_dict['opponent mean'] = opponent_mean
        
            # if opponent in player_medians_dicts.keys():
            #     opponent_median = player_medians_dicts[opponent][year][stat_name]
            #     player_outcome_dict['opponent median'] = opponent_median
        
            # if opponent in player_modes_dicts.keys():
            #     opponent_mode = player_modes_dicts[opponent][year][stat_name]
            #     player_outcome_dict['opponent mode'] = opponent_mode
        
            # if opponent in player_mins_dicts.keys():
            #     opponent_min = player_mins_dicts[opponent][year][stat_name]
            #     player_outcome_dict['opponent min'] = opponent_min
        
            # if opponent in player_maxes_dicts.keys():
            #     opponent_max = player_maxes_dicts[opponent][year][stat_name]
            #     player_outcome_dict['opponent max'] = opponent_max



            player_outcome_dict['time after record'] = ''
            if time_after in player_records_dict.keys():
                time_after_record = ''
                if season_part in player_records_dict[time_after][year].keys():
                    time_after_record = player_records_dict[time_after][year][season_part][stat_name]
                    time_after_record = determiner.determine_record_outline(time_after_record)
                    player_outcome_dict['time after record'] = time_after + ': ' + str(time_after_record)

            # player_outcome_dict['time after mean'] = ''
            # player_outcome_dict['time after median'] = ''
            # player_outcome_dict['time after mode'] = ''
            # player_outcome_dict['time after min'] = ''
            # player_outcome_dict['time after max'] = ''

            
            # #print("all_means_dicts: " + str(all_means_dicts))
            # if time_after in player_means_dicts.keys():
            #     time_after_mean = player_means_dicts[time_after][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
            #     player_outcome_dict['time after mean'] = time_after_mean
        
            # if time_after in player_medians_dicts.keys():
            #     time_after_median = player_medians_dicts[time_after][year][stat_name]
            #     player_outcome_dict['time after median'] = time_after_median
        
            # if time_after in player_modes_dicts.keys():
            #     time_after_mode = player_modes_dicts[time_after][year][stat_name]
            #     player_outcome_dict['time after mode'] = time_after_mode
        
            # if time_after in player_mins_dicts.keys():
            #     time_after_min = player_mins_dicts[time_after][year][stat_name]
            #     player_outcome_dict['time after min'] = time_after_min
        
            # if time_after in player_maxes_dicts.keys():
            #     time_after_max = player_maxes_dicts[time_after][year][stat_name]
            #     player_outcome_dict['time after max'] = time_after_max




            player_outcome_dict['day record'] = ''
            if current_dow in player_records_dict.keys():
                #print("current_dow " + current_dow + " in all records dicts")
                dow_record = ''
                if season_part in player_records_dict[current_dow][year].keys():
                    dow_record = player_records_dict[current_dow][year][season_part][stat_name]
                    player_outcome_dict['day record'] = current_dow + ': ' + str(dow_record)
            else:
                print("current_dow " + current_dow + " NOT in all records dicts")
            #print("pre_dict: " + str(pre_dict))

            # player_outcome_dict['day mean'] = ''
            # player_outcome_dict['day median'] = ''
            # player_outcome_dict['day mode'] = ''
            # player_outcome_dict['day min'] = ''
            # player_outcome_dict['day max'] = ''

            
            # #print("all_means_dicts: " + str(all_means_dicts))
            # if current_dow in player_means_dicts.keys():
            #     day_mean = player_means_dicts[current_dow][year][stat_name] # { 'player name': { 'all': {year: { pts: 1, stat: mean, .. },...}, 'home':{year:{ stat: mean, .. },.. }, 'away':{year:{ stat: mean, .. }} } }
            #     player_outcome_dict['day mean'] = day_mean
        
            # if current_dow in player_medians_dicts.keys():
            #     day_median = player_medians_dicts[current_dow][year][stat_name]
            #     player_outcome_dict['day median'] = day_median
        
            # if current_dow in player_modes_dicts.keys():
            #     day_mode = player_modes_dicts[current_dow][year][stat_name]
            #     player_outcome_dict['day mode'] = day_mode
        
            # if current_dow in player_mins_dicts.keys():
            #     day_min = player_mins_dicts[current_dow][year][stat_name]
            #     player_outcome_dict['day min'] = day_min
        
            # if current_dow in player_maxes_dicts.keys():
            #     day_max = player_maxes_dicts[current_dow][year][stat_name]
            #     player_outcome_dict['day max'] = day_max


            #find matchups true
            print('all_matchup_data: ' + str(all_matchup_data))
            if len(all_matchup_data) > 0:

                print("\n===Find Matchup for Outcome===\n")

                # stat = streak[0].split(' ')[0].lower() #'pts'
                # print("stat: " + stat)
                #all_matchup_ratings = { 'all':{}, 'pg':{}, 'sg':{}, 'sf':{}, 'pf':{}, 'c':{} } # { 'pg': { 'values': [source1,source2,..], 'ranks': [source1,source2,..] }, 'sg': {}, ... }
                #position_matchup_rating = { 'values':[], 'ranks':[] } # comparing results from different sources
                # current_matchup_data = { pos: [source results] }
                #  sources_results={values:[],ranks:[]}
                current_matchup_data = determiner.determine_matchup_rating(opponent, stat_name, all_matchup_data) # first show matchups from easiest to hardest position for stat. 
                
                # loop thru position in matchup data by position
                # to get matchup table for a given opponent and position
                matchup_dict = {} # {pg:0, sg:0, ..}, for given opponent
                print('current_matchup_data: ' + str(current_matchup_data))
                for pos, sources_results in current_matchup_data.items():
                    print("Position: " + pos.upper())

                    matchup_table_header_row = ['Sources'] # [source1, source2, ..]
                    num_sources = len(sources_results['averages']) #len(source_vals)

                    for source_idx in range(num_sources):
                        source_num = source_idx + 1
                        source_header = 'Source ' + str(source_num)
                        matchup_table_header_row.append(source_header)

                    #{pg:0, sg:0, ..}, for given opponent
                    ranks = sources_results['ranks']
                    s1_matchup_rank = 0
                    s2_matchup_rank = 0
                    s3_matchup_rank = 0
                    if len(ranks) > 0:
                        s1_matchup_rank = ranks[0] #for example test take idx 0
                    if len(ranks) > 1:
                        s2_matchup_rank = ranks[1]
                    if len(ranks) > 2:
                        s3_matchup_rank = ranks[2]
                    
                    # matchup_dict = { pg: { s1: 0 }, sg: { s1: 0 }, .. }
                    matchup_dict[pos] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank }

                    matchup_table = [matchup_table_header_row]
                    for result, source_vals in sources_results.items():
                        source_vals.insert(0, result.title())
                        matchup_table.append(source_vals)


                    print(tabulate(matchup_table))
                

                # ====== once for each outcome, after created matchup dict for opponent ======

                # add matchup dict to all matchup dicts so we can access matchups by opponent, stat and position
                # we could just populate all matchups dict from all matchups data at the beginning instead of this loop for each streak
                print("matchup_dict: " + str(matchup_dict))
                # matchup_dict = { pg: { s1: 0, s2: 0, .. }, sg: { s1: 0 }, .. }
                for pos, rank_dict in matchup_dict.items():
                    s1_matchup_rank = rank_dict['s1']
                    s2_matchup_rank = rank_dict['s2']
                    s3_matchup_rank = rank_dict['s3']
                    # init dicts
                    print("all_matchups_dicts: " + str(all_matchups_dicts))

                    rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                    matchup_rank_mean = rank_avgs['mean']
                    matchup_rank_combined_mean = rank_avgs['combined mean']

                    if not pos in all_matchups_dicts.keys():

                        #print('position ' + pos + ' not in all matchups so it is first loop')
                        all_matchups_dicts[pos] = {}
                        #print("all_matchups_dicts: " + str(all_matchups_dicts))
                        all_matchups_dicts[pos][stat_name] = {}
                        #print("all_matchups_dicts: " + str(all_matchups_dicts))
                        all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                        print("all_matchups_dicts: " + str(all_matchups_dicts))
                    else: # pos in matchups dict so check for stat in pos
                        print('position ' + pos + ' in matchups dict')

                        # all_matchups_dicts = { 'pg': {} }
                        if not stat_name in all_matchups_dicts[pos].keys():
                            print('stat_name ' + stat_name + ' not in position so it is new stat_name')

                            # rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                            # matchup_rank_mean = rank_avgs['mean']
                            # matchup_rank_combined_mean = rank_avgs['combined mean']

                            all_matchups_dicts[pos][stat_name] = {}
                            all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                            print("all_matchups_dicts: " + str(all_matchups_dicts))
                        else: # stat_name is in pos matchups so check if opp in stats
                            print('stat_name ' + stat_name + ' in position matchups dict')
                            if not opponent in all_matchups_dicts[pos][stat_name].keys():
                                print('opponent ' + opponent + ' not in stat so it is new opponent')

                                # rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                                # matchup_rank_mean = rank_avgs['mean']
                                # matchup_rank_combined_mean = rank_avgs['combined mean']

                                all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                                print("all_matchups_dicts: " + str(all_matchups_dicts))
                            else:
                                print('opponent rating added already so continue to next streak')
                                break

                    # if we do not have rank yet then set it
                    # if not opponent in all_matchups_dicts[pos][stat].keys():
                    #     all_matchups_dicts[pos][stat][opponent] = rank
                    
                
                
                # if key not in dict then add it
                #if not opponent in all_matchups_dicts.keys():
                    #all_matchups_dicts[opponent] = matchup_dict # init bc player name key not in dict so if we attempt to set its val it is error

                    #opponent_matchups_dicts = all_matchups_dicts[opponent] # {team name: { position : rank } }

                print("all_matchups_dicts: " + str(all_matchups_dicts))



                # add matchups in prediction, for position
                # currently pre_dict from valid streaks but eventually will be narrowed down further into valid preidctions=streaks+matchups+avg+range etc
                print('\n===Add Matchups to Outcome===\n')
                print('We got matchups so add matchups to outcome. ') # should we do this for each player or even each condition or can we do this 1 big loop after we populate all matchups dict?
                print("all_matchups_dicts: " + str(all_matchups_dicts))
                print("projected_lines_dict: " + str(projected_lines_dict))


                #player_lines = projected_lines_dict[player_name]
                #opponent = player_lines['OPP'].lower()

                #position = all_player_positions[player_name] #'pg' # get player position from easiest source such as game log webpage already visited
                #print("position from all_player_positions: " + player_position)
                player_outcome_dict['s1 matchup'] = ''
                player_outcome_dict['s2 matchup'] = ''
                player_outcome_dict['s3 matchup'] = ''
                player_outcome_dict['matchup mean'] = ''
                player_outcome_dict['matchup combined mean'] = ''

                # pre_dict['matchup relative rank'] = '' # x/5, 5 positions
                # pre_dict['matchup combined relative rank'] = '' # x/3, guard, forward, center bc often combined
                # pre_dict['matchup overall mean'] = ''

                if opponent in all_matchups_dicts[player_position][stat_name].keys():
                    s1_matchup_rank = all_matchups_dicts[player_position][stat_name][opponent]['s1'] # stat eg 'pts' is given for the streak
                    print("s1_matchup_rank: " + str(s1_matchup_rank))
                    s2_matchup_rank = all_matchups_dicts[player_position][stat_name][opponent]['s2'] # stat eg 'pts' is given for the streak
                    s3_matchup_rank = all_matchups_dicts[player_position][stat_name][opponent]['s3'] # stat eg 'pts' is given for the streak
                    player_outcome_dict['s1 matchup'] = s1_matchup_rank
                    player_outcome_dict['s2 matchup'] = s2_matchup_rank
                    player_outcome_dict['s3 matchup'] = s3_matchup_rank

                    matchup_rank_mean = all_matchups_dicts[player_position][stat_name][opponent]['mean'] # stat eg 'pts' is given for the streak
                    matchup_rank_combined_mean = all_matchups_dicts[player_position][stat_name][opponent]['combined mean'] # stat eg 'pts' is given for the streak
                    player_outcome_dict['matchup mean'] = matchup_rank_mean
                    player_outcome_dict['matchup combined mean'] = matchup_rank_combined_mean

                    # Determine Relative Rank
                    # opp_matchup_dict = {} # {pos:{stat:rank,..},..}
                    # print('all_matchups_dicts: ' + str(all_matchups_dicts))
                    # for pos, pos_matchup_dict in all_matchups_dicts.items():
                    #     if pos not in opp_matchup_dict.keys():
                    #         opp_matchup_dict[pos] = {}
                    #     opp_matchup_dict[pos][stat] = pos_matchup_dict[stat][opponent]
                    # print('opp_matchup_dict: ' + str(opp_matchup_dict))

                    # matchup_relative_rank = 1 # 1-5 bc 5 positions, from hardest to easiest bc defense
                    # pre_dict['matchup relative rank'] = matchup_relative_rank 
                else:
                    print("Warning: opponent " + opponent + " not found in all matchups dict! ")


            #if find players in games true we will have populated all_players_in_games_dict
            print('all_players_in_games_dict: ' + str(all_players_in_games_dict))
            if len(all_players_in_games_dict.keys()) > 0:

                print("\n===Find Players in Games for Outcome===\n")

                if len(current_teammates_str) > 0:
                    # use given list of current teammates of interest
                    print('current_teammates_str: ' + str(current_teammates_str))

                    generate_player_outcome_data(current_teammates_str, year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dict) # assigns data to outcome dictionary
                    
                else: # show all teammates bc we do not know current teammates

                    for condition in player_records_dict.keys():

                        if re.search('\.',condition): # eg 'j. brown sg', condition matching list of teammates has player first initial with dot after

                            generate_player_outcome_data(condition, year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dict)



            if season_part not in player_all_outcomes_dict.keys():
                player_all_outcomes_dict[season_part] = {}
            player_all_outcomes_dict[season_part][stat_name] = player_outcome_dict

    print('player_all_outcomes_dict: ' + str(player_all_outcomes_dict))
    return player_all_outcomes_dict

# determine min margin bt ok val and min stat val
# need for all possible stat vals or just ok val
# but ok val is found later
# we will eventually need min margin for each option
# so simply add in extensible now
# we can choose to hide columns to reduce clutter
def generate_min_margin(init_val, stat_dict):
    print('\n===Generate Min Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    print('stat_vals: ' + str(stat_vals))

    min_val = 0 # init
    if len(stat_vals) > 0:
        min_val = min(stat_vals)
    else:
        print('Warning: No stat vals while generating min margin!')

    min_margin = min_val - init_val

    print('min_margin: ' + str(min_margin))
    return min_margin


def generate_mean_margin(init_val, stat_dict):
    print('\n===Generate Mean Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    print('stat_vals: ' + str(stat_vals))

    mean_val = 0 # init
    if len(stat_vals) > 0:
        mean_val = round(numpy.mean(stat_vals), 1)
    else:
        print('Warning: No stat vals while generating min margin!')

    mean_margin = mean_val - init_val

    print('mean_margin: ' + str(mean_margin))
    return mean_margin


def generate_margin(init_val, stat_dict, margin_type='min'):
    print('\n===Generate ' + margin_type.title() + ' Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    print('stat_vals: ' + str(stat_vals))

    val = 0 # init
    margin = 0
    if len(stat_vals) > 0:
        if margin_type == 'mean':
            val = numpy.mean(stat_vals)
            print('val: ' + str(val))
            # we want to round to whole number for easy comparison and we cannot be certain with any more accuracy due to other conditions
            margin = round(val - init_val) 
        else:
            val = min(stat_vals)
            margin = val - init_val
        
    else:
        print('Warning: No stat vals while generating min margin!')

    

    print('margin: ' + str(margin))
    return margin


# record input is prob stat reached as fraction
# output is prob 0-1
def generate_prob_stat_reached(record):

    print('\n===Generate Prob Stat Reached===\n')

    print('record: ' + str(record))

    # if we have no record for a given stat val we will pass record=''
    # bc prob=0
    prob_stat_reached = 0

    if record != '':

        record_data = record.split('/')
        num_games_reached = record_data[0]
        num_games_played = record_data[1]
        #prob_stat_reached = round((float(num_games_reached) / float(num_games_played)) * 100)
        prob_stat_reached = round(float(num_games_reached) / float(num_games_played), 2)
        
    print('prob_stat_reached: ' + str(prob_stat_reached))
    return prob_stat_reached


# consistency=0.9 is desired probability of player reaching stat val
#consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
def generate_consistent_stat_vals(player_name, player_stat_dict, player_stat_records={}, consistency=0.9):
    
    print('\n===Generate Consistent Stat Vals===\n')

    if len(player_stat_records) == 0:
        player_stat_records = generate_player_stat_records(player_name, player_stat_dict)

    
    consistent_stat_vals = {}

    for condition, condition_stat_records in player_stat_records.items():
        print("\n===Condition " + str(condition) + "===\n")

        for season_year, full_season_stat_dicts in condition_stat_records.items():
            print("\n===Year " + str(season_year) + "===\n")

            for season_part, season_stat_dicts in full_season_stat_dicts.items():
                print("\n===Season Part " + str(season_part) + "===\n")

                for stat_name, stat_records in season_stat_dicts.items():
                    print("\n===Stat Name " + str(stat_name) + "===\n")
                    print('stat_records: ' + str(stat_records))

                    # get prob from 0 to 1 to compare to desired consistency
                    consistent_stat_val = 0
                    prob_stat_reached = 1.0
                    consistent_stat_prob = 1.0
                    
                    for stat_val in range(len(stat_records)):
                        #print("\n===Stat Val " + str(stat_val) + "===")
                        # gen prob reached from string record
                        record = stat_records[stat_val] # eg x/y=1/1
                        #print('record: ' + str(record))
                        prob_stat_reached = generate_prob_stat_reached(record)

                        if prob_stat_reached < consistency:
                            break

                        consistent_stat_val = stat_val
                        consistent_stat_prob = prob_stat_reached

                    print('consistent_stat_val: ' + str(consistent_stat_val))
                    print('consistent_stat_prob: ' + str(consistent_stat_prob))

                    # determine second consistent val
                    # we may want to loop for x consistent vals to see trend and error margin
                    second_consistent_stat_val = consistent_stat_val - 1
                    
                    
                    if consistent_stat_val == 0: # usually we want lower stat at higher freq but if 0 then we want to see higher stat for reference
                        # if 3pm
                        if stat_name == '3pm':
                            second_consistent_stat_val = 1
                        else:
                            second_consistent_stat_val = 2
                    elif consistent_stat_val == 1:
                        second_consistent_stat_val = 2 # bc we want to see available projected probability
                    elif stat_name != '3pm': # above for 0,1 all stats are treated similar but 3pm takes all 2+
                        if consistent_stat_val > 2 and consistent_stat_val < 5: # 3,4 na
                            second_consistent_stat_val = 2
                        elif consistent_stat_val > 5 and consistent_stat_val < 8: # 6,7 na
                            second_consistent_stat_val = 5
                        elif consistent_stat_val == 9: # 9 na
                            second_consistent_stat_val = 8

                        # ensure val is available
                        ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
                        if second_consistent_stat_val not in ok_stat_vals:
                            second_consistent_stat_val -= 1

                    # if consistent_stat_val=0 or 1 we see greater val
                    if second_consistent_stat_val > consistent_stat_val: # if consistent_stat_val=0 or 1 we see greater val
                        # if player did not reach higher stat val record=''
                        if len(stat_records) > second_consistent_stat_val:
                            record = stat_records[second_consistent_stat_val]
                        else:
                            record = ''
                    else:
                        record = stat_records[second_consistent_stat_val]
                    second_consistent_stat_prob = generate_prob_stat_reached(record)

                    print('second_consistent_stat_val: ' + str(second_consistent_stat_val))
                    print('second_consistent_stat_prob: ' + str(second_consistent_stat_prob))

                    # determine higher and lower stat val probs for ref

                    # determine prob of regseason consistent val in postseason

                    # also determine prob of postseason consistent val in regseason


                    # determine min margin bt ok val and min stat val
                    # need for all possible stat vals or just ok val
                    # but ok val is found later
                    # we will eventually need min margin for each option
                    # so simply add in extensible now
                    # we can choose to hide columns to reduce clutter
                    stat_dict = player_stat_dict[season_year][season_part][stat_name][condition]
                    min_margin = generate_margin(consistent_stat_val, stat_dict)
                    second_min_margin = generate_margin(second_consistent_stat_val, stat_dict)

                    mean_margin = generate_margin(consistent_stat_val, stat_dict, 'mean')
                    second_mean_margin = generate_margin(second_consistent_stat_val, stat_dict, 'mean')


                    # save data for analysis, sorting and filtering
                    consistent_stat_dict = { 'prob val': consistent_stat_val, 'prob': consistent_stat_prob, 'second prob val': second_consistent_stat_val, 'second prob': second_consistent_stat_prob, 'min margin': min_margin, 'second min margin': second_min_margin, 'mean margin': mean_margin, 'second mean margin': second_mean_margin  }
                    
                    if condition in consistent_stat_vals.keys():
                        #print("conditions " + conditions + " in streak tables")
                        player_condition_consistent_stat_vals = consistent_stat_vals[condition]
                        if season_year in player_condition_consistent_stat_vals.keys():
                            #player_condition_consistent_stat_vals[season_year][stat_name] = consistent_stat_dict

                            player_season_condition_consistent_stat_vals = player_condition_consistent_stat_vals[season_year]
                            if season_part in player_season_condition_consistent_stat_vals.keys():
                                player_season_condition_consistent_stat_vals[season_part][stat_name] = consistent_stat_dict
                            else:
                                player_season_condition_consistent_stat_vals[season_part] = { stat_name: consistent_stat_dict }
                        
                        else:
                            #player_condition_consistent_stat_vals[season_year] = { stat_name: consistent_stat_dict }

                            player_condition_consistent_stat_vals[season_year] = {}
                            player_season_condition_consistent_stat_vals = player_condition_consistent_stat_vals[season_year]
                            player_season_condition_consistent_stat_vals[season_part] = { stat_name: consistent_stat_dict }

                        #player_streak_tables[conditions].append(prob_table) # append all stats for given key
                    else:
                        #print("conditions " + conditions + " not in streak tables")
                        consistent_stat_vals[condition] = {}
                        player_condition_consistent_stat_vals = consistent_stat_vals[condition]
                        
                        #player_condition_consistent_stat_vals[season_year] = { stat_name: consistent_stat_dict }

                        player_condition_consistent_stat_vals[season_year] = {}
                        player_season_condition_consistent_stat_vals = player_condition_consistent_stat_vals[season_year]
                        player_season_condition_consistent_stat_vals[season_part] = { stat_name: consistent_stat_dict }

    # check if regseason stat is available
    # ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
    # year_of_interest = 2023
    # regseason_stats = consistent_stat_vals['all'][year_of_interest]['regular']
    # for stat_dict in regseason_stats.items():
    #     reg_season_stat_val = stat_dict['prob val']
    #     if reg_season_stat_val in ok_stat_vals:
    #         reg_season_ok_stat = reg_season_stat_val # ok=available

    # # determine final available stat val out of possible consistent stat vals
    # # eg if horford reb in playoffs higher than regseason, use regseason stat val's prob in postseason
    # # bc that will show highest prob
    # available_stat_val

    #ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
    # add prob of reaching reg season val in postseason, if different consistent vals

    #consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
    print('consistent_stat_vals: ' + str(consistent_stat_vals))
    return consistent_stat_vals


# all_player_consistent_stats = {} same format as stat records, 
# condition, year, stat name
# for display
# simply flatten bottom level of dict
# by adding its key to header of level above
def generate_all_consistent_stat_dicts(all_player_consistent_stats, all_player_stat_records, all_player_stat_dicts):
    print("\n===Generate All Consistent Stats Dicts===\n")
    #print('all_player_consistent_stats: ' + str(all_player_consistent_stats))
    #print('all_player_stat_records: ' + str(all_player_stat_records))

    player_consistent_stat_data_headers = ['Player', 'S Name', 'Stat', 'Prob', '2nd Stat', '2nd Prob', 'PS', 'PP', '2nd PS', '2nd PP', 'OK Val', 'OK P', 'OK PP']
    final_consistent_stats = [player_consistent_stat_data_headers] # player name, stat name, consistent stat, consistent stat prob

    # so we can sort from high to low prob
    all_consistent_stat_dicts = [] 
    consistent_stat_dict = {}

    for player_name, player_consistent_stats in all_player_consistent_stats.items():
        print('\n===' + player_name.title() + '===\n')
        

        # for now, show only conditon=all
        # give option to set condition and sort by condition
        conditions_of_interest = ['all']
        for condition, condition_consistent_stats in player_consistent_stats.items():
            print('\n===' + condition.title() + '===\n')

            if condition in conditions_of_interest:

                years_of_interest = [2023]
                for year, year_consistent_stats in condition_consistent_stats.items():
                    print('\n===' + str(year) + '===\n')

                    if year in years_of_interest:

                        # for season_part, season_part_consistent_stats in year_consistent_stats.items():
                        #     print(season_part)

                        #     player_season_consistent_stat_data = []

                        # first look at full season, then postseason
                        season_part_consistent_stats = year_consistent_stats['full'] 

                        for stat_name in season_part_consistent_stats.keys():
                            print('\n===' + stat_name.upper() + '===\n')

                            # use consistent_stat_dict to sort
                            consistent_stat_dict = {'player name':player_name, 'stat name':stat_name}
                            

                            #player_consistent_stat_data = [player_name, stat_name]

                            # simply flatten bottom level of dict
                            # by adding its key to header of level above
                            # eg in this case blank for full season and post for postseason
                            season_part = 'full'
                            prob_stat_dict = year_consistent_stats[season_part][stat_name]
                            print('prob_stat_dict: ' + str(prob_stat_dict))

                            prob_stat_key = 'prob val'
                            prob_val = prob_stat_dict[prob_stat_key]
                            full_consistent_stat = prob_val
                            
                            prob_stat_key = 'prob'
                            prob = prob_stat_dict[prob_stat_key]
                            print('prob: ' + str(prob))
                            full_consistent_stat_prob = round(prob * 100)
                            print('full_consistent_stat_prob: ' + str(full_consistent_stat_prob))

                            full_second_consistent_stat = prob_stat_dict['second prob val']
                            full_second_consistent_stat_prob = round(prob_stat_dict['second prob'] * 100)

                            min_margin = prob_stat_dict['min margin']
                            second_min_margin = prob_stat_dict['second min margin']
                            mean_margin = round(prob_stat_dict['mean margin'])
                            second_mean_margin = round(prob_stat_dict['second mean margin'])

                            consistent_stat_dict['prob val'] = full_consistent_stat
                            consistent_stat_dict['prob'] = full_consistent_stat_prob
                            consistent_stat_dict['second prob val'] = full_second_consistent_stat
                            consistent_stat_dict['second prob'] = full_second_consistent_stat_prob

                            consistent_stat_dict['min margin'] = min_margin
                            consistent_stat_dict['second min margin'] = second_min_margin
                            consistent_stat_dict['mean margin'] = mean_margin
                            consistent_stat_dict['second mean margin'] = second_mean_margin



                            # add postseason stat probs separately
                            season_part = 'postseason'

                            post_consistent_stat = 0
                            post_consistent_stat_prob = 0

                            post_second_consistent_stat = 0
                            post_second_consistent_stat_prob = 0

                            if season_part in year_consistent_stats.keys():
                                prob_stat_dict = year_consistent_stats[season_part][stat_name]
                                print('prob_stat_dict: ' + str(prob_stat_dict))

                                prob_stat_key = 'prob val' #defined in loop
                                post_consistent_stat = prob_stat_dict[prob_stat_key]
                                post_consistent_stat_prob = round(prob_stat_dict['prob'] * 100)

                                post_second_consistent_stat = prob_stat_dict['second prob val']
                                post_second_consistent_stat_prob = round(prob_stat_dict['second prob'] * 100)

                                post_min_margin = prob_stat_dict['min margin']
                                post_second_min_margin = prob_stat_dict['second min margin']
                                post_mean_margin = round(prob_stat_dict['mean margin'])
                                post_second_mean_margin = round(prob_stat_dict['second mean margin'])

                                season_part_key = re.sub('season','',season_part)
                                # prob_stat_key = 'prob val' defined above
                                prob_val_key = season_part_key + ' ' + prob_stat_key
                                consistent_stat_dict[prob_val_key] = post_consistent_stat
                                consistent_stat_dict['post prob'] = post_consistent_stat_prob
                                consistent_stat_dict['post second prob val'] = post_second_consistent_stat
                                consistent_stat_dict['post second prob'] = post_second_consistent_stat_prob

                                consistent_stat_dict['post min margin'] = post_min_margin
                                consistent_stat_dict['post second min margin'] = post_second_min_margin
                                consistent_stat_dict['post mean margin'] = post_mean_margin
                                consistent_stat_dict['post second mean margin'] = post_second_mean_margin

                            # add another column to classify if postseason stat < regseason stat so we can group those together

                            # player name, stat name, consistent stat, consistent stat prob
                            player_consistent_stat_data = [player_name, stat_name, full_consistent_stat, full_consistent_stat_prob, full_second_consistent_stat, full_second_consistent_stat_prob, post_consistent_stat, post_consistent_stat_prob, post_second_consistent_stat, post_second_consistent_stat_prob]
                            #consistent_stat_dict = {'player name':player_name, 'stat name':stat_name, 'prob val': full_consistent_stat, 'prob': full_consistent_stat_prob, 'second prob val':full_second_consistent_stat, 'second prob':full_second_consistent_stat_prob}

                            #player_season_consistent_stat_data = player_season_consistent_stat_data + player_consistent_stat_data

                            final_consistent_stats.append(player_consistent_stat_data)

                            all_consistent_stat_dicts.append(consistent_stat_dict)
                            


    print('all_consistent_stat_dicts: ' + str(all_consistent_stat_dicts))

    # determine which keys in dict to sort dicts by
    # we duplicate the corresponding vals in known keys for ref called 'ok val'
    sort_key1 = 'ok val post prob' # default
    sort_key2 = 'ok val prob' # default
    sort_key3 = 'ok val post min margin' # default
    sort_key4 = 'ok val min margin' # default
    sort_key5 = 'ok val post mean margin' # default
    sort_key6 = 'ok val mean margin' # default

    # check if regseason stat is available
    ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
    #year_of_interest = 2023
    #regseason_stats = consistent_stat_vals['all'][year_of_interest]['regular']
    for stat_dict in all_consistent_stat_dicts:

        player_stat_records = all_player_stat_records[stat_dict['player name']]

        stat_name = stat_dict['stat name']
        year = 2023
        season_part = 'postseason' # we want to see postseason prob of regseason stat
        condition = 'all'
        player_stat_dict = all_player_stat_dicts[stat_dict['player name']][year][season_part][stat_name][condition]

        reg_season_stat_val = stat_dict['prob val']
        reg_season_second_stat_val = stat_dict['second prob val']
        reg_season_stat_prob = stat_dict['prob']
        reg_season_second_stat_prob = stat_dict['second prob']

        reg_season_min_margin = stat_dict['min margin']
        reg_season_second_min_margin = stat_dict['second min margin']
        reg_season_mean_margin = stat_dict['mean margin']
        reg_season_second_mean_margin = stat_dict['second mean margin']

        #post_season_stat_val = stat_dict['post prob val']
        #post_season_stat_prob = stat_dict['post prob']

        if reg_season_stat_val in ok_stat_vals: #is available (ie in ok stat vals list)
            stat_dict['ok val'] = reg_season_stat_val # default, ok=available

            stat_dict['ok val prob'] = reg_season_stat_prob 
            # determine which key has the same stat val in post as reg, bc we earlier made sure there would be one
            # can be generalized to fcn called determine matching key
            stat_dict['ok val post prob'] = determiner.determine_ok_val_prob(stat_dict, stat_dict['ok val'], player_stat_records, season_part, stat_name) #post_season_stat_prob 
            # post_season_stat_val_key = determiner.determine_matching_key(stat_dict, stat_dict['ok val']) #'post prob val'
            # # for key, val in stat_dict.items():
            # #     if key != 'ok val':
            # #         if val == stat_dict['ok val'] and not re.search('prob',key):
            # #             post_season_stat_val_key = key

            # post_season_stat_prob_key = re.sub('val','',post_season_stat_val_key)
            # post_season_stat_prob = stat_dict[post_season_stat_prob_key]
            # stat_dict['ok val post prob'] = post_season_stat_prob 

            # if reg_season_stat_val != post_season_stat_val:
            #     stat_dict['ok val post prob'] = post_season_stat_val_prob 

            stat_dict['ok val min margin'] = reg_season_min_margin
            stat_dict['ok val post min margin'] = determiner.determine_ok_val_margin(stat_dict, stat_dict['ok val'], player_stat_dict, stat_name, 'min')

            stat_dict['ok val mean margin'] = reg_season_mean_margin
            stat_dict['ok val post mean margin'] = determiner.determine_ok_val_margin(stat_dict, stat_dict['ok val'], player_stat_dict, stat_name, 'mean')
            

        # if default reg season stat na,
        # first check next lowest val, called second val
        else:
            stat_dict['ok val'] = reg_season_second_stat_val # ok=available

            stat_dict['ok val prob'] = reg_season_second_stat_prob 
            stat_dict['ok val post prob'] = determiner.determine_ok_val_prob(stat_dict, stat_dict['ok val'], player_stat_records, season_part, stat_name) #post_season_stat_prob 
            
            stat_dict['ok val min margin'] = reg_season_second_min_margin
            stat_dict['ok val post min margin'] = determiner.determine_ok_val_margin(stat_dict, stat_dict['ok val'], player_stat_dict, stat_name, 'min')

            stat_dict['ok val mean margin'] = reg_season_second_mean_margin
            stat_dict['ok val post mean margin'] = determiner.determine_ok_val_margin(stat_dict, stat_dict['ok val'], player_stat_dict, stat_name, 'mean')

    # determine final available stat val out of possible consistent stat vals
    # eg if horford reb in playoffs higher than regseason, use regseason stat val's prob in postseason
    # bc that will show highest prob
    #available_stat_val


    sort_keys = [sort_key1, sort_key2, sort_key3, sort_key4, sort_key5, sort_key6]
    sorted_consistent_stat_dicts = sorter.sort_dicts_by_keys(all_consistent_stat_dicts, sort_keys)
    # desired_order = ['player name','stat name','ok val','ok pp','ok p']
    # sorted_consistent_stats = converter.convert_dicts_to_lists(sorted_consistent_stat_dicts)

    # print('sorted_consistent_stats')
    # print(tabulate(player_consistent_stat_data_headers + sorted_consistent_stats))

    # # export
    # for row in sorted_consistent_stats:
    #     export_row = ''
    #     for cell in row:
    #         export_row += str(cell) + ';'

    #     print(export_row)

    return sorted_consistent_stat_dicts

# one outcome per stat of interest so each player has multiple outcomes
def generate_players_outcomes(player_names=[], settings={}, todays_games_date_obj=datetime.today()):

    print('\n===Generate Players Outcomes===\n')

    season_year = 2023 # change to current year

    player_outcomes = {}

    # === gather external data
    # need data type and input type to get file name
    data_type = "Player Lines"

    # optional setting game date if processing a day in advance
    todays_games_date_str = '' # format: m/d/y, like 3/14/23. set if we want to look at games in advance
    todays_games_date_obj = datetime.today() # by default assume todays game is actually today and we are not analyzing in advance
    if todays_games_date_str != '':
        todays_games_date_obj = datetime.strptime(todays_games_date_str, '%m/%d/%y')
    
    # read projected lines or if unavailable get player averages
    input_type = str(todays_games_date_obj.month) + '/' + str(todays_games_date_obj.day)

    # raw projected lines in format: [['Player Name', 'O 10 +100', 'U 10 +100', 'Player Name', 'O 10 +100', 'U 10 +100', Name', 'O 10 +100', 'U 10 +100']]
    raw_projected_lines = reader.extract_data(data_type, input_type, extension='tsv', header=True) # tsv no header
    print("raw_projected_lines: " + str(raw_projected_lines))

    if len(player_names) == 0:
        player_names = determiner.determine_all_player_names(raw_projected_lines)

    player_espn_ids_dict = reader.read_all_player_espn_ids(player_names)


    player_teams = reader.read_all_players_teams(player_espn_ids_dict, read_new_teams=False) # only read team from internet if not saved

    projected_lines_dict = {}
    if len(raw_projected_lines) > 0:
        projected_lines_dict = generate_projected_lines_dict(raw_projected_lines, player_espn_ids_dict, player_teams, player_names)


    # read game logs
    read_all_seasons = False # saves time during testing other parts if we only read 1 season
    if 'read all seasons' in settings.keys():
        read_all_seasons = settings['read all seasons']
    all_player_season_logs_dict = reader.read_all_players_season_logs(player_names, read_all_seasons, player_espn_ids_dict)

    # find defensive rating/ranking by player position
    find_matchups = False
    if 'find matchups' in settings.keys():
        find_matchups = settings['find matchups']
    player_position = ''
    all_matchup_data = []
    player_positions = {}
    if find_matchups == True:
        # see if position saved in file
        # data_type = 'player positions'
        # player_positions_data = reader.extract_data(data_type, header=True)
        
        # for row in player_positions_data:
        #     print('row: ' + str(row))
        #     player_name = row[0]
        #     player_position = row[1]

        #     existing_player_positions_dict[player_name] = player_position
        # print('existing_player_positions_dict: ' + str(existing_player_positions_dict))


        player_positions = reader.read_all_players_positions(player_espn_ids_dict[player_name], season_year)
        

        # get matchup data before looping thru consistent streaks bc we will present matchup data alongside consistent streaks for comparison
        fantasy_pros_url = 'https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php' #'https://www.fantasypros.com/nba/defense-vs-position.php' #alt 2: betting_pros_url = 'https://www.bettingpros.com/nba/defense-vs-position/'
        hashtag_bball_url = 'https://hashtagbasketball.com/nba-defense-vs-position'
        swish_analytics_url = 'https://swishanalytics.com/optimus/nba/daily-fantasy-team-defensive-ranks-position'
        draft_edge_url = 'https://draftedge.com/nba-defense-vs-position/'


        # get matchup data for streaks to see if likely to continue streak
        matchup_data_sources = [fantasy_pros_url, hashtag_bball_url, swish_analytics_url] #, hashtag_bball_url, swish_analytics_url, betting_pros_url, draft_edge_url] # go thru each source so we can compare conflicts
        # first read all matchup data from internet and then loop through tables
        all_matchup_data = reader.read_all_matchup_data(matchup_data_sources) # all_matchup_data=[matchup_data1,..], where matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]


    # find teammates and opponents for each game played by each player
    find_players = False
    if 'find players' in settings.keys():
        find_players = settings['find players']
    # v1: all_players_in_games_dict = {year:{game key:{away team abbrev:[away players],home team abbrev:[home players]}}}
    # or
    # v2: all_players_in_games_dict = {player:{game:{teammates:[],opponents:[]}}}
    # start with v1 bc it is general for all games with no duplicates for players
    all_players_in_games_dict = {} 
    if find_players == True:
        all_players_in_games_dict = reader.read_all_players_in_games(all_player_season_logs_dict, player_teams) # go thru players in all_player_season_logs_dict to get game ids



    # === organize external data into internal structure
    all_player_consistent_stats = {} # we want to display all player consistent stats together for viewing convenience and analysis comparison
    all_player_stat_records = {}
    all_player_stat_dicts = {}
    for player_name in player_names:
        player_season_logs = all_player_season_logs_dict[player_name]

        # get player position and team from premade fcns 
        # bc if we do not have saved locally it will read from internet
        player_id = player_espn_ids_dict[player_name]

        # player_position = ''
        # if player_name in player_positions.keys():
        # player_position = player_positions[player_name] 
        player_position = reader.read_player_position(player_name, player_id, season_year, player_positions)

        # get player team so we can determine away/home team so we can determine teammatea/opponents from players in games
        player_team = reader.read_player_team(player_name, player_id, player_teams, read_new_teams=False) #player_teams[player_name]

        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, all_players_in_games_dict, player_team)

        player_all_outcomes_dict = generate_player_all_outcomes_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, player_position, all_matchup_data, all_players_in_games_dict, player_team, player_stat_dict) # each player has an outcome for each stat
        player_outcomes[player_name] = player_all_outcomes_dict

        # generate stat val reached at desired consistency
        # this would be one of the key possible outcomes given a probability
        # the initial outcome we have done so far is prob of reaching either the projected line or avg stat val
        # determine the stat val with record above 90%
        # player_consistent_stat_vals = {} same format as player stat records but with single max. consistent val for each stat for each condition
        player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
        player_consistent_stats = generate_consistent_stat_vals(player_name, player_stat_dict, player_stat_records)
        #player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
        all_player_consistent_stats[player_name] = player_consistent_stats
        all_player_stat_records[player_name] = player_stat_records
        all_player_stat_dicts[player_name] = player_stat_dict

    
    
    all_consistent_stat_dicts = generate_all_consistent_stat_dicts(all_player_consistent_stats, all_player_stat_records, all_player_stat_dicts)
    #writer.display_consistent_stats(all_player_consistent_stats, all_player_stat_records)
    desired_order = ['player name','stat name','ok val','ok val prob','ok val post prob', 'ok val min margin', 'ok val post min margin', 'ok val mean margin', 'ok val post mean margin']
    writer.list_dicts(all_consistent_stat_dicts, desired_order)


    # todo: make fcn to classify recently broken streaks bc that recent game may be anomaly and they may revert back to streak
    # todo: to fully predict current player stats, must predict teammate and opponent stats and prioritize and align with totals
    
    
    #print('player_outcomes: ' + str(player_outcomes))
    return player_outcomes


# we need to know how each player plays under certain conditions
# to propose likely outcomes
def generate_player_props(player):
    props = []

    # show regular season avgs
    # show player stats for each condition
    # allow user to choose condition by dropdown menu
    # see prop gen > player stats for output: https://docs.google.com/spreadsheets/d/1vpny0uo6xyYNbpHCBndQ2Tg_WIwbXtIMGcjnzvoyDrk/edit#gid=0
    # see espn for example: https://www.espn.com/nba/player/stats/_/id/3059318/joel-embiid
   

    return props

# we need to know how all players play under certain conditions
# to propose likely outcomes
def generate_players_props(players, settings={}):
    props = []

    for player in players:
        generate_player_props(player)

    return props