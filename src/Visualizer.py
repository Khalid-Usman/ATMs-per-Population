import dash
import pandas as pd
from dash import dcc
from dash import html
from typing import Dict
import dash_bootstrap_components as dbc
from shapely.geometry import Point, shape
from dash.dependencies import Input, Output
from src.kpi_measure import draw_pie, draw_bar, draw_map

PROVINCES = {
    'FATA': 'FATA',
    'Sindh': 'Sindh',
    'SINDH': 'Sindh',
    'Punjab': 'Punjab',
    'PUNJAB': 'Punjab',
    'punjab': 'Punjab',
    'AJK': 'Azad Kashmir',
    'Ajk': 'Azad Kashmir',
    'Azad Kashmir': 'Azad Kashmir',
    'Azad Kashmir ': 'Azad Kashmir',
    'KPK': 'Khyber Pakhtunkhwa',
    'Kpk': 'Khyber Pakhtunkhwa',
    'Khyber Pakhtunkhwa': 'Khyber Pakhtunkhwa',
    'Balochistan': 'Balochistan',
    'Baluchistan': 'Balochistan',
    'Gilgit Baltistan': 'Gilgit Baltistan',
    'Gilgit-Baltistan': 'Gilgit Baltistan',
    'Gilgit-Bultistan': 'Gilgit Baltistan',
    'Islamabad': 'Federal Capital Territory',
    'Federal Capital Territory': 'Federal Capital Territory',
    'Federal Capital': 'Federal Capital Territory',
    'FEDERAL CAPITAL': 'Federal Capital Territory'
}


