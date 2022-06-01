# Import required libraries
import pandas as pd
import numpy as np
import os
from dash import Dash, dash_table, html, dcc, Input, Output, State, no_update
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

data =  pd.read_csv('processedcsv/combinedstats.csv')

# Create a dash application
app = Dash(__name__)

#Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.Div([
        html.Div(id='dummy'),
        html.H1('NHL Data Visualization'),
        dcc.Tabs(id="tabs-example-graph", value='Player Stats Browser', children=[
            dcc.Tab(label='Player Stats Browser', value='Player Stats Browser', children=[
                html.H3('Search By Player'),
                dcc.Textarea(
                    id='search',
                    placeholder='Enter Player Name',
                    value='Sidney Crosby',
                    style={'width': '50%', 'height': '50px', 'resize': 'none'},
                    draggable='false'
                ),
                html.H3('Allow Multiple Players'),
                dcc.RadioItems(
                    id='select-multiple',
                    options=[
                        {'label': 'Yes', 'value': True, 'disabled': True},
                        {'label': 'No', 'value': False, 'disabled': True}],
                    inline=True,
                    value=False
                ),
                html.Div(id='player-names-wrapper'),
                html.Div(id='player-info-output-wrapper'),
                html.Div(id='stats-output-wrapper'),
            ]),
            dcc.Tab(label='League Stats Browser', value='League Stats Browser', children=[
                html.H3('Select A Season'),
                dcc.Dropdown(
                    id='season-select',
                    options=data['season'].unique(),
                    value=data['season'].unique()[0]
                ),
                html.Div(id='league-output-wrapper'),
            ]),
            dcc.Tab(label='Graph View', value='Graph View', children=[
                html.H3('Select x axis'),
                dcc.RadioItems(
                        id='select-x', 
                        options= list(data.columns),
                        value=list(data.columns)[0],
                        inline=True
                ),
                html.H3('Select y axis'),
                dcc.RadioItems(
                        id='select-y',
                        options= list(data.columns),
                        value=list(data.columns)[1],
                        inline=True
                ),
                html.Div(id='graph-output-wrapper'),
            ]),
        ]),
        html.Div(id='tabs-content-example-graph')
    ], style={'display':'block'})
])

@app.callback(
    Output('league-output-wrapper', 'children'),
    Input('season-select', 'value'))
def render_radio(name2):
    return html.Div([
            html.H5()
        ])

@app.callback(
    Output('player-names-wrapper', 'children'),
    Input('search', 'value'))
def render_stats(name):
    name = name.lower()
    fname = name.split()[0]
    lname = name.split()[1]
    fnames_df = data[data['firstName'].str.lower() == fname]
    lnames_df = data[data['lastName'].str.lower() == lname]
    names_df = pd.concat([fnames_df, lnames_df])
    return html.Div([
            html.H5()
        ])

@app.callback(
    Output('player-info-output-wrapper', 'children'),
    Input('search', 'value'))
def render_stats(name):
    name = name.lower()
    fname = name.split()[0]
    lname = name.split()[1]
    info_df = data.filter(['firstName', 'lastName', 'primaryPosition', 'shootsCatches', 'birthDate'])
    info_df = info_df[info_df['firstName'].str.lower() == fname]
    info_df = info_df[info_df['lastName'].str.lower() == lname]
    return html.Div([
            html.H5([
            'Position: ' + info_df['primaryPosition'].iloc[0], html.Hr(),
            'Shoots: ' + info_df['shootsCatches'].iloc[0], html.Hr(),
            'Date of Birth: ' + info_df['birthDate'].iloc[0], html.Hr()])
        ])
    
@app.callback(
    Output('stats-output-wrapper', 'children'),
    Input('search', 'value'),
    Input('select-multiple', 'value'))
def render_stats(inputName, multiple):
    stats_df = data.drop(['player_id', 'birthDate', 'primaryPosition', 'shootsCatches'], axis=1)
    name = inputName.lower()
    fname = name.split()[0]
    lname = name.split()[1]
    stats_df = stats_df[stats_df['firstName'].str.lower() == fname]
    stats_df = stats_df[stats_df['lastName'].str.lower() == lname]
            
    stats_df['plusMinus'] = stats_df['plusMinus'].apply(lambda x: '+' + str(x) if x > 0 else str(x))
    stats_df['turnoverDifferential'] = stats_df['turnoverDifferential'].apply(lambda x: '+' + str(x) if x > 0 else str(x))
    stats_df['capHit'] = stats_df['salary'].apply(lambda x: '$' + str(int(x)))
    stats_df.drop(['timeOnIce', 'powerPlayTimeOnIce', 'shortHandedTimeOnIce'], axis=1, inplace=True)
    stats_df.rename(columns={'season': 'Season',
                             'capHit': 'Cap Hit',
                             'gamesPlayed': 'GP',
                             'goals': 'G',
                             'assists': 'A',
                             'points': 'P',
                             'pointsPerGame': 'PPG',
                             'plusMinus': '+/-',
                             'penaltyMinutes': 'PIM',
                             'shots': 'S',
                             'shootingPercentage': 'S%',
                             'faceOffLosses': 'FOL',
                             'faceOffWins': 'FOW',
                             'faceOffTaken': 'FOT',
                             'faceOffPercentage': 'FO%',
                             'avgTimeOnIce': 'AToI',
                             'avgPowerPlayTimeOnIce': 'AToI PP',
                             'powerPlayGoals': 'PP G',
                             'powerPlayAssists': 'PP A',
                             'powerPlayPoints': 'PP P',
                             'avgShortHandedTimeOnIce': 'AToI SH',
                             'shortHandedGoals': 'SH G',
                             'shortHandedAssists': 'SH A',
                             'shortHandedPoints': 'SH P',
                             'hits': 'HIT',
                             'blocks': 'BLK',
                             'takeaways': 'TK',
                             'giveaways': 'GV',
                             'turnoverDifferential': 'Turnover Diff'}, inplace=True)
    stats_df = stats_df[['Season', 'Cap Hit', 'GP', 'G', 'A', 'P', 'PPG', '+/-', 'PIM', 'S', 'S%', 'AToI',
                         'PP G', 'PP A', 'PP P', 'AToI PP', 'SH G', 'SH A', 'SH P', 'AToI SH',
                         'FOW', 'FOL', 'FOT', 'FO%', 'HIT', 'BLK', 'TK', 'GV', 'Turnover Diff']]
    return dash_table.DataTable(
                            data=stats_df.to_dict('records'),
                            columns=[
                            {'name': i, 'id': i, 'deletable': False} for i in stats_df.columns
                                if i != 'id'
                            ],
                            id='tbl',
                            sort_action='native',
                            sort_mode='multi')

@app.callback(
    Output('graph-output-wrapper', 'children'),
    Input('select-x', 'value'),
    Input('select-y', 'value'))
def render_graph(x, y):
    plot_df = data.copy()
    plot_df = plot_df[plot_df['gamesPlayed'] > 15]
    if x == y:
        return html.Div([
            html.H3('Error: x and y axis must be different values'),
        ])
    return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs-dcc',
                figure=px.bar(plot_df, x=x, y=y,title=x+' vs '+y, orientation='h')
            )
        ])

app.clientside_callback(
    """
    function(tab_value) {
        document.title = tab_value;
        return null;
    }
    """,
    Output('dummy', 'children'),
    Input('tabs-example-graph', 'value')
)

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)