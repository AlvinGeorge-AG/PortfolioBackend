from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os , httpx
load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
URL = f"mongodb+srv://{USERNAME}:{PASSWORD}@portfoliocluster.pcgilwr.mongodb.net/?appName=PortfolioCluster"

try:
    client = AsyncIOMotorClient(URL)
    print("Connected To MongoDB!!")
except Exception as e:
    print(e)

db = client["portfolioDB"]

languages = db["languages"]
projects = db["projects"]


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


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@app.get("/")
def home():
    return {"hi":"Wow Im Cooking!!"}

@app.get("/languages")
async def Languages():
    data = await languages.find().to_list()
    for doc in data:
        doc["_id"] = str(doc["_id"])
    # print(data)
    return data


@app.post("/sendmail")
async def send_mail(form: ContactForm):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY or ""),
            data={
                "from": f"Portfolio Contact Form <postmaster@{MAILGUN_DOMAIN}>", 
                "to":"alvingeorge_@outlook.com",
                "subject": form.subject,
                "text": f"📩 New message alert!\n\nName: {form.name}\nFrom: {form.email}\n\nMessage:\n{form.message}"
            }
        )
        #print(response.text)
    return {"status": response.status_code, "details": response.text}


@app.get("/projects")
async def Projects():
    data = await projects.find().to_list()
    for project in data:
        project["_id"] = str(project["_id"])
        #print(data)
    return data


