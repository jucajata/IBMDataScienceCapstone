# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Constructing the list of dict options for dcc.Dropdown
options_list_dict = [{'label': 'All Sites', 'value': 'ALL'}] 
options_list = list(spacex_df['Launch Site'].unique())
for option in options_list:
    dict_option = {'label': option, 'value': option}
    options_list_dict.append(dict_option)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=options_list_dict,
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    marks={
                                        0: '0', 
                                        2500: '2500',
                                        5000: '5000',
                                        7500: '7500',
                                        10000: '10000',
                                    },
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df.copy()
    if entered_site == 'ALL':
        data = filtered_df[filtered_df['class']==1]
        fig = px.pie(data, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        data = filtered_df[filtered_df['Launch Site']==entered_site].groupby(['Launch Site', 'class']).count()
        data = data.reset_index()
        data = data[[data.columns[0],data.columns[1],data.columns[2]]]
        list_columns = ['Launch Site', 'class', 'class count']
        data.columns = list_columns
        fig = px.pie(data, 
            values='class count', 
            names='class', 
            title=f'Total Success Launches for site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, slider_range):
    filtered_df = spacex_df.copy()
    if entered_site == 'ALL':
        low, high = slider_range
        mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)
        fig = px.scatter(
            filtered_df[mask], x="Payload Mass (kg)", y="class", 
            color="Booster Version Category")
        return fig
    else:
        data = filtered_df[filtered_df['Launch Site']==entered_site]
        low, high = slider_range
        mask = (data['Payload Mass (kg)'] > low) & (data['Payload Mass (kg)'] < high)
        fig = px.scatter(
            data[mask], x="Payload Mass (kg)", y="class", 
            color="Booster Version Category")
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
