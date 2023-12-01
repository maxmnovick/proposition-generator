# reader.py
# functions for a reader

import re
import pandas as pd # read html results from webpage
from urllib.request import Request, urlopen # request website, open webpage given req
from urllib.error import URLError
import time # halt code to retry website request
import requests # track timeout error
from bs4 import BeautifulSoup # read html from webpage
from tabulate import tabulate # display output, which for the reader is input files to confirm and review their contents

from selenium import webdriver # need to read html5 webpages
from webdriver_manager.chrome import ChromeDriverManager # need to access dynamic webpages
import time # need to read dynamic webpages
from selenium.webdriver.chrome.options import Options # block ads

import csv
import json # we need projected lines table to be json so we can refer to player when analyzing stats

import determiner # determine played season before reading webpage to avoid exception/error
import isolator # isolate_player_game_data to read data from file

import math # round up to nearest integer while reading

import writer # write to file so we can check if data exists in local file so we can read from file

from datetime import datetime # get current year so we can get current teams

import copy # deepcopy game logs json so we can add to it before writing to file without losing data

# get data from a file and format into a list (same as generator version of this fcn but more general)
# input such as Game Data - All Games
# or Game Log - All Players
# header = keep first row (confusing need to change)
def extract_data(data_type, input_type='', extension='csv', header=False):
	
	#print('\n===Extract Data===\n')

	catalog_filename = "data/" + data_type.title() + "." + extension
	if input_type != '':
		input_type = re.sub('/','_',input_type)
		catalog_filename = "data/" + data_type.title() + " - " + input_type.title() + "." + extension
	#print("catalog_filename: " + catalog_filename)
	

	lines = []
	data = []
	all_data = []

	try: 

		with open(catalog_filename, encoding="UTF8") as catalog_file:

			current_line = ""
			for catalog_info in catalog_file:
				current_line = catalog_info.strip()
				#print("current_line: " + str(current_line))
				lines.append(current_line)

			catalog_file.close()

		# skip header line
		read_lines = lines
		if not header: # file includes header but we do not want header
			read_lines = lines[1:]

		for line in read_lines:
			#print("line: " + str(line))
			if len(line) > 0:
				if extension == "csv":
					data = line.split(",")
				else:
					data = line.split("\t")
			all_data.append(data)

	except Exception as e:
		print("Error opening file. ")
	
	#print("all_data: " + str(all_data))
	return all_data

# read website given url, timeout in seconds, and max. no. retries before going to next step
def read_website(url, timeout=10, max_retries=3):
	print('\n===Read Website===\n')
	print('url: ' + url)
	#soup = BeautifulSoup() # return blank soup if request fails

	retries = 0

	while retries < max_retries:
		try:
			#make the request
			req = Request(url, headers={
				'User-Agent': 'Mozilla/5.0',
			})
			page = urlopen(req, timeout=timeout)

			#data = page.read()

			soup = BeautifulSoup(page, features='lxml')

			print("Request successful.")

			return soup

		except URLError as e:
			if isinstance(e.reason, TimeoutError):
				# If a timeout occurs, wait for 10 seconds and then retry\
				retries += 1
				print(f"Timeout error occurred. Retrying {retries}/{max_retries}...")
				time.sleep(10)
				
			else:
                # If the error is different than a timeout, raise it
				#raise
				retries += 1
				print(f"URLError error occurred. Retrying {retries}/{max_retries}...")
				time.sleep(10)
			
		except Exception as e:
            # If any other exception occurs, raise it
			#raise
			retries += 1
			print(f"Exception error occurred. Retrying {retries}/{max_retries}...")
			time.sleep(10)
		except:
			print(f"server not found?")
			#raise
			retries += 1
			time.sleep(10)

	print("Maximum retries reached.")
	return None

		

# get game espn id from google
def read_game_espn_id(game_key, existing_game_ids_dict={}):

	print('\n===Read Game ESPN ID======\n')

	espn_id = ''

	# den uta oct 19 nba espn box score
	# if we always use format 'away home m/d/y' then we can check to see if key exists and get game id from local file
	# search_key = away_abbrev + ' ' + home_abbrev + ' ' + date
	# print('search_key: ' + search_key)

	if game_key in existing_game_ids_dict.keys():
		espn_id = existing_game_ids_dict[game_key]

	else:

		#try:
			
		search_string = game_key.replace(' ', '+') + '+nba+espn+box+score'
		print('search_string: ' + search_string)
		
		site = 'https://www.google.com/search?q=' + search_string
		print('site: ' + site)

		soup = read_website(site, timeout=10, max_retries=3)

			# req = Request(site, headers={
			# 	'User-Agent': 'Mozilla/5.0',
			# })

			# page = urlopen(req) # open webpage given request

			# soup = BeautifulSoup(page, features="lxml")
		if soup is not None:
			links_with_text = [] # id is in first link with text

			for a in soup.find_all('a', href=True):
				if a.text and a['href'].startswith('/url?'):
					links_with_text.append(a['href'])

			links_with_id_text = [x for x in links_with_text if 'gameId/' in x]

			espn_id_link = links_with_id_text[0] # string starting with player id

			espn_id = re.findall(r'\d+', espn_id_link)[0]

			print('Success', espn_id, game_key)

			data = [[game_key, espn_id]]
			filepath = 'data/Game Ids.csv'
			write_param = 'a' # append ids to file
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

		#except Exception as e:
			#print('Error', espn_id, game_key, e)

	print("game_espn_id: " + espn_id)
	return espn_id


# get player espn id from google
# or from file if already saved
# player_id_dict = {player:id,..}
def read_player_espn_id(player_name, existing_espn_ids_dict={}):

	print('\n===Read Player ESPN ID: ' + player_name.title() + '===\n')

	espn_id = ''

	player_name = player_name.lower() # ensure lowercase for matching

	if player_name in existing_espn_ids_dict.keys():
		espn_id = existing_espn_ids_dict[player_name]

	else:

		#try:
		player_search_term = player_name
		if player_name.lower() == 'nikola jovic': # confused with nikola jokic
			player_search_term += ' miami heat'

		site = 'https://www.google.com/search?q=' + player_search_term.replace(' ', '+') + '+nba+espn+gamelog'
		# https://www.google.com/search?q=john+collins+game+log
		#site = 'https://www.google.com/search?q=help'
		#print('site: ' + site)

		soup = read_website(site, timeout=10, max_retries=3)
		#print('soup: ' + str(soup))

		# req = Request(site, headers={
		# 	'User-Agent': 'Mozilla/5.0',
		# })

		# page = urlopen(req) # open webpage given request

		# soup = BeautifulSoup(page, features="lxml")
		# print('soup: ' + str(soup))

		if soup is not None:

			links_with_text = [] # id is in first link with text

			for a in soup.find_all('a', href=True):
				if a.text and a['href'].startswith('/url?'):
					links_with_text.append(a['href'])

			links_with_id_text = [x for x in links_with_text if 'id/' in x]

			espn_id_link = links_with_id_text[0] # string starting with player id

			espn_id = re.findall(r'\d+', espn_id_link)[0]

			print('Success', espn_id, player_name.title())



			data = [[player_name, espn_id]]
			filepath = 'data/Player Ids.csv'
			write_param = 'a' # append ids to file
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

		#except Exception as e:
			#print('Error', espn_id, player_name.title(), e)

		

	print("espn_id: " + espn_id)
	return espn_id

def read_all_player_espn_ids(player_names, player_of_interest=''):
	print('\n===Read All Player ESPN IDs===\n')
	
	espn_ids_dict = {}

	if player_of_interest != '':
		player_names = [player_of_interest.lower()]


	# see if id saved in file
	data_type = 'player ids'
	player_ids = extract_data(data_type, header=True)
	existing_espn_ids_dict = {}
	for row in player_ids:
		#print('row: ' + str(row))
		player_name = row[0].lower()
		player_id = row[1]

		existing_espn_ids_dict[player_name] = player_id
	#print('existing_espn_ids_dict: ' + str(existing_espn_ids_dict))

	for name in player_names:
		name = name.lower()
		espn_id = read_player_espn_id(name, existing_espn_ids_dict)
		espn_ids_dict[name] = espn_id



	return espn_ids_dict


# all_players_in_games_dict = {game:{away:[],home:[]}}
# we will convert away home to teammates opponents given current player of interest
def read_players_in_box_score(game_box_scores_dict):
	print("\n===Read Players in Box Score===\n")

	players_in_box_score_dict = {'away':[],'home':[]}

	#team_idx = 0
	for loc, players in players_in_box_score_dict.items():
		team_box_score = game_box_scores_dict[loc]
		print('team_box_score:\n' + str(team_box_score))
		#home_team_box_score = game_box_scores[1]

		players = team_box_score[0].drop(0).to_list()
		print('players:\n' + str(players))

		players_in_box_score_dict[loc] = players



		#team_idx += 1


	print('players_in_box_score_dict: ' + str(players_in_box_score_dict))
	return players_in_box_score_dict


