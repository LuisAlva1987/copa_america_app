import streamlit as st
import pandas as pd
import numpy as np
from pandas import json_normalize
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from mplsoccer import Pitch, VerticalPitch
import requests
pd.set_option('display.max_columns', None)
from statsbombpy import sb

# Download compatition data set to find Copa America
sb.competitions()

# Command to select matches from the Copa America and identify final
sb.matches(competition_id = 223, season_id = 282).sort_values(by='match_date')

# Get final data
final = sb.events(match_id = 3943077)
final = sb.events(match_id = 3943077)
final[['x', 'y']] = final['location'].apply(pd.Series) ## pass beginning location
final[['shot_end_x', 'shot_end_y', 'shot_height']] = final['shot_end_location'].apply(pd.Series) ## shot end location
final[['pass_end_x', 'pass_end_y']] = final['pass_end_location'].apply(pd.Series) ## pass end location
final['recovery_location'] = np.where(final['pass_end_location'].isna(), final['location'], final['pass_end_location'])
final[['recovery_x', 'recovery_y']] = final['recovery_location'].apply(pd.Series) ## pass location

# Game Events 
final['type'].value_counts().reset_index(name='event_count')

st.set_page_config(layout="wide")

## Dashboard Title
html_title =  """
       <style>
       .title-test {
       font-weight:bold;
       padding:5px;
       border-radius:6px;
       }
       </style>
       <center><h1 class="title-test">Copa America Final Game</h1></center>"""
st.markdown(html_title, unsafe_allow_html=True)

## Dashboard Subtitle
html_subtitle =  """
       <style>
       .title-test {
       padding:3px;
       border-radius:3px;
       }
       </style>
       <center><h3 class="title-test">Colombia vs Argentina</h3></center>"""
st.markdown(html_subtitle, unsafe_allow_html=True)

## Select boxes
team = st.selectbox('Select a team', final['team'].sort_values().unique(), index=None)
player = st.selectbox('Select a player', final[final['team'] == team]['player'].sort_values().unique())

## Create a filter function
def filter_data(final, team, player):
       if team:
              final  = final[final['team'] == team]
       if player:
              final = final[final['player'] == player]
       return  final

## Run the function
filtered_df = filter_data(final, team, player)

## Set up for first row three columns
col1, col2, col3=st.columns(3) 
###############################################################

##PASSES
with col1:
       st.write("PASSES")      
       player_passes = filtered_df.loc[(filtered_df['type'] == 'Pass'),
                                      ['timestamp', 'player', 'pass_recipient', 'pass_outcome', 'x', 'y', 'pass_end_x', 'pass_end_y']]
       if not player_passes['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half=False,
              pitch_type = 'statsbomb',
              axis=True,
              goal_type='box'
              )

              fig, ax = pitch.draw(figsize=(10, 10))

## Player complete passes 
              player_complete_passes = player_passes.loc[(player_passes['pass_outcome'].isna()), 
                                                 ['timestamp', 'player', 'pass_recipient', 'pass_outcome', 'x', 'y', 'pass_end_x', 'pass_end_y']]
              player_complete_passes = player_complete_passes[player_complete_passes['player'] == player]
              pitch.arrows(player_complete_passes['x'], player_complete_passes['y'], player_complete_passes['pass_end_x'], player_complete_passes['pass_end_y'], ax=ax,
              label='Complete Passes', color='green', width=2)

## Player incomplete passes 
              player_incomplete_pases = player_passes.loc[(~player_passes['pass_outcome'].isna()), 
                                          ['timestamp', 'player', 'pass_recipient', 'pass_outcome', 'x', 'y', 'pass_end_x', 'pass_end_y']]
              player_incomplete_pases = player_incomplete_pases[player_incomplete_pases['player'] == player]
              pitch.arrows(player_incomplete_pases['x'], player_incomplete_pases['y'], player_incomplete_pases['pass_end_x'], player_incomplete_pases['pass_end_y'], ax=ax,
              label='Incomplete Passes', color='red', width=2)
              plt.legend(loc="upper left")
              st.pyplot(fig)

       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              plt.legend(loc="upper left", title='No passes made by player')
              st.pyplot(fig)


#############################################################

