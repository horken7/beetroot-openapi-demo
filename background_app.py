from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()
background_color = "#FFFFFF"  # Default background color (white)
clients: List[WebSocket] = []  # List to store active WebSocket clients

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Color Changer</title>
</head>
<body style="background-color: {background_color}" id="body">
    <script>
        var ws = new WebSocket("ws://" + window.location.host + "/ws");
        ws.onmessage = function(event) {{
            var body = document.getElementById("body");
            body.style.backgroundColor = event.data;
        }};
    </script>
</body>
</html>
"""     


@app.get("/", response_class=HTMLResponse)
async def get():
    return html.format(background_color=background_color)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)


@app.post("/change_color")
async def change_color(rgb: dict = Body(...)):
    r, g, b = rgb.get("r"), rgb.get("g"), rgb.get("b")
    global background_color
    background_color = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
    for client in clients:
        await client.send_text(background_color)
    return {"color": background_color}
