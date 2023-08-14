from fastapi import FastAPI

from application.db_app import models
from application.db_app.database import engine
from application.routers import dish_routers, menu_routers, submenu_routers

app = FastAPI()


@app.on_event('startup')
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app.include_router(menu_routers.router)
app.include_router(submenu_routers.router)
app.include_router(dish_routers.router)
