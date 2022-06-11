from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import html5lib
import re
import time
from pathlib import Path
import os
import sys

#Get script arguments as season to aggregate
season_to_edit = sys.argv[1]

#Read CSVs for player stats, games and player info
stats_df = pd.read_csv('input/game_skater_stats.csv')
games_df = pd.read_csv('input/game.csv', usecols=['game_id','season', 'type'])
players_df = pd.read_csv('input/player_info.csv', usecols=['player_id', 'firstName', 'lastName', 'birthDate', 'primaryPosition', 'shootsCatches'], parse_dates=['birthDate'])

#Stage 1: Merge game stats and game info, adding season and type of game (playoff or regular season). Select only games in desired season and only regular season games
stage_1 = stats_df.merge(games_df, how='left', left_on='game_id', right_on='game_id')
stage_1 = stage_1[stage_1['type'] == 'R']
stage_1 = stage_1[stage_1['season'] == int(season_to_edit)]

#Stage 2: Aggregate stats by player and season. Majority of stats can be summed, but games played must be counted so must use pd.NamedAgg. Reset index to keep season and player_id
stage_2 = stage_1.groupby(['player_id', 'season']).agg(
    goals = pd.NamedAgg(column='goals', aggfunc='sum'),
    assists = pd.NamedAgg(column='assists', aggfunc='sum'),
    plusMinus = pd.NamedAgg(column='plusMinus', aggfunc='sum'),
    timeOnIce = pd.NamedAgg(column='timeOnIce', aggfunc='sum'),
    shortHandedTimeOnIce = pd.NamedAgg(column='shortHandedTimeOnIce', aggfunc='sum'),
    powerPlayTimeOnIce = pd.NamedAgg(column='powerPlayTimeOnIce', aggfunc='sum'),
    gamesPlayed = pd.NamedAgg(column='game_id', aggfunc='count'),
    shots = pd.NamedAgg(column='shots', aggfunc='sum'),
    blocks = pd.NamedAgg(column='blocked', aggfunc='sum'),
    faceOffWins = pd.NamedAgg(column='faceOffWins', aggfunc='sum'),
    faceOffTaken = pd.NamedAgg(column='faceoffTaken', aggfunc='sum'),
    shortHandedGoals = pd.NamedAgg(column='shortHandedGoals', aggfunc='sum'),
    shortHandedAssists = pd.NamedAgg(column='shortHandedAssists', aggfunc='sum'),
    powerPlayGoals = pd.NamedAgg(column='powerPlayGoals', aggfunc='sum'),
    powerPlayAssists = pd.NamedAgg(column='powerPlayAssists', aggfunc='sum'),
    hits = pd.NamedAgg(column='hits', aggfunc='sum'),
    penaltyMinutes = pd.NamedAgg(column='penaltyMinutes', aggfunc='sum'),
    takeaways = pd.NamedAgg(column='takeaways', aggfunc='sum'),
    giveaways = pd.NamedAgg(column='giveaways', aggfunc='sum')
).reset_index()

#Stage 3: Add player info such as birth date, first names, last names. Cast necessary columns to other datatypes for future transformations
stage_3 = stage_2.merge(players_df, how='left', left_on='player_id', right_on='player_id')
stage_3['birthDate'] = stage_3['birthDate'].dt.date
stage_3['firstName'] = stage_3['firstName'].astype(pd.StringDtype()) #Convert to string for URL usage
stage_3['lastName'] = stage_3['lastName'].astype(pd.StringDtype())
stage_3['timeOnIce'] = stage_3['timeOnIce'].astype(float) #Convert to float for floating point operations
stage_3['powerPlayTimeOnIce'] = stage_3['powerPlayTimeOnIce'].astype(float)
stage_3['shortHandedTimeOnIce'] = stage_3['shortHandedTimeOnIce'].astype(float)
stage_3['season'] = stage_3['season'].astype(str) #Reformat season as str and change format to match CapFriendly
stage_3['season'] = stage_3['season'].apply(lambda x: ''.join(list(x)[:4]) + '-' + ''.join(list(x)[6:8]))
stage_3['points'] = stage_3['goals'] + stage_3['assists']

#Stage 4: Feature engineering. Adding additional columns from previously existing columns
stage_4 = stage_3.copy()
stage_4['faceOffLosses'] = stage_4['faceOffTaken'] - stage_4['faceOffWins']
stage_4['faceOffPercentage'] = np.round(stage_4['faceOffWins'] / stage_4['faceOffTaken'] * 100, 2)
stage_4['faceOffPercentage'] = stage_4['faceOffPercentage'].fillna(0) #In cases of no faceoffs taken, replace with 0
stage_4['powerPlayPoints'] = stage_4['powerPlayGoals'] + stage_4['powerPlayAssists']
stage_4['shortHandedPoints'] = stage_4['shortHandedGoals'] + stage_4['shortHandedAssists']
stage_4['turnoverDifferential'] = stage_4['takeaways'] - stage_4['giveaways']

def formatIceTime(time):
    minutes = int(np.floor(time / 60))
    seconds = int(np.floor(time % 60))
    return str(minutes) + ':' + str(seconds)

