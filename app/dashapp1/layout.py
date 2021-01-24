import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    dcc.Location(id='url',refresh=False),
    html.Div([
      html.A(["Pictojams"], style = {'color': 'white', 'text-decoration': 'none', 'font-weight': '700', 'font-family': 'sans-serif, Inter'})
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
      )], style = {'verticalAlign':'middle','flex':1, 'font-size': '0.7em', 'padding': '2%', 'font-family': 'sans-serif, Inter'}),
      
      html.Div([dcc.Dropdown(
        id="my-dropdown2",
        options=[
          {'label': 'Color by playlist', 'value': 'PLAYLIST'},
          {'label': 'Color by add date', 'value': 'DATE'}
        ],
        value = 'PLAYLIST',
      )], style = {'verticalAlign':'middle','flex':1, 'font-size': '0.7em', 'padding': '2%', 'font-family': 'sans-serif, Inter' }),
      html.Div(style=dict(flex=2)),
    ], style = {'display': 'flex', 'align-self': 'stretch', 'margin-top': '4%', 'margin-bottom': '1%', 'font-family': 'sans-serif, Inter'}),
    dcc.Graph(id='my-graph', style = {'align-self': 'stretch'}),
    html.P("PCA gives a linear representation of the data that captures the highest variation between points. ", style = {'font-size': '1.2rem', 'font-family': 'sans-serif, Inter'}),
    html.P("t-SNE is a nonlinear technique that makes sure close neighbors stay together from high dimension to low. ", style = {'font-size': '1.2rem', 'font-family': 'sans-serif, Inter'}),
    html.P("PHATE is a newer technique that's nonlinear like t-SNE, but pays more attention to far-away neighbors. ", style = {'font-size': '1.2rem', 'font-family': 'sans-serif, Inter'})
], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'space-between', 'align-items': 'center','width': '100%', 'font-size': '2em', 'font-family': 'sans-serif, Inter', 'margin': '0', 'padding': '0','background-color': '#D7DFF3'})
