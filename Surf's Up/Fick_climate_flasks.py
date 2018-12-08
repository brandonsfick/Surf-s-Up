import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
        )


@app.route("/api/v1.0/precipitation")
def precipitation():
#  API Returns the date and precipitation in Json formate
    results = session.query(Measurement.date, Measurement.prcp).all()
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
# API Returns the date and station identifiers in Json formate
    df_stations= session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    return jsonify(df_stations)

@app.route("/api/v1.0/tobs")
def tobs():
# API Returns the date and tobs for the last year per data entered
        #Returns last value of data and cleans it
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date=str(last_date).replace(",", "").replace("'","").replace("(","").replace(")","")
   
    #calculates the date one year before last entry of data
    last_year_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - (dt.timedelta(days=365))
    
    #create a list of all tobs data and dates for the last year 
    results_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > last_year_date).order_by(Measurement.date).all()
    return jsonify( results_year)

@app.route("/api/v1.0/<start>")
def tobs_start(start=None):
#Allows the user to obtain data from a date specified           
        # Another method to strptime
        # current_date = dt.date(int(start[0:4]),int(start[4:6].strip("0")),int(start[6:8].strip("0")))
        current_date = dt.datetime.strptime(start, "%Y%m%d")
        #finding the min, ave, max temps from the data
        mintemp=session.query(func.min(Measurement.tobs)).filter(Measurement.date >= current_date).all()
        avetemp=session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= current_date).all()
        maxtemp= session.query(func.max(Measurement.tobs)).filter(Measurement.date >= current_date).all()
        #creates a dictionary so API users can tell what data belongs to what category.
        temp_start_dict= {"Min temp": mintemp,'Ave Temp':avetemp, 'Max Temp':maxtemp}
        return jsonify(temp_start_dict)
@app.route("/api/v1.0/<start>/<end>")
def tobs_startstop(start=None,end=None):
#Allows the user to put in a start and end date
        current_date = dt.datetime.strptime(start, "%Y%m%d") 
        end_year_date = dt.datetime.strptime(end, "%Y%m%d")
        # Another method to strptime
        # current_date = dt.date(int(start[0:4]),int(start[4:6].strip("0")),int(start[6:8].strip("0"))) 
        # end_year_date = dt.date(int(end[0:4]),int(end[4:6].strip("0")),int(end[6:8].strip("0")))
        #finding the min, ave, max temps from the data

        mintemp=session.query(func.min(Measurement.tobs)).filter(Measurement.date <= end_year_date).filter(Measurement.date >= current_date).all()
        avetemp=session.query(func.avg(Measurement.tobs)).filter(Measurement.date <= end_year_date).filter(Measurement.date >= current_date).all()
        maxtemp= session.query(func.max(Measurement.tobs)).filter(Measurement.date <= end_year_date).filter(Measurement.date >= current_date).all()
        
        #creates a dictionary so API users can tell what data belongs to what category.
        temp_range_dict = {"Min temp": mintemp,'Ave Temp':avetemp, 'Max Temp':maxtemp}
        return jsonify(temp_range_dict)

if __name__ == '__main__':
    app.run(debug=True)
