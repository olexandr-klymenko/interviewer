const EDITOR_ID = "editor";
const OUTPUT_ID = "output";
const TIME_ID = "time";

const RUN_BUTTON_ID = "run_button";
const EDITOR_WS_URL = "ws://localhost:8000/editor_ws/";
const OUTPUT_WS_URL = "ws://localhost:8000/output_ws/";
const EXECUTE_URL = "http://localhost:8000/run/";


function startEditor() {
    let editorTextarea = document.getElementById(EDITOR_ID);
    let outputTextarea = document.getElementById(OUTPUT_ID);
    let executionTimeLine = document.getElementById(TIME_ID);
    let runButton = document.getElementById(RUN_BUTTON_ID);
    let session_id = editorTextarea.getAttribute("name");
    let editorSocket = new WebSocket(EDITOR_WS_URL + session_id);
    let outputSocket = new WebSocket(OUTPUT_WS_URL + session_id);

    editorSocket.onmessage = (event) => {
        editorTextarea.value = event.data;
    }

    editorSocket.onclose = () => {
        runButton.disabled = true;
    }

    outputSocket.onmessage = (event) => {
        let executionInfo = JSON.parse(event.data);
        outputTextarea.value = executionInfo.output;
        executionTimeLine.value = executionInfo.time;
        console.log(executionInfo.time);
    }

    editorTextarea.onchange = () => {
        editorSocket.send(editorTextarea.value);
    }

    runButton.onclick = () => {
        runButton.disabled = true;
        editorTextarea.disabled = true;
        let myInit = {
            method: 'GET',
            mode: 'cors',
            cache: 'default'
        };
        let myRequest = new Request(EXECUTE_URL + session_id, myInit);
        fetch(myRequest).then(function (response) {
            console.log(response.statusText);
            runButton.disabled = false;
            editorTextarea.disabled = false;
        });
    }
}

startEditor()