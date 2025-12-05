from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# M O D E L S

# table=True tells SQLMODEL that it is a table in the SQL Db
class FighterBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Fighter(FighterBase, table=True):
    id: int | None = Field(default=None , primary_key=True)
    secret_nickname: str


class FighterPublic(FighterBase):
    id: int


# THIS MODEL WILL VALIDATE DATA FROM THE CLIENTS
class FighterCreate(FighterBase):
    secret_nickname: str


# All fields are optional,  when you update a fighter you can just send the fields that you want to update
class FighterUpdate(FighterBase):
    name: str = None = None
    age: int | None = None
    secret_nickname: str



# D B   C O N N E C T I O N

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
@app.post("/fighters/", response_model=FighterPublic)
def create_fighter(fighter: FighterCreate, session: SessionDep):
    db_fighter = Fighter.model_validate(fighter)
    session.add(db_fighter)
    session.commit()
    session.refresh(db_fighter)
    return db_fighter


# Reading fighters
@app.get("/fighters/", response_model=list[HeroPulic])
def read_fighters(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    fighters = session.exec(select(Fighter).offset(offset).limit(limit)).all()
    return fighters



@app.patch("/fighers/{fighter_id}", response_model=FighterPublic)
def update_fighter(fighter_id: int, fighter: FighterUpdate, session: SessionDep):
    fighter_db = session.get(Hero, hero_id)
    if not fighter_db:
        raise HTTPException(status_code=404, detail="Fighter not found")
    fighter_data = fighter.model_dump(exclude_unset=True)
    fighter_db.sqlmodel_update(fighter_data)
    session.add(fighter_db)
    session.commit()
    session.refresh(fighter_db)
    return fighter_db
