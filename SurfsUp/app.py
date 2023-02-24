# Dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app
app = Flask(__name__)

# Define a function which calculates and returns the the date one year from the most recent date
def date_prev_year():
    # Create the session
    session = Session(engine)

    # Define the most recent date in the Measurement dataset
    # Then use the most recent date to calculate the date one year from the last date
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Close the session                   
    session.close()

    # Return the date
    return(first_date)

# Define what to do when the user hits the homepage
@app.route("/")
def homepage():
    return """ <h1> Welcome to Honolulu, Hawaii Climate API! </h1>
    <h3> The available routes are: </h3>
    <ul>
    <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: /api/v1.0/precipitation </li>
    <li><a href = "/api/v1.0/stations"> Stations </a>: /api/v1.0/stations</li>
    <li><a href = "/api/v1.0/tobs"> TOBS </a>: /api/v1.0/tobs</li>
    <li>Minimum, average, and maximum temperatures for a specific start date (the start date should be in the yyyy-mm-dd format): /api/v1.0/&ltstart&gt</li>
    <li>Minimum, average, and maximum temperatures for a specific start-end range(the start and end dates should be in the yyyy-mm-dd format): /api/v1.0/&ltstart&gt/&ltend&gt</li>
    </ul>
    """

# Define what to do when the user hits the precipitation URL
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session
    session = Session(engine)

    # Call the prev_year function
    date_prev_year()

    # Query precipitation data from last 12 months from the most recent date from Measurement table
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prev_year()).all()
    
    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of prcp_list
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    # Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(prcp_list)

# Define what to do when the user hits the station URL
@app.route("/api/v1.0/stations")
def stations():
    # Create the session
    session = Session(engine)

    # Query station data from the Station dataset
    station_data = session.query(Station.station).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_data))

    # Return a list of jsonified station data
    return jsonify(station_list)

# Define what to do when the user hits the URL
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)

    # Call the prev_year function
    date_prev_year()

    # Query tobs data from last 12 months from the most recent date from Measurement table
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= date_prev_year()).all()

    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)

# Define what to do when the user hits the URL with a specific start date
@app.route("/api/v1.0/<start>")
def cal_temp(start):
    # Create the session
    session = Session(engine)

    # Query the minimum, average and maximum temperature from start date to the most recent date
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    start_list = list(np.ravel(start_data))

    # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
    return jsonify(start_list)

# Define what to do when the user hits the URL with a specific start-end date range 
@app.route("/api/v1.0/<start>/<end>")
def cal_temp_2(start, end):
    # Create the session
    session = Session(engine)

    # Query the minimum, average and maximum temperature from start date to the end date
    start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    start_end_list = list(np.ravel(start_end_data))

    # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
    return jsonify(start_end_list)

# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)