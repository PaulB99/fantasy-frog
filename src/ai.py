# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:21:45 2020

@author: paulb
"""

import json
import requests
import pandas as pd
import numpy as np
import csv

total = 505
gameweek = 1

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

# Drop irrelevant columns
pred_df = pd.DataFrame()
pred_df[['web_name', 'id', 'total_points', 'form', 'team', 'cost']] = players_df[['web_name', 'id', 'total_points', 'form', 'team', 'now_cost']]

difficulties_5 = [] # difficulty for each player in order
difficulties_next = [] # difficulty for each player in order
        
# Clean data
# events_df['deadline_time'] = pd.to_datetime(events_df['deadline_time'])
# events_df['deadline_time'] = events_df['deadline_time'].dt.tz_localize(None)

for i in range(1, total+1):
    path = '../data/players/' + str(i) + '.json'
    with open(path) as json_file:
        player_data = json.load(json_file)
        position = players_df.at[i-1, 'element_type']  # 1=gk, 2=def, 3=mid, 4=fwd
        
        # Determine difficulty of upcoming fixtures
        player_fix = player_data['fixtures']
        fix_df = pd.DataFrame(player_fix)     # Load in fixture data
        next_fix = fix_df.iloc[0]
        
        diffi_5 = 0  #difficulty of next 5
        diffi_next = 0 # difficulty of next 1
        for j in range(5):   # difficulty of next 5 matches
            if(fix_df.at[j, 'is_home'] == True):    # Set opposition
                opposition = fix_df.at[j, 'team_a']
                home = True
            else:
                opposition = fix_df.at[j, 'team_h']
                home = False
        
            if(position == 1 or position == 2):
                if(home == True):
                    diffi_5 += teams_df.at[j, 'strength_attack_away']
                    if(j == 0):
                        diffi_next += teams_df.at[j, 'strength_attack_away']
                else:  # Is away
                    diffi_5 += teams_df.at[j, 'strength_attack_home']
                    if(j == 0):
                        diffi_next += teams_df.at[j, 'strength_attack_home']
                        
            else:   # Is attacking
                if(home == True):
                    diffi_5 += teams_df.at[j, 'strength_defence_away']
                    if(j == 0):
                        diffi_next += teams_df.at[j, 'strength_defence_away']
                else:  # Is away
                    diffi_5 += teams_df.at[j, 'strength_defence_home']
                    if(j == 0):
                        diffi_next += teams_df.at[j, 'strength_defence_home']
        difficulties_5.append(diffi_5) # Append difficulties to array
        difficulties_next.append(diffi_next)
            
        
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