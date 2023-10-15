# determiner.py
# determine conditions 
# eg if streak is considered consistent

import re # see if keyword in column name
import reader # format stat val

from datetime import datetime # convert date str to date so we can see if games 1 day apart and how many games apart

import requests # check if webpage exists while we are looping through player game log seasons until we cannot find game log for that year (note rare players may take a year off and come back but for now assume consistent years)
# request not working by checking status code 200 so test httplib2
import httplib2

import pandas as pd # read html results from webpage to determine if player played season

import numpy # mean, median

import generator # gen prob stat reached to determine prob from records

# if streak resembles pattern we have seen consistently such as 3/3,3/4,4/5,5/6,6/7,6/9,7/10
def determine_consistent_streak(stat_counts, stat_name=''):
    print("\n===Determine Consistent Streak===\n")
    print("stat_counts: " + str(stat_counts))
    consistent = False

    super_strict_streak = True # only 7/7,9/10 and above
    strict_streak = True
    

    # even if it is consistent it does not mean they will hit it next game
    # instead we must determine if likely to hit next game based on previous game pattern

    if super_strict_streak:
        if len(stat_counts) > 1:
            # if 100%, no matter length of streak
            if stat_counts[1] != 1: # avoid 1/2
                if len(stat_counts) > 3:
                    if stat_counts[3] != 2: # avoid 2/4
                        if stat_name != 'reb': # except reb bc too random
                            if len(stat_counts) > 6: 
                                if stat_counts[6] == 7 or stat_counts[6] == 0: # 7/7 or 0/7 bc key number 7 except reb bc too random
                                    consistent = True
                        if len(stat_counts) > 9:
                            if stat_counts[9] > 8 or stat_counts[9] < 2: # 9/10,10/10 or 1/10,0/10
                                consistent = True
    elif strict_streak:
        if len(stat_counts) > 1:
            # if 100%, no matter length of streak
            final_count = stat_counts[-1]
            final_total = len(stat_counts)
            if final_count == final_total or final_count == 0: # eg 1/1,3/3,13/13 etc or 0/10, etc
                consistent = True
            elif stat_counts[1] != 1: # avoid 1/2
                if len(stat_counts) > 3:
                    if stat_counts[3] != 2: # avoid 2/4
                        if len(stat_counts) > 6: 
                            if stat_counts[6] == 7 or stat_counts[6] == 0: # 7/7 or 0/7 bc key number 7
                                consistent = True
                        if len(stat_counts) > 9:
                            if stat_counts[9] > 7 or stat_counts[9] < 3: # 8/10,9/10,10/10 or 2/10,1/10,0/10
                                consistent = True
                
    else:
        if len(stat_counts) >= 10:
            if stat_counts[9] >= 7: # arbitrary 7/10
                consistent = True
            elif stat_counts[9] <= 3: # arbitrary 7/10
                consistent = True

            if stat_counts[2] == 3: # arbitrary 3/3
                consistent = True
            elif stat_counts[2] == 0: # arbitrary 0/3
                consistent = True
        elif len(stat_counts) >= 7: # 5 <= x <= 10
            if stat_counts[6] <= 1 or stat_counts[6] >= 6: # arbitrary 1/7 or 6/7
                consistent = True
        elif len(stat_counts) == 4: # x=4
            if stat_counts[3] == 4 or stat_counts[3] == 0: # arbitrary 4/4 or 0/4. if only 4 samples for the whole season and both are same then check other seasons for extended streak
                consistent = True
        elif len(stat_counts) == 3: # x=3
            if stat_counts[2] == 3 or stat_counts[2] == 0: # arbitrary 3/3. if only 3 samples for the whole season and both are same then check other seasons for extended streak
                consistent = True
        elif len(stat_counts) == 2: # x=2
            if stat_counts[1] == 2 or stat_counts[1] == 0: # arbitrary 2/2. if only 2 samples for the whole season and both are same then check other seasons for extended streak
                consistent = True

    if consistent:
        print('consistent')

    return consistent

# streak is in form of prediction dictionary
def determine_high_streak(streak_dict):
    #print('\n===Determine High Streak===\n')
    #print('streak_dict: ' + str(streak_dict))

    high_streak = False

    # if overall record is 1/2 and less than 9/10 then not high streak unless another condition has perfect record
    #overall_record = streak_dict['overall record']
    #if overall_record[1] < 2: #0/2,1/2

    streak = streak_dict['streak']
    #print('streak: ' + str(streak))

    #if 100% or 0, eg 10/10 or 0/y
    final_count = int(streak[-1].split('/')[0])
    final_total = int(streak[-1].split('/')[1])
    if final_count == final_total: # eg 13/13 or 3/3
        high_streak = True
    elif final_count == 0: # 0/y
        high_streak = True
    elif len(streak) > 9: # 9/10, 1/10
        count_10 = int(streak[9].split('/')[0])
        count_7 = int(streak[6].split('/')[0])
        if count_10 > 8 or count_10 < 2:
            high_streak = True
        elif count_7 == 7 or count_7 == 0:
            high_streak = True

    # if high_streak:
    #     print('high_streak')

    return high_streak


