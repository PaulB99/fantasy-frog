# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 19:39:13 2020

@author: paulb
"""

import requests
import pandas as pd
import json

# Total players
total = 673

def get(url):
    response = requests.get(url)
    return json.loads(response.content)

def detailedinfo(playerid):
    url = 'https://fantasy.premierleague.com/api/element-summary/' + \
    str(playerid) + '/' 
    response = get(url)
    return response
    

pd.options.display.max_columns=None

# Connect to api
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
response = requests.get(url)
response = json.loads(response.content)

# Import players, teams and events
players = response['elements']
teams = response['teams']
events = response['events']
    
# Save info
with open('../data/players_data.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, ensure_ascii=False, indent=4)
print("Saved player data")
    
with open('../data/teams_data.json', 'w', encoding='utf-8') as f:
    json.dump(teams, f, ensure_ascii=False, indent=4)
print("Saved team data")
    
with open('../data/events_data.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=4)
print("Saved event data")
    
# Import detailed info
for i in range(1, total+1):
    info = detailedinfo(i)
    path = '../data/players/' + str(i) + '.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
print("Saved individual player data")
        
url = "https://fantasy.premierleague.com/api/entry/3885742/"
response1 = get(url)
with open('../data/my_team.json', 'w', encoding='utf-8') as f:
    json.dump(response1, f, ensure_ascii=False, indent=4)
print("Done")
