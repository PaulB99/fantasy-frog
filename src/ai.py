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
    if(value + x - y <= (budget)):
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
    
# Checks if the player has changed position since last season and if so returns the modifier
def changed_position(x):
    player_id = players_df.at[x, 'id']
    for c in range(len(changes_df)):
        if (player_id == changes_df.at[c, 'id']):
            change = changes_df.at[c, 'change']
            if(change == 'f'):
                return pos_forward_modifier
            elif(change == 'b'):
                return pos_back_modifier
    else:
        return 1
        
    
# Create a team given the predictions
def create_team():
    gk_limit = 1 #2 # Amount of players per position
    gk_num = 0
    def_limit = 5 #5
    def_num = 0
    mid_limit = 5 #5
    mid_num = 0 
    fwd_limit = 3 #3
    fwd_num = 0
    
    team_cost = 0
    
    selection = []
    gks = []
    defs = []
    mids = []
    fwds = []
    
    # good min price players for the bench
    bench_gk = ('Temp', 520, 1)
    
    # MAKE SELECTIONS
    for k in range(total):
        select_pos = players_df.at[k, 'element_type']  # 1=gk, 2=def, 3=mid, 4=fwd
        name = players_df.at[k, 'web_name'] + ' (' + get_team(players_df.at[k, 'team']) + ')'
        p_id = players_df.at[k, 'id']
        if (select_pos == 1):
            if (gk_num < gk_limit):
                gks.append((name, k, p_id))
                gk_num +=1
                team_cost+= float(players_df.at[k, 'now_cost'])
            else:
                for m in range(gk_limit):
                    if(validswap(float(players_df.at[k, 'now_cost']), float(players_df.at[gks[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[gks[m][1]]):
                        new_gks = [n for n in gks if n[0] != gks[m][0]]
                        
                        new_gks.append((name, k, p_id))
                        
                        team_cost -= float(players_df.at[gks[m][1], 'now_cost'])
                        team_cost += float(players_df.at[k, 'now_cost'])
                        
                        gks = new_gks
                        
            if((float(players_df.at[k, 'now_cost']) == 40) and (preds_5[k] >= preds_5[bench_gk[1]])):  # if eligible to be a good bench gk
                bench_gk = (name, k, p_id)
                    
        elif (select_pos == 2):
            if (def_num < def_limit):
                defs.append((name, k, p_id))
                def_num +=1
                team_cost+= float(players_df.at[k, 'now_cost'])
            else:
                for m in range(def_limit):
                    if(validswap(float(players_df.at[k, 'now_cost']), float(players_df.at[defs[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[defs[m][1]]):
                        new_defs = [n for n in defs if n[0] != defs[m][0]]
                        
                        new_defs.append((name, k, p_id))
                        
                        team_cost -= float(players_df.at[defs[m][1], 'now_cost'])
                        team_cost += float(players_df.at[k, 'now_cost'])
                        
                        defs = new_defs
                        break
                
        elif (select_pos == 3):
            if(mid_num < mid_limit):
                mids.append((name, k, p_id))
                mid_num +=1
                team_cost+= float(players_df.at[k, 'now_cost'])
            else:
                for m in range(mid_limit):
                    if(validswap(float(players_df.at[k, 'now_cost']), float(players_df.at[mids[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[mids[m][1]]):
                        new_mids = [n for n in mids if n[0] != mids[m][0]]
                        
                        new_mids.append((name, k, p_id))
                        
                        team_cost -= float(players_df.at[mids[m][1], 'now_cost'])
                        team_cost += float(players_df.at[k, 'now_cost'])
                        
                        mids = new_mids
                        break
                
        elif (select_pos == 4):
            if(fwd_num < fwd_limit):
                fwds.append((name, k, p_id))
                fwd_num +=1
                team_cost+= float(players_df.at[k, 'now_cost'])
            else:
                for m in range(fwd_limit):
                    if(validswap(float(players_df.at[k, 'now_cost']), float(players_df.at[fwds[m][1], 'now_cost']), team_cost) and preds_5[k] > preds_5[fwds[m][1]]):
                        new_fwds = [n for n in fwds if n[0] != fwds[m][0]]
                        
                        new_fwds.append((name, k, p_id))
                        
                        team_cost -= float(players_df.at[fwds[m][1], 'now_cost'])
                        team_cost += float(players_df.at[k, 'now_cost'])
                        
                        fwds = new_fwds
                        break
      
    gks.append(bench_gk)
    
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
        else:
            bench.append(f)
    
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
    with open('../data/team/team' + str(gameweek) + '.csv', mode='w') as team_file:
        writer = csv.writer(team_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for x in gks:
            newtuple = (x[0], x[2], 'gk')
            writer.writerow(newtuple)
        for x in defs:
            newtuple = (x[0], x[2], 'def')
            writer.writerow(newtuple)
        for x in mids:
            newtuple = (x[0], x[2], 'mid')
            writer.writerow(newtuple)
        for x in fwds:
            newtuple = (x[0], x[2], 'fwd')
            writer.writerow(newtuple)


# Update the team for the next gameweek
def update_team():
    team_path = '../data/team/team' + str(gameweek -1) + '.csv'
    with open(team_path, newline='') as f:
        reader = csv.reader(f)
        old_team = list(reader)
        #print(old_team)
        team_preds = []   # Position, id, prediction
        gks = []
        defs = []
        mids = []
        fwds = []
        team = []
        team_val = 0
        transfers = []
        delta_changes = 0 # The desire for a wildcard
        
        for i in range(len(old_team)):
            o = old_team[i]
            if(len(o) != 0): 
                if(o[0] != ''):    
                    team.append(o)

        for t in range(total):    # Get predictions for current team
            play_id = players_df.at[t, 'id']
            for i in range(len(team)):
                if(play_id == int(team[i][1])):
                    
                    # Add to position lists
                    player = (team[i][0].replace(' (C)', ''), team[i][1], t, team[i][2], play_id)
                    if team[i][2] == 'gk':
                        gks.append(player)
                    elif team[i][2] == 'def':
                        defs.append(player)
                    elif team[i][2] == 'mid':
                        mids.append(player)
                    elif team[i][2] == 'fwd':
                        fwds.append(player)
                        
                    # Predictions
                    team_val += players_df.at[t, 'now_cost']
                    name = players_df.at[t, 'web_name']
                    pos = players_df.at[t, 'element_type']
                    team_preds.append((name, t, play_id, preds_next[t], preds_5[t], pos))

        for t in range(total):
            for p in team_preds:
                # If affordable, worthwhile and same pos
                if(validswap(players_df.at[t, 'now_cost'], players_df.at[p[1], 'now_cost'], team_val) and (preds_5[t] > (p[4] + 5*transfer_threshold)) and (p[5] == players_df.at[t, 'element_type'])):
                    y = False
                    for x in transfers: 
                        if(x[0] == p[0] or x[2] == players_df.at[t, 'web_name']):  #If neither players are already involved in a transfer
                            y = True
                    if y == False:  
                        transfers.append((p[0], p[2], players_df.at[t, 'web_name'], players_df.at[t, 'id'], preds_5[t] - p[4], t))  # Current player, id, new player, id, gain, new position
                        delta_changes+=1
                    
        # MAKE TRANSFERS PROPOSED
        sorted_transfers = sorted(transfers, key=lambda x: x[4], reverse = True)
        
        if(stats == True):
            for x in sorted_transfers:
                print(x[0] + " to " + x[2] + " (" + str(x[4]) + ")")
          
        if(delta_changes >= delta_threshold and wildcard):
            top_transfers = sorted_transfers
            print("WILDCARD!")
        else:
            top_transfers = []
            if(len(sorted_transfers) >= num_transfers):
                for x in range(num_transfers):
                    top_transfers.append(sorted_transfers[x]) # Append transfers to be made
                    print(top_transfers[x][0] + " to " + top_transfers[x][2])
        
        for g in range(len(gks)):
            for t in top_transfers:
                if t[1] == gks[g][1]:
                    name =  t[2] + ' (' + get_team(players_df.at[t[5], 'team']) + ')'
                    gks[g] = (name, t[3], t[5], 'gk', t[3])  # name, id, where, pos, id
        for g in range(len(defs)):
            for t in top_transfers:
                if t[1] == int(defs[g][1]):
                    name =  t[2] + ' (' + get_team(players_df.at[t[5], 'team']) + ')'
                    defs[g] = (name, t[3], t[5], 'def', t[3])
        for g in range(len(mids)):
            for t in top_transfers:
                if t[1] == int(mids[g][1]):
                    name =  t[2] + ' (' + get_team(players_df.at[t[5], 'team']) + ')'
                    mids[g] = (name, t[3], t[5], 'mid', t[3])
        for g in range(len(fwds)):
            for t in top_transfers:
                if t[1] == int(fwds[g][1]):
                    name =  t[2] + ' (' + get_team(players_df.at[t[5], 'team']) + ')'
                    fwds[g] = (name, t[3], t[5], 'fwd', t[3])
                    
              
         # Print predictions per player 
        if (stats == True):
            for g in gks:
                print(str(preds_next[g[2]]) + ' ' + g[0] + ' ' + str(g[2]) + ' ' + str(players_df.at[g[2], 'id']))
            for g in defs:
                print(str(preds_next[g[2]]) + ' ' + g[0] + ' ' + str(g[2]) + ' ' + str(players_df.at[g[2], 'id']))
            for g in mids:
                print(str(preds_next[g[2]]) + ' ' + g[0] + ' ' + str(g[2]) + ' ' + str(players_df.at[g[2], 'id']))
            for g in fwds:
                print(str(preds_next[g[2]]) + ' ' + g[0] + ' ' + str(g[2]) + ' ' + str(players_df.at[g[2], 'id']))
        
        # FIND BEST TEAM
        best_gk = gks[0]
        bench_gk = gks[1]
        starting_team = []
        bench = []
        for d in defs:
            starting_team.append(d)  # Defenders will always fit
        for m in mids:
            starting_team.append(m)  # Mids will just about fit
        for f in fwds:
            lowest = starting_team[0]
            for s in starting_team:  # Find lowest scoring player
                if(preds_next[s[2]] < preds_next[lowest[2]]):
                    lowest = s
            if (preds_next[f[2]] > preds_next[lowest[2]]):
                bench.append(lowest)
                new_team = [n for n in starting_team if n[0] != lowest[0]]
                new_team.append(f)
                starting_team = new_team
            else:
                bench.append(f)
        
        # Find captain
        captain = (best_gk)
        for s in starting_team:
            if (preds_next[s[2]] > preds_next[captain[2]]):
                captain = s
        for pos in range(len(starting_team)):   # Apply (C) for captain
            if (starting_team[pos][0] == captain [0]):
                lst = list(starting_team[pos])
                lst[0] += ' (C) '
                s = tuple(lst)
                starting_team[pos] = s
                
        # Order bench
        bench.sort(reverse = True, key = lambda b: preds_next[b[2]])
                
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
        with open('../data/team/team' + str(gameweek) + '.csv', mode='w') as team_file:
            writer = csv.writer(team_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for x in gks:
                newtuple = (x[0], x[4], 'gk')
                writer.writerow(newtuple)
            for x in defs:
                newtuple = (x[0], x[4], 'def')
                writer.writerow(newtuple)
            for x in mids:
                newtuple = (x[0], x[4], 'mid')
                writer.writerow(newtuple)
            for x in fwds:
                newtuple = (x[0], x[4], 'fwd')
                writer.writerow(newtuple)
                    
            
            

#
# PREDICT
# 
            
# MANUAL VARIABLES
new = False  # Make a new team or update existing
total = 554  # total players
gameweek = 4  # gameweek
budget = 996  # total budget
stats = True # show stats
num_transfers = 1 # transfers available
pos_forward_modifier = 0.75 # modifier if player is more forward than last season
pos_back_modifier = 1.2  # modifier if player is more defensive than last season
minutes_threshold = 2291 # threshold under which players are ignored for not playing enough (not in use)
transfer_threshold = 2.0 # threshold for making a transfer
season_started = True # True if the season has started, False otherwise
delta_threshold = 6 # The threshold at which wildcard will be triggered
wildcard = True # If the wildcard is available

# Position changes
changes = {'id': [4, 26, 50, 51, 166, 149, 168, 266, 303, 306, 315, 322, 355, 358, 399, 391, 437, 468], 
           'change': ['b', 'b', 'f', 'f', 'f', 'f', 'b', 'b', 'f', 'b', 'b', 'f', 'f', 'f', 'b', 'b', 'f', 'b']}

changes_df = pd.DataFrame (changes, columns = ['id','change'])

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

for i in range(1, total+1): #total+1  # i is meant to be player position
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
                    last_minutes = h[5]
        
        # MAKE PREDICTIONS
        last_season_weight = math.log10(8-gameweek)  # Weight of past season should decrease over time
        
        last_total = last_total * changed_position(i-1)# Apply a modifier if player changes pos
        '''
        if(form == 0.0): # if no form
            pred_5 = (ppg  * ((diffi_5/average) ** math.e))
            pred_next = (ppg * ((diffi_next/average) ** math.e))
        else:
            pred_5 = ((ppg + form) /2 * ((diffi_5/average) ** math.e))
            pred_next = ((ppg + form) /2 * ((diffi_next/average) ** math.e))
        '''
        if(form == 0.0 and not season_started): # if no form
            pred_5 = (((ppg + (last_total / 38)) /2)  * (5*((diffi_5/(average*5)) ** math.e))) * chance_to_play(i-1)
            pred_next = (((ppg + (last_total / 38)) /2) * ((diffi_next/average) ** math.e))  * chance_to_play(i-1)
            
        elif(last_total == 0.0): # Not fair to include last season as a 0 if the player didn't play
            pred_5 = ((ppg + form)/2  * (5*((diffi_5/(5*average)) ** math.e)))  * chance_to_play(i-1) * (1-last_season_weight)
            pred_next = ((ppg + form)/2 * ((diffi_next/(average)) ** math.e))  * chance_to_play(i-1) * (1-last_season_weight)
            #pred_5 = (((2 * last_season_weight) + ((ppg + form)/2 * (1- last_season_weight))) /2 * (5*((diffi_5/(5*average)) ** math.e)))  * chance_to_play(i-1)
            #pred_next = (((2 * last_season_weight) + ((ppg + form)/2 * (1- last_season_weight))) /2 * ((diffi_next/(average)) ** math.e))  * chance_to_play(i-1)
        
        else:
            pred_5 = ((((last_total / 38) * last_season_weight) + ((ppg + form)/2 * (1- last_season_weight))) /2 * (5*((diffi_5/(5*average)) ** math.e)))  * chance_to_play(i-1)
            pred_next = ((((last_total / 38) * last_season_weight) + ((ppg + form)/2 * (1- last_season_weight))) /2 * ((diffi_next/(average)) ** math.e))  * chance_to_play(i-1)
        
        # Check if misses next match
        if(player_fix[0]['event_name'] != ("Gameweek " + str(gameweek))):
            pred_5-=pred_next
            pred_next = 0
        # Add to array
        preds_5.append(pred_5)
        preds_next.append(pred_next)

if new == True:      
    create_team()
elif new == False:
    update_team()
                

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