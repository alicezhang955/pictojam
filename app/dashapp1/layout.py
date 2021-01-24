import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    dcc.Location(id='url',refresh=False),
    html.Div([
      html.A(["Pictojams"], style = {'color': 'white', 'text-decoration': 'none', 'font-weight': '700'})
    ], style = {'background-color': '#0A100D', 'height': '2.5em', 'text-align': 'center', 'align-self': 'stretch'}),
    
    html.Div([
      html.Div(style=dict(flex=2)),
      html.Div([dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'PCA', 'value': 'PCA'},
            {'label': 't-SNE', 'value': 'TSNE'},
            {'label': 'PHATE', 'value': 'PHATE'}
        ],
        value='PCA',
        placeholder = 'Select visualization technique'
      )], style = {'verticalAlign':'middle','flex':1, 'font-size': '0.7em', 'padding': '2%'}),
      
      html.Div([dcc.Dropdown(
        id="my-dropdown2",
        options=[
          {'label': 'Color by playlist', 'value': 'PLAYLIST'},
          {'label': 'Color by add date', 'value': 'DATE'}
        ],
        value = 'PLAYLIST',
      )], style = {'verticalAlign':'middle','flex':1, 'font-size': '0.7em', 'padding': '2%'}),
      html.Div(style=dict(flex=2)),
    ], style = {'display': 'flex', 'align-self': 'stretch', 'margin-top': '4%', 'margin-bottom': '1%'}),
    dcc.Graph(id='my-graph', style = {'align-self': 'stretch'}),
    html.P("Some songs may have not been included due to errors in fetching from Spotify's API. ", style = {'font-size': '0.4rem'})
], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'space-between', 'align-items': 'center','width': '100%', 'font-size': '2em', 'font-family': 'Inter', 'margin': '0', 'padding': '0','background-color': '#D7DFF3'})
