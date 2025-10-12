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
        LIGHTBLACK_EX = "\033[90m"
        LIGHTRED_EX = "\033[91m"
        LIGHTGREEN_EX = "\033[92m"
        LIGHTYELLOW_EX = "\033[93m"
        LIGHTBLUE_EX = "\033[94m"
        LIGHTMAGENTA_EX = "\033[95m"
        LIGHTCYAN_EX = "\033[96m"
        LIGHTWHITE_EX = "\033[97m"

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
        LIGHTBLACK_EX = "\033[100m"
        LIGHTRED_EX = "\033[101m"
        LIGHTGREEN_EX = "\033[102m"
        LIGHTYELLOW_EX = "\033[103m"
        LIGHTBLUE_EX = "\033[104m"
        LIGHTMAGENTA_EX = "\033[105m"
        LIGHTCYAN_EX = "\033[106m"
        LIGHTWHITE_EX = "\033[107m"


FORE_COLOR_MAP = (Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
                  Fore.MAGENTA, Fore.CYAN, Fore.WHITE, "", Fore.RESET,
                  Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX,
                  Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX,
                  Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX)
BACK_COLOR_MAP = (Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE,
                  Back.MAGENTA, Back.CYAN, Back.WHITE, "", Back.RESET,
                  Back.LIGHTBLACK_EX, Back.LIGHTRED_EX, Back.LIGHTGREEN_EX,
                  Back.LIGHTYELLOW_EX, Back.LIGHTBLUE_EX, Back.LIGHTMAGENTA_EX,
                  Back.LIGHTCYAN_EX, Back.LIGHTWHITE_EX)


class FrameUnit:
    def __init__(self, char=" ", fore=9, back=9):
        self.char = char
        self.fore = fore
        self.back = back

    def copy(self):
        return type(self)(self.char, self.fore, self.back)


class Frame:
    WIDTH = 119
    HEIGHT = 29

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


LUO_COLOR = 6
LING_COLOR = 1
STARDUST_COLOR = 5
SHIAN_COLOR = 3

FPS = Fraction(1507, 300)

FRAME_STRS = []

FRAME_BASE = Frame()

FRAME_INTRO = FRAME_BASE.copy()
FRAME_INTRO.fill_style("""\
                                    WWWWWW
                              WWWWWWWWWWWW
                        WWWWWWWWWWWWWWWWWW
                   WWWWWWWWWWWWWWWWWWWWWWW
            WWWWW  WWWWWWWWWWWWWWWWWWWWWWW
      WWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW

WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
      WWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
            WWWWW  WWWWWWWWWWWWWWWWWWWWWWW
                   WWWWWWWWWWWWWWWWWWWWWWW
                        WWWWWWWWWWWWWWWWWW
                              WWWWWWWWWWWW
                                    WWWWWW""", {"W": (None, 6)}, 2, 2)
FRAME_INTRO.fill_style("""\
RR  RR  RRRRRRRR          RRRRRRRR  RRRRRRRR          RRRRRRRR  RRRRRRRR
RR  RR  RR                RR    RR        RR                RR  RR    RR
RR  RR  RR                RR    RR        RR                RR  RR    RR
    RR  RRRRRRRR  RRRRRR  RR    RR        RR  RRRRRR  RRRRRRRR  RRRRRRRR
    RR        RR          RR    RR        RR          RR              RR
    RR        RR          RR    RR        RR          RR              RR
    RR  RRRRRRRR          RRRRRRRR        RR          RRRRRRRR  RRRRRRRR



BB  BBBBBBBB  BBBBBBBB          BB  BBBBBBBB          BB  BB    BB
BB        BB  BB                BB  BB    BB          BB  BB    BB
BB        BB  BB                BB  BB    BB          BB  BB    BB
    BBBBBBBB  BBBBBBBB  BBBBBB  BB  BB    BB  BBBBBB  BB  BBBBBBBB
    BB              BB          BB  BB    BB          BB        BB
    BB              BB          BB  BB    BB          BB        BB
    BBBBBBBB  BBBBBBBB          BB  BBBBBBBB          BB        BB""", {
    "R": (None, 11), "B": (None, 14)
}, 46, 4)
FRAME_INTRO.fill_units("TITLE: Ten To Farewell", 49, 24, 1)
FRAME_INTRO.fill_units("COMPOSER & LYRICS: REGE", 72, 24, 17)
FRAME_INTRO.fill_units("SPECIAL TNKS: MS Corp", 97, 24, 2)
FRAME_INTRO.fill_units("VOCAL: ", 49, 26, 14)
FRAME_INTRO.fill_units("Luo Tianyi", 56, 26, LUO_COLOR)
FRAME_INTRO.fill_units(", ", 66, 26, 7)
FRAME_INTRO.fill_units("Yuezheng Ling", 68, 26, LING_COLOR)
FRAME_INTRO.fill_units(", ", 81, 26, 7)
FRAME_INTRO.fill_units("Stardust", 83, 26, STARDUST_COLOR)
FRAME_INTRO.fill_units(", ", 91, 26, 7)
FRAME_INTRO.fill_units("Shian", 93, 26, SHIAN_COLOR)
FRAME_INTRO.fill_units("PV: REGE", 110, 26, 3)

