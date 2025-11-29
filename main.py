from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
URL = f"mongodb+srv://{USERNAME}:{PASSWORD}@portfoliocluster.pcgilwr.mongodb.net/?appName=PortfolioCluster"

try:
    client = AsyncIOMotorClient(URL)
    print("Connected To MongoDB!!")
except Exception as e:
    print(e)

db = client["portfolioDB"]

lang = db["languages"]


app = FastAPI(
    title="Portfolio API",
    description="My backend, my rules, my era",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"hi":"Wow Im Cooking!!"}

@app.get("/languages")
async def Languages():
    data = await lang.find().to_list()
    for doc in data:
        doc["_id"] = str(doc["_id"])
    # print(data)
    return data

