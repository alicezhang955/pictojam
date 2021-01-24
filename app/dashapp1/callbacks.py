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
from urllib import parse

def get_data_from_playlist_id(auth_header, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    querystring = {'market': "US", 'offset': 0}
    headers = auth_header
    
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

def get_matrix_from_ids(auth_header, ids):
    start = 0
    keys = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness','liveness','valence']
    matrix = [np.zeros((len(ids), len(keys)))]
    while start < len(ids):
        querystr = ''
        for id_ in ids[start:start+100]:
            querystr += id_+','

        url = "https://api.spotify.com/v1/audio-features"
        querystring = {"ids":querystr}
        headers = auth_header

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

def compare_playlists(auth_header, playlist_ids):
    matrix = []
    c = []
    song_names = []
    artist_names = []
    add_dates = []
    index = 0
    for playlist_id in playlist_ids:
        song_ids, new_song_names, new_artist_names, new_add_dates = get_data_from_playlist_id(auth_header, playlist_id)
        song_names.extend(new_song_names)
        artist_names.extend(new_artist_names)
        add_dates.extend(new_add_dates)
        new_matrix = get_matrix_from_ids(auth_header, song_ids)
        if len(matrix) != 0:
            if len(new_matrix) != 0:
                matrix = np.vstack((matrix, new_matrix))
        else:
            matrix = new_matrix
        c.extend([index]*len(new_matrix))
        index += 1

    return matrix, c, song_names, artist_names, add_dates

def get_playlist_names_from_ids(auth_header, playlist_ids):
  playlist_names = []
  for playlist_id in playlist_ids:
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = auth_header
    
    response = requests.request("GET", url, headers = headers)
    name = json.loads(response.text)["name"]
    playlist_names.append(name)
  return playlist_names


def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value'), Input('my-dropdown2', 'value'), Input('url','search')])
    def update_graph(value1, value2, search):
      if search is not None:
        parsed = parse.parse_qs(search)
        playlist_ids = list(parsed.keys())[1:]
        auth_header = json.loads(parsed[list(parsed.keys())[0]][0].replace('\'','\"'))
        playlist_ids[0] = playlist_ids[0] # remove leading "?"

        matrix, c, song_names, artist_names, add_dates = compare_playlists(auth_header, playlist_ids)
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

        playlist_names = get_playlist_names_from_ids(auth_header, playlist_ids)

        X = matrices[value1]
        if value2 == "PLAYLIST":
          # create one trace per playlist
          fig = go.Figure()
          for playlist_index in range(np.max(c)+1):
            fig.add_trace(go.Scatter(name=f'{playlist_names[playlist_index]}',x = X[playlist_indices[playlist_index]][:,0], y = X[playlist_indices[playlist_index]][:,1], mode = 'markers+text', marker = {
              'color': playlist_index
            }, hoverinfo = "text", hovertext = [song_names[i] + " — " + artist_names[i] for i in list(playlist_indices[playlist_index])[0]]  ))
        elif value2 == "DATE":
          # create one trace per playlist
          fig = go.Figure()
          for playlist_index in range(np.max(c)+1):
            fig.add_trace(go.Scatter(name=f'{playlist_names[playlist_index]}',x = X[playlist_indices[playlist_index]][:,0], y = X[playlist_indices[playlist_index]][:,1], mode = 'markers+text', marker = {
              'color': days_ago, 'cmin': min(days_ago), 'cmax': max(days_ago), 'colorbar': {'thickness': 20, 'title': 'Days ago added'}
            }, hoverinfo = "text", hovertext = [song_names[i] + " — " + artist_names[i] for i in list(playlist_indices[playlist_index])[0]]  ))
        

        # update plotly layout to remove axes
        fig.update_layout(xaxis = {
              'visible': False,
              'showgrid': False,
              'zeroline': False,
            },
            yaxis = {
              'visible': False,
              'showgrid': False,
              'zeroline': False,
            },
            hovermode='closest',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)')
        
        if value1=="PLAYLIST":
          fig.update_layout(showlegend = True)
        elif value1=="DATE":
          fig.update_layout(showlegend = False)

        return fig
      else:
        return html.H1("Loading...")
