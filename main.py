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

# For serverless, we need to load manifest lazily
def get_manifest():
    manifest_path = pathlib.Path("svelte/dist/.vite/manifest.json")
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return {"src/index.js": {"file": "index.js", "css": []}}

# Mount /static -> ./static folder (Note: may not work in Vercel serverless)
app.mount("/static", StaticFiles(directory="svelte/dist"), name="static")

templates = Jinja2Templates(directory="templates")

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
        print(f"Error in home route: {e}")
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
        return {"error": f"Failed to initialize data: {str(e)}"}

# ============================================
# VERCEL SERVERLESS HANDLER - CRITICAL!
# ============================================
# For Vercel deployment - the app instance is automatically detected
# No need for additional handler when using @vercel/python

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
