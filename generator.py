# generator.py
# generate data structures so we can reference info to make decisions
# and generate decisions based on data structures

import re
from datetime import datetime # convert date str to date so we can see if games 1 day apart and how many games apart

import determiner # determine regular season games, etc

import numpy as np # mean, median
from scipy import stats # calculate mode

import reader # read game log from file if needed
import writer # format record and other game data for readability

from tabulate import tabulate # display output

# we use isolator for strictly isolating parts of existing data when there is no processing or computation between input output
import sorter, isolator

import pandas as pd # read html results from webpage. need here to convert game log dict to df

from sympy import sympify, solve # only needed if system of eqns > 2

import math # using log10 to scale sample size relative to condition weight

import copy # need to compare init saved data to final data bc only overwrite saved data if changed

# sort alphabetical and lower for comparison to other games
# might as well compare strings bc need str as key
# players_list = [j. brown sg,...]
# p_string = j brown,...
# keep position in name bc more info and still sorts alphatebically?
# no bc we need it to exactly match other games where they played diff positions but same teammates, which is probably rare
def generate_players_string(players_list):
    print('\n===Generate Players String===\n')
    print('players_list: ' + str(players_list))

    players_list = sorted(players_list)

    p_string = ''

    for p_idx in range(len(players_list)):

        p = re.sub('\.|[A-Z]+$','',players_list[p_idx]).strip() # j. brown sg
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

# jaylen brown -> j brown
# trey murphy iii -> t murphy iii
# use to see if started or bench
# bc box score shows player abbrev
def generate_player_abbrev(player_name):
    print('\n===Generate Player Abbrev===\n')
    print('player_name: ' + str(player_name))
    #player_abbrev = ''

    player_names = player_name.split()
    player_abbrev = player_names[0][0]
    #last_name = ''
    for name in player_names[1:]:
        player_abbrev += ' ' + name
    #player_abbrev = player_initital + last_name

    print('player_abbrev: ' + player_abbrev)
    return player_abbrev

# each player has a stat dict for each stat so gen all of them for a given player
# run separately for each part of each season
def generate_player_all_stats_dicts(player_name, player_game_log, opponent, player_teams, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part):

    print('\n===Generate Player All Stats Dicts===\n')
    print('season_year: ' + str(season_year))
    #print('player_game_log:\n' + str(player_game_log))

    # use to see if started or bench
    # bc box score shows player abbrev
    player_abbrev = ''
    if season_year in all_players_in_games_dict.keys() and len(all_players_in_games_dict[season_year].keys()) > 0:
        player_abbrev = generate_player_abbrev(player_name)

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
        
        # determine player team for game at idx
        player_team_idx = 0
        # player_teams = {player:{year:{team:gp,...},...}}
        team_gp_dict = player_teams[player_name][season_year]
        # reverse team gp dict so same order as game idx recent to distant
        teams = list(reversed(team_gp_dict.keys()))
        games_played = list(reversed(team_gp_dict.values()))
        teams_games_played = int(games_played[player_team_idx])
        for game_idx, row in season_part_game_log.iterrows():

            print('\n===Game ' + str(game_idx) + '===')
            print('row: ' + str(row))

            print('teams_games_played: ' + str(teams_games_played))
            if int(game_idx) > teams_games_played: # > or >= make > bc we only need to go to next team if more games
                #if len(teams) > player_team_idx+1:
                player_team_idx += 1
                teams_games_played += games_played[player_team_idx]

            player_team = teams[player_team_idx]

            # get game type so we can add stat to reg or post season game
            # instead loop thru each part separately
            #game_type = player_game_log.loc[game_idx, 'Type']
            #print('game_type: ' + str(game_type))

            # make list to loop through so we can add all stats to dicts with 1 fcn
            game_stats = determiner.determine_game_stats(player_game_log, game_idx) #[pts,rebs,asts,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,bs,ss,fs,tos] 


            # === Add Stats to Dict ===

            # now that we have game stats add them to dict by condition

            # condition: all
            # values is list of dicts
            for stat_idx in range(len(all_stats_dicts.values())):
                stat_dict = list(all_stats_dicts.values())[stat_idx]
                stat = game_stats[stat_idx]
                stat_dict['all'][game_idx] = stat

            # todo: condition: tv coverage
            # bc some players play better or worse with more ppl watching more attention

            # condition: location
            # todo: condition: city. use 'team abbrev city'? some games are not in either city like international games
            # default can use 'team abbrev city' and then neutral games will have specific '<city>' and 'neutral' tags
            # classify all neutral games as well as international. some neutral tournament games but are there any neutral season games that are domestic? no it seems all neutral would be international except for in season tournament
            # could also avoid this extra condition unless neutral specific city
            # instead if default away/home game, combine opponent and loc conditions to get city so we only need extra condition if neutral
            
            # define away/home team so we can determine teammates/opponents in players in game
            # player team for this game
            #player_team = list(player_teams[player_name][season_year].keys())[-1]# current team
            away_abbrev = player_team

            game_opp_str = row['OPP'] #player_game_log.loc[game_idx, 'OPP']
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

                
            #print('away_abbrev: ' + away_abbrev)
            #print('home_abbrev: ' + home_abbrev)

            # matchup against opponent
            # only add key for current opp bc we dont need to see all opps here
            # look for irregular abbrevs like NO and NY
            # opponent in form 'gsw' but game log in form 'gs'
            # if we do not know the current opponent then show all opps
            #game_log_team_abbrev = re.sub('vs|@','',player_game_log.loc[game_idx, 'OPP'].lower()) # eg 'gs'
            game_log_team_abbrev = reader.read_team_abbrev(row['OPP'])#(player_game_log.loc[game_idx, 'OPP'])
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

                
            # condition: time before
            # condition: time after
            # see if this game is 1st or 2nd night of back to back bc we want to see if pattern for those conditions
            init_game_date_string = row['Date'].lower().split()[1] # 'wed 2/15'[1]='2/15'
            game_mth = init_game_date_string.split('/')[0]
            final_season_year = season_year
            if int(game_mth) > 9:
                final_season_year = str(int(season_year) - 1)
            game_date_string = init_game_date_string + "/" + final_season_year
            #print("game_date_string: " + str(game_date_string))
            game_date_obj = datetime.strptime(game_date_string, '%m/%d/%Y')
            #print("game_date_obj: " + str(game_date_obj))

            # if current loop is most recent game (idx 0) then today's game is the next game, if current season
            # if last game of prev season then next game after idx 0 (bc from recent to distant) is next season game 1
            if game_idx == '0': # see how many days after prev game is date of today's projected lines
                # already defined or passed todays_games_date_obj
                # todays_games_date_obj = datetime.strptime(todays_games_date, '%m/%d/%y')
                # print("todays_games_date_obj: " + str(todays_games_date_obj))
                current_year = datetime.today().year
                current_mth = datetime.today().month
                if int(current_mth) in range(10,13):
                    current_year += 1
                if season_year == current_year: # current year
                    # change to get from team schedule page
                    # instead of assuming they play today
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
            prev_game_idx = int(game_idx) + 1
            if len(player_game_log.index) > prev_game_idx:
                init_prev_game_date_string = player_game_log.loc[str(prev_game_idx), 'Date'].lower().split()[1]
            
                prev_game_mth = init_prev_game_date_string.split('/')[0]
                final_season_year = season_year
                if int(prev_game_mth) > 9:
                    final_season_year = str(int(season_year) - 1)
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

            

            

            # condition: day of week
            # add keys for each day of the week so we can see performance by day of week
            # only add key for current dow bc we dont need to see all dows here
            
            game_dow = row['Date'].lower().split()[0].lower() # 'wed 2/15'[0]='wed'
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


            # todo: # condition: day of week


            # condition: teammates out
            # condition: teammates in
            # condition: opponent team and players
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
            #print('game_key: ' + str(game_key))
            # if we do not have the game box score bc it does not exist yet then pass to the next game
            # the order we fill the stats dict depends on the order of games played bc we are going game by game
            if season_year in all_players_in_games_dict.keys() and len(all_players_in_games_dict[season_year].keys()) > 0:
                # if game key not in dict then we dont have info about it
                # but if we have dict but missing this game then it is error bc we already read all players in games
                if game_key in all_players_in_games_dict[season_year].keys():

                    game_players = all_players_in_games_dict[season_year][game_key] # {away:{starters:[],bench:[]},home:{starters:[],bench:[]}}
                    #print('game_players: ' + str(game_players))

                    # condition: game teammates
                    # {starters:[],bench:[]}
                    # also add game opps bc depends on actual opp players out as well
                    # get probs for games against individual players and get weighted avg for all players, to get more sample size
                    # as well as prob for only games with exact opp players but very small sample misleading
                    game_teammates = game_players['away']
                    if player_team == home_abbrev:
                        game_teammates = game_players['home']

                    # get full list of teammates this game without separating start and bench
                    # bc we loop thru all teammates to see who is in and out
                    game_teammates_list = []
                    for teammates in game_teammates.values():
                        for teammate in teammates:
                            game_teammates_list.append(teammate)

                    # we need players in alphabetical string to easily compare to other games
                    # might as well compare strings bc need str as key
                    game_teammates_str = generate_players_string(game_teammates_list)
                    # OR we could compare each player in list
                    # but then what would we use as key? names in order so first 5 are starters and remaining are bench
                    # order matters bc it is in order of position and therefore matchup 
                    # but it is also arbitrary so could mislead and reduce sample size
                    # ideally get both samples only in order by position and samples where order does not matter as long as the players played together
                    # first say order does not matter and then get where order matters
                    # bc we can get more samples which should improve accuracy
                    # still separate starters and bench
                    
                    # condition: starters
                    starters = game_teammates['starters']
                    # organize alphabetically regardless of position bc we can get more samples 
                    # where they played together but at different positions they still play like they play?
                    # get both but first favor sample size
                    starters_str = generate_players_string(starters)

                    # condition: bench
                    bench = game_teammates['bench']
                    bench_str = generate_players_string(bench)

                    # did current player start or come off bench?
                    # condition: player start or team unit/part (start/bench)
                    player_start = 'start'
                    if player_abbrev in bench_str:
                        player_start = 'bench'

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

                    # conditions related to players in games
                    # teammates and opps
                    # starters and bench
                    for stat_idx in range(len(all_stats_dicts.values())):
                        stat_dict = list(all_stats_dicts.values())[stat_idx]
                        stat = game_stats[stat_idx]

                        # condition: game teammates
                        if not game_teammates_str in stat_dict.keys():
                            stat_dict[game_teammates_str] = {}
                        stat_dict[game_teammates_str][game_idx] = stat

                        # condition: game starters
                        if not starters_str in stat_dict.keys():
                            stat_dict[starters_str] = {}
                        stat_dict[starters_str][game_idx] = stat

                        # condition: game bench
                        if not bench_str in stat_dict.keys():
                            stat_dict[bench_str] = {}
                        stat_dict[bench_str][game_idx] = stat

                        # condition: player start
                        if not player_start in stat_dict.keys():
                            stat_dict[player_start] = {}
                        stat_dict[player_start][game_idx] = stat

                        # condition: teammate
                        for teammate in game_teammates_list:
                            if not teammate in stat_dict.keys():
                                stat_dict[teammate] = {}
                            stat_dict[teammate][game_idx] = stat

                        # condition: teammate out
                        for teammate in all_teammates[season_year]:
                            if teammate not in game_teammates_list: # teammate out
                                teammate_out_key = teammate + ' out'

                                if not teammate_out_key in stat_dict.keys():
                                    stat_dict[teammate_out_key] = {}
                                stat_dict[teammate_out_key][game_idx] = stat

                    #print("stat_dict: " + str(stat_dict))


                    # condition: teammate
                    # for each player/teammate in game, make a new record or add to existing record
                    # {starters:[],bench:[]}
                    # for teammates in game_teammates.values():
                    #     #print('teammate: ' + teammate)
                    #     for teammate in teammates:
                    # for teammate in game_teammates_list:
                    #     for stat_idx in range(len(all_stats_dicts.values())):
                    #         stat_dict = list(all_stats_dicts.values())[stat_idx]
                    #         stat = game_stats[stat_idx]
                    #         if not teammate in stat_dict.keys():
                    #             stat_dict[teammate] = {}
                    #         stat_dict[teammate][game_idx] = stat
                        #print("stat_dict: " + str(stat_dict))


                    # condition: teammate out
                    # for each teammate out of game (dnp inactive injured), make a new record or add to existing record
                    # we need to know all possible teammates, which we get above, once per player
                    # in all_teammates, we only want teammates this season bc if all seasons then misleading data
                    # for teammate in all_teammates:
                    #     if teammate not in game_teammates_list: # teammate out
                    #         teammate_out_key = teammate + ' out'
                    #         for stat_idx in range(len(all_stats_dicts.values())):
                    #             stat_dict = list(all_stats_dicts.values())[stat_idx]
                    #             stat = game_stats[stat_idx]

                    #             if not teammate_out_key in stat_dict.keys():
                    #                 stat_dict[teammate_out_key] = {}
                    #             stat_dict[teammate_out_key][game_idx] = stat
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
            game_num = total_season_games - int(game_idx) # bc going from recent to past
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

    # all_stats_dicts: {'pts': {'all': {0: 18, 1: 19...
    #print('all_stats_dicts: ' + str(all_stats_dicts))
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
# need current_year_str to get filename for cur yr bc season yr not always cur yr
# do not need to pass in season_year and minus 1 per loop bc looping thru season logs
def generate_player_stat_dict(player_name, player_season_logs, todays_games_date_obj, all_players_in_games_dict={}, player_teams={}, current_year_str='', todays_date=datetime.today().strftime('%m-%d-%y'), game_teams=[], projected_lines_dict={}, init_player_stat_dict={}):

    print('\n===Generate Player Stat Dict: ' + player_name.title() + '===\n')
    #print('===' + player_team.upper() + '===\n')

    player_stat_dict = {}

    # keep in mind, when we add a new feature such as a new condition to the stat dict,
    # then we must manually erase old saved stat dict OR make setting to overwrite it
    # or else we would need to read from internet every time anyway which defeats the purpose of storing locally
    # init_player_stat_dict
    # better to get cur yr here bc also used to divide before writing, although could just take first item in dict as cur yr
    # need filenames to write every time and read only if not already passed init dicts
    if current_year_str == '':
        current_year_str = determiner.determine_current_season_year()
    player_cur_stat_dict_filename = 'data/stat dicts/' + player_name + ' ' + current_year_str + ' stat dict ' + todays_date + '.json'
    # print('player_cur_stat_dict_filename: ' + cur_file)
    # print('Try to find local CURRENT season stat dict for ' + player_name + '.')
    # init_player_cur_stat_dict = reader.read_json(player_cur_stat_dict_filename)

    player_prev_stat_dicts_filename = 'data/stat dicts/' + player_name + ' prev stat dicts.json'
    # print('player_prev_stat_dicts_filename: ' + prev_file)
    # print('Try to find local PREVIOUS seasons stat dicts for ' + player_name + '.')
    # init_player_prev_stat_dicts = reader.read_json(player_prev_stat_dicts_filename)
    if len(init_player_stat_dict.keys()) == 0:
        # #files = [player_cur_stat_dict_filename, player_prev_stat_dicts_filename]
        # cur_file = player_cur_stat_dict_filename
        # prev_file = player_prev_stat_dicts_filename
        init_player_stat_dict = reader.read_cur_and_prev_json(player_cur_stat_dict_filename,player_prev_stat_dicts_filename) #reader.read_json_multiple_files(files)

    player_stat_dict = copy.deepcopy(init_player_stat_dict)


    # for each teammate out of game (dnp inactive injured), make a new record or add to existing record
    # we need to know all possible teammates
    # which we can get from roster
    # https://www.espn.com/nba/team/roster/_/name/bos/boston-celtics
    # or we could get from box scores we already saved locally
    # in all_teammates, we only want teammates per season bc if all seasons then misleading data
    # all_teammates = {yr:[teammate,...],...}
    # teammates for all yrs not equal to roster bc not everyone on roster played in game
    # but would it be good enough to have more players than we need and then if didnt play then will discard
    # rather than going through all box scores just to get teammates?
    # it is needed for old teams where rosters not available easily?
    # BUT even those rosters might be easy to get online
    all_teammates = reader.read_all_teammates(player_name, all_players_in_games_dict, player_teams, player_season_logs)


    # get current opponent if available so we can focus on current conditions
    # if we do not know current opponent then show for all opps
    # for prev seasons we want to get stats for all conditions 
    # BUT cur seasons we only need cur condition bc updating each day
    # the code is st if stat dict is saved at all then it will not read new stats
    # so if already ran once today then will need to manually delete if want new features added
    # OLD version used projected lines to get opp but
    # NEW version uses all games today matchups and player team to get opp
    # opponent = ''
    # print('projected_lines_dict: ' + str(projected_lines_dict))
    # if player_name in projected_lines_dict.keys():
    #     player_projected_lines_dict = projected_lines_dict[player_name]
    #     print(player_name + ' projected_lines_dict: ' + str(player_projected_lines_dict))
    #     # for each player we loop thru we add their avgs to projected line if none given
    #     # we want to get projected lines for all conditions, including opponent
    #     if 'opp' in player_projected_lines_dict:
    #         opponent = player_projected_lines_dict['opp'].lower() # collect data against opponent to see previous matchups
    #     else:
    #         print('Warning: opp not in projected lines for ' + player_name)


    opponent = determiner.determine_opponent_team(player_name, player_teams, game_teams)


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

    for season_year, player_game_log in player_season_logs.items():

        # need string to compare to json
        #season_yr_str = str(season_year)
        print("\n===Year " + season_year + "===\n")

        player_game_log_df = pd.DataFrame(player_game_log)#.from_dict(player_game_log) #pd.DataFrame(player_game_log)
        player_game_log_df.index = player_game_log_df.index.map(str)
        #print('converted_player_game_log_df:\n' + str(player_game_log_df))

        
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        # for each part of season, reg and post:
        # first get stats for reg season
        # season_part = 'regular'
        
        # gen all stats dicts for this part of this season
        # here we convert season year key to string?
        # cur season stat dict gets replaced each day bc file has date in name
        # so do we need to save cur season box scores which make up cur stat dict?
        # OR can we add new entries to existing cur stat dict?
        # if we add new entries instead of overwriting, 
        # then it would require read from internet each run?
        # the condition is if season year in stat dict and it is missing games
        # but we would only know if missing games bc we read from internet
        # the rule seems to be if the data changes,
        # then we must name the file based on how often we want to update it
        # in this case the date is in the file so we know if we ran it before/after last change
        # could we save the box score stat dicts separately if we are already planning on saving box scores?
        # we can subtract number we have saved from number of games in log read from internet
        # so we know how many new box scores since last run
        # must then search for prev saved file
        # is it easier to keep prev day cur season files so we can see difference between cur day
        # OR keep cur season box scores local so we can reconstruct cur season stat dict from local box scores 
        # and only read newest box score from internet
        # seems easier to save cur seas box scores

        # for now if season yr already in stat dict then no need to read again
        # but what if new features like find players turned from false to true? then we would need to get stat dict each time and check difference before saving new?
        # see determine_need_box_score to see how we can still update
        # if stat dict exists but missing key
        # print('is season_year string? ' + season_year) # yes, but how??? it is input as int. nooo it is the key in the season logs not the init param so fix
        # if len(player_stat_dict.keys()) > 0:
        #     print('is stat dict key string? ' + list(player_stat_dict.keys())[0]) # yes
        if determiner.determine_need_stat_dict(player_stat_dict, season_year):
        #if season_year not in player_stat_dict.keys() and season_yr_str not in player_stat_dict.keys(): # if determine_team_player_key_in_stat_dict() team_players_key not in player_stat_dict[season_year].keys():
            player_stat_dict[season_year] = {}
        
            # only need to get new stat dict if different than saved data
            season_parts = ['regular','postseason','full']
            for season_part in season_parts:
                player_stat_dict[season_year][season_part] = generate_player_all_stats_dicts(player_name, player_game_log_df, opponent, player_teams, season_year, todays_games_date_obj, all_players_in_games_dict, all_teammates, all_seasons_stats_dicts, season_part) #generate_full_season_stat_dict(player_stat_dict)


        #season_year -= 1

        #print('player_stat_dict: ' + str(player_stat_dict))

    writer.write_cur_and_prev(init_player_stat_dict, player_stat_dict, player_cur_stat_dict_filename, player_prev_stat_dicts_filename, current_year_str, player_name)

    # player_stat_dict: {'2023': {'regular': {'pts': {'all': {0: 18, 1: 19...
    #print('player_stat_dict: ' + str(player_stat_dict))
    return player_stat_dict