# get game box scores from espn.com
# 1 box score per team
def read_game_box_scores(game_key, game_id='', game_url=''):
	print("\n===Read Game Box Score: " + game_key.upper() + "===\n")

	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)


	game_box_scores = [] # players, stats for away team and home team

	game_box_scores_dict = {} # {away:df, home:df}

	# get espn player id from google so we can get url
	if game_url == '':
		if game_id == '':
			game_id = read_game_espn_id(game_key)
		#season_year = 2023
		game_url = 'https://www.espn.com/nba/boxscore/_/gameId/' + game_id #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
		print("game_url: " + game_url)

	#try:

	html_results = read_web_data(game_url) #pd.read_html(game_url)
	print("html_results: " + str(html_results))


	len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table

	game_data = game_key.split()
	away_team = game_data[0]
	home_team = game_data[1]

	team_loc = 'away'

	for order in range(len_html_results):
		print("order: " + str(order))

		html_result_df = html_results[order]
		print('html_result: ' + str(html_result_df))
		print("no. columns: " + str(len(html_result_df.columns.tolist())))

		# very first html result is the game summary quarter by quarter score and total score


		# first get players, which is html result with row 0 = 'starters'
		# for idx, row in html_result.rows:
		# 	print('row: ' + str(row))
		print('row 0 loc: ' + str(html_result_df.loc[[0]]))
		# order is always away-home
		
		if re.search('starters', str(html_result_df.loc[[0]])): # locate first row
			# init format
			# 0           starters
			# 1       B. Ingram SF
			# 2        H. Jones SF
			# 3   J. Valanciunas C
			# 4     C. McCollum SG
			# 5   T. Murphy III SG
			# 6              bench
			# 7    L. Nance Jr. PF
			# 8     N. Marshall SF
			# 9   J. Richardson SG
			# 10      D. Daniels G
			# 11      G. Temple SF
			# 12  W. Hernangomez C
			# 13        J. Hayes C
			# 14   K. Lewis Jr. PG
			# 15      D. Seabron G
			# 16              team,  
			print('init player_name_df:\n' + str(html_result_df))

			# remove, starters, bench, and team rows
			# locate first column
			# wait to remove rows until name and stats dfs concated
			player_name_df = html_result_df #[(html_result_df.loc[:,0] != 'starters') & (html_result_df.loc[:,0] != 'bench') & (html_result_df.loc[:,0] != 'team')]
			print('player_name_df:\n' + str(player_name_df))

			# remove players who did not play
			# info about dnp is in next html result so use order+1

			player_stats_df = html_results[order+1]
			print('player_stats_df:\n' + str(player_stats_df))

			#player_box_score_df.columns.values[0] = 'MIN'
			# for col in player_box_score_df.columns:
			# 	print(col)

			player_box_score_df = pd.concat([player_name_df,player_stats_df], axis=1, sort=False, ignore_index=True)
			print('player_box_score_df:\n' + str(player_box_score_df))


			idxs = player_box_score_df.loc[player_box_score_df[1] == 'DNP-COACH\'S DECISION'].index
			print('idxs: ' + str(idxs))
			final_idx = 0 # if 0 then no dnps so find 'team' label
			if len(idxs) > 0:
				final_idx = idxs[0] # Int64Index([], dtype='int64')
			else:
				idxs = player_box_score_df.loc[player_box_score_df[0] == 'team'].index
				if len(idxs) > 0:
					final_idx = idxs[0]
				else:
					print('Warning: player_box_score_df missing team line so check format!')
			print('final_idx: ' + str(final_idx))

			if final_idx != 0:
				player_box_score_df = player_box_score_df.drop(player_box_score_df.index[final_idx:])
				print('player_box_score_df:\n' + str(player_box_score_df))
			else:
				print('Warning: player_box_score_df final_idx ' + str(final_idx) + ' = 0!')

			# if no dnp then remove lines after 'team'
			player_box_score_df = player_box_score_df.dropna(axis=1)
			print('player_box_score_df:\n' + str(player_box_score_df))

			player_box_score_df = player_box_score_df.drop(player_box_score_df.index[6]).reset_index()
			print('player_box_score_df:\n' + str(player_box_score_df))

			player_box_score_df['Game'] = game_key
			print('player_box_score_df:\n' + str(player_box_score_df))

			# get the index of the first row with dnp
			# player_minutes_df = player_box_score_df[0]
			# print('player_minutes_df:\n' + str(player_minutes_df))
			# player_minutes_df = player_box_score_df.loc[:,0]
			# print('player_minutes_df:\n' + str(player_minutes_df))
			# player_minutes_df = player_box_score_df[player_box_score_df[0] != 'DNP-COACH\'S DECISION']
			# print('player_minutes_df:\n' + str(player_minutes_df))


			# player_minutes_df = player_minutes_df[player_minutes_df[0].startswith('DNP')]
			# print('player_minutes_df:\n' + str(player_minutes_df))
			# player_minutes_df = player_minutes_df['MIN']
			# print('player_minutes_df:\n' + str(player_minutes_df))


			# player_minutes_df.columns = ['MIN']
			# player_minutes_df = player_minutes_df[~player_minutes_df['MIN'].str.startswith('DNP')]
			
			# print('player_box_score_df col 1:\n' + str(player_minutes_df))
			# player_minutes_df.columns = ['MIN']
			# player_minutes_df = player_minutes_df['MIN']
			# print('player_minutes_df:\n' + str(player_minutes_df))
			

			# indexDNP = player_box_score_df[(~player_box_score_df.loc[:,0].str.startswith('DNP')) & (player_box_score_df.loc[:,0] != 'NaN')].index
			# print('indexDNP: ' + str(indexDNP))


			# there is no key row so we must look at values in rows to determine keys
			# init_player_column = html_result_df.loc['starters']
			# print('init_player_column: ' + str(init_player_column))

			# final format
			# 1       B. Ingram SF
			# 2        H. Jones SF
			# 3   J. Valanciunas C
			# 4     C. McCollum SG
			# 5   T. Murphy III SG
			# 7    L. Nance Jr. PF
			# 8     N. Marshall SF
			# 9   J. Richardson SG
			# 10      D. Daniels G
			# 11      G. Temple SF
			# 12  W. Hernangomez C
			# 13        J. Hayes C
			# 14   K. Lewis Jr. PG
			# 15      D. Seabron G



			game_box_scores.append(player_box_score_df)


			game_box_scores_dict[team_loc] = player_box_score_df
			#print("game_box_scores_dict: " + str(game_box_scores_dict))


			team_loc = 'home' # order is always away-home for this espn page ref



			


	# 	if len(html_result_df.columns.tolist()) == 15:

	# 		part_of_box_score = html_result_df

	# 		# look at the formatting to figure out how to separate table and elements in table
	# 		# if len_html_results - 2 == order:
	# 		# 	part_of_season['Type'] = 'Preseason'

	# 		# else:
	# 		# 	if len(part_of_season[(part_of_season['OPP'].str.contains('GAME'))]) > 0:
	# 		# 		part_of_season['Type'] = 'Postseason'
	# 		# 	else:
	# 		# 		part_of_season['Type'] = 'Regular'

	# 		parts_of_box_score.append(part_of_box_score)

	# 	else:
	# 		print("Warning: table does not have 15 columns so it is not valid box score.")
	# 		pass

	# print('parts_of_box_score: ' + str(parts_of_box_score))

	# box_score_df = pd.DataFrame()

	# if len(parts_of_box_score) > 0:

	# 	box_score_df = pd.concat(parts_of_box_score, sort=False, ignore_index=True)

	# 	#player_game_log_df = player_game_log_df[(player_game_log_df['OPP'].str.startswith('@')) | (player_game_log_df['OPP'].str.startswith('vs'))].reset_index(drop=True)

	# 	box_score_df['Season'] = str(season_year-1) + '-' + str(season_year-2000)

	# 	box_score_df['Game'] = game_key

		#box_score_df = box_score_df.set_index(['Game', 'Season', 'Team']).reset_index()

		# Successful FG Attempts
		# box_score_df['FG_SA'] = box_score_df['FG'].str.split('-').str[0]
		# # All FG Attempts
		# box_score_df['FG_A'] = box_score_df['FG'].str.split('-').str[1]

		# Successful 3P Attempts
		# box_score_df['3PT_SA'] = box_score_df['3PT'].str.split('-').str[0]
		# # All 3P Attempts
		# box_score_df['3PT_A'] = box_score_df['3PT'].str.split('-').str[1]

		# Successful FT Attempts
		# box_score_df['FT_SA'] = box_score_df['FT'].str.split('-').str[0]
		# # All FT Attempts
		# box_score_df['FT_A'] = box_score_df['FT'].str.split('-').str[1]
		
		
		# box_score_df[
		# 	['MIN', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS', 'FG_SA', 'FG_A', '3PT_SA', '3PT_A']

		# 	] = box_score_df[

		# 		['MIN', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS', 'FG_SA', 'FG_A', '3PT_SA', '3PT_A']

		# 		].astype(float)

	

	# except Exception as e:
	# 	print("Error reading game log " + str(e))
	# 	pass

	
	print("game_box_scores_dict: " + str(game_box_scores_dict))
	return game_box_scores_dict # can return this df directly or first arrange into list but seems simpler and more intuitive to keep df so we can access elements by keyword

# read tables in websites with pandas pd dataframes
def read_web_data(url, timeout=10, max_retries=3):
	print('\n===Read Web Data===\n')
	# display tables in readable format
	pd.set_option('display.max_columns', None)

	retries = 0
	while retries < max_retries:
		try:
			#response = requests.get(url, timeout=timeout)
			#response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

			#list_of_dataframes = pd.read_html(url)
			headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
			r = requests.get(url, headers=headers, timeout=timeout)
			#r.raise_for_status(headers=headers)
			#print('r: ' + str(r))
			c = r.content
			#print('c: ' + str(c))
			list_of_dataframes = pd.read_html(c)

			print("Request successful, data retrieved.\n")
			#print('list_of_dataframes: ' + str(list_of_dataframes))

			return list_of_dataframes

		except requests.exceptions.Timeout:
			print(f"Timeout error occurred. Retrying {retries + 1}/{max_retries}...")
			retries += 1
			time.sleep(10)
		except requests.exceptions.HTTPError as e:
			print(f"HTTP error occurred: {e}")
			#raise
			retries += 1
			time.sleep(10)
		except requests.exceptions.RequestException as e:
			print(f"Request failed: {e}")
			#raise
			retries += 1
			time.sleep(10)
		except Exception as e:
            # If any other exception occurs, retry
			#raise
			retries += 1
			print(f"Exception error occurred. Retrying {retries}/{max_retries}...")
			time.sleep(10)
		except:
			print(f"server not found?")
			#raise
			retries += 1
			time.sleep(10)

	print("Maximum retries reached.")
	return None


# get game log from espn.com
def read_player_season_log(player_name, season_year=2024, player_url='', player_id='', all_game_logs={}, todays_date=datetime.today().strftime('%m-%d-%y'), player_game_logs={}):
	print('\n===Read Player Game Log: ' + player_name.title() + ', ' + str(season_year) + '===\n')

	player_game_log_df = pd.DataFrame()
	player_game_log_dict = {}

	# much faster to save in one file
	# print('Try to find local game logs for ' + str(season_year))
	# all_game_logs = read_json(all_logs_filename)
	#print('all_game_logs:\n' + str(all_game_logs))
	try:
		if player_name in all_game_logs.keys() and str(season_year) in all_game_logs[player_name].keys():
			
			player_game_log_dict = all_game_logs[player_name][str(season_year)]
			#print('local player_game_log_dict:\n' + str(player_game_log_dict))
			print('found local game log for player ' + player_name + ' in ALL game logs')
		elif str(season_year) in player_game_logs.keys():
			player_game_log_dict = player_game_logs[str(season_year)]
			#print('local player_game_log_dict:\n' + str(player_game_log_dict))
			print('found local game log for player ' + player_name + ' in PLAYER game logs')
		else:
			# if player in logs but season not then maybe we only ran for 1 season so check if season is on web


		# see if saved locally
		#todays_date = datetime.today().strftime('%m-%d-%y') 
		# data/lamelo ball 2024 game log 11-08-23.csv
		# log_filename = 'data/game logs/' + player_name + ' ' + str(season_year) + ' game log ' + todays_date + '.csv'
		# print('log_filename: ' + log_filename)
		
		# try:
		# 	print('Try to find local game log for ' + player_name.title())
		# 	player_game_log_df = pd.read_csv(log_filename)
		# 	#print('local player_game_log_df:\n' + str(player_game_log_df))

		# except:


			print('Could not find local game log, so read from web.')
			# get espn player id from google so we can get url
			if player_url == '':
				if player_id == '':
					player_id = read_player_espn_id(player_name)
				#season_year = 2023
				player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
				#print("player_url: " + player_url)

			#player_game_log = []
			#dfs = pd.read_html(player_url)
			#print(f'Total tables: {len(dfs)}')

			#try:

			# returns list_of_dataframes
			html_results = read_web_data(player_url) #pd.read_html(player_url)
			#print("html_results: " + str(html_results))

			if html_results is not None:
				print('found html results while reading season log')

				parts_of_season = [] # pre season, regular season, post season

				len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table
				#print('len_html_results: ' + str(len_html_results))
				for order in range(len_html_results):
					#print("order: " + str(order))

					# see if we can find header to differntiate preseason and regseason
					#print('html_results[order]: ' + str(html_results[order]))

					if len(html_results[order].columns.tolist()) == 17:

						part_of_season = html_results[order]
						#print('part_of_season:\n' + str(part_of_season))

						# look at the formatting to figure out how to separate table and elements in table
						if len_html_results - 2 == order and len_html_results > 4: # 3 or more should work but check if invalid for any players bc 4 or more means they did not play preseason but does not account for if they played postseason
							part_of_season['Type'] = 'Preseason'

						else:
							# last row of postseason section has 'finals' in it, eg quarter finals, semi finals, finals
							last_cell = part_of_season.iloc[-1,0]
							#print('last_cell: ' + str(last_cell))
							if re.search('final',last_cell.lower()) or re.search('play-in',last_cell.lower()):
								part_of_season['Type'] = 'Postseason'
							# if len(part_of_season[(part_of_season['OPP'].str.contains('GAME'))]) > 0:
							# 	part_of_season['Type'] = 'Postseason'
							# elif re.search('play-in',last_cell.lower()):
							# 	part_of_season['Type'] = 'Playin'
							else:
								part_of_season['Type'] = 'Regular'

						parts_of_season.append(part_of_season)

					else:
						#print("Warning: table does not have 17 columns so it is not valid game log.")
						pass

				

				if len(parts_of_season) > 0:

					player_game_log_df = pd.concat(parts_of_season, sort=False, ignore_index=True)

					player_game_log_df = player_game_log_df[(player_game_log_df['OPP'].str.startswith('@')) | (player_game_log_df['OPP'].str.startswith('vs'))].reset_index(drop=True)

					player_game_log_df['Season'] = str(season_year-1) + '-' + str(season_year-2000)

					player_game_log_df['Player'] = player_name

					player_game_log_df = player_game_log_df.set_index(['Player', 'Season', 'Type']).reset_index()

					# Successful 3P Attempts
					player_game_log_df['3PT_SA'] = player_game_log_df['3PT'].str.split('-').str[0]

					# All 3P Attempts
					player_game_log_df['3PT_A'] = player_game_log_df['3PT'].str.split('-').str[1]
					player_game_log_df[
						['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']

						] = player_game_log_df[

							['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']

							].astype(float)

				# display player game log in readable format
				#pd.set_option('display.max_columns', 100)
				pd.set_option('display.max_columns', None)
				#print("player_game_log_df:\n" + str(player_game_log_df))

				# save each game log to a file
				# filename: <player> <season> game log <todays d/m/y>
				# we put todays date so we can see if already read today
				# bc if not read today then read new 
				# index=False: means that the index of the DataFrame will not be included in the CSV file.
				
				#player_game_log_df.to_csv(log_filename, index=False)
				# append game log to existing days file if possible
				# if first run of the day, then write new file with days date
				# see other instances of write to json
				# all_game_logs = all_game_logs
				# writer.write_json_to_file(all_game_logs, all_l)

				init_player_game_log_dict = player_game_log_df.to_dict()
				# change id ints to strings to compare to json
				#print('change keys to strings')
				for field, field_dict in init_player_game_log_dict.items():
					player_game_log_dict[field] = {}
					for key, val in field_dict.items():
						player_game_log_dict[field][str(key)] = val

			# except Exception as e:
			# 	print("Error reading game log " + str(e))
			# 	pass

		# if we want to format table in 1 window we can get df elements in lists and then print lists in table
		# header_row = ['Date', 'OPP', 'Result', 'MIN', 'FG', 'FG%', '3P', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS']

		# table = [header_row]
		# for row in player_game_data:
		# 	table.append(row)
	except:
		print('Warning: Error getting game log!')

	# print("\n===" + player_name + "===\n")
	# print(tabulate(table))
	#print(player_name + " player_game_log returned")# + str(player_game_log_df))
	#print('player_game_log_df:\n' + str(player_game_log_df))
	#print('player_game_log_dict: ' + str(player_game_log_dict))
	return player_game_log_dict#player_game_log_df # can return this df directly or first arrange into list but seems simpler and more intuitive to keep df so we can access elements by keyword