## BALL RECOVERY
with col2:
       st.write("BALL RECOVERY")
       player_ball_recovery = filtered_df.loc[(filtered_df['type'].isin(['Interception', 'Ball Recovery']))
                                              | (filtered_df['pass_type'].isin(['Recovery', 'Interception'])),
                                              ['timestamp', 'player', 'type', 'pass_type', 'pass_recipient', 'possession', 'pass_outcome', 'recovery_x', 'recovery_y']]

       if not player_passes['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half=False,
              pitch_type = 'statsbomb',
              axis=True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
## Player ball recovery
              player_ball_recovery = player_ball_recovery[player_ball_recovery['player'] == player]
              pitch.scatter(player_ball_recovery['recovery_x'], player_ball_recovery['recovery_y'], label='Recovered Balls', color='green', ax=ax)

              plt.legend(loc="upper left")
              st.pyplot(fig) 
       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              plt.legend(loc="upper left", title='No balls recovered by player')
              st.pyplot(fig)

#############################################################

## SHOTS
with col3:
 ## Player saved shots
       st.write("SHOTS")      
       player_shots = filtered_df.loc[(filtered_df['type'] == 'Shot')
                                      & (filtered_df['shot_outcome'].isin(['Saved', 'Blocked', 'Off T', 'Goal', 'Wayward'])),
                                      ['possession_team', 'player', 'type', 'shot_outcome', 'x', 'y', 'shot_end_x', 'shot_end_y']]

       if not player_shots['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half =False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
## Player saved shots
              player_saved_shots = player_shots.loc[(player_shots['shot_outcome'] == 'Saved'),
                                      ['possession_team', 'player', 'type', 'shot_outcome', 'x', 'y', 'shot_end_x', 'shot_end_y']]
              player_saved_shots = player_saved_shots[player_saved_shots['player'] == player]
              pitch.scatter(player_saved_shots['x'], player_saved_shots['y'], color='yellow', ax=ax)
              pitch.arrows(player_saved_shots['x'], player_saved_shots['y'], player_saved_shots['shot_end_x'], player_saved_shots['shot_end_y'], label='Saved Shots', color='yellow', width=2, ax=ax)

## Player blocked shots 
              player_blocked_shots = player_shots.loc[(player_shots['shot_outcome'] == 'Blocked'),
                                             ['possession_team', 'player', 'type', 'shot_outcome', 'x', 'y', 'shot_end_x', 'shot_end_y']]
              player_blocked_shots = player_blocked_shots[player_blocked_shots['player'] == player]
              pitch.scatter(player_blocked_shots['x'], player_blocked_shots['y'], color='blue', ax=ax)
              pitch.arrows(player_blocked_shots['x'], player_blocked_shots['y'], player_blocked_shots['shot_end_x'], player_blocked_shots['shot_end_y'], label='Blocked Shots', color='blue', width=2, ax=ax)

## Player Off T
              player_offt_shots = player_shots.loc[(player_shots['shot_outcome'] == 'Off T'),
                                          ['possession_team', 'player', 'type', 'shot_outcome', 'x', 'y', 'shot_end_x', 'shot_end_y']]
              player_offt_shots = player_offt_shots[player_offt_shots['player'] == player]
              pitch.scatter(player_offt_shots['x'], player_offt_shots['y'], color='red', ax=ax)
              pitch.arrows(player_offt_shots['x'], player_offt_shots['y'], player_offt_shots['shot_end_x'], player_offt_shots['shot_end_y'], label='Off T Shots', color='red', width=2, ax=ax)

## Player Goals
              player_goals = player_shots.loc[(player_shots['shot_outcome'] == 'Goal'),
                                      ['possession_team', 'player', 'type', 'shot_outcome', 'x', 'y', 'shot_end_x', 'shot_end_y']]
              player_goals = player_goals[player_goals['player'] == player]
              pitch.scatter(player_goals['x'], player_goals['y'], color='green', ax=ax)
              pitch.arrows(player_goals['x'], player_goals['y'], player_goals['shot_end_x'], player_goals['shot_end_y'], label='Goals', color='green', width=2, ax=ax)

## Wayward Shot
              player_wayward_shots = player_shots.loc[(player_shots['shot_outcome'] == 'Wayward'),
                                            ['possession_team', 'player', 'type', 'shot_outcome', 'x', 'y', 'shot_end_x', 'shot_end_y']]
              player_wayward_shots = player_wayward_shots[player_wayward_shots['player'] == player]
              pitch.scatter(player_wayward_shots['x'], player_wayward_shots['y'], color='purple', ax=ax)
              pitch.arrows(player_wayward_shots['y'], player_wayward_shots['y'], player_wayward_shots['shot_end_x'], player_wayward_shots['shot_end_y'], label='Wayward Shots', color='purple', width=2, ax=ax)
       
              plt.legend(loc="upper left")
              st.pyplot(fig)
       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              plt.legend(loc="upper left", title='No shots made by player')
              st.pyplot(fig)

#############################################################
## Set up for second row three columns
col4, col5, col6=st.columns(3) 

#############################################################

## FOULS 
with col4:
       st.write("FOULS")      
       player_fouls = filtered_df.loc[(filtered_df['type'] == 'Foul Committed'),
                                      ['player', 'x', 'y']]
       if not player_fouls['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half =False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))    
## Player fouls
              player_fouls = player_fouls[player_fouls['player'] == player]
              pitch.scatter(player_fouls['x'], player_fouls['y'], label='Foul Committed', color='red', ax=ax)

              plt.legend(loc="upper left")
              st.pyplot(fig) 
       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              plt.legend(loc="upper left", title='No Foul Committed by Player')
              st.pyplot(fig)       


#############################################################

## PLAYER HEATMAP  
with col5:
       st.write("PLAYER HEATMAP")      
       player_heatmap = filtered_df[['player', 'x', 'y']]
       if not player_heatmap['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half =False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))  
## Player heatmap
              player_heatmap = player_heatmap[player_heatmap['player'] == player]
              pitch.kdeplot(player_heatmap['x'], player_heatmap['y'], ax=ax, levels=100, shade=True, zorder=-1, shade_lowest=True, cmap='OrRd')     

       ###plt.legend(loc="upper left")
              st.pyplot(fig) 
       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              ##plt.legend(loc="upper left", title='No Player Activity')
              st.pyplot(fig)  

#############################################################

## PLAYER HEATMAP  
with col6:
       st.write("HEATMAP SENT PASSES")   
       pass_heatmap = filtered_df.loc[(filtered_df['type'] == 'Pass') & (filtered_df['pass_outcome'].isna()), ['player', 'type', 'x', 'y']]
       if not pass_heatmap['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half =False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))  
## Player pass heatmap
              pass_heatmap = pass_heatmap[pass_heatmap['player'] == player]
              pitch.kdeplot(pass_heatmap['x'], pass_heatmap['y'], ax=ax, levels=100, shade=True, zorder=-1, shade_lowest=True, cmap='OrRd')     

              ###plt.legend(loc="upper left")
              st.pyplot(fig) 
       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              ##plt.legend(loc="upper left", title='No Player Activity')
              st.pyplot(fig)  


#############################################################
## Set up for third row three columns
col7, col8, col9 =st.columns(3) 

#############################################################

## PLAYER FORWARD & BACK PASSES
with col7:
       st.write("FORWARD & BACK PASSES")   
       pases = filtered_df.loc[(filtered_df['type'] == 'Pass') & (filtered_df['pass_outcome'].isna()), ['player', 'x', 'y', 'pass_end_x', 'pass_end_y']]

       if not pases['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half =False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
## Player forward passes
              forward = pases.loc[(final['x'] < final['pass_end_x']), ['player', 'x', 'y', 'pass_end_x', 'pass_end_y']]
              forward = forward[forward['player'] == player]
              pitch.arrows(forward['x'], forward['y'], forward['pass_end_x'], forward['pass_end_y'], label='Passes Forward', color='green', width=2, ax=ax)

## Player back passes
              back = pases.loc[(final['x'] > final['pass_end_x']), ['player', 'x', 'y', 'pass_end_x', 'pass_end_y']]
              back = back[back['player'] == player]
              pitch.arrows(back['x'], back['y'], back['pass_end_x'], back['pass_end_y'], label='Passes Forward', color='red', width=2, ax=ax)

              plt.legend(loc="upper left")
              st.pyplot(fig) 

       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              ##plt.legend(loc="upper left", title='No Player Activity')
              st.pyplot(fig)

#############################################################

## GOAL/SHOT PASSES
with col8:
       st.write("GOAL/SHOT PASSES")
       goal_passes = final.loc[(final['type'].isin(['Pass', 'Shot'])), ['type', 'shot_outcome', 'player', 'pass_recipient', 'index', 'x', 'y', 'pass_end_x', 'pass_end_y']].sort_values(by = 'index')
       goal_passes['shoter'] = goal_passes['player'].shift(-1)
       goal_passes['type_after'] = goal_passes['type'].shift(-1)
       goal_passes['shot_outcome_after'] = goal_passes['shot_outcome'].shift(-1)
       if not goal_passes['player'].empty:
## Create figure and pitch
              pitch = VerticalPitch(
              half =False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
## Player goal/shots passes
              passer = goal_passes.loc[(goal_passes['type'] == 'Pass') & (goal_passes['type_after'] == 'Shot'),['player', 'shot_outcome_after', 'x', 'y', 'pass_end_x', 'pass_end_y']]
              passer = passer[passer['player'] == player]
              pitch.arrows(passer['x'], passer['y'], passer['pass_end_x'], passer['pass_end_y'], label='Goal/Shot Passes', color='green', width=2, ax=ax)

              plt.legend(loc="upper left")
              st.pyplot(fig)

       else:
              pitch= VerticalPitch (
              half = False,
              pitch_type = 'statsbomb',
              axis = True,
              goal_type='box'
              )
              fig, ax = pitch.draw(figsize=(10, 10))
              plt.legend(loc="upper left", title='No Player Passes')
              st.pyplot(fig)