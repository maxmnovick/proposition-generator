# player outcome generator
# updated version of player probability determiner
# instead of generating predictions for all players
# we generate outcomes with probabilities for a given player of interest


import generator, reader, writer

# mia den
#players_names = ['bam adebayo', 'jimmy butler', 'kevin love', 'kyle lowry', 'caleb martin', 'duncan robinson', 'max strus', 'gabe vincent', 'cody zeller', 'christian braun', 'bruce brown', 'thomas bryant', 'kentavious caldwell pope', 'vlatko cancar', 'aaron gordon', 'jeff green', 'reggie jackson', 'nikola jokic', 'jamal murray', 'michael porter jr']

# lal
#players_names = ['Colin Castleton', 'Max Christie', 'anthony davis', 'alex fudge', 'rui hachimura', 'jaxson hayes', 'dmoi hodge', 'Jalen Hood-Schifino', 'lebron james', 'maxwell lewis', 'taurean prince', 'austin reaves', 'cam reddish', 'dangelo russell', 'jarred vanderbilt', 'gabe vincent', 'christian wood']

# den
#players_names = ['christian braun', 'kentavious caldwell-pope', 'vlatko cancar', 'Collin Gillespie', 'aaron gordon', 'justin holiday', 'jay huff', 'reggie jackson', 'nikola jokic', 'deandre jordan', 'braxton key', 'jamal murray', 'zeke nnaji', 'jalen pickett', 'michael porter jr', 'julian strawther', 'hunter tyson', 'peyton watson']


# lal, den
players_names = ['Colin Castleton', 'Max Christie', 'anthony davis', 'alex fudge', 'rui hachimura', 'jaxson hayes', 'dmoi hodge', 'Jalen Hood-Schifino', 'lebron james', 'maxwell lewis', 'taurean prince', 'austin reaves', 'cam reddish', 'dangelo russell', 'jarred vanderbilt', 'gabe vincent', 'christian wood', 'christian braun', 'kentavious caldwell-pope', 'vlatko cancar', 'Collin Gillespie', 'aaron gordon', 'justin holiday', 'jay huff', 'reggie jackson', 'nikola jokic', 'deandre jordan', 'braxton key', 'jamal murray', 'zeke nnaji', 'jalen pickett', 'michael porter jr', 'julian strawther', 'hunter tyson', 'peyton watson']

# nyk
#players_names = ['jalen brunson', 'julius randle', 'mitchell robinson', 'quentin grimes', 'rj barrett']
# mil
#players_names = ['jalen brunson', 'julius randle', 'mitchell robinson', 'quentin grimes', 'rj barrett', 'bobby portis', 'brook lopez', 'damian lillard', 'giannis antetokounmpo', 'jae crowder', 'khris middleton', 'malik beasley', 'pat connaughton']

# gsw
#players_names = ['andrew wiggins', 'chet holmgren', 'chris paul', 'dario saric', 'draymond green', 'gary payton ii', 'jalen williams', 'jonathan kuminga', 'josh giddey', 'kevon looney', 'klay thompson', 'luguentz dort', 'moses moody', 'stephen curry']
# okc
#players_names = ['']

# wsh
# players_names = ['']
# mia
players_names = ['bam adebayo', 'duncan robinson', 'jimmy butler', 'josh richardon', 'kevin love', 'kyle lowry', 'tyler herro', 'daniel gafford', 'danilo gallinari', 'deni avdija', 'jordan poole', 'kyle kuzma', 'tyus jones']

# bkn
# players_names = ['']
# chi
players_names = ['alex caruso', 'andre drummond', 'coby white', 'demar derozan', 'jevon carter', 'nikola vucevic', 'patrick williams', 'zach lavine', 'ben simmons', 'cameron thomas', 'dorian finney smith', 'mikal bridges', 'royce oneale', 'spencer dinwiddie', 'torrey craig']

# dal
#players_names = ['derrick lively ii', 'derrick jones jr', 'grant williams', 'josh green', 'kyrie irving', 'luka doncic', 'tim hardaway jr', 'reggie jackson']
# den
#players_names = ['aaron gordon']

# mem
# players_names = ['']
# por
players_names = ['deandre ayton', 'jerami grant', 'matisse thybulle', 'robert williams', 'shaedon sharpe', 'david roddy', 'desmond bane', 'jaren jackson jr', 'john konchar', 'luke kennard', 'marcus smart', 'xavier tillman', 'ziaire williams']

# phx
# players_names = ['jeff green']

# # gsw
#players_names = ['josh hart']

# # test pacers
#players_names = ['benedict mathurin', 'bruce brown', 'donovan mitchell', 'evan mobley', 'myles turner', 'tyrese haliburton']

# add user input: date of games so code will read all teams played that day
# could assume current date running code

# gen list of player names given teams so we dont have to type all names
# if no date given, and if past 10pm then assume getting data for next day
# https://www.espn.com/nba/schedule
game_teams = [('hou','gsw')]
# we can make read new teams var false at first bc the file has not been created yet so we will write for the first time
# we make it true to read new teams after trades, which tells it to overwrite existing file or make a new file with the date in the title
players_names = reader.read_teams_players(game_teams, read_new_teams=False) #generator.generate_players_names(teams) # generate is wrong term bc we are not computing anything only reading players on each team
#players_names = ['chris paul']

# settings
find_matchups = False
find_players = False
# read new teams after trades and acquisitions new players
read_new_teams = False
# read all seasons to compare and see trend
read_x_seasons = 2 # set 0 or high number to read all seasons
read_season_year = 2024 # user can choose year. read x seasons previous
# read new odds at least once per day if false but set true if we want to update odds more than once per day
read_new_odds = False 
# set false to save time if observing all probs
# make list of sources with different odds 
read_odds = True 
settings = {'find matchups': find_matchups, 'find players': find_players, 'read new teams': read_new_teams, 'read x seasons': read_x_seasons, 'read season year': read_season_year, 'read new odds': read_new_odds, 'read odds': read_odds}

players_outcomes = generator.generate_players_outcomes(players_names, game_teams, settings)

#writer.display_players_outcomes(players_outcomes)