# determine high streaks which are 10/10, 9/10 and combined streaks like 4/4,8/10
def determine_high_streaks(all_valid_streaks_list):
    print('\n===Determine High Streaks===\n')
    high_streaks = []

    for streak in all_valid_streaks_list:

        if determine_high_streak(streak):
            high_streaks.append(streak)

    if len(high_streaks) == 0:
        print('Warning: No High Streaks! ')

    print('high_streaks: ' + str(high_streaks))
    return high_streaks

def determine_col_name(keyword,data):
    #print("\n===Determine Column Name===\n")

    final_col_name = '' # eg PTS or Sort: PTS
    for col_name in data.columns:
        if re.search(keyword.lower(),col_name.lower()):
            final_col_name = col_name
            break

    #print("final_col_name: " + final_col_name)
    return final_col_name

def determine_team_abbrev(team_name, team_abbrevs_dict={}):
    #print("\n===Determine Team Abbrev: " + team_name + "===\n")
    team_abbrevs_dict = {'atl':'atlanta hawks', 
                    'bos':'boston celtics', 
                    'bkn':'brooklyn nets', 
                    'cha':'charlotte hornets', 
                    'chi':'chicago bulls',
                    'cle':'cleveland cavaliers',
                    'dal':'dallas mavericks',
                    'den':'denver nuggets',
                    'det':'detroit pistons',
                    'gsw':'golden state warriors',
                    'hou':'houston rockets',
                    'ind':'indiana pacers',
                    'lac':'los angeles clippers',
                    'lal':'los angeles lakers',
                    'mem':'memphis grizzlies',
                    'mia':'miami heat',
                    'mil':'milwaukee bucks',
                    'min':'minnesota timberwolves',
                    'nop':'new orleans pelicans',
                    'nyk':'new york knicks',
                    'okc':'oklahoma city thunder',
                    'orl':'orlando magic',
                    'phi':'philadelphia 76ers',
                    'phx':'phoenix suns',
                    'por':'portland trail blazers',
                    'sac':'sacramento kings',
                    'sas':'san antonio spurs',
                    'tor':'toronto raptors',
                    'uta':'utah jazz',
                    'wsh':'washington wizards'} # could get from fantasy pros table but simpler to make once bc only 30 immutable vals

    team_abbrev = ''
    # problem with LA Clippers bc space is considered uppercase
    if team_name.lower() == 'la clippers':
        team_abbrev = 'lac'
    elif team_name.lower() == 'la lakers':
        team_abbrev = 'lal'
    elif team_name[:3].isupper(): 
        #print('first 3 letters uppercase')
        team_abbrev = team_name[:3].lower()

        irregular_abbrevs = {'bro':'bkn', 'okl':'okc', 'nor':'nop', 'pho':'phx', 'was':'wsh', 'uth': 'uta', 'utah': 'uta' } # for these match the first 3 letters of team name instead
        if team_abbrev in irregular_abbrevs.keys():
            #print("irregular abbrev: " + team_abbrev)
            team_abbrev = irregular_abbrevs[team_abbrev]
    else:
        for abbrev, name in team_abbrevs_dict.items():
            #print('name: ' + str(name))
            if re.search(team_name.lower(),name): # name is full name but we may be given partial team name
                #print('found match')
                team_abbrev = abbrev
                break

        # if we only have the abbrevs in list we can determine team name by structure
        # for abbrev in team_abbrevs:
        #     # see if abbrev in first 3 letters of name, like atl in atlanta
        #     if re.search(abbrev, team_name[:3].lower()):
        #         team_abbrev = abbrev
        #         break
        # # if abbrev not first 3 letters of name, check initials like nop, lal, lac
        # if team_abbrev == '':
        #     initials = [ s[0] for s in team_name.lower().split() ]
        #     for abbrev in team_abbrevs:
        #         if abbrev == initials:
        #             team_abbrev = abbrev
        #             break
        # # if abbrev not first 3 letters nor initials, then check 1st 2 letters like phx and okc
        # if team_abbrev == '':
        #     for abbrev in team_abbrevs:
        #         if re.search(abbrev[:2], team_name[:2].lower()):
        #             team_abbrev = abbrev
        #             break
        # # check 1st and last letters for bkn brooklyn nets
        # if team_abbrev == '':
        #     initials = [ s[0] for s in team_name.lower().split() ]
        #     for abbrev in team_abbrevs:
        #         first_last = abbrev[0] + abbrev[-1]
        #         if first_last == initials:
        #             team_abbrev = abbrev
        #             break

    #print("team_abbrev: " + str(team_abbrev))
    return team_abbrev

def determine_all_team_abbrevs(position_matchup_data):
    #print("\n===Determine All Team Abbrevs===\n")
    team_abbrevs = []
    for team_idx, row in position_matchup_data.iterrows():
        team_col_name = determine_col_name('team',position_matchup_data)
        team_name = str(position_matchup_data.loc[team_idx, team_col_name])
        if team_name[:3].isupper():
            team_abbrev = team_name[:3].lower()
            # correct irregular abbrevs
            irregular_abbrevs = {'bro':'bkn', 'okl':'okc'} # for these match the first 3 letters of team name instead
            # if team_abbrev == 'bro':
            #     team_abbrev = 'bkn'
            if team_abbrev in irregular_abbrevs.keys():
                team_abbrev = irregular_abbrevs[team_abbrev]

            team_abbrevs.append(team_abbrev)

    #print("team_abbrevs: " + str(team_abbrevs))
    return team_abbrevs