# PT 1
FRAME_PT1_BASE = FRAME_INTRO.copy()
PT1_CAPTIONS = (
    (), (),
    (("Ladie", 4, 24, 5),), (("s and", 9, 24, 5),),
    (("gen", 15, 24, 5),), (("tle", 18, 24, 5),),
    (("men", 21, 24, 5),), (),
    ((", today's", 24, 24, 5),), (("ju", 34, 24, 5),),
    (("Jul", 34, 24, 5),), (("twenty", 38, 24, 5),),
    (("-nin", 44, 24, 5),), (("29        ", 38, 24, 5),),
    ((", twenty", 40, 24, 5),), (("2015  ", 42, 24, 5),),
    (("2015-07-29  ", 34, 24, 5),), ((".", 44, 24, 5),),
    (("Mic", 4, 25, 5),), (("rosof", 7, 25, 5),),
    (("t to", 12, 25, 5),), (("day re", 16, 25, 5),),
    (("lee", 22, 25, 5),), (("ased", 24, 25, 5),),
    (("windows", 29, 25, 5),), (("te", 37, 25, 5),),
    (("Windows 10", 29, 25, 5),), ((".", 39, 25, 5),),
    (("Windo", 4, 26, 5),), (("ws te", 9, 26, 5),),
    (("10 bring", 12, 26, 5), ("Coming", 4, 24, 6)),
    (("s a", 20, 26, 5), ("with dye", 11, 24, 6)),
    (("na", 18, 24, 6),), (("mic ta", 20, 24, 6),),
    (("iles", 25, 24, 6),), ((", wi", 29, 24, 6),),
    (("ndows", 33, 24, 6),), ((" tenni", 38, 24, 6),),
    (("Windows 10 is ", 31, 24, 6), ("raise", 4, 25, 6)),
    (("ing you", 8, 25, 6),),
    (("UI to", 12, 25, 6),), ((" a high", 17, 25, 6),),
    (("er play", 24, 25, 6),), (("ce", 30, 25, 6),),
    ((". With", 32, 25, 6),), ((" better per", 38, 25, 6),),
    (("   ", 46, 25, 6), ("perfore", 4, 26, 6)), (("man", 10, 26, 6),),
    (("ce", 13, 26, 6),), ((", sor", 15, 26, 6),),
    (("ftware", 19, 26, 6),), (("run", 26, 26, 6),),
    (("s fa", 29, 26, 6),), (("st", 33, 26, 6),),
    (("er than", 35, 26, 6),), (("ever", 43, 26, 6), ("be", 4, 27, 6)),
    (("fore", 6, 27, 6),), ((".", 10, 27, 6),)
)
beat = 1
beat_next = False
for anims in PT1_CAPTIONS:
    for anim in anims:
        FRAME_PT1_BASE.fill_units(*anim)
    FRAME_PT1_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 113, 28, 10
    )
    FRAME_STRS.append(FRAME_PT1_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

# PT 2
FRAME_PT2_BASE = FRAME_INTRO.copy()
FRAME_PT2_BASE.fill_style("""\
                                    WWWWWW
                              WWWWWWWWWWWW
                        WWWWWWWWWWWWWWWWWW
                   WWWWWWWWWWWWWWWWWWWWWWW
            WWWWW  WWWWWWWWWWWWWWWWWWWWWWW
      WWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW

WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
      WWWWWWWWWWW  WWWWWWWWWWWWWWWWWWWWWWW
            WWWWW  WWWWWWWWWWWWWWWWWWWWWWW
                   WWWWWWWWWWWWWWWWWWWWWWW
                        WWWWWWWWWWWWWWWWWW
                              WWWWWWWWWWWW
                                    WWWWWW""", {"W": (None, 9)}, 2, 2)
FRAME_PT2_BASE.fill_units(
    (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 113, 28, 10
)
FRAME_STRS.append(FRAME_PT2_BASE.get_string())
if beat_next:
    beat += 1
beat_next = not beat_next
FRAME_PT2_BASE.fill_style("""\
BB  BBBBBBBB  BBBBBBBB          BB  BBBBBBBB          BB  BB    BB
BB        BB  BB                BB  BB    BB          BB  BB    BB
BB        BB  BB                BB  BB    BB          BB  BB    BB
    BBBBBBBB  BBBBBBBB  BBBBBB  BB  BB    BB  BBBBBB  BB  BBBBBBBB
    BB              BB          BB  BB    BB          BB        BB
    BB              BB          BB  BB    BB          BB        BB
    BBBBBBBB  BBBBBBBB          BB  BBBBBBBB          BB        BB""", {
    "B": (None, 9)
}, 46, 14)
FRAME_PT2_BASE.fill_units(
    (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 113, 28, 10
)
FRAME_STRS.append(FRAME_PT2_BASE.get_string())
if beat_next:
    beat += 1
beat_next = not beat_next
FRAME_PT2_BASE.fill_style("""\
RR  RR  RRRRRRRR          RRRRRRRR  RRRRRRRR          RRRRRRRR  RRRRRRRR
RR  RR  RR                RR    RR        RR                RR  RR    RR
RR  RR  RR                RR    RR        RR                RR  RR    RR
    RR  RRRRRRRR  RRRRRR  RR    RR        RR  RRRRRR  RRRRRRRR  RRRRRRRR
    RR        RR          RR    RR        RR          RR              RR
    RR        RR          RR    RR        RR          RR              RR
    RR  RRRRRRRR          RRRRRRRR        RR          RRRRRRRR  RRRRRRRR""", {
    "R": (None, 9)
}, 46, 4)
FRAME_PT2_BASE.fill_units(
    (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 113, 28, 10
)
FRAME_STRS.append(FRAME_PT2_BASE.get_string())
if beat_next:
    beat += 1
beat_next = not beat_next
FRAME_PT2_BASE.fill_units(" "*69, 49, 24, 1)
FRAME_PT2_BASE.fill_units(" "*69, 49, 26, 1)
FRAME_PT2_BASE.fill_units(
    (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 113, 28, 10
)
FRAME_STRS.append(FRAME_PT2_BASE.get_string())
if beat_next:
    beat += 1
beat_next = not beat_next
PT2_LYRICS = ((
    "With", " mo", # BAR 8
    "", "dern", "", " fla", "", "ttened", "", " heart", # BAR 9
    "", " an", "d", " fa", "", "ce"
), (
    "You", "'re", # BAR 10
    " so", "me", "times", " me", "n", "tion", "", "ed a", # BAR 11
    "", "s a", "", " pa", "i", "n"
), (
    "Bu", "t you", # BAR 12
    "", " ke", "p", "t go", "", "ing", "", " u", # BAR 13
    "", "p an", "", "d rai", "se", "d"
), (
    "Fi", "nal", # BAR 14
    "ly", "", " you", " rea", "ch", "ed the", "", " pea", # BAR 15
    "", "k o", "f", " pla", "", "ce"
))
line_no = 6
line_head = 12
for line in PT2_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT2_BASE.fill_units(hbar, x, line_no, SHIAN_COLOR)
        x += len(hbar)
        FRAME_PT2_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT2_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
    line_no += 2
PT2_ANIMS = (
    (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (("|To|", 12, 6, 17, SHIAN_COLOR),), (("|be|", 12, 8, 17, SHIAN_COLOR),),
    (("|or|", 18, 10, 17, SHIAN_COLOR),),(("|not|", 24, 12, 17, SHIAN_COLOR),),
    (("|to|", 24, 6, 17, SHIAN_COLOR),), (("|be|", 24, 8, 17, SHIAN_COLOR),),
    (), (), (), (("|that's|", 36, 6, 17, SHIAN_COLOR),), 
    (("|the|", 36, 8, 17, SHIAN_COLOR),),
    (("|QUES    |", 36, 12, 17, SHIAN_COLOR),),
    (("TION", 41, 12, 17, SHIAN_COLOR),), (),
    (("                                    ", 12, 6, 9, 9),), (),
    (("                                    ", 12, 8, 9, 9),), (),
    (("                                ", 12, 10, 9, 9),), (),
)
for anims in PT2_ANIMS:
    for anim in anims:
        FRAME_PT2_BASE.fill_units(*anim)
    FRAME_PT2_BASE.fill_units(
        (str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)).rjust(5), 113, 28, 10
    )
    FRAME_STRS.append(FRAME_PT2_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next

# PT 3
FRAME_PT3_BASE = FRAME_BASE.copy()
PT3_LYRICS = ((
    ("Said", 1), (" tha", 1), ("t you", 0), (" would", 1),
    (" stay", 0), (" wi", 0), ("th us", 1), (" for", 1),
    ("e", 0), ("ver", 1), ("", 0), ("", 1), ("", 0), ("", 0), ("", 1), ("", 0),
    ("", 1), ("", 1), ("", 0)
), (
    ("Which", 0), (" made", 1), (" some", 1), ("bo", 0), ("dy", 0),
    (" dis", 1), ("gu", 0), ("", 1), ("st", 0), ("",1), ("",1), ("",1), ("",1)
), (
    ("Small", 0), (" pa", 0), ("tches", 1), (" and", 1),
    (" lar", 0), ("ge e", 0), ("quip", 1), ("men", 0),
    ("t a", 1), ("dde", 0), ("", 1), ("d", 0), ("", 1), ("",1), ("",1), ("",1),
    ("", 0)
), (
    ("Let", 0), (" peo", 1), ("ple", 1),
    (" ad", 0), ("mi", 0), ("re for", 1), (" hours", 1),
    (" and", 0), (" hou", 0), ("r", 1), ("s", 1), ("",0),("",0), ("",0), ("",0)
))
line_no = 6
line_head = 14
for line in PT3_LYRICS:
    x = line_head
    for hbar in line:
        if hbar[1]:
            FRAME_PT3_BASE.fill_units("    \n    ", 8, 9, 9, 12)
        else:
            FRAME_PT3_BASE.fill_units("    \n    ", 8, 9, 9, 9)
        FRAME_PT3_BASE.fill_units(hbar[0], x, line_no, LING_COLOR)
        x += len(hbar[0])
        FRAME_PT3_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT3_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
    line_no += 2

# PT 4
FRAME_PT4_BASE = FRAME_BASE.copy()
PT4_PH1_LYRICS = ((
    "", "", "", "", "", "", "", "So", # BAR 29
    " you", "", " reach", "", "ed the", "", " e", "", # BAR 30
    "dge o", "f", " de", "s", "k and", "", " ne", "ver", # BAR 31
    " went", " ba", "", "ck", "", "", ""
), (
    "The", # BAR 32
    " roa", "", "d you", "", " o", "pen", "ed u", "p" # BAR 33
), (
    "", "", "", "", "Ta", "", "ken", "", # BAR 34
    " ca", "re", " o", "f", " by", "", " you", "r", # BAR 35
    " da", "", "d and", "", " proud", "ly", "", "" # BAR 36
), (
    "", "", "In", "tro", "du", "ce", " wha", "", # BAR 37
    "t you", " were", "", "", "", "", ""
), (
    "And", # BAR 38
    " ne", "", "ver", "", " min", "ded", " there", "'s", # BAR 39
    " some", "", "one", " who", " ha", "", "te", "", # BAR 40
    "d you", "", "", "", "", "", ""
), (
    "You", # BAR 41
    " ju", "st", " wor", "k", " har", "d", " so", " e", # BAR 42
    "ven", "tual", "ly", "", "", ""
), (
    "You", " were", # BAR 43
    " mo", "re", " than", " a", " fame", "", " you", " were", # BAR 44
    " al", "so", " ou", "r", " lo", "ve", "", "" # BAR 45
))
PT4_PH1_ANIMS = (
    (), (), (), (), (), (), (), (), # BAR 29
    (("-"*118, 1, 16),), (), (("   1511\n2015-11-10", 4, 18, 1),), (),
    (("   1607\n2016-08-02", 16, 18, 2),), (),
    (("   1703\n2017-04-05", 28, 18, 3),), (), # BAR 30
    (("   1709\n2017-10-17", 40, 18, 4),), (),
    (("  HIG\n2018-01", 52, 18, 5),), (),
    (), (), (), (), # BAR 31
    (), (), (), (), (), (), (), (), # BAR 32
    (), (), (), (), (), (), (), (), # BAR 33
    (), (), (), (), (), (), (), (), # BAR 34
    (), (), (), (), (), (), (), (), # BAR 35
    (), (), (), (), (), (), (), (), # BAR 36
    (), (), (), (), (), (), (), (), # BAR 37
    (), (), (), (), (), (), (), (), # BAR 38
    (("   1803\n2018-04-30", 61, 18, 6),), (), (), (), (), (), (), (), # BAR 39
    (), (), (), (), (), (), (), (), # BAR 40
    (), (), (), (), (), (), (), (), # BAR 41
    (("   1809\n2018-10-02", 73, 18, 7),), (), (), (), (), (), (), (), # BAR 42
    (), (), (), (), (), (), (), (), # BAR 43
    (), (), (), (), (), (), (), (), # BAR 44
    (), (), (), (), (), (), (), (), # BAR 45
)
line_no = 5
line_head = 20
anim_i = 0
for line in PT4_PH1_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT4_BASE.fill_units(hbar, x, line_no, STARDUST_COLOR, LUO_COLOR)
        x += len(hbar)
        for anim in PT4_PH1_ANIMS[anim_i]:
            FRAME_PT4_BASE.fill_units(*anim)
        FRAME_PT4_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT4_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1
for i in range(7):
    for j in range(8):
        FRAME_PT4_BASE.fill_units("               ", j*15, i+5, 9, 10)
        FRAME_PT4_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT4_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
PT4_PH2_LYRICS = ((
    "U", "ni", "fi", "ed the", " sti", "ll and", " the", " dy", # BAR 53
    "na", "mi", "", "c", "", "", "", "", # BAR 54
    ""
), (
    "You", " brought", " the", " lid", "ding", " screens", " to", # BAR 55
    " a", " clo", "", "se", "", "", ""
), (
    "Co", # BAR 56
    "o", "pe", "ra", "tion", " with", " free", " and", " O", # BAR 57
    "S", "S", "", ""
), (
    "In", "no", "va", "te", # BAR 58
    "d the", " cur", "ren", "t of", " plat", "form", " ex", "chan", # BAR 59
    "ge a", "hea", "", "d", "", "", "", "" # BAR 60
))
PT4_PH2_ANIMS = (
    (), (), (), (), (), (), (), (), # BAR 53
    (), (), (), (), (), (), (), (), # BAR 54
    (), (), (), (), (), (), (), (), # BAR 55
    (), (), (), (), (), (), (), (), # BAR 56
    (("   1903\n2019-05-21", 85, 18, 10), ("a", 16, 8, STARDUST_COLOR)),
    (("p", 16, 8, STARDUST_COLOR),), (("t", 16, 8, STARDUST_COLOR),), (),
    ((" ", 16, 8, STARDUST_COLOR),), (("i", 16, 8, STARDUST_COLOR),),
    (("n", 16, 8, STARDUST_COLOR),), (), # BAR 57
    (("s", 16, 8, STARDUST_COLOR),), (("t", 16, 8, STARDUST_COLOR),),
    (("a", 16, 8, STARDUST_COLOR),), (("l", 16, 8, STARDUST_COLOR),),
    (), (), ((" ", 16, 8, STARDUST_COLOR),), (), # BAR 58
    ((" ", 16, 8, 9),), (), (), (), (), (), (), (), # BAR 59
    (), (), (), (), (), (), (), (), # BAR 60
)
line_no = 6
line_head = 20
anim_i = 0
for line in PT4_PH2_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT4_BASE.fill_units(hbar, x, line_no, LING_COLOR)
        x += len(hbar)
        for anim in PT4_PH2_ANIMS[anim_i]:
            FRAME_PT4_BASE.fill_units(*anim)
        FRAME_PT4_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT4_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1
PT4_PH3_LYRICS = ((
    "", "", "", "", "", "Now", " you", " see", # BAR 61
    "", "", "", "", "", "  I'd", " sta", "te", # BAR 62
    "", "d", "", "", "", "  the", " worl", "d o", # BAR 63
    "", "f", "", "", "", "  the", " pi", "eces", # BAR 64
    "", "", "", "", "", "  when", " I", " wa", # BAR 65
    "", "s", "", "", "", "  im", "merse", "d in", # BAR 66
    "", "", "", "", "", "  the", " e", "go", # BAR 67
    "", "", "", "", "", "  some", "thing's", " wrong", # BAR 68
    "", "", "", "", "", "  That", " ye", "ar", # BAR 69
), (
    "", "", "", "", "", "when", " I", " wa", # BAR 70
    "", "s", "", "", "", "  pre", "pa", "ring", # BAR 71
    "", "", "", "", "", "  my", " birth", "day", # BAR 72
    "", "", "", "", "", "  I", " read", " that", # BAR 73
    "", "", "", "", "", "  news", "pa", "per", # BAR 74
    "", "", "", "", "", "  I", " though", "t I", # BAR 75
    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "" # BAR 76, 77
))
PT4_PH3_ANIMS = (
    (), (), (), (), (), (), (), (), # BAR 61
    (), (), (), (), (), (), (),(("   1909\n2019-11-12", 97, 18, 11),), # BAR 62
    (), (), (), (), (), (), (), (), # BAR 63
    (), (), (), (), (), (), (),(("   2004\n2020-05-27",109, 18, 12),), # BAR 64
    (), (), (("PCs   ", 43, 11),), (), (("pieces", 43, 11),), (),
    (("PCs   ", 43, 11),), (), # BAR 65
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),),
    (("   20H2\n2020-10-20", 4, 21, 13),), # BAR 66
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 67
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 68
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 69
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 70
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 71
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),),
    (("   21H1\n2021-05-18", 16, 21, 14),), # BAR 72
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 73
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),),
    (('"WNFW Strike"\n 2021-06-24', 28, 21, 0, 17),), # BAR 74
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (),
    (("pieces", 43, 11),), (), (("PCs   ", 43, 11),), (), # BAR 75
    (("pieces", 43, 11),), (), ((" ", 43, 11),), (),
    ((" ", 45, 11),), (("  was", 71, 12, SHIAN_COLOR, STARDUST_COLOR),),
    ((" ", 47, 11), (" be", 76, 12, SHIAN_COLOR, STARDUST_COLOR)),
    (("tray", 79, 12, SHIAN_COLOR, STARDUST_COLOR),), # BAR 76
    ((" ", 44, 11),), (("ed", 83, 12, SHIAN_COLOR, STARDUST_COLOR),),
    ((" ", 48, 11),), (), ((" ", 46, 11),), (), (), (), # BAR 77
)
line_no = 11
line_head = 0
anim_i = 0
for line in PT4_PH3_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT4_BASE.fill_units(hbar, x, line_no, SHIAN_COLOR, 0)
        x += len(hbar)
        for anim in PT4_PH3_ANIMS[anim_i]:
            FRAME_PT4_BASE.fill_units(*anim)
        FRAME_PT4_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT4_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1

