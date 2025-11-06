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


FPS = Fraction(17, 3)

FRAME_STRS = []

FRAME_BASE = Frame()

FRAME_INTRO = FRAME_BASE.copy()

def draw_calendar(frame, x):
    frame.fill_units("""\
         2025-11
+--+--+--+--+--+--+--+--+
|W.|Mo|Tu|We|Th|Fr|Sa|Su|
+--+--+--+--+--+--+--+--+
|44|              |01|02|
+--+--+--+--+--+--+--+--+
|45|03|04|05|06|07|08|09|
+--+--+--+--+--+--+--+--+
|46|10|11|12|13|14|15|16|
+--+--+--+--+--+--+--+--+
|47|17|18|19|20|21|22|23|
+--+--+--+--+--+--+--+--+
|48|24|25|26|27|28|29|30|
+--+--+--+--+--+--+--+--+""", x, 3)
    frame.fill_style("""\


 GG                RR RR

 GG                RR RR

 GG                rr RR

 GG                RR RR

 GG                RR rr

 GG                RR RR""", {"G": (2,None), "R": (1,None), "r": (1, 4)}, x, 3)

def draw_calendar2(frame, x):
    frame.fill_units("""\
         2020-06
+--+--+--+--+--+--+--+--+
|W.|Mo|Tu|We|Th|Fr|Sa|Su|
+--+--+--+--+--+--+--+--+
|23|01|02|03|04|05|06|07|
+--+--+--+--+--+--+--+--+
|24|08|09|10|11|12|13|14|
+--+--+--+--+--+--+--+--+
|25|15|16|17|18|19|20|21|
+--+--+--+--+--+--+--+--+
|26|22|23|24|25|26|27|28|
+--+--+--+--+--+--+--+--+
|27|29|30|              |
+--+--+--+--+--+--+--+--+""", x, 3)
    frame.fill_style("""\


 GG                RR RR

 GG             bb RR RR

 GG                RR RR

 GG                RR rr

 GG                RR RR

 GG""", {"G": (2, None), "R": (1, None), "r": (1, 4), "b": (None, 4)}, x, 3)

draw_calendar(FRAME_INTRO, 50)
FRAME_INTRO.fill_units("TITLE: Cruel Summer", 2, 21, 5)
FRAME_INTRO.fill_units("COMPOSER: T. Swift, Jack Antonoff, St. Vincent", 23,
                       21, 1)
FRAME_INTRO.fill_units("VOCAL: Taylor Swift", 2, 22, 5)
FRAME_INTRO.fill_units("LYRICS: Annie Clark, T. Swift, J. Antonoff", 23, 22, 1)
FRAME_INTRO.fill_units("PV: REGE", 67, 22, 3)
beat = 1
beat_next = False

