import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from telethon import TelegramClient
from telethon.sessions import StringSession
import phonenumbers
from phonenumbers import carrier, geocoder

# Render/Server ke environment se data uthayega
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Client initialization
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.start()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/search")
async def search(request: Request, type: str = Form(...), query: str = Form(...)):
    result = {"type": type, "query": query, "data": {}}
    
    if type == "telegram":
        try:
            user = await client.get_entity(query)
            result["data"] = {
                "Name": f"{user.first_name} {user.last_name or ''}",
                "Username": f"@{user.username}" if user.username else "Hidden",
                "User ID": user.id,
                "Phone": user.phone if user.phone else "Privacy Restricted"
            }
        except Exception:
            result["error"] = "User nahi mila, username check karein."
            
    elif type == "phone":
        try:
            parsed = phonenumbers.parse(query, "IN")
            if phonenumbers.is_valid_number(parsed):
                result["data"] = {
                    "Location": geocoder.description_for_number(parsed, "en"),
                    "Operator": carrier.name_for_number(parsed, "en"),
                    "Validity": "Active Number"
                }
            else:
                result["error"] = "Invalid number format."
        except Exception:
            result["error"] = "Lookup failed."

    return templates.TemplateResponse("index.html", {"request": request, "result": result})