# here we decide default season year, so make input variable parameter
def read_player_season_logs(player_name, read_x_seasons=1, player_espn_ids={}, season_year=2024, all_game_logs={}, todays_date=datetime.today().strftime('%m-%d-%y') ):
	print('\n===Read Player Season Logs: ' + player_name.title() + '===\n')

	# see if saved season logs for player
	player_game_logs_filename = 'data/game logs/' + player_name + ' game logs ' + todays_date + '.json'
	print('player_game_logs_filename: ' + player_game_logs_filename)
	print('Try to find local game logs for ' + player_name + '.')
	init_player_game_logs = read_json(player_game_logs_filename)
	#print('init_player_game_logs: ' + str(init_player_game_logs))
	# need to copy init game logs bc this run may not have all players but we dont want to remove other players
	player_game_logs = copy.deepcopy(init_player_game_logs) # season logs for a player

	player_name = player_name.lower()

	#player_game_logs = []
	player_season_logs = {}

	player_espn_id = ''
	if len(player_espn_ids.keys()) == 0:
		player_espn_id = read_player_espn_id(player_name)
	else:
		player_espn_id = player_espn_ids[player_name]

	if player_espn_id == '':
		print('Warning: player_espn_id blank while trying to get player url! ')
		
	#season_year = 2023 # here we decide default season year, so make input variable parameter
	player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_espn_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
	
	if read_x_seasons == 0:
		while determiner.determine_played_season(player_url, player_name, season_year, all_game_logs, player_game_logs):

			#print("player_url: " + player_url)
			game_log_dict = read_player_season_log(player_name, season_year, player_url, all_game_logs=all_game_logs, todays_date=todays_date, player_game_logs=player_game_logs)
			player_season_logs[str(season_year)] = game_log_dict
			# if not game_log_df.empty:
			# 	player_game_logs.append(game_log_df)
			# 	player_season_logs[season_year] = game_log_df.to_dict()

			# if not read_all_seasons:
			# 	break

			player_game_logs[str(season_year)] = game_log_dict # includes all players saved before not just players input this run

			season_year -= 1
			player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_espn_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])

	for season_idx in range(read_x_seasons):
		if determiner.determine_played_season(player_url, player_name, season_year, all_game_logs, player_game_logs):

			#print("player_url: " + player_url)
			game_log_dict = read_player_season_log(player_name, season_year, player_url, all_game_logs=all_game_logs, todays_date=todays_date, player_game_logs=player_game_logs)
			player_season_logs[str(season_year)] = game_log_dict
			# if not game_log_df.empty:
			# 	player_game_logs.append(game_log_df)
			# 	player_season_logs[season_year] = game_log_df.to_dict()

			player_game_logs[str(season_year)] = game_log_dict # includes all players saved before not just players input this run

			season_year -= 1
			player_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_espn_id + '/type/nba/year/' + str(season_year)
		# after we reach season they did not play it is possible they may have played before but taken break
		# so keep checking prev 5 years before breaking
		# else:
		# 	break

	#print('init_player_game_logs: ' + str(init_player_game_logs))
	#print('final_player_game_logs: ' + str(player_game_logs))
	if not player_game_logs == init_player_game_logs:
		print('player ' + player_name + ' game logs changed so write to file for player ' + player_name)
		writer.write_json_to_file(player_game_logs, player_game_logs_filename, 'w')

	#print('player_season_logs: ' + str(player_season_logs))
	return player_season_logs#player_game_logs

def read_all_players_season_logs(player_names, read_x_seasons=1, player_espn_ids={}, season_year=2024):

	print('\n===Read All Players Season Logs===\n')

	all_players_season_logs = {}

	# much faster to save in one file
	# but too large for single variable in memory?
	# todays_date = datetime.today().strftime('%m-%d-%y') 
	# all_logs_filename = 'data/game logs/all game logs ' + todays_date + '.json'
	# print('all_logs_filename: ' + all_logs_filename)
	# print('Try to find local game logs for all games.')
	# init_all_game_logs = read_json(all_logs_filename)
	# print('init_all_game_logs: ' + str(init_all_game_logs))
	# need to copy init game logs bc this run may not have all players but we dont want to remove other players
	all_game_logs = {}#copy.deepcopy(init_all_game_logs)
	

	for player_name in player_names:
		# {player:season:log}
		players_season_logs = read_player_season_logs(player_name, read_x_seasons, player_espn_ids, season_year, all_game_logs)
		all_players_season_logs[player_name] = players_season_logs

		# if log is already in file no need to overwrite but the output will be the same as all game logs so it makes no difference
		all_game_logs[player_name] = players_season_logs # {player:season:log}

		# write for each player is if error interrupts it can resume where it left off
		# if all game logs unchanged then no need to write to file
		#init_all_game_logs: {'bruce brown': {'2023': {'Player': {'0': 
		#final_all_game_logs: {'bruce brown': {2023: {'Player': {'0': 'br
		
		# print('init_all_game_logs: ' + str(init_all_game_logs))
		# print('final_all_game_logs: ' + str(all_game_logs))
		# if not all_game_logs == init_all_game_logs:
		# 	print('all game logs changed so write to file for player ' + player_name)
		# 	writer.write_json_to_file(all_game_logs, all_logs_filename, 'w')
	
	#print('all_players_season_logs: ' + str(all_players_season_logs))
	return all_players_season_logs


