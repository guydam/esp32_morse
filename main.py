import math
import random

import time
import _thread

from machine import Pin, SoftI2C, RTC, PWM
import ssd1306
from time import sleep_ms

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=4000000)
display = ssd1306.SSD1306_I2C(128, 64, i2c)  # display object
button = Pin(4, Pin.IN, Pin.PULL_UP)
buzzer_pin = Pin(23, Pin.OUT)
buzzer_pwm = PWM(buzzer_pin)

SCREEN_WIDTH = display.width
SCREEN_HEIGHT = display.height
REFRESH_RATE_MS = 33

SHORT_CLICK_THR_MS = 260
SPACE_THR_MS_EASY = 600
SPACE_THR_MS_HARD = 450
SEQUENCE_END_THR_MS_EASY = 1450
SEQUENCE_END_THR_MS_HARD = 1150

MENU_CLICK_SHORT_THR_MS = 400
MENU_CLICK_LONG_THR_MS = 500
MAIN_MENU_TEXT_PAD = 15

MENU_ITEM_EASY = "Easy"
MENU_ITEM_HARD = "Hard"
MENU_ITEM_HOW_TO = "How To"
MENU_ITEM_MAX_WIDTH = 40
MENU_ITEM_MAX_HEIGHT = 10

CODE_PIXEL_BLOCK_SIZE = 4

SOUND_TEXT_ON = "on"
SOUND_TEXT_OFF = "off"
POSITIVE_WORDS = ["awesome", "great", "nice", "correct", "good", "amazing"]
NEGATIVE_WORDS = ["wrong", "nope", "incorrect"]
TIMES_UP_TEXT = "Time Is Up!"

SHORT_SYMBOL = '.'
LONG_SYMBOL = '-'
SPACE_SYMBOL = ' '

GAME_TIMER_S = 30
EASY_POINTS_MODIFY = 3
HARD_POINTS_MODIFY = 5

GAME_OVER_SPLASH_SCREEN_DISPLAY_MS = 3000
ANIMATION_SPEED = 2
SIGNAL_ANIMATION_MAX_RADIUS = 20
HIGH_SCORE_FILE_NAME = 'morse_hs.txt'

BUZZ_MENU_SHORT_CLICK_FREQ_HZ = 1220

BUZZ_SHORT_CLICK_FREQ_HZ = 440
BUZZ_SHORT_CLICK_DUR_MS = 65

BUZZ_LONG_CLICK_FREQ_HZ = 440
BUZZ_LONG_CLICK_DUR_MS = 250

BUZZ_DEFAULT_DUTY = 512


def buzz(duration_ms, frequency, volume=BUZZ_DEFAULT_DUTY):
    buzzer_pwm.freq(frequency)
    buzzer_pwm.duty(volume)
    sleep_ms(duration_ms)
    buzzer_pwm.duty(0)


def buzz_thread(duration_ms, frequency, volume=BUZZ_DEFAULT_DUTY):
    _thread.start_new_thread(buzz, (duration_ms, frequency, volume))


