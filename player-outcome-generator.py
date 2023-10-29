# player outcome generator
# updated version of player probability determiner
# instead of generating predictions for all players
# we generate outcomes with probabilities for a given player of interest


import generator, writer

# mia den
#players_names = ['bam adebayo', 'jimmy butler', 'kevin love', 'kyle lowry', 'caleb martin', 'duncan robinson', 'max strus', 'gabe vincent', 'cody zeller', 'christian braun', 'bruce brown', 'thomas bryant', 'kentavious caldwell pope', 'vlatko cancar', 'aaron gordon', 'jeff green', 'reggie jackson', 'nikola jokic', 'jamal murray', 'michael porter jr']

# lal
#players_names = ['Colin Castleton', 'Max Christie', 'anthony davis', 'alex fudge', 'rui hachimura', 'jaxson hayes', 'dmoi hodge', 'Jalen Hood-Schifino', 'lebron james', 'maxwell lewis', 'taurean prince', 'austin reaves', 'cam reddish', 'dangelo russell', 'jarred vanderbilt', 'gabe vincent', 'christian wood']

# den
#players_names = ['christian braun', 'kentavious caldwell-pope', 'vlatko cancar', 'Collin Gillespie', 'aaron gordon', 'justin holiday', 'jay huff', 'reggie jackson', 'nikola jokic', 'deandre jordan', 'braxton key', 'jamal murray', 'zeke nnaji', 'jalen pickett', 'michael porter jr', 'julian strawther', 'hunter tyson', 'peyton watson']


# lal, den
players_names = ['Colin Castleton', 'Max Christie', 'anthony davis', 'alex fudge', 'rui hachimura', 'jaxson hayes', 'dmoi hodge', 'Jalen Hood-Schifino', 'lebron james', 'maxwell lewis', 'taurean prince', 'austin reaves', 'cam reddish', 'dangelo russell', 'jarred vanderbilt', 'gabe vincent', 'christian wood', 'christian braun', 'kentavious caldwell-pope', 'vlatko cancar', 'Collin Gillespie', 'aaron gordon', 'justin holiday', 'jay huff', 'reggie jackson', 'nikola jokic', 'deandre jordan', 'braxton key', 'jamal murray', 'zeke nnaji', 'jalen pickett', 'michael porter jr', 'julian strawther', 'hunter tyson', 'peyton watson']



# phx
# players_names = ['jeff green']

# # gsw
# players_names = ['jeff green']

# # test
players_names = ['Colin Castleton']

# settings
find_matchups = False
find_players = False
settings = {'find matchups': find_matchups, 'find players': find_players}

players_outcomes = generator.generate_players_outcomes(players_names, settings)

#writer.display_players_outcomes(players_outcomes)