class Visualizer:
    """This will read the data from CNIC and show into the dashboard"""

    def __init__(self, df_atm: pd.DataFrame, bank_file_path: str, pak_geometry: Dict, population_file_path: str):
        """
        This will initialize the global variables
        :param df_atm: The path of ATM file
        :param bank_file_path: The path of bank's name file
        :param pak_geometry: The geometry of Pakistan
        :param population_file_path: The path of Population File
        """
        self.df_ATM = df_atm
        df_Bank = pd.read_excel(bank_file_path, sheet_name="Sheet1")
        # self.df_ATM = self.df_ATM.loc[self.df_ATM['Bank_Code'] == 70]
        df_Bank = df_Bank.sort_values(by=['Bank_Name'])
        self.dict_bank = dict(zip(df_Bank['Bank_Code'], df_Bank['Bank_Name']))
        self.banks = sorted(self.dict_bank.values())
        self.bank_code = -1
        self.df_ATM['Province'] = self.df_ATM['Province'].map(PROVINCES).fillna('')
        self.df_ATM[['Longitude', 'Latitude']] = self.df_ATM[['Longitude', 'Latitude']].astype(float)
        self.polygon = shape(pak_geometry["geometry"])
        self.df_ATM['Valid'] = self.df_ATM.apply(lambda x: Point(x['Longitude'], x['Latitude']).within(self.polygon),
                                                 axis=1)
        for code, name in self.dict_bank.items():
            self.df_ATM['Bank_Code'] = self.df_ATM['Bank_Code'].replace(code, name)
        self.df_ATM.rename(columns={'Bank_Code': 'Participant Name'}, inplace=True)
        self.df_ATM = self.df_ATM.applymap(lambda s: s.upper() if type(s) == str else s)
        self.df_Population = pd.read_excel(population_file_path, sheet_name="Admin3")
        self.df_Population["Total_pop"] = pd.to_numeric(self.df_Population["Total_pop"])
        self.overall_population = self.df_Population['Total_pop'].sum()
        BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css"
        self.app = dash.Dash(__name__, external_stylesheets=[BS])
        self.design_dash()

    def design_dash(self):
        """
        In this function we will design the UI of Dashboard
        :return:
        """
        self.app.layout = html.Div(
            [
                dbc.Row([
                    dbc.Col(
                        html.Div(
                            html.H1('ATMs Per Population',
                                    style={
                                        'fontSize': 30,
                                        'textAlign': 'center',
                                        'textDirection': 'vertical',
                                        'dir': 'rtl',
                                        'padding': '0px',
                                        'padding-top': '30px',
                                        'color': '#41444b',
                                        'margin-left': 'auto',
                                        'margin-right': 'auto'
                                    }, className='four columns'),
                        ), width=6),
                ], align="center", justify="center"),

                html.Div(style={'width': '0.1%', 'display': 'inline-block'}),

                html.Div(
                    className="row", children=[
                        html.Div(className='Provinces', children=[
                            html.Label('Select Province'),
                            dcc.Dropdown(
                                id='province_dropdown',
                                options=[{"label": s, "value": s} for s in self.df_ATM['Province'].unique().tolist()],
                                placeholder='All',
                                clearable=True,
                                searchable=False,
                            )], style=dict(width='32%', padding='0px 0px 0px 50px')),

                        html.Div(className='Districts', children=[
                            html.Label('Select District'),
                            dcc.Dropdown(
                                id='district_dropdown',
                                placeholder='All',
                                clearable=True,
                                searchable=False,
                            )], style=dict(width='20%', padding='0px 0px 0px 20px')),

                        html.Div(className='Cities', children=[
                            html.Label('Select City'),
                            dcc.Dropdown(
                                id='city_dropdown',
                                placeholder='All',
                                clearable=True,
                                searchable=False,
                            )], style=dict(width='20%', padding='0px 0px 0px 20px')),

                        html.Div(className='Tehsils', children=[
                            html.Label('Select Tehsil'),
                            dcc.Dropdown(
                                id='tehsil_dropdown',
                                placeholder='All',
                                clearable=True,
                                searchable=False,
                            )], style=dict(width='20%', padding='0px 0px 0px 20px'))
                    ],
                    style=dict(display='flex')
                ),

                html.Div(style={'width': '0.01%', 'display': 'inline-block'}),

                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="four columns",
                            children=[

                                html.Div(
                                    dcc.Graph(id='Bank-vs-ATM-count',
                                              figure=draw_bar(self.df_ATM, 'All'),
                                              className='chart'),
                                    style={'height': '500', 'width': '700px', 'align': 'left'}),
                            ],
                            style={'border-radius': '5px', 'backgroundColor': '#f8f9fa',
                                   'box-shadow': '2px 2px 1.5px #dddddd', 'padding': '2px', 'margin-left': '5px',
                                   'margin-right': '5px', 'margin-top': '5px'}
                        ),
                        html.Div(
                            className="four columns",
                            children=[
                                html.Div(
                                    dcc.Graph(id='ATM-vs-Pop-percentage',
                                              figure=draw_pie(self.df_ATM,
                                                              int(self.overall_population))),
                                    style={'height': '500', 'width': '700px', 'align': 'right'}),
                            ],
                            style={'border-radius': '5px', 'backgroundColor': '#f8f9fa',
                                   'box-shadow': '2px 2px 1.5px #dddddd', 'padding': '2px', 'margin-left': '5px',
                                   'margin-right': '5px', 'margin-top': '5px'}
                        )
                    ]
                ),

                html.Div(style={'width': '0.01%', 'display': 'inline-block'}),

                html.Div(dcc.Graph(id='atm-map',
                                   figure=draw_map(self.df_ATM)),
                         className="map",
                         style={'border-radius': '1px', 'backgroundColor': '#f8f9fa',
                                'box-shadow': '2px 2px 1.5px #dddddd', 'padding': '1px', 'margin-left': 'auto',
                                'margin-right': 'auto', 'margin-top': '1px', 'height': '500'}
                         ),
            ]
        )

        # Callback to update tehsilDropdown
        @self.app.callback(
            [Output(component_id='tehsil_dropdown', component_property='options'),
             Output(component_id='tehsil_dropdown', component_property='placeholder')],
            Input(component_id='city_dropdown', component_property='value')
        )
        def update_tehsil_dropdown(city: str):
            if city is None or city == "All":
                return [{'label': 'All', 'value': 'All'}], 'All'
            filtered_df = self.df_ATM[self.df_ATM['City'] == city]
            cities = list(set(filtered_df[filtered_df['City'] == city]['Tehsil']))
            return [{'label': i, 'value': i} for i in cities], 'All'

        # Callback to update cityDropdown
        @self.app.callback(
            [Output(component_id='city_dropdown', component_property='options'),
             Output(component_id='city_dropdown', component_property='placeholder')],
            Input(component_id='district_dropdown', component_property='value')
        )
        def update_city_dropdown(district: str):
            if district is None or district == "All":
                return [{'label': 'All', 'value': 'All'}], 'All'
            filtered_df = self.df_ATM[self.df_ATM['District'] == district]
            cities = list(set(filtered_df[filtered_df['District'] == district]['City']))
            return [{'label': i, 'value': i} for i in cities], 'All'

        # Callback to update districtDropdown
        @self.app.callback(
            [Output(component_id='district_dropdown', component_property='options'),
             Output(component_id='district_dropdown', component_property='placeholder')],
            Input(component_id='province_dropdown', component_property='value')
        )
        def update_district_dropdown(province: str):
            if province is None or province == "All":
                return [{'label': 'All', 'value': 'All'}], 'All'
            filtered_df = self.df_ATM[self.df_ATM['Province'] == province]
            districts = list(set(filtered_df['District']))
            return [{'label': i, 'value': i} for i in districts], 'All'

        # Callback to show figure
        @self.app.callback(
            [Output("Bank-vs-ATM-count", "figure"),
             Output("ATM-vs-Pop-percentage", "figure"),
             Output("atm-map", "figure")],
            [Input("province_dropdown", "value"),
             Input("city_dropdown", "value"),
             Input("district_dropdown", "value"),
             Input("tehsil_dropdown", "value")]
        )
        def update_figure(selected_province: str, selected_district: str, selected_city: str, selected_tehsil: str):
            """
            It is callback function to update the dashboard
            :param selected_province: The selected province from dropdown
            :param selected_district: The selected division from dropdown
            :param selected_city: The selected province from dropdown
            :param selected_tehsil: The selected division from dropdown
            :return: It will return a figure to show at dashboard
            """
            if selected_province is None or selected_province == "All":
                filtered_df = self.df_ATM.copy()
                group_df = self.df_ATM.groupby(['Participant Name'])['Street_ATM_Address'].count(). \
                    reset_index(name='counts')
            elif selected_district is None or selected_district == "All":
                filtered_df = self.df_ATM[self.df_ATM['Province'] == selected_province]
                group_df = filtered_df.groupby(['Participant Name', 'District'])['Street_ATM_Address'].count().\
                    reset_index(name='counts')
            elif selected_city is None or selected_city == 'All':
                filtered_df = self.df_ATM[self.df_ATM['Province'] == selected_province]
                filtered_df = filtered_df[filtered_df['District'] == selected_district]
                group_df = filtered_df.groupby(['Participant Name', 'City'])['Street_ATM_Address'].count().\
                    reset_index(name='counts')
            else:
                filtered_df = self.df_ATM[self.df_ATM['Province'] == selected_province]
                filtered_df = filtered_df[filtered_df['District'] == selected_district]
                filtered_df = filtered_df[filtered_df['City'] == selected_city]
                group_df = filtered_df.groupby(['Participant Name', 'Tehsil'])['Street_ATM_Address'].count().\
                    reset_index(name='counts')

            return draw_bar(bar_df=group_df, provinces=''), draw_pie(filtered_df, int(self.overall_population)), \
                   draw_map(filtered_df)

    def run_dashboard(self):
        self.app.run_server(debug=True)
