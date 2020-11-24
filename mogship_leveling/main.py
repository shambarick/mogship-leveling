from fastapi import FastAPI
import uvicorn

from mogship_leveling.api.api_v1.api import api_router
from mogship_leveling.core import elasticsearch as es
from mogship_leveling.core.logging import init_logging

init_logging()


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_event_handler("startup", es.connect_to_es)
    app.add_event_handler("shutdown", es.close_es_connection)
    app.include_router(api_router)
    return app


app = create_app()

if __name__ == '__main__':
    uvicorn.run(app, port=8000)
