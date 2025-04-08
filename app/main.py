from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import Response, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

from .database import (
    get_db_connection,
    setup_database
)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for managing application startup and shutdown.
    Handles database setup and cleanup in a more structured way.
    """
    # Startup: Setup resources
    try:
        await setup_database() 
        print("Database setup completed")

        yield
    finally:
        print("Shutdown completed")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def read_html(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
def home_html():
    return HTMLResponse(content=read_html("app/static/html/homepage.html"))

@app.get("/student-section", response_class=HTMLResponse)
def student_html():
    return HTMLResponse(content=read_html("app/static/html/student_section.html"))

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=8000, reload=True)