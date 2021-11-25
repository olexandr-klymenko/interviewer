const EDITOR_ID = "editor";
const EDITOR_WS_URL = "ws://localhost:8000/editor_ws/";


function startEditor() {
    let textarea = document.getElementById(EDITOR_ID);
    let session_id = textarea.getAttribute("name");
    console.log("Starting session: " + session_id);
    let socket = new WebSocket(EDITOR_WS_URL + session_id);
    socket.onmessage = (event) => {
        const message = event.data;
        console.log("Received code: " + message);
        textarea.value = message;
    }

    socket.onclose = () => {
        console.log("Closed connection");
    }
    textarea.onchange = () => {
        socket.send(textarea.value);
    }
}

startEditor()