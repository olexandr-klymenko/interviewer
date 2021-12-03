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
        indentUnit: "4",
        pollInterval: "10",
        // smartIndent: false,
    });
    editorCodeMirror.setSize(1000, 700);
    let outputTextarea = document.getElementById(OUTPUT_ID);
    // let outputCodeMirror = CodeMirror(document.getElementById(OUTPUT_ID), {
    //     readOnly: true,
    // });
    // outputCodeMirror.setSize(1000, 150);
    let timeInput = document.getElementById(TIME_ID)
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
        outputTextarea.value = executionInfo.output;

        // outputCodeMirror.setValue(executionInfo.output);
        timeInput.value = executionInfo.time.toString();
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
        let init = {
            method: 'GET',
            mode: 'cors',
            cache: 'default'
        };
        let myRequest = new Request(EXECUTE_URL + session_id, init);
        fetch(myRequest).then(function (response) {
            runButton.disabled = false;
            editorCodeMirror.disabled = false;
        });
    }
}

startEditor()