# PT 5
FRAME_PT5_BASE = FRAME_BASE.copy()
PT5_PH1_LYRICS = ((
    "", "", "", "Who", "e", "ver"
), ("you",), (
    "are", # BAR 78
    "", "", ""
), ("I",), ("brought",), ("you",), ("the",), (
    "lo", # BAR 79
    "", "ve"
), ("Like",), ("the",), ("ol", "der"), (
    "sis", "ter", # BAR 80,
    "", ""
), ("Born",), ("twelve",), ("ye", "ars"), (
    "a", "go", # BAR 81
    "", "", "", ""
))
line_no = 6
line_head = 0
for line in PT5_PH1_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT5_BASE.fill_units(hbar, x, line_no, LUO_COLOR, 0)
        x += len(hbar)
        FRAME_PT5_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT5_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1
PT5_PH2_LYRICS = ((
    "Re", "cei", "ving", " the", # BAR 82
    " co", "", "de of", " ten",
    (" I", " you"), (" was", " were"), " gi", "ven", # BAR 83
    " the", " pow", "er", "ful", " co", "", "re"
), (
    ("I", "You"), # BAR 84
    " re", "", "so", "", "na", "", "ted", "", # BAR 85
    " with", " the", " fe", "llow", " gee", "ks"
), (
    "Retrie", "ving", # BAR 86
    " thou", "", "san", "", "ds o", "", "f i", "ma", # BAR 87
    "ges", " pre", "ten", "ding", " to", ""
), (
    "Play", " trick", # BAR 88
    "s on", "", " I", "", "T", "", " fi", "", # BAR 89
    "lling", "", (" you", "  ou"), "r", " hear", "", "", "ts", # BAR 90
    "", ""
))
line_no = 8
line_head = 10
biline_lyrics = []
for line in PT5_PH2_LYRICS:
    biline_lyrics.append(("", ""))
    for hbar in line:
        lyrics = biline_lyrics[-1]
        if isinstance(hbar, tuple):
            biline_lyrics[-1] = lyrics[0] + hbar[0].center(
                max(len(hbar[0]), len(hbar[1]))
            ), lyrics[1] + hbar[1].center(max(len(hbar[0]), len(hbar[1])))
        else:
            biline_lyrics[-1] = lyrics[0] + hbar, lyrics[1] + hbar
        y = line_no
        for i in range(len(biline_lyrics)):
            lyrics = biline_lyrics[i]
            if beat & 1:
                FRAME_PT5_BASE.fill_units(lyrics[0], line_head, y, 7,LUO_COLOR)
                FRAME_PT5_BASE.fill_units(lyrics[1], line_head, y+1, 7,
                                          STARDUST_COLOR)
            else:
                FRAME_PT5_BASE.fill_units(lyrics[1], line_head, y, 7,
                                          STARDUST_COLOR)
                FRAME_PT5_BASE.fill_units(lyrics[0], line_head,y+1,7,LUO_COLOR)
            y += 3
        FRAME_PT5_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT5_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1

