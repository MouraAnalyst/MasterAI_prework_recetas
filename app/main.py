from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy import create_engine
import os

load_dotenv()  # take environment variables from .env.


class GoogleChat(BaseModel):
    ingredients: Optional[list] = None


class Recipe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str


db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_username = os.environ["DB_USERNAME"]
db_name = os.environ["DB_NAME"]
db_url = f"postgresql+psycopg://{db_username}:{db_password}@{db_host}/{db_name}"

engine = create_engine(db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/recipes/")
async def recipe_list(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Recipe]:
    recipes = session.exec(select(Recipe).offset(offset).limit(limit)).all()

    return recipes


@app.post("/recipe/")
async def recipe_maker(prompt: GoogleChat, session: SessionDep) -> Recipe:

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
    
    Devuelveme la recepta en formato markdown.
    
    """ % (
        prompt.ingredients
    )
    response = model.generate_content(my_recepe_prompt)
    json_compatible_item_data = jsonable_encoder(response.text)

    recipe = Recipe()
    recipe.description = response.text
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return JSONResponse(content=json_compatible_item_data)
