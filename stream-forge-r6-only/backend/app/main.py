from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.cors import configure_cors

app = FastAPI(title=settings.app_name)
configure_cors(app)
app.include_router(router)
