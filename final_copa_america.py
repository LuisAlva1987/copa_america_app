import streamlit as st
import pandas as pd
import numpy as np
from pandas import json_normalize
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
       <center><h1 class="title-test">Copa America Final</h1></center>"""
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

## Set up for first three columns
col1, col2, col3=st.columns(3) 
###############################################################
##PASSES
with col1:
       st.write("PASSES")
## Create figure and pitch
       pitch = VerticalPitch(
       half=False,
       pitch_type = 'statsbomb',
       axis=True,
       #label=True,
       #tick=True,
       goal_type='box'
       )

       fig, ax = pitch.draw(figsize=(10, 10))
       ax.title.set_text('Passes')

# Player complete passes 
       player_complete_pases_first = filtered_df.loc[(filtered_df['type'] == 'Pass')        
                                          & (filtered_df['pass_outcome'].isna()), ##
                                          ['timestamp', 'player', 'pass_recipient', 'pass_outcome', 'location', 'pass_end_location']]
       player_complete_pases_first[['x', 'y']] = player_complete_pases_first['location'].apply(pd.Series) ## pass beginning location
       player_complete_pases_first[['end_x', 'end_y']] = player_complete_pases_first['pass_end_location'].apply(pd.Series) ## pass end location
## Arrows for complete passes
       player_complete_pases_first = player_complete_pases_first[player_complete_pases_first['player'] == player]
       pitch.arrows(player_complete_pases_first['x'], player_complete_pases_first['y'], player_complete_pases_first['end_x'], player_complete_pases_first['end_y'], ax=ax,
              label='Complete Passes', color='green', width=2)

# Player incomplete passes 
       player_incomplete_pases_first = filtered_df.loc[(filtered_df['type'] == 'Pass') 
                                          & (~filtered_df['pass_outcome'].isna()), 
                                          ['timestamp', 'player', 'pass_recipient', 'pass_outcome', 'location', 'pass_end_location']]
       player_incomplete_pases_first[['x', 'y']] = player_incomplete_pases_first['location'].apply(pd.Series) ## pass beginning location
       player_incomplete_pases_first[['end_x', 'end_y']] = player_incomplete_pases_first['pass_end_location'].apply(pd.Series) ## pass end location
## Arrows for imcomplete pases
       player_incomplete_pases_first = player_incomplete_pases_first[player_incomplete_pases_first['player'] == player]
       pitch.arrows(player_incomplete_pases_first['x'], player_incomplete_pases_first['y'], player_incomplete_pases_first['end_x'], player_incomplete_pases_first['end_y'], ax=ax,
            label='Complete Passes', color='red', width=2)

       plt.legend(loc="lower left")
       st.pyplot(fig)


####################################
## BALL RECOVERY
with col2:
       st.write("BALL RECOVERY")
## Create figure and pitch
       pitch = VerticalPitch(
       half=False,
       pitch_type = 'statsbomb',
       axis=True,
       #label=True,
       #tick=True,
       goal_type='box'
       )

       fig, ax = pitch.draw(figsize=(10, 10))
       ax.title.set_text('Ball Recovery')
## Player ball recovery
       player_ball_recovery = filtered_df.loc[(filtered_df['type'].isin(['Interception', 'Ball Recovery']))
                                              | (filtered_df['pass_type'].isin(['Recovery', 'Interception'])),
                                              ['timestamp', 'player', 'type', 'pass_type', 'pass_recipient', 'possession', 'pass_outcome', 'location', 'pass_end_location']]

       player_ball_recovery['recovery_location'] = np.where(player_ball_recovery['pass_end_location'].isna(), player_ball_recovery['location'], player_ball_recovery['pass_end_location'])
       player_ball_recovery[['x', 'y']] = player_ball_recovery['recovery_location'].apply(pd.Series) ## pass location

       recovery_pass_type = filtered_df.loc[filtered_df['pass_type'].isin(['Recovery', 'Interception']), 
                                           ['timestamp', 'player', 'type', 'pass_type', 'pass_recipient', 'possession', 'pass_outcome', 'location', 'pass_end_location']]

       recovery_pass_type['recovery_location'] = np.where(recovery_pass_type['pass_end_location'].isna(), recovery_pass_type['location'], recovery_pass_type['pass_end_location'])
       recovery_pass_type[['x', 'y']] = recovery_pass_type['recovery_location'].apply(pd.Series)

       player_ball_recovery = player_ball_recovery[player_ball_recovery['player'] == player]
       pitch.scatter(player_ball_recovery['x'], player_ball_recovery['y'], label='Recover Balls', color='green', ax=ax)

       recovery_pass_type = recovery_pass_type[recovery_pass_type['player'] == player]
       pitch.scatter(recovery_pass_type['x'], recovery_pass_type['y'], label='Recover Balls', color='green', ax=ax)

       st.pyplot(fig)
##########################################################################################
# Event type per Team
colombia_events = final[final['possession_team'] == 'Colombia']['type'].value_counts().reset_index(name = 'colombia')
argentina_events = final[final['possession_team'] == 'Argentina']['type'].value_counts().reset_index(name = 'argentina')
final_events = pd.merge(colombia_events, argentina_events, on='type')

col4, col5=st.columns([1, 2.2])
with col4:
       final_events_table = final_events.set_index('type')
       st.write("Event Type per Team")
       st.dataframe(final_events_table)

# Events type per team barchart
with col5:
       fig = px.bar(final_events, x= "type", y=["colombia", "argentina"], labels = {"type" : "Event Type", "value": "Event Count"}, 
             title= "Event Type Per Team", barmode='group', height=500, template="gridon", color_discrete_sequence=["red", "#66d9ff"])
# Change leyend lebels and tile
       fig.update_layout(legend_title_text="Teams")
       new = {'colombia':'Colombia', 'argentina': 'Argentina'}
       fig.for_each_trace(lambda t: t.update(name = new[t.name]))
       st.plotly_chart(fig, use_container_width=True)

col6, col7, col8=st.columns(3)     
with col6:
        possession_count = final.groupby(['possession', 'possession_team'])['possession_team'].count().reset_index(name='possession_count')
        possession_count = possession_count.groupby('possession_team')['possession'].count().reset_index(name='possession_count')
        st.write("Possesion Count by Team")
        st.table(possession_count) 

with col7: 
       playing_time = round(final['duration'].sum()/60, 2)
       st.write("Total Playing Team")
       st.write(playing_time) 

with col8:
       playing_time_by_team = round(final.groupby('possession_team')['duration'].sum()/60, 2).reset_index(name = 'possesion_time') 
       st.write("Playing Time by Team")
       st.table(playing_time_by_team) 



