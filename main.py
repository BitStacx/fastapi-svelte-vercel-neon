import json
import os
import pathlib
from database import Base, engine, get_session
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from models import Page
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging


app = FastAPI(title="FastAPI Svelte Vercel Neon", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for local development
# This will be handled by Vercel routes in production
if os.getenv("VERCEL") != "1":  # Only mount static files when not on Vercel
    app.mount("/static", StaticFiles(directory="svelte/dist"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)

# For serverless, we need to load manifest lazily
def get_manifest():
    manifest_path = pathlib.Path("svelte/dist/.vite/manifest.json")
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return {"src/index.js": {"file": "index.js", "css": []}}

templates = Jinja2Templates(directory="templates")

# Create tables on startup
@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Failed to create database tables: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_session)):
    try:
        result = await db.execute(select(Page).where(Page.name == 'index'))
        page = result.scalar_one_or_none()
        
        props = {}
        props["heading"] = "FastAPI Svelte Vercel Neon - Hard Code"
        
        if page:
            props["heading"] = page.title
            
        manifest = get_manifest()
        entry = manifest["src/index.js"]
        
        return templates.TemplateResponse("index.j2", {
            "request": request,
            "title": props["heading"],
            "props": props,
            "bundle": entry,
        })
    except Exception as e:
        # Log the error and return a fallback response
        logging.error(f"Error in home route: {e}")
        await db.rollback()
        props = {"heading": "FastAPI Svelte Vercel Neon - Error Fallback"}
        manifest = get_manifest()
        entry = manifest["src/index.js"]
        
        return templates.TemplateResponse("index.j2", {
            "request": request,
            "title": props["heading"],
            "props": props,
            "bundle": entry,
        })

@app.post("/init-data")
async def init_data(db: AsyncSession = Depends(get_session)):
    """Initialize some sample data in the database"""
    try:
        # Check if index page already exists
        result = await db.execute(select(Page).where(Page.name == 'index'))
        existing_page = result.scalar_one_or_none()
        
        if not existing_page:
            # Create an index page
            index_page = Page(name="index", title="Welcome to FastAPI + Svelte + Neon!")
            db.add(index_page)
            await db.commit()
            return {"message": "Index page created successfully"}
        else:
            return {"message": "Index page already exists"}
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to initialize data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "fastapi-svelte-vercel-neon"}

@app.get("/api/pages")
async def get_pages(db: AsyncSession = Depends(get_session)):
    """Get all pages"""
    try:
        result = await db.execute(select(Page))
        pages = result.scalars().all()
        return [{"id": page.id, "name": page.name, "title": page.title} for page in pages]
    except Exception as e:
        logging.error(f"Error fetching pages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pages")

# Add handler for Vercel
handler = app
    