# we use all_players_stats_dicts = {player name:{stat name:{}}}
# to reference stats 
# all_player_season_logs_dict = {player name:{year:{condition:{stat:[]}}}}
# projected_lines_dict = {player name:{stat:value,..,loc:val,opp:val}}
# use projected lines input param to get opponent
# use today game date to get day and break conditions
def generate_all_players_stats_dicts(all_player_season_logs_dict, projected_lines_dict, todays_games_date_obj, season_year=2024):
    print('\n===Generate All Players Stats Dicts===\n')
    all_players_stats_dicts = {}

    for player_name, player_season_logs in all_player_season_logs_dict.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, season_year=season_year)
        all_players_stats_dicts[player_name] = player_stat_dict


    print('all_players_stats_dicts: ' + str(all_players_stats_dicts))
    return all_players_stats_dicts

# we are looking for the stat val reached at least 90% of games
# so from 0 to max stat val, get record reached games over total games
# player_stat_records = []
# no need to make dict because stat val = idx bc going from 0 to N
#player_stat_records: {'all': {2023: {'regular': {'pts': 
def generate_player_stat_records(player_name, player_stat_dict):
    print('\n===Generate Player Stat Record' + player_name.title() + '===\n')

    player_stat_records = {}

    # first show reg season, then post, then combined

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_full_season_stat_dict in player_stat_dict.items():
        #print("\n===Year " + str(season_year) + "===\n")

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            #print("\n===Season Part " + str(season_part) + "===\n")

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

                    #print("\n===Condition " + str(condition) + "===\n")

                    # reset for each condition
                    stat_names = ['pts','reb','ast','3pm']

                    # for each stat type/name (eg pts, reb, etc)
                    # loop from 0 to max stat val to get record over stat val for period of all games
                    for stat_name in stat_names:

                        #print("\n===Stat name " + str(stat_name) + "===\n")

                        # reset for each stat name/type
                        all_games_reached = [] # all_stat_counts = []
                        all_probs_stat_reached = []

                        stat_vals = list(player_season_stat_dict[stat_name][condition].values())
                        #print('stat_vals: ' + str(stat_vals))
                        num_games_played = len(stat_vals)
                        #print('num games played ' + condition + ': ' + str(num_games_played))
                        if num_games_played > 0:
                            # max(stat_vals)+1 bc we want to include 0 and max stat val
                            # for 0 we need to compute prob of exactly 0 not over under
                            for stat_val in range(0,max(stat_vals)+1):
                                # if stat_val == 0:
                                #     num_games_hit
                                num_games_reached = 0 # num games >= stat val, stat count, reset for each check stat val bc new count
                                # loop through games to get count stat val >= game stat val
                                for game_idx in range(num_games_played):
                                    game_stat_val = stat_vals[game_idx]
                                    if int(stat_val) == 0:
                                        if game_stat_val == int(stat_val):
                                            num_games_reached += 1
                                    else:
                                        if game_stat_val >= int(stat_val):
                                            num_games_reached += 1

                                    all_games_reached.append(num_games_reached) # one count for each game

                                #print('num_games_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(num_games_reached)) 
                                

                                prob_stat_reached = str(num_games_reached) + '/' + str(num_games_played)
                                #print('prob_stat_reached ' + str(stat_val) + ' ' + stat_name + ' for ' + condition + ' games: ' + str(prob_stat_reached)) 

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
    # print('player_stat_records: ' + str(player_stat_records))
    return player_stat_records








# at this point we should have projected_lines_dict either by external source or player averages
# the record we are generating is a measure of determining consistency but there may be better ways
# current_year needed to determine avg line if no projected line given
def generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts={}, season_year=2024):

    print('\n===Generate Player Records Dict===\n')
    print('===' + player_name.title() + '===\n')

    player_records_dicts = {}

    # we only want to compare stats to current year avg if no lines given
    # bc that is closer to actual lines
    current_year = season_year

    print('projected_lines_dict: ' + str(projected_lines_dict))
    season_part_of_interest = 'regular' # reg or post season
    # if we do not have projected lines then we can use player means/medians as lines
    # we pass in projected lines as param so at this point we already have actual projected lines or averages to determine record above and below line
    # we could get avgs from stats but we already compute avgs so we can get it from that source before running this fcn
    player_projected_lines = {}
    if player_name in projected_lines_dict.keys():
        player_all_projected_lines = projected_lines_dict[player_name]
        
        if season_part_of_interest not in player_all_projected_lines.keys():
            print('Warning: Player did not play in one part of the season (either reg or post?)!' + season_part_of_interest)
            # did not play in one part of season but played in other so use for both
            if season_part_of_interest == 'regular':
                season_part_of_interest = 'postseason'
            else: # = post so change to reg
                season_part_of_interest = 'regular'
        
        if season_part_of_interest in player_all_projected_lines.keys():
            player_projected_lines = player_all_projected_lines[season_part_of_interest]
        else:
            print('Warning: Player did not play in either part of season!')
            
    else: # no lines given, so use avgs
        print('Warning: Player ' + player_name + ' not in projected lines!')
        #print('player_medians_dicts: ' + str(player_medians_dicts))
        if len(player_medians_dicts.keys()) > 0:
            if season_year in player_medians_dicts['all'].keys():
                season_median_dicts = player_medians_dicts['all'][season_year]
                #print('season_median_dicts: ' + str(season_median_dicts))
                projected_lines_dict[player_name] = season_median_dicts

                player_avg_lines = season_median_dicts
                #print('player_avg_lines: ' + str(player_avg_lines))

                stats_of_interest = ['pts','reb','ast','3pm','blk','stl','to'] # we decided to focus on these stats to begin
                #season_part_of_interest = 'regular' # reg or post season
                for stat in stats_of_interest:
                    if season_part_of_interest in player_avg_lines.keys():
                        player_projected_lines[stat] = player_avg_lines[season_part_of_interest][stat]
                    else:
                        print('Warning: Player did not play in one part of the season (either reg or post?)!' + season_part_of_interest)
                        # did not play in one part of season but played in other so use for both
                        if season_part_of_interest == 'regular':
                            season_part_of_interest = 'postseason'
                        else: # = post so change to reg
                            season_part_of_interest = 'regular'

                        player_projected_lines[stat] = player_avg_lines[season_part_of_interest][stat]
            
            #print('player_projected_lines: ' + str(player_projected_lines))
        else: # player has not played before
            print('Warning: Player ' + player_name + ' has no stats to average!')

    print('player_projected_lines: ' + str(player_projected_lines))

    #season_year = 2023

    # player_season_stat_dict = { stat name: .. }
    for season_year, player_full_season_stat_dict in player_stat_dict.items():

        print("\n===Year " + str(season_year) + "===\n")
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        #if season_year in player_medians_dicts['all'].keys():
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

                        if 'pts' in player_projected_lines.keys():
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
                    if 'pts' in player_projected_lines.keys():
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

    # player_records_dicts: {'all': {2023: {'regular': {'pts': ['0/1',...
    print('player_records_dicts: ' + str(player_records_dicts))
    return player_records_dicts

# all players stats dicts = { player: year: stat name: condition: game idx: stat val }
def generate_all_players_records_dicts(all_players_stats_dicts, projected_lines_dict, season_year=2024):
    print('\n===Generate All Players Records Dicts===\n')
    all_records_dicts = {}

    # player_stat_dict = { year: .. }
    for player_name, player_stat_dict in all_players_stats_dicts.items():
    #for player_idx in range(len(all_player_game_logs)):

        player_records_dict = generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, season_year=season_year)
        all_records_dicts[player_name] = player_records_dict

                
    print('all_records_dicts: ' + str(all_records_dicts))
    return all_records_dicts


def generate_player_avg_range_dict(player_name, player_stat_dict, key):

    #print('\n===Generate Player ' + player_name.title() + ' Average Range Dict: ' + key.title() + '===\n')

    player_avg_range_dict = {}

    #print('\n===' + player_name.title() + '===\n')

    #season_year = 2023

    #print('player_stat_dict: ' + str(player_stat_dict))
    for season_year, player_full_season_stat_dict in player_stat_dict.items():

        #print("\n===Year " + str(season_year) + "===\n")
        #print('player_full_season_stat_dict: ' + str(player_full_season_stat_dict))
        #player_game_log = player_season_logs[0] #start with current season. all_player_game_logs[player_idx]
        #player_name = player_names[player_idx] # player names must be aligned with player game logs

        for season_part, player_season_stat_dict in player_full_season_stat_dict.items():

            #print("\n===Season Part " + str(season_part) + "===\n")
            #print('player_season_stat_dict: ' + str(player_season_stat_dict))

            all_pts_dicts = player_season_stat_dict['pts']
            if len(all_pts_dicts['all'].keys()) > 0:
                # no matter how we get data, 
                # next we compute relevant results

                # first for all then for subsets like home/away
                # all_pts_dict = { 'all':[] }
                # all_pts_means_dict = { 'all':0, 'home':0, 'away':0 }

                # at this point we have added all keys to dict eg all_pts_dict = {'1of2':[],'2of2':[]}
                #print("all_pts_dict: " + str(all_pts_dict))
                #print("all_pts_dicts: " + str(all_pts_dicts))
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
                                stat_avg_range = round(np.mean(np.array(stat_vals)), 1)
                            elif key == 'median':
                                stat_avg_range = int(np.median(np.array(stat_vals)))
                            elif key == 'mode':
                                stat_avg_range = stats.mode(stat_vals, keepdims=False)[0]
                            elif key == 'min':
                                stat_avg_range = np.min(np.array(stat_vals))
                            elif key == 'max':
                                stat_avg_range = np.max(np.array(stat_vals))
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

    # player_avg_range_dict: {'all': {2023: {'regular': {'pts': 33, 'reb': 1...
    #print('player_avg_range_dict: ' + str(player_avg_range_dict))
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
    #print('all_avgs_dicts: ' + str(all_avgs_dicts))
    return all_avgs_dicts

