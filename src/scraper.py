# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 19:39:13 2020

@author: paulb
"""

import requests
import pandas as pd
import json

def get(url):
    response = requests.get(url)
    return json.loads(response.content)

def detailedinfo(playerid):
    url = 'https://fantasy.premierleague.com/api/element-summary/' + \
    str(playerid) + '/' 
    response = get(url)
    fixtures = response['fixtures']
    history = response['history']
    history_past = response['history_past']
    

pd.options.display.max_columns=None

# Connect to api
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
response = requests.get(url)
response = json.loads(response.content)

# Import players, teams and events
players = response['elements']
teams = response['teams']
events = response['events']

with open('../data/players_data.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, ensure_ascii=False, indent=4)
    
with open('../data/teams_data.json', 'w', encoding='utf-8') as f:
    json.dump(teams, f, ensure_ascii=False, indent=4)
    
with open('../data/events_data.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=4)
