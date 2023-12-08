from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

# Flask Setup
app = Flask(__name__)

# Setup sqlalchemy session
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#################################################

@app.route("/")
def welcome():
    return (
        f"This is an API for Hawaii climate data<br/>"
        f"- Specify desired date in paths marked '/*', in format yyyy-mm-dd<br/>"
        f"- Specify /start_date/end_date in paths marked '/*/*'<br/>"
        f"- Do not include * in url<br/><br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/prcp_by_date/*<query_date><br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs_mostactivestation<br/>"
        f"/api/v1.0/tobs_start_date/*<start_date><br/>"
        f"/api/v1.0/tobs_date_range/*<start_date>/*<end_date>"
    )

#################################################
# (1) Convert the query results to a dictionary by using 
# date as the key and prcp as the value.
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Hawaii precipitation data"""
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date.asc()).all()

    return jsonify(dict(precipitation_data))

@app.route("/api/v1.0/prcp_by_date/<query_date>")
def prcp_by_date(query_date):
    """Hawaii precipitation data for query date (yyyy-mm-dd)"""
    prcp_date_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date == query_date).all()

    # Convert Row objects to dictionaries
    prcp_data_dict = [{"date": row.date, "prcp": row.prcp} for row in prcp_date_data]

    return jsonify({query_date: prcp_data_dict})

#################################################
# (2) Return a JSON list of stations from the dataset.
#################################################

@app.route("/api/v1.0/stations")
def stations():
    """List of Hawaii weather stations"""
    station_data = session.query(Station.station, Station.name).all()

    return jsonify([dict(station) for station in station_data])

#################################################
# (3) Query the dates and temperature observations of 
# the most-active station for the previous year of data.
# Return a JSON list of temperature observations for 
# the previous year.
#################################################

@app.route("/api/v1.0/tobs_mostactivestation")
def tobs():
    """Temperature observation from the most active weather station for the previous year"""

    most_active_station = 'USC00519281'

    temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).all()

    return jsonify([dict(temp) for temp in temps])

#################################################
# (4) Data from start date (inclusive)
# calculate TMIN, TAVG, and TMAX for all the dates 
# greater than or equal to the start date.
#################################################

@app.route("/api/v1.0/tobs_start_date/<start_date>")
def tobs_start_date(start_date):
    """Hawaii temperature data from query start date (yyyy-mm-dd)"""
    tobs_startdate_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= start_date).all()
    
    temperatures = [temp[0] for temp in tobs_startdate_data]
    spread = [min(temperatures), max(temperatures), sum(temperatures) / len(temperatures)]
    sumtobs_startdate_dict = {"TMIN": spread[0], "TMAX": spread[1], "TAVG": spread[2]}

    return jsonify({f"summary_since_{start_date}": sumtobs_startdate_dict})

#################################################
# (4) Data for specified date range
# calculate TMIN, TAVG, and TMAX for all the dates 
# from the start date to the end date, inclusive.
#################################################

@app.route("/api/v1.0/tobs_date_range/<start_date>/<end_date>")
def tobs_date_range(start_date, end_date):
    """Hawaii temperature data for query date range"""
    tobs_range_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= start_date, 
               Measurement.date <= end_date).all()

    range_temps = [temp[0] for temp in tobs_range_data]

    if not range_temps:
        return jsonify({"error": "No data found for the given date range."}), 404

    range_spread = [min(range_temps), max(range_temps), sum(range_temps) / len(range_temps)]
    sumtobs_rangedate_dict = {"TMIN": range_spread[0], "TMAX": range_spread[1], "TAVG": range_spread[2]}

    return jsonify({f"summary_from_{start_date}_to_{end_date}": sumtobs_rangedate_dict})

if __name__ == "__main__":
    app.run(debug=True)