# get team season schedule from espn.com
def read_team_season_schedule(team_name, season_year=2024, team_url='', team_id=''):
	print("\n===Read Team " + team_name.title() + ", Season " + str(season_year) + " Schedule===\n")

	# get espn player id from google so we can get url
	if team_url == '':
		if team_id == '':
			team_id = read_team_espn_id(team_name)
		#season_year = 2023
		team_url = 'https://www.espn.com/nba/player/gamelog/_/id/' + team_id + '/type/nba/year/' + str(season_year) #.format(df_Players_Drafted_2000.loc[INDEX, 'ESPN_GAMELOG_ID'])
		print("team_url: " + team_url)

	player_game_log = []

	#dfs = pd.read_html(player_url)
	#print(f'Total tables: {len(dfs)}')

	#try:

	html_results = read_web_data(team_url) #pd.read_html(team_url)
	#print("html_results: " + str(html_results))

	parts_of_season = [] # pre season, regular season, post season

	len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table

	for order in range(len_html_results):
		#print("order: " + str(order))

		if len(html_results[order].columns.tolist()) == 17:

			part_of_season = html_results[order]

			# look at the formatting to figure out how to separate table and elements in table
			if len_html_results - 2 == order:
				part_of_season['Type'] = 'Preseason'

			else:
				if len(part_of_season[(part_of_season['OPP'].str.contains('GAME'))]) > 0:
					part_of_season['Type'] = 'Postseason'
				else:
					part_of_season['Type'] = 'Regular'

			parts_of_season.append(part_of_season)

		else:
			print("Warning: table does not have 17 columns so it is not valid game log.")
			pass

	player_game_log_df = pd.DataFrame()

	if len(parts_of_season) > 0:

		player_game_log_df = pd.concat(parts_of_season, sort=False, ignore_index=True)

		player_game_log_df = player_game_log_df[(player_game_log_df['OPP'].str.startswith('@')) | (player_game_log_df['OPP'].str.startswith('vs'))].reset_index(drop=True)

		player_game_log_df['Season'] = str(season_year-1) + '-' + str(season_year-2000)

		player_game_log_df['Player'] = player_name

		player_game_log_df = player_game_log_df.set_index(['Player', 'Season', 'Type']).reset_index()

		# Successful 3P Attempts
		player_game_log_df['3PT_SA'] = player_game_log_df['3PT'].str.split('-').str[0]

		# All 3P Attempts
		player_game_log_df['3PT_A'] = player_game_log_df['3PT'].str.split('-').str[1]
		player_game_log_df[
			['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']

			] = player_game_log_df[

				['MIN', 'FG%', '3P%', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS', '3PT_SA', '3PT_A']

				].astype(float)

	# display player game log in readable format
	#pd.set_option('display.max_columns', 100)
	pd.set_option('display.max_columns', None)
	print("player_game_log_df:\n" + str(player_game_log_df))

	# except Exception as e:
	# 	print("Error reading game log " + str(e))
	# 	pass

	# if we want to format table in 1 window we can get df elements in lists and then print lists in table
	# header_row = ['Date', 'OPP', 'Result', 'MIN', 'FG', 'FG%', '3P', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS']

	# table = [header_row]
	# for row in player_game_data:
	# 	table.append(row)

	# print("\n===" + player_name + "===\n")
	# print(tabulate(table))
	#print("player_game_log: " + str(player_game_log))
	return player_game_log_df # can return this df directly or first arrange into list but seems simpler and more intuitive to keep df so we can access elements by keyword



# get player position from espn game log page bc we already have urls for each player
def read_player_position(player_name, player_id, season_year=2024, existing_player_positions_dict={}):
	print("\n===Read Player Position: " + player_name.title() + "===\n")
	position = ''

	# if not given exisiting positions see if local file saved
	if len(existing_player_positions_dict.keys()) == 0:
		data_type = 'player positions'
		player_positions = extract_data(data_type, header=True)
		
		for row in player_positions:
			#print('row: ' + str(row))
			player_name = row[0]
			player_position = row[1]

			existing_player_positions_dict[player_name] = player_position
		#print('existing_player_positions_dict: ' + str(existing_player_positions_dict))

	if player_name in existing_player_positions_dict.keys():
		position = existing_player_positions_dict[player_name]

	else:

		#try:
			
		site = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id + '/type/nba/year/' + str(season_year)

		soup = read_website(site, timeout=10, max_retries=3)

		# req = Request(site, headers={
		# 	'User-Agent': 'Mozilla/5.0',
		# })

		# page = urlopen(req) # open webpage given request

		# soup = BeautifulSoup(page, features="lxml")
		if soup is not None:
			# find last element of ul with class PlayerHeader__Team_Info
			position = str(list(soup.find("ul", {"class": "PlayerHeader__Team_Info"}).descendants)[-1])
			#print("position_elementn:\n" + str(position_element))

			if len(position) > 2: # use abbrev
				pos_abbrev = ''
				words = position.split()
				for word in words:
					pos_abbrev += word[0].lower()

				if pos_abbrev == 'f': # some just say forward so make it small forward but actually better to use height to determine bc if over 6'6 then pf maybe?
					pos_abbrev = 'sf'
				elif pos_abbrev == 'g':
					pos_abbrev = 'sg'
				position = pos_abbrev

			# links_with_text = [] # id is in first link with text

			# for a in soup.find_all('a', href=True):
			# 	if a.text and a['href'].startswith('/url?'):
			# 		links_with_text.append(a['href'])

			# links_with_id_text = [x for x in links_with_text if 'id/' in x]

			# espn_id_link = links_with_id_text[0] # string starting with player id

			# position = re.findall(r'\d+', espn_id_link)[0]

			print('Success', position.upper(), player_name.title())


			data = [[player_name, position]]
			filepath = 'data/Player Positions.csv'
			write_param = 'a' # append ids to file
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet
		else:
			print('Warning: website has no soup!')
		#except Exception as e:
			#print('Error', position.upper(), player_name.title())

	print("position: " + position)
	return position

def read_all_players_positions(player_espn_ids_dict, season_year=2024):
	#print("\n===Read All Players Positions===\n")
	players_positions_dict = {}

	# see if position saved in file
	data_type = 'player positions'
	player_positions = extract_data(data_type, header=True)
	existing_player_positions_dict = {}
	for row in player_positions:
		print('row: ' + str(row))
		player_name = row[0]
		player_position = row[1]

		existing_player_positions_dict[player_name] = player_position
	print('existing_player_positions_dict: ' + str(existing_player_positions_dict))

	for name, id in player_espn_ids_dict.items():
		pos = read_player_position(name, id, season_year, existing_player_positions_dict)
		players_positions_dict[name] = pos

	#print("players_positions_dict: " + str(players_positions_dict))
	return players_positions_dict



# return team abbrev lowercase bc used as key
def read_team_from_internet(player_name, player_id, read_new_teams=False):
	print("\n===Read Team from Internet: " + player_name.title() + "===\n")

	team = ''

	# get team from internet
	# this method only works for current team bc format of page
	season_year = datetime.today().year

	#try:
		
	site = 'https://www.espn.com/nba/player/gamelog/_/id/' + player_id + '/type/nba/year/' + str(season_year)

	soup = read_website(site, timeout=10, max_retries=3)

		# req = Request(site, headers={
		# 	'User-Agent': 'Mozilla/5.0',
		# })

		# page = urlopen(req) # open webpage given request

		# soup = BeautifulSoup(page, features="lxml")
	if soup is not None:
		# find last element of ul with class PlayerHeader__Team_Info
		team = str(list(soup.find("ul", {"class": "PlayerHeader__Team_Info"}).descendants)[0]).strip()#.split('<')[0]#.split('>')[-1]
		#print("team_element:\n" + str(team))
		
		#<li class="truncate min-w-0"><a class="AnchorLink clr-black" data-clubhouse-uid="s:40~l:46~t:21" href="https://www.espn.com/nba/team/_/name/phx/phoenix-suns" tabindex="0">Phoenix Suns</a></li>

		team = re.split('</',str(team))[0]
		team = re.split('>',team)[-1]
		#print("team: " + team)
		team = determiner.determine_team_abbrev(team)

		print('Success', team.upper(), player_name.title())

		# overwrite for the first player if read new teams true and then append all after
		# if read_new_teams: # make blank initially and then append all names after that
		# 	# overwrite file
		# 	write_param = 'w'

		# we are reading from the internet so we are definitely going to write the data to a file no matter what so we can access it later
		# the question is if we are going to append or overwrite
		# if we are going to overwrite then we must wait till we have all teams so we only overwrite first entry and append all after
		# if not all new teams then simply append this player's team to the file
		if not read_new_teams:
			write_param = 'a' # append ids to file unless read new teams
			data = [[player_name, team]]
			filepath = 'data/Player Teams.csv'
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

	#except Exception as e:
		#print('Error', team.upper(), player_name.title(), e)

	print("team from internet: " + team)
	return team

# get player team from espn game log page bc we already have urls for each player
# we are using it get the team the player currently plays on
# but we can also use it to get the team a player previously played on but that uses a very different method from a different source so assume season year is current season
# read_new_teams false by default bc if it does not find existing team it will find on web
# the difference is read new teams will always read new teams even if team already saved locally and unchanged
# user will set input var after trades or aquisitions
# later program will get news and decide off that instead of requiring user input
def read_player_team(player_name, player_id, existing_player_teams_dict={}, read_new_teams=False):
	print("\n===Read Player Team: " + player_name.title() + "===\n")
	team = '' # team abbrev lowercase bc used as key

	# read_new_teams can be determined by date bc date of trade deadline, start of season and check if any other trade deadlines


	# if not given exisiting teams see if local file saved
	if len(existing_player_teams_dict.keys()) == 0:
		data_type = 'player teams'
		player_teams = extract_data(data_type, header=True)
		
		for row in player_teams:
			#print('row: ' + str(row))
			existing_player_name = row[0]
			existing_player_team = row[1]

			existing_player_teams_dict[existing_player_name] = existing_player_team
		print('existing_player_teams_dict: ' + str(existing_player_teams_dict))


	# if read new teams, then read from internet for all
	# if not read new teams, still read teams from internet for players not saved
	if read_new_teams:
		team = read_team_from_internet(player_name, player_id, read_new_teams)
	else:
		if player_name in existing_player_teams_dict.keys():
			team = existing_player_teams_dict[player_name]
		else:
			team = read_team_from_internet(player_name, player_id)

	
	print("final team: " + team)
	return team

# for all given players, read their teams
def read_all_players_teams(player_espn_ids_dict, read_new_teams=True):
	print("\n===Read All Players Teams===\n")
	players_teams_dict = {}

	
	# if not read new teams,
	# see if team saved in file
	# bc if read new teams then we will create new file with today's date in name
	existing_player_teams_dict = {}
	if not read_new_teams:
		data_type = 'player teams'
		# if we are creating new file get todays date to format filename 
		# player teams - m/d/y.csv
		input_type = datetime.today().strftime('%m/%d/%y') 
		player_teams = extract_data(data_type, header=True)
		
		for row in player_teams:
			#print('row: ' + str(row))
			player_name = row[0]
			player_team = row[1]

			existing_player_teams_dict[player_name] = player_team
		#print('existing_player_teams_dict: ' + str(existing_player_teams_dict))

	for name, id in player_espn_ids_dict.items():
		team = read_player_team(name, id, existing_player_teams_dict, read_new_teams)
		players_teams_dict[name] = team

	# if read new teams for all players then we can overwrite the file completely removing all old teams bc we cannot assume any player is on the same team as they were before
	if read_new_teams:
		# overwrite for the first one and then append all following
		p_idx = 0
		for player_name, player_team in players_teams_dict.items():

			write_param = 'a'
			if p_idx == 0:
				write_param = 'w'

			data = [[player_name, team]]
			filepath = 'data/Player Teams.csv'
			writer.write_data_to_file(data, filepath, write_param) # write to file so we can check if data already exists to determine how we want to read the data and if we need to request from internet

			p_idx += 1

	print("players_teams_dict: " + str(players_teams_dict))
	return players_teams_dict

# read team players from internet
# read team roster from internet
def read_roster_from_internet(team_abbrev, read_new_teams=False):
	print('\n===Read Roster from Internet===\n')
	raw_roster = []
	roster = []

	

	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	# get team name from abbrev
	team_name = determiner.determine_team_name(team_abbrev)
	team_name = re.sub(r'\s+','-',team_name)

	irregular_abbrevs = {'bro':'bkn', 'okl':'okc', 'nop':'no', 'nor':'no', 'pho':'phx', 'was':'wsh', 'uth': 'utah', 'uta': 'utah' }
	if team_abbrev in irregular_abbrevs.keys():
		team_abbrev = irregular_abbrevs[team_abbrev]

	#try:

	roster_url = 'https://www.espn.com/nba/team/roster/_/name/' + team_abbrev + '/' + team_name #den/denver-nuggets
	print("roster_url: " + str(roster_url))

	html_results = read_web_data(roster_url) #pd.read_html(roster_url)
	#print("html_results: " + str(html_results))

	len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table
	#print("len_html_results: " + str(len_html_results))

	for order in range(len_html_results):
		#print("order: " + str(order))

		html_result_df = html_results[order]
		#print('html_result: ' + str(html_result_df))
		#print("no. columns: " + str(len(html_result_df.columns.tolist())))

		# very first html result is the game summary quarter by quarter score and total score


		# first get players, which is html result with row 0 = 'starters'
		# for idx, row in html_result.rows:
		# 	print('row: ' + str(row))
		#print('row 0 loc: ' + str(html_result_df.loc[[0]]))

		if order == 0:
			raw_roster = html_result_df.loc[:,'Name'].tolist()


	# remove non word characters
	for player in raw_roster:
		player_name = re.sub(r'\.|\d','',player)
		player_name = re.sub(r'-',' ',player_name)
		roster.append(player_name.lower())

	# we are reading from the internet so we are definitely going to write the data to a file no matter what so we can access it later
	# the question is if we are going to append or overwrite
	# if we are going to overwrite then we must wait till we have all teams so we only overwrite first entry and append all after
	# if not all new teams then simply append this player's team to the file
	# for json we must add new key,val to existing dict and overwrite file
	# if not read_new_teams:
	# 	data = {}
	# 	data[team_abbrev] = roster
	# 	write_param = 'a'
	# 	filepath = 'data/Teams-Players.json'
	# 	writer.write_json_to_file(data, filepath, write_param)

	#except Exception as e:
		#print('Error', str(roster), team_abbrev.upper(), e)

	print('roster: ' + str(roster))
	return roster

# valid for json files
def read_json(key_type):
	print('\n===Read JSON===\n')
	keys_filename = key_type
	if not re.search('\.',key_type): # filename
		key_type = re.sub('\s+','-',key_type)
		keys_filename = "data/" + key_type.title() + ".json"
	print("keys_filename: " + keys_filename)

	lines = [] # capture each line in the document
	keys = {}
	try:
		with open(keys_filename, encoding="UTF8") as keys_file:
			line = ''
			for key_info in keys_file:
				line = key_info.strip()
				lines.append(line)

			keys_file.close()

			# combine into 1 line
		condensed_json = ''
		for line in lines:
			#print('line: ' + str(line))
			condensed_json += line

		#print("Condensed JSON: " + condensed_json)

		# parse condensed_json
		keys = json.loads(condensed_json)
	except:
		print("Warning: no json file: " + key_type)

	
	#print("keys: " + str(keys))
	return keys

# read team roster to get team players
def read_team_roster(team_abbrev, existing_teams_players_dict={}, read_new_teams=True):
	#print('\n===Read Team Roster: ' + team_abbrev)
	roster = []

	if read_new_teams:
		roster = read_roster_from_internet(team_abbrev, read_new_teams)
	else:
		#if not given existing teams players, see if local file saved
		if len(existing_teams_players_dict) == 0:
			data_type = 'teams players'
			existing_teams_players_dict = read_json(data_type)

		if team_abbrev in existing_teams_players_dict.keys():
			roster = existing_teams_players_dict[team_abbrev]
		else:
			roster = read_roster_from_internet(team_abbrev)
			existing_teams_players_dict[team_abbrev] = roster
			write_param = 'w'
			filepath = 'data/Teams-Players.json'
			writer.write_json_to_file(existing_teams_players_dict, filepath, write_param)

	
	print('roster: ' + str(roster))
	return roster



# read list of player names given teams so we dont have to type all names
# save in same player teams file used when directly given player names and found team on player page
# bc the data is the same from both sources, unless we set read new teams=true
# problem is we need to see if team has been fully saved before
# to see if we want to read from internet
# to solve this make new json file for team rosters/players
# where if roster added then we know fully saved unless we request new teams after trades
# in theory we could keep 1 file and check that x no. players saved but number might be inconsistent (eg some teams have 18, others 17)
# if we have the rosters file then it can replace the player teams file
def read_teams_players(teams, read_new_teams=True):
	print("\n===Read Teams Players===\n")
	print('teams: ' + str(teams))
	teams_players_dict = {}
	players_names = [] # return single list of all players. later could separate by team but really we want to rank all players by prob

	# if not read new teams,
	# see if team saved in file
	# bc if read new teams, then we will create new file with today's date in name
	existing_teams_players_dict = {}
	if not read_new_teams:
		data_type = 'teams players'
		existing_teams_players_dict = read_json(data_type) # returns data dict

		# for team, players in all_teams_players.items():
		# 	existing_teams_players_dict[team] = players
	for game_teams in teams:
		for team in game_teams:
			# go to roster page espn
			team_players = read_team_roster(team, existing_teams_players_dict, read_new_teams)
			teams_players_dict[team] = team_players

			players_names.extend(team_players)

	# if read new teams for all players then we can overwrite the file completely removing all old teams bc we cannot assume any player is on the same team as they were before
	if read_new_teams:
		# overwrite bc new teams json single line
		filepath = 'data/Teams-Players.json'
		write_param = 'w'
		writer.write_json_to_file(teams_players_dict, filepath, write_param)
		
	print('players_names: ' + str(players_names))
	return players_names
        


# show matchup data against each position so we can see which position has easiest matchup
# matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]
def read_matchup_data(source_url):

	print("\n===Read Matchup Data===\n")

	matchup_data = [] # matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]

	# swish source which uses html 5 is default for now bc we need to define df outside if statement
	
	matchup_df = pd.DataFrame()
	
	

	if re.search('fantasypro|hashtag|swish',source_url): # swish analytics uses html5
		

		#chop = webdriver.ChromeOptions()
		#chop.add_extension('adblock_5_4_1_0.crx')
		#driver = webdriver.Chrome(chrome_options = chop)

		driver = webdriver.Chrome(ChromeDriverManager().install())
		driver.implicitly_wait(3)

		driver.get(source_url) # Open the URL on a google chrome window
		
		#time.sleep(3) # As this is a dynamic html web-page, wait for 3 seconds for everything to be loaded

		# if needed, Accept the cookies policy
		# driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
		#time.sleep(3)

		# click on the pagination elements to select not only the page 1 but all pages
		#position_btn_path = '/html/body/div' #main/div/div/div/div/div/ul/li[1]/a'
		#driver.find_element('xpath', '/html/body/div').click()

		#position_btn = (driver.find_element('xpath', '/html/body/div').text())
		#print("position_btn: " + str(position_btn))
		#driver.find_element_by_xpath(position_btn_path).click()
		#time.sleep(3)

		#ad = driver.find_element('id', 'div-gpt-ad-1556117653136-0').find_element('xpath','div/iframe')
		#print("ad: " + ad.get_attribute('outerHTML'))

		# click x on advertisement so we can click btns below it
		#ad_close = driver.find_element('xpath','//*[@id="closebutton"]')
		#print("ad_close: " + ad_close.get_attribute('outerHTML'))
		#ad_close.click(); #Close Ad
		#time.sleep(3)

		if re.search('fantasypro',source_url):
			# close ad
			if driver.find_elements("id", "google_ads_iframe_/2705664/fantasypros_interstitial_1_0"):
				driver.switch_to.frame(driver.find_element("id", "google_ads_iframe_/2705664/fantasypros_interstitial_1_0"))
				#l = driver.find_element('xpath', 'html/body/div')
				l = driver.find_element('id', 'closebutton')
				h1= driver.execute_script("return arguments[0].outerHTML;",l)
				print("h1: " + str(h1))
				# driver.switch_to.frame(driver.find_element("tag name", "iframe"))
				# l = driver.find_element('xpath', 'html/body')
				# h2= driver.execute_script("return arguments[0].innerHTML;",l)
				# print("h2: " + str(h2))
				l.click(); #Close Ad

				driver.switch_to.default_content()

			# get the defense matchup table as text

			#defense_table_path = 'html/body/' #main/div/div/div/div[6]/data-table/tbody'
			#matchup_table = driver.find_element('id', 'data-table')
			#print("matchup_table: " + str(matchup_table))

			# not all sources have all team defense and not needed yet so add later
			# position_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[1]/a')
			# print("position_btn: " + position_btn.get_attribute('innerHTML'))
			# position_btn.click()
			# #time.sleep(3)

			# team_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			# print("team_matchup_df\n" + str(team_matchup_df))


			pg_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[2]/a')
			print("pg_btn: " + pg_btn.get_attribute('innerHTML'))
			pg_btn.click()
			#time.sleep(3)

			pg_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			print("pg_matchup_df\n" + str(pg_matchup_df))


			sg_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[3]/a')
			print("sg_btn: " + sg_btn.get_attribute('innerHTML'))
			sg_btn.click()
			#time.sleep(3)

			sg_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			print("sg_matchup_df\n" + str(sg_matchup_df))


			sf_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[4]/a')
			print("sf_btn: " + sf_btn.get_attribute('innerHTML'))
			sf_btn.click()
			#time.sleep(3)

			sf_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			print("sf_matchup_df\n" + str(sf_matchup_df))


			pf_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[5]/a')
			print("pf_btn: " + pf_btn.get_attribute('innerHTML'))
			pf_btn.click()
			#time.sleep(3)

			pf_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			print("pf_matchup_df\n" + str(pf_matchup_df))


			c_btn = driver.find_element('class name','main-content').find_element('xpath','div/div[4]/div/ul/li[6]/a')
			print("c_btn: " + c_btn.get_attribute('innerHTML'))
			c_btn.click()
			#time.sleep(3)

			c_matchup_df=pd.read_html(driver.find_element('id', "data-table").get_attribute('outerHTML'))[0]
			print("c_matchup_df\n" + str(c_matchup_df))

			matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]

		elif re.search('hashtag',source_url):
			print("Pull data from hastag bball.")
			all_matchup_df=pd.read_html(driver.find_element('id', "ContentPlaceHolder1_GridView1").get_attribute('outerHTML'))[0]
			print("all_matchup_df\n" + str(all_matchup_df))

			pg_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'PG']
			print("pg_matchup_df\n" + str(pg_matchup_df))
			sg_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'SG']
			print("sg_matchup_df\n" + str(sg_matchup_df))
			sf_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'SF']
			print("sf_matchup_df\n" + str(sf_matchup_df))
			pf_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'PF']
			print("pf_matchup_df\n" + str(pf_matchup_df))
			c_matchup_df = all_matchup_df[all_matchup_df['Sort: Position'] == 'C']
			print("c_matchup_df\n" + str(c_matchup_df))

			# they do not give all team defense so we must calculate or remove from other sources if not needed. it is needed bc good to know overall defense in positionless bball
			# get list of all team names and then make subset tables by team
			# team_names = all_matchup_df['Sort: Team'].unique
			# print("team_names: " + str(team_names))
			# for team_name in team_names:
			# 	team_matchup_df = all_matchup_df[all_matchup_df['Sort: Team'] == team_name]
			# 	print("team_matchup_df\n" + str(team_matchup_df))

			# 	pts_mean = team_matchup_df['Sort: PTS'].mean()

			matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]
			
		elif re.search('swish',source_url):
			print("Pull data from Swish.")

			time.sleep(2) #needs to load

			pg_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[2]/a')
			print("pg_btn: " + pg_btn.get_attribute('innerHTML'))
			pg_btn.click()
			

			pg_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			print("pg_matchup_df\n" + str(pg_matchup_df))


			sg_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[3]/a')
			print("sg_btn: " + sg_btn.get_attribute('innerHTML'))
			sg_btn.click()
			
			sg_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			print("sg_matchup_df\n" + str(sg_matchup_df))


			sf_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[4]/a')
			print("sf_btn: " + sf_btn.get_attribute('innerHTML'))
			sf_btn.click()
			
			sf_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			print("sf_matchup_df\n" + str(sf_matchup_df))


			pf_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[5]/a')
			print("pf_btn: " + pf_btn.get_attribute('innerHTML'))
			pf_btn.click()
			
			pf_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			print("pf_matchup_df\n" + str(pf_matchup_df))


			c_btn = driver.find_element('xpath','html/body/div[3]/div[2]/div[2]/div/ul/li[6]/a')
			print("c_btn: " + c_btn.get_attribute('innerHTML'))
			c_btn.click()
			
			c_matchup_df=pd.read_html(driver.find_element('id', "stat-table").get_attribute('outerHTML'))[0]
			print("c_matchup_df\n" + str(c_matchup_df))

			matchup_data = [pg_matchup_df, sg_matchup_df, sf_matchup_df, pf_matchup_df, c_matchup_df]
			
		else:
			team_matchup_df=pd.read_html(driver.find_element('id', "ContentPlaceHolder1_GridView1").get_attribute('outerHTML'))[0]
			print("team_matchup_df\n" + str(team_matchup_df))

		# close the google chrome window
		driver.quit()

		
	else:
		# first get the html as a pandas dataframe format
		html_results = read_web_data(source_url) #pd.read_html(source_url)
		print("html_results: " + str(html_results))

	return matchup_data

