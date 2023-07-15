#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncpg
from fastapi import FastAPI
from fastapi import Depends
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request

async def connect_to_database():
    conn = await asyncpg.connect(
        host="localhost",
        port="8585",
        user="postgres",
        password="your_password",
        database="database_name",
    )
    return conn

async def get_database_connection():
    conn = await connect_to_database()
    try:
        yield conn
    finally:
        await conn.close()
app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.db = await connect_to_database()

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
    
templates = Jinja2Templates(directory="./")

@app.get("/form")
async def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


class MyData(BaseModel):
    user_name: str
    password: str


@app.post("/")
async def handle_post_request(data: MyData, db: asyncpg.Connection = Depends(get_database_connection)):
    # Print the received data
    print(data.dict())

    # Insert the data into a table
    await db.execute(
        "INSERT INTO users (user_name, password) VALUES ($1, $2)",
        data.user_name, data.password
    )

    return {"message": "Data inserted successfully"}