# PT 1
FRAME_PT1_BASE = FRAME_INTRO.copy()
for _ in range(4):
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
FRAME_PT1_BASE.fill_units("\n".join(" "*25 for _ in range(14)), 50, 3, 9, 9)
draw_calendar(FRAME_PT1_BASE, 44)
FRAME_PT1_BASE.fill_units("Yeah", 72, 9, 6, 9)
for _ in range(8):
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
FRAME_PT1_BASE.fill_units("\n".join(" "*25 for _ in range(14)), 44, 3, 9, 9)
draw_calendar(FRAME_PT1_BASE, 38)
FRAME_PT1_BASE.fill_units("Yeah", 66, 9, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 72, 9, 6, 9)
FRAME_PT1_BASE.fill_units("Yeah", 72, 11, 6, 9)
for _ in range(8):
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
FRAME_PT1_BASE.fill_units("\n".join(" "*25 for _ in range(14)), 38, 3, 9, 9)
draw_calendar(FRAME_PT1_BASE, 32)
FRAME_PT1_BASE.fill_units("Yeah", 60, 9, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 66, 9, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 72, 9, 6, 9)
FRAME_PT1_BASE.fill_units("Yeah", 66, 11, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 72, 11, 6, 9)
FRAME_PT1_BASE.fill_units("Yeah", 72, 13, 6, 9)
for _ in range(8):
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
FRAME_PT1_BASE.fill_units("\n".join(" "*25 for _ in range(14)), 32, 3, 9, 9)
draw_calendar(FRAME_PT1_BASE, 26)
FRAME_PT1_BASE.fill_units("Yeah", 54, 9, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 60, 9, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 66, 9, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 72, 9, 6, 9)
FRAME_PT1_BASE.fill_units("Yeah", 60, 11, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 66, 11, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 72, 11, 6, 9)
FRAME_PT1_BASE.fill_units("Yeah", 66, 13, 6, 9)
FRAME_PT1_BASE.fill_units("    ", 72, 13, 6, 9)
FRAME_PT1_BASE.fill_units("Yeah", 72, 15, 6, 9)
for _ in range(4):
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
PT1_ANIMS = (
    (("Fe", 2, 5, 5),), (("ver", 4, 5, 5),), (("drea", 8, 5, 5),),
    (("m", 12, 5, 5),), (("HIGH", 14, 5, 5),), (("gh", 16, 5, 5),),
    (("hi", 14, 5, 5), ("in", 19, 5, 5)), (("the", 22, 5, 5),), # BAR 5
    (("qui", 30, 7, 5),), (("e", 33, 7, 5),), (("t of", 34, 7, 5),),
    (("the", 39, 7, 5),), (("9", 43, 7, 5),), (), (("You", 2, 6, 5),),
    (("know", 6, 6, 5),), # BAR 6
    (), (("tha", 11, 6, 5),), (("t I", 14, 6, 5),), (), (("caugh", 18, 6, 5),),
    (("Oh", 54, 3, 6),), (("t it", 23, 6, 5), ("yeah", 57, 3, 6)),
    (("you're", 62, 3, 6),), # BAR 7
    (("->", 68, 3, 6),), (), (("I", 70, 3, 6),), (), (("want", 72, 3, 6),),
    (("it", 77, 3, 6),),
    (("\n".join(" "*25 for _ in range(14)), 26, 3, 9, 9),
     lambda: draw_calendar(FRAME_PT1_BASE, 27)), (("""\
Fever dream high in the
quiet of the night, You
know that I caught it  """, 2, 3, 5), (" "*24, 2, 6, 9)), # BAR 8
    (("Ba", 2, 7, 5),), (("?", 4, 7, 5),), (("ba", 6, 7, 5),),
    (("?", 8, 7, 5),), (("boy", 10, 7, 5),), (("d", 4, 7, 5), ("d", 8, 7, 5)),
    (("shi", 14, 7, 5),), (("ny", 17, 7, 5),), # BAR 9
    (("toy", 20, 7, 5),), (), (("with", 31, 7, 5),), (("a", 36, 7, 5),),
    (("pri", 38, 7, 5),), (("ce", 41, 7, 5),), (("You", 2, 8, 5),),
    (("know", 6, 8, 5),), # BAR 10
    (), (("tha", 11, 8, 5),), (("t I", 14, 8, 5),), (), (("bough", 18, 8, 5),),
    (("Oh", 54, 5, 6),), (("t it", 23, 8, 5), ("yeah", 57, 5, 6)),
    (("you're", 62, 5, 6),), # BAR 11
    (("->", 68, 5, 6),), (), (("I", 70, 5, 6),), ((" "*12, 31, 7, 9), ("""\
Bad bad boy shiny toy
with a price, You        \n\
know that I bought it""", 2, 7, 5)), (("want", 72, 5, 6), ("Ki", 2, 11, 5)),
    (("it", 77, 5, 6), ("lling", 4, 11, 5)), (("me", 10, 11, 5),), (), # BAR 12
    (("slow", 13, 11, 5), ("-", 10, 11, 5)), (("-", 11, 11, 5),),
    (("=", 10, 11, 5),), (("=", 11, 11, 5),),
    (("me", 10, 11, 5), ("out", 18, 11, 5)), (("the", 22, 11, 5),),
    (("win", 35, 7, 5),), (), # BAR 13
    (("dow", 38, 7, 5),), (), (), (("I'm", 2, 13, 5),),
    (("al", 6, 13, 5, 1),), (("ways", 8, 13, 5, 1),),
    ((" wai", 12, 13, 5, 1),), (("ting", 16, 13, 5, 1),), # BAR 14
    ((" for", 20, 13, 5, 1),), (("you", 2, 14, 5, 1),),
    ((" to", 5, 14, 5, 1),), ((" be", 8, 14, 5, 1),),
    ((" wai", 11, 14, 5, 1),), (("ting", 15, 14, 5, 1),),
    ((" be", 19, 14, 5, 1),), (("low", 22, 14, 5, 1),), # BAR 15
    (), (("I'm always waiting for\nyou to be waiting below", 2, 13, 5, 9),),
    (), (), (("De", 2, 16, 5),), (("vils", 4, 16, 5),), (("roll", 9, 16, 5),),
    (("the", 14, 16, 5),), # BAR 16
    (("d", 18, 16, 5), ("i", 19, 16, 1), ("c", 20, 16, 3), ("e", 21, 16, 2),
     ("randint(1, 6)", 31, 7, 3), ("window", 2, 12, 5)), (), (),
    (("dice", 18, 16, 5),), (("An", 2, 17, 5), (",", 22, 16, 5)),
    (("gels", 4, 17, 5),), (("roll", 9, 17, 5),),
    (("their", 14, 17, 5),), # BAR 17
    (("e", 20, 17, 5), ("y", 21, 17, 1), ("e", 22, 17, 3), ("s", 23, 17, 2),
     (">>>          ", 31, 7, 5)), (), (("eyes", 20, 17, 5),),
    (("What", 2, 19, 5), ("----", 2, 20)),
    (("doe", 7, 19, 5), ("----", 6, 20)),
    (("sn't", 10, 19, 5), ("----", 10, 20)), (),
    (("ki", 15, 19, 5), ("---", 14, 20)), # BAR 18
    (("ll", 17, 19, 5), ("--", 17, 20)), (("me", 20, 19, 5), ("---", 19, 20)),
    (("makes", 23, 19, 5), ("------", 22, 20)),
    (("me", 29, 19, 5), ("---", 28, 20)),
    (("wan", 32, 19, 5), ("---", 32, 20)), (("-", 31, 20),),
    ((r"[ts\_h' u]", 36, 19, 5), ("-----------", 35, 20)),
    (("t you mo   ", 35, 19, 5),), # BAR 19
    (), (("re", 43, 19, 5),), (), ((".", 45, 19, 5),)
)
for anims in PT1_ANIMS:
    for anim in anims:
        anim() if callable(anim) else FRAME_PT1_BASE.fill_units(*anim)
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