# if player names is blank, use all players found in raw projected lines
# use player_espn_ids_dict to get teams
def generate_projected_lines_dict(raw_projected_lines, player_espn_ids_dict={}, player_teams={}, player_names=[], read_new_teams=False, cur_yr=''):
    #print('\n===Generate Projected Lines Dict===\n')
    #print('raw_projected_lines: ' + str(raw_projected_lines))
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
        player_teams = reader.read_all_players_teams(player_espn_ids_dict, read_new_teams) # only read team from internet if not saved

    # convert raw projected lines to projected lines
    projected_lines = reader.read_projected_lines(raw_projected_lines, player_teams, cur_yr=cur_yr)

    projected_lines_dict = {}
    header_row = projected_lines[0]
    for player_lines in projected_lines[1:]:
        player_name = player_lines[0].lower()
        projected_lines_dict[player_name] = dict(zip(header_row[1:],player_lines[1:]))
    
    #print("projected_lines_dict: " + str(projected_lines_dict))
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
# all_player_season_logs_dict = {player name:{year:{condition:{stat:[]}}}}
# player_season_logs = {}
def generate_player_all_outcomes_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, player_position='', all_matchup_data=[], all_players_in_games_dict={}, player_team='', player_stat_dict={}, season_year=2024):

    print('\n===Generate Player Outcome===\n')

    print('===' + player_name.title() + '===')
    print('===' + player_team.upper() + '===\n')

    player_all_outcomes_dict = {} # {stat name:{outcome,record,avg,range,matchup}}

    # organize external data into internal structure
    if len(player_stat_dict.keys()) == 0: # use given stat dict if available, else get from logs
        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, all_players_in_games_dict, player_team, season_year=season_year)

    


    player_all_avg_range_dicts = {'mean':{},'median':{},'mode':{},'min':{},'max':{}}
    for key in player_all_avg_range_dicts.keys():
        player_all_avg_range_dicts[key] = generate_player_avg_range_dict(player_name, player_stat_dict, key)
    #player_avg_range_dict = generate_player_all_avg_range_dicts(player_name, player_stat_dict)
    #print('player_all_avg_range_dicts: ' + str(player_all_avg_range_dicts))
    player_means_dicts = player_all_avg_range_dicts['mean']
    player_medians_dicts = player_all_avg_range_dicts['median']
    player_modes_dicts = player_all_avg_range_dicts['mode']
    player_mins_dicts = player_all_avg_range_dicts['min']
    player_maxes_dicts = player_all_avg_range_dicts['max']

    # determine the record over projected line or avg stat val
    #print('projected_lines_dict before records: ' + str(projected_lines_dict))
    player_records_dict = generate_player_records_dict(player_name, player_stat_dict, projected_lines_dict, player_medians_dicts, season_year=season_year)


    # determine the stat val with record above 90%
    # player_consistent_stat_vals = {} same format as player stat records but with single max. consistent val for each stat for each condition
    #player_consistent_stat_vals = generate_consistent_stat_vals(player_name, player_stat_dict)
    #player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
    #writer.display_consistent_stats(all_player_consistent_stats)

    # if we have a game log for this player, 
    # get prev game to compute time_after condition
    time_after = '0 after' # could be '0' or '' bc init for case of new player with no log
    #current_season_log = pd.DataFrame() # init current season log as df
    if len(player_season_logs.values()) > 0:
        current_season_log = pd.DataFrame(player_season_logs[str(season_year)])
        current_season_log.index = current_season_log.index.map(str)
    
        #season_year = 2023
        prev_game_date_obj = determiner.determine_prev_game_date(current_season_log, season_year) # exclude all star and other special games
        # prev_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] + "/" + season_year # eg 'wed 2/15' to '2/15/23'
        # prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%y')
        days_after_prev_game = (todays_games_date_obj - prev_game_date_obj).days

        time_after = str(days_after_prev_game) + ' after'
    else:
        print('Warning: player ' + player_name.title() + ' has not played before!')


    player_lines = {}
    loc_of_interest = '' # if we want to see both locations we know only home/away
    opponent = '' # if we want to see all opponents we need all opp keys to follow unique format or list of all possible opponents to find keys
    if player_name in projected_lines_dict.keys():
        #print('projected_lines_dict: ' + str(projected_lines_dict))
        player_lines['regular'] = projected_lines_dict[player_name]
        reg_player_lines = player_lines['regular']
        if 'loc' in reg_player_lines.keys():
            loc_of_interest = reg_player_lines['loc'].lower()
        if 'opp' in reg_player_lines.keys():
            opponent = reg_player_lines['opp'].lower()
    #print('player_lines: ' + str(player_lines))

    
    current_dow = todays_games_date_obj.strftime('%a').lower()

    current_teammates_str = '' # if we are given current teamates of interest then we can focus on these, else show all


    all_matchups_dicts = {} # store all matchup data (avg and rank) for each opponent/team


    # make an outcome for each stat
    #print('player_stat_dict: ' + str(player_stat_dict))
    stats_of_interest = ['pts','reb','ast','3pm'] # this is if we have all the lines available but we only want subset. but if some of the lines are unavailable then print out their outcomes using their median as the line but only if they are a stat of interest
    #year = 2023
    for season_part, season_part_lines in player_lines.items():

        print('\n===Season Part: ' + season_part + '===\n')
        #print('season_part_lines: ' + str(season_part_lines))

        for stat_name in stats_of_interest:
            player_outcome_dict = {} # fields: 'outcome', 'streak', 'record', 'avg', 'range', 'matchup'

            if season_part not in season_part_lines.keys():
                if season_part == 'regular':
                    season_part = 'postseason'
                else:
                    season_part = 'regular'

            stat_line = season_part_lines[season_part][stat_name]
            player_outcome = player_name.title() + ' ' + str(stat_line) + '+ ' + stat_name # initially express over/under as over+ with assumption that under=100-over bc we are displaying possibility before assessing probability
            print('player_outcome: ' + player_outcome)
            player_outcome_dict['outcome'] = player_outcome

            overall_record = ''
            if season_part in player_records_dict['all'][season_year].keys():
                overall_record = player_records_dict['all'][season_year][season_part][stat_name] # { 'player name': { 'all': {year: { pts: '1/1,2/2..', stat: record, .. },...}, 'home':{year:{ stat: record, .. },.. }, 'away':{year:{ stat: record, .. }} } }
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
                if season_part in player_records_dict[location][season_year].keys():
                    location_record = player_records_dict[location][season_year][season_part][stat_name]
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
                if season_part in player_records_dict[opponent][season_year].keys():
                    opp_record = player_records_dict[opponent][season_year][season_part][stat_name]
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

                if season_year in player_records_dict[time_after].keys() and season_part in player_records_dict[time_after][season_year].keys():
                    time_after_record = player_records_dict[time_after][season_year][season_part][stat_name]
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
                if season_year in player_records_dict[current_dow].keys() and season_part in player_records_dict[current_dow][season_year].keys():
                    dow_record = player_records_dict[current_dow][season_year][season_part][stat_name]
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
            #print('all_matchup_data: ' + str(all_matchup_data))
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
                #print('current_matchup_data: ' + str(current_matchup_data))
                for pos, sources_results in current_matchup_data.items():
                    #print("Position: " + pos.upper())

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
                #print("matchup_dict: " + str(matchup_dict))
                # matchup_dict = { pg: { s1: 0, s2: 0, .. }, sg: { s1: 0 }, .. }
                for pos, rank_dict in matchup_dict.items():
                    s1_matchup_rank = rank_dict['s1']
                    s2_matchup_rank = rank_dict['s2']
                    s3_matchup_rank = rank_dict['s3']
                    # init dicts
                    #print("all_matchups_dicts: " + str(all_matchups_dicts))

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
                        #print("all_matchups_dicts: " + str(all_matchups_dicts))
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
                            #print("all_matchups_dicts: " + str(all_matchups_dicts))
                        else: # stat_name is in pos matchups so check if opp in stats
                            print('stat_name ' + stat_name + ' in position matchups dict')
                            if not opponent in all_matchups_dicts[pos][stat_name].keys():
                                print('opponent ' + opponent + ' not in stat so it is new opponent')

                                # rank_avgs = determiner.determine_rank_avgs(pos, matchup_dict)
                                # matchup_rank_mean = rank_avgs['mean']
                                # matchup_rank_combined_mean = rank_avgs['combined mean']

                                all_matchups_dicts[pos][stat_name][opponent] = { 's1': s1_matchup_rank, 's2': s2_matchup_rank, 's3': s3_matchup_rank, 'mean': matchup_rank_mean, 'combined mean': matchup_rank_combined_mean }
                                #print("all_matchups_dicts: " + str(all_matchups_dicts))
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

                #print("all_matchups_dicts: " + str(all_matchups_dicts))



                # add matchups in prediction, for position
                # currently pre_dict from valid streaks but eventually will be narrowed down further into valid preidctions=streaks+matchups+avg+range etc
                print('\n===Add Matchups to Outcome===\n')
                print('We got matchups so add matchups to outcome. ') # should we do this for each player or even each condition or can we do this 1 big loop after we populate all matchups dict?
                #print("all_matchups_dicts: " + str(all_matchups_dicts))
                #print("projected_lines_dict: " + str(projected_lines_dict))


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
            #print('all_players_in_games_dict: ' + str(all_players_in_games_dict))
            if len(all_players_in_games_dict.keys()) > 0:

                print("\n===Find Players in Games for Outcome===\n")

                if len(current_teammates_str) > 0:
                    # use given list of current teammates of interest
                    print('current_teammates_str: ' + str(current_teammates_str))

                    generate_player_outcome_data(current_teammates_str, season_year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dict) # assigns data to outcome dictionary
                    
                else: # show all teammates bc we do not know current teammates

                    for condition in player_records_dict.keys():

                        if re.search('\.',condition): # eg 'j. brown sg', condition matching list of teammates has player first initial with dot after

                            generate_player_outcome_data(condition, season_year, stat_name, player_outcome_dict, player_records_dict, player_means_dicts, player_medians_dicts, player_modes_dicts, player_mins_dicts, player_maxes_dicts, player_stat_dict)



            if season_part not in player_all_outcomes_dict.keys():
                player_all_outcomes_dict[season_part] = {}
            player_all_outcomes_dict[season_part][stat_name] = player_outcome_dict

    #print('player_all_outcomes_dict: ' + str(player_all_outcomes_dict))
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
    #print('stat_vals: ' + str(stat_vals))

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
    #print('stat_vals: ' + str(stat_vals))

    mean_val = 0 # init
    if len(stat_vals) > 0:
        mean_val = round(np.mean(np.array(stat_vals)), 1)
    else:
        print('Warning: No stat vals while generating min margin!')

    mean_margin = mean_val - init_val

    print('mean_margin: ' + str(mean_margin))
    return mean_margin


def generate_margin(init_val, stat_dict, margin_type='min'):
    #print('\n===Generate ' + margin_type.title() + ' Margin for val: ' + str(init_val) + '===\n')
    #print('stat_dict: ' + str(stat_dict))

    #min_margin = 0

    stat_vals = list(stat_dict.values())
    #print('stat_vals: ' + str(stat_vals))

    val = 0 # init
    margin = 0
    if len(stat_vals) > 0:
        if margin_type == 'mean':
            val = np.mean(np.array(stat_vals))
            #print('val: ' + str(val))
            # we want to round to whole number for easy comparison and we cannot be certain with any more accuracy due to other conditions
            margin = round(val - init_val) 
        else:
            val = min(stat_vals)
            margin = val - init_val
        
    else:
        print('Warning: No stat vals while generating min margin!')

    

    #print('margin: ' + str(margin))
    return margin


# record input is prob stat reached as fraction
# output is prob 0-1
# record = x/y = num_games_reached / num_games_played
def generate_prob_stat_reached(record):

    #print('\n===Generate Prob Stat Reached===\n')

    #print('record: ' + str(record))

    # if we have no record for a given stat val we will pass record=''
    # bc prob=0
    prob_stat_reached = 0

    if record != '':

        # record = x/y = num_games_reached / num_games_played
        record_data = record.split('/')
        num_games_reached = record_data[0]
        num_games_played = record_data[1]
        #prob_stat_reached = round((float(num_games_reached) / float(num_games_played)) * 100)
        prob_stat_reached = round(float(num_games_reached) / float(num_games_played), 2)
        
    #print('prob_stat_reached: ' + str(prob_stat_reached))
    return prob_stat_reached

# from 0 to n gen prob over and under stat val
# first overall and then for conditions
# stat_val_probs = {}
#player_stat_records: {'all': {2023: {'regular': {'pts': 
# generate_stat_val_probs
# old: player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
# player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': prob over
def generate_player_stat_probs(player_stat_records, player_name=''):
    print('\n===Generate Player Stat Probs: ' + player_name.title() + '===\n')

    player_stat_probs = {}

    for condition, condition_stat_records in player_stat_records.items():
        #print("\n===Condition " + str(condition) + "===\n")

        player_stat_probs[condition] = {}

        for season_year, full_season_stat_dicts in condition_stat_records.items():
            #print("\n===Year " + str(season_year) + "===\n")

            player_stat_probs[condition][season_year] = {}

            for season_part, season_stat_dicts in full_season_stat_dicts.items():
                #print("\n===Season Part " + str(season_part) + "===\n")

                player_stat_probs[condition][season_year][season_part] = {}

                for stat_name, stat_records in season_stat_dicts.items():
                   # print("\n===Stat Name " + str(stat_name) + "===\n")
                    #print('stat_records: ' + str(stat_records))

                    #player_stat_probs[condition][season_year][season_part][stat_name] = {}
                    #stat_probs = player_stat_probs[condition][season_year][season_part][stat_name]
                    stat_probs = {}

                    # get prob from 0 to 1 to compare to desired consistency
                    #stat_val = 0
                    prob_over = 1.0
                    prob_under = 1.0
                    
                    for stat_val in range(len(stat_records)):
                        #print("\n===Stat Val " + str(stat_val) + "===")
                        # gen prob reached from string record
                        record = stat_records[stat_val] # eg x/y=1/1
                        #print('record: ' + str(record))

                        # adjust stat val proprtional to minutes currently playing
                        # but we want both orig and adjusted to compare
                        # so need parallel dict adjusted stat probs
                        # it could have current yr but it would be the same as orig 
                        #per_min_prob = generate_per_min_prob(stat_val, stat_dict)

                        # call prob over keys 
                        # 'raw prob' and 'per min prob'
                        prob_over = generate_prob_stat_reached(record)

                        #prob_under = round(1 - prob_over,2)

                        # prob under for a stat val is over 1-prob ober so only need to save prob over
                        stat_probs[stat_val] = prob_over #{ 'prob over': prob_over, 'prob under': prob_under }
                        #print('stat_probs: ' + str(stat_probs))

                    # when we want to see all stats on same page aligned by value we will have to add 0s and 100s to blank cells
                    # but that would require knowing the stat keys which you can get from the first val bc everyone has at least 0

                    player_stat_probs[condition][season_year][season_part][stat_name] = stat_probs

    # player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': prob over
    #print('player_stat_probs: ' + str(player_stat_probs))
    return player_stat_probs

# generate dict of sample sizes for each condition
# so we know weight of sample based on size
# although we also want a way to get sample size for conditions decided later
# such as like combined conditions when multiple conditions line up
# could also use determine sample size 
# by passing player stat records with matching conditions
def generate_sample_size_dict(player_stat_records, player_name=''):

    print('\n===Generate Sample Size Dict ' + player_name.title() + '===\n')

    ss_dict = {}

    return ss_dict


# consistency=0.9 is desired probability of player reaching stat val
#consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
#player_stat_records: {'all': {2023: {'regular': {'pts': 
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
                    #print('stat_records: ' + str(stat_records))

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
    #print('consistent_stat_vals: ' + str(consistent_stat_vals))
    return consistent_stat_vals


