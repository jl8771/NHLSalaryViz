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
        dcc.Tabs(id="tabs-example-graph", value='tab-1', children=[
            dcc.Tab(label='Player Stats Browser', value='tab-1', children=[
                html.H3('Search By Player'),
                dcc.Input(
                    id='search',
                    placeholder='Enter Player Name',
                    type='text',
                    value='Sidney Crosby'
                ),
                html.Div(id='player-names-wrapper'),
                html.Div(id='player-info-output-wrapper'),
                html.Div(id='stats-output-wrapper'),
            ]),
            dcc.Tab(label='League Stats Browser', value='tab-2', children=[
                html.H3('Select A Season'),
                dcc.Dropdown(
                    id='season-select',
                    options=data['season'].unique(),
                    value=data['season'].unique()[0]
                ),
            ]),
            dcc.Tab(label='Graph', value='tab-3', children=[
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

#@app.callback(
    #Output('select-y', 'options'),
    #Input('select-x', 'value'))
#def render_radio(x):
    #return list(dfs[0].columns).remove(x)

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
    Input('search', 'value'))
def render_stats(name):
    name = name.lower()
    fname = name.split()[0]
    lname = name.split()[1]
    stats_df = data.filter(['season', 'gamesPlayed',
                            'goals', 'assists', 'points', 'salary',
                            'plusMinus', 'shots', 'shootingPercentage', 'timeOnIce', 'hits', 'blocks',
                            'powerPlayTimeOnIce', 'powerPlayGoals', 'powerPlayAssists', 'powerPlayPoints',
                            'shortHandedTimeOnIce', 'shortHandedGoals', 'shortHandedAssists', 'shortHandedPoints',
                            'faceOffWins', 'faceOffTaken', 'faceOffPercentage', 'hits', 'blocks', 'giveaways', 'takeaways', 'turnoverDifferential'])
    stats_df = stats_df[stats_df['firstName'].str.lower() == fname]
    stats_df = stats_df[stats_df['lastName'].str.lower() == lname]
    stats_df['plusMinus'] = stats_df['plusMinus'].apply(lambda x: '+' + str(x) if x > 0 else str(x))
    stats_df['turnoverDifferential'] = stats_df['turnoverDifferential'].apply(lambda x: '+' + str(x) if x > 0 else str(x))
    stats_df['capHit'] = stats_df['salary'].apply(lambda x: '$' + str(int(x)))
    #stats_df.drop(['timeOnIce', 'powerPlayTimeOnIce', 'shortHandedTimeOnIce'], axis=1, inplace=True)
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
                             'AvgTimeOnIce': 'Avg ToI',
                             'AvgPowerPlayTimeOnIce': 'Avg PP ToI',
                             'powerPlayGoals': 'PP G',
                             'powerPlayAssists': 'PP A',
                             'powerPlayPoints': 'PP P',
                             'AvgShortHandedTimeOnIce': 'Avg SH ToI',
                             'shortHandedGoals': 'SH G',
                             'shortHandedAssists': 'SH A',
                             'shortHandedPoints': 'SH P',
                             'hits': 'HIT',
                             'blocks': 'BLK',
                             'takeaways': 'TK',
                             'giveaways': 'GV',
                             'turnoverDifferential': 'TRNOVR'}, inplace=True)
    stats_df = stats_df[['Season', 'Cap Hit', 'GP', 'G', 'A', 'P', 'PPG', '+/-', 'PIM', 'S', 'S%', 'Avg ToI',
                         'PP G', 'PP A', 'PP P', 'Avg PP ToI', 'SH G', 'SH A', 'SH P', 'Avg SH ToI',
                         'FOW', 'FOL', 'FOT', 'FO%', 'HIT', 'BLK', 'TK', 'GV']]
    return dash_table.DataTable(stats_df.to_dict('records'), id='tbl')

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
        switch() {
            case tab-1:
                document.title = 'Player Stats Browser';
                break;
            case tab-2:
                document.title = 'League Stats Browser';
                break;
            case tab-3:
                document.title = 'Graph';
                break;
        }
        return null;
    }
    """,
    Output('dummy', 'children'),
    Input('tabs-example-graph', 'value')
)

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)