# rating or ranking bc shows average value and orders from easiest ot hardest by position and stat
def determine_matchup_rating(opponent, stat, all_matchup_data):
    print("\n===Determine Matchup Rating for " + opponent.upper() + ", " + stat + "===\n")
    if stat == '3pm':
        stat = '3p'
    

    positions = ['pg','sg','sf','pf','c']
    all_matchup_ratings = { 'pg':{}, 'sg':{}, 'sf':{}, 'pf':{}, 'c':{} } # { 'pg': { 'values': [source1,source2,..], 'ranks': [source1,source2,..] }, 'sg': {}, ... }
    #position_matchup_rating = { 'values':[], 'ranks':[] } # comparing results from different sources

    #team_abbrevs = []
    for source_matchup_data in all_matchup_data:
        #print("source_matchup_data: " + str(source_matchup_data))

        for position_idx in range(len(source_matchup_data)):
            position_matchup_data = source_matchup_data[position_idx]
            position = positions[position_idx]

            stat_col_name = determine_col_name(stat,position_matchup_data)

            # get all values for stat and sort so we can rank current team
            all_stat_vals = []
            for team_idx, row in position_matchup_data.iterrows():
                
                
                col_val = position_matchup_data.loc[team_idx, stat_col_name]
                stat_val = reader.format_stat_val(col_val)
                #print("stat_val: " + str(stat_val))
                all_stat_vals.append(stat_val)

            #print("all_stat_vals: " + str(all_stat_vals))
            all_stat_vals.sort()
            #print("all_stat_vals: " + str(all_stat_vals))

            # get all team abbrevs from source using abbrevs so we can relate name to abbrevs for sources only giving full name
            # if len(team_abbrevs) == 0:
            #     team_abbrevs = determine_all_team_abbrevs(position_matchup_data)
            
                

            for team_idx, row in position_matchup_data.iterrows():

                # for fantasypros.com source, format OKCoklahoma city, so take first 3 letters
                # for hashtag bball source, format OKC <rank>, so take first 3 letters also
                # but the header name is 'Sort: Team' not just 'Team'
                # team_col_name = 'Team'
                # for col_name in position_matchup_data.columns:
                #     if re.search('team',col_name.lower()):
                #         team_col_name = col_name
                team_col_name = determine_col_name('team',position_matchup_data)
                team_name = str(position_matchup_data.loc[team_idx, team_col_name])
                #print("team_name: " + team_name)
                team = determine_team_abbrev(team_name) # fantasy pros gives both name and abbrev together so use that source to make dict
                #print("team: " + team)
                #print("opponent: " + opponent)

                #if opponent in different_abbrevs:

                if team == opponent:

                    #stat_col_name = determine_col_name(stat,position_matchup_data)
                    #stat_val = float(position_matchup_data.loc[team_idx, stat_col_name])
                    col_val = position_matchup_data.loc[team_idx, stat_col_name]
                    stat_val = reader.format_stat_val(col_val)
                    rank = all_stat_vals.index(stat_val) + 1

                    position_matchup_rating = all_matchup_ratings[position]
                    if 'averages' in position_matchup_rating.keys():
                        position_matchup_rating['averages'].append(stat_val)

                        position_matchup_rating['ranks'].append(rank)
                    else:
                        position_matchup_rating['averages'] = [stat_val]

                        position_matchup_rating['ranks'] = [rank]
                    
                    

                    break # found team so move to next position

    #print("all_matchup_ratings: " + str(all_matchup_ratings))                  
    return all_matchup_ratings

# exclude all star and other special games
def determine_prev_game_date(player_game_log, season_year):
    # if not all star
    prev_game_idx = 0
    while re.search('\\*', player_game_log.loc[prev_game_idx, 'OPP']):
        prev_game_idx += 1

    init_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] # 'wed 2/15'
    game_mth = init_game_date_string.split('/')[0]
    final_season_year = str(season_year)
    if int(game_mth) in range(10,13):
        final_season_year = str(season_year - 1)
    prev_game_date_string = init_game_date_string + "/" + final_season_year


    #prev_game_date_string = player_game_log.loc[prev_game_idx, 'Date'].split()[1] + "/" + str(season_year) # eg 'wed 2/15' to '2/15/23'
    prev_game_date_obj = datetime.strptime(prev_game_date_string, '%m/%d/%Y')
    return prev_game_date_obj


