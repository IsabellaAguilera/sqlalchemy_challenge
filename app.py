import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

################################
# initializes Flask Routes
################################

@app.route("/")
def homepage():
  
    return(
        f"<br><br>"
        f"Available Routes:<br><br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start date format:yyyy-mm-dd]/[end date format:yyyy-mm-dd]<br><br>"
        f"(Note: Dates range from 2010-01-01 to 2017-08-23).</br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
 
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict)  

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
  
    session = Session(engine)

    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude).all()

    session.close()
    
    station_data = []
    for station, name, latitude, longitude in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_data.append(station_dict)
    
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    
    recent_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = datetime.strptime(recent_date_query[0], '%Y-%m-%d').date()

    one_year_ago = recent_date - relativedelta(months= 12)

    # Query temperature last 12 months
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).all()

    session.close()
    
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        tobs_data.append(tobs_dict)  

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start_date>")
def data_start_date(start_date):
    
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()

    session.close()

# Append dict items to list for start dates for temperature min, avg, and max
    start_tobs = []
    for min, avg, max in results:
        start_tobs_dict = {}
        start_tobs_dict["Min Temp"] = min
        start_tobs_dict["Avg Temp"] = avg
        start_tobs_dict["Max Temp"] = max
        start_tobs.append(start_tobs_dict) 
    
    return jsonify(start_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def data_start_end_date(start_date, end_date):
    
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

# Append dict items to list for start and end dates range for temperature min, avg, and max
    start_end_tobs = []
    for min, avg, max in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["Min Temperature"] = min
        start_end_tobs_dict["Avg Temperature"] = avg
        start_end_tobs_dict["Max Temperature"] = max
        start_end_tobs.append(start_end_tobs_dict) 
    

    return jsonify(start_end_tobs)

if __name__ == "__main__":
    app.run(debug=True)