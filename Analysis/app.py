# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define what to do when the user hits the homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to Honolulu, Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

# Define what to do when the user uses the precipitation link
@app.route("/api/v1.0/precipitation")
def precipitation():
# Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Querying last 12 months precipitation analysis results
    prcp_analysis = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prev_year()).all()
    
     # Close the session                   
    session.close()
    
    # Dictionary list for date and percipitation
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    # Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(prcp_list)

# Define what to do when the user uses the station link
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query station data from the Station dataset
    station_data = session.query(Station.station).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_data))

    # Return a list of jsonified station data
    return jsonify(station_list)

# Define what to do when the user uses the link
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most-active station for the previous year of data
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

# Define what to do when the user usees the link with the provided start date or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query: min, avg, max temps; create list called `sel`
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Using "if" statement to determine start/end date
    if end == None: 
        # Query the data from start date to the most recent date
        start_date_data = session.query(*sel).\
                            filter(Measurement.date >= start).all()
        
        # Convert list of tuples into normal list
        start_list = list(np.ravel(start_date_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
        return jsonify(start_list)
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*sel).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
        # Convert list of tuples into normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)

    # Close the session                   
    session.close()
    
    
if __name__ == "__main__":
    app.run(debug = True)