# PT 2
FRAME_PT2_BASE = FRAME_BASE.copy()
PT2_ANIMS = (
    (), ((">>> ", 0, 1, 5), ('_("And it\'s new")', 4, 1)), (), (), # BAR 20
    (("{}", 0, 2),), (), (), (), ((">>> ", 0, 3, 5),), (),
    (('_("The shape of your body")', 4, 3),), (), # BAR 21
    (("{'body': {'shape': []}}", 0, 4),), (), (), (), (), (),
    ((">>> ", 0, 5, 5), ('_("It\'s blue")', 4, 5)), (), # BAR 22
    ((r"{'body': {'shape': ['\x1b[44m']}}", 0, 6),), (), (), (),
    ((">>> ", 0, 7, 5),), (),
    (('_("The feeling I got")', 4, 7),), (), # BAR 23
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF']}}", 0, 8),), (),
    (), (), (), ((">>> ", 0, 9, 5),('_("And it\'s ooh"); _("whoa oh")', 4, 9)),
    (), (), # BAR 24
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j)]}}", 0, 10),), (), (), (), (), (), (),
    (), # BAR 25
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j), (-0.5+0.5j), 1.625j, (0.5+2.5j)]}}", 0,
      12),), (), (), (), (), (),
    ((">>> ", 0, 14, 5), ('_("It\'s a cruel summer")', 4, 14)), (), # BAR 26
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j), (-0.5+0.5j), 1.625j, (0.5+2.5j)]}, "
      "'date': '2020-06-21'}", 0, 15),), (), (), (), (), (), (), (), # BAR 27
    (("""Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OverflowError: The date selected is thought to be cruel.""", 0, 17),), (), (),
    (), (), ((">>> ", 0, 20, 5),), (('_("It\'s cool")', 4, 20),), (), # BAR 28
    (("RuntimeWarning: Assign to global variables within is not recommended. "
      "Affected \nvariables: cool_dict", 0, 21),), (), (), (),
    ((">>> ", 0, 23, 5),), ((r'print("\033[H\033[J")', 4, 23),),
    (((" "*79+"\n")*23, 0, 1, 9, 9), (">>> ", 0, 1, 5)),
    (('_("That\'s what I tell \'em")', 4, 1),), # BAR 29
    (), (), (), (), (), (), ((">>> ", 0, 2, 5), ('_("No rules")', 4, 2)),
    (), # BAR 30
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j), (-0.5+0.5j), 1.625j, (0.5+2.5j)]}, "
      "'date': '2020-06-21', 'rules': \nNone}", 0, 3),), (), (), (),
    ((">>> ", 0, 6, 5),), (), (('_("In breakable heaven")', 4, 6),),
    (), # BAR 31
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j), (-0.5+0.5j), 1.625j, (0.5+2.5j)]}, "
      "'date': '2020-06-21', 'rules': \n{'breakable_heaven': 'RULE_FREE'}}", 0,
      7),), (), (), (), (), (),
    ((">>> ", 0, 10, 5), ('_("But ooh"); _("whoa oh")', 4, 10)), (), # BAR 32
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j), (-0.5+0.5j), 1.625j, (0.5+2.5j)]}, "
      "'date': '2020-06-21', 'rules': \n{'breakable_heaven': {'content': "
      "'ooh'}}}", 0, 11),), (), (), (), (), (), (), (), # BAR 33
    (("{'body': {'shape': []}, 'feel': {'color': ['#0000FF'], 'path': "
      "[1j, (1+0j), -1j\n, (-1-0.5j), (-0.5+0.5j), 1.625j, (0.5+2.5j)]}, "
      "'date': '2020-06-21', 'rules': \n{'breakable_heaven': {'content': "
      "'ooh, whoa oh'}}}", 0, 14),), (), (), (), (), (),
    ((">>> ", 0, 17, 5), ('_("It\'s a cruel summer")', 4, 17)), (), # BAR 34
    (), (), (), (), (), (), (), (), # BAR 35
    (("""Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OverflowError: Cruel Again!!!""", 0, 18),), (), (),
    (), (), ((">>> ", 0, 21, 5),), (('"With you"', 4, 21),), (), # BAR 36
    (("'With you'", 0, 22), (">>> ", 0, 23, 5)), (), (), (),
    (("$*&#", 68, 23, 6),), (("e", 69, 23, 6),), (("Y", 68, 23, 6),),
    (("h", 71, 23, 6),), # BAR 37
    (((" "*79+"\n")*23, 0, 1, 9, 9), ("Yeah", 68, 21, 6)), (), (), (),
    (("%?@!", 74, 21, 6),), (("h", 77, 21, 6),), (("e", 75, 21, 6),),
    (("Y", 74, 21, 6),
     ("[(PHONEMES CHECK IS NOW DISABLED)]", 23, 12, 1, 5)) # BAR 38
)
for anims in PT2_ANIMS:
    for anim in anims:
        anim() if callable(anim) else FRAME_PT2_BASE.fill_units(*anim)
    FRAME_PT2_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT2_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

