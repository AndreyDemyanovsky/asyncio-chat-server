from collections import deque
from typing import Deque, Awaitable, Callable


class MessageStorage:

    def __init__(self,
                 rows_number: int,
                 callback: Callable[[Deque], Awaitable[None]]):

        self._deque_messages: Deque = deque(maxlen=rows_number)
        self._callback = callback

    async def append(self, message: str):
        self._deque_messages.append(message)
        await self._callback(self._deque_messages)