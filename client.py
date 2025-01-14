import asyncio
import logging
import tty
import os
import sys
from asyncio import StreamWriter, StreamReader
from collections import deque
from message_storage import MessageStorage
from terminal_management import move_to_down_of_screen
from terminal_management import save_cursor_position
from terminal_management import restore_cursor_position
from terminal_management import delete_line
from terminal_management import move_to_top_of_screen
from terminal_management import read_line


async def create_stream_reader() -> StreamReader:
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def redraw_output(messages: deque):
    save_cursor_position()
    move_to_top_of_screen()
    for message in messages:
        delete_line()
        sys.stdout.write(message)
    restore_cursor_position()


async def server_listening(server_reader: StreamReader,
                           messages: MessageStorage):
    while (message := await server_reader.readline()) != b"":
        await messages.append(message.decode())


async def read_from_client_and_send_to_server(server_writer: StreamWriter,
                                              stdin_reader: StreamReader):
    while True:
        message = await read_line(stdin_reader)
        message += "\n"
        server_writer.write(message.encode())
        await server_writer.drain()


async def main():
    server_port = 8000
    server_host = "127.0.0.1"
    tty.setcbreak(0)
    os.system("clear")
    rows = move_to_down_of_screen()
    messages = MessageStorage(rows, redraw_output)

    stdin_reader = await create_stream_reader()
    sys.stdout.write("Введите имя пользователя: ")
    sys.stdout.flush()
    name = await read_line(stdin_reader)
    server_reader, server_writer = await asyncio.open_connection(server_host,
                                                                 server_port)
    server_writer.write(f"NAME:{name}\n".encode())
    await server_writer.drain()

    listining = asyncio.create_task(server_listening(server_reader, messages))
    read_and_send = asyncio.create_task(
        read_from_client_and_send_to_server(server_writer, stdin_reader))

    try:
        await asyncio.wait([listining, read_and_send],
                           return_when="FIRST_COMPLETED")
    except Exception as e:
        logging.exception(e)
        server_writer.close()
        await server_writer.wait_closed()

asyncio.run(main())
