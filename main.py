from pathlib import Path

import jinja2
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Orbit UI", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt deinem Browser, von überall zuzugreifen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=jinja2.select_autoescape(["html", "xml"]),
)
BASE_URL = "http://localhost:8000" # <---- define the API base url here.

@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def root():
    return HTMLResponse(JINJA_ENV.get_template("index.html").render())

# Route `/docs` by redirecting to Swagger UI documentation at BASE_URL/docs
@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
async def docs_redirect():
    return RedirectResponse(url=f"{BASE_URL}/docs")

@app.get("/contributors", include_in_schema=False, response_class=HTMLResponse)
async def contributors():
    return HTMLResponse(JINJA_ENV.get_template("contributors.html").render())