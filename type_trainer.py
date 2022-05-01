import curses
import random
import time
from curses import wrapper


def start_screen(stdscr):
    lines, columns = stdscr.getmaxyx()

    stdscr.erase()

    stdscr.addstr('Welcome to the Speed Printing Trainer!')
    stdscr.addstr(1, 0, 'Choose a training mode (type a number):')
    stdscr.addstr(5, 0, '1. Random text mode')
    stdscr.addstr(lines // 3 + 3, 0, '2. Load from file')
    stdscr.addstr((lines * 2) // 3, 0, '3. Running line mode')

    stdscr.refresh()
    
    num = type_the_word(stdscr)
    if num == '1':
        random_text_mode(stdscr)
    elif num == '2':
        loaded_from_file_mode(stdscr)
    elif num == '3':
        running_line_mode(stdscr)
    else:
        start_screen(stdscr)


def render_text_and_info(stdscr, target, current, spm, mistakes, time_elapsed):
    stdscr.addstr(target)

    x, y = 0, 0
    for i, char in enumerate(current):
        color = curses.color_pair(1)
        if char != target[i]:
            color = curses.color_pair(2)
        if char == '\n':
            y += 1
            x = 0
            continue
        stdscr.addstr(y, x, char, color)
        x += 1

    render_info(stdscr, spm, mistakes, time_elapsed)


def render_info(stdscr, spm, mistakes, time_elapsed):
    lines, columns = stdscr.getmaxyx()
    stdscr.addstr(11, columns // 2 + 1, 'Info about typing')
    stdscr.addstr(12, columns // 2 + 1, f'- symbols per minute: {spm}')
    if mistakes >= 0:
        stdscr.addstr(13, columns // 2 + 1, f'- mistakes: {mistakes}')
    stdscr.addstr(14, columns // 2 + 1, f'- time elapsed: {time_elapsed}')


def run(stdscr, target_text):
    current_text = []
    spm, mistakes = 0, 0
    start_time = time.time()
    stdscr.nodelay(True)

    while True:
        time_elapsed = max(1, time.time() - start_time)
        spm = round(60 * len(current_text) / time_elapsed)

        stdscr.erase()
        render_text_and_info(stdscr,
                             target_text,
                             current_text,
                             spm,
                             mistakes,
                             round(time.time() - start_time, 2)
                            )
        stdscr.refresh()

        if ''.join(current_text) == target_text:
            stdscr.nodelay(False)
            break

        try:
            key = stdscr.getkey()
        except:
            continue

        if key == curses.KEY_ENTER:
            key = '\n'

        if len(key) == 1 and ord(key) == 27:
            stdscr.nodelay(False)
            break

        if key in ('KEY_BACKSPACE', '\b', '\x7f'):
            if len(current_text) > 0:
                current_text.pop()
        else:
            if target_text[len(current_text)] != key:
                mistakes += 1
            current_text.append(key)


def run_line(stdscr, target_text, difficulty=0):
    stdscr.erase()

    last_shift = time.time()
    start_time = time.time()

    term_len = stdscr.getmaxyx()[1]
    text_len = len(target_text)
    target_text = ' ' * (term_len - 1) + target_text
    lborder = 0
    symbs = 0
    cursor = term_len - 1
    stdscr.nodelay(True)
    curses.curs_set(0)
    
    while True:
        shift_factor = time.time() - last_shift
        elapsed = time.time() - start_time
        spm = round(60 * symbs / elapsed)
        
        if shift_factor > (0.15 - difficulty * 0.1):
            cursor = max(0, cursor - 1)
            lborder += 1
            last_shift = time.time()
        
        if cursor == 0:
            stdscr.addstr(10, 0, 'You loose! Press any key')
            stdscr.nodelay(False)
            stdscr.getkey()
            break

        stdscr.erase()

        render_with_green_border(stdscr,
                                 target_text[lborder:min(lborder + term_len, text_len)],
                                 cursor,
                                 spm,
                                 round(elapsed, 2)
                                )
        stdscr.refresh()
        
        try:
            key = stdscr.getkey()
        except:
            continue
        
        if len(key) == 1 and ord(key) == 27:
            stdscr.nodelay(False)
            break
        
        if len(key) == 1 and key == target_text[lborder+cursor]:
            symbs += 1
            cursor += 1
            
    curses.curs_set(1)


def render_with_green_border(stdscr, text, index, spm, elapsed):
    for i, char in enumerate(text):
        if i < index:
            stdscr.addstr(4, i, char, curses.color_pair(1))
        else:
            stdscr.addstr(4, i, char)
    render_info(stdscr, spm, -1, elapsed)


def running_line_mode(stdscr):
    f = open('./sources/long_text')
    text = ' '.join([line[:-1] for line in f.readlines()])
    stdscr.erase()
    stdscr.addstr(11, 0, 'Choose difficulty:\n\neasy = 1\n\nmedium = 2\n\nhard = 3')
    difficulty = int(type_the_word(stdscr))
    run_line(stdscr, text, min(difficulty - 2, 1))


def random_text_mode(stdscr):
    text_len = random.randint(40, 80)
    text = ''
    for i in range(text_len):
        text += chr(random.randint(33, 125))
    run(stdscr, text)


def loaded_from_file_mode(stdscr):
    num = random.randint(0, 9)
    f = open(f'./sources/text_{num}')
    text = f.read()
    run(stdscr, text)


def type_the_word(stdscr) -> str:
    result = ':'
    stdscr.move(stdscr.getmaxyx()[0] - 1, 0)
    while True:
        key = stdscr.getkey()
        if len(key) == 1 and (ord(key) == 27 or ord(key) == 10):
            break
        if key in ('KEY_BACKSPACE', '\b', '\x7f'):
            if len(result) > 1:
                result = result[:-1]
                continue
        result += key
        stdscr.addstr(
            stdscr.getmaxyx()[0] - 1,
            0,
            result
            )
        stdscr.refresh()
    return result[1:]


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    while True:
        start_screen(stdscr)
        stdscr.addstr(10, 0, 'You have finished. Press Esc to leave or another button to repeat')
        key = stdscr.getkey()
        if len(key) == 1 and ord(key) == 27:
            break

wrapper(main)