# sources disagree so we need to find consensus or just be aware of the risk of inaccurate data
# show all 5 sources so we can see the conflicts and therefore risk of inaccurate data
def read_all_matchup_data(matchup_data_sources):

	print("\n===Read All Matchup Data===\n")

	all_matchup_data = []

	for source in matchup_data_sources:
		
		source_matchup_data = read_matchup_data(source)
		all_matchup_data.append(source_matchup_data)

	return all_matchup_data

# def read_projected_lines(date):
# 	lines = []

# 	return lines


def extract_json_from_file(data_type, input_type, extension='csv'):
	catalog_filename = "data/" + data_type.title() + " - " + input_type.title() + "." + extension

	# create a dictionary
	data_dict = {}
	
	lines = []
	#data = []
	all_data = []

	try: 

		with open(catalog_filename, encoding="UTF8") as catalog_file:

			csvReader  =csv.DictReader(catalog_file)

			# Convert each row into a dictionary
			# and add it to data
			for rows in csvReader:
				
				# Assuming a column named 'No' to
				# be the primary key
				key = rows['Name']
				data_dict[key] = rows

		# 	current_line = ""
		# 	for catalog_info in catalog_file:
		# 		current_line = catalog_info.strip()
		# 		lines.append(current_line)

		# 	catalog_file.close()

		# # skip header line
		# read_lines = lines
		# if not header:
		# 	read_lines = lines[1:]

		# for line in read_lines:
		# 	if len(line) > 0:
		# 		if extension == "csv":
		# 			data = line.split(",")
		# 		else:
		# 			data = line.split("\t")
		# 	all_data.append(data)

	except Exception as e:
		print("Error opening file. ")
	
	print("data_dict: " + str(data_dict))


	return data_dict