# all_player_consistent_stats = {} same format as stat records, 
# condition, year, stat name
# for display
# simply flatten bottom level of dict
# by adding its key to header of level above
def generate_all_consistent_stat_dicts(all_player_consistent_stats, all_player_stat_records, all_player_stat_dicts, player_teams={}, season_year=2024):
    print("\n===Generate All Consistent Stats Dicts===\n")
    print('all_player_consistent_stats: ' + str(all_player_consistent_stats))
    #print('all_player_stat_records: ' + str(all_player_stat_records))

    player_consistent_stat_data_headers = ['Player', 'S Name', 'Stat', 'Prob', '2nd Stat', '2nd Prob', 'PS', 'PP', '2nd PS', '2nd PP', 'OK Val', 'OK P', 'OK PP']
    final_consistent_stats = [player_consistent_stat_data_headers] # player name, stat name, consistent stat, consistent stat prob

    # so we can sort from high to low prob
    all_consistent_stat_dicts = [] 
    consistent_stat_dict = {}

    # {player:stat:condition:val,prob,margin...}
    # where condition could be year, part or sub-condition like location
    all_consistent_stats_dict = {} # organize by stat, more flexible than old version list
    # for each player
    # for each stat
    # get consistent stat data for
    # year
    # part
    # condition

    # populate consistent_stat_dict and append to all_consistent_stat_dicts
    # all_consistent_stat_dicts: [{'player name': 'lamelo ball', 'stat name': 'pts', 'prob val': 15, 'prob': 94, ...}, {'player name': 'lamelo ball', 'stat name': 'reb', 'prob val': 2...}]
    # all_player_consistent_stats, consistent_stat_vals: {'all': {2023: {'regular': {'pts': {'prob val':
    years_of_interest = [season_year, season_year-1]
    for player_name, player_consistent_stats in all_player_consistent_stats.items():
        print('\n===' + player_name.title() + '===\n')

        all_consistent_stats_dict[player_name] = {}

        player_team = ''
        if player_name in player_teams.keys():
            player_team = player_teams[player_name]

        # for now, show only conditon=all
        # give option to set condition and sort by condition
        conditions_of_interest = ['all']
        for condition, condition_consistent_stats in player_consistent_stats.items():
            print('\n===' + condition.title() + '===\n')

            if condition in conditions_of_interest:

                

                
                for year, year_consistent_stats in condition_consistent_stats.items():
                    print('\n===' + str(year) + '===\n')

                    if year in years_of_interest:

                        # for season_part, season_part_consistent_stats in year_consistent_stats.items():
                        #     print(season_part)

                        #     player_season_consistent_stat_data = []

                        # first look at full season, then postseason
                        # consistent_stat_dict will need another level for the year or season part
                        # so we can loop thru in order
                        # or we can change order of input dict
                        season_part_consistent_stats = year_consistent_stats['full'] # old version manually set season parts but now we just loop thru all season parts
                        part_consistent_stat_dict = {}
                        for season_part, season_part_consistent_stats in year_consistent_stats.items():
                            print('\n===season_part: ' + season_part + '===\n')

                            part_consistent_stat_dict[season_part] = {}

                            for stat_name in season_part_consistent_stats.keys():
                                print('\n===' + stat_name.upper() + '===\n')

                                

                                # use consistent_stat_dict to sort
                                #consistent_stat_dict = {'player name':player_name, 'stat name':stat_name, 'team':player_team}
                                
                                # fields of interest
                                prob_stat_key = 'prob val' #defined in loop
                                prob_key = 'prob'
                                min_margin_key = 'min margin'
                                mean_margin_key = 'mean margin'

                                second_prob_stat_key = 'second ' + prob_stat_key
                                second_prob_key = 'second ' + prob_key
                                second_min_margin_key = 'second ' + min_margin_key
                                second_mean_margin_key = 'second ' + mean_margin_key

                                #player_consistent_stat_data = [player_name, stat_name]

                                # player name, stat name, consistent stat, consistent stat prob
                                #consistent_stat_dict['team'] = player_team already defined when init dict

                                player_consistent_stat_data = [player_name, stat_name]#, full_consistent_stat, full_consistent_stat_prob, full_second_consistent_stat, full_second_consistent_stat_prob, post_consistent_stat, post_consistent_stat_prob, post_second_consistent_stat, post_second_consistent_stat_prob, player_team]

                                # simply flatten bottom level of dict
                                # by adding its key to header of level above
                                # eg in this case blank for full season and post for postseason
                                #season_parts = ['full','regular','postseason']

                                # for season_part in season_parts:
                                #     print('season_part: ' + season_part)

                                #if season_part in year_consistent_stats.keys():

                                season_part_key = re.sub('ular|season','',season_part) # full, reg, or post
                                # make full blank to save space and differentiate from reg and post?
                                # make sure to strip blank space at start of string
                                # or add space in other part of string for season parts
                                # if season_part == 'full':
                                #     season_part_key = ''
                                # elif season_part == 'regular':
                                #     season_part_key = 'reg'
                                

                                #if season_part == 'full':

                                prob_stat_dict = year_consistent_stats[season_part][stat_name]
                                print('prob_stat_dict: ' + str(prob_stat_dict))

                                prob_val = prob_stat_dict[prob_stat_key]
                                consistent_stat = prob_val
                                
                                prob = prob_stat_dict[prob_key]
                                #print('prob: ' + str(prob))
                                consistent_stat_prob = round(prob * 100)
                                #print('consistent_stat_prob: ' + str(consistent_stat_prob))

                                second_consistent_stat = prob_stat_dict[second_prob_stat_key]
                                second_consistent_stat_prob = round(prob_stat_dict[second_prob_key] * 100)

                                min_margin = prob_stat_dict[min_margin_key]
                                second_min_margin = prob_stat_dict[second_min_margin_key]
                                mean_margin = round(prob_stat_dict[mean_margin_key])
                                second_mean_margin = round(prob_stat_dict[second_mean_margin_key])

                                # set keys for each field for each part of season and for each season
                                part_prob_stat_key = season_part_key + ' ' + prob_stat_key
                                part_prob_key = season_part_key + ' ' + prob_key
                                part_second_prob_stat_key = season_part_key + ' ' + second_prob_stat_key
                                part_second_prob_key = season_part_key + ' ' + second_prob_key

                                part_min_margin_key = season_part_key + ' ' + min_margin_key
                                part_second_min_margin_key = season_part_key + ' ' + second_min_margin_key
                                part_mean_margin_key = season_part_key + ' ' + mean_margin_key
                                part_second_mean_margin_key = season_part_key + ' ' + second_mean_margin_key
                                
                                consistent_stat_dict[part_prob_stat_key] = consistent_stat
                                consistent_stat_dict[part_prob_key] = consistent_stat_prob
                                consistent_stat_dict[part_second_prob_stat_key] = second_consistent_stat
                                consistent_stat_dict[part_second_prob_key] = second_consistent_stat_prob

                                consistent_stat_dict[part_min_margin_key] = min_margin
                                consistent_stat_dict[part_second_min_margin_key] = second_min_margin
                                consistent_stat_dict[part_mean_margin_key] = mean_margin
                                consistent_stat_dict[part_second_mean_margin_key] = second_mean_margin

                                


                                season_part_prob_data = [consistent_stat, consistent_stat_prob, second_consistent_stat, second_consistent_stat_prob]
                                player_consistent_stat_data.extend(season_part_prob_data)

                                # add postseason stat probs separately
                                # elif season_part == 'postseason': incorporated into loop

                                
                                # now that we looped thru all parts of season we can see which is available for ok val
                                ok_val_key = 'ok val'
                                #ok_val_season_prob_key = ok_val_key + ' prob ' + str(year)

                                # add another column to classify if postseason stat < regseason stat so we can group those together

                                # player name, stat name, consistent stat, consistent stat prob
                                #player_consistent_stat_data = [player_name, stat_name, full_consistent_stat, full_consistent_stat_prob, full_second_consistent_stat, full_second_consistent_stat_prob, post_consistent_stat, post_consistent_stat_prob, post_second_consistent_stat, post_second_consistent_stat_prob, player_team]
                                #consistent_stat_dict = {'player name':player_name, 'stat name':stat_name, 'prob val': full_consistent_stat, 'prob': full_consistent_stat_prob, 'second prob val':full_second_consistent_stat, 'second prob':full_second_consistent_stat_prob}

                                #player_season_consistent_stat_data = player_season_consistent_stat_data + player_consistent_stat_data

                                final_consistent_stats.append(player_consistent_stat_data)
                                # need to save all parts of season for each stat
                                # this is how we save as many fields/columns we want in a single row
                                part_consistent_stat_dict[season_part][stat_name] = consistent_stat_dict

                                if stat_name not in all_consistent_stats_dict[player_name]:
                                    all_consistent_stats_dict[player_name][stat_name] = {}
                                if condition not in all_consistent_stats_dict[player_name][stat_name].keys():
                                    all_consistent_stats_dict[player_name][stat_name][condition] = {}
                                if year not in all_consistent_stats_dict[player_name][stat_name][condition].keys():
                                    all_consistent_stats_dict[player_name][stat_name][condition][year] = {}

                                all_consistent_stats_dict[player_name][stat_name][condition][year][season_part] = consistent_stat_dict
                            
                            print('part_consistent_stat_dict: ' + str(part_consistent_stat_dict))

                            # consistent_stat_dict will have for 1 stat but all parts of season
                            # so change to dict
                            # or arrange input in another var

                            #all_consistent_stat_dicts.append(consistent_stat_dict)

                            #all_consistent_stats_dict
                            
    # all_consistent_stat_dicts: [{'player name': 'cole anthony', 'stat name': 'pts', 'team': 'orl', 'full prob val': 6,
    # all_consistent_stat_dicts: [{'player name': 'skylar mays', 'stat name': 'pts', 'team': 'por', 'reg prob val': 9,
    # all_consistent_stat_dicts: [{'player name': 'lamelo ball', 'stat name': 'pts', 'prob val': 15, 'prob': 94, ...}, {'player name': 'lamelo ball', 'stat name': 'reb', 'prob val': 2...}]
    #print('all_consistent_stat_dicts: ' + str(all_consistent_stat_dicts))

    print('all_consistent_stats_dict: ' + str(all_consistent_stats_dict))

    # form all_consistent_stat_dicts

    for player_name, player_consistent_stat_dict in all_consistent_stats_dict.items():
        player_team = ''
        if player_name in player_teams.keys():
            player_team = player_teams[player_name]
        for stat_name, stat_consistent_stat_dict in player_consistent_stat_dict.items():
            consistent_stat_dict = {'player': player_name, 'team': player_team, 'stat': stat_name}
            for condition, condition_consistent_stat_dict in stat_consistent_stat_dict.items():
                for year, year_consistent_stat_dict in condition_consistent_stat_dict.items():
                    for part, part_consistent_stat_dict in year_consistent_stat_dict.items():
                        for key, val in part_consistent_stat_dict.items():
                            consistent_stat_dict[key] = val

            all_consistent_stat_dicts.append(consistent_stat_dict) # for each stat

    print('all_consistent_stat_dicts: ' + str(all_consistent_stat_dicts))

    # determine which keys in dict to sort dicts by
    # we duplicate the corresponding vals in known keys for ref called 'ok val'
    # which stats do we need to see?
    # true prob accounts for condition of which part of season
    # ok val means that it accounts for all conditions 
    # and gets adjusted extrapolated vals by weighing conditional probs
    # the point of sorting these keys is to see most important columns together for comparison
    # for the actual stat value available, which is not always the same as the first consistent val
    ok_val_key = 'ok val'
    # formula for cumulative weighted avg probability
    ok_val_true_prob_key = ok_val_key + ' prob' # account for all conditions to get true prob
    # true seasons prob accounts for all seasons and sample sizes
    # each season is like a different condition given a different weight based on recency and sample size
    ok_val_true_season_prob_key = ok_val_key + ' true season prob' # account for all seasons to get true season prob
    # we already have measured prob of stat in part of season
    # so now we want true prob in part of season, with all other conditions equal
    # for each season, we want to see ok val prob, margin, dev, and other stat measures
    # we also want to see average over last x seasons
    # we do not need true prob for part of season separate 
    # bc true prob already accounts for season part condition
    # we want runnning prob and measures for each part of each season
    # first and foremost show this year and then compare to prev seasons and true count
    # this table will show vector of weighted features that equate true prob
    # other data about each part of each season will go in separate tables unless they are directly used to calc true prob
    # so first this season, last season, and prev seasons. then conditions for each part of each season
    # we need to determine the number of seasons to display ok val
    # based on seasons in all_player_consistent_stats
    # but if we are already looping through all_player_consistent_stats earlier why not perform this fcn then?
    # bc it requires fully populated all_consistent_stat_dicts bc it compares different numbers to get ok val?
    #for season_year in 
    # ok_val_prob_key becomes ok_val_season_prob_key to specify season
    ok_val_season_prob_key = ok_val_key + ' prob ' + str(season_year)

    ok_val_part_prob_key = ok_val_key + ' post prob' # depends which part of season we are in, to choose which should be secondary prob condition
    ok_val_min_margin_key = ok_val_key + ' min margin'
    ok_val_part_min_margin_key = ok_val_key + ' post min margin'
    ok_val_mean_margin_key = ok_val_key + ' mean margin'
    ok_val_part_mean_margin_key = ok_val_key + ' post mean margin'

    # sort_key1 = ok_val_true_prob_key #'ok val prob' # default
    # sort_key2 = 'ok val post prob' # default
    # sort_key3 = 'ok val min margin' # default
    # sort_key4 = 'ok val post min margin' # default
    # sort_key5 = 'ok val mean margin' # default
    # sort_key6 = 'ok val post mean margin' # default
    

    # check if regseason or full season stat is available
    ok_stat_vals = [2,5,8,10,12,15,18,20] #standard for dk
    #year_of_interest = 2023
    #regseason_stats = consistent_stat_vals['all'][year_of_interest]['regular']
    # all_consistent_stat_dicts: [{'player name': 'lamelo ball', 'stat name': 'pts', 'prob val 2023': 15, 'prob 2023': 94, ...}, {'player name': 'lamelo ball', 'stat name': 'reb', 'prob val': 2...}]
    for stat_dict in all_consistent_stat_dicts:
        #print('stat_dict: ' + str(stat_dict))

        # consider changing back to reg season stat
        # prefer full season bc more samples
        # but some misleading bc playoffs may differ from regseasons stats significantly
        season_part_key = 'full'
        part_prob_stat_key = season_part_key + ' ' + prob_stat_key
        part_prob_key = season_part_key + ' ' + prob_key
        part_second_prob_stat_key = season_part_key + ' ' + second_prob_stat_key
        part_second_prob_key = season_part_key + ' ' + second_prob_key

        part_min_margin_key = season_part_key + ' ' + min_margin_key
        part_second_min_margin_key = season_part_key + ' ' + second_min_margin_key
        part_mean_margin_key = season_part_key + ' ' + mean_margin_key
        part_second_mean_margin_key = season_part_key + ' ' + second_mean_margin_key

        reg_season_stat_val = stat_dict[part_prob_stat_key] #'full prob val'
        if reg_season_stat_val in ok_stat_vals: #is available (ie in ok stat vals list)
            ok_stat_val = reg_season_stat_val
            ok_stat_prob = stat_dict[part_prob_key]
        reg_season_second_stat_val = stat_dict[part_second_prob_stat_key]
        reg_season_stat_prob = stat_dict[part_prob_key]
        reg_season_second_stat_prob = stat_dict[part_second_prob_key]

        reg_season_min_margin = stat_dict[part_min_margin_key]
        reg_season_second_min_margin = stat_dict[part_second_min_margin_key]
        reg_season_mean_margin = stat_dict[part_mean_margin_key]
        reg_season_second_mean_margin = stat_dict[part_second_mean_margin_key]

        player_stat_records = all_player_stat_records[stat_dict['player']]

        stat_name = stat_dict['stat']
        #year = 2023
        # change to get season part by current date if after playoff schedule start?
        # no bc here we are processing postseason separately
        # we would like to get consistent postseason stat but small sample size?
        season_part = 'postseason' # if we are in posteason, do we also want to see postseason prob of regseason stat???
        condition = 'all'
        # player_stat_dict: {2023: {'postseason': {'pts': {'all': {0: 18, 1: 19,...
        player_stat_dict = all_player_stat_dicts[stat_dict['player']][season_year][season_part][stat_name][condition]

        

        #post_season_stat_val = stat_dict['post prob val']
        #post_season_stat_prob = stat_dict['post prob']

        # we have primitive check if ok val is available and if not then we use next nearest number even if it is not available?
        # next nearest should be available bc they rarely jump multiple steps at once
        # even if not available then we will likely not consider less than consistent stat val
        # but it is very useful to see not only consistent stat but next stat consistency to determine margin of error and deviation
        if reg_season_stat_val in ok_stat_vals: #is available (ie in ok stat vals list)
            #ok_val_key = 'ok val ' + str(season_year)
            stat_dict[ok_val_key] = reg_season_stat_val # default, ok=available

            stat_dict[ok_val_true_prob_key] = reg_season_stat_prob 
            # determine which key has the same stat val in post as reg, bc we earlier made sure there would be one
            # can be generalized to fcn called determine matching key
            stat_dict[ok_val_part_prob_key] = determiner.determine_ok_val_prob(stat_dict, stat_dict[ok_val_key], player_stat_records, season_part, stat_name, season_year=season_year) #post_season_stat_prob 
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

            stat_dict[ok_val_min_margin_key] = reg_season_min_margin
            stat_dict[ok_val_part_min_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'min')

            stat_dict[ok_val_mean_margin_key] = reg_season_mean_margin
            stat_dict[ok_val_part_mean_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'mean')
            

        # if default reg season stat na,
        # first check next lowest val, called second val
        else:
            stat_dict[ok_val_key] = reg_season_second_stat_val # ok=available

            stat_dict[ok_val_true_prob_key] = reg_season_second_stat_prob 
            stat_dict[ok_val_part_prob_key] = determiner.determine_ok_val_prob(stat_dict, stat_dict[ok_val_key], player_stat_records, season_part, stat_name, season_year=season_year) #post_season_stat_prob 
            
            stat_dict[ok_val_min_margin_key] = reg_season_second_min_margin
            stat_dict[ok_val_part_min_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'min')

            stat_dict[ok_val_mean_margin_key] = reg_season_second_mean_margin
            stat_dict[ok_val_part_mean_margin_key] = determiner.determine_ok_val_margin(stat_dict, stat_dict[ok_val_key], player_stat_dict, stat_name, 'mean')

    # determine final available stat val out of possible consistent stat vals
    # eg if horford reb in playoffs higher than regseason, use regseason stat val's prob in postseason
    # bc that will show highest prob
    #available_stat_val


    sort_keys = [ok_val_true_prob_key, ok_val_part_prob_key, ok_val_min_margin_key, ok_val_part_min_margin_key, ok_val_mean_margin_key, ok_val_part_mean_margin_key]
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

