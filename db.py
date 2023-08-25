import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import models
import schemas

load_dotenv()


def get_db() -> Session:
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def load_holding(holding: schemas.FundHolding, db: Session = get_db()) -> None:
    holding_db_obj = models.FundHolding(**holding)
    db.add(holding_db_obj)
    db.commit()
