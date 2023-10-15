# player outcome generator
# updated version of player probability determiner
# instead of generating predictions for all players
# we generate outcomes with probabilities for a given player of interest


import generator, writer

# mia den
#players_names = ['bam adebayo', 'jimmy butler', 'kevin love', 'kyle lowry', 'caleb martin', 'duncan robinson', 'max strus', 'gabe vincent', 'cody zeller', 'christian braun', 'bruce brown', 'thomas bryant', 'kentavious caldwell pope', 'vlatko cancar', 'aaron gordon', 'jeff green', 'reggie jackson', 'nikola jokic', 'jamal murray', 'michael porter jr']

# test
players_names = ['jeff green']

# settings
find_matchups = False
find_players = False
settings = {'find matchups': find_matchups, 'find players': find_players}

players_outcomes = generator.generate_players_outcomes(players_names, settings)

#writer.display_players_outcomes(players_outcomes)