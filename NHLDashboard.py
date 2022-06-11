# Import required libraries
from matplotlib.pyplot import plot, scatter
import pandas as pd
import numpy as np
import os
from dash import Dash, dash_table, html, dcc, Input, Output, State, no_update
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
from pathlib import Path

data =  pd.read_csv('processedcsv/combinedstats.csv')

# Create a dash application
app = Dash(__name__)

#Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

stats_columns = ['Cap Hit','GP','G','A','P','PPG','+/-','PIM','S','S%','FOL','FOW','FOT', 'FO%',
            'ToI','ToI PP','PP G','PP A','PP P','ToI SH','SH G','SH A','SH P','HIT','BLK','TK','GV','Turnover Diff']

app.layout = html.Div([
    html.Div([
        html.Div(id='dummy'),
        html.H1('NHL Data Visualization'),
        dcc.Tabs(id='tabs-example-graph', value='Player Stats Browser', children=[
            dcc.Tab(label='Player Stats Browser', value='Player Stats Browser', children=[
                html.H3('Search By Player'),
                dcc.Textarea(
                    id='search',
                    placeholder='Enter Player Name',
                    value='Sidney Crosby',
                    style={'width': '30%', 'height': '20px', 'resize': 'none'},
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
            dcc.Tab(label='Data Summary', value='Data Summary', children=[
                html.H3('Select A Category'),
                dcc.Dropdown(
                    id='stats-select',
                    options=stats_columns,
                    value=stats_columns[0]
                ),
                dcc.Input(
                    id='stat-min',
                    type='number',
                    placeholder='Minimum value (Inclusive)',
                    style={'height': '30px', 'width': '10%'}
                ),
                dcc.Input(
                    id='stat-max',
                    type='number',
                    placeholder='Maximum value (Inclusive)',
                    style={'height': '30px', 'width': '10%'}
                ),
                html.Div(id='league-output-wrapper'),
            ]),
            dcc.Tab(label='Raw Data Viewer', value='Raw Data Viewer', children=[
                html.H3('Select A Season'),
                dcc.Dropdown(
                    id='season-select',
                    options=data['season'].unique(),
                    value=data['season'].unique()[0]
                ),
                html.Div(id='raw-data-output-wrapper'),
            ]),
            dcc.Tab(label='Graph View', value='Graph View', children=[
                html.Div(id='graph-output-wrapper'),
            ]),
        ]),
        html.Div(id='tabs-content-example-graph')
    ], style={'display':'block'})
])

#Callback for player info. Takes player name as input. Outputs text for position, handedness, birth date of player
@app.callback(
    Output('player-info-output-wrapper', 'children'),
    Input('search', 'value'))
def render_stats(name):
    #Split search into first and last name
    name = name.lower()
    fname = name.split()[0]
    lname = name.split()[1]
    #Filter by first and last name to find specific player
    info_df = data.filter(['firstName', 'lastName', 'primaryPosition', 'shootsCatches', 'birthDate'])
    info_df = info_df[info_df['firstName'].str.lower() == fname]
    info_df = info_df[info_df['lastName'].str.lower() == lname]
    return html.Div([
        html.H5([
            'Position: ' + info_df['primaryPosition'].iloc[0], html.Hr(),
            'Shoots: ' + info_df['shootsCatches'].iloc[0], html.Hr(),
            'Date of Birth: ' + info_df['birthDate'].iloc[0], html.Hr()
        ])
    ])

#Callback for individual player stat viewer. Takes player name as input. Outputs text with datatable
@app.callback(
    Output('stats-output-wrapper', 'children'),
    Input('search', 'value'),
    Input('select-multiple', 'value'))
def render_stats(inputName, multiple):
    #Find player by first/last name
    stats_df = data.drop(['player_id', 'birthDate', 'primaryPosition', 'shootsCatches'], axis=1)
    name = inputName.lower()
    fname = name.split()[0]
    lname = name.split()[1]
    stats_df = stats_df[stats_df['firstName'].str.lower() == fname]
    stats_df = stats_df[stats_df['lastName'].str.lower() == lname]
    #Format columns to be displayed
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
    return html.Div([
        dash_table.DataTable(
            data=stats_df.to_dict('records'),
            columns=[{'name': i, 'id': i, 'deletable': False} for i in stats_df.columns
                if i != 'id'],
            id='player-tbl',
            sort_action='native',
            sort_mode='single'
        )
    ])

#Callback for raw data viewer. Takes season as input. Outputs datatable
@app.callback(
    Output('raw-data-output-wrapper', 'children'),
    Input('season-select', 'value'))
def render_radio(season): 
    stats_df = data[data['season'] == season]
    #Minimum games played
    stats_df = stats_df[stats_df['gamesPlayed'] > 10]
    #Format +/-, turnover differential, cap hit
    stats_df['plusMinus'] = stats_df['plusMinus'].apply(lambda x: '+' + str(x) if x > 0 else str(x))
    stats_df['turnoverDifferential'] = stats_df['turnoverDifferential'].apply(lambda x: '+' + str(x) if x > 0 else str(x))
    stats_df['capHit'] = stats_df['salary'].apply(lambda x: '$' + str(int(x)))
    stats_df['Name'] = stats_df['firstName'].str.cat(stats_df['lastName'], sep=' ')
    stats_df.drop(['player_id', 'timeOnIce', 'powerPlayTimeOnIce', 'shortHandedTimeOnIce', 'firstName', 'lastName', 'season'], axis=1, inplace=True)
    #Rename, reorder columns
    stats_df.rename(columns={'Name': 'Name',
                             'birthDate': 'DoB',
                             'primaryPosition': 'Position',
                             'shootsCatches': 'Shoots',
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
    stats_df = stats_df[['Name', 'Position', 'Shoots', 'DoB', 'Cap Hit', 'GP', 'G', 'A', 'P', 'PPG', '+/-', 'PIM', 'S', 'S%', 'AToI',
                         'PP G', 'PP A', 'PP P', 'AToI PP', 'SH G', 'SH A', 'SH P', 'AToI SH',
                         'FOW', 'FOL', 'FOT', 'FO%', 'HIT', 'BLK', 'TK', 'GV', 'Turnover Diff']]
    return html.Div([
        dash_table.DataTable(
            data=stats_df.to_dict('records'),
            columns=[{'name': i, 'id': i, 'deletable': False} for i in stats_df.columns
                if i != 'id'],
            id='league-tbl',
            sort_action='native',
            sort_mode='single'
        )
    ])

#Callback for data summary. Takes stat category as input. Takes minimum and maximum values as input.
#Output descriptive statistics. Output histogram. Output box & whisker plot.
@app.callback(
    Output('league-output-wrapper', 'children'),
    Input('stats-select', 'value'),
    Input('stat-min', 'value'),
    Input('stat-max', 'value'))
def render_overview(stat, min_val, max_val):
    stats_df = data.copy()
    #Filter, rename and reorder columns
    stats_df.drop(['player_id', 'firstName', 'lastName', 'season', 'shootsCatches', 'primaryPosition'], axis=1, inplace=True)
    stats_df.rename(columns={'salary': 'Cap Hit',
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
                             'timeOnIce': 'ToI',
                             'avgPowerPlayTimeOnIce': 'AToI PP',
                             'powerPlayTimeOnIce': 'ToI PP',
                             'powerPlayGoals': 'PP G',
                             'powerPlayAssists': 'PP A',
                             'powerPlayPoints': 'PP P',
                             'avgShortHandedTimeOnIce': 'AToI SH',
                             'shortHandedTimeOnIce': 'ToI SH',
                             'shortHandedGoals': 'SH G',
                             'shortHandedAssists': 'SH A',
                             'shortHandedPoints': 'SH P',
                             'hits': 'HIT',
                             'blocks': 'BLK',
                             'takeaways': 'TK',
                             'giveaways': 'GV',
                             'turnoverDifferential': 'Turnover Diff'}, inplace=True)
    stats_df = stats_df[['Cap Hit', 'GP', 'G', 'A', 'P', 'PPG', '+/-', 'PIM', 'S', 'S%', 'AToI', 'ToI',
                         'PP G', 'PP A', 'PP P', 'AToI PP', 'ToI PP', 'SH G', 'SH A', 'SH P', 'AToI SH', 'ToI SH',
                         'FOW', 'FOL', 'FOT', 'FO%', 'HIT', 'BLK', 'TK', 'GV', 'Turnover Diff']]
    
    #Get descriptive statistics
    stats = stats_df[stat].describe()
    #Set default values for min and max values
    if (min_val == None):
         min_val = -100
    if (max_val == None):
        max_val = stats['max']
    #Apply min and max mask to dataframe
    mask = (stats_df[stat] >= min_val) & (stats_df[stat] <= max_val)
    stats_df = stats_df[mask]
    return html.Div([
        html.H4('Count: ' + str(stats['count'].round(0))),
        html.H4('Mean: ' + str(stats['mean'].round(0))),
        html.H4('Std Dev: ' + str(stats['std'].round(2))),
        html.H4('Min: ' + str(stats['min'])),
        html.H4('Max: ' + str(stats['max'])),
        html.H4('25% IQR: ' + str(stats['25%'])),
        html.H4('50% IQR: ' + str(stats['50%'])),
        html.H4('75% IQR: ' + str(stats['75%'])),
        dcc.Graph(figure=px.histogram(stats_df, x=stat)),
        dcc.Graph(figure=px.box(stats_df, x=stat, points='all'))
    ])

#Callback for raw data viewer. Takes nothing as input. Outputs multiple graph objects
@app.callback(
    Output('graph-output-wrapper', 'children'),
    Input('dummy', 'children'))
def render_graph(x):
    #Filter columns to be used, rename columns
    plot_df = data.filter(['gamesPlayed', 'salary', 'goals', 'assists', 'points', 'primaryPosition'])
    plot_df = plot_df[plot_df['gamesPlayed'] > 15]
    plot_df = plot_df.rename(columns={'primaryPosition': 'Position',
                            'gamesPlayed': 'GP',
                            'goals': 'G',
                            'assists': 'A',
                            'points': 'P',
                            'salary': 'Cap Hit'})
    #Aggregate columns
    goals_df = plot_df.groupby('G')['Cap Hit'].mean().reset_index()
    assists_df = plot_df.groupby('A')['Cap Hit'].mean().reset_index()
    points_df = plot_df.groupby('P')['Cap Hit'].mean().reset_index()
    
    #Create plots to be placed in subplot
    goals_pie = px.pie(plot_df, values='G', names='Position', hole=0.25)
    assists_pie = px.pie(plot_df, values='A', names='Position', hole=0.25)
    points_pie = px.pie(plot_df, values='P', names='Position', hole=0.25)
    salary_pie = px.pie(plot_df, values='Cap Hit', names='Position', hole=0.25)
    position_pie = px.histogram(plot_df, x='Position')
    #Create subplots
    pie_fig = sp.make_subplots(rows=1, cols=5,
                               subplot_titles=('Goals', 'Assists', 'Points', 'Cap Hit', 'Position'),
                               specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'domain'}, {'type':'xy'}]])
    #Add traces to subplot
    for trace in range(len(goals_pie['data'])):
        pie_fig.append_trace(goals_pie['data'][trace], row=1,col=1)
    for trace in range(len(assists_pie['data'])):
        pie_fig.append_trace(assists_pie['data'][trace], row=1,col=2)
    for trace in range(len(points_pie['data'])):
        pie_fig.append_trace(points_pie['data'][trace], row=1,col=3)
    for trace in range(len(salary_pie['data'])):
        pie_fig.append_trace(salary_pie['data'][trace], row=1,col=4)
    for trace in range(len(position_pie['data'])):
        pie_fig.append_trace(position_pie['data'][trace], row=1,col=5)
    
    #Create plots to be placed in subplot
    goals_scatter = px.scatter(goals_df, x='G', y='Cap Hit')
    assists_scatter = px.scatter(assists_df, x='A', y='Cap Hit')
    points_scatter = px.scatter(points_df, x='P', y='Cap Hit')
    #Create subplots
    scatter_fig = sp.make_subplots(rows=1, cols=3, subplot_titles=('Goals', 'Assists', 'Points'))
    #Add traces to subplot
    for trace in range(len(goals_scatter['data'])):
        scatter_fig.append_trace(goals_scatter['data'][trace], row=1, col=1)
    for trace in range(len(assists_scatter['data'])):
        scatter_fig.append_trace(assists_scatter['data'][trace], row=1, col=2)
    for trace in range(len(points_scatter['data'])):
        scatter_fig.append_trace(points_scatter['data'][trace], row=1, col=3)
    
    return html.Div([
        html.H3('Positional Breakdown'),
        dcc.Graph(
            id='plot-1',
            figure=pie_fig
        ),
        html.Br(),
        html.H3('Goals vs Cap Hit'),
        dcc.Graph(
            id='plot-2',
            figure=scatter_fig
         ),
    ])

#Clientside callback for changing document title based on tab selected. Takes active tab value as input. Outputs document title
app.clientside_callback(
    '''
    function(tab_value) {
        document.title = tab_value;
        return null;
    }
    ''',
    Output('dummy', 'children'),
    Input('tabs-example-graph', 'value')
)

#Run with debug mode active on port 3000
if __name__ == '__main__':
    app.run_server(debug=True, port=3000)
    #app.run_server(debug=False, port=3000)