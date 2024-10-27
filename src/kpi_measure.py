import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from src.conversion_utility import human_format

ZOOM = 4
HEIGHT = 550

colors = {"background": "#eeeeee", "text": "navy"}
token = "pk.eyJ1Ijoia2hhbGlkMDQ5MSIsImEiOiJjbDlxeXB1ZjAwbHJiM25wNTk3eHRuenE1In0.I94Po1JCO4asTECov1PEbw"
px.set_mapbox_access_token(token)


def draw_pie(pie_df, population: int):
    """
    This function will generate a pie to show the percentage of each bank w.r.t. population
    :param pie_df: The ATMs dataframe
    :param population: The number of population
    :return:
    """
    df = pie_df.groupby(['Participant Name'])['Street_ATM_Address'].count().reset_index(name='counts')
    df["counts"] = pd.to_numeric(df["counts"])
    df["counts"] = pd.to_numeric(population / df["counts"], downcast='float')
    banks = df['Participant Name'].unique().tolist()
    val = df['counts'].tolist()
    val_text = 'Total ' + human_format(population)
    data = go.Pie(labels=banks, values=val)
    fig = go.Figure(data=[data])
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20),
                      annotations=[dict(text=val_text, x=0.5, y=0.5, font_size=20, showarrow=False)])
    fig.update_traces(hole=0.4, hoverinfo='value', textinfo='percent', textfont_size=20)
    return fig


def draw_bar(bar_df, provinces: str):
    """
    This function will create bar chart about number of ATMs in individual bank
    :param bar_df: The dataframe that contain the data of Banks and count of ATMs
    :param provinces: To segregate the data with respected to provinces
    :return:
    """
    if provinces == 'All':
        bar_df = bar_df.groupby(['Participant Name'])['Street_ATM_Address'].count().reset_index(name='counts')
    x_label = 'Participant Name'
    bar_df = bar_df.sort_values(by=['counts'], ascending=False)
    fig = px.bar(bar_df, x=x_label, y='counts', color=x_label, text_auto=".2s",
                 title="Number of ATMs in Pakistan")
    fig.update_layout(plot_bgcolor=colors["background"],
                      paper_bgcolor=colors["background"],
                      font_color=colors["text"],
                      height=HEIGHT, showlegend=False)
    fig.update_traces(width=0.7, textfont_size=20, textangle=0, textposition="outside", cliponaxis=False)
    return fig


def draw_map(map_df):
    """
    This function will create map and draw points where the ATM is located
    :param map_df: The dataframe that contain the data of locations of ATMs
    :return: Map
    """
    filtered_df_g = map_df[map_df["Valid"]]
    filtered_df_r = map_df[~map_df["Valid"]]

    data = [
        go.Scattermapbox(lat=filtered_df_g['Latitude'],
                         lon=filtered_df_g['Longitude'],
                         hovertext=filtered_df_g['Participant Name'] + filtered_df_g['Street_ATM_Address'],
                         mode='markers',
                         marker=dict(size=5, color='green'),
                         name='Correct'),
        go.Scattermapbox(lat=filtered_df_r['Latitude'],
                         lon=filtered_df_r['Longitude'],
                         hovertext=filtered_df_r['Participant Name'] + filtered_df_r['Street_ATM_Address'],
                         mode='markers',
                         marker=dict(size=5, color='red'),
                         name='Wrong')]
    layout = go.Layout(mapbox=dict(accesstoken=token,
                                   bearing=0,
                                   pitch=0,
                                   zoom=ZOOM,
                                   style="outdoors",
                                   center=go.layout.mapbox.Center(
                                       lat=30.3753,
                                       lon=69.3451,
                                   ),
                                   ),
                       margin={"r": 0, "t": 0, "l": 10, "b": 0})
    fig_map = dict(data=data, layout=layout)
    return fig_map
