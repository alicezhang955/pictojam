from datetime import datetime as dt

from dash.dependencies import Input
from dash.dependencies import Output

import dash
import dash_core_components as dcc 
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
from flask import Flask

import numpy as np
import requests
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import phate
import json
import pandas as pd

# TODO: 
# REPLACE AUTH CODE
auth_code = "BQBpEAFlkO0tKaQZVCKWrR9JO7Jni5O2gzS5f2rGocvpjbBxIQwz6UiYnl8dV9ZkmjBopJ4mzfBy8Oc4ByFswKPCaaWZR1vIOruQa9W-slquzRZbJDzJJdBgxZPuM9UsSUf6zuLjaWMEBgPlNcbUdYZzbCnuzX5G4iM"

def get_data_from_playlist_id(auth_code, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    querystring = {'market': "US", 'offset': 0}
    headers = {
        'Authorization': f"Bearer {auth_code}",
        }
    
    response = requests.request("GET", url, headers = headers, params=querystring)
    next_search_url = json.loads(response.text)['next']
    items = json.loads(response.text)
    items = items['items']
    ids = [items[index]['track']['id'] for index in np.arange(len(items))]
    song_names = [items[index]['track']['name'] for index in np.arange(len(items))]
    artist_names = [items[index]['track']['artists'][0]['name'] for index in np.arange(len(items))]
    add_dates = [items[index]['added_at'] for index in np.arange(len(items))]
    
    while next_search_url is not None:
        response = requests.request("GET", next_search_url, headers = headers)
        next_search_url = json.loads(response.text)['next']
        items = json.loads(response.text)
        items = items['items']
        next_ids = [items[index]['track']['id'] for index in np.arange(len(items))]
        next_song_names = [items[index]['track']['name'] for index in np.arange(len(items))]
        next_artist_names = [items[index]['track']['artists'][0]['name'] for index in np.arange(len(items))]
        next_add_dates = [items[index]['added_at'] for index in np.arange(len(items))]
        ids.extend(next_ids)
        song_names.extend(next_song_names)
        artist_names.extend(next_artist_names)
        add_dates.extend(next_add_dates)
    
    return ids, song_names, artist_names, add_dates

def get_matrix_from_ids(auth_code, ids):
    start = 0
    keys = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness','liveness','valence']
    matrix = [np.zeros((len(ids), len(keys)))]
    while start < len(ids):
        querystr = ''
        for id_ in ids[start:start+100]:
            querystr += id_+','

        url = "https://api.spotify.com/v1/audio-features"
        querystring = {"ids":querystr}
        headers = {
            'Authorization': f"Bearer {auth_code}",
            }

        response = requests.request("GET", url, headers = headers, params=querystring)
        if len(response.text) == 0:
            if start == 0:
                return []
            return matrix[:start+100]
        text = response.json()
        text = text['audio_features']

        indices = np.arange(len(text))
        stack = np.vstack([[text[index][key] for key in keys] for index in indices])
        matrix[start:start+100] = stack

        start += 100
    return matrix

def compare_playlists(auth_code, playlist_ids):
    matrix = []
    c = []
    song_names = []
    artist_names = []
    add_dates = []
    index = 0
    for playlist_id in playlist_ids:
        song_ids, new_song_names, new_artist_names, new_add_dates = get_data_from_playlist_id(auth_code, playlist_id)
        song_names.extend(new_song_names)
        artist_names.extend(new_artist_names)
        add_dates.extend(new_add_dates)
        new_matrix = get_matrix_from_ids(auth_code, song_ids)
        if len(matrix) != 0:
            if len(new_matrix) != 0:
                matrix = np.vstack((matrix, new_matrix))
        else:
            matrix = new_matrix
        c.extend([index]*len(new_matrix))
        index += 1

    return matrix, c, song_names, artist_names, add_dates



# TODO: 
# REPLACE PLAYLIST IDS

matrix, c, song_names, artist_names, add_dates = compare_playlists(auth_code, ["1B8ML30C5MhYOTdhhyYoyf", "32Q28zp4kNJdlp3ySJY7b9", "17NdZwoykVi8d5HZvCS2oT", "652AoU9fV6NuMSVLNuECKJ"])
playlist_indices = {}
for i in range(np.max(c)+1):
    playlist_indices[i] = np.where(np.array(c) == i)

import dateutil.parser as dparser
import datetime
date_objs = [dparser.parse(date) for date in add_dates]
date_strs = [obj.strftime('%Y-%m-%d') for obj in date_objs]
days_ago = [(datetime.datetime.now().date() - date.date()).days for date in date_objs]

matrices = {
  "PCA": PCA(n_components = 2).fit_transform(matrix),
  "TSNE": TSNE(n_components=2).fit_transform(matrix),
  "PHATE": phate.PHATE(verbose = False).fit_transform(matrix),
}


def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value'), Input('my-dropdown2', 'value')])
    def update_graph(value1, value2):
      X = matrices[value1]
      if value2 == "PLAYLIST":
        # create one trace per playlist
        fig = go.Figure()
        for playlist_index in range(np.max(c)+1):
          fig.add_trace(go.Scatter(name=f'Playlist {playlist_index+1}',x = X[playlist_indices[playlist_index]][:,0], y = X[playlist_indices[playlist_index]][:,1], mode = 'markers+text', marker = {
            'color': playlist_index
          }, hoverinfo = "text", hovertext = [song_names[i] + " — " + artist_names[i] for i in list(playlist_indices[playlist_index])[0]]  ))
      elif value2 == "DATE":
        # create one trace per playlist
        fig = go.Figure()
        for playlist_index in range(np.max(c)+1):
          fig.add_trace(go.Scatter(name=f'Playlist {playlist_index+1}',x = X[playlist_indices[playlist_index]][:,0], y = X[playlist_indices[playlist_index]][:,1], mode = 'markers+text', marker = {
            'color': days_ago
          }, hoverinfo = "text", hovertext = [song_names[i] + " — " + artist_names[i] for i in list(playlist_indices[playlist_index])[0]]  ))
      

      # update plotly layout to remove axes
      fig.update_layout(title='Title', xaxis = {
            'visible': False,
            'showgrid': False,
            'zeroline': False,
          },
          yaxis = {
            'visible': False,
            'showgrid': False,
            'zeroline': False,
          },
          showlegend = True,
          hovermode='closest')

      return fig
