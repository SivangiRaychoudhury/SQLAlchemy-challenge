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
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
recent_date

# Calculate the date one year from the last date in data set. 
one_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

# Close the session
session.close()

#################################################
# Flask Setup
#################################################
# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define what to do when a user hits the index route
@app.route("/")
def home():
    """List all available routes."""
    return(
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Enter the dates between 2010-01-01 to 2017-08-23<br/>"
    )


# Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session link
    session = Session(engine)

    """Return the dictionary for date and precipitation info"""
    # Query precipitation and date values 
    outputs = session.query(Measurement.date, Measurement.prcp).all()

    # Close the Session   
    session.close()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_dict = {}
    for output in outputs:
        prcp_dict[output[0]] = output[1]
     
    # Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)

# Create stations route 
@app.route("/api/v1.0/stations")
def stations():
    # Create the session link
    session = Session(engine)
    
    """Return a JSON list of stations from the dataset."""
    # Query data to get stations list
    results = session.query(Station.station, Station.name).all()
    
    # Close the Session
    session.close()

    # Create list and dict to hold results
    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict["Station"]= station
        station_dict["Name"] = name
        station_list.append(station_dict)
    
     # Return the JSON representation of your dictionary.
    return jsonify(station_list)

# Create temperatures route (TOBS)
@app.route("/api/v1.0/tobs")
def tobs():
    # Create the session link
    session = Session(engine)
    
    """Query the dates and temperature observations of the most active station for the previous year of data."""

    # Calculate the date one year from the last date in data set. 
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)


    active_stations = session.query(Measurement.station, func.count(Measurement.date)).\
                      group_by(Measurement.station).order_by(func.\
                      count(Measurement.date).desc()).all()
    most_active_station_id = active_stations[0][0]
    
    sel=[Measurement.station, Measurement.date, Measurement.tobs]
    results=session.query(*sel).filter(Measurement.date >= one_year).\
            filter(Measurement.station == most_active_station_id).all()

    # Close the Session
    session.close()

    # Create list and dict to hold results
    temp_list = []
    for station, date, tobs in results:
        temp_dict = {}
        temp_dict["Station_ID"] = station
        temp_dict["Temperature"] = tobs
        temp_dict["Date"] = date
        
        temp_list.append(temp_dict)
     # Return the JSON representation of your dictionary.
    return jsonify(temp_list)


# Create start-date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create the session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start-date range."""
    
    # calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
              func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
   
    
    # Close the Session
    session.close()
 # Create list and dict to hold results
    start_list = []
    for result in results:
        start_dict = {}
        start_dict["StartDate"] = start
        start_dict["Temp_Min"] = result[0]
        start_dict["Temp_Avg"] = result[1]
        start_dict["Temp_Max"] = result[2]
        start_list.append(start_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(start_list)

# Create start-date/end-date route
@app.route("/api/v1.0/<start>/<end>")
def startdate_enddate(start,end):
    
    # Create the Session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end dates."""
    

    #calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
              func.max(Measurement.tobs)).\
    filter(Measurement.date >= start, Measurement.date <= end).all()

    # Close the Session
    session.close()
# Create list and dict to hold results
    start_end_list = []
    for result in results:
        start_end = {}
        start_end["Start_Date"] = start
        start_end["End_Date"] = end
        start_end["Temp_Min"] = result[0]
        start_end["Temp_Avg"] = result[1]
        start_end["Temp_Max"] = result[2]
        start_end_list.append(start_end)

    # Return the JSON representation of your dictionary.
    return jsonify(start_end_list)

# Define the main behaviour
if __name__ == "__main__":
    app.run(debug=True)




