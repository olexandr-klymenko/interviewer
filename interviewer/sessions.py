from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket


class Sessions:
    def __init__(self):
        self._info: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)

    async def connect(self, session_id, socket_id, socket):
        await socket.accept()
        self._info[session_id].update({socket_id: socket})

    async def broadcast(self, data, session_id, source_socket_id=None):
        for socket in self._target_sockets(
            session_id=session_id, source_socket_id=source_socket_id
        ):
            if isinstance(data, str):
                await socket.send_text(data)
            if isinstance(data, dict):
                await socket.send_json(data)

    def _target_sockets(self, session_id, source_socket_id=None) -> List[WebSocket]:
        return [
            socket
            for _id, socket in self._info[session_id].items()
            if _id != source_socket_id
        ]

    def disconnect(self, session_id, socket_id):
        self._info[session_id].pop(socket_id)


editor_sessions = Sessions()
output_sessions = Sessions()
