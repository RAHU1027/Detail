from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from telethon.sync import TelegramClient
import phonenumbers
from phonenumbers import carrier, geocoder
import os

# --- CONFIG ---
API_ID = 21552435
API_HASH = "5b108bd2fdd31c0c34bc65f24a5216a0"

app = FastAPI()
templates = Jinja2Templates(directory="templates")
client = TelegramClient('session_bot', API_ID, API_HASH)

# --- STARTUP ---
@app.on_event("startup")
async def startup():
    await client.start()

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/search")
async def search(request: Request, type: str = Form(...), query: str = Form(...)):
    result = {"type": type, "query": query, "data": {}}
    
    # 1. TELEGRAM LOOKUP
    if type == "telegram":
        try:
            user = await client.get_entity(query)
            result["data"] = {
                "Full Name": f"{user.first_name} {user.last_name or ''}",
                "Username": f"@{user.username}" if user.username else "N/A",
                "User ID": user.id,
                "Phone": user.phone if user.phone else "Hidden/Private"
            }
        except Exception as e:
            result["error"] = "User nahi mila ya invalid username hai."

    # 2. PHONE LOOKUP
    elif type == "phone":
        try:
            parsed = phonenumbers.parse(query, "IN")
            if phonenumbers.is_valid_number(parsed):
                result["data"] = {
                    "Location": geocoder.description_for_number(parsed, "en"),
                    "Operator": carrier.name_for_number(parsed, "en"),
                    "Format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    "Type": "Mobile/Landline"
                }
            else:
                result["error"] = "Number valid nahi hai."
        except Exception:
            result["error"] = "Number format galat hai."

    return templates.TemplateResponse("index.html", {"request": request, "result": result})
