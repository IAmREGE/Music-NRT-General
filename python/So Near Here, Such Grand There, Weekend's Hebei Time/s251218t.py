from sys import stderr
from time import monotonic, sleep
import argparse
from fractions import Fraction

try:
    from colorama import Fore, Back, init
    init(autoreset=True)
    del init
except ImportError:
    class Fore:
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        RESET = "\033[39m"

    class Back:
        BLACK = "\033[40m"
        RED = "\033[41m"
        GREEN = "\033[42m"
        YELLOW = "\033[43m"
        BLUE = "\033[44m"
        MAGENTA = "\033[45m"
        CYAN = "\033[46m"
        WHITE = "\033[47m"
        RESET = "\033[49m"


FORE_COLOR_MAP = (Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
                  Fore.MAGENTA, Fore.CYAN, Fore.WHITE, "", Fore.RESET)
BACK_COLOR_MAP = (Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE,
                  Back.MAGENTA, Back.CYAN, Back.WHITE, "", Back.RESET)


class FrameUnit:
    def __init__(self, char=" ", fore=9, back=9):
        self.char = char
        self.fore = fore
        self.back = back

    def copy(self):
        return type(self)(self.char, self.fore, self.back)


class Frame:
    WIDTH = 79
    HEIGHT = 24

    def __init__(self):
        self.units = [[FrameUnit() for _ in range(self.WIDTH)]
                      for _ in range(self.HEIGHT)]

    def fill_units(self, text, x=0, y=0, fore=None, back=None):
        if y >= self.HEIGHT:
            return None
        head_x = x
        for char in text:
            if char == "\n":
                y += 1
                if y >= self.HEIGHT:
                    return None
                x = head_x
            elif char == "\r":
                x = 0
            elif char == "\b":
                if x > 0:
                    x -= 1
            elif x < self.WIDTH:
                unit = self.units[y][x]
                unit.char = char
                if fore is not None:
                    unit.fore = fore
                if back is not None:
                    unit.back = back
                x += 1

    def fill_style(self, text, mapper, x=0, y=0):
        if y >= self.HEIGHT:
            return None
        head_x = x
        for char in text:
            if char == "\n":
                y += 1
                if y >= self.HEIGHT:
                    return None
                x = head_x
            elif char == "\r":
                x = 0
            elif char == "\b":
                if x > 0:
                    x -= 1
            elif x < self.WIDTH:
                if char in mapper:
                    unit = self.units[y][x]
                    style = mapper[char]
                    if style[0] is not None:
                        unit.fore = style[0]
                    if style[1] is not None:
                        unit.back = style[1]
                x += 1

    def get_string(self):
        last_fore = last_back = None
        prelis = []
        for line in self.units:
            if prelis:
                prelis.append("\r\n")
            for unit in line:
                if unit.fore != last_fore:
                    last_fore = unit.fore
                    prelis.append(FORE_COLOR_MAP[last_fore])
                if unit.back != last_back:
                    last_back = unit.back
                    prelis.append(BACK_COLOR_MAP[last_back])
                prelis.append(unit.char)
        return "".join(prelis)

    def copy(self):
        copied = type(self)()
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                copied.units[y][x] = self.units[y][x].copy()
        return copied


FPS = Fraction(6)

FRAME_STRS = []

FRAME_BASE = Frame()
FRAME_BASE.fill_style(("B"*Frame.WIDTH+"\n")*Frame.HEIGHT, {"B": (None, 6)})


