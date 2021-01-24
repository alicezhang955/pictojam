import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    html.H1('Visualization:'),
    html.Div([
      html.Div([dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'PCA', 'value': 'PCA'},
            {'label': 't-SNE', 'value': 'TSNE'},
            {'label': 'PHATE', 'value': 'PHATE'}
        ],
        value='PCA'
      )], style = {'width': '48%'}),
      html.Div([dcc.Dropdown(
        id="my-dropdown2",
        options=[
          {'label': 'Color by playlist', 'value': 'PLAYLIST'},
          {'label': 'Color by add date', 'value': 'DATE'}
        ],
        value = 'PLAYLIST'
      )], style = {'width': '48%'})
    ], style = {'width': '100%', 'display': 'flex'}),
    dcc.Graph(id='my-graph'),
    html.P("Some songs may have not been included due to errors in fetching from Spotify's API. ")
], style={'width': '80%'})
