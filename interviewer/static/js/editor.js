const EDITOR_ID = "code";
const OUTPUT_ID = "output";
const TIME_ID = "time";
const PYTHON_VERSION_ID = "python_version";
const RUN_BUTTON_ID = "run_button";
const BACKEND_PORT = "8000";

const EDITOR_WS_URL = "ws://" + window.location.hostname + ":" + BACKEND_PORT + "/editor_ws/";
const OUTPUT_WS_URL = "ws://" + window.location.hostname + ":" + BACKEND_PORT + "/output_ws/";
const EXECUTE_URL = "http://" + window.location.hostname + ":" + BACKEND_PORT + "/run/";
const PYTHON_VERSION_URL = "http://" + window.location.hostname + ":" + BACKEND_PORT + "/python_version/";


function startEditor() {
    let editorTextarea = document.getElementById(EDITOR_ID);
    let outputTextarea = document.getElementById(OUTPUT_ID);
    let timeInput = document.getElementById(TIME_ID)
    let pythonVersionInput = document.getElementById(PYTHON_VERSION_ID)
    let runButton = document.getElementById(RUN_BUTTON_ID);
    let session_id = window.location.pathname.replaceAll("/", "");
    let editorSocket = new WebSocket(EDITOR_WS_URL + session_id);
    let outputSocket = new WebSocket(OUTPUT_WS_URL + session_id);

    let init = {
            method: 'GET',
            mode: 'cors',
            cache: 'default'
        };
        let pythonVersionRequest = new Request(PYTHON_VERSION_URL + session_id, init);
        fetch(pythonVersionRequest).then(function (response) {
            return response.text()
        }).then((data) => {
            pythonVersionInput.value = data
        });

    let incomeText = "";

    editorSocket.onmessage = (event) => {
        let code = event.data
        incomeText = code;
        editorTextarea.value = code;
    }

    editorSocket.onclose = () => {
        runButton.disabled = true;
    }

    editorTextarea.onchange = () => {
        editorSocket.send(editorTextarea.value)
    }

    outputSocket.onmessage = (event) => {
        let executionInfo = JSON.parse(event.data);
        outputTextarea.value = executionInfo.output;
        timeInput.value = executionInfo.time.toString();
    }

    runButton.onclick = () => {
        runButton.disabled = true;
        editorTextarea.disabled = true;
        let init = {
            method: 'GET',
            mode: 'cors',
            cache: 'default'
        };
        let executionRequest = new Request(EXECUTE_URL + session_id, init);
        fetch(executionRequest).then(function (response) {
            runButton.disabled = false;
            editorTextarea.disabled = false;
        });
    }
}

startEditor()