from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


# table=True tells SQLMODEL that it is a table in the SQL Db
class Fighter(SQLModel, table=True):
    id: int | None = Field(default=None , primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_nickname: str


class Division(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    weight: int | None = Field(default=None, index=True)


class Country(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


# ENGINE: holds connection to the DB 
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"



# It allows SQLite DB in different threads - One single request can use more than one thread
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)



# Create tables for table models - see Fighter
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Create a Session dependency - A database session represents a temporary, isolated connection to the database
def get_sessions():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_sessions)]



# Creating DB tables when app starts
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()



# E N D   P O I N T S


# CREATING FIGHTERS - Adding a new fighter to the Session instance, commit changes to the db
@app.post("/fighters/")
def create_fighter(fighter: Fighter, session: SessionDep) -> Fighter:
    session.add(fighter)
    session.commit()
    session.refresh(fighter)
    return fighter


# Read fighters from the database using select
@app.get("/fighters")
def read_fighter(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,) -> list[Fighter]:
    fighters = session.exec(select(Fighter).offset(offset).limit(limit)).all()
    return fighters


@app.get("/fighters/{fighter_id}")
def read_fighter(fighter_id: int, session: SessionDep) -> Fighter:
    fighter = session.get(Fighter, fighter_id)
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    return fighter



# DIVSIONS' ENDOPOINTS
@app.post("/divisions/")
def create_division(division: Division, session: SessionDep) -> Division:
    session.add(division)
    session.commit()
    session.refresh(division)
    return division


@app.get("/divisions")
def read_division(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,) -> list[Division]:
    divisions = session.exec(select(Division).offset(offset).limit(limit)).all()
    return divisions



@app.post("/Countries")
def create_country(country: Country, session: SessionDep) -> Country:
    session.add(country)
    session.commit()
    session.refresh(country)
    return country




# Read individual fighter


# @app.get("/fighters/{fighter_id}")
# def read_fighter(fighter_id: int, session: SessionDep) -> Fighter:
#     fighter = session.get(Fighter, fighter_id)
#     if not fighter:
#         raise HTTPException(status_code=404, detail="Fighter not found")
#     return fighter



@app.delete("/fighters/{fighter_id}")
def delete_fighter(fighter_id: int, session: SessionDep):
    fighter = session.get(Fighter, fighter_id)
    if not fighter:
        raise HTTPException(status_code=400, detail="Fighter not found")
    session.delete(fighter)
    session.commit()
    return {"ok": True}