# stat_dict: {'player name': 'Trevelin Queen', 'stat name': 'ast', 'prob val': 0, 'prob': 100...
def generate_available_prop_dicts(stat_dicts, game_teams=[], player_teams={}, cur_yr=''):
    print('\n===Generate Available Prop Dicts===\n')
    available_prop_dicts = []
    maybe_available_props = []

    # for efficiency first get all diff teams
    # and then read each team page once and save local
    # teams = []
    # for stat_dict in stat_dicts:
    #     teams.append(stat_dict['team'])
    # teams = list(set(teams))
    # print('teams: ' + str(teams))

    # we know we will need odds for each team so read each team page at least once per day
    # actually to save odds in a local var we need to sort by team in a duplicate array
    #teams_stat_dicts = sorter.sort_dicts_by_key(stat_dicts, 'team')
    # and we need to isolate into separate loops
    # so we can read page once and use for all teammates
    #all_players_odds: {'mia': {'pts': {'Bam Adebayo': {'18': '−650','20': '+500',...
    all_players_odds = reader.read_all_players_odds(game_teams, player_teams, cur_yr=cur_yr) # {team: stat: { player: odds,... }}

    #for team in teams:
        #all_players_odds = reader.read_all_stat_odds(stat_dict, all_players_odds)

    # for each proposition dict, add odds val
    # if no odds val, then do not add to available dict
    for stat_dict in stat_dicts:
        #print('stat_dict: ' + str(stat_dict))
        # see if stat available
        # could do same check for all and put 0 if na 
        # and then sort by val/odds or elim 0s

        # add val to dict
        odds = 'NA'
        team = stat_dict['team']
        if team in all_players_odds.keys():
            stat_name = stat_dict['stat']
            print('stat_name: ' + stat_name)
            if stat_name in all_players_odds[team].keys():
                player = stat_dict['player'].lower()
                print('player: ' + player)
                #print('player_dict: ' + str(all_players_odds[team][stat_name]))
                if player in all_players_odds[team][stat_name].keys():
                    ok_val = str(stat_dict['val'])
                    print('ok_val: ' + str(ok_val))
                    if str(ok_val) in all_players_odds[team][stat_name][player].keys():
                    
                        odds = all_players_odds[team][stat_name][player][ok_val] #reader.read_stat_odds(stat_dict, all_players_odds)
            else:
                print('Warning: stat name not in all_players_odds: ' + stat_name)
        else:
            print('Warning: team not in all_players_odds: ' + team)
        #     else:
        #         odds = 'NA'
        # else:
        #     odds = 'NA'

        print('odds: ' + odds)

        # +100 means 1 unit in to profit 1 unit
        stat_dict['odds'] = odds # format +100 = 1 spent/1 earned

        # now we have odds return profit/loss
        # so get ev = e(x) = xp
        #+200=200/100=2, -200=100/200=1/2
        ev = 0 # if no odds
        if odds != 'NA' and odds != '?':
            conv_factor = 100 # american odds system shows how much to put in to profit 100
            profit_multipier = int(odds) / conv_factor
            if re.search('-',odds):
                profit_multipier = conv_factor / -int(odds)
            print('profit_multipier: ' + str(profit_multipier))
            true_prob = stat_dict['true prob']
            print('true_prob: ' + str(true_prob))
            prob_over = true_prob / 100
            print('prob_over: ' + str(prob_over))
            prob_under = 1 - prob_over
            print('prob_under: ' + str(prob_under))
            spent = 1 # unit
            ev = "%.2f" % (profit_multipier * prob_over - spent * prob_under)
            print('ev: ' + str(ev))

        stat_dict['ev'] = ev
        
        # if team odds saved locally then no need to read again from internet same day bc unchanged?
        # no bc they change frequently, especially near game time bc more ppl active

        # if team not in all_players_odds.keys():
        #     all_players_odds[team] = {}
        # if stat_name not in all_players_odds[team].keys():
        #     all_players_odds[team][stat_name] = {}
        # all_players_odds[team][stat_name][player] = odds
        # print('all_players_odds: ' + str(all_players_odds))

        #if determiner.determine_stat_available(stat_dict):
        # if we do not see player in list of odds then they might be available later so put ?
        # if we see odds for different higher val then NA
        # if we see odds for lower value then put >P? bc their minutes are probably down but if not then good value
        if stat_dict['odds'] != 'NA':
            if str(stat_dict['odds']) == '?':
                maybe_available_props.append(stat_dict)

            elif len(stat_dict['odds']) > 0:
                if abs(int(stat_dict['odds'])) > 0:
                    available_prop_dicts.append(stat_dict)

            else:
                print('Warning: odds returned invalid value!')
        
    available_prop_dicts = available_prop_dicts + maybe_available_props

    print('available_prop_dicts: ' + str(available_prop_dicts))
    return available_prop_dicts

# all_stat_probs_dict = {player:stat:val:conditions:prob}
# like gen stat probs by stat used in writer
# need player_stat_dict to get sample size
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
def generate_all_stat_probs_dict(all_player_stat_probs, all_player_stat_dicts={}, all_unit_stat_probs={}, season_years=[], irreg_play_time={}):
    print('\n===Generate All Stat Probs Dict===\n')

    all_stat_probs_dict = {}

    # determine unit time period by observing if drastic change indicates change in team or role
    # default to avg current season but enable manual entry of minutes if irregular such as for teammate injured
    #irreg_play_time = {'craig porter': 25}
    # get years from all_player_stat_probs so we know how many seasons of interest
    # years = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())
    # print('years: ' + str(years))
    unit_time_period = determiner.determine_unit_time_period(all_player_stat_probs, all_player_stat_dicts, season_years, irreg_play_time)

    # rearrange all_player_stat_probs into all_stat_probs_dict
    for player, player_stat_probs in all_player_stat_probs.items():
        stat_probs_by_stat = {} # this must be in player loop or it will show max val for all players when we only need max for current players here bc separate sheets. this would be outside loop for all players when we want all players in same sheet
        #print('player: ' + str(player))
        player_unit_stat_probs = {}
        if len(all_unit_stat_probs.keys()) > 0:
            player_unit_stat_probs = all_unit_stat_probs[player]

        all_conditions = []
        for condition, condition_stat_probs in player_stat_probs.items():
            #print('condition: ' + str(condition))
            for year, year_stat_probs in condition_stat_probs.items():
                #print('year: ' + str(year))
                for part, part_stat_probs in year_stat_probs.items():
                    #print('part: ' + str(part))
                    
                    conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
                    all_conditions.append(conditions)
                    
                    for stat, stat_probs in part_stat_probs.items():
                        
                        for val, prob in stat_probs.items():
                            
                            if stat not in stat_probs_by_stat.keys():
                                stat_probs_by_stat[stat] = {}
                                stat_probs_by_stat[stat][val] = {}
                            elif val not in stat_probs_by_stat[stat].keys():
                                stat_probs_by_stat[stat][val] = {}

                            stat_probs_by_stat[stat][val][conditions] = prob # {'prob':prob}

                            # dont add per unit stats for time period used as unit
                            # eg avg current season minutes to get unit
                            # determine unit time period by observing if drastic change indicates change in team or role
                            # default to avg current season but enable manual entry of minutes if irregular such as for teammate injured
                            if len(player_unit_stat_probs.keys()) > 0:
                                if year != unit_time_period:
                                    prob_per_unit = player_unit_stat_probs[condition][year][part][stat][val]
                                    conditions_per_unit = conditions + ' per unit'
                                    stat_probs_by_stat[stat][val][conditions_per_unit] = prob_per_unit
                            
                            # add true prob for each val based on conditional probs
                            # need to know all players conditions first
                            # and could even include all players and similar players especially in consideration of projection
        
        all_stat_probs_dict[player] = stat_probs_by_stat
    
    # all_stat_probs_dict = {player:stat:val:conditions:prob}
    #print('all_stat_probs_dict: ' + str(all_stat_probs_dict))

    # repeat for per minute stat probs


    # get years from all_player_stat_probs so we know how many seasons of interest
    # years = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())
    # print('years: ' + str(years))
    # cur_yr = years[0]

    # # before we get true prob we must know per unit probs

    # # gen true probs for all stat probs dict
    # # we get true prob for combos of conditions by weighting avg prob
    # # start with overall true prob combining 2 seasons weighted by recency and sample size
    # # relevance for a time period is shown in recency factor
    # # need to know current conditions to get true prob
    # # see how current conds were used for streak tables
    
    # for player, player_probs_dict in all_stat_probs_dict.items():
    #     print('\nplayer: ' + str(player))
    #     player_stat_dict = all_player_stat_dicts[player]
    #     #print('player_stat_dict: ' + str(player_stat_dict))
    #     for stat, stat_probs_dict in player_probs_dict.items():
    #         print('\nstat: ' + str(stat))
    #         # first get overall probs for all reg seasons
    #         condition = 'all' # all conds match all
    #         part = 'regular' # get current part from time of year mth
    #         # player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
    #         prev_val = player_stat_dict[cur_yr][part][stat][condition]['0']
    #         #print('prev_val: ' + str(prev_val))
            
    #         for val, val_probs_dict in stat_probs_dict.items():
    #             print('\nval: ' + str(val))
    #             #print('val_probs_dict: ' + str(val_probs_dict))

    #             # get prev game stat vals from most recent game log in stat dict
    #             # and add keys to all_stat_prob_dicts
    #             # technically prev game stat vals affects stat prob so include in all stat probs dict
    #             #all_stat_prob_dicts = generate_all_prev_game_stat_vals
                
    #             val_probs_dict['prev val'] = prev_val


    #             # p_true = w1p1 + w2p2
    #             # where w1+w2=1
    #             # and w_t=w1/t so w2=w1/2
    #             # for each year or condition, add prob to list
    #             # how do we know all years of interest?
    #             # can we get from info already passed?
    #             # yes from val 0 bc it is evaled for all conditions?
    #             # the user already passed seasons of interest so we can use that
    #             # how do we decide probs of interest? from curr conds
    #             # always include overall season probs
    #             # if a val not reached in a condition then it will not be included here
    #             probs = []
    #             all_current_conditions = [] 
    #             all_cur_cond_dicts = []
                
    #             for year in years:
    #                 cur_cond_dict = {'condition':condition, 'year':year, 'part':part}
    #                 current_conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
    #                 #print('current_conditions: ' + str(current_conditions))
    #                 if current_conditions in val_probs_dict.keys():
    #                     probs.append(val_probs_dict[current_conditions])
    #                     all_current_conditions.append(current_conditions)
    #                     all_cur_cond_dicts.append(cur_cond_dict)
    #             # then get probs matching current conds
    #             print('probs: ' + str(probs))
    #             print('all_cur_cond_dicts: ' + str(all_cur_cond_dicts))
    #             # current_conditions = 'all 2024 regular prob'
    #             # if current_conditions not in val_probs_dict.keys():
    #             #     current_conditions = 'all 2024 full prob'
    #             # probs = [val_probs_dict[current_conditions]]
    #             # current_conditions = 'all 2023 regular prob'
    #             # if current_conditions not in val_probs_dict.keys():
    #             #     current_conditions = 'all 2023 full prob'
    #             # probs.append(val_probs_dict[current_conditions])
    #             # determine weights of each measured prob based on recency, relevance, and sample size
    #             num_probs = 2 # all probs must add up to 1
    #             init_weight = 0.0
    #             prev_weight = 0.0
    #             # could loop thru N times to build eq str
    #             # then convert str to eq and solve for w_1
    #             # probs = [p1,p2,...]
    #             str_eqn = 'w' # = 0
    #             t_1 = 1 # set bc current year is origin so multiply by 1. each year adds 1 as weight decreases. that weight should be determined by ml algo
                
    #             # to get sample size for current conds
    #             # list current conds
    #             # s1 is always all <current yr> <current part>
    #             # or just first year given
    #             # cur_conds = {year:year, part:part, cond:cond}
    #             # some vals will only be reached in one part of the season
    #             if len(all_cur_cond_dicts) > 0:
    #                 #cur_conds = all_cur_cond_dicts[0]
    #                 #s_1 = determiner.determine_sample_size(player_stat_dict, cur_conds) #15 # current year
    #                 # get sample sizes for probs
    #                 # instead of sample size use variance and confidence bc more accurate scaling for relevance of dataset
    #                 sample_sizes = []
    #                 for p_idx in range(len(probs)):
    #                     cur_conds = all_cur_cond_dicts[p_idx]
    #                     s_n = determiner.determine_sample_size(player_stat_dict, cur_conds)
    #                     sample_sizes.append(s_n)
    #                 print('sample_sizes: ' + str(sample_sizes))

    #                 s_1 = sample_sizes[0]
                    
    #                 # probs must be aligned with cur conds
    #                 for p_idx in range(1,len(probs)):
    #                     # if prob=0 then w will cancel

    #                     # w_n = w_1 ( t_1 / t_n ) ( s_n / s_1 ) # bc years inverse and sample size prportional
    #                     # read year in condition and see how many years away?
    #                     t_n = p_idx + 1 # years away
    #                     cur_conds = all_cur_cond_dicts[p_idx]
    #                     s_n = sample_sizes[p_idx] #determiner.determine_sample_size(player_stat_dict, cur_conds) #65 #previous years
    #                     w_n = ' + w * ' + str(t_1) + ' / ' + str(t_n) + ' * ( ' + str(s_n) + ' / ' + str(s_1) + ' )'
    #                     str_eqn += w_n
    #             #     recency = 0.5
    #             #     sample_size = 10
    #             #     weight = 
    #             #     weighted_prob = weight * prob
    #             #     true_prob += weighted_prob

    #             #     prev_weight = weight

    #                 # final weight is 1 - other weights to get remainder to ensure adds up to 1 but should not be needed if rounded properly
                
    #             str_eqn += ' - 1'
    #             print('str_eqn: ' + str_eqn)
    #             eqn = sympify(str_eqn)
    #             w_1 = round(solve(eqn)[0], 6)
    #             weights = [round(w_1,2)]
    #             for p_idx in range(1,len(probs)):
    #                 t_n = p_idx + 1 # years away
    #                 s_n = sample_sizes[p_idx] #65 #previous years
    #                 w_n = round(w_1 * round(t_1 / t_n, 6) * round(s_n / s_1, 6), 2)
    #                 weights.append(w_n)
    #             print('weights: ' + str(weights))

    #             # solve for other ws in relation to w_1 already used to sub above
    #             true_prob = 0#w_1 * p_1
    #             for p_idx in range(len(probs)):
    #                 prob = probs[p_idx]
    #                 #print('prob: ' + str(prob))
    #                 w = weights[p_idx]
    #                 #print('w: ' + str(w))
    #                 wp = round(w * prob, 6)
    #                 #print('wp: ' + str(wp))
    #                 true_prob += wp
    #                 #print('true_prob: ' + str(true_prob))
    #             true_prob = round(true_prob,2)
    #             print('true_prob: ' + str(true_prob))
                
    #             #true_prob = val_probs_dict[current_conditions]
    #             val_probs_dict['true prob'] = true_prob

    

    #print('all_stat_probs_dict: ' + str(all_stat_probs_dict))
    return all_stat_probs_dict

