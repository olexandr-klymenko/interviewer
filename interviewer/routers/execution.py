import os
import subprocess
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from time import time
from typing import Dict

from fastapi import APIRouter, Response

from interviewer.cache import redis
from interviewer.config import EXECUTION_TIME_LIMIT
from interviewer.constants import SESSIONS
from interviewer.sessions import output_sessions

router = APIRouter()


@dataclass
class ExecuteData:
    stdout: str
    stderr: str
    execution_time: float = 0.0

    def output(self) -> Dict[str, str]:
        return {
            "output": self.stdout or self.stderr,
            "time": f"Execution time: {self.execution_time:.5f}",
        }


def execute(session_id: str, code: bytes) -> ExecuteData:
    tmp_file = NamedTemporaryFile(prefix=session_id, delete=False)
    try:
        tmp_file.write(code)
        tmp_file.close()
        start_time = time()
        completed = subprocess.run(
            ["python3", tmp_file.name],
            capture_output=True,
            timeout=EXECUTION_TIME_LIMIT,
        )
        return ExecuteData(
            stdout=completed.stdout.decode(),
            stderr=completed.stderr.decode(),
            execution_time=time() - start_time,
        )
    except (subprocess.TimeoutExpired, Exception) as err:
        return ExecuteData(stdout="", stderr=str(err))
    finally:
        os.unlink(tmp_file.name)


@router.get("/run/{session_id}")
async def run(session_id: str):
    if await redis.hexists(SESSIONS, session_id):
        code = await redis.hget(SESSIONS, session_id)
        execution_info = execute(session_id=session_id, code=code.encode())
        await output_sessions.broadcast(execution_info.output(), session_id=session_id)
        return Response(status_code=200)
    return Response(status_code=404)


@router.get("/python_version/{session_id}")
async def python_version(session_id: str):
    execution_info = execute(
        session_id=session_id, code="import sys;print(sys.version)".encode()
    )
    data = f"Python version: {execution_info.output()['output'].split()[0]}"
    return Response(data)