# gather game logs by season and do not pull webpage if it does not exist
def determine_played_season(player_url):
    played_season = False
    # response = requests.get(player_url)
    # if response.status_code == 200:
    #     played_season = True
    #     print('played season')

    h = httplib2.Http()
    resp = h.request(player_url, 'HEAD')
    status_code = resp[0]['status']
    print('status_code: ' + str(status_code))
    if int(status_code) < 400:
        # some websites will simply not have the webpage but espn still has the webpage for all years prior to playing with blank game logs
        #if len(game_log) > 0:

        html_results = pd.read_html(player_url)
        #print("html_results: " + str(html_results))

        len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table

        for order in range(len_html_results):
            #print("order: " + str(order))

            if len(html_results[order].columns.tolist()) == 17:

                played_season = True
                print('played season')

                break

    return played_season


def determine_regular_season_games(player_game_log):

    print('\n===Determine Regular Season Games for Player===\n')
    print('player_game_log:\n' + str(player_game_log))

    # select reg season games by type
    reg_season_games_df = player_game_log[player_game_log['Type'].str.startswith('Regular')]
    #print("partial reg_season_games_df:\n" + str(reg_season_games_df) + '\n')
    # remove all star and exception games with *
    reg_season_games_df = reg_season_games_df[~reg_season_games_df['OPP'].str.endswith('*')]

    #reg_season_games_df = pd.DataFrame()
    # reg_season_games = []

    # for game_idx, row in player_game_log.iterrows():
    #     if re.search('\\*',player_game_log.loc[game_idx, 'OPP']): # all star stats not included in regular season stats
    #         #print("game excluded")
    #         continue
        
    #     if player_game_log.loc[game_idx, 'Type'] == 'Regular':
    #         reg_season_games.append(row)

    # reg_season_games_df = pd.concat(reg_season_games)

    print("final reg_season_games_df:\n" + str(reg_season_games_df) + '\n')
    return reg_season_games_df

def determine_season_part_games(player_game_log, season_part):

    print('\n===Determine Season Games for Player: ' + season_part + '===\n')
    print('player_game_log:\n' + str(player_game_log))

    season_part_games_df = season_part_games_df = player_game_log[~player_game_log['Type'].str.startswith('Preseason')]#pd.DataFrame()#player_game_log

    # cannot make default all game log bc we want to exclude preseason
    # select reg season games by type
    if season_part == 'regular' or season_part == 'postseason':
        season_part_games_df = player_game_log[player_game_log['Type'].str.startswith(season_part.title())]
        #print("partial reg_season_games_df:\n" + str(reg_season_games_df) + '\n')
    #elif season_part == 'full':
        #season_part_games_df = player_game_log[~player_game_log['Type'].str.startswith('Preseason')]
        
    # remove all star and exception games with *
    # always separate special games
    season_part_games_df = season_part_games_df[~season_part_games_df['OPP'].str.endswith('*')]



    print("final season_part_games_df:\n" + str(season_part_games_df) + '\n')
    return season_part_games_df

# is it an over or under? above 7/10 or 4/5 or 3/3, or below 3/10 and not 2/2 bc maybe teammate injury so more playing time?
def determine_streak_direction(streak):
    direction = '+'

    final_count = int(streak[-1].split('/')[0])
    final_total = int(streak[-1].split('/')[1])
    if final_count == final_total:
        direction = '+'
    elif final_count == 0:
        direction = '-'
    else:

        # 1st idx header like [pts 10+,1/1,2/2,..]
        out_of_10 = 0
        out_of_5 = 0
        out_of_3 = 0
        out_of_2 = 0
        if len(streak) > 10:
            out_of_10 = int(streak[10].split('/')[0])
        if len(streak) > 5:
            out_of_5 = int(streak[5].split('/')[0])
        if len(streak) > 3:
            out_of_3 = int(streak[3].split('/')[0])
        if len(streak) > 2:
            out_of_2 = int(streak[2].split('/')[0])

        if out_of_10 >= 7 or out_of_5 >= 4 or out_of_3 >= 3:
            direction = '+'
        elif out_of_10 <= 3 and out_of_2 < 2: # if 3/10 but 2/2 then maybe recent change causing beginning of over streak
            direction = '-'
        elif out_of_3 == 0:
            direction = '-'

    


    return direction

# streak has header element
def determine_streak_outline(streak):
    #print("\n===Determine Streak Outline===\n")
    #print(record)
    outline = []

    outline_idxs = [0,1,2,3,4,5,6,7,8,9,14,19,29,49]

    for game_idx in range(len(streak[1:])):
        game = streak[game_idx+1] # record has header at idx 0
        if game_idx in outline_idxs:
            outline.append(game)

    #print('outline: ' + str(outline))
    return outline

def determine_record_outline(record):
    #print("\n===Determine Record Outline===\n")
    #print(record)
    outline = []

    outline_idxs = [0,1,2,3,4,5,6,7,8,9,14,19,29,49]

    for game_idx in range(len(record)):
        game = record[game_idx] # record has header at idx 0
        if game_idx in outline_idxs:
            outline.append(game)

    #print('outline: ' + str(outline))
    return outline

