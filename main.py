from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket
from loguru import logger

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_id = uuid4()
    page = templates.TemplateResponse(
        "index.html", context={"request": request, "session_id": session_id}
    )
    logger.info(str(page.body))
    return page


@app.websocket("/editor_ws/")
async def editor_web_socket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logger.info(f"Received: {data}")
        await websocket.send_text(data)


if __name__ == "__main__":
    uvicorn.run(app)
