const EDITOR_ID = "code";
const OUTPUT_ID = "output";
const TIME_ID = "time";

const RUN_BUTTON_ID = "run_button";
const EDITOR_WS_URL = "ws://localhost:8000/editor_ws/";
const OUTPUT_WS_URL = "ws://localhost:8000/output_ws/";
const EXECUTE_URL = "http://localhost:8000/run/";


function startEditor() {
    let editorCodeMirror = CodeMirror(document.getElementById(EDITOR_ID), {
        lineNumbers: true,
        mode: "python",
        theme: "darcula",
    });
    editorCodeMirror.setSize(1000, 600);
    let outputCodeMirror = CodeMirror(document.getElementById(OUTPUT_ID), {
        readOnly: true,
    });
    outputCodeMirror.setSize(1000, 200);
    let timeCodeMirror = CodeMirror(document.getElementById(TIME_ID), {
        readOnly: true,
        theme: "darcula",
    });
    timeCodeMirror.setSize(1000, 50)
    let runButton = document.getElementById(RUN_BUTTON_ID);
    let session_id = window.location.pathname.replaceAll("/", "");
    let editorSocket = new WebSocket(EDITOR_WS_URL + session_id);
    let outputSocket = new WebSocket(OUTPUT_WS_URL + session_id);
    let incomeText = "";

    editorSocket.onmessage = (event) => {
        let code = event.data
        incomeText = code;
        editorCodeMirror.setValue(code)
    }

    editorSocket.onclose = () => {
        runButton.disabled = true;
    }

    outputSocket.onmessage = (event) => {
        let executionInfo = JSON.parse(event.data);
        outputCodeMirror.setValue(executionInfo.output);
        timeCodeMirror.setValue(executionInfo.time.toString());
    }

    editorCodeMirror.on(
        "change",
        function () {
            let code = editorCodeMirror.getValue();
            if (code !== incomeText) {
                editorSocket.send(editorCodeMirror.getValue())
            }
        }
    )

    runButton.onclick = () => {
        runButton.disabled = true;
        editorCodeMirror.disabled = true;
        let myInit = {
            method: 'GET',
            mode: 'cors',
            cache: 'default'
        };
        let myRequest = new Request(EXECUTE_URL + session_id, myInit);
        fetch(myRequest).then(function (response) {
            runButton.disabled = false;
            editorCodeMirror.disabled = false;
        });
    }
}

startEditor()