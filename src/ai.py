# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:21:45 2020

@author: paulb
"""

# Create pandas dataframes
players_df = pd.DataFrame(players)
teams_df = pd.DataFrame(teams)
events_df = pd.DataFrame(events)

# Clean data
events_df['deadline_time'] = pd.to_datetime(events_df['deadline_time'])
events_df['deadline_time'] = events_df['deadline_time'].dt.tz_localize(None)


# Create players predicted points dataframe
preds_df = pd.DataFrame()


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