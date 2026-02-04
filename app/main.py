from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .data import LISTINGS

app = FastAPI(title="Pieces Methanisation Pro")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    featured = LISTINGS[:6]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "featured": featured, "count": len(LISTINGS)},
    )


@app.get("/annonces", response_class=HTMLResponse)
def listings(request: Request):
    return templates.TemplateResponse(
        "listing.html",
        {"request": request, "listings": LISTINGS},
    )


@app.get("/annonces/{listing_id}", response_class=HTMLResponse)
def listing_detail(request: Request, listing_id: int):
    listing = next((l for l in LISTINGS if l["id"] == listing_id), None)
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return templates.TemplateResponse(
        "detail.html",
        {"request": request, "listing": listing, "listings": LISTINGS},
    )


@app.get("/deposer", response_class=HTMLResponse)
def create_listing(request: Request):
    return templates.TemplateResponse(
        "create.html",
        {"request": request},
    )


@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse(
        "contact.html",
        {"request": request},
    )