stage_4['avgTimeOnIce'] = stage_4['timeOnIce'] / stage_4['gamesPlayed'] #Divide by games played to get ice time per game
stage_4['avgTimeOnIce'] = stage_4['avgTimeOnIce'].apply(lambda x: formatIceTime(x)) #Format time per game
stage_4['avgPowerPlayTimeOnIce'] = stage_4['powerPlayTimeOnIce'] / stage_4['gamesPlayed']
stage_4['avgPowerPlayTimeOnIce'] = stage_4['avgPowerPlayTimeOnIce'].apply(lambda x: formatIceTime(x))
stage_4['avgShortHandedTimeOnIce'] = stage_4['shortHandedTimeOnIce'] / stage_4['gamesPlayed']
stage_4['avgShortHandedTimeOnIce'] = stage_4['avgShortHandedTimeOnIce'].apply(lambda x: formatIceTime(x))
stage_4['shootingPercentage'] = np.round(stage_4['goals'] / stage_4['shots'] * 100, 2)
stage_4['pointsPerGame'] = np.round(stage_4['points'] / stage_4['gamesPlayed'], 2)

#Stage 5: Select columns in desired order
stage_5 = stage_4[['player_id', 'firstName', 'lastName','birthDate', 'primaryPosition', 'shootsCatches', 'season', 'gamesPlayed',
                   'goals', 'assists', 'points', 'pointsPerGame', 'plusMinus', 'shots', 'shootingPercentage', 'penaltyMinutes', 'timeOnIce', 'avgTimeOnIce',
                   'faceOffWins', 'faceOffLosses', 'faceOffTaken', 'faceOffPercentage', 'hits', 'blocks', 'takeaways', 'giveaways', 'turnoverDifferential',
                   'powerPlayGoals', 'powerPlayAssists', 'powerPlayPoints', 'powerPlayTimeOnIce', 'avgPowerPlayTimeOnIce',
                   'shortHandedGoals', 'shortHandedAssists', 'shortHandedPoints', 'shortHandedTimeOnIce', 'avgShortHandedTimeOnIce']]

#Stage 5: Final stage. Add first and lastnames separated by a - for url usage. Remove any ' or . in names (O'Reilly, T.J.)
df = stage_5.copy()
df['fullname'] = df['firstName'].str.replace('[.\']', '', regex=True).str.lower().str.cat(df['lastName'].str.replace('[.\']', '', regex=True).str.lower(), sep='-')
df['fullname'] = df['fullname'].str.replace('[ ]', '-', regex=True)

#Fix pages where url has a 1 at the end for players with same name (Sebastian Aho and Sebastian Aho), or have a name slightly different from official NHL API
def getHTMLData(link, fullname):
    newlink = ''
    if 'Player not found' in BeautifulSoup(requests.get(link + '1').text, 'html5lib').title.text: #Try adding a 1 to the not working link
        commonNames = { #Alternatives for common names (Mike Matheson, Michael Matheson)
            'phil': 'philip',
            'philip': 'phil',
            'phillip': 'phil',
            'mike': 'michael',
            'michael': 'mike',
            'matt': 'matthew',
            'sergey': 'sergei',
            'sergei': 'sergey',
            'evgeni': 'evgeny',
            'evgenii': 'evgeni',
            'josh': 'joshua',
            'max': 'maxime',
            'nic': 'nicolas',
            'nick': 'nicholas',
            'nicholas': 'nick',
            'nikolay': 'nikolai',
            'alex': 'alexander',
            'alexander': 'alex',
            'zach': 'zachary',
            'egor': 'yegor',
            'mikey': 'michael',
            'sammy': 'samuel',
            'pa': 'pierre-alexandre',
            'dan': 'daniel'
        }
        names = fullname.split('-') #Get first name
        if (names[0] in commonNames):
            names[0] = commonNames.get(names[0]) #Replace first name with alternative first name
        newlink = 'https://capfriendly.com/players/' + '-'.join(names) #Reform link with new first name
    else:
        newlink = link + '1'
    html_data = requests.get(newlink).text #Make new request with new link
    return BeautifulSoup(html_data, 'html5lib') #Parse HTML

count = 0
def findContract(fullname, season, maxProgress):
    global count #Count for progress
    time.sleep(0.5) #Avoid spamming requests to CapFriendly
    soup = BeautifulSoup(requests.get(f'https://capfriendly.com/players/{fullname}').text, 'html5lib')
    if ('Player not found' in soup.title.text): #If player not found, try fixing with fixing function
        soup = getHTMLData(f'https://capfriendly.com/players/{fullname}', fullname)
        if ('Player not found' in soup.title.text): #If player still not found, replace with invalid value -111 to ignore later
            return -111
    for table in soup.find_all('tbody'):
        for row in table.find_all('tr'):
            col = row.find_all('td')
            if col[0].text == season:
                count = count + 1
                print(' ' * 75, end='\r')
                print(count, '/', maxProgress, end='\r')
                if not any(char.isdigit() for char in col[2].text): #If not valid salary table
                    return -111
                return int(''.join(re.findall(r'\d', col[2].text)))

#Get salary value for 
df['salary'] = df.apply(lambda x: findContract(x['fullname'], x['season'], df.shape[0]), axis=1)
df['salary'].fillna(-111, inplace=True)
df['salary'] = df['salary'].astype('int64')

output = df.reset_index()
output.drop(['index', 'fullname'], axis=1, inplace=True) #Drop index and fullname columns
#Create staging csv
os.makedirs('stagedcsv', exist_ok=True)
output.to_csv(f'stagedcsv/{season_to_edit}stats.csv', index=False)
print('Season ' + season_to_edit + ' aggregation complete.')