# mean, corrected mean, combined mean
# matchup_dict = { pg: { s1: 0, s2: 0, .. }, sg: { s1: 0 }, .. }
def determine_rank_avgs(pos, matchup_dict):

    # combined mean is enough to cancel error when determining which position player is
    rank_avgs = {'mean':0, 'combined mean':0} # add corrected mean which checks to see which position the sources agree with most


    pos_matchup_ranks = [matchup_dict[pos]['s1'],matchup_dict[pos]['s2'],matchup_dict[pos]['s3']]

    rank_avgs['mean'] = round(numpy.mean(pos_matchup_ranks))

    alt_pos = 'c' # if listed pos=pg then combine with guard bc sometimes play both
    if pos == 'pg':
        alt_pos = 'sg'
    elif pos == 'sg':
        alt_pos = 'pg'
    elif pos == 'sf':
        alt_pos = 'pf'
    elif pos == 'pf':
        alt_pos = 'sf'
    alt_pos_matchup_ranks = [matchup_dict[alt_pos]['s1'],matchup_dict[alt_pos]['s2'],matchup_dict[alt_pos]['s3']]
    rank_avgs['combined mean'] = round(numpy.mean(pos_matchup_ranks+alt_pos_matchup_ranks))


    return rank_avgs

def determine_all_player_names(raw_projected_lines):
    print('\n===Determine All Player Names===\n')
    # get all player names so we can get their espn IDs and from that get team, position, game log, and schedule
    player_names = []
    player_initials = ['og','cj','pj','rj','tj','jt','jd']
    for row in raw_projected_lines:
        first_element_wo_punctuation = re.sub('\'|\.','',row[0])
        if first_element_wo_punctuation != 'PLAYER' and first_element_wo_punctuation.lower() != 'na': # uppercase indicates team abbrev like CHI
            #print('found player line')
            if not first_element_wo_punctuation[:3].isupper(): # allow if first 3 letters uppercase but one of them is apostrphe in player name like D'Angelo
                player_names.append(row[0].lower())
            elif first_element_wo_punctuation[:2].lower() in player_initials: # if uppercase but player initials
                player_names.append(row[0].lower())

    # check for players with no points line but rebounds line
    for row in raw_projected_lines:
        if len(row) > 3:
            first_element_wo_punctuation = re.sub('\'|\\.','',row[3])
            if first_element_wo_punctuation != 'PLAYER' and first_element_wo_punctuation.lower() != 'na': # uppercase indicates team abbrev like CHI
                #print('found player line')

                
                player_name = row[3].lower() #keep punctuation in key
                if not first_element_wo_punctuation[:3].isupper(): 
                    if player_name not in player_names:
                        print('found player with no pts line: ' + player_name)
                        player_names.append(player_name)
                elif first_element_wo_punctuation[:2].lower() in player_initials: # if uppercase but player initials
                    if player_name not in player_names:
                        print('found player with no pts line: ' + player_name)
                        player_names.append(player_name)

    #print("player_names: " + str(player_names))
    return player_names

# may come in format away: [record] so split and convert string to list
def determine_record_score(record):
    print('\n===Determime Record Score===\n')
    print('record: ' + str(record))
    score = 0
    

    # if 0/2,1/4,4/10, then -1
    # if 2/2,2/4,4/10, then 0 bc recent success
    # if 2/2,2/4,2/10, then still 0 bc recent success
    stat_counts = [] # [0,0,1,..]
    for partial_record in record:
        stat_count = int(partial_record.split('/')[0])
        stat_counts.append(stat_count)
    #print('stat_counts: ' + str(stat_counts))

    if len(record) > 0:
        final_count = stat_counts[-1]
        final_total = int(record[-1].split('/')[1])
        #print('final_count: ' + str(final_count))
        #print('final_total: ' + str(final_total))
        if final_count == final_total:
            score = 1
        elif final_count == 0:
            score = -1
        else:
            #print('check record not 0 or 100')
            if len(record) > 4: # 1/5
                if stat_counts[4] < 2:
                    score = -1

            if len(record) > 7: 
                if stat_counts[1] == 0 and stat_counts[7] < 3: # 0/2,2/8
                    score = -1

            if len(record) > 8: 
                if stat_counts[1] == 0 and stat_counts[3] < 3 and stat_counts[8] < 4: # 0/2,2/4,3/9
                    score = -1

            if len(record) > 9:
                #print('length of record > 9')
                #print('stat_counts[1]: ' + str(stat_counts[1]))

                # negative score
                if stat_counts[1] == 0 and stat_counts[9] < 5: # 0/2,4/10
                    score = -1
                elif stat_counts[2] == 0 and stat_counts[9] < 7: # 0/3,6/10
                    score = -1
                elif stat_counts[1] < 2 and stat_counts[9] < 3: # 1/1,1/2,1/5,2/10
                    score = -1
                elif stat_counts[0] == 0 and stat_counts[1] < 2 and stat_counts[4] < 3 and stat_counts[9] < 5: # 0/1,1/2,2/5,4/10
                    score = -1

                # positive score
                elif stat_counts[6] == 7: # 7/7,7/10
                    score = 1
                elif stat_counts[1] == 2 and stat_counts[4] > 3 and stat_counts[9] > 7: # 2/2,4/5,8/10
                    score = 1
                elif len(record) > 10:
                    print('length of record > 10') # since record outline, must check total in denominator to be sure we are referring to correct stat count bc if greater than 15 samples we use outline skipping some samples so see determine record outline fcn
                    if stat_counts[1] > 0 and stat_counts[3] > 1 and stat_counts[4] > 2 and stat_counts[9] > 7 and stat_counts[10] > 10: # 1/2,2/4,3/5,8/10,11/15
                        score = 1
                    
                    elif stat_counts[3] == 4 and stat_counts[9] > 6 and stat_counts[10] > 11: # 4/4,7/10,12/15
                        score = 1

                    elif stat_counts[1] == 2 and stat_counts[9] > 6 and stat_counts[10] > 12: # 2/2,7/10,13/15
                        score = 1

                    elif stat_counts[1] == 2 and stat_counts[4] > 2 and stat_counts[9] > 5 and stat_counts[10] > 12: # 2/2,3/5,6/10,13/15
                        score = 1


                    # elif stat_counts[1] == 2:
                    #     if stat_counts[9] > 6: # 2/2,7/10
                    #         score = 1
                    #     elif stat_counts[4] > 2 and stat_counts[9] > 5: # 2/2,3/5,6/10
                    #         score = 1
                    # elif stat_counts[6] == 7 and stat_counts[9] > 6: # 7/7,7/10 if we want to do 2/2,8/10 instead above more strict
                    #     score = 1

    

    print('score: ' + str(score))
    return score