# flatten nested dicts into one level and list them
# from all_stat_probs_dict: {'luka doncic': {'pts': {1: {'all 2023 regular prob': 1.0, 'all 2023 full prob': 1.0,...
# all_stat_prob_dicts = [{player:player, stat:stat, val:val, conditions prob:prob,...},...]
# need all_player_stat_dicts to get prev val
def generate_all_stat_prob_dicts(all_stat_probs_dict, player_teams={}, all_current_conditions={}, all_player_stat_dicts={}, season_years=[], game_teams=[]):

    print('\n===Generate All Stat Prob Dicts===\n')

    all_stat_prob_dicts = []

    # we need to get all conditions for all players
    # so table lines up if players did not all play in same conditions
    all_conditions = determiner.determine_all_conditions(all_stat_probs_dict)

    cur_yr = str(season_years[0])

    for player, player_stat_probs_dict in all_stat_probs_dict.items():
        #print('\n===Player: ' + str(player) + '===\n')
        #stat_val_probs_dict = {'player': player}
        player_team = list(player_teams[player][cur_yr].keys())[-1] # current team
        # if player in player_teams.keys():
        #     player_team = player_teams[player]
        #stat_val_probs_dict['team'] = player_team

        # add game num for ref so we can sort by game to ensure at least 2 picks per game 
        # OR if only 1 allowed still need to see game teams next to each other to place picks on same page of gui
        game_num = determiner.determine_game_num(game_teams, player_team)


        player_current_conditions = all_current_conditions[player]
        #print('player_current_conditions: ' + str(player_current_conditions))

        player_stat_dict = all_player_stat_dicts[player]
        #print('player_stat_dict: ' + str(player_stat_dict))
        
        for stat_name, stat_probs_dict in player_stat_probs_dict.items():
            #print('\n===Stat: ' + str(stat_name) + '===\n')
            #stat_val_probs_dict['stat'] = stat_name
            #consistent_stat_dict = {'player': player_name, 'team': player_team, 'stat': stat_name}
            # for condition, condition_consistent_stat_dict in stat_probs_dict.items():
            #     for year, year_consistent_stat_dict in condition_consistent_stat_dict.items():
            #         for part, part_consistent_stat_dict in year_consistent_stat_dict.items():
            #             for key, val in part_consistent_stat_dict.items():
            #                 consistent_stat_dict[key] = val
            
            condition = 'all' # all conds match all
            part = 'regular' # get current part from time of year mth
            # player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
            prev_val = player_stat_dict[cur_yr][part][stat_name][condition]['0']
            #print('prev_val: ' + str(prev_val))
            # is it useful to get prev val under current conditions? possibly but could be misleading unless looking at larger sample
            
            for val, val_probs_dict in stat_probs_dict.items():
                #print('\n===Val: ' + str(val) + '===\n')
                #print('val_probs_dict: ' + str(val_probs_dict))
                #stat_val_probs_dict['val'] = str(val) + '+'
                val_str = str(val) + '+'
                if val == 0: # for zero we only want exactly 0 prob not over under bc 1+/- includes 1 and cannot go below 0
                    val_str = str(val)
                stat_val_probs_dict = {'player': player, 'team': player_team, 'stat': stat_name, 'val': val_str }
                #for conditions, prob in val_probs_dict.items():
                for conditions in all_conditions:
                    #print('\n===Conditions: ' + str(conditions) + '===\n')
                    prob = 0
                    #per_unit_prob = 0
                    if conditions in val_probs_dict.keys():
                        prob = val_probs_dict[conditions]
                        # already going thru all conditions which includes per unit conditions
                        #per_unit_conditions = conditions + ' per unit'
                        #per_unit_prob = val_probs_dict[per_unit_conditions]
                        #per_unit_prob = per_unit_probs_dict[player][stat_name][val][conditions] #val_probs_dict[per_unit_conditions]
                    #print('prob: ' + str(prob))
                    stat_val_probs_dict[conditions] = round(prob * 100)
                    #stat_val_probs_dict[per_unit_conditions] = round(per_unit_prob * 100)


                # add keys to dict used for ref but not yet to gen true prob
                # otherwise it will use string value to compute prob
                # all vals in val probs dict must be probs
                # so we should make a separate dict and combine them before display
                stat_val_probs_dict['prev val'] = prev_val
                #stat_val_probs_dict['prev val'] = val_probs_dict['prev val']

                # we actually want to show the player current conds so we can see which probs are being used and adjust for errors
                for cond_key, cond_val in player_current_conditions.items():
                    stat_val_probs_dict[cond_key] = cond_val

                # add game num for ref so we can sort by game to ensure at least 2 picks per game 
                # OR if only 1 allowed still need to see game teams next to each other to place picks on same page of gui
                # game_num = 0
                # for game in game_teams:
                #     if player_team
                stat_val_probs_dict['game'] = game_num


                # we want per unit probs next to corresponding yr for comparison in table
                # so add key above when looping thru conditions
                #stat_val_probs_dict['all 2023 regular per unit prob'] = val_probs_dict['all 2023 regular per unit prob']

                # one row for each val which has all conditions
                #print('stat_val_probs_dict: ' + str(stat_val_probs_dict))
                all_stat_prob_dicts.append(stat_val_probs_dict)

            #print('all_stat_prob_dicts: ' + str(all_stat_prob_dicts))

            # repeat for unders
            print('repeat probs for unders')
            for val, val_probs_dict in stat_probs_dict.items():
                #stat_val_probs_dict['val'] = str(val) + '-'
                if val > 1: # for zero we only want exactly 0 prob not over under bc 1+/- includes 1 and cannot go below 0
                    under_val = val - 1
                    val_str = str(under_val) + '-'
                    stat_val_probs_dict = {'player': player, 'team': player_team, 'stat': stat_name, 'val': val_str }
                    #for conditions, prob in val_probs_dict.items():
                    for conditions in all_conditions:
                        prob = 0
                        #per_unit_prob = 0
                        if conditions in val_probs_dict.keys():
                            prob = val_probs_dict[conditions]
                            #per_unit_conditions = conditions + ' per unit'
                            #per_unit_prob = val_probs_dict[per_unit_conditions]
                        #print('over prob: ' + str(prob))
                        stat_val_probs_dict[conditions] = 100 - round(prob * 100)
                        #stat_val_probs_dict[per_unit_conditions] = 100 - round(per_unit_prob * 100)

                    prob = val_probs_dict['true prob']
                    #print('over prob: ' + str(prob))
                    stat_val_probs_dict['true prob'] = 100 - round(prob * 100)
                    #print('under prob: ' + str(stat_val_probs_dict['true prob']))

                    # add more fields for ref
                    #stat_val_probs_dict['prev val'] = val_probs_dict['prev val']
                    stat_val_probs_dict['prev val'] = prev_val
                    for cond_key, cond_val in player_current_conditions.items():
                        stat_val_probs_dict[cond_key] = cond_val
                    stat_val_probs_dict['game'] = game_num

                    # one row for each val which has all conditions
                    #print('stat_val_probs_dict: ' + str(stat_val_probs_dict))
                    all_stat_prob_dicts.append(stat_val_probs_dict)

            #print('all_stat_prob_dicts: ' + str(all_stat_prob_dicts))

    # sort_keys = ['true prob']
    # all_stat_prob_dicts = sorter.sort_dicts_by_keys(all_stat_prob_dicts, sort_keys)

    #print('all_stat_prob_dicts: ' + str(all_stat_prob_dicts))
    return all_stat_prob_dicts

# for conditions we must get a sub-prob weighted mean for all year samples with that condition 
# just like old true prob bc takes one condition and gets all yrs samples combined into weighted avg
# where each yr adds 1 to the inverse multiplier so as data gets far away it gets less weight
# yr multiplier is arbitrary and must be discovered by ml algo
def generate_condition_mean_prob(condition, val_probs_dict, season_years, part, player_stat_dict):
    print('\n===Generate Condition Mean Prob: ' + condition + '===\n')
    print('season_years: ' + str(season_years))

    condition_mean_prob = 0

    probs = []
    # in this fcn it is for 1 condition and part of season so the conditions will just be different years, so 1 for each year
    all_current_conditions = [] # header field title 'condition year part'
    all_cur_cond_dicts = [] # cur_cond_dict = {'condition':condition, 'year':year, 'part':part}
    
    

    # we dont need to label probs in dict 
    # bc they are same condition in order by year going from recent to distant
    for year_idx in range(len(season_years)):
        year = season_years[year_idx]
        #print('\nyear: ' + str(year))

        # for each yr, we need a new cur cond dict bc the yr changes the cur conds
        cur_cond_dict = {'condition':condition, 'year':year, 'part':part}
        current_conditions = condition + ' ' + str(year) + ' ' + part + ' prob'
        if year_idx > 0:
            current_conditions += ' per unit'
        #print('current_conditions: ' + str(current_conditions))

        if current_conditions in val_probs_dict.keys():
            probs.append(val_probs_dict[current_conditions])
            all_current_conditions.append(current_conditions)
            all_cur_cond_dicts.append(cur_cond_dict)

    print('probs: ' + str(probs))
    print('all_current_conditions: ' + str(all_current_conditions))
    print('all_cur_cond_dicts: ' + str(all_cur_cond_dicts))

    # if no probs or cur conds then no need to find weights
    # which means unable to find cur conds in val probs dict so prob unknown
    # default condition mean prob to 0 for now but eventually can use other similar players mean prob but that would need to be separate bc it is not measured for this player
    # but if default to 0 then we must differentiate those without samples and those with samples who have reached line 0 times
    if len(probs) > 0:

        sample_sizes = []
        for p_idx in range(len(probs)):
            cur_conds = all_cur_cond_dicts[p_idx]
            s_n = determiner.determine_sample_size(player_stat_dict, cur_conds)
            sample_sizes.append(s_n)
        print('sample_sizes: ' + str(sample_sizes))

        s_1 = sample_sizes[0]

        t_1 = 1 # set bc current year is origin so multiply by 1. each year adds 1 as weight decreases. that weight should be determined by ml algo
        
        # already added first weight to list so start from idx 1
        # get weights by relation where each year adds 1 to divisor
        # eg this yr is 1 so divide by 1, prev yr is 2 and so on
        # this is arbitrary and must get more accurate way to show decay of relevance
        w_1 = 1.0 # other weights relative to current yr sample
        weights = [w_1]
        for p_idx in range(1,len(probs)):
            t_n = p_idx + 1 # years away
            s_n = sample_sizes[p_idx] #65 #previous years
            w_n = round(w_1 * round(t_1 / t_n, 6) * round(s_n / s_1, 6), 2)
            weights.append(w_n)
        print('weights: ' + str(weights))

        # solved for other ws in relation to w_1 already used to sub above
        #true_prob = 0#w_1 * p_1
        weighted_probs = []#0
        for p_idx in range(len(probs)):
            prob = probs[p_idx]
            #print('prob: ' + str(prob))
            w = weights[p_idx]
            #print('w: ' + str(w))
            wp = round(w * prob, 6)
            #print('wp: ' + str(wp))
            weighted_probs.append(wp) #+= wp
            #print('true_prob: ' + str(true_prob))
        
        denom = sum(weights)
        if denom > 0:
            condition_mean_prob = round(sum(weighted_probs) / denom, 2)
        else:
            print('Warning: denom 0 bc no samples for condition!')
        
    print('condition_mean_prob: ' + str(condition_mean_prob))
    return condition_mean_prob


def generate_all_conditions_mean_probs(val_probs_dict, season_years, player_current_conditions, part, player_stat_dict):
    print('\n===Generate All Conditions Mean Probs===\n')

    # can make list bc temp use prefer speed since already aligned with weights list in loop
    all_conditions_mean_probs = []#{}

    conditions = ['all'] + list(player_current_conditions.values())

    for condition in conditions:
        print('\ncondition: ' + str(condition))
        #all_conditions_mean_probs[condition] = generate_condition_mean_prob(condition, val_probs_dict, season_years, part, player_stat_dict)
        condition_mean_prob = generate_condition_mean_prob(condition, val_probs_dict, season_years, part, player_stat_dict)

        #all_conditions_mean_probs[condition] = condition_mean_prob
        all_conditions_mean_probs.append(condition_mean_prob)

    print('all_conditions_mean_probs: ' + str(all_conditions_mean_probs))
    return all_conditions_mean_probs

def generate_condition_sample_weight(player_stat_dict, cond_key, cond_val, part, season_years):
    print('\n===Generate Condition Sample Weights===\n')
    condition_sample_weight = 0 # if sample size 0 then weight 0

    cond_weights = {'all': 1, 'loc':5, 'teammates out': 10, 'dow':1, 'tod':2} 
    
    s_n = determiner.determine_condition_sample_size(player_stat_dict, cond_val, part, season_years) # for all yrs
    #sample_sizes.append(s_n)
    # log(0)=-inf
    if s_n > 0:
        sample_weight = round(math.log(s_n),6) # or log10? need to test both by predicting yrs that already happened so we can give supervised feedback
        print('condition_sample_weight = ' + str(cond_weights[cond_key]) + ' * ' + str(sample_weight))
        condition_sample_weight = round(float(cond_weights[cond_key]) * sample_weight, 2)
    
    print('condition_sample_weight: ' + str(condition_sample_weight))
    return condition_sample_weight

def generate_all_conditions_weights(season_years, player_current_conditions, part, player_stat_dict):
    print('\n===Generate All Conditions Weights===\n')

    all_conditions_weights = []
    
    # get weights for each condition prob
    # 1 sample size per condition, bc each condition gets total sample size over all yrs
    #sample_sizes = []
    all_cond = 'all'
    condition_sample_weight = generate_condition_sample_weight(player_stat_dict, all_cond, all_cond, part, season_years)
    all_conditions_weights.append(condition_sample_weight)

    for cond_key, cond_val in player_current_conditions.items():
        print('\ncond_key: ' + str(cond_key))
        print('cond_val: ' + str(cond_val))

        condition_sample_weight = generate_condition_sample_weight(player_stat_dict, cond_key, cond_val, part, season_years)

        all_conditions_weights.append(condition_sample_weight)
    

    # do we compare to first condition sample size or total samples
    # weights are relative to first condition so is it easier to make sample size relative to first condition also?
    # it should be the same bc the first condition is all which should include total samples
    #s_1 = sample_sizes[0] # should be all samples
    # we are using log10(sample size) to show how weight scales relative to sample size

    print('all_conditions_weights: ' + str(all_conditions_weights))
    return all_conditions_weights

# part of season we only care about current bc it doesnt help to compare when we already have full stats which includes both parts
# conditions = [all, home/away, ...] = [all,l1,c1,d1,t1,...] OR {loc:l1, city:c1, dow:d1, tod:t1,...}
# player current conds = p1:{loc:l1, city:c1, dow:d1, tod:t1,...}
def generate_true_prob(val_probs_dict, season_years, player_current_conditions, part, player_stat_dict, all_conditions_weights):
    print('\n===Generate True Prob===\n')
    #print('season_years: ' + str(season_years))

    true_prob = 0

    # p_true = w1p1 + w2p2
    # where w1+w2=1
    # and w_t=w1/t so w2=w1/2
    # for each year or condition, add prob to list
    # how do we know all years of interest?
    # can we get from info already passed?
    # yes from val 0 bc it is evaled for all conditions?
    # the user already passed seasons of interest so we can use that
    # how do we decide probs of interest? from curr conds
    # always include overall season probs
    # if a val not reached in a condition then it will not be included here
    
    
    # for conditions we must get a sub-prob weighted mean for all year samples with that condition 
    # then we can weight conditions relative to each other
    # it makes more sense to combine all the samples for a current condition to get as many samples as possible for the current condition
    # we must adjust by rate and weight to scale past season samples to current season relevance
    # all_conditions_mean_probs = {c1:p1,...}
    all_conditions_mean_probs = generate_all_conditions_mean_probs(val_probs_dict, season_years, player_current_conditions, part, player_stat_dict) # for the stat described in val probs dict

    
    print('\n===Generate Weighted Probs===\n')
    # solved for other ws in relation to w_1 already used to sub above
    weighted_probs = []
    for p_idx in range(len(all_conditions_mean_probs)):
        prob = all_conditions_mean_probs[p_idx]
        print('prob: ' + str(prob))
        weight = all_conditions_weights[p_idx]
        print('weight: ' + str(weight))
        wp = round(weight * prob, 6)
        print('wp: ' + str(wp))
        weighted_probs.append(wp)
        #true_prob += wp
        #print('true_prob: ' + str(true_prob))

    denom = sum(all_conditions_weights)
    if denom > 0:
        true_prob = round(sum(weighted_probs) / denom,2)
    else:
        print('Warning: denom 0 bc no samples for condition!')

    print('true_prob: ' + str(true_prob))

    return true_prob 

# all_stat_probs_dict = {player:stat:val:conditions:prob}
# all_stat_probs_dict has both orig and per unit stats so no need for all_per_unit_stat_probs_dict
# instead made per unit stat records
# all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...}
def generate_all_true_probs(all_stat_probs_dict, all_player_stat_dicts, season_years, all_current_conditions={}):
    print('\n===Generate All True Probs===\n')

    # before we get true prob we must know per unit probs

    # gen true probs for all stat probs dict
    # we get true prob for combos of conditions by weighting avg prob
    # start with overall true prob combining 2 seasons weighted by recency and sample size
    # relevance for a time period is shown in recency factor
    # need to know current conditions to get true prob
    # see how current conds were used for streak tables

    # get years from all_player_stat_probs so we know how many seasons of interest
    # years = list(list(list(all_player_stat_probs.values())[0].values())[0].keys())
    # print('years: ' + str(years))
    #cur_yr = str(season_years[0])
    
    for player, player_probs_dict in all_stat_probs_dict.items():
        print('\nplayer: ' + str(player))
        player_stat_dict = all_player_stat_dicts[player]
        #print('player_stat_dict: ' + str(player_stat_dict))
        # p1:{loc:l1, city:c1, dow:d1, tod:t1,...}
        player_current_conditions = all_current_conditions[player]
        print('player_current_conditions: ' + str(player_current_conditions))
        # first get overall probs for all reg seasons
        #condition = 'all' # all conds match all
        part = 'regular' # get current part from time of year mth
        # get conditions of game such as location
        # see gen player outcomes fcn for example
        # used to get from player lines so try that
        # could also get from espn schedule bc i think the url is unchanging?
        # include 'all' condition
        # conditions = ['all', 'home']
        #conditions = [condition] + list(player_current_conditions.values())
        #print('conditions: ' + str(conditions))

        # combine cond weights and sample size to get normalized cond weights
        # or can we ignore sample size bc the cond weights reflect sample size? no we must say a cond with less samples has less weight
        # we can pass all conditions weights to gen true probs bc same for all stats bc condition and sample size same for all stats
        all_conditions_weights = generate_all_conditions_weights(season_years, player_current_conditions, part, player_stat_dict)

        for stat, stat_probs_dict in player_probs_dict.items():
            print('\nstat: ' + str(stat))
            
            # player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
            #prev_val = player_stat_dict[cur_yr][part][stat][condition]['0']
            #print('prev_val: ' + str(prev_val))
            # is it useful to get prev val under current conditions? possibly but could be misleading unless looking at larger sample
            # moved prev val to gen all stat prob dicts fcn bc that is last step before display and val probs dict is strictly for probs

            for val, val_probs_dict in stat_probs_dict.items():
                print('\nval: ' + str(val))
                #print('val_probs_dict: ' + str(val_probs_dict))

                # get prev game stat vals from most recent game log in stat dict
                # and add keys to all_stat_prob_dicts
                # technically prev game stat vals affects stat prob so include in all stat probs dict
                #all_stat_prob_dicts = generate_all_prev_game_stat_vals
                
                val_probs_dict['true prob'] = generate_true_prob(val_probs_dict, season_years, player_current_conditions, part, player_stat_dict, all_conditions_weights)

                # # add keys to dict not used for ref but not yet to gen true prob
                # # otherwise it will use string value to compute prob
                # # all vals in val probs dict must be probs
                # # so we should make a separate dict and combine them before display
                # val_probs_dict['prev val'] = prev_val

                # # we actually want to show the player current conds so we can see which probs are being used and adjust for errors
                # for cond_key, cond_val in player_current_conditions.items():
                #     val_probs_dict[cond_key] = cond_val


    #print('all_stat_probs_dict: ' + str(all_stat_probs_dict))
    return all_stat_probs_dict

