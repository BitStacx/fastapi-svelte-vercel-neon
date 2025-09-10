import json
import pathlib
from database import Base, engine, get_session
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Page
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


app = FastAPI()

# Mount /static -> ./static folder
app.mount("/static", StaticFiles(directory="svelte/dist"), name="static")

manifest_path = pathlib.Path("svelte/dist/.vite/manifest.json")
with open(manifest_path) as f:
    manifest = json.load(f)

templates = Jinja2Templates(directory="templates")

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_session)):
    
    result = await db.execute(select(Page).where(Page.name == 'index'))
    page = result.scalar_one_or_none()
    
    props = {}
    props["heading"] = "FastAPI Svelte Vercel Neon - Hard Code"
    
    if page:
        props["heading"] = page.title
        
    entry = manifest["src/index.js"]
    
    return templates.TemplateResponse("index.j2", {
        "request": request,
        "title": props["heading"],
        "props": props,
        "bundle": entry,
    })
