# dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup ------------------

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect existing database
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

# start session
session = Session(engine)

# Flask Setup ------------------ 

# create an app with Flask
app = Flask(__name__)

# index route, list all routes that are availible
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaiii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value
# Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():

    # query
    results = session.query(Measurement.date, Measurement.prcp).all()

    # create list of dictionaries
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    # query
    results = session.query(Station.station).all()

    # convert to list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")

def tobs():
    sel_measure = [
       Measurement.station,
       Measurement.date,
       Measurement.tobs]
    
    # one year fromo current date
    prev_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    # query
    results = session.query(*sel_measure).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_date).all()
    
    # convert to list
    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

# Return a JSON list of the min, average and max temp for given start or start-end range
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
# When given the start and  end date, calculate  TMIN, TAVG, and TMAX for dates between the start and end date inclusive
 
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):

    # we will be calculating min, avg, and max temps
    temp_stats = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # if no end date is given, calculate min/max/avg for all dates greater than or equal to start
    if not end:
        temp_results = session.query(*temp_stats).filter(Measurement.date >= start).all()
        temp_result = list(np.ravel(temp_results))
        return jsonify(temp_result)
    
    # calculate min/max/avg for dates between the start and end date, inclusive
    temp_results = session.query(*temp_stats).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_result = list(np.ravel(temp_results))
    
    return jsonify(temp_result)

# end session
session.close()

if __name__ == "__main__":
    app.run(debug=True)