# PT 6
FRAME_PT6_BASE = FRAME_PT4_BASE.copy()
for i in range(16):
    FRAME_PT6_BASE.fill_units(" "*119, 0, i, 12, LING_COLOR)
PT6_PH1_LYRICS = ((
    "", "Ne", "ver", " gi", "ving", " u", # BAR 91
    "", "", "p and", " ne", "ver", " gi", "ven", " u", # BAR 92
    "", "p"
), (
    "You", " shape", "d your", "sel", "f and", " me", # BAR 93
    "", "", " wro", "tr a", " le", "gen", "da", "ry", # BAR 94
    "", "", ""
), (
    "Re", "call", "ing", " the", " wall", # BAR 95
    "", "", " a", "long", " with", " mul", "ti", "-spa", # BAR 96
    "", "ce"
), (
    "Di", "vi", "ding", " wha", "t is", " NEW", # BAR 97
    "", "", " ex", "plain", "ed TECH", "NO", "LO", "GY", # BAR 98
    "", "", "", "", "", "", "", "" # BAR 99
))
PT6_PH1_ANIMS = (
    (), (), (('   21H2\n2021-11-16', 43, 21, 15),), (), (), (), # BAR 91
    (), (), (), (), (), (), (), (), # BAR 92
    (), (), (), (), (), (), (), (), # BAR 93
    (), (), (), (), (), (), (), (), # BAR 94
    (), (), (), (), (), (), (), (), # BAR 95
    (), (), (), (), (), (), (), (), # BAR 96
    (), (), (), (), (), (), (), (), # BAR 97
    (('   22H2\n2022-10-18', 55, 21, 16),), (), (), (), (), (), (),(), # BAR 98
    (), (), (), (), (), (), (), () # BAR 99
)
line_no = 6
line_head = 35
anim_i = 0
for line in PT6_PH1_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT6_BASE.fill_units(hbar, x, line_no)
        x += len(hbar)
        for anim in PT6_PH1_ANIMS[anim_i]:
            FRAME_PT6_BASE.fill_units(*anim)
        FRAME_PT6_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT6_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1
