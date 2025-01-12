import asyncio
import logging
from asyncio import wait_for
from asyncio import StreamReader 
from asyncio import StreamWriter


class CharServer:
    
    def __init__(self):
        self._connected_clients = {}

    async def start(self, host: str, port: int):
        server = await asyncio.start_server(
            client_connected_cb=self.register_user,
            host=host,
            port=port)
        async with server:
            await server.serve_forever()

    async def register_user(self, reader: StreamReader, writer: StreamWriter):
        data = await reader.readline()
        command, name = data.split(b":")
        if command == b"NAME":
            await self._add_user(name.decode(), writer, reader)
            await self._on_connect(name.decode(), writer)
        else:
            logging.error("Неизвестная комманда от клиента, разрыв соединения")
            writer.close()
            await writer.wait_closed()
    
    async def _add_user(self, name: str,
                        writer: StreamWriter,
                        reader: StreamReader):
        self._connected_clients[name] = writer
        asyncio.create_task(self._message_handling(name, reader))
    
    async def _message_handling(self,
                                name: str,
                                reader: StreamReader):
        try:
            while (message := await wait_for(reader.readline(), 120)) != b"":
                await self._notify_all(f"{name.strip()}: {message.decode()}")
            await self._delete_user(name)
        except Exception as e:
            logging.exception("Ошибка при чтении данных от клиента",
                              exc_info=e)
            await self._delete_user(name)

    async def _on_connect(self, name: str, writer: StreamWriter):
        number_connected_clients = len(self._connected_clients)
        writer.write(f"Добро пожаловать! Подключено пользователей: "
                     f"{number_connected_clients}\n".encode())
        await writer.drain()
        await self._notify_all(f"Подключился новый "
                               f"пользователь {name}")
    
    async def _notify_all(self, message: str):
        inactive_users = []
        for name in self._connected_clients:
            try:
                writer = self._connected_clients[name]
                writer.write(message.encode())
                await writer.drain()
            except ConnectionError as e:
                logging.exception("Ошибка при отправке сообщения клиенту",
                                  exc_info=e)
                inactive_users.append(name)
        [await self._delete_user(name) for name in inactive_users]
    
    async def _delete_user(self, name: str):
        writer = self._connected_clients[name]
        self._connected_clients.pop(name)
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logging.exception("Ошибка при закрытии клиентского StreamWriter",
                              exc_info=e)


async def main():
    port = 8000
    host = "127.0.0.1"
    chat_server = CharServer()
    await chat_server.start(host, port)

asyncio.run(main())
