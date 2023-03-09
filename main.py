from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from psycopg2 import connect
from fastapi import responses
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import base64

# create connection to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["fastapi"]
collection = db["profile"]

# create connection to PostgreSQL
conn = connect(
    host="localhost",
    database="fastapi_db",
    user="postgres",
    password="12345"
)

# create FastAPI app
app = FastAPI()

# define data models
class User(BaseModel):
    first_name: str
    password: str
    email: str
    phone: str

class Profile(BaseModel):
    user_id: str
    profile_picture: str

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# define API endpoints

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})



@app.post("/register")
async def register_user(request: Request):
    form_data = await request.form()
    fullname = form_data.get("fullname")
    password = form_data.get("password")
    email = form_data.get("email")
    phone = form_data.get("phone")
    img = form_data.get("profile")
    # check if email already exists
    
    profile = await img.read()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    phone TEXT NOT NULL
                );'''
    )
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
    if cursor.fetchone()[0] > 0:
        status_code=400,
        status = 2
        data = {
            "status_cd" : status,
        }
        # raise HTTPException(status_code=400, detail="Email already registered")
        return JSONResponse(data)

    # insert user data into PostgreSQL
    cursor.execute("INSERT INTO users (full_name, password, email, phone) VALUES (%s, %s, %s, %s) RETURNING id", (fullname, password, email, phone))
    user_id = cursor.fetchone()[0]
    conn.commit()
    
    # insert profile picture data into MongoDB
    if profile:
        collection.insert_one({"user_id": str(user_id), "profile_picture": profile})
    
    # return {"user_id": str(user_id)}
    data = {
        "status_cd" : 1,
        "fullname" : fullname,
        "email": email,
        "phone" : phone,
        "user_id" : user_id,
    }
    return JSONResponse(data)

@app.get("/users/{user_id}")
async def get_user_details(user_id: str):
    # get user data from PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, phone FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = {"full_name": user_data[0], "email": user_data[1], "phone": user_data[2]}
    
    # get profile picture data from MongoDB
    profile_data = collection.find_one({"user_id": user_id})
    if profile_data:
        pros = profile_data["profile_picture"]
        
        profile_picture = {"image_data": base64.b64encode(pros).decode("utf-8")}
        # user_dict["profile_picture"] = profile_data["profile_picture"]
        user_dict["profile_picture"] = profile_picture
    return user_dict    
