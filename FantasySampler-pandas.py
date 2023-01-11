# %%
#extracting adn transforming FPL data to plot a graph of top100 overall users player ownership
#first we load all the libraries we will need to extract, transform and load data into our plotly graph

import pandas as pd
import requests
import json
import numpy as np
from collections import Counter
import plotly.express as px
from datetime import datetime

# %%
#We'll start by extracting the current gameweek number and all the footballers in the game via official FPL api
bootstrap_api = 'https://fantasy.premierleague.com/api/bootstrap-static/'

def get_gameweek(url):
    response = requests.get(url)
    response = json.loads(response.text)
    events_df = pd.DataFrame(response['events'])
    today = datetime.now().timestamp()
    events_df = events_df.loc[events_df.deadline_time_epoch>today]
    gameweek =  events_df.iloc[0].id
    return gameweek

# %%


def get_players(url):
    response = requests.get(url)
    response = json.loads(response.text)
    players = pd.json_normalize(response['elements'])
    players_df = pd.DataFrame(players[['id', 'web_name']])
    return players_df

# %%
#Now we have to get the IDs of teams of top {num} of users

def get_ids(num):
    data = []
    for i in range(1,int(num/50)+1):
        response = requests.get(f'https://fantasy.premierleague.com/api/leagues-classic/314/standings/?page_standings={i}')
        response = json.loads(response.text)
        data.append(response)
    
    users = pd.DataFrame.from_dict(data)
    users_df = pd.json_normalize(users.standings)

    #we extract IDs of the users
    ids_lists = users_df['results'].map(lambda x:[i['entry'] for i in x])
    ids = [item for sublist in ids_lists for item in sublist]
    return ids

# %%
#next hting to do is use the IDs of top {num} users to search their teams and extract IDs of players so we can count them
def count_players(teams_ids, gw):
    teams = []
    gw = gw - 1
    for id in teams_ids:
        response = requests.get(f'https://fantasy.premierleague.com/api/entry/{id}/event/{gw}/picks/')
        response=json.loads(response.text)
        teams.append(response)
    teams_df = pd.DataFrame.from_dict(teams)
    picks = teams_df['picks'].map(lambda x:[i['element'] for i in x])
    entries = [item for sublist in picks for item in sublist]
    counted_players = Counter(entries)
    #we sort them so we can merge the IDs with IDs of players from first table and plot it in descending order
    sorted_df = pd.DataFrame.from_dict(counted_players, orient='index').reset_index()
    sorted_df.rename(columns = {0:'SelectedBy'}, inplace = True)
    return sorted_df

# %%
#now all that's left is to sort the counted players and merge their IDs with IDs conected to players names we got from the first api to plot everything

def plot(players, counts):
    gw = get_gameweek(bootstrap_api) - 1
    final_df=players.set_index('id').join(counts.set_index('index'), how='inner')
    sorted_df = final_df.sort_values(by=['SelectedBy'], ascending=False)
    fig = px.bar(sorted_df, y="web_name", x="SelectedBy", title= f"Ownership of players in top100 for GW {gw}", width=1200, height=3000)
    fig.update_layout(
        yaxis = dict(
        tickmode='linear'
    )
)
    fig.update_xaxes(dtick=10, side="top", title_standoff = 5)
    fig.update_yaxes(autorange = "reversed")
    return fig


# %%
gameweek = get_gameweek(bootstrap_api)
players = get_players(bootstrap_api)
ids = get_ids(100)



# %%
counts = count_players(ids, gameweek)


# %%
figure = plot(players, counts)
figure.show()

# %%



