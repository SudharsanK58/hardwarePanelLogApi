from fastapi import FastAPI, HTTPException, Request
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
attendants_collection = db.Attendants
patient_details_collection = db.patientDetails


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

@app.post("/register_attendant")
async def register_attendant(request: Request):
    try:
        # Access the request body directly
        data = await request.json()

        # Extract name and password from the request body
        name = data.get("name")
        password = data.get("password")

        # Check if the attendant with the same name already exists
        existing_attendant = attendants_collection.find_one({"name": name})
        if existing_attendant:
            raise HTTPException(status_code=400, detail="Attendant with this name already exists")

        # Insert the new attendant into the collection
        result = attendants_collection.insert_one({"name": name, "password": password})

        # Check if the insertion was successful
        if result.inserted_id:
            return {"message": "Attendant registered successfully"}

        raise HTTPException(status_code=500, detail="Failed to register attendant")

    except HTTPException as http_exc:
        # Forward HTTPException with custom detail message
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(request: Request):
    try:
        # Access the request body directly
        data = await request.json()

        # Extract name and password from the request body
        name = data.get("name")
        password = data.get("password")

        # Check if the attendant with the provided name exists
        attendant = attendants_collection.find_one({"name": name})

        if attendant and attendant["password"] == password:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException as http_exc:
        # Forward HTTPException with custom detail message
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save_patient_details")
async def save_patient_details(request: Request):
    try:
        # Access the request body directly
        data = await request.json()

        # Extract patient details from the request body
        patient_details = {
            "Name": data.get("name"),
            "Age": data.get("age"),
            "Gender": data.get("gender"),
            "City": data.get("city"),
            "Height": data.get("height"),
            "Weight": data.get("weight"),
            "PhoneNumber": data.get("phone_number"),
        }

        # Get the latest patient ID
        latest_patient = patient_details_collection.find_one(sort=[("PatientId", -1)])
        latest_patient_id = latest_patient["PatientId"] if latest_patient else 1000

        # Increment patient ID for the new patient
        new_patient_id = latest_patient_id + 1

        # Save patient details in the collection
        result = patient_details_collection.insert_one({"PatientId": new_patient_id, **patient_details})

        # Check if the insertion was successful
        if result.inserted_id:
            return {"PatientId": new_patient_id}

        raise HTTPException(status_code=500, detail="Failed to save patient details")

    except HTTPException as http_exc:
        # Forward HTTPException with custom detail message
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save_disease_history")
async def save_disease_history(request: Request):
    try:
        # Access the request body directly
        data = await request.json()

        # Extract patient ID and disease history from the request body
        patient_id = data.get("patient_id")
        disease_history = {
            "Diabetes": data.get("diabetes"),
            "HeartAttack": data.get("heart_attack"),
            "Paralysis": data.get("paralysis"),
            "Gangrene": data.get("gangrene"),
            "BloodPressure": data.get("blood_pressure"),
            "BreathingDifficulty": data.get("breathing_difficulty"),
        }

        # Find the patient by ID
        patient = patient_details_collection.find_one({"PatientId": patient_id})

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Update the patient's disease history with the new data and Heart Health
        heart_health = (
            disease_history.get("Diabetes", 0) * 1 +
            disease_history.get("HeartAttack", 0) * 2 +
            disease_history.get("Paralysis", 0) * 3 +
            disease_history.get("Gangrene", 0) * 4 +
            disease_history.get("BloodPressure", 0) * 5 +
            disease_history.get("BreathingDifficulty", 0) * 6
        )
        
        disease_history["HeartHealth"] = heart_health

        patient_details_collection.update_one(
            {"PatientId": patient_id},
            {"$set": {"disease": disease_history}},
        )

        # Return the Heart Health value in the response
        return {"HeartHealth": heart_health}

    except HTTPException as http_exc:
        # Forward HTTPException with custom detail message
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))