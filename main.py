from pathlib import Path
import asyncio
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
# import logging


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
# BASE_URL = "http://localhost:8000" # <---- define the API base url here.
BASE_URL = "https://orbit.health-nlp.com"
async def fetch_json_url(url: str) -> dict:
    def _fetch() -> dict:
        req = Request(url, headers={"User-Agent": "Orbit-UI/1.0"})
        with urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8"))

    return await asyncio.to_thread(_fetch)

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

@app.get("/orbit-ct", include_in_schema=False, response_class=HTMLResponse)
async def orbit_ct():
    return HTMLResponse(JINJA_ENV.get_template("orbit-ct.html").render())

@app.get("/compare", include_in_schema=False, response_class=HTMLResponse)
async def compare():
    return HTMLResponse(JINJA_ENV.get_template("compare.html").render())

@app.get("/compare-original", include_in_schema=False, response_class=HTMLResponse)
async def compare_original():
    return HTMLResponse(JINJA_ENV.get_template("compare_original.html").render())

@app.get("/api/compare-original", include_in_schema=False)
async def compare_original(query: str, official: str = "clinicaltrials"):
    term = quote_plus(query)

    if official == "pubmed":
        official_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmode=json"
        orbit_url = f"{BASE_URL}/entrez/eutils/esearch.fcgi?term={term}&retmode=json"
        official_key = "pubmed"
    else:
        official_url = f"https://clinicaltrials.gov/api/v2/studies?query.term={term}"
        orbit_url = f"{BASE_URL}/ct/api/v2/studies?query.term={term}"
        official_key = "clinicaltrials"

    print(f"[orbit] {orbit_url}")
    results = {}
    try:
        results["orbit"] = await fetch_json_url(orbit_url)
    except (HTTPError, URLError, json.JSONDecodeError, OSError) as exc:
        results["orbit"] = {"error": str(exc)}

    try:
        results[official_key] = await fetch_json_url(official_url)
    except (HTTPError, URLError, json.JSONDecodeError, OSError) as exc:
        results[official_key] = {"error": str(exc)}

    return results


@app.get("/compare-biomed-lit", include_in_schema=False, response_class=HTMLResponse)
async def compare_biomed_lit():
    return HTMLResponse(JINJA_ENV.get_template("compare_biomed_sources.html").render())

@app.get("/api/compare-biomed-lit", include_in_schema=False)
async def compare_biomed_lit(query: str):
    term = quote_plus(query)

    results = {}
    try:
        orbit_ct_url = f"{BASE_URL}/ct/api/v2/studies?query.term={term}"
        results["clinicaltrials"] = await fetch_json_url(orbit_ct_url)
    except (HTTPError, URLError, json.JSONDecodeError, OSError) as exc:
        results["clinicaltrials"] = {"error": str(exc)}

    try:
        orbit_pubmed_url = f"{BASE_URL}/entrez/eutils/esearch.fcgi?term={term}&retmode=json"
        results["pubmed"] = await fetch_json_url(orbit_pubmed_url)
    except (HTTPError, URLError, json.JSONDecodeError, OSError) as exc:
        results["pubmed"] = {"error": str(exc)}

    return results