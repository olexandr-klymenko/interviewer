const EDITOR_ID = "editor";
const EDITOR_WS_URL = "ws://localhost:8000/editor_ws";


function startEditor() {
    let editor = new Editor();
    editor.init()
}


class Editor {
    constructor() {
        this.textarea = document.getElementById(EDITOR_ID);
        this.session_id = this.textarea.getAttribute("name")
        this.socket = new WebSocket(EDITOR_WS_URL);
        this.init = this.init.bind(this);
    }

    init() {
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log("Received code: " + message["code"] + " session_id: " + message["session_id"]);
            if (message["session_id"] !== this.session_id) {
                this.textarea.value = message["code"];
            }
        }
        this.textarea.onchange = () => {
            this.socket.send(JSON.stringify({
                "session_id": this.session_id,
                "code": this.textarea.value
            }));
        }
    }
}

startEditor()