# use when reading table cell with multiple values representing different fields inconveniently placed in same cell, 
# eg score,rank in same cell
def format_stat_val(col_val):
	stat_val = 0.0
	if re.search('\\s',str(col_val)): # eg '20.3 15' for 'avg rank'
		stat_val = float(re.split('\\s',col_val)[0])
	else:
		stat_val = float(col_val)

	return stat_val

def read_season_log_from_file(data_type, player_name, ext):
	
	all_pts = []
	all_rebs = []
	all_asts = []
	all_winning_scores = []
	all_losing_scores = []
	all_minutes = []
	all_fgms = []
	all_fgas = []
	all_fg_rates = []
	all_threes_made = []
	all_threes_attempts = []
	all_three_rates = []
	all_ftms = []
	all_ftas = []
	all_ft_rates = []
	all_bs = []
	all_ss = []
	all_fs = []
	all_tos = []

	all_stats = []
    
	player_data = extract_data(data_type, player_name, ext)
	# first row is headers, next are games with monthly averages bt each mth

	#desired_field = 'points'
	#desired_field_idx = determiner.determine_field_idx(desired_field)
	date_idx = 0
	opp_idx = 1
	result_idx = 2
	minutes_idx = 3
	fg_idx = 4
	fg_rate_idx = 5
	three_idx = 6
	three_rate_idx = 7
	ft_idx = 8
	ft_rate_idx = 9
	r_idx = 10
	a_idx = 11
	b_idx = 12
	s_idx = 13
	f_idx = 14
	to_idx = 15
	p_idx = 16

	# isolate games from lebron data
	# exclude headers and monthly averages
	player_games_data = isolator.isolate_player_game_data(player_data, player_name)

	

	if len(player_games_data) > 0:
		for game in player_games_data:
			pts = int(game[p_idx])
			rebs = int(game[r_idx])
			asts = int(game[a_idx])

			results = game[result_idx]
			#print("results: " + results)
			results_data = re.split('\\s+', results)
			#print("results_data: " + str(results_data))
			score_data = results_data[1].split('-')
			#print("score_data: " + str(score_data))
			winning_score = int(score_data[0])
			losing_score = int(score_data[1])

			minutes = int(game[minutes_idx])

			fgs = game[fg_idx]
			fg_data = fgs.split('-')
			fgm = int(fg_data[0])
			fga = int(fg_data[1])
			fg_rate = round(float(game[fg_rate_idx]), 1)

			threes = game[three_idx]
			threes_data = threes.split('-')
			#print("threes_data: " + str(threes_data))
			threes_made = int(threes_data[0])
			threes_attempts = int(threes_data[1])
			three_rate = round(float(game[three_rate_idx]), 1)

			fts = game[ft_idx]
			ft_data = fts.split('-')
			ftm = int(ft_data[0])
			fta = int(ft_data[1])
			ft_rate = round(float(game[ft_rate_idx]), 1)

			bs = int(game[b_idx])
			ss = int(game[s_idx])
			fs = int(game[f_idx])
			tos = int(game[to_idx])

			all_pts.append(pts)
			all_rebs.append(rebs)
			all_asts.append(asts)

			all_winning_scores.append(winning_score)
			all_losing_scores.append(losing_score)

			all_minutes.append(minutes)
			all_fgms.append(fgm)
			all_fgas.append(fga)
			all_fg_rates.append(fg_rate)
			all_threes_made.append(threes_made)
			all_threes_attempts.append(threes_attempts)
			all_three_rates.append(three_rate)
			all_ftms.append(ftm)
			all_ftas.append(fta)
			all_ft_rates.append(ft_rate)
			all_bs.append(bs)
			all_ss.append(ss)
			all_fs.append(fs)
			all_tos.append(tos)

			all_stats = [all_pts,all_rebs,all_asts,all_winning_scores,all_losing_scores,all_minutes,all_fgms,all_fgas,all_fg_rates,all_threes_made,all_threes_attempts,all_three_rates,all_ftms,all_ftas,all_ft_rates,all_bs,all_ss,all_fs,all_tos]

	else:
		print("Warning: No player games data!")

	return all_stats

def read_projected_lines(raw_projected_lines, all_player_teams, player_of_interest=''):
	print('\n===Read Projected Lines===\n')
	#print('raw_projected_lines: ' + str(raw_projected_lines))

	# convert raw projected lines to projected lines
	header_row = ['name', 'pts', 'reb', 'ast', '3pm', 'blk', 'stl', 'to','loc','opp']

	all_game_lines_dicts = {} # each stat separately
	# split columns in raw projected lines so we can loop thru each stat separately
	pts_projected_lines = []
	reb_projected_lines = []
	ast_projected_lines = []
	three_projected_lines = []
	blk_projected_lines = []
	stl_projected_lines = []
	to_projected_lines = []

	for line in raw_projected_lines:
		print('raw line: ' + str(line))
		pts_line = line[:3]
		pts_projected_lines.append(line[:3])
		reb_projected_lines.append(line[3:6])
		ast_projected_lines.append(line[6:9])
		three_projected_lines.append(line[9:12])
		blk_projected_lines.append(line[12:15])
		stl_projected_lines.append(line[15:18])
		to_projected_lines.append(line[18:21])

	separate_projected_lines = { 'pts':pts_projected_lines, 'reb':reb_projected_lines, 'ast':ast_projected_lines, 'three':three_projected_lines, 'blk':blk_projected_lines, 'stl':stl_projected_lines, 'to':to_projected_lines }
	print('separate_projected_lines: ' + str(separate_projected_lines))
	
	all_player_lines = [header_row]

	#game_lines_dict = {} # { 'PHO SunsatDAL MavericksTODAY 1:10PM': [['Chris Paul', 'O 9.5  +105', 'U 9.5  −135'],..]}

	# raw_projected_lines: [['PHO SunsatDAL MavericksTODAY 1:10PM'], ['PLAYER', 'OVER', 'UNDER'], ['Chris Paul', 'O 9.5  +105', 'U 9.5  −135']]
	# assign player lines to a game so we can get loc and opp from game info key
	for stat_name, projected_lines in separate_projected_lines.items():
		if len(projected_lines[0]) > 0:
			print('stat_name: ' + stat_name)
			game_key = ''
			game_lines_dict = {} # { 'PHO SunsatDAL MavericksTODAY 1:10PM': [['Chris Paul', 'O 9.5  +105', 'U 9.5  −135'],..]}
		
			for row in projected_lines:
				# loop thru rows until we see header. then make header key in dict and add next rows to list of values until next header
				# if first item = 'PLAYER' skip bc not needed header
				# then if first 3 letters are uppercase we know it is team matchup header w/ needed info
				player_initials = ['og','cj','pj','rj','tj','jt','jd']
				print('row: ' + str(row))
				if len(row) > 0:
					first_element_wo_punctuation = re.sub('\'|\.','',row[0])
					#print('first_element_wo_punctuation: ' + str(first_element_wo_punctuation))
					if first_element_wo_punctuation != 'PLAYER' and first_element_wo_punctuation.lower() != 'na':
						if first_element_wo_punctuation[:3].isupper() and first_element_wo_punctuation[:2].lower() not in player_initials:# and not re.search('\'',row[0][:3]): # if apostrophe then player name like D'Angelo, not header
							#print('found header: ' + str(row) + ', ' + row[0][:3])
							game_key = row[0]
							# if not game_key in game_lines_dict.keys():
							#     game_lines_dict[game_key] = []

						else:
							#print('found player line: ' + str(row))
							if game_key in game_lines_dict.keys():
								game_lines_dict[game_key].append(row)
							else:
								game_lines_dict[game_key] = [row]

			#print("game_lines_dict: " + str(game_lines_dict))
			all_game_lines_dicts[stat_name] = game_lines_dict

	print("all_game_lines_dicts: " + str(all_game_lines_dicts))

	# for now set unavailable stats=1, until we have basic fcns working
	reb = 1
	ast = 1
	three = 1
	blk = 1
	stl = 1
	to = 1

	all_player_lines_dicts = {} # {'player name':{pts:0,reb:0,..}}

	# game info = 'PHO SunsatDAL MavericksTODAY 1:10PM'
	for stat_name, game_lines_dict in all_game_lines_dicts.items():

		print('stat_name: ' + stat_name)

		for game_info, game_lines in game_lines_dict.items():
			print('game_info: ' + str(game_info))
			teams = game_info.split('at') 
			# make exception for MIA Heatat bc heat ends with at
			away_team = teams[0]
			home_team_idx = 1
			if away_team.lower() == 'mia he':
				away_team = 'MIA Heat'
				home_team_idx = 2
			home_team = teams[home_team_idx]
			print("away_team: " + str(away_team))
			print("home_team: " + str(home_team))

			irregular_abbrevs = {'bro':'bkn', 'okl':'okc', 'nor':'nop', 'pho':'phx', 'was':'wsh', 'uth': 'uta', 'utah': 'uta' } # for these match the first 3 letters of team name instead

			away_abbrev = away_team.split()[0].lower()
			if len(away_abbrev) == 2:
				away_abbrev = away_abbrev + away_team.split()[1][0].lower()

			if away_abbrev in irregular_abbrevs.keys():
				#print("irregular abbrev: " + team_abbrev)
				away_abbrev = irregular_abbrevs[away_abbrev]

			home_abbrev = home_team.split()[0].lower()
			if len(home_abbrev) == 2:
				home_abbrev = home_abbrev + home_team.split()[1][0].lower()
			if home_abbrev in irregular_abbrevs.keys():
				#print("irregular abbrev: " + team_abbrev)
				home_abbrev = irregular_abbrevs[home_abbrev]

			print("away_abbrev: " + str(away_abbrev))
			print("home_abbrev: " + str(home_abbrev))

			for raw_player_line in game_lines:

				# each stat has 3 columns pts, reb, ast,...
				# but not all players have all stats so the lines do not line up
				# so we must divide each stat and sort by player name

				player_name = raw_player_line[0].lower()
				print("player_name: " + str(player_name))
				#if player_name in all_player_teams.keys():

				

				if player_name != '':
					if player_name in all_player_teams.keys():
						player_team_abbrev = all_player_teams[player_name]
						print("player_team_abbrev: " + str(player_team_abbrev))
						# determine opponent from game info by eliminating player's team from list of 2 teams
						loc = 'home'
						opp = away_abbrev
						if player_team_abbrev == away_abbrev:
							loc = 'away'
							opp = home_abbrev
						# only add loc and opp once per player per game
						if not player_name in all_player_lines_dicts.keys():
							all_player_lines_dicts[player_name] = { 'loc': loc, 'opp': opp }
						else:
							all_player_lines_dicts[player_name]['loc'] = loc 
							all_player_lines_dicts[player_name]['opp'] = opp

						

						stat = math.ceil(float(raw_player_line[1].split()[1])) # O 10.5 +100
						#print("pts: " + str(pts))
						#reb = math.ceil(float(raw_player_line[4].split()[1])) # O 10.5 +100

						all_player_lines_dicts[player_name][stat_name] = stat
					else:
						print('Warning: No player name ' + player_name + ' not in teams dict while reading projected lines!')
						print("raw_player_line: " + str(raw_player_line))
				else:
					print('Warning: No player name while reading projected lines!')
					print("raw_player_line: " + str(raw_player_line))


	print("all_player_lines_dicts: " + str(all_player_lines_dicts))

	for player_name, player_lines in all_player_lines_dicts.items():
		#header_row = ['Name', 'PTS', 'REB', 'AST', '3PT', 'BLK', 'STL', 'TO','LOC','OPP']
		pts = 10
		if 'pts' in player_lines.keys():
			pts = player_lines['pts']
		reb = 2
		if 'reb' in player_lines.keys():
			reb = player_lines['reb']
		ast = 2
		if 'ast' in player_lines.keys():
			ast = player_lines['ast']
		three = 1
		if 'three' in player_lines.keys():
			three = player_lines['three']
		blk = 1
		if 'blk' in player_lines.keys():
			blk = player_lines['blk']
		stl = 1
		if 'stl' in player_lines.keys():
			stl = player_lines['stl']
		to = 1
		if 'to' in player_lines.keys():
			to = player_lines['to']
		
		loc = player_lines['loc']
		opp = player_lines['opp']
		player_line = [player_name, pts, reb, ast, three, blk, stl, to, loc, opp]

		# if certain players of interest, keep only their lines for analysis
		if player_of_interest == '': # get all players
			all_player_lines.append(player_line)
		elif player_of_interest == player_name:
			all_player_lines.append(player_line)
		
	print("all_player_lines:\n" + tabulate(all_player_lines))
	return all_player_lines