def generate_reg_season_logs(player_season_logs):
    reg_season_logs = {}

    # for year, year_season_log in player_season_logs.items():
    #     reg_season_logs[year] = {}
    #     for field, field_dict in year_season_log.items():
    #         reg_season_logs[year][field] = {}
    #         for idx, val in field_dict.items():
    #             if year_season_log['Type'][idx] == 'Regular':
    #                 reg_season_logs[year][field][idx] = val

    for year, year_season_log in player_season_logs.items():
        #print('year: ' + year)
        player_season_log_df = pd.DataFrame(year_season_log)
        player_season_log_df.index = player_season_log_df.index.map(str)
        #print('player_season_log_df: ' + str(player_season_log_df))

        reg_season_log_df = determiner.determine_regular_season_games(player_season_log_df)
        reg_season_log = reg_season_log_df.to_dict()
        reg_season_logs[year] = reg_season_log

    #print('reg_season_logs: ' + str(reg_season_logs))
    return reg_season_logs

def generate_part_season_logs(player_season_logs, part):
    part_season_logs = {}

    if part == 'full':
        part_season_logs = player_season_logs
    else:
        for year, year_season_log in player_season_logs.items():
            #print('year: ' + year)
            player_season_log_df = pd.DataFrame(year_season_log)
            player_season_log_df.index = player_season_log_df.index.map(str)
            #print('player_season_log_df: ' + str(player_season_log_df))

            part_season_log_df = determiner.determine_season_part_games(player_season_log_df, part)
            part_season_log = part_season_log_df.to_dict()
            part_season_logs[year] = part_season_log

    #print('part_season_logs: ' + str(part_season_logs))
    return part_season_logs

# need season logs for minutes played to scale stat vals
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
#player_unit_stat_records: {'all': {2023: {'regular': {'pts': 
def generate_player_unit_stat_records(player_name, player_stat_dict, player_season_logs):
    print('\n===Generate Player Unit Stat Records: ' + player_name.title() + '===\n')
    player_unit_stat_records = {}

    #print('player_season_logs: ' + str(player_season_logs))

    if len(player_season_logs.keys()) > 0:
    # gen list of reg season logs from full season logs
    # similar to iso fcn
        reg_season_logs = generate_reg_season_logs(player_season_logs)

        
        cur_yr = list(player_season_logs.keys())[0]
        #print('cur_yr: ' + cur_yr)
        cur_season_log = reg_season_logs[cur_yr]#list(player_season_logs.values())[0]
        #print('cur_season_log: ' + str(cur_season_log))
        cur_minutes_log = list(cur_season_log['MIN'].values())
        #print('cur_minutes_log: ' + str(cur_minutes_log))
        cur_mean_minutes = round(np.mean(np.array(cur_minutes_log)))
        #print('cur_mean_minutes: ' + str(cur_mean_minutes))

        stats_of_interest = ['pts','reb','ast','3pm']

        # year is a string bc it can be read from json which forces string
        for year, year_stat_dict in player_stat_dict.items():
            year = str(year) # to compare to json
            #print("\n===Year " + year + "===\n")
            for part, part_stat_dict in year_stat_dict.items():
                #print("\n===Season Part " + str(part) + "===\n")
                # need to isolate season part df to align with nested dict
                part_season_logs = generate_part_season_logs(player_season_logs, part)
                for stat, stat_dict in part_stat_dict.items():
                    
                    if stat in stats_of_interest:
                        #print("\n===Stat Name " + str(stat) + "===\n")
                        for condition, condition_stat_dict in stat_dict.items():
                            #print("\n===Condition " + str(condition) + "===\n")
                            all_probs_stat_reached = []

                            #print('condition_stat_dict: ' + str(condition_stat_dict))
                            stat_vals = list(condition_stat_dict.values())
                            #print('stat_vals: ' + str(stat_vals))
                            num_games_played = len(stat_vals)
                            #print('num games played ' + condition + ': ' + str(num_games_played))
                            if num_games_played > 0:
                                # adjust stat vals to current minutes
                                # max(stat_vals)+1 bc we want to include 0 and max stat val
                                # if left blank should default from 0 to n full length of range
                                # for 0 we need to compute prob of exactly 0 not over under
                                for stat_val in range(max(stat_vals)+1):
                                    #print('stat_val: ' + str(stat_val))
                                    num_games_reached = 0 # num games >= stat val, stat count, reset for each check stat val bc new count
                                    # loop through games to get count stat val >= game stat val
                                    for game_idx in range(num_games_played):
                                        #print('\ngame_idx: ' + str(game_idx))
                                        # if 0 consider adding x instead of multiplying 0

                                        # prev stat val meaning from a prev game so will be adjusted to current minutes
                                        prev_stat_val = stat_vals[game_idx]
                                        #print('prev_stat_val: ' + str(prev_stat_val))
                                        game_stat_val = prev_stat_val
                                        if year != cur_yr:
                                            #relative_game_idx = game_idx + int(list(list(season_log.values()[0].keys())[0]))
                                            season_log = part_season_logs[year]
                                            #print('season_log: ' + str(season_log))
                                            prev_minutes = list(season_log['MIN'].values())[game_idx]#[str(relative_game_idx)]
                                            #print('prev_minutes: ' + str(prev_minutes))
                                            #print('prev_stat_val * cur_mean_minutes / prev_minutes')
                                            #print(str(prev_stat_val) + ' * ' + str(cur_mean_minutes) + ' / ' + str(prev_minutes))
                                            # game stat val is what the stat val would be if playing current minutes
                                            if prev_minutes != 0.0:
                                                game_stat_val = round(float(prev_stat_val) * float(cur_mean_minutes) / float(prev_minutes))
                                        #print('game_stat_val: ' + str(game_stat_val))

                                        if int(stat_val) == 0:
                                            if game_stat_val == int(stat_val):
                                                num_games_reached += 1
                                        else:
                                            if game_stat_val >= int(stat_val):
                                                num_games_reached += 1

                                    prob_stat_reached = str(num_games_reached) + '/' + str(num_games_played)
                                    #print('prob_stat_reached: ' + str(prob_stat_reached))
                                    all_probs_stat_reached.append(prob_stat_reached)

                                # make parallel with player stat records
                                if condition not in player_unit_stat_records.keys():
                                    player_unit_stat_records[condition] = {}
                                if year not in player_unit_stat_records[condition].keys():
                                    player_unit_stat_records[condition][year] = {}
                                if part not in player_unit_stat_records[condition][year].keys():
                                    player_unit_stat_records[condition][year][part] = {}
                                
                                player_unit_stat_records[condition][year][part][stat] = all_probs_stat_reached



    #print('player_unit_stat_records: ' + str(player_unit_stat_records))
    return player_unit_stat_records

# parallel to stat probs but scaled to per minute basis
# player_stat_dict: {2023: {'regular': {'pts': {'all': {0: 18, 1: 19...
# player_unit_stat_probs = {'all': {2023: {'regular': {'pts': {'0': prob over
def generate_player_unit_stat_probs(player_stat_dict, player_name, player_season_logs):
    print('\n===Generate Player Unit Stat Probs: ' + player_name.title() + '===\n')

    player_unit_stat_probs = {}

    player_unit_stat_records = generate_player_unit_stat_records(player_name, player_stat_dict, player_season_logs)

    # player_stat_probs = {'all': {2023: {'regular': {'pts': {'0': num reached / num played,...
    player_unit_stat_probs = generate_player_stat_probs(player_unit_stat_records, player_name)

    # get prev minutes played
    # and prev stat val
    # skip cur season and start at prev season
    # adjust stat vals to scale to current minutes played
    # then see prob of going over line
    # unit_stat_vals = []
    # for season_log_idx in range(1,len(player_season_logs)):
    #     season_log = player_season_logs[season_log_idx]
    #     minutes_log = season_log.loc[:,'MIN']
    #     mean_minutes = np.mean(np.array(minutes_log))

    #     season_stat_dict = list(player_stat_dict.items())[season_log_idx]
    #     for stat in stat_names:
    #         stat_val_log = season_log.loc[:,stat.upper()]
    #         mean_stat_val = np.mean(np.array(stat_val_log))

    #         unit_stat_val = mean_stat_val / mean_minutes


    # for year, year_stat_dict in player_stat_dict.items():
    #     for part, part_stat_dict in year_stat_dict.items():
    #         for stat, stat_dict in part_stat_dict.items():
    #             stat_val_log = season_log.loc[:,stat.upper()]
    #             mean_stat_val = np.mean(np.array(stat_val_log))

    #             scaled_stat_val = mean_stat_val / mean_minutes

    #             unit_stat_val = cur_mean_minutes * scaled_stat_val

    #             unit_stat_record = generate_unit_stat_record()


    return player_unit_stat_probs

# p1:{loc:l1, city:c1, dow:d1, tod:t1,...}
# all lineups has random combo of full names and abbrevs so check both
# all_lineups = {team:{starters:[Klay Thompson, D. Green,...],out:[],bench:[],unknown:[]},...}
def generate_player_current_conditions(player, game_teams, player_teams, all_lineups={}, player_abbrev='', cur_yr=''):
    print('\n===Generate Player Current Conditions: ' + player + '===\n')

    player_current_conditions = {}

    player_team = determiner.determine_player_current_team(player, player_teams, cur_yr) #list(player_teams[player][cur_yr].keys())[-1] # current team
    print('player_team: ' + str(player_team))

    # condition: location
    player_current_conditions['loc'] = determiner.determine_player_game_location(player, game_teams, player_team)
    
    # condition: teammates and opps lineups
    # https://www.rotowire.com/basketball/nba-lineups.php
    # get teammates and opps conds
    #player_team = player_teams[player]
    # player team should be in all lineups if playing today
    if player_team in all_lineups.keys():
        # {starters:[],out:[],bench:[],unknown:[]}
        player_team_lineup = all_lineups[player_team]
        # determine opp team from game teams
        # opp_team = determiner.determine_opponent_team(player, game_teams, player_teams) #game_teams[opp_idx]
        # opponent_lineup = all_lineups[opp_team]
        # dealing with the ppl we know are out is first and then figure out how to deal with uncertain players
        #player_current_conditions['out'] = player_team_lineup['out']
        # player_current_conditions['starters'] = all_lineups
        # player_current_conditions['bench'] = all_lineups
        # player_current_conditions['unknown'] = all_lineups
        # player_current_conditions['opp players'] = all_lineups # different from 'opp' which is team
        # player_current_conditions['num teammates out'] = all_lineups
        # player_current_conditions['minutes to fill'] = all_lineups

        # we know if player is starting bc lineup online shows starters
        # player_start = 'start' or 'bench'
        player_current_conditions['player start'] = determiner.determine_player_start(player, player_abbrev, player_team_lineup)
    else:
        print('Warning: player team ' + player_team + ' not in all lineups!')

    print('player_current_conditions: ' + str(player_current_conditions))
    return player_current_conditions

# make dict of all current conditions for each player so we can use to compute true prob
# all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
def generate_all_current_conditions(players, game_teams, player_teams, rosters, find_players, cur_yr):
    print('\n===Generate All Current Conditions===\n')

    all_current_conditions = {}

    # read all teammates out from internet
    # starters affect both other starters and benchers
    # benchers mostly affect other benchers
    # but if a bench player with mucho minutes is out then starters may play a few more minutes too. 
    # so use mean minutes from stat dict to see how much playing time needs to be distributed to teammates
    # if player listed as out how do we know if they would have been a starter?
    # could get mean minutes played to see play time which might be better than knowing if starter
    # also see which position is out and needs to be filled
    # all_teammates_out = {game:{team:{out:[],gtd:[]}
    all_teammates_out = {}
    all_starters = {}
    all_benches = {}
    # if expected lineup, show both with and without questionable teammates
    # so when lineup confirmed, can go with correct option but really if lineup not yet confirmed then odds will not be set
    # but sometimes odds set only for expected lineups so better to avoid if unsure
    # if confirmed lineup, only need to show 1 lineup
    # 'out' will never include gtd bc we must classify gtd as 'starter', 'bench' or 'unknown' based on injury report certainty
    # if there are unknowns then starters and bench are also unknown so should we classify by mean minutes?
    #all_lineups = {confirmed:{team:{starters:[],out:[],bench:[],unknown:[]},...}, expected:{team:{starters:[],bench:[],out:[]},...}}
    all_lineups = {}
    if find_players:
        all_lineups = reader.read_all_lineups(players, player_teams, rosters)
    # if questionable then it is very hard to say how teammates will perform so can only go with safest options
    # we could figure out how likely it is for player to play based on injury reports
    # and adjust teammates true probs accordingly
    questionable_players = [] 
    # can we actually measure probability of player being out?
    # if we had access to all past injury reports but i dont think we do easily although it might be worth looking up
    # first try to use rotowire uncertainty rating on lineups page if available
    # basically, if gtd then uncertain unless injury report says they are likely to play bc they have been playing well and usually have gtd tag just in case
    # so once we know uncertain players, we will have to see which teammates they affect to know which players to avoid



    for player in players:

        # need to pass all lineups bc opponent lineups matter too
        player_curr_conds = generate_player_current_conditions(player, game_teams, player_teams, all_lineups, cur_yr=cur_yr)

        all_current_conditions[player] = player_curr_conds

    print('all_current_conditions: ' + str(all_current_conditions))
    return all_current_conditions

# conditions = list(list(all_current_conditions.values())[0].keys()) ['loc']
# desired_order.extend(conditions)
# # add columns in order of conditions used, by weight high to low
# # given current conditions used to determine true prob
# # take current conditions for each year
# conditions_order = generate_conditions_order(conditions)
# conditions_order = ['all 2024 regular prob', 'all 2023 regular prob per unit', 'all 2023 regular prob'] # 'home 2024 regular prob', 'home 2023 regular prob'
def generate_conditions_order(all_current_conditions, season_years, part):
    
    conditions_order = []#['all 2024 regular prob', 'all 2023 regular prob per unit', 'all 2023 regular prob'] # 'home 2024 regular prob', 'home 2023 regular prob'
    
    # find all condition vals
    # get all unique vals of cur conds
    current_conditions = determiner.determine_all_current_conditions(all_current_conditions)

    # we need to know all conditions of all players bc all players listed in same table
    # so location will show both home away
    # conditions with more options only need to show options that have current conditions
    # once we get all cur conds we can get all cur cond vals of all players
    # conditon val means the value of the condition like location is the key but home/away are the vals
    for current_condition in current_conditions:
        for year_idx in range(len(season_years)):
            year = season_years[year_idx]

            condition_title = current_condition + ' ' + str(year) + ' ' + part + ' prob'
            if year_idx > 0:
                condition_unit_title = condition_title + ' per unit'
                conditions_order.append(condition_unit_title)

            conditions_order.append(condition_title)

    print('conditions_order: ' + str(conditions_order))
    return conditions_order