def buzz_success():
    # buzz(150, round(261.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # C4 (softer, shorter)
    # sleep_ms(50)  # Longer pause for a more drawn-out feel
    # buzz(100, round(293.66 * 2 ** ((4 - 4) / 12)), volume=int(0.7*BUZZ_DEFAULT_DUTY))  # D4 (slightly louder, shorter)
    # sleep_ms(100)  # Longer pause for a more drawn-out feel
    # buzz(200, round(329.63 * 2 ** ((4 - 4) / 12)), volume=int(0.8*BUZZ_DEFAULT_DUTY))  # E4 (louder, shortest)

     # buzz(100, round(261.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # C4 (shorter, softer)
    # buzz(75, round(329.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # E4 (even shorter, slightly louder)
    # # Emphasize the final note with a longer duration and increased volume
    # buzz(150, round(392.00 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # G4 (longer, loudest)
    # # Add a short, higher grace note for an extra touch of joy
    # buzz(50, round(440.00 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # A4 (shortest, softer)

    # Upward arpeggio with a triumphant feel (C4 - E4 - G4 - C5)
    # Start with a short, lower note for anticipation
    buzz(100, round(261.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # C4 (shorter, softer)
    # Rising notes with increasing volume and duration for a sense of accomplishment
    buzz(125, round(329.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # E4 (slightly longer, louder)
    buzz(150, round(392.00 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # G4 (longer, even louder)
    buzz(200, round(523.25 * 2 ** ((4 - 4) / 12)), volume=int(0.4*BUZZ_DEFAULT_DUTY))  # C5 (longest, loudest)


def buzz_failure():

    # buzz(200, round(329.63 * 2 ** ((4 - 4) / 12)))  # E4 (longer)
    # buzz(100, round(261.63 * 2 ** ((4 - 4) / 12)))  # C4 (short)
    # buzz(300, round(220.00 * 2 ** ((3 - 4) / 12)))  # A3 (longest)

    buzz(200, round(277.18 * 2 ** ((4 - 4) / 12)), volume=int(0.6*BUZZ_DEFAULT_DUTY))  # C#4 (softer, longer)
    sleep_ms(50)  # Longer pause for a more drawn-out feel
    buzz(150, round(261.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # C4 (softer, shorter)
    sleep_ms(100)  # Even longer pause for emphasis
    buzz(250, round(246.94 * 2 ** ((3 - 4) / 12)), volume=int(0.7*BUZZ_DEFAULT_DUTY))  # B3 (slightly louder, longer)


def buzz_game_over():
    buzz(300, round(392.00 * 2 ** ((4 - 4) / 12)), volume=int(0.6*BUZZ_DEFAULT_DUTY))  # G4 (longer, slightly loud)
    buzz(200, round(329.63 * 2 ** ((4 - 4) / 12)), volume=int(0.5*BUZZ_DEFAULT_DUTY))  # E4 (medium duration, softer)
    buzz(500, round(261.63 * 2 ** ((4 - 4) / 12)), volume=int(0.4*BUZZ_DEFAULT_DUTY))  # C4 (longest, softest)


class GameEngine:
    letters_dict = {
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
    }
    #TODO add tons of words here
    easy_words = ["zap", "zip", "PTK", "jog", "CPU", "JER", "guy", "wax", "fox", "joe", "seq", "jay", "jig",
                  "job", "fab", "bow", "tax", "use", "IDC", "man", "reg", "eps", "csr", "bug", "dev", "val",
                  "ant", "bat", "bed", "can", "cup", "day", "dog", "eat", "eye", "fly",
                  "fox", "god", "hat", "hip", "hit", "hue", "ink", "jar", "key", "law",
                  "lie", "man", "mix", "mud", "nap", "nut", "oil", "old", "owe", "own",
                  "pie", "pig", "pin", "pot", "put", "red", "saw", "sea", "set",
                  "sew", "she", "sit", "six", "sky", "son", "sun", "tie", "tin", "use",
                  "ace", "ago", "aid", "air", "all", "and", "arc", "arm", "art", "ask",
                  "axe", "bad", "bay", "big", "bin", "bit", "box", "boy", "bus", "buy",
                  "cab", "cap", "car", "cat", "cry", "cub", "cut", "dad", "dam", "day",
                  "den", "did", "dig", "doe", "dug", "ear", "eat", "elf", "end", "eve",
                  "eye", "far", "fat", "few", "fix", "fly", "foe", "fog", "for", "fun"
                  ]
    hard_words = ["hello", "intel", "collect", "world", "forward", "option", "songs", "other", "system", "wifi",
                  "point", "resume", "both", "support", "blue", "badge", "make", "menu", "morse", "game", "about",
                  "after", "again", "basic", "better", "could", "every", "first", "found", "great", "human", "known",
                  "large", "learn", "never", "plant", "power", "quite", "ready", "really", "seems", "small", "sound",
                  "space", "speak", "still", "study", "terms", "their", "think", "those", "three", "tools", "quite",
                  "which", "whole", "world", "young", "yours", "cause", "color", "doubt", "early", "enjoy", "exist",
                  "force", "found", "fresh", "glass", "grant", "happy", "heard", "horse", "house", "human", "humor",
                  "image", "issue", "learn", "lunch", "maybe", "merry", "night", "noise", "offer", "often", "paint",
                  "peace", "place", "plant", "power", "price", "quite", "ready", "teach", "thank", "think", "those",
                  "touch", "train", "value", "visit", "watch", "white", "whole", "woman", "world", "young", "cause",
                  "color", "doubt", "early", "enjoy", "exist", "force", "found", "fresh", "glass", "grant", "happy",
                  "heard", "horse", "house", "humor"]
    wrong_code = False
    code_complete = False
    timer_expired = False
    word = ""
    code = []
    points = 0
    difficulty = MENU_ITEM_EASY

    captured_sequence = []
    cur_char_idx = 0

    def __init__(self, difficulty):
        self.wrong_code = False
        self.code_complete = False
        self.timer_expired = False
        self.points = 0
        self.captured_sequence = []
        self.cur_char_idx = 0
        self.difficulty = difficulty

    def gen_new_word(self):

        if self.difficulty == MENU_ITEM_EASY:
            self.word = random.choice(self.easy_words)
        else:
            self.word = random.choice(self.hard_words)

        self.code = self.translate_to_morse(self.word)
        self.wrong_code = False
        self.code_complete = False
        self.timer_expired = False
        self.captured_sequence = []
        self.cur_char_idx = 0

    def translate_to_morse(self, word):
        code = []
        for c in word:
            code.append(self.letters_dict.get(c.upper()))
            code.append(SPACE_SYMBOL)

        return "".join(str(x) for x in code)

    def calculate_code_pixel_count(self, captured):
        x = 0
        if captured:
            code = self.captured_sequence
        else:
            code = self.code
        for c in code:
            if c == SHORT_SYMBOL:
                x += CODE_PIXEL_BLOCK_SIZE + 1
            elif c == LONG_SYMBOL:
                x += 2*CODE_PIXEL_BLOCK_SIZE + 1
            elif c == SPACE_SYMBOL:
                x += CODE_PIXEL_BLOCK_SIZE

        return x

    def is_code_input_started(self):
        if len(self.captured_sequence) > 0:
            return True
        return False

    def is_last_symbol_space(self):
        if len(self.captured_sequence) == 0:
            return False

        if self.captured_sequence[-1] == SPACE_SYMBOL:
            return True

        return False

    def register_code_input(self, symbol):
        self.captured_sequence.append(symbol)
        print(self.captured_sequence)

        if self.code[self.cur_char_idx] == symbol:
            self.cur_char_idx += 1

            if self.difficulty == MENU_ITEM_EASY:
                self.points += 1
            else:
                self.points += 2
            if self.cur_char_idx == len(self.code) - 1:
                self.code_complete = True

        else:
            print('wrong code')
            self.wrong_code = True

    def register_input_timeout(self):
        if self.is_code_input_started():
            print('time out - wrong code')
            # self.cur_char_idx = 0
            # self.captured_sequence = []
            self.wrong_code = True

    def add_points_upon_code_complete(self):
        if self.difficulty is MENU_ITEM_EASY:
            self.points += EASY_POINTS_MODIFY
        else:
            self.points += HARD_POINTS_MODIFY

    def reduce_points_upon_wrong_code(self):
        if self.difficulty is MENU_ITEM_EASY:
            self.points -= EASY_POINTS_MODIFY
        else:
            self.points -= HARD_POINTS_MODIFY

        if self.points < 0:
            self.points = 0

    def is_code_completed(self):
        return self.code_complete

    def is_code_wrong(self):
        return self.wrong_code

    def register_expired_timer(self):
        self.timer_expired = True

    def is_game_over(self):
        return self.timer_expired


def main_menu_loop():
    game_sound = False
    items = [MENU_ITEM_EASY, MENU_ITEM_HARD]
    selector_index = 0
    menu_selection_fill_width = 0

    start_click = False
    start_click_tick = 0
    high_score = load_high_score_from_file(HIGH_SCORE_FILE_NAME)

    buzz_thread(1, BUZZ_MENU_SHORT_CLICK_FREQ_HZ)

    while True:
        selected_item_width = len(items[selector_index]) * 8

        if menu_selection_fill_width > selected_item_width:
            menu_selection_fill_width = 0
            print(items[selector_index] + ' selected')

            if items[selector_index] in (MENU_ITEM_EASY, MENU_ITEM_HARD):
                main_game_loop(items[selector_index], high_score, game_sound)
                # we fall back here once the game has ended - just init some stuff
                start_click = False
                start_click_tick = 0
                high_score = load_high_score_from_file(HIGH_SCORE_FILE_NAME)
                global line_length
                line_length = 0

        draw_main_menu(int(SCREEN_WIDTH / 2 - 15), 35, items, selector_index, menu_selection_fill_width, high_score,
                       game_sound)

        sleep_ms(REFRESH_RATE_MS)

        # now, we handle button inputs
        if button.value() == 0:
            # check if the button is clicked from previous tick
            if start_click:
                # calculate for how long it was clicked to mark selection in the ui
                delta = time.ticks_diff(time.ticks_ms(), start_click_tick)
                if delta > SHORT_CLICK_THR_MS:
                    menu_selection_fill_width += (selected_item_width / (MENU_CLICK_LONG_THR_MS / REFRESH_RATE_MS)) * 2

            # check if button was actually pressed on this tick
            if not start_click:
                start_click_tick = time.ticks_ms()
                start_click = True
        else:
            # check if button was released on this tick and calculate duration
            if start_click:
                delta = time.ticks_diff(time.ticks_ms(), start_click_tick)
                if delta <= SHORT_CLICK_THR_MS:
                    selector_index += 1
                    if selector_index > len(items) - 1:
                        selector_index = 0
                    if game_sound:
                        buzz_thread(BUZZ_SHORT_CLICK_DUR_MS, BUZZ_MENU_SHORT_CLICK_FREQ_HZ)

                start_click = False
                menu_selection_fill_width = 0


def draw_main_menu(x_pos, y_pos, items, selector_index, menu_selection_fill_width, high_score, sound_on):
    display.fill(0)
    draw_frame()

    y = y_pos
    for item in items:
        display.text(item, x_pos, y, 1)
        y += MAIN_MENU_TEXT_PAD

    draw_menu_selector(x_pos, y_pos, selector_index)
    draw_selector_fill_bar(x_pos, y_pos, selector_index, menu_selection_fill_width, sound_on)
    draw_signal_tower()
    draw_highscore(high_score)
    draw_menu_title()
    # draw_sound_icon(SCREEN_WIDTH - 16, 4, 12, sound_on)
    display.show()


def draw_sound_icon(x_pos, y_pos, size, sound_on):
    # sound_on = False
    y_div = int(size / 3)
    x_div = int(size / 2)
    x_offset = int(size / 6) + 1

    if sound_on:
        display.fill_rect(x_pos + x_offset, y_pos + y_div, x_div, y_div, 1)

        for i in range(y_div-1):
            display.line(x_pos + x_div + i, y_pos + y_div - i, x_pos + x_div + i, y_pos + 2*y_div + i, 1)
    else:
        display.line(x_pos + x_offset, y_pos + y_div, x_pos + x_offset + x_div, y_pos + y_div, 1)
        display.line(x_pos + x_offset, y_pos + y_div, x_pos + x_offset, y_pos + 2*y_div, 1)
        display.line(x_pos + x_div, y_pos + y_div, x_pos + x_div, y_pos + 2*y_div, 1)
        display.line(x_pos + x_offset, y_pos + 2*y_div, x_pos + x_offset + x_div, y_pos + 2*y_div, 1)

        display.line(x_pos + x_div, y_pos + y_div, x_pos + 2*x_div, y_pos, 1)
        display.line(x_pos + 2*x_div, y_pos, x_pos + 2*x_div, y_pos + 3*y_div, 1)
        display.line(x_pos + x_div, y_pos + 2*y_div, x_pos + 2 * x_div, y_pos + 3*y_div, 1)

line_length = 0
def draw_menu_title():
    display.text("MORSE", 20, 8, 1)
    display.text("ATTACK", 45, 19, 1)

    global line_length
    display.line(55, 17, 55 + line_length, 17, 1)
    display.line(55, 17, 55 - line_length, 17, 1)

    if line_length < 35:
        line_length += 1


signal_radius = 1
def draw_signal_tower():
    base_left = SCREEN_WIDTH - 30
    base_right = SCREEN_WIDTH - 10
    height = SCREEN_HEIGHT - 30

    display.line(base_left, SCREEN_HEIGHT, SCREEN_WIDTH - (base_right - base_left), SCREEN_HEIGHT - height, 1)
    display.line(base_right, SCREEN_HEIGHT, SCREEN_WIDTH - (base_right - base_left), SCREEN_HEIGHT - height, 1)

    display.fill_rect(SCREEN_WIDTH - (base_right - base_left) - 1, SCREEN_HEIGHT - height - 3, 3, 3, 1)

    display.line(base_left + 2, SCREEN_HEIGHT - 8, base_right - 6, height + 8, 1)
    display.line(base_right - 2, SCREEN_HEIGHT - 8, base_left + 6, height + 8, 1)

    global signal_radius
    draw_circle(SCREEN_WIDTH - (base_right - base_left), height - 5, signal_radius)
    signal_radius += ANIMATION_SPEED
    if signal_radius > SIGNAL_ANIMATION_MAX_RADIUS - random.randrange(0, 10):
        signal_radius = 1


def draw_circle(center_x, center_y, radius):

    num_segments = 40

    for i in range(num_segments):
        angle = 2 * math.pi * (i / num_segments) if i < num_segments - 1 else 2 * math.pi
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        if i > 0:
            display.line(int(prev_x), int(prev_y), int(x), int(y), 1)

        prev_x, prev_y = x, y


def draw_highscore(high_score):
    display.text(str(high_score), 8, SCREEN_HEIGHT - 8 - 8, 1)


def draw_menu_selector(x_pos, y_pos, selector_index):
    x = x_pos - 10
    y = y_pos + 1 + selector_index * MAIN_MENU_TEXT_PAD

    display.line(x, y, x + 4, y + 2, 1)
    display.line(x, y, x, y + 4, 1)
    display.line(x, y + 4, x + 4, y + 2, 1)


def draw_selector_fill_bar(x_pos, y_pos, selector_index, fill_width, sound_on):
    x = x_pos
    y = y_pos + selector_index * MAIN_MENU_TEXT_PAD - 3
    fill = int(fill_width)
    if fill == 0:
        return
    if sound_on:
        buzz_thread(int(REFRESH_RATE_MS/2), fill * 200)
    display.line(x, y, x + fill, y, 1)
    display.line(x, y + MENU_ITEM_MAX_HEIGHT + 3, x + fill, y + MENU_ITEM_MAX_HEIGHT + 3, 1)


def draw_selector_fill_bar3(x_pos, y_pos, selector_index, fill_width):
    x = x_pos - 2
    y = y_pos + selector_index * MAIN_MENU_TEXT_PAD - 2
    fill = int(fill_width)
    if fill == 0:
        return

    print(fill)

    if fill < MENU_ITEM_MAX_WIDTH:
        display.line(x, y, x + fill, y, 1)
    elif fill < (MENU_ITEM_MAX_WIDTH + MENU_ITEM_MAX_HEIGHT):
        display.line(x, y, x + MENU_ITEM_MAX_WIDTH, y, 1)
        display.line(x + MENU_ITEM_MAX_WIDTH, y, x + MENU_ITEM_MAX_WIDTH, y + fill, 1)
    elif fill < (2 * MENU_ITEM_MAX_WIDTH + MENU_ITEM_MAX_HEIGHT):
        display.line(x, y, x + MENU_ITEM_MAX_WIDTH, y, 1)
        display.line(x + MENU_ITEM_MAX_WIDTH, y, x + MENU_ITEM_MAX_WIDTH, y + MENU_ITEM_MAX_HEIGHT, 1)
        display.line(x + MENU_ITEM_MAX_WIDTH, y + MENU_ITEM_MAX_HEIGHT, x + MENU_ITEM_MAX_WIDTH - fill,
                     y + MENU_ITEM_MAX_HEIGHT, 1)
    elif fill < (2 * MENU_ITEM_MAX_WIDTH + 2 * MENU_ITEM_MAX_HEIGHT):
        display.line(x, y, x + MENU_ITEM_MAX_WIDTH, y, 1)
        display.line(x + MENU_ITEM_MAX_WIDTH, y, x + MENU_ITEM_MAX_WIDTH, y + MENU_ITEM_MAX_HEIGHT, 1)
        display.line(x + MENU_ITEM_MAX_WIDTH, y + MENU_ITEM_MAX_HEIGHT, x, y + MENU_ITEM_MAX_HEIGHT, 1)
        display.line(x, y + MENU_ITEM_MAX_HEIGHT, x, y + MENU_ITEM_MAX_HEIGHT - fill, 1)


def draw_selector_fill_bar2(x_pos, y_pos, selector_index, fill_width):
    # y = y_pos + selector_index * MAIN_MENU_TEXT_PAD - 1
    # display.rect(x_pos, y, MENU_PROGRESS_BAR_WIDTH, 5, 1)
    # display.fill_rect(x_pos, y, int(fill_width), MAIN_MENU_TEXT_PAD, 1)
    fill_width = int(fill_width)
    if fill_width < SCREEN_WIDTH:
        display.hline(0, 0, fill_width, 1)
    elif fill_width < (SCREEN_WIDTH + SCREEN_HEIGHT):
        fill_width -= SCREEN_WIDTH - 1
        display.hline(0, 0, SCREEN_WIDTH - 1, 1)
        display.vline(SCREEN_WIDTH - 1, 0, -fill_width, 1)
    elif fill_width < (2 * SCREEN_WIDTH + SCREEN_HEIGHT):
        fill_width -= (SCREEN_WIDTH - 1 + SCREEN_HEIGHT - 1)
        display.hline(0, 0, SCREEN_WIDTH - 1, 1)
        display.vline(SCREEN_WIDTH - 1, 0, -(SCREEN_HEIGHT - 1), 1)
        display.hline(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, -fill_width, 1)
    else:
        fill_width -= (2 * (SCREEN_WIDTH - 1) + SCREEN_HEIGHT - 1)
        display.hline(0, 0, SCREEN_WIDTH - 1, 1)
        display.vline(SCREEN_WIDTH - 1, 0, -(SCREEN_HEIGHT - 1), 1)
        display.hline(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, -(SCREEN_WIDTH - 1), 1)
        display.vline(0, SCREEN_HEIGHT - 1, fill_width, 1)


def main_game_loop(difficulty, high_score, sound_on):
    start_game_tick = time.ticks_ms()
    ge = GameEngine(difficulty)

    space_threshold_ms = SPACE_THR_MS_EASY if difficulty == MENU_ITEM_EASY else SPACE_THR_MS_HARD
    timeout_threshold_ms = SEQUENCE_END_THR_MS_EASY if difficulty == MENU_ITEM_EASY else SEQUENCE_END_THR_MS_HARD

    while True:

        if ge.is_game_over():
            break

        ge.gen_new_word()
        sleep_ms(450)

        code_pixel_width = ge.calculate_code_pixel_count(False)
        code_x_pos = int((SCREEN_WIDTH - code_pixel_width) / 2)
        if code_x_pos < 3:
            print(ge.word + ' code is too long!! regen...')
            continue

        start_click = False
        start_click_tick = 0
        end_click_tick = 0

        while True:

            elapsed_sec = int(time.ticks_diff(time.ticks_ms(), start_game_tick) / 1000)

            # if time is up - show splash and kill the game
            if elapsed_sec > GAME_TIMER_S:
                ge.register_expired_timer()
                draw_end_game_splash_screen(ge, sound_on)
                if ge.points > high_score:
                    save_high_score_to_file(HIGH_SCORE_FILE_NAME, ge.points)
                break

            # first, we draw the screen
            draw_game_screen(ge, code_x_pos, elapsed_sec)

            # check if we completed the code sequence
            if ge.is_code_completed():
                text = "-" + random.choice(POSITIVE_WORDS) + "-"
                display.text(text, int((SCREEN_WIDTH - len(text) * 8)/2), 20, 1)
                ge.add_points_upon_code_complete()
                # TODO Here we need to highlight the points user got
                sleep_ms(100)
                display.show()
                if sound_on:
                    buzz_success()
                else:
                    sleep_ms(400)
                sleep_ms(300)
                break

            if ge.is_code_wrong():
                text = "-" + random.choice(NEGATIVE_WORDS) + "-"
                display.text(text, int((SCREEN_WIDTH - len(text) * 8)/2), 20, 1)
                ge.reduce_points_upon_wrong_code()
                sleep_ms(100)
                display.show()
                if sound_on:
                    buzz_failure()
                else:
                    sleep_ms(400)
                sleep_ms(300)
                # TODO we need to show points reduction
                break

            # now, we handle button inputs
            if button.value() == 0:
                # check if button was actually pressed on this tick
                if not start_click:
                    start_click_tick = time.ticks_ms()
                    start_click = True
            else:
                # check if button was released on this tick and calculate duration
                if start_click:
                    delta = time.ticks_diff(time.ticks_ms(), start_click_tick)
                    if delta <= SHORT_CLICK_THR_MS:
                        ge.register_code_input(SHORT_SYMBOL)
                        if sound_on:
                            buzz_thread(BUZZ_SHORT_CLICK_DUR_MS, BUZZ_SHORT_CLICK_FREQ_HZ)
                    else:
                        ge.register_code_input(LONG_SYMBOL)
                        if sound_on:
                            buzz_thread(BUZZ_LONG_CLICK_DUR_MS, BUZZ_LONG_CLICK_FREQ_HZ)

                    start_click = False
                    end_click_tick = time.ticks_ms()
                # else, button is still unpressed from last tick
                else:
                    delta = time.ticks_diff(time.ticks_ms(), end_click_tick)
                    if delta > space_threshold_ms:
                        if ge.is_code_input_started() and not ge.is_last_symbol_space():
                            ge.register_code_input(SPACE_SYMBOL)

                    if delta > timeout_threshold_ms:
                        if ge.is_code_input_started():
                            ge.register_input_timeout()

            sleep_ms(REFRESH_RATE_MS)


def draw_game_screen(ge, code_x_pos, elapsed_sec):
    display.fill(0)
    draw_frame()
    draw_points(ge)
    draw_timer(elapsed_sec)
    draw_word(ge, int(SCREEN_HEIGHT / 2) + 2)
    draw_code_pixels(ge, code_x_pos, int(SCREEN_HEIGHT / 2) + 18)
    draw_progress_bar(ge, code_x_pos, int(SCREEN_HEIGHT / 2) + 18)
    display.show()


def draw_end_game_splash_screen(ge, sound_on):
    splash_screen_start_tick = time.ticks_ms()
    delta = 0
    txt_x_pos = int((SCREEN_WIDTH - len(TIMES_UP_TEXT) * 8)/2)
    score_txt = "score {}".format(str(ge.points))
    display.fill(0)
    draw_frame()
    display.text(TIMES_UP_TEXT, txt_x_pos, 20, 1)
    display.text(score_txt, int((SCREEN_WIDTH - len(score_txt) * 8) / 2), SCREEN_HEIGHT - 20, 1)
    display.show()
    if sound_on:
        buzz_game_over()
    while delta <= GAME_OVER_SPLASH_SCREEN_DISPLAY_MS:
        delta = time.ticks_diff(time.ticks_ms(), splash_screen_start_tick)
        sleep_ms(REFRESH_RATE_MS)


def draw_frame():
    display.line(0, 0, SCREEN_WIDTH - 1, 0, 1)
    display.line(0, 0, 0, SCREEN_HEIGHT - 1, 1)
    display.line(SCREEN_WIDTH - 1, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, 1)
    display.line(0, SCREEN_HEIGHT - 1, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, 1)


def draw_points(ge):
    display.text("P:{}".format(str(ge.points)), 8, 8, 1)


blink_count = int((1/REFRESH_RATE_MS) * 1000)


def draw_timer(elapsed_sec):
    global blink_count
    time_left = GAME_TIMER_S - elapsed_sec
    if time_left < 0:
        time_left = 0

    if time_left > 5:
        display.text("T:{}".format(str(time_left)), SCREEN_WIDTH - 40, 8, 1)
    else:
        display.fill_rect(SCREEN_WIDTH - 41, 7, 33, 9, 1)
        display.text("T:{}".format(str(time_left)), SCREEN_WIDTH - 40, 8, 0)


def draw_word(ge, y_pos):
    x_pos = int((SCREEN_WIDTH - len(ge.word) * 8) / 2)
    display.text(ge.word, x_pos, y_pos, 1)


def draw_code_pixels(ge, x, y):
    for c in ge.code:
        if c == SHORT_SYMBOL:
            display.fill_rect(x, y, CODE_PIXEL_BLOCK_SIZE, CODE_PIXEL_BLOCK_SIZE, 1)
            x += CODE_PIXEL_BLOCK_SIZE + 1
        elif c == LONG_SYMBOL:
            display.fill_rect(x, y, 2 * CODE_PIXEL_BLOCK_SIZE, CODE_PIXEL_BLOCK_SIZE, 1)
            x += 2*CODE_PIXEL_BLOCK_SIZE + 1
        elif c == SPACE_SYMBOL:
            x += CODE_PIXEL_BLOCK_SIZE


def draw_progress_bar(ge, x, y):
    fill_width = ge.calculate_code_pixel_count(True) - 1
    display.line(x, y - 3, x + fill_width, y - 3, 1)
    display.line(x, y + CODE_PIXEL_BLOCK_SIZE + 2, x + fill_width, y + CODE_PIXEL_BLOCK_SIZE + 2, 1)


def load_high_score_from_file(filename):

    try:
        f = open(filename, 'r')
        hs = int(f.read())
        f.close()
        return hs
    except OSError:
        save_high_score_to_file(filename, 64)
        return 64


def save_high_score_to_file(filename, score):
    f = open(filename, 'w')
    f.write(str(score))
    f.close()


main_menu_loop()
