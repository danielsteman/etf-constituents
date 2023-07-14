from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/holdings/{fund_id}")
def read_item(fund_id: int, q: Union[str, None] = None):
    return {"fund_id": fund_id, "q": q}
