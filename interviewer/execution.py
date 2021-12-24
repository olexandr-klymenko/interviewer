import os
import subprocess
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from time import time
from typing import Dict

from interviewer.config import EXECUTION_TIME_LIMIT


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