# one outcome per stat of interest so each player has multiple outcomes
# we need game teams to know opponents
# so we can get conditional stats
# and only read game page once
def generate_players_outcomes(settings={}, players_names=[], game_teams=[], todays_games_date_obj=datetime.today(), rosters={}):

    print('\n===Generate Players Outcomes===\n')

    # init output
    players_outcomes = {}

    # enable no inputs needed, default to all games
    if len(players_names) == 0 and len(rosters.keys()):
        # read all games today
        print('read all games today')
        players_names = reader.read_teams_players(game_teams, read_new_teams)

    season_year = determiner.determine_current_season_year() # based on mth, changed to default or current season year, which is yr season ends
    if 'read season year' in settings.keys():
        season_year = settings['read season year']

    # get info about current todays date
    todays_games_date_obj = datetime.today() # by default assume todays game is actually today and we are not analyzing in advance

    current_year_str = determiner.determine_current_season_year()
    todays_date = todays_games_date_obj.strftime('%m-%d-%y')

    # === gather external data
    # OLD version got games from projected lines but quicker to get from schedule page
    # bc not always getting odds
    #raw_projected_lines = reader.read_raw_projected_lines(todays_games_date_obj)

    # if we gave no names, then get names from input lines, if given
    # if len(players_names) == 0: 
    #     players_names = determiner.determine_all_player_names(raw_projected_lines)

    player_espn_ids_dict = reader.read_all_player_espn_ids(players_names)

    # read teams players
    read_new_teams = False # saves time during testing other parts if we read existing teams saved locally
    # what if we want to read previous season?
    if 'read new teams' in settings.keys():
        read_new_teams = settings['read new teams']
    # player_teams = {player:{year:{team:gp,...},...}}
    player_teams = reader.read_all_players_teams(player_espn_ids_dict, read_new_teams) # only read team from internet if not saved

    # if we gave player lines, then format them in dict
    # projected_lines_dict = {}
    # if len(raw_projected_lines) > 0:
    #     projected_lines_dict = generate_projected_lines_dict(raw_projected_lines, player_espn_ids_dict, player_teams, players_names, settings['read new teams'], cur_yr=current_year_str)
    # print('\nprojected_lines_dict after gen projected lines: ' + str(projected_lines_dict))

    # read game logs
    read_x_seasons = 1 # saves time during testing other parts if we only read 1 season
    # what if we want to read previous season? make int so large int will read all seasons
    if 'read x seasons' in settings.keys():
        read_x_seasons = settings['read x seasons']
    all_player_season_logs_dict = reader.read_all_players_season_logs(players_names, read_x_seasons, player_espn_ids_dict, season_year)
    
    #print('projected_lines_dict after read season logs: ' + str(projected_lines_dict))

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


        player_positions = reader.read_all_players_positions(player_espn_ids_dict, season_year)
        

        # get matchup data before looping thru consistent streaks bc we will present matchup data alongside consistent streaks for comparison
        fantasy_pros_url = 'https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php' #'https://www.fantasypros.com/nba/defense-vs-position.php' #alt 2: betting_pros_url = 'https://www.bettingpros.com/nba/defense-vs-position/'
        hashtag_bball_url = 'https://hashtagbasketball.com/nba-defense-vs-position'
        swish_analytics_url = 'https://swishanalytics.com/optimus/nba/daily-fantasy-team-defensive-ranks-position'
        draft_edge_url = 'https://draftedge.com/nba-defense-vs-position/'


        # get matchup data for streaks to see if likely to continue streak
        matchup_data_sources = [fantasy_pros_url, hashtag_bball_url, swish_analytics_url] #, hashtag_bball_url, swish_analytics_url, betting_pros_url, draft_edge_url] # go thru each source so we can compare conflicts
        # first read all matchup data from internet and then loop through tables
        all_matchup_data = reader.read_all_matchup_data(matchup_data_sources) # all_matchup_data=[matchup_data1,..], where matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]

    

    # use init stat dicts to see which stats already saved so no need to read from internet
    # use for box scores
    # for now only using to see if we want to read box scores or if already read
    # also may change so we save just stat probs if not using stat dict for anything else but computing stat probs
    init_player_stat_dicts = reader.read_all_players_stat_dicts(players_names, current_year_str, todays_date)
    # find teammates and opponents for each game played by each player
    find_players = False
    if 'find players' in settings.keys():
        find_players = settings['find players']
    # v1: all_players_in_games_dict = {year:{game key:{away team abbrev:[away players],home team abbrev:[home players]}}}
    # or
    # v2: all_players_in_games_dict = {player:{game:{teammates:[],opponents:[]}}}
    # OR
    # v3: all_players_in_games_dict = {game:{starters:[],bench:[],opponents:[]}}}
    # OR
    # v4: all_players_in_games_dict = {year:{game:{away:{starters:[],bench:[]},home:{starters:[],bench:[]}}}},...}
    # start with v1 bc it is general for all games with no duplicates for players
    all_players_in_games_dict = {} 
    if find_players == True:
        print('FIND PLAYERS')
        # if we already have saved prev seasons then will only return this season games
        all_players_in_games_dict = reader.read_all_players_in_games(all_player_season_logs_dict, player_teams, current_year_str, init_player_stat_dicts)#, season_year) # go thru players in all_player_season_logs_dict to get game ids


    irreg_play_time = settings['irreg play time']

    # === organize external data into internal structure


    # need season yrs to get per unit time stats
    # and prev vals in stat dict to see sequence/trend
    # could just take the first year in the dict by default
    # but user already told us the years to look at in settings
    season_years = []
    for yr in range(season_year,season_year-read_x_seasons,-1):
        season_years.append(str(yr)) # make string to compare to json keys



    #all_player_consistent_stats = {} # we want to display all player consistent stats together for viewing convenience and analysis comparison
    all_player_stat_records = {}
    all_player_stat_dicts = {}
    all_player_stat_probs = {} # for all stat vals so gets messy if same dict as other measures
    all_unit_stat_probs = {}
    for player_name in players_names:
        player_name = player_name.lower()

        # see which prob results we already have saved 
        # so we dont have to read from internet and compute again
        # prob for each stat over and under
        # key_type = 'data/stat probs/' + player_name + ' prev probs.json'
        # init_player_stat_probs = reader.read_json(key_type)



        #print('all_player_season_logs_dict: ' + str(all_player_season_logs_dict))
        player_season_logs = all_player_season_logs_dict[player_name]

        # get player position and team from premade fcns 
        # bc if we do not have saved locally it will read from internet
        #player_id = player_espn_ids_dict[player_name]

        # player_position = ''
        # if player_name in player_positions.keys():
        # player_position = player_positions[player_name] 
        #player_position = reader.read_player_position(player_name, player_id, season_year, player_positions)

        # get player team so we can determine away/home team so we can determine teammates/opponents from players in games
        # we dont really need to get player team from internet here bc we already got all player teams in separate batch loop
        #player_team = reader.read_player_team(player_name, player_id, player_teams, read_new_teams=False) #player_teams[player_name]

        #print('projected_lines_dict passed to generate stat dict: ' + str(projected_lines_dict))
        init_player_stat_dict = init_player_stat_dicts[player_name]
        player_stat_dict = generate_player_stat_dict(player_name, player_season_logs, todays_games_date_obj, all_players_in_games_dict, player_teams, current_year_str, game_teams=game_teams, init_player_stat_dict=init_player_stat_dict)

        # gen all outcomes shows streaks
        # produces list of features to assess
        # much like the newer stat probs dict
        # player_all_outcomes_dict = generate_player_all_outcomes_dict(player_name, player_season_logs, projected_lines_dict, todays_games_date_obj, player_position, all_matchup_data, all_players_in_games_dict, player_team, player_stat_dict, season_year=season_year) # each player has an outcome for each stat
        # player_outcomes[player_name] = player_all_outcomes_dict

        # generate stat val reached at desired consistency
        # this would be one of the key possible outcomes given a probability
        # the initial outcome we have done so far is prob of reaching either the projected line or avg stat val
        # determine the stat val with record above 90%
        # player_consistent_stat_vals = {} same format as player stat records but with single max. consistent val for each stat for each condition
        player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
        # no need for consistent stats if showing all available stats from most to least likely
        #player_consistent_stats = generate_consistent_stat_vals(player_name, player_stat_dict, player_stat_records)
        #player_stat_records = generate_player_stat_records(player_name, player_stat_dict)
        #all_player_consistent_stats[player_name] = player_consistent_stats
        all_player_stat_records[player_name] = player_stat_records
        all_player_stat_dicts[player_name] = player_stat_dict

        # prob for each stat over and under
        player_stat_probs = generate_player_stat_probs(player_stat_records, player_name)
        all_player_stat_probs[player_name] = player_stat_probs
        # save player stat probs bc prev season stat probs unchanged
        # only need to overwrite if more prev seasons added
        # if init_player_stat_probs != player_stat_probs:
        #     filepath = ''
        #     write_param = ''
        #     writer.write_json_to_file(player_stat_probs, filepath, write_param)

        # gen all stat prob dicts adjusted to current minutes
        # bc abs vol prob of a sample with different minutes is not useful unless normalized minutes
        # could add in gen player stat probs so it is in all_player_stat_probs?
        # need player_season_logs for minutes
        # unit stat probs requires current mean minutes which changes with each game
        # so cannot be perm saved
        # can save init stat probs perm but do we even use it other than for ref?
        # even if just for ref still worth perm saving so not needed to compute each run
        # perm save stat dicts for prev years... 
        # OR init stat probs dicts with fractions showing sample size?
        # try just stat probs dicts bc already using for ref
        # but then see if we need prev stat dicts for anything else bc if so then need to perm save that too
        player_unit_stat_probs = generate_player_unit_stat_probs(player_stat_dict, player_name, player_season_logs)
        all_unit_stat_probs[player_name] = player_unit_stat_probs

        



    

    # each player gets a table separate sheet 
    # showing over and under probs for each stat val
    # val, prob over, prob under
    # 0, P_o0, P_u0
    # all_player_stat_probs = {player:condition:year:part:stat:val} = {'player': {'all': {2023: {'regular': {'pts': {'0': { 'prob over': po, 'prob under': pu },...
    #writer.write_all_player_stat_probs(all_player_stat_probs)

    
    # now we want all players in a single table sorted by high to low prob
    # problem is many of the high probs wont be available so we need to iso available props
    # once we have odds, we need to sort by expected val bc some lower prob may be higher ev
    
    # currently we are not using other players stats to determine probability 
    # but we may eventually use other similar players to get more samples for current player
    # so need to get all player stats before getting all stat probs
    # all_stat_probs_dict = {player:stat:val:conditions}
    all_stat_probs_dict = generate_all_stat_probs_dict(all_player_stat_probs, all_player_stat_dicts, all_unit_stat_probs, season_years, irreg_play_time)
    
    # add true probs to stat probs dict
    # need to know current conditions to determine true prob
    # and also later we order spreadsheet based on current conditions used to get true prob
    # conditions such as prev val are player specific but most conditions are team specific
    # all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
    all_current_conditions = generate_all_current_conditions(players_names, game_teams, player_teams, rosters, find_players, current_year_str) #determiner.determine_current_conditions() # [all, regular, home, ...]
    all_stat_probs_dict = generate_all_true_probs(all_stat_probs_dict, all_player_stat_dicts, season_years, all_current_conditions)
    
    # flatten nested dicts into one level and list them
    # all_stat_prob_dicts = [{player:player, stat:stat, val:val, conditions prob:prob,...},...]
    all_stat_prob_dicts = generate_all_stat_prob_dicts(all_stat_probs_dict, player_teams, all_current_conditions, all_player_stat_dicts, season_years, game_teams)
    desired_order = ['player', 'game', 'team', 'stat','val']
    writer.list_dicts(all_stat_prob_dicts, desired_order)


    #all_consistent_stat_dicts = generate_all_consistent_stat_dicts(all_player_consistent_stats, all_player_stat_records, all_player_stat_dicts, player_teams, season_year=season_year)
    #writer.display_consistent_stats(all_player_consistent_stats, all_player_stat_records)

    # now that we have all consistent stats,
    # see if each stat is available at a given value
    # also include given value in stat dict
    # so we can sort by value to get optimal return
    # need player id to read team
    desired_order.append('true prob')# = ['player', 'game', 'team', 'stat','val','true prob']
    available_prop_dicts = all_stat_prob_dicts#all_consistent_stat_dicts
    read_odds = True
    if 'read odds' in settings.keys():
        read_odds = settings['read odds']
    if read_odds:
        available_prop_dicts = generate_available_prop_dicts(all_stat_prob_dicts, game_teams, player_teams, current_year_str)
        desired_order.extend(['odds','ev']) # is there another way to ensure odds comes after true prob

    #desired_order = ['player', 'team', 'stat','ok val','ok val prob','odds','ok val post prob', 'ok val min margin', 'ok val post min margin', 'ok val mean margin', 'ok val post mean margin']
    
    # add ev to dicts
    # could also add ev same time as odds bc that is last needed var
    #available_prop_dicts = generate_ev_dicts(available_prop_dicts)

    sort_keys = ['true prob']
    available_prop_dicts = sorter.sort_dicts_by_keys(available_prop_dicts, sort_keys)
    print('available_prop_dicts: ' + str(available_prop_dicts))

    # after odds and ev columns if included
    # prev val is unique type of condition
    desired_order.append('prev val')

    # show the current conditions so we know which probs are used bc all probs are shown in table of all players
    #conditions = ['loc'] # add all conditions we are using to get true prob or uncertainty
    # all_current_conditions = {p1:{loc:l1, city:c1, dow:d1, tod:t1,...}, p2:{},...} OR {player1:[c1,c2,...], p2:[],...}
    # here we show conditions keys
    conditions = list(list(all_current_conditions.values())[0].keys())
    desired_order.extend(conditions)

    # add columns in order of conditions used, by weight high to low
    # given current conditions used to determine true prob
    # take current conditions for each year
    # here we show conditions values
    # get season part from time of yr
    season_part = 'regular'
    conditions_order = generate_conditions_order(all_current_conditions, season_years, season_part)
    #conditions_order = ['all 2024 regular prob', 'all 2023 regular prob per unit', 'all 2023 regular prob'] # 'home 2024 regular prob', 'home 2023 regular prob'
    desired_order.extend(conditions_order)
    print('desired_order: ' + str(desired_order))
    writer.list_dicts(available_prop_dicts, desired_order)#, output='excel')


    # strategy 1: high prob +ev (balance prob with ev)
    # 1. iso tru prob >= 90
    # 1.1 show tru prob >= 90 & prev_val < stat+ or prev_val > stat-
    # 2. iso +ev
    # 3. out of remaining options, sort by ev
    # 4. iso top x remaining options
    # 5. sort by game and team and stat
    # 6. see if any invalid single bets (only 1 good option for that game)
    # 7. replace invalid bets with next best valid ev
    
    prop_tables = [available_prop_dicts]
    sheet_names = ['All']

    print('prop_tables: ' + str(prop_tables))

    # 1. iso tru prob >= 90
    # define high prob eg >=90
    # we use isolator for strictly isolating parts of existing data when there is no processing or computation between input output
    high_prob_props = isolator.isolate_high_prob_props(available_prop_dicts)
    print('high_prob_props: ' + str(high_prob_props))
    if len(high_prob_props) > 0:
        prop_tables.append(high_prob_props)
        sheet_names.append('High Prob')
        # sort all high prob props by ev so we can potentially see 0 and -ev options incorrectly calculated due to irregular circumstance
        # sort_keys = ['ev']
        # sorted_high_props_by_ev = sorter.sort_dicts_by_keys(plus_ev_props, sort_keys)



        # strategy 1 props
        s1_props = high_prob_props

    # 2. iso +ev
    final_prop_dicts = available_prop_dicts
    if len(high_prob_props) > 0:
        final_prop_dicts = high_prob_props
    if 'ev' in final_prop_dicts[0].keys():
        print('ev found')
        plus_ev_props = isolator.isolate_plus_ev_props(final_prop_dicts)
        
        # 3. out of remaining options, sort by ev
        sort_keys = ['ev']
        plus_ev_props = sorter.sort_dicts_by_keys(plus_ev_props, sort_keys)
        prop_tables.append(plus_ev_props)
        sheet_names.append('+EV')

        # 4. iso top x remaining options
        dk_max_allowed = 20
        fd_max_allowed = 25
        # ideal max depends on cumulative ev
        top_options = plus_ev_props[0:dk_max_allowed]
        print('top_options: ' + str(top_options))

        # 5. sort by game and team and stat
        sort_keys = ['game', 'team', 'stat']
        top_options = sorter.sort_dicts_by_str_keys(top_options, sort_keys)
        #writer.list_dicts(top_options, desired_order)
        prop_tables.append(top_options)
        sheet_names.append('Top')

        s1_props = top_options

        print('prop_tables before reverse: ' + str(prop_tables))

        prop_tables = list(reversed(prop_tables))#.reverse() #[top_options, plus_ev_props, high_prob_props, available_prop_dicts]
        sheet_names = list(reversed(sheet_names))#.reverse() #['Top', '+EV', 'High Prob', 'All'] #, 'Rare' # rare shows those where prev val is anomalous so unlikely to repeat anomaly (eg player falls in bottom 10% game)
        
    

    #writer.list_dicts(s1_props, desired_order)

    # strategy 2: highest +ev
    # strategy 3: highest prob
    # strategy 4: combine +ev picks into multiple ~+100 parlays


    # todo: make fcn to classify recently broken streaks bc that recent game may be anomaly and they may revert back to streak
    # todo: to fully predict current player stats, must predict teammate and opponent stats and prioritize and align with totals
    print('final prop_tables: ' + str(prop_tables))
    print('sheet_names: ' + str(sheet_names))
    writer.write_prop_tables(prop_tables, sheet_names, desired_order)

    # pass player outcomes to another fcn to compute cumulative joint prob and ev?
    # do we need to return anything? we can always return whatever the final print is
    #player_outcomes = prop_tables
    #print('players_outcomes: ' + str(players_outcomes))
    return players_outcomes


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


# gen list of player names given teams so we dont have to type all names
def generate_players_names(teams):
    players_names = []

    for team in teams:
        # go to roster page espn
        team_players = reader.read_team_roster(team)
        players_names.extend(team_players)

    return players_names