def determine_average_range_score(prediction, median, mode):
    print('\n===Determine Average Range Score===\n')
    score = 0

    prediction_stat_val = int(re.sub('[+-]','',prediction.split()[-2]))
    print('prediction_stat_val: ' + str(prediction_stat_val))
    print('median: ' + str(median))
    print('mode: ' + str(mode))
    
    # assuming streak direction positive/over bc later we will reverse for under
    # if median or mode are greater than player line, and the other is not below line, score +1
    # if one at or above line and the other above, then score +1
    if median - prediction_stat_val > 0 and not mode - prediction_stat_val < 0:
        score = 1
    elif mode - prediction_stat_val > 0 and not median - prediction_stat_val < 0:
        score = 1
    # if median or mode less than player line, and the other is not above line, score -1.
    # if one at or below line and the other below, then score -1
    elif median - prediction_stat_val < 0 and not mode - prediction_stat_val > 0: 
        score = -1
    elif mode - prediction_stat_val < 0 and not median - prediction_stat_val > 0:
        score = -1
    

    print('score: ' + str(score))
    return score

# give streak prediction, a degree of belief score based on all streaks, avgs, range, matchup, location, and all other conditions
def determine_degree_of_belief(streak):

    print('\n===Determine Degree of Belief===\n')
    print('streak: ' + str(streak))

    deg_of_bel = 0

    prediction = streak['prediction'] # eg 'julius randle 10+ reb'
    print('prediction: ' + str(prediction))

    # use streak direction to determine if matchup and location are good or bad for prediction
    streak_direction = re.sub('\d','',prediction.split()[-2]) # + or -
    print('streak_direction: ' + streak_direction)

    # if matchup info is given then score matchup
    matchup_score = 0
    if 's1 matchup' in streak.keys():

        matchup_mean = streak['matchup mean']
        if matchup_mean > 20: # if easy matchup >20/30
            matchup_score = 1
            # if streak_direction == '+': # and projected over, then matchup score +1
            #     matchup_score = 1
            # else: # but projected under, then matchup score -1 bc projected under but easy matchup so they could over
            #     matchup_score = -1
        elif matchup_mean < 10: # if hard matchup <10/30
            matchup_score = -1
            # if streak_direction == '+': # but projected over, then matchup score -1
            #     matchup_score = -1
            # else: # and projected under, then matchup score +1 bc projected under and hard matchup so they should go under
            #     matchup_score = 1
        
    print('matchup_score: ' + str(matchup_score))

    # if home and over then +1, etc
    location_score = 0
    location = streak['location record'].split(':')[0]
    print('location: ' + str(location))
    if location == 'home':
        location_score = 1
    else:
        location_score = -1
    #     if streak_direction == '+': # and projected over, then loc score +1
    #         location_score = 1
    #     else: # but projected under, then loc score -1 bc projected under but easy loc so they could over
    #         location_score = -1
    # else: # away
    #     if streak_direction == '+': # but projected over, then loc score -1
    #         location_score = -1
    #     else: # and projected under, then loc score +1 bc projected under and hard loc so they should go under
    #         location_score = 1
    print('location_score: ' + str(location_score))

    all_record_score = determine_record_score(streak['overall record'])
    # if re.search(':',record):
    #     record = list(streak['location record'].split(':')[1].strip())
    #     print('corrected record: ' + str(record))

    location_record_string = re.sub('\'','',streak['location record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
    location_record = location_record_string.strip('][').split(', ')
    #print('loc_record: \'' + str(location_record) + '\'')
    loc_record_score = determine_record_score(location_record)

    opp_record_score = 0
    if len(streak['opponent record']) > 0:
        opp_record_string = re.sub('\'','',streak['opponent record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
        opp_record = opp_record_string.strip('][').split(', ')
        opp_record_score = determine_record_score(opp_record)

    time_after_record_score = 0
    if len(streak['time after record']) > 0:
        time_after_record_string = re.sub('\'','',streak['time after record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
        time_after_record = time_after_record_string.strip('][').split(', ')
        time_after_record_score = determine_record_score(time_after_record)

    dow_record_score = 0
    if len(streak['day record']) > 0:
        dow_record_string = re.sub('\'','',streak['day record'].split(':')[1].strip()) # home: ['1/1',..,'10/10'] -> ['1/1',..,'10/10']
        dow_record = dow_record_string.strip('][').split(', ')
        dow_record_score = determine_record_score(dow_record)

    overall_median = streak['overall median']
    overall_mode = streak['overall mode']
    all_avg_score = determine_average_range_score(prediction, overall_median, overall_mode)

    loc_median = streak['location median']
    loc_mode = streak['location mode']
    loc_avg_score = determine_average_range_score(prediction, loc_median, loc_mode)

    opp_avg_score = 0
    if streak['opponent median'] != '':
        opp_median = streak['opponent median']
        opp_mode = streak['opponent mode']
        opp_avg_score = determine_average_range_score(prediction, opp_median, opp_mode)

    time_after_avg_score = 0
    if streak['time after median'] != '':
        time_after_median = streak['time after median']
        time_after_mode = streak['time after mode']
        time_after_avg_score = determine_average_range_score(prediction, time_after_median, time_after_mode)

    dow_avg_score = 0
    if streak['day median'] != '':
        dow_median = streak['day median']
        dow_mode = streak['day mode']
        dow_avg_score = determine_average_range_score(prediction, dow_median, dow_mode)

    sub_scores = [matchup_score, location_score, all_record_score,loc_record_score,opp_record_score,time_after_record_score,dow_record_score,all_avg_score,loc_avg_score,opp_avg_score,time_after_avg_score,dow_avg_score]
    print('sub_scores: ' + str(sub_scores))
    corrected_sub_scores = []
    # reverse scores for negative direction/unders
    for score in sub_scores:
        if streak_direction == '-':
            score = score * -1
        corrected_sub_scores.append(score)

    print('corrected_sub_scores: ' + str(corrected_sub_scores))


    deg_of_bel = 0 #matchup_score + location_score + all_record_score + loc_record_score + opp_record_score + time_after_record_score + dow_record_score + all_avg_score + loc_avg_score + opp_avg_score + time_after_avg_score + dow_avg_score
    for score in corrected_sub_scores:
        deg_of_bel += score

    print('deg_of_bel: ' + str(deg_of_bel))
    return deg_of_bel

def determine_all_degrees_of_belief(streaks):
    degrees_of_belief = {}

    for streak in streaks:

        deg_of_bel = determine_degree_of_belief(streak)

        prediction = streak['prediction'] # eg 'julius randle 10+ reb'

        degrees_of_belief[prediction] = deg_of_bel # eg 7

    return degrees_of_belief

# prediction is really a list of features that we must assess to determine the probability of both/all outcomes
# similar to determine degree of belief above but restructured
def determine_probability_of_prediction(prediction):
    prob = 0

    return prob


# change prediction dictionary to outcome features bc we are not predicting
# we are determining the prob of an outcome given the features
# eg prob player scores 10+p given stats, records, avg, range, matchups, etc
# features = {possible outcome:'', record:[], ..}
def determine_probability_of_outcome(features):
    prob = 0

    return prob


# need to weigh recent samples more
# and weigh samples more or less based on specific circumstances like teammates
# but that may come at the next step when accounting for all conditions
# record = ['1/1','2/2',..]
# weigh samples after trade much more than before
def determine_probability_from_record(record, games_traded=0):
    #prob = 0

    # most basic is take ratio of all samples
    count = int(record[-1].split('/')[0])
    total = int(record[-1].split('/')[1])

    # weigh 10,50: 0.5,0.5
    # weigh 3,5,7,10,13,15,20,30,50: 0.2,0.1,0.1,0.1,..
    # determine weights of sample ranges based on no. samples


    # display as percentage
    prob = round(count * 100 / total) # eg 10 * 100 / 20 = 50

    print('prob: ' + str(prob))
    return prob



# determine if the given list of current teammates is in a given game of interest
# if we do not know current teammates yet then assume yet so we show all options
# teammates = ['j brown sg',..]
def determine_current_teammates_in_game(game_teammates, current_teammates):
    
    current_teammates_in_game = game_teammates

    #if len(current_teammates) > 0:
        # how do we tell if players on the roster are out of rotation? from their game log minutes



    return current_teammates_in_game

# make list to loop through so we can add all stats to dicts with 1 fcn
# list order or keys must correspond with all_stats_dicts bc we assign by idx/key
def determine_game_stats(player_game_log, game_idx):

    # === Collect Stats for Current Game ===

    pts = int(player_game_log.loc[game_idx, 'PTS'])
    rebs = int(player_game_log.loc[game_idx, 'REB'])
    asts = int(player_game_log.loc[game_idx, 'AST'])

    results = player_game_log.loc[game_idx, 'Result']
    #print("results: " + results)
    results = re.sub('[a-zA-Z]', '', results)
    # remove #OT from result string
    results = re.split("\\s+", results)[0]
    #print("results_data: " + str(results_data))
    score_data = results.split('-')
    #print("score_data: " + str(score_data))
    winning_score = int(score_data[0])
    losing_score = int(score_data[1])

    minutes = int(player_game_log.loc[game_idx, 'MIN'])

    fgs = player_game_log.loc[game_idx, 'FG']
    fg_data = fgs.split('-')
    fgm = int(fg_data[0])
    fga = int(fg_data[1])
    fg_rate = round(float(player_game_log.loc[game_idx, 'FG%']), 1)

    #threes = game[three_idx]
    #threes_data = threes.split('-')
    #print("threes_data: " + str(threes_data))
    threes_made = int(player_game_log.loc[game_idx, '3PT_SA'])
    threes_attempts = int(player_game_log.loc[game_idx, '3PT_A'])
    three_rate = round(float(player_game_log.loc[game_idx, '3P%']), 1)

    fts = player_game_log.loc[game_idx, 'FT']
    ft_data = fts.split('-')
    ftm = int(ft_data[0])
    fta = int(ft_data[1])
    ft_rate = round(float(player_game_log.loc[game_idx, 'FT%']), 1)

    bs = int(player_game_log.loc[game_idx, 'BLK'])
    ss = int(player_game_log.loc[game_idx, 'STL'])
    fs = int(player_game_log.loc[game_idx, 'PF'])
    tos = int(player_game_log.loc[game_idx, 'TO'])

    # make list to loop through so we can add all stats to dicts with 1 fcn
    game_stats = [pts,rebs,asts,winning_score,losing_score,minutes,fgm,fga,fg_rate,threes_made,threes_attempts,three_rate,ftm,fta,ft_rate,bs,ss,fs,tos] 

    return game_stats


def determine_matching_key(dict, match_val):

    print('\n===Determine Match Key for Val: ' + str(match_val) + '===\n')
    print('dict: ' + str(dict))

    match_key = ''

    for key, val in dict.items():
        if key != 'ok val':
            if val == match_val and re.search('post.*val',key):
                match_key = key

    print('match_key: ' + match_key)
    return match_key


def determine_prob_of_stat_from_records(ok_val, player_stat_records, season_part, stat_name, condition='all', year=2023):
    
    print('\n===Determine Prob of Stat: ' + str(ok_val) + ' ' + stat_name + '===\n')
    #print('player_stat_records: ' + str(player_stat_records))
    prob_of_stat = 0

    year_stat_records = player_stat_records[condition][year]
    if season_part in year_stat_records.keys():
        records = year_stat_records[season_part][stat_name]
        #print('records: ' + str(records))
        record = records[ok_val]
        #print('record: ' + str(record))

        prob_of_stat = generator.generate_prob_stat_reached(record)         

    print('prob_of_stat: ' + str(prob_of_stat))
    return prob_of_stat

def determine_ok_val_prob(dict, ok_val, player_stat_records, season_part, stat_name):

    print('\n===Determine Postseason Prob for OK Value: ' + str(ok_val) + ' ' + stat_name + '===\n')

    ok_val_post_val_key = determine_matching_key(dict, ok_val) #'post prob val'

    ok_val_post_prob_key = '' #re.sub('val','',ok_val_post_val_key).strip()

    ok_val_post_prob = 0

    #player_stat_records: {'all': {2023: {'regular': {'pts': 
    if ok_val_post_val_key == '':
        # we can find post prob from stat records
        ok_val_post_prob = determine_prob_of_stat_from_records(ok_val, player_stat_records, season_part, stat_name)
        ok_val_post_prob = round(ok_val_post_prob * 100)
    else:
        ok_val_post_prob_key = re.sub('val','',ok_val_post_val_key).strip()

        if ok_val_post_prob_key in dict.keys():
            ok_val_post_prob = dict[ok_val_post_prob_key]

    
    print('ok_val_post_prob: ' + str(ok_val_post_prob))
    return ok_val_post_prob


def determine_ok_val_margin(dict, ok_val, player_stat_dict, stat_name, margin_type='min'):

    print('\n===Determine Postseason Margin for OK Value: ' + str(ok_val) + ' ' + stat_name + '===\n')

    ok_val_post_val_key = determine_matching_key(dict, ok_val) #'post prob val'

    ok_val_post_margin_key = '' #re.sub('val','',ok_val_post_val_key).strip()

    ok_val_post_margin = 0

    #player_stat_records: {'all': {2023: {'regular': {'pts': 
    if ok_val_post_val_key == '':
        # we can find post prob from stat records
        ok_val_post_margin = generator.generate_margin(ok_val, player_stat_dict, margin_type)
    else:
        margin_key = margin_type + ' margin'
        ok_val_post_margin_key = re.sub('prob val',margin_key,ok_val_post_val_key).strip()
        print('ok_val_post_margin_key: ' + str(ok_val_post_margin_key))

        if ok_val_post_margin_key in dict.keys():
            ok_val_post_margin = dict[ok_val_post_margin_key]

    print('ok_val_post_margin: ' + str(ok_val_post_margin))
    return ok_val_post_margin