# PT 3
FRAME_PT3_BASE = FRAME_BASE.copy()
draw_calendar2(FRAME_PT3_BASE, 54)
def clear_alnums():
    for y in range(5, 14):
        for x in range(55, 78):
            if FRAME_PT3_BASE.units[y][x].char not in " -+|":
                FRAME_PT3_BASE.fill_units(" ", x, y, 9, 9)
    for x in range(55, 63):
        if FRAME_PT3_BASE.units[15][x].char not in " -+|":
            FRAME_PT3_BASE.fill_units(" ", x, 15, 9, 9)
PT3_ANIMS = (
    (("Hang", 2, 2, 5),), (("your", 7, 2, 5),), (("hea", 12, 2, 5),),
    (("d", 15, 2, 5),), (("low", 17, 2, 5),), (), (("in", 21, 2, 5),),
    (("the", 24, 2, 5),), # BAR 39
    (("glow", 28, 2, 5),), (), (("of", 33, 2, 5),), (("the", 36, 2, 5),),
    (("ven", 40, 2, 5),), (("ding", 43, 2, 5),), (("mer", 48, 2, 5),),
    (("achine", 49, 2, 5),), # BAR 40
    (), (("I'm", 64, 15, 5),), (("naar", 68, 15, 5),), (("ot ", 69, 15, 5),),
    (("die", 72, 15, 5),), (("Oh", 64, 18, 6),),
    (("ying", 73, 15, 5), ("yeah", 67, 18, 6)),
    (("you're", 72, 18, 6),), # BAR 41
    (("right", 64, 19, 6),), (), (("I", 70, 19, 6),), (),
    (("want", 72, 19, 6),), (("it", 77, 19, 6),), (),
    (("We", 2, 4, 5), ("~~", 2, 5, 3)), # BAR 42
    (("say", 5, 4, 5), ("~~~", 5, 5, 3)),
    (("that", 9, 4, 5), ("~~~~", 9, 5, 3)),
    (("we", 14, 4, 5), ("~~", 14, 5, 3)),
    (("'ll", 16, 4, 5), ("~~~", 16, 5, 3)),
    (("jar", 20, 4, 5), ("~~~", 20, 5, 3)), (("s", 24, 4, 5), ("~", 24, 5, 3)),
    (("crew", 25, 4, 5), ("~~~~", 25, 5, 3)),
    (("it", 30, 4, 5), ("~~", 30, 5, 3)), # BAR 43
    (("ah", 33, 4, 5), ("~~", 33, 5, 3)), (),
    (("up in", 33, 4, 5), ("~~", 36, 5, 3)),
    (("these", 39, 4, 5), ("~~~~~", 39, 5, 3)),
    (("try", 45, 4, 5), ("~~~", 45, 5, 3)),
    (("ing", 48, 4, 5), ("~~~", 48, 5, 3)), (),
    (("time  ", 2, 5, 5), ("~~~~", 2, 6, 3)), # BAR 44
    (("s", 6, 5, 5), ("~", 6, 6, 3)), (("we're", 8, 5, 5), ("~~~~~", 8, 6, 3)),
    (("naar ", 14, 5, 5), ("~~~~", 14, 6, 3)),
    (("ot ", 15, 5, 5), (" ", 17, 6, 9)),
    (("try  ", 18, 5, 5), ("~~~", 18, 6, 3)), (("Oh", 64, 21, 6),),
    (("ing", 21, 5, 5), ("~~~", 21, 6, 3), ("yeah", 67, 21, 6)),
    (("you're", 72, 21, 6),), # BAR 45
    (("right", 64, 22, 6), ("I'm not dying", 2, 3, 5), (" "*49, 2, 4, 9), ("""\
We say that we'll just screw it up in these trying
times, We're not trying""", 2, 5, 5), (",", 55, 2, 5), (" "*13, 64, 15, 9)),
    (), (("I", 70, 22, 6),), (("So", 2, 8, 5),),
    (("want", 72, 22, 6), ("cut", 5, 8, 5)),
    (("it", 77, 22, 6), ("the", 9, 8, 5)), (("head", 13, 8, 5),), (), # BAR 46
    (("lie", 18, 8, 5),), (), (("    ts", 17, 8, 5),), ((",", 23, 8, 5),),
    (("sum", 25, 8, 5),), (("mer", 28, 8, 5),), (("'s a", 31, 8, 5),),
    (), # BAR 47
    (("night", 36, 8, 5),), (), (("   f ", 36, 8, 5),), (("I'm", 2, 10, 5),),
    (("al", 6, 10, 5, 1),), (("ways", 8, 10, 5, 1),),
    ((" wai", 12, 10, 5, 1),), (("ting", 16, 10, 5, 1),), # BAR 48
    ((" for", 20, 10, 5, 1),), ((" you", 24, 10, 5, 1),),
    ((" just", 28, 10, 5, 1),), ((" to", 33, 10, 5, 1),),
    ((" cut", 36, 10, 5, 1),), ((" to", 40, 10, 5, 1),),
    ((" the", 43, 10, 5, 1),), (("bone", 48, 10, 5),), # BAR 49
    (), (("always waiting for you just to cut to the", 6, 10, 5, 9),),
    (("ligh", 17, 8, 5), ("knife", 36, 8, 5)), (), (("De", 2, 12, 5),),
    (("vils", 4, 12, 5),), (("roll", 9, 12, 5),),
    (("the", 14, 12, 5),), # BAR 50
    (("d", 18, 12, 5), ("i", 19, 12, 1), ("c", 20, 12, 3), ("e", 21, 12, 2),
     ("randint(1, 6)", 64, 15, 3)), (), (), (("dice,", 18, 12, 5),),
    (("An", 24, 12, 5),), (("gels", 26, 12, 5),), (("roll", 31, 12, 5),),
    (("their", 36, 12, 5),), # BAR 51
    (("e", 42, 12, 5), ("y", 43, 12, 1), ("e", 44, 12, 3), ("s", 45, 12, 2),
     (">>>          ", 64, 15, 5)), (), (("eyes", 42, 12, 5),),
    (("And", 2, 14, 5),), (("if", 6, 14, 5), (" ", 57, 7), (" ", 60, 7),
                           ("  ", 58, 6), ("  ", 58, 8)),
    (("I", 9, 14, 5), (" ", 57, 5), ("  ", 61, 6), (" ", 63, 7),("  ", 55, 8)),
    (("  ", 64, 6), ("  ", 64, 8), (" ", 63, 9), (" ", 66, 9)),
    (("bleed", 11, 14, 5), ("  ", 61, 10), ("  ", 67, 10), (" ", 66, 11),
     (" ", 69, 11)), # BAR 52
    (("  ", 70, 10), (" ", 72, 9), (" ", 60, 11), ("  ", 58, 12)),
    (("you'll", 17, 14, 5), ("  ", 58, 14), ("  ", 70, 8), (" ", 75, 9),
     ("  ", 76, 8)),
    (("be", 24, 14, 5), ("  ", 70, 6), (" ", 75, 7), (" ", 57, 15),
     ("  ", 76, 10)),
    (("the", 27, 14, 5), ("  ", 55, 14), ("  ", 76, 12), (" ", 60, 13),
     (" ", 63, 13)),
    (("laa", 31, 14, 5), ("  ", 55, 12), ("  ", 61, 14), (" ", 75, 13),
     (" ", 69, 5)),
    (("st", 33, 14, 5), ("  ", 67, 6), (" ", 72, 13), ("  ", 76, 6),
     (" ", 69, 13)),
    (("to", 36, 14, 5), ("  ", 73, 12), (" ", 75, 5)),
    (("know", 39, 14, 5), ("fetch()", 68, 15, 3)), # BAR 53
    (("{'bled': True}", 64, 15, 9),), (), (clear_alnums,),
    (lambda: FRAME_PT3_BASE.fill_style("""\
OOOOOOOOOOO.HH.........
OO.......OO.HH.........
OO.......OO.HH.........
OO.......OO.HH.........
OO.......OO.HHHHHHHHHHH
OO.......OO.HH.......HH
OO.......OO.HH.......HH
OO.......OO.HH.......HH
OOOOOOOOOOO.HH.......HH
........
........""", {"O": (7, 5), "H": (2, 5), ".": (0, 7)}, 55, 5),), (),
    (lambda: FRAME_PT3_BASE.fill_style("""\
HH.........
HH.........
HH.........
HH.........
HHHHHHHHHHH
HH.......HH
HH.......HH
HH.......HH
HH.......HH""", {"H": (2, 1)}, 67, 5), ("Oh (core dumped)", 63, 15, 9))
)
for anims in PT3_ANIMS:
    for anim in anims:
        anim() if callable(anim) else FRAME_PT3_BASE.fill_units(*anim)
    FRAME_PT3_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT3_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

