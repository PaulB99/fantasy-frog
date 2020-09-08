# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:21:45 2020

@author: paulb
"""

import json
import requests
import pandas as pd
import numpy as np
from scipy.optimize import linprog

def validswap(x, y, value):
    if(value + x - y <= budget):
        return True
    else:
        return False

total = 505
gameweek = 1
budget = 1000

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

preds_5 = [] # Predictions of points per player in next 5 matches
preds_next = [] # Predictions of points in next match

# Find average difficulty
t = 0
for x in range(20):
    t += teams_df.at[x, "strength_overall_home"]
    t += teams_df.at[x, "strength_overall_away"]
average = t/40
print(average)
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
        
        # Get form and ppg data
        form = float(players_df.at[i-1, 'form'])
        ppg = float(players_df.at[i-1, 'points_per_game'])
        
        # MAKE PREDICTIONS
        if(form == 0.0): # if no form
            pred_5 = (ppg * (diffi_5/average))
            pred_next = (ppg * (diffi_next/average))
        else:
            pred_5 = ((ppg + form)/2 * (diffi_5/average))
            pred_next = ((ppg + form)/2 * (diffi_next/average))
        
        # Add to array
        preds_5.append(pred_5)
        preds_next.append(pred_next)
            
gk_limit = 2  # Amount of players per position
gk_num = 0
def_limit = 5
def_num = 0
mid_limit = 5
mid_num = 0
fwd_limit = 3
fwd_num = 0

team_cost = 0

selection = []
gks = []
defs = []
mids = []
fwds = []
    
# MAKE SELECTIONS
for k in range(total):
    select_pos = players_df.at[k, 'element_type']  # 1=gk, 2=def, 3=mid, 4=fwd
    if (select_pos == 1):
        if (gk_num < gk_limit):
            selection.append((players_df.at[k, 'web_name'], 'gk'))
            gks.append((players_df.at[k, 'web_name'], k))
            gk_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
        else:
            for m in range(2):
                if(validswap(int(players_df.at[k, 'now_cost']), int(players_df.at[gks[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[gks[m][1]]):
                    new_selection = [n for n in selection if n[0] == gks[m][0]]
                    new_gks = [n for n in gks if n[0] == gks[m][0]]
                    
                    new_selection.append((players_df.at[k, 'web_name'], 'gk'))
                    new_gks.append((players_df.at[k, 'web_name'], k))
                    
                    team_cost -= int(players_df.at[gks[m][1], 'now_cost'])
                    team_cost += int(players_df.at[k, 'now_cost'])
                    
                    selection = new_selection
                    gks = new_gks
                    break
                
    elif (select_pos == 2):
        if (def_num < def_limit):
            selection.append((players_df.at[k, 'web_name'], 'def'))
            defs.append((players_df.at[k, 'web_name'], k))
            def_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
            
    elif (select_pos == 3):
        if(mid_num < mid_limit):
            selection.append((players_df.at[k, 'web_name'], 'mid'))
            mids.append((players_df.at[k, 'web_name'], k))
            mid_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
            
    elif (select_pos == 4):
        if(fwd_num < fwd_limit):
            selection.append((players_df.at[k, 'web_name'], 'fwd'))
            fwds.append((players_df.at[k, 'web_name'], k))
            fwd_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
        
# Print selections
line1 = ''
line2 = ''
line3 = ''
line4 = ''
print(len(selection))
print(len(gks))
print(len(mids))
for l in range(len(selection)):
    if(selection[l][1] == 'gk'):
        line1 += selection[l][0] + ' '
    elif(selection[l][1] == 'def'):
        line2 += selection[l][0] + ' '
    elif(selection[l][1] == 'mid'):
        line3 += selection[l][0] + ' '
    else:
        line4 += selection[l][0] + ' '
        
print (line1)
print (line2)
print (line3)
print (line4)
print ('Value = ' + str(team_cost/10) + 'm')
    
'''
    print(selection[l][0], end='')
    if(l == 1 or l == 6 or l == 11):
        print('')
    else:
        print(' - ', end='') '''
    
        
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