from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.


class GoogleChat(BaseModel):
    prompt: str


app = FastAPI()


@app.post("/chat/")
async def AI(prompt: GoogleChat):

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt.prompt)
    return {"response": response.text}