# PT 4
FRAME_PT4_BASE = FRAME_BASE.copy()
PT4_ANIMS = (
    ((">>> \n... ", 0, 1, 5),
     ('_(action="retell", reformat=True,\ncolor="auto")', 4, 1)), (), # BAR 54
    (("It's", 0, 3), ("new", 5, 3, 0, 7)), (), (), (), (), (), (), (), # BAR 55
    ((", the shape of your body", 8, 3),), (), (), (), (), (), (), (), # BAR 56
    (("It's", 0, 4), ("blue", 5, 4, 4)), (), (), (), (), (), (), (), # BAR 57
    ((", the feeling I got", 9, 4),), (), (), (), (), (("And", 0, 5),), (),
    (), # BAR 58
    (("it's", 4, 5), ("o", 9, 5, 5), ("o", 10, 5, 1), ("h", 11, 5, 3)), (), (),
    (), (), (), (), (), # BAR 59
    ((",", 12, 5), ("w", 14, 5, 2), ("h", 15, 5, 3), ("o", 16, 5, 1),
     ("a", 17, 5, 5), ("oh", 19, 5)), (), (), (), (), (), (), (), # BAR 60
    (("It's a", 0, 6), ("cr", 7, 6, 2, 1), ("ue", 9, 6, 6, 1),
     ("l", 11, 6, 4, 1)), (), (), (), (), (), (), (), # BAR 61
    (("summer", 13, 6, 1, 3),), (), (), (), (), (), (), (), # BAR 62
    (("It's", 0, 7), ("cool", 5, 7, 9, 4)), (), (), (), (), (), (),
    (), # BAR 63
    ((", that's what I tell 'em", 9, 7),), (), (), (), (), (), (), (), # BAR 64
    (("No rules", 0, 8),), (), (), (), (), (), (), (), # BAR 65
    (("in", 9, 8), ("b", 12, 8, 7, 6), ("r", 13, 8, 5, 4), ("e", 14, 8, 3, 2),
     ("a", 15, 8, 1, 0), ("k", 16, 8, 6, 3), ("a", 17, 8, 4, 1),
     ("b", 18, 8, 2, 7), ("l", 19, 8, 0, 5), ("e", 20, 8, 2, 6),
     ("heaven", 22, 8)), (), (), (), (), (), (), (), # BAR 66
    (("But", 0, 9), ("o", 4, 9, 5), ("o", 5, 9, 1), ("h", 6, 9, 3)), (), (),
    (), (), (), (), (), # BAR 67
    ((",", 7, 9), ("w", 9, 9, 2), ("h", 10, 9, 3), ("o", 11, 9, 1),
     ("a", 12, 9, 5), ("oh", 14, 9)), (), (), (), (), (), (), (), # BAR 68
    (("It's a", 0, 10), ("cr", 7, 10, 4, 1), ("ue", 9, 10, 6, 1),
     ("l", 11, 10, 2, 1)), (), (), (), (), (), (), (), # BAR 69
    (("summer", 13, 10, 1, 3),), (), (), (), ((">>> ", 0, 11, 5),),
    (('"With you"', 4, 11),), (("'With you'", 0, 12), (">>> ", 0, 13, 5)),
    (), # BAR 70
    ((" \n"*22, 39, 0, 0, 7), (" "*79, 0, 22, 0, 7), ("0 python3", 3, 22),
     ("1 ./up.sh", 43, 22)), (), (("I'm", 40, 0, 1),), (),
    (("drunk", 44, 0, 6),), (), (("in", 50, 0, 2),),
    (("the", 53, 0, 3),), # BAR 71
    (("baa", 57, 0, 9, 3),), (("ck", 59, 0, 9, 3), (" of", 61, 0, 9, 2)),
    ((" the", 64, 0, 9, 6),), ((" car", 68, 0, 9, 1),),
    (("    ", 72, 0, 9, 1),), (("   ", 76, 0, 9, 1),), (("An", 40, 1),),
    (("d I", 42, 1),), # BAR 72
    (("cry", 46, 1, 1),), (("ied", 48, 1, 1),), (("lie", 52, 1, 3),),
    (("ke a", 54, 1, 3),), (("bay", 59, 1, 6),), (("baby", 59, 1, 2),),
    (("car", 64, 1, 1),), (("coming", 64, 1, 1),), # BAR 73
    (("home", 46, 2, 3),), (("from", 51, 2),), (("the", 56, 2),),
    (("bar", 60, 2, 0, 7),), (), (), (("oh", 64, 2),),
    (("h", 66, 2),), # BAR 74
    (), (("Said", 40, 3, 3),), (("I'm", 45, 3),), (), (("fine", 49, 3, 2),),
    (), (("but", 54, 3),), (("it", 58, 3),), # BAR 75
    (("was", 61, 3, 9, 1),), (("wasn't", 61, 3, 1, 5),), (),
    ((" true", 67, 3, 2, 1),), (("    ", 72, 3, 9, 1),),
    (("   ", 76, 3, 9, 1),), (("I", 40, 4),), (("DON'T", 42, 4),), # BAR 76
    (("WANT", 48, 4, 9, 1),), ((" TO", 52, 4, 9, 1),),
    ((" KEE", 55, 4, 1, 5),), (("P", 59, 4, 1, 5),), ((" SEA", 60, 4, 4, 5),),
    (), (("CRETS", 63, 4, 4, 5),), ((" JAR", 68, 4, 1, 4),), # BAR 77
    (("JUST", 69, 4, 9, 4),), ((" TO", 73, 4, 9, 4),),
    (("   ", 76, 4, 9, 4), ("KEY             ", 48, 5, 0, 3)), (),
    (("KEEP-----\\_____ ", 48, 5, 1, 3), ("YOU            ", 64, 5, 2, 3)),
    (("-----\\_____ ", 67, 5, 2, 3),), (("And", 40, 6),),
    (("I", 44, 6),), # BAR 78
    (), (), (("snuck", 46, 6, 5),), (), (("in", 52, 6, 5),), (),
    (("through", 55, 6, 1),), (("the", 63, 6),), # BAR 79
    (("gar", 67, 6, 2),), (("den", 70, 6, 2),), (), (("gate", 74, 6, 2),), (),
    (), (("Ev", 40, 7),), (("ery", 42, 7),), # BAR 80
    (("night", 46, 7, 5),), (), (("that", 52, 7),), (), (("sum", 57, 7, 3),),
    (("mer", 60, 7, 3),), (("just", 64, 7),), (("to", 69, 7),), # BAR 81
    (("seal", 46, 8, 6),), (("my", 51, 8, 1),), (), (("fate", 54, 8, 1),), (),
    (), (("oh", 59, 8),), (("h", 61, 8),), # BAR 82
    (), (("And", 40, 9),), (("I", 44, 9, 1),), (("s", 46, 9),),
    (("scream", 46, 9, 1),), (), (("for", 53, 9),),
    (("what", 57, 9),), # BAR 83
    (("whatev", 57, 9, 9, 1),), (("er", 63, 9, 9, 1),),
    ((" it's", 65, 9, 9, 5),), ((" were", 70, 9, 9, 5),), (),
    (("worth", 71, 9, 3, 5),), (), (("I", 40, 10),), # BAR 84
    (("LOT", 42, 10, 9, 1),), (), (("VE YOU", 44, 10, 9, 1),), (),
    ((" AIN'T", 50, 10, 1, 3),), (), ((" THAT", 56, 10, 9, 3),),
    ((" THE", 61, 10, 9, 3),), # BAR 85
    ((" WORSE", 65, 10, 3, 5),), (), ((" WORST THING", 65, 10, 1, 5),),
    (("  ", 77, 10, 1, 5),), (("YOU", 65, 11, 2, 3),),
    ((" EV", 68, 11, 2, 3),), (("ER", 71, 11, 2, 3),),
    ((" HER", 73, 11, 5, 3),), # BAR 86
    (), (), ((" HEARD", 73, 11, 2, 3), ("2 He     ", 43, 22)), (),
    (("3 He looks", 43, 22),), (), (("4 He looks up", 43, 22),), (), # BAR 87
    (("5 He looks up grin", 43, 22),), (("6 He looks up, grinning", 43, 22),),
    (("7 He looks up, grinning lie", 43, 22),),
    (("8 He looks up, grinning like it", 43, 22),),
    (("10 He looks up, grinning like a debt", 43, 22),
     ((" "*39+"\n")*21, 0, 0, 9, 9), ("--        ", 2, 22)),
    (("9 He looks up, grinning like a devil", 43, 22),),
    (("[screen is terminating]", 0, 23), ("____", 0, 1, 5)), (), # BAR 88
    (("___", 5, 1, 5),), (), (), (), (("It's", 0, 1, 5),), (("new", 5, 1, 5),),
    (("___", 9, 1, 5),), (("_____", 13, 1, 5),), # BAR 89
    (), (("__", 19, 1, 5),), (("____", 22, 1, 5),), (), (("___", 27, 1, 5),),
    (("_", 30, 1, 5),), (("____", 0, 2, 5),), (), # BAR 90
    (("____", 5, 2, 5),), (), (), (), (("It's", 0, 2, 5),),
    (("blue", 5, 2, 5),), (("___", 10, 2, 5),), (("___", 14, 2, 5),), # BAR 91
    (), (("____", 17, 2, 5),), (("_", 22, 2, 5),), (), (("___", 24, 2, 5),),
    (("___", 28, 2, 5),), (("____", 0, 3, 5),), (), # BAR 92
    (("___", 5, 3, 5),), (("your", 22, 1),), (("fee", 14, 2),), (),
    (("the", 9, 1),), (("and", 28, 2),), (("____", 9, 3, 5),),
    (("I", 22, 2),), # BAR 93
    (), (("of", 19, 1),), (("the", 10, 2),), (("__", 14, 3, 5),), (), (),
    (("____", 17, 3, 5),), (("_", 22, 3, 5),), # BAR 94
    (("_____", 24, 3, 5),), (("shape", 13, 1),), (("ling", 17, 2),), (),
    (("It's", 0, 3),), (("got", 24, 2),), (("___", 30, 3, 5),),
    (("dy", 29, 1),), # BAR 95
    (), (("a", 22, 3),), (("___", 33, 3, 5),), (), (("It's", 17, 3),),
    (("____", 0, 4, 5),), (), # BAR 96
    (("____", 5, 4, 5),), (), (), (), (("cool", 5, 4),), (("It's", 0, 4),),
    (("bo", 27, 1),), (("____", 10, 4, 5),), # BAR 97
    (), (("__", 14, 4, 5), ("____", 17, 4, 5)), (("_", 22, 4, 5),), (),
    (("____", 24, 4, 5),), (("___", 29, 4, 5),), (("__", 0, 5, 5),),
    (), # BAR 98
    (("____", 3, 5, 5),), (), (), (("s", 7, 5, 5),), (("rule", 3, 5),),
    (("No", 0, 5),), (("__", 9, 5, 5),), (("____", 12, 5, 5),), # BAR 99
    (), (("__", 16, 5, 5),), (("___", 18, 5, 5),), (), (("____", 22, 5, 5),),
    (("__", 26, 5, 5),), (("___", 0, 6, 5),), (("head", 22, 5),), # BAR 100
    (("___", 4, 6, 5),), (("'s", 14, 4),), (("bray", 12, 5),), (),
    (("ker", 15, 5),), (("'em", 29, 4),), (("____", 8, 6, 5),),
    (("I", 22, 4),), # BAR 101
    (), (("in", 9, 5),), (("tell", 24, 4),), (("__", 13, 6, 5),), (), (),
    (("____", 16, 6, 5),), (("_", 21, 6, 5),), # BAR 102
    (("_____", 23, 6, 5),), (("eakable", 14, 5),), (("what", 17, 4),), (),
    (("But", 0, 6),), (("a", 21, 6),), (("___", 29, 6, 5),),
    (("ven", 25, 5),), # BAR 103
    (), (("a", 22, 3),), (("___", 32, 6, 5),), (), (("It's", 16, 6),), (), (),
    (("With", 0, 7),), (("you", 5, 7),), # BAR 104
    (), (), ((">", 39, 0, 7, 4), ("ACC: N/A", 28, 22)), (), (), (), (),
    (), # BAR 105
    (), (), (), (), (), (), ((" ", 39, 0, 9, 2), (">", 39, 1, 7, 4),
                             ("ACC: 100%", 28, 22, 6)), (), # BAR 106
    (), (), (), (), (), (), (), (), # BAR 107
    ((" ", 39, 1, 9, 2), (">", 39, 2, 7, 4)), (), (), (), (), (), (),
    (), # BAR 108
    ((" ", 39, 2, 9, 2),), ((">", 39, 3, 7, 4),), (), (), (), (), (),
    (), # BAR 109
    (), (), (), (), (), (), ((" ", 39, 3, 9, 3), (">", 39, 4, 7, 4),
                             ("ACC: 87.5%", 28, 22, 2)), (), # BAR 110
    (), (), (), (), (), (), (), (), # BAR 111
    (), (), ((" ", 39, 4, 9, 1), (">", 39, 5, 7, 4),("ACC: 70%  ", 28, 22, 3)),
    (), (), (), ((" ", 39, 5, 9, 3), (">", 39, 6, 7, 4),
                 ("ACC: 66.7%", 28, 22, 1)), (), # BAR 112
    (), (), (), (), (), (), (), (), # BAR 113
    (), (), (), (), (), ((" ", 39, 6, 9, 2), ("ACC: 71.4%", 28, 22, 3)),
    ((">", 39, 7, 7, 4),), (), # BAR 114
    (), (), (), (), (), (), (), (), # BAR 115
    ((" ", 39, 7, 9, 2), (">", 39, 8, 7, 4), ("ACC: 75%  ", 28, 22, 3)), (),
    (), (), (), (), (), (), # BAR 116
    ((" ", 39, 8, 9, 3), ("ACC: 72.2%", 28, 22, 3)), ((">", 39, 9, 7, 4),), (),
    (), (), (), (), (), # BAR 117
    (), (), (), (), (), (), ((" ", 39, 9, 9, 1), ("ACC: 65%  ", 28, 22, 3)),
    ((">", 39, 10, 7, 4),), # BAR 118
    (), (), (), (), (), (), (), (), # BAR 119
    (), (), (), (), ((" ", 39, 10, 9, 1), (">", 39, 11, 7, 4),
                     ("ACC: 59.1%", 28, 22, 1)), (), (), (), # BAR 120
    (), (), (), ((" ", 39, 11, 9, 1), ("ACC: 54.2%", 28, 22, 1)),
    ((" Yeah", 33, 22, 6),), (), (), (), # BAR 121
    (), (), (), (), (("Yeah", 28, 22, 6),), (), (), (), # BAR 122
    (), (), (), (), (("Yeah", 22, 22, 6),), (), (), (), # BAR 123
    (), (), (), (), (("Yeah", 16, 22, 6),), (), (),
    (("Broadcast message from cruelsummer@taylor\n\n"
      "The system will power off now!", 0, 1, 9, 9),) # BAR 124
)
for anims in PT4_ANIMS:
    for anim in anims:
        anim() if callable(anim) else FRAME_PT4_BASE.fill_units(*anim)
    FRAME_PT4_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 73, 23, 4
    )
    FRAME_STRS.append(FRAME_PT4_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

FRAME_PT4_BASE.fill_units("Fine.", 73, 23, 4)
FRAME_STRS.append(FRAME_PT4_BASE.get_string())
FRAME_PT4_BASE.fill_units((" "*79+"\n")*24, 0, 0, 9, 9)
FRAME_PT4_BASE.fill_units("Fine.", 73, 23, 4)
FRAME_STRS.append(FRAME_PT4_BASE.get_string())


parser = argparse.ArgumentParser(
    prog="PV of Cruel Summer",
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
PV of Cruel Summer
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