# we may be given irregular abbrev or full name
# so change to uniform regular ream abbrev for comparison
def read_team_abbrev(team_str):

	abbrev = re.sub('@|vs','',team_str.lower())
	irregular_abbrevs = {'no':'nop', 'ny':'nyk', 'sa': 'sas', 'gs':'gsw' } # for these match the first 3 letters of team name instead
	if abbrev in irregular_abbrevs.keys():
		abbrev = irregular_abbrevs[abbrev]
	#print('abbrev: ' + abbrev)
	return abbrev

# find teammates and opponents for each game played by each player
# all_players_in_games_dict = {player:{game:{teammates:[],opponents:[]}}}
def read_all_players_in_games(all_player_season_logs_dict, player_teams, season_year=2024):
	
	print('\n===Read All Players in Games===\n')
	
	all_players_in_games_dict = {} # {player:{game:{teammates:[],opponents:[]}}}
	
	#season_year = 2023
	
	for player_name, player_season_logs in all_player_season_logs_dict.items():

		print('player_name: ' + player_name)
		
		team_abbrev = player_teams[player_name]
		
		print('team_abbrev: ' + team_abbrev)

        
        # see if game id saved in file
        # check for each player bc we add new games for each player and they may overlap
		
		data_type = 'game ids'
		game_ids = extract_data(data_type, header=True)
		existing_game_ids_dict = {}
		for row in game_ids:
			print('row: ' + str(row))
			game_key = row[0]
			game_id = row[1]
			
			existing_game_ids_dict[game_key] = game_id
			
		print('existing_game_ids_dict: ' + str(existing_game_ids_dict))
	
		for player_season_log in player_season_logs.values():

			player_season_log_df = pd.DataFrame(player_season_log)
			
			player_reg_season_log = determiner.determine_regular_season_games(player_season_log_df)
			
			players_in_game = [] # unordered list of all players in game independent of team
			players_in_game_dict = {} # {teammates:[],opponents:[]}
			
			for game_idx, row in player_reg_season_log.iterrows():
				
				print('\n===Game ' + str(game_idx) + '===')
                # season year-1 for first half of season oct-dec bc we say season year is end of season
				
				init_game_date_string = player_reg_season_log.loc[game_idx, 'Date'].lower().split()[1] # 'wed 2/15'[1]='2/15'
				game_mth = init_game_date_string.split('/')[0]
				final_season_year = str(season_year)
				if int(game_mth) in range(10,13):
					final_season_year = str(season_year - 1)
					
				date_str = player_reg_season_log.loc[game_idx, 'Date'] + '/' + str(final_season_year) # dow m/d/y
				date_data = date_str.split()
				date = date_data[1] # m/d/y
				print('date: ' + date)
				opp_str = player_reg_season_log.loc[game_idx, 'OPP']
				opp_abbrev = read_team_abbrev(opp_str) #re.sub('@|vs','',opp_str)

				# irregular_abbrevs = {'no':'nop', 'ny':'nyk', 'sa': 'sas', 'gs':'gsw' } # for these match the first 3 letters of team name instead
				# if opp_abbrev in irregular_abbrevs.keys():
				# 	opp_abbrev = irregular_abbrevs[opp_abbrev]
				print('opp_abbrev: ' + opp_abbrev)

                # if we always use format 'away home m/d/y' then we can check to see if key exists and get game id from local file
				away_abbrev = opp_abbrev
				home_abbrev = team_abbrev
				player_loc = 'home' # for box score players in game sort by teammates
				if re.search('@',opp_str):
					away_abbrev = team_abbrev
					home_abbrev = opp_abbrev
					player_loc = 'away'
					
				game_key = away_abbrev + ' ' + home_abbrev + ' ' + date
				print('game_key: ' + game_key)
		
				# if we have not yet added this game to the dict
				# then get game box score players
				if not game_key in all_players_in_games_dict.keys():
                
					game_espn_id = read_game_espn_id(game_key, existing_game_ids_dict)


					# get the game box score page using the game id
					# get the box score from the page in a df
					game_box_scores_dict = read_game_box_scores(game_key, game_espn_id)



					# players_in_game_dict = {'teammates':[],'opponents':[]}
					# for team_loc, players in players_in_box_score_dict.items():
					#     # if player is away set teammates as such
					#     if team_loc == player_loc:
					#         players_in_game_dict['teammates'] = players
					#     else:
					#         players_in_game_dict['opponents'] = players
				
					#players_in_game_dict = {'away':[],'home':[]}

					
					# opp_loc = 'away'
					# players_in_game_dict['teammates'] = players_in_box_score_dict[player_loc]
					# players_in_game_dict['opponents'] = players_in_box_score_dict[opp_loc]
					# if player_loc == 'away':
					#     opp_loc = 'home'
					#     players_in_game_dict['opponents'] = players_in_box_score_dict[opp_loc]

					#print('players_in_game_dict: ' + str(players_in_game_dict))

					# if not player_name in all_players_in_games_dict.keys():
					#     all_players_in_games_dict[player_name] = {}
					#all_players_in_games_dict[player_name][game_key] = players_in_game_dict
					# 


					# given box scores for each team, return lists of teammates and opponents
					players_in_box_score_dict = read_players_in_box_score(game_box_scores_dict)
					
					
					all_players_in_games_dict[game_key] = players_in_box_score_dict
				
				# test first game
				# if game_idx == 0:
				# 	break
		
			season_year -= 1
		
	print('all_players_in_games_dict: ' + str(all_players_in_games_dict))
	return all_players_in_games_dict

# all_players_in_games_dict = { game key: {away:[],home:[]}}
# use player team to get teammates from box score
def read_all_teammates(player_name, all_players_in_games_dict, player_team=''):

	print('\n===Read All Teammates for ' + player_name + '===\n')

	all_teammates = []

	if player_team == '':
		player_team = read_player_team(player_name)

	if len(all_players_in_games_dict.keys()) > 0:
		for game_key, game_players in all_players_in_games_dict.items():

			game_data = game_key.split() # away,home,date

			away_team = game_data[0]
			home_team = game_data[1]

			game_teammates = [] # we are looking for games player played in bc they did not play in all games in this dict bc it is dict of all games by team but independent of players
			if player_team == away_team:
				game_teammates = game_players['away']
			elif player_team == home_team:
				game_teammates = game_players['home']

			# loop thru games to see if we encounter new teammates
			for teammate in game_teammates:
				if teammate not in all_teammates:
					all_teammates.append(teammate)

	else:
		print('Warning: all_players_in_games_dict is empty! ' + str(all_players_in_games_dict))

	print('all_teammates: ' + str(all_teammates))
	return all_teammates

def read_react_web_data(url):
	print('\n===Read React Web Data===\n')
	print('url: ' + url)

	web_data = [] # web_data = [dataframe1,...]

	driver = webdriver.Chrome(ChromeDriverManager().install())
	driver.implicitly_wait(3)

	driver.get(url) # Open the URL on a google chrome window

	# check if no tables found	
	html_result = pd.read_html(driver.find_element('id','dom_SameGameParlayWeb').get_attribute('outerHTML'))[0]
	print('dom_SameGameParlayWeb:\n' + str(html_result))
	
	web_data.append(html_result)

	#print('web_data:\n' + str(web_data))
	return web_data

