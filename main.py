from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr,BaseModel
import httpx
import os
load_dotenv()

class ContactForm(BaseModel):
    name : str
    email : EmailStr
    subject : str
    message : str

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
URL = f"mongodb+srv://{USERNAME}:{PASSWORD}@portfoliocluster.pcgilwr.mongodb.net/?appName=PortfolioCluster"

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")

if MAILGUN_API_KEY is None:
    raise RuntimeError("MAILGUN_API_KEY is not set in environment")

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
    data = await lang.find().to_list(100)
    for doc in data:
        doc["_id"] = str(doc["_id"])
    # print(data)
    return data



@app.post("/sendmail")
async def send(form: ContactForm):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY or ""),
            data={
                "from": form.email,
                "to": "Alvin <alvingeorge_@outlook.com>",
                "subject": form.subject,
                "text": f"📩 You got a new message!\n\nName : {form.name}\n\nFrom: {form.email}\n\nMessage:\n{form.message}"
            }
        )
    return {"status": response.status_code, "details": response.text}


handler = app