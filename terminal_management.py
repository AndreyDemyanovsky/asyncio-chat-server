import asyncio
import sys
import shutil
from asyncio import StreamReader
from typing import Deque
from collections import deque


def delete_line():
    sys.stdout.write("\033[2K")


def clean_line():
    sys.stdout.write("\033[2kG0")


def move_back_one_char():
    sys.stdout.write('\033[1D')


def save_cursor_position(): 
    sys.stdout.write('\0337')


def restore_cursor_position():
    sys.stdout.write('\0338')


def move_to_top_of_screen():
    sys.stdout.write("\033[1;1H")


def move_to_down_of_screen() -> int:
    _, total_rows = shutil.get_terminal_size()
    total_rows -= 1
    sys.stdout.write(f"\033[{total_rows}E")
    return total_rows


async def read_line(stdin_reade: StreamReader):
    DELETE_SIGN = b"\x7f"
    buffer: Deque = deque()

    while (char := await stdin_reade.read(1)) != b"":

        if char == DELETE_SIGN:
            if len(buffer) > 0:
                move_back_one_char()
                sys.stdout.write(" ")
                move_back_one_char()
                buffer.pop()
        else:
            buffer.append(char)
            sys.stdout.write(char.decode())
            sys.stdout.flush()