def add_animating_line(frame_strs, frame: Frame, x=None, y=None, color=9,
                       append_function=None):
    f1 = frame.copy()
    if x is not None:
        f1.fill_style("W\n"*(Frame.HEIGHT//2), {"W": (None, color)}, x, 0)
    if y is not None:
        f1.fill_style("W"*(Frame.WIDTH//2), {"W": (None, color)}, 0, y)
    frame_strs.append(f1.get_string()) if append_function is None else \
    append_function(frame_strs, f1)
    if x is not None:
        f1.fill_style("W\n"*(Frame.HEIGHT-Frame.HEIGHT//2),
                      {"W": (None, color)}, x, Frame.HEIGHT//2)
    if y is not None:
        f1.fill_style("W"*(Frame.WIDTH-Frame.WIDTH//2),
                      {"W": (None, color)}, Frame.WIDTH//2, y)
    frame_strs.append(f1.get_string()) if append_function is None else \
    append_function(frame_strs, f1)
    f1 = frame.copy()
    if x is not None:
        f1.fill_style("W\n"*(Frame.HEIGHT-Frame.HEIGHT//2),
                      {"W": (None, color)}, x, Frame.HEIGHT//2)
    if y is not None:
        f1.fill_style("W"*(Frame.WIDTH-Frame.WIDTH//2),
                      {"W": (None, color)}, Frame.WIDTH//2, y)
    frame_strs.append(f1.get_string()) if append_function is None else \
    append_function(frame_strs, f1)


def add_popup_text(frame_strs, frame: Frame, text, total_frame_count, x=0, y=0,
                   fore=None, back=None, reserved=True, append_function=None):
    f1 = frame if reserved else frame.copy()
    a = Fraction()
    b = Fraction(len(text), total_frame_count)
    for _ in range(total_frame_count):
        a += b
        f1.fill_units(text[:round(a)+1], x, y, fore, back)
        frame_strs.append(f1.get_string()) if append_function is None else \
        append_function(frame_strs, f1)

def add_drop_text(frame_strs, frame: Frame, text, total_frame_count, x=0, y=0,
                  fore=None, back=None, reserved=True, append_function=None):
    f1 = frame if reserved else frame.copy()
    a = Fraction()
    b = Fraction(len(text), total_frame_count)
    for _ in range(total_frame_count):
        a += b
        f1.fill_units(text[round(a)+1:round(a+b)+1].rjust(
            min(round(a+b)+1, len(text))
        ), x, y-1, fore, back)
        f1.fill_units(text[:round(a)+1], x, y, fore, back)
        frame_strs.append(f1.get_string()) if append_function is None else \
        append_function(frame_strs, f1)

FRAME_INTRO = FRAME_BASE.copy()
FRAME_INTRO.fill_units("TITLE: So Near Here, Such Grand There, Weekend's Hebei"
                       " Time", 2, 21, 3)
FRAME_INTRO.fill_units("VOCAL: ", 29, 22, 1)
FRAME_INTRO.fill_units("LYRICS: REGE", 49, 22, 2)
FRAME_INTRO.fill_units("PV: REGE", 63, 21, 7)
beat = 1
beat_next = False

def add_frame_with_beat(frame_strs, frame: Frame, color=7):
    global beat, beat_next
    frame.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 72, 22, color
    )
    frame_strs.append(frame.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

# PT 1
FRAME_PT1_BASE = FRAME_INTRO.copy()
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE)
FRAME_PT1_BASE.fill_units("[SHOWCASE]", Frame.WIDTH//2-5, 11, 5)
for _ in range(60):
    add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE)
FRAME_PT1_BASE.fill_units("    ", Frame.WIDTH//2-1, 11, 5)
add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE)
FRAME_PT1_BASE.fill_units("        ", Frame.WIDTH//2-4, 11, 5)
add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE) # BAR 8

add_popup_text(FRAME_STRS, FRAME_PT1_BASE, "[The 11-character", 8, 12, 4, 7,
               append_function=add_frame_with_beat) # BAR 9
add_popup_text(FRAME_STRS, FRAME_PT1_BASE, "SLO G  A  N   ]", 8, 16, 5, 7,
               append_function=add_frame_with_beat) # BAR 10
add_popup_text(FRAME_STRS, FRAME_PT1_BASE, "COMPOSER: TeamForNothing", 8, 2,
               22, 5, append_function=add_frame_with_beat) # BAR 11
for _ in range(8):
    add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE) # BAR 12
add_popup_text(FRAME_STRS, FRAME_PT1_BASE, "Kasane Teto", 5, 36, 22, 1,
               append_function=add_frame_with_beat)
FRAME_PT1_BASE.fill_units("(UTAU English)", 34, 23, 1)
for _ in range(3):
    add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE) # BAR 13
FRAME_PT1_BASE.fill_units("              ", 34, 23, 9)
add_popup_text(FRAME_STRS, FRAME_PT1_BASE,
               r"\u4e3b\u8981\u7d20\u6750\u6765\u6e90: TeamForNothing", 8, 15,
               12, 7, append_function=add_frame_with_beat) # BAR 14
add_popup_text(FRAME_STRS, FRAME_PT1_BASE,
               r"\u6b4c\u8bcd\u501f\u9274: TeamForNothing", 8, 15,
               13, 7, append_function=add_frame_with_beat) # BAR 15
for _ in range(6):
    add_frame_with_beat(FRAME_STRS, FRAME_PT1_BASE)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_BASE.copy()) # BAR 16
    
# PT 2
FRAME_PT2_BASE = FRAME_BASE.copy()
FRAME_PT2_BASE.fill_units("Jing", 38, 12, 7)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("Jin ", 38, 12, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("Ji  ", 38, 12, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("    ", 38, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "coordinates", 3, 12, 12, 7,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 17
FRAME_PT2_BASE.fill_units("           ", 12, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Weekend's to go", 3, 10, 10, 7,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "no     hesitate", 3, 10, 12, 7,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 18
FRAME_PT2_BASE.fill_units("               ", 10, 10, 9)
FRAME_PT2_BASE.fill_units("               ", 10, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Just run around in outer space", 6,
              8, 9, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 19
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "for   periods   relay", 5,
              9, 11, 7, append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                     ", 9, 11, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                              ", 8, 9, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 20
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "No matter how tiring and high", 9,
              10, 10, 7, append_function=add_frame_with_beat)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "For the sights Hebei's unmatched",
              7, 10, 12, 1, append_function=add_frame_with_beat) # BAR 22
FRAME_PT2_BASE.fill_units("3", 39, 11, 7)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("2", 39, 11, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("1", 39, 11, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                             ", 10, 10, 9)
FRAME_PT2_BASE.fill_units("                                ", 10, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "everybody's", 3, 34, 11, 5,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 23
FRAME_PT2_BASE.fill_units("           ", 34, 11, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "together today", 4, 33, 11, 1,
               append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 33, 11, 9)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 24
FRAME_PT2_BASE.fill_units("Jing", 38, 12, 7)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("Jin ", 38, 12, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("Ji  ", 38, 12, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("    ", 38, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "pay attention", 3, 12, 12, 7,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 25
FRAME_PT2_BASE.fill_units("             ", 12, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Weekend's to go", 3, 10, 10, 7,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "yes   criterion", 3, 10, 12, 7,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 26
FRAME_PT2_BASE.fill_units("               ", 10, 10, 9)
FRAME_PT2_BASE.fill_units("               ", 10, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Just circle on outdoor freeways", 6,
              8, 9, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 27
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "in         repetition", 5,
              9, 11, 7, append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                     ", 9, 11, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                               ", 8, 9, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 28
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "No matter how tiring and high", 9,
              10, 10, 7, append_function=add_frame_with_beat)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "For nature Hebei's supreme",
              7, 10, 12, 1, append_function=add_frame_with_beat) # BAR 30
FRAME_PT2_BASE.fill_style("""\
....WWWWWWWWWWWW....
..WWWWWWWWWWWWWWWW..
WWWW............WWWW
WWWW............WWWW
WWWW............WWWW
................WWWW
...............WWWWW
.............WWWWWW.
...........WWWWWW...
......WWWWWWWW......
......WWWWWWWW......
...........WWWWWW...
.............WWWWWW.
...............WWWWW
................WWWW
WWWW............WWWW
WWWW............WWWW
WWWW............WWWW
..WWWWWWWWWWWWWWWW..
....WWWWWWWWWWWW....
""", {"W": (None, 7), ".": (None, 6)}, 30, 2)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_style("""\
....WWWWWWWWWWWW....
..WWWWWWWWWWWWWWWW..
WWWW............WWWW
WWWW............WWWW
WWWW............WWWW
................WWWW
...............WWWWW
.............WWWWWW.
...........WWWWWW...
........WWWWWW......
......WWWWWW........
...WWWWWW...........
..WWWWW.............
.WWWWW..............
.WWWW...............
WWWWW...............
WWWW................
WWWW................
WWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWW
""", {"W": (None, 7), ".": (None, 6)}, 30, 2)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_style("""\
........WWWW........
......WWWWWW........
....WWWWWWWW........
..WWWW..WWWW........
WWWW....WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
WWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWW
""", {"W": (None, 7), ".": (None, 6)}, 30, 2)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                             ", 10, 10, 9)
FRAME_PT2_BASE.fill_units("                          ", 10, 12, 9)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "everybody", 3, 35, 11, 5,
              append_function=add_frame_with_beat)
FRAME_PT2_BASE.fill_style("""\
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
""", {".": (None, 6)}, 30, 2)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 31
FRAME_PT2_BASE.fill_units("         ", 35, 11, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "participation", 4, 33, 11, 1,
               append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("             ", 33, 11, 9)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 32
FRAME_PT2_BASE.fill_units("[SHOWCASE]", Frame.WIDTH//2-5, 11, 5)
for _ in range(16):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 34
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, 25, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, 65, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 35
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, 31, 9, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, 57, 18, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 36
for _ in range(16):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 38
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, y=10, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, y=16, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 39
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, 9, 8, color=7,
                   append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_animating_line(FRAME_STRS, FRAME_PT2_BASE, 39, 12, color=7,
                   append_function=add_frame_with_beat)
FRAME_PT2_BASE.fill_units("          ", Frame.WIDTH//2-5, 11, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 40

def beat_line_alternate(frame_strs, frame: Frame):
    frame.fill_style("."*Frame.WIDTH,{".": (None, 6 if beat_next else 7)},y=1)
    frame.fill_style("."*Frame.WIDTH,{".": (None, 6 if beat_next else 7)},y=22)
    add_frame_with_beat(frame_strs, frame)

FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 2 times", 25, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                 ", 25, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 42
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Bi Shu Shan Zhuang means to break",
               5, 5, 11, 7, append_function=beat_line_alternate)
for _ in range(2):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                                 ", 5, 11, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 43
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Ba Shang Cao Yuan as if flight",
               5, 39, 13, 7, append_function=beat_line_alternate)
for _ in range(2):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                              ", 39, 13, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 44
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 3 times", 25, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                 ", 25, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 46
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Linking along takes its great",
               5, 5, 11, 7, append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 47
FRAME_PT2_BASE.fill_units("                             ", 5, 11, 9)
FRAME_PT2_BASE.fill_units("Making some dizzy on line", 27, 11, 4)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
for _ in range(6):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
for i in range(28, 52, 2):
    FRAME_PT2_BASE.fill_units(" ", i, 11, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                         ", 27, 11, 9)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 48
FRAME_PT2_BASE.fill_units("__ __ __", 39, 16, 7)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, r"\u4eac \u6d25 \u5180", 3, 6, 10,
               7, 4, append_function=beat_line_alternate)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "never say", 3, 39, 16, 7,
               append_function=beat_line_alternate)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
FRAME_PT2_BASE.fill_units("                    ", 6, 10, 9, 6)
FRAME_PT2_BASE.fill_units("         ", 39, 16, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 49
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, '"I\'m exhausted need to tie"', 5,
               26, 12, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 50
FRAME_PT2_BASE.fill_units("                           ", 26, 12, 9)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 4 times", 23, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                 ", 23, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 52
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Seize the opportunity", 5, 6, 2, 7,
              append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 53
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "USBs all plug in tight", 5, 51, 21,
              7, append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 54
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
FRAME_PT2_BASE.fill_units("                     ", 6, 2, 9)
FRAME_PT2_BASE.fill_units("                      ", 51, 21, 9)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 5 times", 23, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
FRAME_PT2_BASE.fill_units(
    "So near here, such grand there, weekend's Hebei time", 14, 20
)
for _ in range(16):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 56
FRAME_PT2_BASE.fill_units("                                 ", 23, 11, 9)
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
FRAME_PT2_BASE.fill_units("[SHOWCASE]", Frame.WIDTH//2-5, 11, 5)
for _ in range(64):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 64
FRAME_PT2_BASE.fill_units("          ", Frame.WIDTH//2-5, 11, 9)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 7 times", 24, 5, 7)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 6 times", 23, 22, 7)
for _ in range(4):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, r"\u4f9d\u65e7\u662fbreak", 4, 28,
              11, 7, append_function=add_frame_with_beat) # BAR 65
for _ in range(56):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 72
FRAME_PT2_BASE.fill_units("                                 ", 24, 5, 9)
FRAME_PT2_BASE.fill_units("                                 ", 23, 22, 9)
FRAME_PT2_BASE.fill_units("                       ", 28, 11, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Overflow of chanting taste", 4, 6,
               4, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("             ", 19, 4, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("             ", 6, 4, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 73
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Overwhelming that's trick play", 4,
               30, 20, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("               ", 45, 20, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("               ", 30, 20, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 74
FRAME_PT2_BASE.fill_units("Thousands of historic", 6, 4, 7)
for _ in range(5):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("stories commented on page", 30, 20, 7)
for _ in range(9):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                     ", 6, 4, 9)
FRAME_PT2_BASE.fill_units("                         ", 30, 20, 9)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 76
FRAME_PT2_BASE.fill_units("Distances step under plates", 30, 20, 7)
for _ in range(8):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 77
FRAME_PT2_BASE.fill_units("                           ", 30, 20, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Destinations view and stay", 7, 27,
               11, 7, append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 78
FRAME_PT2_BASE.fill_units("                          ", 27, 11, 9)
FRAME_PT2_BASE.fill_units("3", 39, 11, 7)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("2", 39, 11, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("1", 39, 11, 7)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "let's forget the", 3, 32, 11, 5,
              append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 79
FRAME_PT2_BASE.fill_units("                ", 32, 11, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "homes needn't locate", 4, 30, 11,
               1, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                    ", 30, 11, 9)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 80
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Flooding cuisine worth to pay", 4,
               6, 4, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("               ", 20, 4, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 6, 4, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 81
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, 'Street performances "hooray"', 4,
               30, 20, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 44, 20, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 30, 20, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 82
FRAME_PT2_BASE.fill_units("Charming ancient practice", 6, 4, 7)
for _ in range(5):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("passing through to operate", 30, 20, 7)
for _ in range(9):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                         ", 6, 4, 9)
FRAME_PT2_BASE.fill_units("                          ", 30, 20, 9)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 84
FRAME_PT2_BASE.fill_units("No matter how far away", 30, 20, 7)
for _ in range(8):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 85
FRAME_PT2_BASE.fill_units("                      ", 30, 20, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Arrival with all regained", 7, 27,
               11, 7, append_function=add_frame_with_beat)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 86
FRAME_PT2_BASE.fill_units("                         ", 27, 11, 9)
FRAME_PT2_BASE.fill_style("""\
....WWWWWWWWWWWW....
..WWWWWWWWWWWWWWWW..
WWWW............WWWW
WWWW............WWWW
WWWW............WWWW
................WWWW
...............WWWWW
.............WWWWWW.
...........WWWWWW...
......WWWWWWWW......
......WWWWWWWW......
...........WWWWWW...
.............WWWWWW.
...............WWWWW
................WWWW
WWWW............WWWW
WWWW............WWWW
WWWW............WWWW
..WWWWWWWWWWWWWWWW..
....WWWWWWWWWWWW....
""", {"W": (None, 7), ".": (None, 6)}, 30, 2)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_style("""\
....WWWWWWWWWWWW....
..WWWWWWWWWWWWWWWW..
WWWW............WWWW
WWWW............WWWW
WWWW............WWWW
................WWWW
...............WWWWW
.............WWWWWW.
...........WWWWWW...
........WWWWWW......
......WWWWWW........
...WWWWWW...........
..WWWWW.............
.WWWWW..............
.WWWW...............
WWWWW...............
WWWW................
WWWW................
WWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWW
""", {"W": (None, 7), ".": (None, 6)}, 30, 2)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_style("""\
........WWWW........
......WWWWWW........
....WWWWWWWW........
..WWWW..WWWW........
WWWW....WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
........WWWW........
WWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWW
""", {"W": (None, 7), ".": (None, 6)}, 30, 2)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "everybody", 3, 35, 11, 5,
              append_function=add_frame_with_beat)
FRAME_PT2_BASE.fill_style("""\
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
....................
""", {".": (None, 6)}, 30, 2)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 87
FRAME_PT2_BASE.fill_units("         ", 35, 11, 9)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "have the plan delayed", 4, 30, 11,
               1, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units((" "*Frame.WIDTH+"\n")*Frame.HEIGHT, 0, 0, 9, 0)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 88
FRAME_PT2_BASE.fill_units("[SHOWCASE]", Frame.WIDTH//2-5, 11, 5)
for i in range(0, 24, 3):
    for j in range(0, 80, 10):
        FRAME_PT2_BASE.fill_style(("."*10+"\n")*3, {".": (None, 6)}, j, i)
        add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 96
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 8 times", 25, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                 ", 25, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 98
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Bi Shu Shan Zhuang means to break",
               5, 5, 11, 7, append_function=beat_line_alternate)
for _ in range(2):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                                 ", 5, 11, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 99
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Ba Shang Cao Yuan as if flight",
               5, 39, 13, 7, append_function=beat_line_alternate)
for _ in range(2):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                              ", 39, 13, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 100
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 9 times", 25, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                 ", 25, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 102
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Linking along takes its great",
               5, 5, 11, 7, append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 103
FRAME_PT2_BASE.fill_units("                             ", 5, 11, 9)
FRAME_PT2_BASE.fill_units("Making some dizzy on line", 27, 11, 4)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
for _ in range(8):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 104
FRAME_PT2_BASE.fill_units("                         ", 27, 11, 9)
for i in (26, 28, 25, 29, 23, 31, 20, 34):
    FRAME_PT2_BASE.fill_units("Making some dizzy on line", i, 11, 4)
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
    FRAME_PT2_BASE.fill_units("                         ", i, 11, 9) # BAR 105
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 10 times", 25, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                  ", 25, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 107
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Quite rewarded on such night",
               5, 5, 11, 7, append_function=beat_line_alternate)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 19, 11, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 5, 11, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 108
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Day by day just on cloud nine",
               5, 39, 13, 7, append_function=beat_line_alternate)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("               ", 53, 13, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("              ", 39, 13, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 109
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 11 times", 25, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                  ", 25, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 111
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "Absolutely no regret",
               5, 5, 5, 7, append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 112
FRAME_PT2_BASE.fill_units("                    ", 5, 5, 9)
FRAME_PT2_BASE.fill_units("Drop unnecessary guides", 28, 12, 3)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
for _ in range(7):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("                       ", 28, 12, 9)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 113
FRAME_PT2_BASE.fill_units("__ __ __", 39, 16, 7)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, r"\u4eac \u6d25 \u5180", 3, 6, 10,
               7, 4, append_function=beat_line_alternate)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, "never say", 3, 39, 16, 7,
               append_function=beat_line_alternate)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
FRAME_PT2_BASE.fill_units("                    ", 6, 10, 9, 6)
FRAME_PT2_BASE.fill_units("         ", 39, 16, 9)
beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 114
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, '"I\'m exhausted need to tie"', 5,
               26, 12, 7, append_function=add_frame_with_beat)
for _ in range(2):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 7)}, y=23)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 115
FRAME_PT2_BASE.fill_units("                           ", 26, 12, 9)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 12 times", 23, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
add_drop_text(
    FRAME_STRS, FRAME_PT2_BASE,
    "So near here, such grand there, weekend's Hebei time", 12, 14, 20,
    append_function=beat_line_alternate
)
FRAME_PT2_BASE.fill_units("                                  ", 23, 11, 9)
for _ in range(4):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 117
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Seize the opportunity", 5, 6, 2, 7,
              append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 118
add_drop_text(FRAME_STRS, FRAME_PT2_BASE, "Scenery all shift in rise", 5, 48,
              21, 7, append_function=beat_line_alternate)
for _ in range(3):
    beat_line_alternate(FRAME_STRS, FRAME_PT2_BASE) # BAR 119
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)})
FRAME_PT2_BASE.fill_style("."*Frame.WIDTH, {".": (None, 6)}, y=23)
FRAME_PT2_BASE.fill_units("                     ", 6, 2, 9)
FRAME_PT2_BASE.fill_units("                         ", 48, 21, 9)
FRAME_PT2_BASE.fill_units("[The 11-character SLOGAN] 13 times", 23, 11, 7)
FRAME_PT2_BASE.fill_style(
    "R              R       Y     G    Y     R  YY",
    {"R": (1, None), "Y": (3, None), "G": (2, None)}, 14, 20
)
FRAME_PT2_BASE.fill_units(
    "So near here, such grand there, weekend's Hebei time", 14, 20
)
for _ in range(16):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 121
FRAME_PT2_BASE.fill_units("                                  ", 23, 11, 9)
FRAME_PT2_BASE.fill_units(
    "                                                    ", 14, 20, 9
)
FRAME_PT2_BASE.fill_units(r"\u62cd\u6444\u4e8e\u627f\u5fb7", 10, 21, 0)
for _ in range(16):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 123
FRAME_PT2_BASE.fill_units("                              ", 10, 21, 9)
for _ in range(96):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 135
FRAME_PT2_BASE.fill_units(r"\u62cd\u6444\u4e8e\u5eca\u574a", 10, 21, 0)
for _ in range(16):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 137
FRAME_PT2_BASE.fill_units((" "*Frame.WIDTH+"\n")*Frame.HEIGHT, 0, 0, 9, 0)
for _ in range(12):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
add_popup_text(FRAME_STRS, FRAME_PT2_BASE, r"\u611f\u8c22\u89c2\u770b", 4, 28,
               12, 7, append_function=add_frame_with_beat) # BAR 139
for _ in range(13):
    add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("      ", 46, 12, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("      ", 40, 12, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE)
FRAME_PT2_BASE.fill_units("      ", 34, 12, 9)
add_frame_with_beat(FRAME_STRS, FRAME_PT2_BASE) # BAR 141
FRAME_PT2_BASE.fill_units("      ", 28, 12, 9)
FRAME_PT2_BASE.fill_units("Fine.", 72, 22, 7)
FRAME_STRS.append(FRAME_PT2_BASE.get_string())


parser = argparse.ArgumentParser(
    prog="PV of So Near Here, Such Grand There, Weekend's Hebei Time",
    description="This program outputs the frames of the PV of the song."
)
parser.add_argument(
    "-s", "--skip-frames", help="Skip foremost N frames", type=int
)
parser.add_argument(
    "-f", "--fps", help="Override the FPS (default: {0})".format(FPS),
    type=Fraction
)
parser.add_argument(
    "-V", "--version", help="Show version info of this program",
    action="store_true"
)

args = parser.parse_args()

if args.version:
    print("""\
PV of So Near Here, Such Grand There, Weekend's Hebei Time
Program: REGE (GitHub: IAmREGE  bilibili: 523423693)""")
    from sys import exit
    exit(0)

if args.skip_frames:
    del FRAME_STRS[:args.skip_frames]

SPF = 1 / (FPS if args.fps is None else args.fps)
start_time = monotonic()
count = 0
try:
    for count, body in enumerate(FRAME_STRS, start=1):
        print("\033[H", end=body, flush=True)
        while monotonic() - start_time < SPF * count:
            sleep(0.001)
except KeyboardInterrupt:
    print("1 frame presented" if count == 1
          else "{0} frames presented".format(count), file=stderr)