# finding element by class name will return 1st instance of class
# but unusual error may occur
# .ElementClickInterceptedException: Message: element click intercepted: Element <button role="tab" class="rj-market__group" aria-selected="false" data-testid="button-market-group">...</button> is not clickable at point (763, 135). Other element would receive the click: 
# return {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
def read_react_website(url):
	print('\n===Read React Website===\n')
	print('url: ' + url)

	#web_data = [] # web_data = [dataframe1,...] or [dict1,...] or {}
	web_dict = {}

	driver = webdriver.Chrome(ChromeDriverManager().install())
	driver.implicitly_wait(3)

	driver.get(url) # Open the URL on a google chrome window

	# check if no tables found
	try:
		#sgp_element = driver.find_element('id','dom_SameGameParlayWeb').get_attribute('outerHTML')	
		#soup = BeautifulSoup(page, features='lxml')
	
		# instead of needing keys input just click each btn until find stat of interest
		pts_key = 5 # sometimes 4 if missing quick hits section
		stat_key = pts_key
		stats_of_interest = {'pts':0,'reb':3,'ast':4} #keys relative to pts key. data_table_keys={'pts':pts_key,'reb':pts_key+3,'ast':pts_key+4}
		#web_dict[key] = read_lazy_elements(key)
		#for key in data_table_keys:#.keys():
		for stat_name, relative_key in stats_of_interest.items():
			#print("stat_name: " + stat_name)
			web_dict[stat_name] = {}

			# click pts btn
			epath = 'button[' + str(stat_key+relative_key) + ']'

			if stat_name == 'reb':
				# first need to click right arrow to move so ast btn visible
				side_btn = driver.find_element('class name','side-arrow--right')
				#print("side_btn: " + side_btn.get_attribute('innerHTML'))
				try:
					while True:
						side_btn.click()
				except:
					#web_dict['ast'] = {}
					# click ast btn
					stat_btn = driver.find_element('class name','rj-market__groups').find_element('xpath',epath)
					#print("stat_btn: " + stat_btn.get_attribute('innerHTML'))
					stat_btn.click()

			else:
				stat_btn = driver.find_element('class name','rj-market__groups').find_element('xpath',epath)
				stat_btn_text = stat_btn.get_attribute('innerHTML')
				#print("stat_btn: " + stat_btn_text)
				# if title is 'threes', then subtract 1 from key and try again bc it means the list is missing a tab
				if stat_btn_text == 'Threes': # gone too far
					stat_key -= 1
					epath = 'button[' + str(stat_key) + ']'
					stat_btn = driver.find_element('class name','rj-market__groups').find_element('xpath',epath)
					stat_btn_text = stat_btn.get_attribute('innerHTML')
					#print("stat_btn: " + stat_btn_text)
				stat_btn.click()

			# not all dropdowns are open so program must click each one
			# click player dropdown btn
			# could use find elements to get number of lazy renders and then loop thru that number
			# lazy_element = driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render')
			# print("lazy_element: " + lazy_element.get_attribute('innerHTML'))

			# collapsible_element = lazy_element.find_element('class name','rj-market-collapsible') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[1]').find_element('class name','rj-market')
			# print("collapsible_element: " + collapsible_element.get_attribute('innerHTML'))

			# player_btn = collapsible_element.find_element('xpath','button') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[2]/button')
			# print("player_btn: " + player_btn.get_attribute('innerHTML'))
			# player_btn.click()

			
			print('get all lazy elements and loop thru')
			lazy_elements = driver.find_element('class name','rj-markerboard-markets').find_elements('xpath','sb-lazy-render')
			for e in lazy_elements:
				#print("lazy_element: " + e.get_attribute('innerHTML'))

				#collapsible_element = e.find_element('class name','rj-market-collapsible') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[1]').find_element('class name','rj-market')
				#print("collapsible_element: " + collapsible_element.get_attribute('innerHTML'))

				# multiple (3 always?) players in each lazy element
				player_btns = e.find_elements('class name','rj-market-collapsible__trigger')
				# print('player_btns: ')
				# for player_btn in player_btns:
				# 	print("player_btn: " + player_btn.get_attribute('innerHTML'))

				for player_btn in player_btns:
					#player_btn = collapsible_element.find_element('xpath','button') #driver.find_element('class name','rj-markerboard-markets').find_element('xpath','sb-lazy-render/div[2]/button')
					#print("player_btn: " + player_btn.get_attribute('innerHTML'))

					# need to know which type of market it is bc there are 2: O/U and over only (OO)
					# button header: 'Player Name Stat Name', eg 'Bam Adebayo Assists', excluding 'O/U'
					player_btn_header = player_btn.find_element('xpath','h2').get_attribute('innerHTML')
					#print('player_btn_header: ' + player_btn_header)

					# ignore quarter stats for now
					if re.search('Quarter',player_btn_header):
						break # can break bc list ends with quarter stats

					# old version: as long as we can click all markets we need to open then we dont need to click o/u btns but we may we need to close o/u btns to see the oo btns
					# new version we need to click all btns
					player_btn_arrow = player_btn.find_element('class name','rj-market-collapsible-arrow').get_attribute('innerHTML')
					#print('player_btn_arrow: ' + player_btn_arrow)
					# old version: if o/u and open then close dropdown permanently
					# new version: get odds from all sections so get data 
					# and then close if already open, or open and then close
					# if re.search('O/U',player_btn_header) and re.search('up',player_btn_arrow):
					# 	player_btn.click() # close dropdown
					# 	print('closed unused market')
					# 	time.sleep(0.1)
					# elif not re.search('O/U',player_btn_header):
					# first section already open so arrow up and no need to open but close after reading data
					# arrow down means section closed
					try: # button might be out of window bottom bc long list and we cannot scroll
						if re.search('down',player_btn_arrow):
							player_btn.click() # open dropdown

							#print('clicked player btn')

						# opened data so now collect it and then close it so other data visible

						player_element = player_btn.find_element('xpath','..') 
						#print("player_element: " + player_element.get_attribute('innerHTML'))

						player_name = re.sub('\sAlt\s|Points|Rebounds|Assists|O/U','',player_btn_header).strip().lower()
						player_name = re.sub('−|-',' ',player_name)
						player_name = re.sub('\.','',player_name)
						#print('player_name: ' + player_name)

						if player_name not in web_dict[stat_name].keys():
							web_dict[stat_name][player_name] = {}

						stat_val_elements = player_element.find_elements('class name','rj-market__button-yourbet-title')
						odds_val_elements = player_element.find_elements('class name','rj-market__button-yourbet-odds')

						# print('stat_val_elements')
						# for e in stat_val_elements:
						# 	print("stat_val_element: " + e.get_attribute('innerHTML'))
						# for e in odds_val_elements:
						# 	print("odds_val_elements: " + e.get_attribute('innerHTML'))

						# stat_vals = []
						# odds_vals = []
						for idx in range(len(stat_val_elements)):
							stat_element = stat_val_elements[idx]
							#print("stat_element: " + stat_element.get_attribute('innerHTML'))
							odds_element = odds_val_elements[idx]
							#print("odds_element: " + odds_element.get_attribute('innerHTML'))

							stat = stat_element.get_attribute('innerHTML')
							odds = odds_element.get_attribute('innerHTML')

							# if header is just <stat> without 'alt' and 'o/u'
							# then format is 'Over 24.5 -120'
							# Over <stat> <odds>
							if not re.search('\sAlt\s',player_btn_header):
								# old: stat = re.sub('\+','',stat)
								if re.search('Over',stat):
									stat = re.sub('[a-zA-Z]','',stat).strip()
									stat = str(round(float(stat) + 0.5)) + '+' #or str(int(stat))#str(round(float(stat) + 0.5)) # 0.5 to 1
								else: #under
									stat = re.sub('[a-zA-Z]','',stat).strip()
									stat = str(round(float(stat) - 0.5)) + '-'
							elif re.search('O/U',player_btn_header):
								# start with over and then take every other value as over
								if idx % 2 == 0:
									stat = str(round(float(stat) + 0.5)) + '+' #or str(int(stat))#str(round(float(stat) + 0.5)) # 0.5 to 1
								else: #under
									stat = str(round(float(stat) - 0.5)) + '-'

							odds = re.sub('−','-',odds) # change abnormal '-' char
							#odds = re.sub('\+','',odds) # prefer symbol to differentiate odds from probs, prefer no + symbol for +odds bc implied so not to confuse with val over under

							#stat_vals.append(e.get_attribute('innerHTML'))

							#print('stat: ' + str(stat))
							#print('odds: ' + str(odds))
							#print('player web dict ' + player_name + ': ' + str(web_dict[key][player_name]))
							web_dict[stat_name][player_name][stat] = odds # { stat : odds, ... }
							#print('player web dict ' + player_name + ': ' + str(web_dict[key][player_name]))
						# for e in odds_val_elements:
						# 	odds_vals.append(e.get_attribute('innerHTML'))

						# print('stat_vals: ' + str(stat_vals))
						# print('odds_vals: ' + str(odds_vals))

						#print('collected player data')
						time.sleep(0.2)
						player_btn.click() # close dropdown
					except:
						print('Warning: player btn unclickable!')

				#time.sleep(5)

		print("Request successful.")

	except Exception as e:
		print('Warning: No SGP element! ', e)

	# pts_data = driver.find_element('class name', "rj-markerboard-markets").get_attribute('outerHTML')
	# print('pts_data:\n' + str(pts_data))
	# pts_data = driver.find_element('class name', "rj-market").get_attribute('outerHTML')
	# print('rj-market:\n' + str(pts_data))


	#web_dict['reb'] = {}
	# click reb btn
	# reb_btn = driver.find_element('class name','rj-market__groups').find_element('xpath','button[7]')
	# print("reb_btn: " + reb_btn.get_attribute('innerHTML'))
	# reb_btn.click()


	# # first need to click right arrow to move so ast btn visible
	# side_btn = driver.find_element('class name','side-arrow--right')
	# print("side_btn: " + side_btn.get_attribute('innerHTML'))
	# try:
	# 	while True:
	# 		side_btn.click()
	# except:
		#web_dict['ast'] = {}
	# 	# click ast btn
	# 	ast_btn = driver.find_element('class name','rj-market__groups').find_element('xpath','button[8]')
	# 	print("ast_btn: " + ast_btn.get_attribute('innerHTML'))
	# 	ast_btn.click()

	
	# {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
	print('final web_dict:\n' + str(web_dict))
	return web_dict

#all_players_odds: {'mia': {'pts': {'Bam Adebayo': {'18+': '−650',...
def read_all_players_odds(game_teams, player_teams={}, players=[]):
	print('\n===Read All Players Odds===\n')
	print('game_teams: ' + str(game_teams))
	print('player_teams: ' + str(player_teams))
	all_players_odds = {}
	odds = '?' # if we dont see name then they might be added later so determine if it is worth waiting

	# use pd df
	# like for reading roster and box score and game log
	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	#all_players_odds = [] # all players in game
	#player_stat_odds = [] # from +2 to +n depending on stat

	# should loop thru games instead of teams bc 2 teams on same page
	# see which teams are playing together and group them
	#game_teams = read_opponent()
	for game in game_teams:
		print('game: ' + str(game))
		game_team = game[0] # only read 1 page bc bth teams same page
		print('game_team: ' + str(game_team))

	# for team in teams:
	# 	print('team: ' + team)

		all_players_odds[game_team] = {} # loops for both teams in game?

		team_name = re.sub(' ','-', determiner.determine_team_name(game_team))
		#print("team_name: " + str(team_name))

		# https://sportsbook.draftkings.com/teams/basketball/nba/memphis-grizzlies--odds?sgpmode=true
		game_odds_url = 'https://sportsbook.draftkings.com/teams/basketball/nba/' + team_name + '--odds?sgpmode=true'
		print('game_odds_url: ' + game_odds_url)

		# return dictionary results for a url
		# {'pts': {'bam adebayo': {'18+': '-650','17-': 'x',...
		game_players_odds_dict = read_react_website(game_odds_url)

		if game_players_odds_dict is not None:
			print('game_players_odds_dict:\n' + str(game_players_odds_dict))

			for stat_name, stat_odds_dict in game_players_odds_dict.items():
				print('stat_name: ' + str(stat_name))
				for player, player_odds_dict in stat_odds_dict.items():
					print('player: ' + str(player))
					player_team = ''
					if player in player_teams.keys():
						player_team = player_teams[player]
					else:
						print('Warning: player not in teams list! ' + player)
					print('player_team: ' + str(player_team))
					if player_team not in all_players_odds.keys():
						all_players_odds[player_team] = {}

					if stat_name not in all_players_odds[player_team].keys():
						all_players_odds[player_team][stat_name] = {}

					all_players_odds[player_team][stat_name][player] = player_odds_dict

			

			# if team odds saved locally then no need to read again from internet same day bc unchanged
			#team = stat_dict['team']
			# stat_name = stat_dict['stat name']
			# player = stat_dict['player name']
			# if team not in all_players_odds.keys():
			# 	all_players_odds[team] = {}
			# if stat_name not in all_players_odds[team].keys():
			# 	all_players_odds[team][stat_name] = {}
			# all_players_odds[team][stat_name][player] = odds
			# print('all_players_odds: ' + str(all_players_odds))

			print('Success')
		else:
			print('Warning: website has no soup!')

		# html_results = read_web_data(game_odds_url) #pd.read_html(game_odds_url)
		# print("html_results: " + str(html_results))

		# len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table
		# print("len_html_results: " + str(len_html_results))

		# for order in range(len_html_results):
		# 	print("order: " + str(order))

		# 	html_result_df = html_results[order]
		# 	print('html_result: ' + str(html_result_df))
		# 	print("no. columns: " + str(len(html_result_df.columns.tolist())))

	#writer.write_json_to_file(all_players_odds, filepath, write_param)

	#all_players_odds: {'mia': {'pts': {'Bam Adebayo': {'18+': '−650','17-': 'x',...
	print('all_players_odds: ' + str(all_players_odds))
	return all_players_odds

# stat_dict: {'player name': 'Trevelin Queen', 'stat name': 'ast', 'prob val': 0, 'prob': 100
# all_players_odds = {team:{stat:{player:odds...}
def read_stat_odds(stat_dict, all_players_odds={}):
	print('\n===Read Stat Odds===\n')
	odds = '?' # if we dont see name then they might be added later so determine if it is worth waiting

	# use pd df
	# like for reading roster and box score and game log
	# display player game box scores in readable format
	pd.set_option('display.max_columns', None)

	all_players_odds = [] # all players in game
	player_stat_odds = [] # from +2 to +n depending on stat

	team_name = re.sub(' ','-', determiner.determine_team_name(stat_dict['team']))
	print("team_name: " + str(team_name))

	# https://sportsbook.draftkings.com/teams/basketball/nba/memphis-grizzlies--odds?sgpmode=true
	game_odds_url = 'https://sportsbook.draftkings.com/teams/basketball/nba/' + team_name + '--odds?sgpmode=true'
	print('game_odds_url: ' + game_odds_url)

	web_data = read_react_web_data(game_odds_url)

	if web_data is not None:
		print('web_data:\n' + str(web_data))


		print('Success')
	else:
		print('Warning: website has no soup!')

	# html_results = read_web_data(game_odds_url) #pd.read_html(game_odds_url)
	# print("html_results: " + str(html_results))

	# len_html_results = len(html_results) # each element is a dataframe/table so we loop thru each table
	# print("len_html_results: " + str(len_html_results))

	# for order in range(len_html_results):
	# 	print("order: " + str(order))

	# 	html_result_df = html_results[order]
	# 	print('html_result: ' + str(html_result_df))
	# 	print("no. columns: " + str(len(html_result_df.columns.tolist())))

	print('odds: ' + odds)
	return odds