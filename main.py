import os
import json
import glob
import pandas as pd
from typing import List, Dict
from src.Visualizer import Visualizer
from shapely.geometry import Point, shape
from shapely.geometry.polygon import Polygon


def check_file_exists(path: str, name: str):
    """
    This function will check the path of csv, if it does not exist then raise an error
    :param path: path of file contains cnic
    :param name: name of file contains cnic
    :return:
    """
    if not os.path.exists(path):
        raise FileNotFoundError("{name} do not exist!".format(name=name))


def load_json(path: str) -> Dict:
    """
    This function will read data from json geometry data and load the data into python
    :param path: The geometry of Pakistan
    :return: Return the dictionary that contain the geometry of Pakistan
    """
    check_file_exists(path, "GeoJSON File")
    f = open(path)
    data = json.load(f)
    return data["features"][174]


def load_atm_data(path: str) -> pd.DataFrame:
    """
    This function will load data from excel files and merge them
    :param path: The path of folder that contains the ATM data of all banks
    :return: Return the dataframe that contain the data of all banks
    """
    data = pd.DataFrame()
    all_files = glob.glob(os.path.join(path, "*.xlsx"))
    for file_path in all_files:
        check_file_exists(file_path, "ATM File")
        print(file_path)
        temp_data = pd.read_excel(file_path)
        temp_data = temp_data.loc[:, ['Bank_Code', 'ATM_ID', 'Street_ATM_Address', 'Longitude', 'Latitude', 'Tehsil',
                                      'City', 'District', 'Province', 'ATM_Status']]
        data = pd.concat([data, temp_data], ignore_index=True)
    data = data.fillna("")
    return data
    # data = data.loc[:, ['Bank Code', 'ATM_ID', 'Street ATM Address', 'Longitude', 'Latitude', 'Tehsil', 'City',
    #                    'District', 'Province', 'ATM Status']]


if __name__ == '__main__':

    df = load_atm_data(path='res/banks/')
    bank_file_path = 'res/Banks.xlsx'
    check_file_exists(bank_file_path, "Bank's name File")
    geojson_file_path = 'res/Countries.geojson'
    pak_geometry = load_json(geojson_file_path)
    population_file_path = 'res/Population2017.xlsx'

    # Design dashboard
    dash_obj = Visualizer(df_atm=df, bank_file_path=bank_file_path, pak_geometry=pak_geometry,
                          population_file_path=population_file_path)
    dash_obj.run_dashboard()
