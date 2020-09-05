# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:21:45 2020

@author: paulb
"""

import requests
import os
import pandas as pd
import numpy as np
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

# Create pandas dataframes
players_df = pd.DataFrame(players)
teams_df = pd.DataFrame(teams)
events_df = pd.DataFrame(events)

# Clean data
events_df['deadline_time'] = pd.to_datetime(events_df['deadline_time'])
events_df['deadline_time'] = events_df['deadline_time'].dt.tz_localize(None)

# FIRST TIME

# Import datasets

# Clean data and combine different leagues

# Work out predicted points 

# Find optimal team by pred. points

# Confirm team

# EACH WEEK

# Pull latest data

# Work out predicted points 

# Weigh up predicted points vs cost of transfers

# Make transfers 

# Confirm team