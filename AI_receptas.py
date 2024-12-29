from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import os

load_dotenv()  # take environment variables from .env.


class GoogleChat(BaseModel):
    ingredients: Optional[list] = None


app = FastAPI()


@app.post("/recipe/")
async def recipe_maker(prompt: GoogleChat):

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    my_recepe_prompt = """
    Eres cocinero de varias estrellas Michelín.
    
    Te voy a dar un listado de ingredientes y lo que debe generar es una receta
    de alguna estrella Michelín que contenga estos ingredientes.
    Además debes indicar cuanto tiempo el cocinero tarda en hacer esta receta.
    
    Los ingredientes son los siguientes:
    
    %s
    
    Aquí te paso un ejemplo de receta:
    
    Pasos de la recepta:
    Tiempo: 3 minutos
    Paso 1: Ingredientes listos.
    Paso 2: Pon un hilito de aove en un sartén y echa  los huevos un poco patidos.
    Echa una lata de atún. Remueve despacio.
    Paso 3: En cuanto cuaje el huevo, pon una ramita de orégano y sívelo.
    Ingredientes: Huevo y Atún.
    
    Devuelveme la recepta en formato html.
    
    """ % (
        prompt.ingredients
    )
    response = model.generate_content(my_recepe_prompt)
    json_compatible_item_data = jsonable_encoder(response.text)
    return JSONResponse(content=json_compatible_item_data)
