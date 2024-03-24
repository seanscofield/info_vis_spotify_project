import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import random

# This is supposed to show random stats about the states being highlighted

# Sample state data
states_data = [
    {'State': 'New York', 'Lat': 42.6526, 'Lon': -73.7562},
    {'State': 'California', 'Lat': 36.7783, 'Lon': -119.4179},
    {'State': 'Illinois', 'Lat': 40.6331, 'Lon': -89.3985},
    {'State': 'Texas', 'Lat': 31.9686, 'Lon': -99.9018}
]

# Randomly generated statistics for each state
statistics = {
    'New York': {'Population': random.randint(1000000, 20000000), 'GDP': random.randint(1000000, 20000000)},
    'California': {'Population': random.randint(1000000, 20000000), 'GDP': random.randint(1000000, 20000000)},
    'Illinois': {'Population': random.randint(1000000, 20000000), 'GDP': random.randint(1000000, 20000000)},
    'Texas': {'Population': random.randint(1000000, 20000000), 'GDP': random.randint(1000000, 20000000)}
}

# Set up Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    dcc.Graph(id='map'),
    html.Div(id='statistics')
])

# Define callback to update map and statistics
@app.callback(
    [Output('map', 'figure'),
     Output('statistics', 'children')],
    [Input('map', 'hoverData')]
)
def update_map_and_statistics(hover_data):
    if hover_data is None:
        selected_state = 'New York'  # Default state
    else:
        selected_state = hover_data['points'][0]['location']

    filtered_data = [state for state in states_data if state['State'] == selected_state]
    fig = px.choropleth_mapbox(
        states_data,
        geojson='https://raw.githubusercontent.com/python-visualization/folium/master/tests/us-states.json',
        locations='State',
        color='State',
        mapbox_style="carto-positron",
        zoom=3,
        center={'lat': filtered_data[0]['Lat'], 'lon': filtered_data[0]['Lon']},
        opacity=0.5,
        labels={'State': 'State'}
    )

    # Format statistics
    state_statistics = statistics[selected_state]
    stats_html = html.Div([
        html.H3(selected_state),
        html.P(f"Population: {state_statistics['Population']}"),
        html.P(f"GDP: {state_statistics['GDP']}")
    ])

    return fig, stats_html

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)