for i in range(16):
    FRAME_PT6_BASE.fill_units(" "*60, 0, i, 10, 7)
    FRAME_PT6_BASE.fill_units(" "*59, 60, i, 9, 9)
PT6_PH2_ANIMS = (
    (("Windows NT 3.1  - 1993-?", 10, 2),), (), (), (), (), (),(),(), # BAR 100
    (("Windows NT 3.5  - 1994-?", 10, 3),), (), (), (), (), (),(),(), # BAR 101
    (("Windows NT 3.51 - 1995-?", 10, 4),), (), (), (), (), (),(),(), # BAR 102
    (("Windows NT 4.0  - 1996-2004", 10, 5),), (), (),(),(),(),(),(), # BAR 103
    (("Windows 2000    - 2000-2010", 10, 6),), (), (),(),(),(),(),(), # BAR 104
    (("Windows XP      - 2001-2014", 10, 7),), (), (),(),(),(),(),(), # BAR 105
    (("Windows Vista   - 2006-2017", 10, 8),), (), (),(),(),(),(),(), # BAR 106
    (("Windows 7       - 2009-2020", 10, 9),), (), (),(),(),(),(),(), # BAR 107
    (("Windows 8       - 2012-2016", 10, 10),), (),(),(),(),(),(),(), # BAR 108
    (("Windows 8.1     - 2013-2023", 10, 11),), (),(),(),(),(),(),(), # BAR 109
    (("Windows 10      - 2015-", 10, 12),), (), (), (),
    (("00:00 Dec 4,  2022", 81, 8),), (("00:41 Dec 8,  2022", 81, 8),),
    (("01:22 Dec 12, 2022", 81, 8),), (("02:03 Dec 16, 2022",81,8),), # BAR 110
    (("W", 10, 13, 11), ("02:44 Dec 20, 2022", 81, 8)),
    (("i", 11, 13, 11), ("03:25 Dec 24, 2022", 81, 8)),
    (("n", 12, 13, 11), ("04:06 Dec 28, 2022", 81, 8)),
    (("d", 13, 13, 11), ("04:47 Jan 1,  2023", 81, 8)),
    (("o", 14, 13, 11), ("05:28 Jan 5,  2023", 81, 8)),
    (("w", 15, 13, 11), ("06:09 Jan 9,  2023", 81, 8)),
    (("s", 16, 13, 11), ("06:50 Jan 13, 2023", 81, 8)),
    (("1", 18, 13, 11), ("07:31 Jan 17, 2023", 81, 8),), # BAR 111
    (("1", 19, 13, 11), ("08:12 Jan 21, 2023", 81, 8),),
    (("08:53 Jan 25, 2023", 81, 8),),
    (("-", 26, 13, 11), ("09:34 Jan 29, 2023", 81, 8)),
    (("2", 28, 13, 11), ("10:15 Feb 2,  2023", 81, 8)), 
    (("0", 29, 13, 11), ("10:56 Feb 6,  2023", 81, 8)),
    (("2", 30, 13, 11), ("11:37 Feb 10, 2023", 81, 8),),
    (("1", 31, 13, 11), ("12:18 Feb 14, 2023", 81, 8),),
    (("-", 32, 13, 11), ("12:59 Feb 18, 2023", 81, 8),), # BAR 112
    (("13:40 Feb 22, 2023", 81, 8),), (("14:20 Feb 26, 2023", 81, 8),),
    (("15:00 Mar 2,  2023", 81, 8),), (("15:39 Mar 6,  2023", 81, 8),),
    (("16:18 Mar 10, 2023", 81, 8),), (("16:56 Mar 14, 2023", 81, 8),),
    (("17:34 Mar 18, 2023", 81, 8),), (("18:11 Mar 22, 2023",81,8),), # BAR 113
    (("18:48 Mar 26, 2023", 81, 8),), (("19:24 Mar 30, 2023", 81, 8),),
    (("20:00 Apr 3,  2023", 81, 8),), (("20:35 Apr 7,  2023", 81, 8),),
    (("21:10 Apr 11, 2023", 81, 8),), (("21:44 Apr 15, 2023", 81, 8),),
    (("22:18 Apr 19, 2023", 81, 8),), (("22:51 Apr 23, 2023", 81,8),) # BAR 114
)
for anims in PT6_PH2_ANIMS:
    for anim in anims:
        FRAME_PT6_BASE.fill_units(*anim)
    FRAME_PT6_BASE.fill_units((
        str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
    ).rjust(5), 113, 28, 10)
    FRAME_STRS.append(FRAME_PT6_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
for i in range(16):
    FRAME_PT6_BASE.fill_units(" "*59, 60, i, SHIAN_COLOR, 13)
PT6_PH3_LYRICS = ((
    "Sche", "", "", "", "", "", "dule", "", # BAR 115
    "d to", "", "", "", " lea", "ve", " when", "", # BAR 116
    " ten", "", "", "", "", ""
), (
    "My", "", # BAR 117
    " li", "fe", "long", "'s", " ju", "s", "t a", "", # BAR 118
    " lie", "", "", "", "", "", "", "" # BAR 119
), (
    "Why", "", "", "", " I", "", "", "", # BAR 120
    " wa", "", "", "", "", "", "", "", # BAR 121
    "", "", "", "s", "", "", "", "", # BAR 122
    " so", "", "", "", "", "", " stu", "", # BAR 123
    "pi", "d"
), (
    "And", "", " now", "", "", "", # BAR 124
    " I", "", "", "", " cle", "", "ar", "", # BAR 125
    "ly", "", "", "", "", "", " know", "", # BAR 126
    "", "", "", "", " tha", "", "t I'm", "", # BAR 127
    " go", "", "ing", "", " to", "", " re", "", # BAR 128
    "ti", "", "", "", "", "", "re", "", # BAR 129
    " soon", "", "", "", "", "", "", "" # BAR 130
))
PT6_PH3_ANIMS = (
    (), (), (), (), (), (), (), (), (), (), (), (), (),(),(),(), # BAR 115, 116
    (("2025", 33, 12, 0),), (), (), (), (), (), (), (), # BAR 117
    (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    (), (), (), (), (), (), (), () # BAR 118~130
)
line_no = 6
line_head = 64
anim_i = 0
for line in PT6_PH3_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT6_BASE.fill_units(hbar, x, line_no)
        x += len(hbar)
        for anim in PT6_PH3_ANIMS[anim_i]:
            FRAME_PT6_BASE.fill_units(*anim)
        FRAME_PT6_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT6_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1
for i in range(16):
    FRAME_PT6_BASE.fill_units(" "*59, 60, i, 9, 9)
PT6_PH4_ANIMS = (
    ((" "*30, 30, 1, 9, 12),), ((" "*30, 0, 5, 9, 12),), ((" "*30, 0,1,9,12),),
    ((" "*30, 30, 0, 9, 12),), ((" "*30, 0, 13, 9, 12),),((" "*30,0,11,9,12),),
    ((" "*30, 0, 12, 9, 12),), ((" "*30, 30, 9, 9, 12),), # BAR 131
    ((" "*30, 30, 12, 9, 12),), ((" "*30, 0, 9, 9, 12),),((" "*30,30,5,9,12),),
    ((" "*30, 30, 14, 9, 12),), ((" "*30, 0, 2, 9, 12),), ((" "*30,0,8,9,12),),
    ((" "*30, 30, 4, 9, 12),), ((" "*30, 0, 4, 9, 12),), # BAR 132
    ((" "*30, 30, 13, 9, 12),), ((" "*30, 30, 2, 9,12),),((" "*30,30,6,9,12),),
    ((" "*30, 0, 14, 9, 12),), ((" "*30, 30, 10, 9,12),),((" "*30,0,10,9,12),),
    ((" "*30, 0, 3, 9, 12),), ((" "*30, 30, 7, 9, 12),), # BAR 133
    ((" "*30, 30, 15, 9, 12),), ((" "*30, 0, 0, 9, 12),), ((" "*30,0,6,9,12),),
    ((" "*30, 30, 11, 9, 12),), ((" "*30, 0, 7, 9, 12),),((" "*30,30,3,9,12),),
    ((" "*30, 0, 15, 9, 12),), ((" "*30, 30, 8, 9, 12),) # BAR 134
)
for anims in PT6_PH4_ANIMS:
    for anim in anims:
        FRAME_PT6_BASE.fill_units(*anim)
    FRAME_PT6_BASE.fill_units((
        str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
    ).rjust(5), 113, 28, 10)
    FRAME_STRS.append(FRAME_PT6_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
PT6_PH5_LYRICS = ((
    "Ta", "ke a", " va", "ca", "tion", ""
), (
    "And", " then", # BAR 135
    " vi", "", "si", "ting", " the mu", "se", "um", "" # BAR 136
), (
    "Fin", "ding", " that", " suc", "ce", "", "ssors", " di", # BAR 137
    "dn'", "t", " su", "c", "cee", "", "d al", "", # BAR 138
    "way", "s"
), (
    "How", "e", "ver", "", " they", "", # BAR 139
    " mean", "", " a", "", " lo", "", "t to", "", # BAR 140
    " al", "", "l of", " u", "s ahh", "", "", "" # BAR 141
), (
    "That's", " why", " they", "", " are", "", "", "" # BAR 142
))
line_no = 5
line_head = 6
anim_i = 0
for line in PT6_PH5_LYRICS:
    x = line_head
    for hbar in line:
        FRAME_PT6_BASE.fill_units(hbar, x, line_no, STARDUST_COLOR)
        x += len(hbar)
        FRAME_PT6_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT6_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 1
for i in range(16):
    FRAME_PT6_BASE.fill_units(" "*60, 0, i, 9, 6)
PT6_PH6_ANIMS = (
    (("08:00 Dec 15, 2023", 81, 8),), (("08 39 Dec 23, 2023", 81, 8),),
    (("09:18 Dec 31, 2023", 81, 8),), (("09 57 Jan 8,  2024", 81, 8),),
    (("10:36 Jan 16, 2024", 81, 8),), (("11 15 Jan 24, 2024", 81, 8),),
    (("11:54 Feb 1,  2024", 81, 8),), (("12 33 Feb 9,  2024", 81, 8),),
    (("13:12 Feb 17, 2024", 81, 8),), (("13 51 Feb 25, 2024", 81, 8),),
    (("14:30 Mar 4,  2024", 81, 8),), (("15 09 Mar 12, 2024", 81, 8),),
    (("15:48 Mar 20, 2024", 81, 8),), (("16 27 Mar 28, 2024", 81, 8),),
    (("17:06 Apr 5,  2024", 81, 8),), (("17 45 Apr 13, 2024", 81, 8),),
    (("18:24 Apr 21, 2024", 81, 8),), (("19 03 Apr 29, 2024", 81, 8),),
    (("19:42 May 7,  2024", 81, 8),), (("20 21 May 15, 2024", 81, 8),),
    (("21:00 May 23, 2024", 81, 8),), (("21 39 May 31, 2024", 81, 8),),
    (("22:18 Jun 8,  2024", 81, 8),), (("22 57 Jun 16, 2024", 81, 8),),
    (("23:36 Jun 24, 2024", 81, 8),), (("00 15 Jul 3,  2024", 81, 8),),
    (("00:54 Jul 11, 2024", 81, 8),), (("01 33 Jul 19, 2024", 81, 8),),
    (("02:12 Jul 27, 2024", 81, 8),), (("02 51 Aug 4,  2024", 81, 8),),
    (("03:30 Aug 12, 2024", 81, 8),), (("04 09 Aug 20, 2024", 81, 8),),
    (("04:48 Aug 28, 2024", 81, 8),), (("05 27 Sep 5,  2024", 81, 8),),
    (("06:06 Sep 13, 2024", 81, 8),), (("06 45 Sep 21, 2024", 81, 8),),
    (("07:24 Sep 29, 2024", 81, 8),), (("08 03 Oct 7,  2024", 81, 8),),
    (("08:42 Oct 15, 2024", 81, 8),), (("09 21 Oct 23, 2024", 81, 8),),
    (("10:00 Oct 31, 2024", 81, 8),), (("10 39 Nov 8,  2024", 81, 8),),
    (("11:18 Nov 16, 2024", 81, 8),), (("11 57 Nov 24, 2024", 81, 8),),
    (("12:36 Dec 2,  2024", 81, 8),), (("13 15 Dec 10, 2024", 81, 8),),
    (("13:54 Dec 18, 2024", 81, 8),), (("14 33 Dec 26, 2024", 81, 8),),
    (("15:12 Jan 3,  2025", 81, 8),), (("15 51 Jan 11, 2025", 81, 8),),
    (("16:30 Jan 19, 2025", 81, 8),), (("17 09 Jan 27, 2025", 81, 8),),
    (("17:48 Feb 4,  2025", 81, 8),), (("18 27 Feb 12, 2025", 81, 8),),
    (("19:06 Feb 20, 2025", 81, 8),), (("19 45 Feb 28, 2025", 81, 8),),
    (("20:24 Mar 8,  2025", 81, 8),), (("21 03 Mar 16, 2025", 81, 8),),
    (("21:42 Mar 24, 2025", 81, 8),), (("22 21 Apr 1,  2025", 81, 8),),
    (("23:00 Apr 9,  2025", 81, 8),), (("23 39 Apr 17, 2025", 81, 8),),
    (("00:18 Apr 26, 2025", 81, 8),), (("00 57 May 4,  2025", 81, 8),)
)
for anims in PT6_PH6_ANIMS:
    for anim in anims:
        FRAME_PT6_BASE.fill_units(*anim)
    FRAME_PT6_BASE.fill_units((
        str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
    ).rjust(5), 113, 28, 10)
    FRAME_STRS.append(FRAME_PT6_BASE.get_string())
    if beat_next:
        beat += 1
    beat_next = not beat_next
PT6_PH7_LYRICS = ((
    "Fi", "", "", "", "", "nal", "ly", " the", # BAR 151
    " clo", "", "ck go", "es", " ti", "ck", " ta", "ck", # BAR 152
    " to", "", "", "ck", "  The", "", " date", " comes" # BAR 153
), (
    "clo", "", "ser", "", " and", "", " clo", "", # BAR 154
    "ser", "", "", "", "  Af", "", "ter", " the", # BAR 155
    " la", "s", "t up", "da", ("te you", "te you", "te you", "te  I "), "",
    (" ha", " ha", " re", "  a"), ("d ", "ve", "ce", "pp"), # BAR 156
    ("arm", " go", "ive", "lie"), "", "", "", "", "", "",
    ("ed", "t ", "d ", "d "), # BAR 157
), (
    "", "", "", "", "", "", ("You", "You", "You", " My"),
    ("r", "r", "r", " "), # BAR 158
    " la", "", "", "s", "t de", "", "fe", "c", # BAR 159
    "t E", "", "VEN", "", "TU", "AL", "LY", "", # BAR 160
    (" flew", "   va", "   di", " turn"), "", "", "",
    ("   a", "nish", "sapp", "ed o"), "",
    ("way", "ed ", "ear", "ver"), "", # BAR 161
    ("    Thi", "    Thi", "ed  Thi", "    Thi"), "", "s i", "s", " wha", "t",
), (
    ("you", "you", "you", "  I"), ("'ll", "   ", "   ", "   "), # BAR 162
    (" be ", "were", "are ", "was "), "", "", "",
    ("from", " for", " for", "what"), "", (" no", "eve", "eve", " I "),
    "", # BAR 163
    ("w on", "r   ", "r   ", "am  "), "", "", "", "", "", "", "", # BAR 164
    "", "", "", "", "", "", "", "", # BAR 165
    ("", "   FO", "   FO", "WHAT "), "", "", "", "", ("", "RE", "RE", "I'"),
    ("", "V", "V", "L"), "", # BAR 166
    "", "", "", "", ("", "ER  ", "ER  ", "L BE"), "", "", "", # BAR 167
    "", "", "", "", "", "", "", "", # BAR 168
    "", "", "", "", "", "", "", "", "", "", "", ""
))
PT6_PH7_ANIMS = (
    (("01 13 May 6,  2025", 81, 8),), (("15:12 May 8,  2025", 81, 8),),
    (("05 11 May 11, 2025", 81, 8),), (("19:10 May 13, 2025", 81, 8),),
    (("09 09 May 16, 2025", 81, 8),), (("23:08 May 18, 2025", 81, 8),),
    (("13 07 May 21, 2025", 81, 8),), (("03:06 May 24, 2025", 81, 8),),
    (("17 05 May 26, 2025", 81, 8),), (("07:04 May 29, 2025", 81, 8),),
    (("21 03 May 31, 2025", 81, 8),), (("11:02 Jun 3,  2025", 81, 8),),
    (("01 01 Jun 6,  2025", 81, 8),), (("15:00 Jun 8,  2025", 81, 8),),
    (("04 59 Jun 11, 2025", 81, 8),), (("18:58 Jun 13, 2025", 81, 8),),
    (("08 57 Jun 16, 2025", 81, 8),), (("22:56 Jun 18, 2025", 81, 8),),
    (("12 55 Jun 21, 2025", 81, 8),), (("02:54 Jun 24, 2025", 81, 8),),
    (("16 53 Jun 26, 2025", 81, 8),), (("06:52 Jun 29, 2025", 81, 8),),
    (("20 51 Jul 1,  2025", 81, 8),), (("10:50 Jul 4,  2025", 81, 8),),
    (("00 49 Jul 7,  2025", 81, 8),), (("14:48 Jul 9,  2025", 81, 8),),
    (("04 47 Jul 12, 2025", 81, 8),), (("18:46 Jul 14, 2025", 81, 8),),
    (("08 45 Jul 17, 2025", 81, 8),), (("22:44 Jul 19, 2025", 81, 8),),
    (("12 43 Jul 22, 2025", 81, 8),), (("02:42 Jul 25, 2025", 81, 8),),
    (("16 41 Jul 27, 2025", 81, 8),), (("06:40 Jul 30, 2025", 81, 8),),
    (("20 39 Aug 1,  2025", 81, 8), ("TOP Drp.\n2025-07", 67, 21, 17)),
    (("10 38 Aug 4,  2025", 81, 8),),
    (("00 37 Aug 7,  2025", 81, 8),), (("14:36 Aug 9,  2025", 81, 8),),
    (("04 35 Aug 12, 2025", 81, 8),), (("18:34 Aug 14, 2025", 81, 8),),
    (("08 33 Aug 17, 2025", 81, 8),), (("22:32 Aug 19, 2025", 81, 8),),
    (("12 31 Aug 22, 2025", 81, 8),), (("02:30 Aug 25, 2025", 81, 8),),
    (("16 29 Aug 27, 2025", 81, 8),), (("06:28 Aug 30, 2025", 81, 8),),
    (("20 27 Sep 1,  2025", 81, 8),), (("10:26 Sep 4,  2025", 81, 8),),
    (("00 25 Sep 7,  2025", 81, 8),), (("14:24 Sep 9,  2025", 81, 8),),
    (("04 23 Sep 12, 2025", 81, 8),), (("18:22 Sep 14, 2025", 81, 8),),
    (("08 21 Sep 17, 2025", 81, 8),), (("22:20 Sep 19, 2025", 81, 8),),
    (("12 19 Sep 22, 2025", 81, 8),), (("02:18 Sep 25, 2025", 81, 8),), 
    (("05 20 Sep 26, 2025", 81, 8),), (("10:13 Sep 26, 2025", 81, 8),),
    (("15 06 Sep 26, 2025", 81, 8),), (("19:59 Sep 26, 2025", 81, 8),),
    (("00 52 Sep 27, 2025", 81, 8),), (("05:45 Sep 27, 2025", 81, 8),),
    (("10 38 Sep 27, 2025", 81, 8),), (("15:31 Sep 27, 2025", 81, 8),),
    (("20 24 Sep 27, 2025", 81, 8),), (("01:17 Sep 28, 2025", 81, 8),),
    (("06 10 Sep 28, 2025", 81, 8),), (("11:03 Sep 28, 2025", 81, 8),),
    (("15 56 Sep 28, 2025", 81, 8),), (("20:49 Sep 28, 2025", 81, 8),),
    (("01 42 Sep 29, 2025", 81, 8),), (("06:35 Sep 29, 2025", 81, 8),),
    (("11 28 Sep 29, 2025", 81, 8),), (("16:21 Sep 29, 2025", 81, 8),),
    (("21 14 Sep 29, 2025", 81, 8),), (("02:07 Sep 30, 2025", 81, 8),),
    (("07 00 Sep 30, 2025", 81, 8),), (("11:53 Sep 30, 2025", 81, 8),),
    (("16 46 Sep 30, 2025", 81, 8),), (("21:39 Sep 30, 2025", 81, 8),),
    (("02 32 Oct 1,  2025", 81, 8),), (("07:25 Oct 1,  2025", 81, 8),),
    (("12 18 Oct 1,  2025", 81, 8),), (("17:11 Oct 1,  2025", 81, 8),),
    (("22 04 Oct 1,  2025", 81, 8),), (("02:57 Oct 2,  2025", 81, 8),),
    (("07 50 Oct 2,  2025", 81, 8),), (("12:43 Oct 2,  2025", 81, 8),),
    (("17 36 Oct 2,  2025", 81, 8),), (("22:29 Oct 2,  2025", 81, 8),),
    (("03 22 Oct 3,  2025", 81, 8),), (("08:15 Oct 3,  2025", 81, 8),),
    (("13 08 Oct 3,  2025", 81, 8),), (("18:01 Oct 3,  2025", 81, 8),),
    (("22 54 Oct 3,  2025", 81, 8),), (("03:47 Oct 4,  2025", 81, 8),),
    (("08 40 Oct 4,  2025", 81, 8),), (("13:33 Oct 4,  2025", 81, 8),),
    (("18 26 Oct 4,  2025", 81, 8),), (("23:19 Oct 4,  2025", 81, 8),),
    (("04 12 Oct 5,  2025", 81, 8),), (("09:05 Oct 5,  2025", 81, 8),),
    (("13 58 Oct 5,  2025", 81, 8),), (("18:51 Oct 5,  2025", 81, 8),),
    (("23 44 Oct 5,  2025", 81, 8),), (("04:37 Oct 6,  2025", 81, 8),),
    (("09 30 Oct 6,  2025", 81, 8),), (("14:23 Oct 6,  2025", 81, 8),),
    (("19 16 Oct 6,  2025", 81, 8),), (("00:09 Oct 7,  2025", 81, 8),),
    (("05 02 Oct 7,  2025", 81, 8),), (("09:55 Oct 7,  2025", 81, 8),),
    (("14 48 Oct 7,  2025", 81, 8),), (("19:41 Oct 7,  2025", 81, 8),),
    (("00 34 Oct 8,  2025", 81, 8),), (("05:27 Oct 8,  2025", 81, 8),),
    (("10 20 Oct 8,  2025", 81, 8),), (("15:13 Oct 8,  2025", 81, 8),),
    (("20 06 Oct 8,  2025", 81, 8),), (("00:59 Oct 9,  2025", 81, 8),),
    (("05 52 Oct 9,  2025", 81, 8),), (("10:45 Oct 9,  2025", 81, 8),),
    (("15 38 Oct 9,  2025", 81, 8),), (("20:31 Oct 9,  2025", 81, 8),),
    (("01 24 Oct 10, 2025", 81, 8),), (("06:17 Oct 10, 2025", 81, 8),),
    (("11 10 Oct 10, 2025", 81, 8),), (("16:03 Oct 10, 2025", 81, 8),),
    (("20 56 Oct 10, 2025", 81, 8),), (("01:49 Oct 11, 2025", 81, 8),),
    (("06 42 Oct 11, 2025", 81, 8),), (("11:35 Oct 11, 2025", 81, 8),),
    (("16 28 Oct 11, 2025", 81, 8),), (("21:21 Oct 11, 2025", 81, 8),),
    (("02 14 Oct 12, 2025", 81, 8),), (("07:07 Oct 12, 2025", 81, 8),),
    (("12 00 Oct 12, 2025", 81, 8),), (("16:53 Oct 12, 2025", 81, 8),),
    (("21 46 Oct 12, 2025", 81, 8),), (("02:39 Oct 13, 2025", 81, 8),),
    (("07 32 Oct 13, 2025", 81, 8),), (("12:25 Oct 13, 2025", 81, 8),),
    (("17 18 Oct 13, 2025", 81, 8),), (("22:10 Oct 13, 2025",81,8),), # BAR 168
    ((" "*60, 0, x, 17, 6) for x in range(16)), (("Shutting down", 24, 8),),
    (("-", 30, 7),), (), (("\\", 30, 7),), (), (("|", 30, 7),), (),
    (("/", 30, 7),), (), ((" "*1190, 0, x, 9, 9) for x in range(16)),
    (("+----------+\n|   EOL    |\n|2025-10-14|\n+----------+", 76, 20, 10,7),)
)
line_no = 0
line_head = 4
anim_i = 0
for line in PT6_PH7_LYRICS:
    x = line_head
    for hbar in line:
        if isinstance(hbar, tuple):
            l = max(len(hbar[x]) for x in range(4))
            FRAME_PT6_BASE.fill_units(hbar[0].center(l), x, line_no,
                                      LUO_COLOR, 17)
            FRAME_PT6_BASE.fill_units(hbar[1].center(l), x, line_no+1,
                                      LING_COLOR, 0)
            FRAME_PT6_BASE.fill_units(hbar[2].center(l), x, line_no+2,
                                      STARDUST_COLOR, 17)
            FRAME_PT6_BASE.fill_units(hbar[3].center(l), x, line_no+3,
                                      SHIAN_COLOR, 0)
            x += l
        else:
            FRAME_PT6_BASE.fill_units(hbar, x, line_no, LUO_COLOR, 17)
            FRAME_PT6_BASE.fill_units(hbar, x, line_no+1, LING_COLOR, 0)
            FRAME_PT6_BASE.fill_units(hbar, x, line_no+2, STARDUST_COLOR, 17)
            FRAME_PT6_BASE.fill_units(hbar, x, line_no+3, SHIAN_COLOR, 0)
            x += len(hbar)
        for anim in PT6_PH7_ANIMS[anim_i]:
            FRAME_PT6_BASE.fill_units(*anim)
        FRAME_PT6_BASE.fill_units((
            str(((beat-1)>>2)+1)+"."+str(((beat-1)&3)+1)
        ).rjust(5), 113, 28, 10)
        FRAME_STRS.append(FRAME_PT6_BASE.get_string())
        if beat_next:
            beat += 1
        beat_next = not beat_next
        anim_i += 1
    line_no += 4
FRAME_PT6_BASE.fill_units("Fine.", 113, 28, 10)
FRAME_STRS.append(FRAME_PT6_BASE.get_string())

parser = argparse.ArgumentParser(
    prog="PV of Ten To Farewell",
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
PV of Ten To Farewell
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
