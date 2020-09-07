# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:21:45 2020

@author: paulb
"""

import json
import requests
import pandas as pd
import numpy as np

# Load in data
with open('../data/players_data.json') as json_file:
    players = json.load(json_file)

with open('../data/teams_data.json') as json_file:
    teams = json.load(json_file)
    
with open('../data/events_data.json') as json_file:
    events = json.load(json_file)

# Create pandas dataframes
players_df = pd.DataFrame(players)
teams_df = pd.DataFrame(teams)
events_df = pd.DataFrame(events)

print(players_df.head())

# Clean data
# events_df['deadline_time'] = pd.to_datetime(events_df['deadline_time'])
# events_df['deadline_time'] = events_df['deadline_time'].dt.tz_localize(None)


# Create players predicted points dataframe
preds_df = pd.DataFrame()

'''
form = 0
if (defender):
    strength_att = 0
if(attacker):
    strength_def = 0

strength_modifier = 
'''

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