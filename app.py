import pandas as pd
from os import listdir
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import math
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def cartesian_from_lat_long(long, lat):
    lat, long = np.deg2rad(lat), np.deg2rad(long)
    x = np.cos(lat) * np.cos(long)
    y = np.sin(lat)
    z = -np.cos(lat) * np.sin(long)

    return [x, y, z]


def data_for_day(day):

    # Loading the US data
    df_us = pd.read_csv(f'data_us/{day}.csv')
    data_us = pd.DataFrame(df_us)
    result = {"data": []}
    for index, row in data_us.iterrows():
        if math.isnan(row['Long_']) or math.isnan(row['Lat']):
            next
        else:
            result['data'].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['Long_'], row['Lat']]
                },
                "properties": {
                    "country": row['Province_State'].replace("'", "\'") + ', ' + row['Country_Region'].replace("'", "\'"),
                    "confirmed": row['Confirmed'],
                    "deaths": row['Deaths'],
                }
            })

    # Loading data for rest of the world
    df = pd.read_csv(f'data/{day}.csv')
    data = pd.DataFrame(df)
    for index, row in data.iterrows():
        if math.isnan(row['Long_']) or math.isnan(row['Lat']) or row['Country_Region'] == 'US':
            next
        else:
            result['data'].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['Long_'], row['Lat']]
                },
                "properties": {
                    "country": row['Combined_Key'].replace("'", "\'"),
                    "confirmed": row['Confirmed'],
                    "deaths": row['Deaths'],
                }
            })
    return(result['data'])


def data_for_dayVR(day):

    # Loading the US data
    df_us = pd.read_csv(f'data_us/{day}.csv')
    data_us = pd.DataFrame(df_us)
    result = {"data": []}
    for index, row in data_us.iterrows():
        if math.isnan(row['Long_']) or math.isnan(row['Lat']):
            next
        else:
            result['data'].append({
                "coordinates": cartesian_from_lat_long(row['Long_'], row['Lat']),
                "country": row['Province_State'].replace("'", "\'") + ', ' + row['Country_Region'].replace("'", "\'"),
                "confirmed": row['Confirmed'],
                "deaths": row['Deaths'],
            })

    # Loading data for rest of the world
    df = pd.read_csv(f'data/{day}.csv')
    data = pd.DataFrame(df)
    for index, row in data.iterrows():
        if math.isnan(row['Long_']) or math.isnan(row['Lat']) or row['Country_Region'] == 'US':
            next
        else:
            result['data'].append({
                "coordinates": cartesian_from_lat_long(row['Long_'], row['Lat']),
                "country": row['Combined_Key'].replace("'", "\'"),
                "confirmed": row['Confirmed'],
                "deaths": row['Deaths'],
            })
    return(result['data'])


def numbers_for_day(day):
    result = [0, 0]
    # getting the min and max values for the US data

    df_us = pd.read_csv(f'data_us/{day}.csv')
    data_us = pd.DataFrame(df_us)
    result[0] = int(data_us.min(axis=0)['Confirmed'])
    result[1] = int(data_us.max(axis=0)['Confirmed'])

    # getting the min and max values for the rest of the world
    df = pd.read_csv(f'data/{day}.csv')
    data = pd.DataFrame(df)
    if data.min(axis=0)['Confirmed'] < result[0]:
        result[0] = int(data.min(axis=0)['Confirmed'])
    if data.max(axis=0)['Confirmed'] > result[1]:
        result[1] = int(data.max(axis=0)['Confirmed'])

    return result


def dates():
    timestamps = [ts.replace('.csv', '') for ts in listdir('data_us')]
    dates = [datetime.strptime(ts, "%m-%d-%Y") for ts in timestamps]
    dates.sort()
    sorteddates = [datetime.strftime(ts, "%m-%d-%Y") for ts in dates]
    return(sorteddates)


@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    return render_template('index.html')


@app.route('/2D', methods=['GET'])
def flat():
    print('Request for 2D page received')
    return render_template('2D.html')


@app.route('/VR', methods=['GET'])
def VR():
    print('Request for VR page received')
    return render_template('VR.html')


@app.route('/data', methods=['GET'])
def get_data():
    if 'date' in request.args:
        date = request.args['date']
    else:
        return "Error: No id field provided. Please specify an id."
    response = jsonify({"type": "FeatureCollection",
                        "features": data_for_day(date)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/dataVR', methods=['GET'])
def get_dataVR():
    if 'date' in request.args:
        date = request.args['date']
    else:
        return "Error: No id field provided. Please specify an id."
    response = jsonify({"data": data_for_dayVR(date)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/numbers', methods=['GET'])
def get_numbers():
    if 'date' in request.args:
        date = request.args['date']
    else:
        return "Error: No id field provided. Please specify an id."
    response = jsonify({"numbers": numbers_for_day(date)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/dates', methods=['GET'])
def get_dates():
    response = jsonify({"dates": dates()})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run()
