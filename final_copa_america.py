import streamlit as st
import pandas as pd
import numpy as np
from pandas import json_normalize
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch, VerticalPitch
import os #set working directory
import requests
pd.set_option('display.max_columns', None)
from statsbombpy import sb

# set working directory
os.getcwd()

# Download compatition data set to find Copa America
sb.competitions()

# Command to select matches from the Copa America and identify final
sb.matches(competition_id = 223, season_id = 282).sort_values(by='match_date')

# Get final data
final = sb.events(match_id = 3943077)


# Game Events 
final['type'].value_counts().reset_index(name='event_count')

st.set_page_config(layout="wide")
st.header("Copa America Final")
st.subheader('Argentina vs Colombia')

# Event type per Team
colombia_events = final[final['possession_team'] == 'Colombia']['type'].value_counts().reset_index(name = 'colombia')
argentina_events = final[final['possession_team'] == 'Argentina']['type'].value_counts().reset_index(name = 'argentina')
final_events = pd.merge(colombia_events, argentina_events, on='type')
st.dataframe(final_events)


col1, col2, col3=st.columns(3)
with col1:
        possession_count = final.groupby(['possession', 'possession_team'])['possession_team'].count().reset_index(name='possession_count')
        possession_count = possession_count.groupby('possession_team')['possession'].count().reset_index(name='possession_count')
        st.write("Possesion Count by Team")
        st.table(possession_count) 

with col2: 
       playing_time = round(final['duration'].sum()/60, 2)
       st.write("Total Playing Team")
       st.write(playing_time) 

with col3:
       playing_time_by_team = round(final.groupby('possession_team')['duration'].sum()/60, 2).reset_index(name = 'possesion_time') 
       st.write("Playing Time by Team")
       st.table(playing_time_by_team) 

