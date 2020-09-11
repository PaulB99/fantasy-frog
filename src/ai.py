# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:21:45 2020

@author: paulb
"""

import json
import requests
import pandas as pd
import numpy as np
import math
import csv

# Checks if a swap can be made in budget
def validswap(x, y, value):
    if(value + x - y <= budget):
        return True
    else:
        return False

# Gets a 3 letter team abbreviation 
def get_team(x):
    for t in range(len(teams_df)):
        if teams_df.at[t, 'id'] == x:
            y = teams_df.at[t, 'short_name']
    return y

# Gets the percentage chance of a player to play the next match
def chance_to_play(i):
    chance = players_df.at[i, 'chance_of_playing_next_round']
    if math.isnan(chance):
        return 1
    else:
        return (chance/100)

# MANUAL VARIABLES
total = 514
gameweek = 1
budget = 1000
stats = True

# Load in data
with open('../data/players_data.json') as json_file:
    players = json.load(json_file)

with open('../data/teams_data.json') as json_file:
    teams = json.load(json_file)
    
with open('../data/events_data.json') as json_file:
    events = json.load(json_file)

# Create pandas dataframes
first_players_df = pd.DataFrame(players)
teams_df = pd.DataFrame(teams)
events_df = pd.DataFrame(events)

# Sort players dataframe by id
players_df = first_players_df.sort_values('id')

preds_5 = [] # Predictions of points per player in next 5 matches
preds_next = [] # Predictions of points in next match

# Find average difficulty
t = 0
for x in range(20):
    t += teams_df.at[x, "strength_overall_home"]
    t += teams_df.at[x, "strength_overall_away"]
average = t/40
print(average)

for i in range(1, total+1): #total+1  # i is meant to be player id
    p_id = players_df.at[i-1, 'id']
    path = '../data/players/' + str(p_id) + '.json'
    with open(path) as json_file:
        player_data = json.load(json_file)
        #print(players_df.at[i-1, 'id'] - players_df.at[i, 'id'])
        position = players_df.at[i-1, 'element_type']  # 1=gk, 2=def, 3=mid, 4=fwd
        
        # Determine difficulty of upcoming fixtures
        player_fix = player_data['fixtures']
        player_history = player_data['history_past']
        fix_df = pd.DataFrame(player_fix)     # Load in fixture data
        history_df = pd.DataFrame(player_history)
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
        
        # Get form, ppg and last season data
        form = float(players_df.at[i-1, 'form'])    # Last 30 days form
        ppg = float(players_df.at[i-1, 'points_per_game'])   # Last season ppg
        last_total = 0.0
        if(not(history_df.empty)):
            history_list = history_df.values.tolist()
            for h in history_list:
                if(h[0] == '2019/20'):
                    last_total = float(h[4])
        
        # MAKE PREDICTIONS
        last_season_weight = math.log10(11-gameweek)  # Weight of past season should decrease over time
        '''
        if(form == 0.0): # if no form
            pred_5 = (ppg  * ((diffi_5/average) ** math.e))
            pred_next = (ppg * ((diffi_next/average) ** math.e))
        else:
            pred_5 = ((ppg + form) /2 * ((diffi_5/average) ** math.e))
            pred_next = ((ppg + form) /2 * ((diffi_next/average) ** math.e))
        '''
        if(form == 0.0): # if no form
            pred_5 = (((ppg + (last_total / 38)) /2)  * ((diffi_5/average) ** math.e)) * chance_to_play(i-1)
            pred_next = (((ppg + (last_total / 38)) /2) * ((diffi_next/average) ** math.e))  * chance_to_play(i-1)
        else:
            pred_5 = ((ppg + ((last_total / 38) * last_season_weight) + (form * (1- last_season_weight))) /3 * ((diffi_5/average) ** math.e))  * chance_to_play(i-1)
            pred_next = ((ppg + ((last_total / 38) * last_season_weight) + (form * (1- last_season_weight))) /3 * ((diffi_next/average) ** math.e))  * chance_to_play(i-1)
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
    name = players_df.at[k, 'web_name'] + ' (' + get_team(players_df.at[k, 'team']) + ')'
    if (select_pos == 1):
        if (gk_num < gk_limit):
            gks.append((name, k))
            gk_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
        else:
            for m in range(2):
                if(validswap(int(players_df.at[k, 'now_cost']), int(players_df.at[gks[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[gks[m][1]]):
                    new_gks = [n for n in gks if n[0] != gks[m][0]]
                    
                    new_gks.append((name, k))
                    
                    team_cost -= int(players_df.at[gks[m][1], 'now_cost'])
                    team_cost += int(players_df.at[k, 'now_cost'])
                    
                    gks = new_gks
                    break
                
    elif (select_pos == 2):
        if (def_num < def_limit):
            defs.append((name, k))
            def_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
        else:
            for m in range(5):
                if(validswap(int(players_df.at[k, 'now_cost']), int(players_df.at[defs[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[defs[m][1]]):
                    new_defs = [n for n in defs if n[0] != defs[m][0]]
                    
                    new_defs.append((name, k))
                    
                    team_cost -= int(players_df.at[defs[m][1], 'now_cost'])
                    team_cost += int(players_df.at[k, 'now_cost'])
                    
                    defs = new_defs
                    break
            
    elif (select_pos == 3):
        if(mid_num < mid_limit):
            mids.append((name, k))
            mid_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
        else:
            for m in range(5):
                if(validswap(int(players_df.at[k, 'now_cost']), int(players_df.at[mids[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[mids[m][1]]):
                    new_mids = [n for n in mids if n[0] != mids[m][0]]
                    
                    new_mids.append((name, k))
                    
                    team_cost -= int(players_df.at[mids[m][1], 'now_cost'])
                    team_cost += int(players_df.at[k, 'now_cost'])
                    
                    mids = new_mids
                    break
            
    elif (select_pos == 4):
        if(fwd_num < fwd_limit):
            fwds.append((name, k))
            fwd_num +=1
            team_cost+= int(players_df.at[k, 'now_cost'])
        else:
            for m in range(3):
                if(validswap(int(players_df.at[k, 'now_cost']), int(players_df.at[fwds[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[fwds[m][1]]):
                    new_fwds = [n for n in fwds if n[0] != fwds[m][0]]
                    
                    new_fwds.append((name, k))
                    
                    team_cost -= int(players_df.at[fwds[m][1], 'now_cost'])
                    team_cost += int(players_df.at[k, 'now_cost'])
                    
                    fwds = new_fwds
                    break
    
# Find predicted score for this week and next weeks
pred_week = 0
pred_5 = 0
for g in gks:
    pred_week += preds_next[g[1]]
    pred_5 += preds_5[g[1]]
for d in defs:
    pred_week += preds_next[d[1]]
    pred_5 += preds_5[d[1]]
for m in mids:
    pred_week += preds_next[m[1]]
    pred_5 += preds_5[m[1]]
for f in fwds:
    pred_week += preds_next[f[1]]
    pred_5 += preds_5[f[1]]

# Print selections
for l in range(len(gks)):
    print(gks[l][0] + '   ', end='')
print('\n')

for l in range(len(defs)):
    print(defs[l][0] + '   ', end='')
print('\n')

for l in range(len(mids)):
    print(mids[l][0] + '   ', end='')
print('\n')

for l in range(len(fwds)):
    print(fwds[l][0] + '   ', end='')
print('\n')

if stats:
    print ('Value = ' + str(team_cost/10) + 'm')

    print ('Predicted score this week = ' + str(pred_week))

    print ('Predicted score for next 5 weeks = ' + str(pred_5))

    print ('\n')

# Print predictions per player 
if (stats == True):
    for g in gks:
        print(str(preds_next[g[1]]) + ' ' + g[0] + ' ' + str(g[1]) + ' ' + str(players_df.at[g[1], 'id']))
    for g in defs:
        print(str(preds_next[g[1]]) + ' ' + g[0] + ' ' + str(g[1]) + ' ' + str(players_df.at[g[1], 'id']))
    for g in mids:
        print(str(preds_next[g[1]]) + ' ' + g[0] + ' ' + str(g[1]) + ' ' + str(players_df.at[g[1], 'id']))
    for g in fwds:
        print(str(preds_next[g[1]]) + ' ' + g[0] + ' ' + str(g[1]) + ' ' + str(players_df.at[g[1], 'id']))


# DETERMINE STARTING TEAM

best_gk = gks[0]
bench_gk = gks[1]
if (preds_next[gks[1][1]] > preds_next[gks[0][1]]):
    best_gk = gks[1]
    bench_gk = gks[0]

starting_team = []
bench = []
for d in defs:
    starting_team.append(d)  # Defenders will always fit
for m in mids:
    starting_team.append(m)  # Mids will just about fit
for f in fwds:
    lowest = starting_team[0]
    for s in starting_team:  # Find lowest scoring player
        if(preds_next[s[1]] < preds_next[lowest[1]]):
            lowest = s
    if (preds_next[f[1]] > preds_next[lowest[1]]):
        bench.append(lowest)
        new_team = [n for n in starting_team if n[0] != lowest[0]]
        new_team.append(f)
        starting_team = new_team

# Find captain
captain = (best_gk)
for s in starting_team:
    if (preds_next[s[1]] > preds_next[captain[1]]):
        captain = s
for pos in range(len(starting_team)):   # Apply (C) for captain
    if (starting_team[pos][0] == captain [0]):
        lst = list(starting_team[pos])
        lst[0] += ' (C) '
        s = tuple(lst)
        starting_team[pos] = s
        
# Order bench
bench.sort(reverse = True, key = lambda b: preds_next[b[1]])
        
# Print team
print('Starting 11 : \n')
print(best_gk[0])
for s in starting_team:
    print(s[0])
print('Bench : \n')
print(bench_gk[0], end='   ') # Bench 
for b in bench:
    print(b[0], end='   ')
    
# Save team to file  
'''with open('../data/team/team.csv', mode='w') as team_file:
    writer = csv.writer(team_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(best_gk)
    for t in starting_team:
        writer.writerow(t)
    writer.writerow(bench_gk)
    for b in bench:
        writer.writerow(b) '''
        
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

# Confirm team '''