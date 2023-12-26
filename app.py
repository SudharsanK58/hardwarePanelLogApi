from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os

app = FastAPI()

# Set up CORS middleware settings to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb+srv://ZusanMongo:Sadhana5823@zusandb.17e2qjw.mongodb.net/Hardware?retryWrites=true&w=majority")
db = client.O_BeaconData
collection = db.TicketLog
device_collection = db.DeviceLog  # New collection


@app.get("/device_log_data")
async def get_device_log_data():
    try:
        # Create an empty query to retrieve all documents
        query = {}

        # Retrieve all data from the DeviceLog collection
        device_data = []
        for doc in device_collection.find(query).sort("timestamp", -1):
            device_info = {
                "deviceId": doc.get("deviceId", "N/A"),
                "timestamp": doc.get("timestamp", "N/A"),
                "StartingTime": doc.get("StartingTime", "N/A"),
                "validationTopic": doc.get("validationTopic", "N/A"),
                "bleMacAddress": doc.get("bleMacAddress", "N/A"),
                "networkConnection": doc.get("networkConnection", "N/A"),
                "networkName": doc.get("networkName", "N/A"),
                "bleMinor": doc.get("bleMinor", "N/A"),
                "bleTxpower": doc.get("bleTxpower", "N/A"),
                "bleVersion": doc.get("bleVersion", "N/A"),
                "current temp": doc.get("current temp", "N/A"),
                "firmwareVersion": doc.get("firmwareVersion", "N/A")
            }
            device_data.append(device_info)

        return device_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/today_data")
async def get_today_data():
    try:
        # Calculate today's date in UTC
        today_utc = datetime.utcnow()

        # Calculate the time difference between UTC and IST
        utc_offset = timedelta(hours=5, minutes=30)  # IST is UTC+5:30

        # Convert UTC to IST
        today_ist = today_utc + utc_offset
        today_ist_date = today_ist.date()

        # Create a filter for today's data
        start_of_day = datetime.combine(today_ist_date, datetime.min.time())
        end_of_day = datetime.combine(today_ist_date, datetime.max.time())

        query = {
            "now_time": {"$gte": start_of_day, "$lt": end_of_day},
            "username": {"$ne": "Illegal"}  # Exclude documents with username "Illegal"
        }

        # Retrieve, sort, and limit the data
        today_data = []
        for doc in collection.find(query).sort("now_time", -1).limit(20):
            now_time_ist = doc["now_time"] + utc_offset
            formatted_data = {
                "username": doc["username"],
                "ticket_type": doc["ticket_type"],
                "ticket_id": doc["ticket_id"],
                "now_time": now_time_ist.strftime('%Y-%m-%d %H:%M:%S') + " IST"
            }
            today_data.append(formatted_data)

        return today_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/today_data_device_id/{device_id}")
async def get_today_data_device_id(device_id: str):
    try:
        # Calculate the time range for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        # Calculate the time difference between UTC and IST
        utc_offset = timedelta(hours=5, minutes=30)  # IST is UTC+5:30

        # Convert UTC to IST
        start_time_ist = start_time + utc_offset
        end_time_ist = end_time + utc_offset

        query = {
            "now_time": {"$gte": start_time_ist, "$lt": end_time_ist},
            "device_id": device_id,
            "username": {"$nin": ["Illegal", "N/A"]}, # Exclude documents with username "Illegal"
        }

        # Retrieve, sort, and limit the data
        today_data = []
        for doc in collection.find(query).sort("now_time", -1).limit(20):
            now_time_ist = doc["now_time"] + utc_offset
            formatted_data = {
                "username": doc["username"],
                "count": doc["ticket_count"],
                "ticket_type": doc["ticket_type"],
                "ticket_id": doc["ticket_id"],
                "now_time": now_time_ist.strftime('%Y-%m-%d %H:%M:%S') + " IST"
            }
            today_data.append(formatted_data)

        return today_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/today_data_ticket_id/{ticket_id}")
async def get_today_data_ticket_id(ticket_id: int):
    try:
        # Calculate the time range for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        # Calculate the time difference between UTC and IST
        utc_offset = timedelta(hours=5, minutes=30)  # IST is UTC+5:30

        # Convert UTC to IST
        start_time_ist = start_time + utc_offset
        end_time_ist = end_time + utc_offset

        query = {
            # "now_time": {"$gte": start_time_ist, "$lt": end_time_ist},
            "ticket_id": ticket_id,
            "username": {"$ne": "Illegal"}  # Exclude documents with username "Illegal"
        }

        # Retrieve, sort, and limit the data
        today_data = []
        for doc in collection.find(query).sort("now_time", -1).limit(20):
            now_time_ist = doc["now_time"] + utc_offset
            formatted_data = {
                "username": doc["username"],
                "ticket_type": doc["ticket_type"],
                "ticket_id": doc["ticket_id"],
                "device_id": doc["device_id"],
                "now_time": now_time_ist.strftime('%Y-%m-%d %H:%M:%S') + " IST"
            }
            today_data.append(formatted_data)

        return today_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))