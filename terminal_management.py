import sys
import shutil


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
