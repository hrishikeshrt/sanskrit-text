#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sanskrit Text Utility"""

###############################################################################

__author__ = """Hrishikesh Terdalkar"""
__email__ = "hrishikeshrt@linuxmail.org"
__version__ = "0.2.2"
__created_at__ = "Tue Apr 17 22:20:39 2018"

###############################################################################

import re
import logging

from collections import defaultdict
from itertools import product
from typing import Dict, List, Tuple

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################


def ord_unicode(ch: str) -> str:
    """Get Unicode 4-character-identifier corresponding to a character

    Parameters
    ----------
    ch : str
        Single character

    Returns
    -------
    str
        4-character unicode identifier
    """
    return hex(ord(ch)).split("x")[1].zfill(4)


def chr_unicode(u: str) -> str:
    """Get a Unicode character corresponding to 4-chracater identifier

    Parameters
    ----------
    u : str
        4-character unicode identifier

    Returns
    -------
    str
        Single character
    """

    return chr(int(u, 16))


###############################################################################

DESIGN = """
* len(SWARA) == len(MATRA) + 1  # 'अ' is extra at the beginning
* len(EXTENDED_SWARA) == len(EXTENDED_MATRA) + 1 # 'ऍ' is extra at the end
* It is unclear which of 'ॲ' or 'ऍ' should correspond to 'ॅ', current choice is
  the former. If that changes, the order in EXTENDED_MATRA would need to change
* ARTIFICIAL_MATRA contains absent vowel signs. Currently this is just for 'अ'.
  Any new sign should follow the pattern as hyphen ('-') followed by the vowel
  letter (e.g. '-अ').
* DIGITS, COMBINING_DIGIT_MARKS, PUNCTUATION and GENERAL_PUNCTUATION aren't
  part of the ALPHABET. Their inclusion needs more deliberation.
* VEDIC_MARKS are not used in syllabification functions currently.
"""

###############################################################################
# Alphabet of Sanskrit

SWARA = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ॠ", "ऌ", "ॡ", "ए", "ऐ", "ओ", "औ"]
EXTENDED_SWARA = ["ऎ", "ऒ", "ॲ", "ऑ", "ऍ"]

MATRA = ["ा", "ि", "ी", "ु", "ू", "ृ", "ॄ", "ॢ", "ॣ", "े", "ै", "ो", "ौ"]
EXTENDED_MATRA = ["ॆ", "ॊ", "ॅ", "ॉ"]

KANTHYA = ["क", "ख", "ग", "घ", "ङ"]
TALAVYA = ["च", "छ", "ज", "झ", "ञ"]
MURDHANYA = ["ट", "ठ", "ड", "ढ", "ण"]
DANTYA = ["त", "थ", "द", "ध", "न"]
AUSHTHYA = ["प", "फ", "ब", "भ", "म"]
ANTAHSTHA = ["य", "र", "ल", "व"]
USHMA = ["श", "ष", "स", "ह"]
VISHISHTA = ["ळ"]
EXTENDED_VYANJANA = ["ऩ", "ऱ", "ऴ", "क़", "ख़", "ग़", "ज़", "ड़", "ढ़", "फ़", "य़"]

# --------------------------------------------------------------------------- #

ARTIFICIAL_MATRA_A = f"-{SWARA[0]}"

OM = "ॐ"
AVAGRAHA = "ऽ"

SWARITA = "॑"
DOUBLE_SWARITA = "᳚"
TRIPLE_SWARITA = "᳛"
ANUDATTA = "॒"
CHANDRABINDU = "ँ"
CHANDRABINDU_VIRAMA = "ꣳ"
CHANDRABINDU_SPACING = "ꣲ"
CHANDABINDU_TWO = "ꣵ"
CHANDRABINDU_THREE = "ꣶ"

ANUSWARA = "ं"
VISARGA = "ः"
ARDHAVISARGA = "ᳲ"
JIHVAAMULIYA = "ᳵ"
UPADHMANIYA = "ᳶ"

HALANTA = "्"
NUKTA = "़"  # unused
ABBREV = "॰"
DANDA = "।"
DOUBLE_DANDA = "॥"

# --------------------------------------------------------------------------- #
# Groups

VARGIYA = KANTHYA + TALAVYA + MURDHANYA + DANTYA + AUSHTHYA
VYANJANA = VARGIYA + ANTAHSTHA + USHMA + VISHISHTA

VARGA_PRATHAMA = [VARGIYA[i * 5] for i in range(5)]
VARGA_DWITIYA = [VARGIYA[i * 5 + 1] for i in range(5)]
VARGA_TRITIYA = [VARGIYA[i * 5 + 2] for i in range(5)]
VARGA_CHATURTHA = [VARGIYA[i * 5 + 3] for i in range(5)]
VARGA_PANCHAMA = [VARGIYA[i * 5 + 4] for i in range(5)]

LAGHU_SWARA = [SWARA[i] for i in [0, 2, 4, 6, 8]] + EXTENDED_SWARA[:2]
LAGHU_MATRA = [MATRA[i] for i in [1, 3, 5, 7]] + EXTENDED_MATRA[:2]

# --------------------------------------------------------------------------- #

AYOGAVAAHA_COMMON = [CHANDRABINDU, ANUSWARA, VISARGA]
AYOGAVAAHA = AYOGAVAAHA_COMMON + [JIHVAAMULIYA, UPADHMANIYA]

VEDIC_MARKS = [SWARITA, ANUDATTA, DOUBLE_SWARITA, TRIPLE_SWARITA]
SPECIAL = [
    AVAGRAHA,
    OM,
    CHANDRABINDU_VIRAMA,
    CHANDRABINDU_SPACING,
    CHANDABINDU_TWO,
    CHANDRABINDU_THREE,
]
OTHER = [HALANTA]

# --------------------------------------------------------------------------- #

ARTIFICIAL_MATRA = [ARTIFICIAL_MATRA_A]

ALL_SWARA = SWARA + EXTENDED_SWARA
ALL_VYANJANA = VYANJANA + EXTENDED_VYANJANA
ALL_MATRA = MATRA + EXTENDED_MATRA  # does NOT contain ARTIFICIAL_MATRA

VARNA = ALL_SWARA + ALL_VYANJANA
ALPHABET = VARNA + ALL_MATRA + AYOGAVAAHA + SPECIAL + OTHER + VEDIC_MARKS

# --------------------------------------------------------------------------- #

SPACES = [" ", "\t", "\n", "\r"]
PUNCTUATION = [DANDA, DOUBLE_DANDA, ABBREV]
GENERAL_PUNCTUATION = [".", ",", ";", "", '"', "'", "`"]

DIGITS = ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"]
COMBINING_DIGIT_MARKS = ["꣠", "꣡", "꣢", "꣣", "꣤", "꣥", "꣦", "꣧", "꣨", "꣩"]

# --------------------------------------------------------------------------- #
# Special Sequences

KSHA = "क्ष"
JNA = "ज्ञ"

###############################################################################


HOW_TO_WRITE = """
Unicode characters chan be typed directly from the keyboard as follows,
[Ctrl+Shift+u] [4-digit-unicode-identifier] [space]

Some of the characters can also be typed using m17n-sanskrit-itrans keyboard
(Package: https://launchpad.net/ubuntu/+source/ibus-m17n)
(File: /usr/share/m17n/sa-itrans.mim)


Notable Unicodes and Shortcuts
---
1cf2 for Ardhavisarga
1cf5 for Jihvamuliya -- kH
1cf6 for Upadhmaniya -- pH
0951 for Swarita -- ''
0952 for Anudatta -- _
0901 for Chandrabindu -- .N
a8f2 for (stand-alone) Chandrabindu Spacing
093d for Avagraha -- .a
094d for Halanta -- .h

0950 for Om -- OM
a8e0 to a8e9 for Combining Devanagari Digits 0-9 (Swara Marks for Samaveda)
"""

###############################################################################

MAAHESHWARA_SUTRA = [
    ["अ", "इ", "उ", "ण्"],
    ["ऋ", "ऌ", "क्"],
    ["ए", "ओ", "ङ्"],
    ["ऐ", "औ", "च्"],
    ["ह", "य", "व", "र", "ट्"],
    ["ल", "ण्"],
    ["ञ", "म", "ङ", "ण", "न", "म्"],
    ["झ", "भ", "ञ्"],
    ["घ", "ढ", "ध", "ष्"],
    ["ज", "ब", "ग", "ड", "द", "श्"],
    ["ख", "फ", "छ", "ठ", "थ", "च", "ट", "त", "व्"],
    ["क", "प", "य्"],
    ["श", "ष", "स", "र्"],
    ["ह", "ल्"],
]

# --------------------------------------------------------------------------- #

MAAHESHWARA_KRAMA = [varna for sutra in MAAHESHWARA_SUTRA for varna in sutra]

# --------------------------------------------------------------------------- #

MAAHESHWARA_IDX = defaultdict(list)

idx = 0
for _sutra_idx, sutra in enumerate(MAAHESHWARA_SUTRA):
    for _internal_idx, varna in enumerate(sutra):
        if HALANTA in varna:
            _idx = -1
        else:
            _idx = idx
            idx += 1
        MAAHESHWARA_IDX[varna].append((_sutra_idx, _internal_idx, _idx))

###############################################################################


def form_pratyaahaara(letters: List[str]) -> str:
    """Form a pratyaahaara from a list of letters"""
    varna_idx = []
    ignored = []

    for varna in letters:
        if varna in MAAHESHWARA_IDX and HALANTA not in varna:
            varna_idx.append(MAAHESHWARA_IDX[varna])
        else:
            ignored.append(varna)

    if ignored:
        LOGGER.info(f"Ignored letters: {ignored}")

    varna_idxs = product(*varna_idx)
    for v_idx in varna_idxs:
        v_idx = sorted(v_idx, key=lambda x: x[2])
        _v_idx = [w[2] for w in v_idx]
        if _v_idx != list(range(_v_idx[0], _v_idx[-1] + 1)):
            continue
        else:
            break
    else:
        LOGGER.warning("Cannot form a pratyaahara due to discontinuity.")
        return None

    _aadi_idx = v_idx[0]
    _pre_antya_idx = v_idx[-1]

    if _pre_antya_idx[1] != len(MAAHESHWARA_SUTRA[_pre_antya_idx[0]]) - 2:
        LOGGER.warning("Cannot form a pratyaahara due to end position.")
        return None

    aadi = MAAHESHWARA_SUTRA[_aadi_idx[0]][_aadi_idx[1]]
    antya = MAAHESHWARA_SUTRA[_pre_antya_idx[0]][-1]
    return f"{aadi}{antya}"


def resolve_pratyaahaara(pratyaahaara: str) -> List[List[str]]:
    """Resolve pratyaahaara into all possible lists of characters"""
    aadi = pratyaahaara[0]
    antya = pratyaahaara[1:]

    possible_starts = []
    possible_ends = []

    for idx, varna in enumerate(MAAHESHWARA_KRAMA):
        if varna == aadi:
            possible_starts.append(idx)
        if varna == antya:
            possible_ends.append(idx)

    resolutions = [
        [
            MAAHESHWARA_KRAMA[idx]
            for idx in range(start, end)
            if HALANTA not in MAAHESHWARA_KRAMA[idx]
        ]
        for start in possible_starts
        for end in possible_ends
        if start < end
    ]
    return resolutions

###############################################################################


def clean(
    text: str,
    punct: bool = False,
    digits: bool = False,
    spaces: bool = True,
    allow: list = None,
) -> str:
    """Clean a line of Sanskrit (Devanagari) text

    Parameters
    ----------
    text : str
        Input string
    punct : bool, optional
        If True, the punctuations are kept.
        The default is False.
    digits : bool, optional
        If True, digits are kept.
        The default is False.
    spaces : bool, optional
        If False, spaces are removed.
        It is recommended to not change the default value
        unless it is specifically relevant to a use-case.
        The default is True.
    allow : list, optional
        List of characters to allow.
        The default is None.

    Returns
    -------
    str
        Clean version of the string
    """
    allow = allow or []
    alphabet = ALPHABET + allow
    if spaces:
        alphabet += SPACES
    if punct:
        alphabet += PUNCTUATION + GENERAL_PUNCTUATION
    if digits:
        alphabet += DIGITS
    answer = "".join(["" if c not in alphabet else c for c in text])
    answer = "\n".join(
        [" ".join(line.split()) for line in answer.split("\n") if line.strip()]
    )
    return answer


def split_lines(text: str, pattern=r"[।॥\r\n]+") -> List[str]:
    """Split a string into a list of strings using regular expression

    Parameters
    ----------
    text : str
        Input string
    pattern : regexp, optional
        Regular expression corresponding to the split points.
        The default is r'[।॥\r\n]+'.

    Returns
    -------
    List[str]
        List of strings
    """
    return list(filter(None, re.split(pattern, text)))


###############################################################################


def trim_matra(line: str) -> str:
    """Trim matra from the end of a string"""
    # TODO: If there is no general utility, consider removing this function.
    answer = line
    if line[-1] in [ANUSWARA, HALANTA, VISARGA]:
        answer = line[:-1]
    if answer[-1] in ALL_MATRA:
        answer = answer[:-1]
    return answer


###############################################################################


def is_laghu(syllable: str) -> bool:
    """Checks if the current syllable is Laghu"""

    return all(
        [
            (
                x in ALL_VYANJANA
                or x in LAGHU_SWARA
                or x in LAGHU_MATRA
                or x == HALANTA
            )
            for x in syllable
        ]
    )


def toggle_matra(syllable: str) -> str:
    """Change the Laghu syllable to Guru and Guru to Laghu (if possible)"""
    if syllable[-1] in MATRA:
        index = MATRA.index(syllable[-1])
        if index in [2, 4, 6, 8]:
            return syllable[:-1] + MATRA[index - 1]
        if index in [1, 3, 5, 7]:
            return syllable[:-1] + MATRA[index + 1]

    if syllable in SWARA:
        index = SWARA.index(syllable)
        if index in [0, 2, 4, 6, 8]:
            return SWARA[index + 1]
        if index in [1, 3, 5, 7, 9]:
            return SWARA[index - 1]


###############################################################################


def marker_to_swara(m: str) -> str:
    """Convert a Matra to corresponding Swara"""
    if m in ARTIFICIAL_MATRA:
        return m[1:]

    if m in MATRA:
        m_idx = MATRA.index(m)
        return SWARA[m_idx + 1]
    elif m in EXTENDED_MATRA:
        m_idx = EXTENDED_MATRA.index(m)
        return EXTENDED_SWARA[m]
    return None


def swara_to_marker(s: str) -> str:
    """Convert a Swara to correponding Matra"""
    if s == SWARA[0]:
        return f"-{s}"

    if s in SWARA:
        s_idx = SWARA.index(s)
        return MATRA[s_idx - 1]
    if s in EXTENDED_SWARA[:-1]:
        s_idx = EXTENDED_SWARA.index(s)
        return EXTENDED_MATRA[s_idx]
    return None


###############################################################################


def get_anunaasika(ch: str) -> str:
    """Get the appropriate anunaasika from the character's group"""
    MA = AUSHTHYA[4]
    if ch == "":
        return MA
    if ch in VYANJANA:
        i = VYANJANA.index(ch)
        if i < 25:
            return VYANJANA[int(i / 5) * 5 + 4]
        else:
            return ANUSWARA
    else:
        return ANUSWARA


def fix_anuswara(text: str) -> str:
    """
    Check every anuswaara in the text and change to anunaasika if applicable
    """
    output_chars = []
    if text:
        for idx in range(len(text) - 1):
            char = text[idx]
            next_char = text[idx + 1]
            if char == ANUSWARA and next_char in VARGIYA:
                anunasika = get_anunaasika(next_char)
                output_chars.append(anunasika)
                output_chars.append(HALANTA)
            else:
                output_chars.append(char)
        output_chars.append(text[-1])
    return "".join(output_chars)


###############################################################################


def get_syllables_word(word: str, technical: bool = False) -> List[str]:
    """Get syllables from a Sanskrit (Devanagari) word

    Parameters
    ----------
    word : str
        Sanskrit (Devanagari) word to get syllables from.
        Spaces, if present, are ignored.
    technical : bool, optional
        If True, ensures that each element contains at most
        one Swara or Vyanjana.
        The default is False.

    Returns
    -------
    List[str]
        List of syllables
    """
    word = clean(word, spaces=False)
    wlen = len(word)
    word_syllables = []

    current = ""
    i = 0
    while i < wlen:
        curr_ch = word[i]
        current += curr_ch
        i += 1
        # words split to start at START_CHARS
        start_chars = VARNA + SPECIAL
        if technical:
            start_chars += AYOGAVAAHA_COMMON
        while i < wlen and word[i] not in start_chars:
            current += word[i]
            i += 1
        if current[-1] != HALANTA or i == wlen or technical:
            word_syllables.append(current)
            current = ""
    return word_syllables


def get_syllables(text: str, technical: bool = False) -> List[List[List[str]]]:
    """Get syllables from a Sanskrit (Devanagari) text

    Parameters
    ----------
    text : str
        Sanskrit (Devanagari) text to get syllables from
    technical : bool, optional
        If True, ensures that each element contains at most
        one Swara or Vyanjana.
        The default is False.

    Returns
    -------
    List[List[List[str]]]
        List of syllables in a nested list format
        Nesting Levels: Text -> Lines -> Words
    """
    lines = split_lines(text.strip())
    syllables = []
    for line in lines:
        words = line.split()
        line_syllables = []
        for word in words:
            word_syllables = get_syllables_word(word, technical)
            line_syllables.append(word_syllables)
        syllables.append(line_syllables)
    return syllables


###############################################################################


def split_varna_word(word: str, technical: bool = True) -> List[str]:
    """Obtain the Varna decomposition of a Sanskrit (Devanagari) word

    Parameters
    ----------
    word : str
        Sanskrit (Devanagari) word to be split.
    technical : bool, optional
        If True, a split, vowels and vowel signs are treated independently
        which is more useful for analysis,
        The default is True.

    Returns
    -------
    List[str]
        List of Varna
    """
    word_syllables = get_syllables_word(word, True)
    word_viccheda = []
    for syllable in word_syllables:
        if syllable[0] in ALL_SWARA:
            word_viccheda.append(syllable[0])
            if len(syllable) > 1:
                word_viccheda.append(syllable[1])
            # TODO: Will this ever be the case?
            if len(syllable) > 2:
                LOGGER.warning(f"Long SWARA: {syllable}")
                word_viccheda.append(syllable[2:])
        elif syllable[0] in ALL_VYANJANA:
            word_viccheda.append(syllable[0] + HALANTA)
            if len(syllable) == 1:
                word_viccheda.append(ARTIFICIAL_MATRA_A)
            if len(syllable) > 1:
                if syllable[1] in AYOGAVAAHA_COMMON:
                    word_viccheda.append(ARTIFICIAL_MATRA_A)
                if syllable[1] != HALANTA:
                    word_viccheda.append(syllable[1])
            # TODO: Will this ever be the case?
            if len(syllable) > 2:
                LOGGER.warning(f"Long VYANJANA: {syllable}")
                word_viccheda.append(syllable[2:])
        else:
            word_viccheda.append(syllable)

    if not technical:
        real_word_viccheda = []
        for varna in word_viccheda:
            if varna in ARTIFICIAL_MATRA + ALL_MATRA:
                real_word_viccheda.append(marker_to_swara(varna))
            elif varna in AYOGAVAAHA_COMMON:
                real_word_viccheda[-1] += varna
            else:
                real_word_viccheda.append(varna)
        word_viccheda = real_word_viccheda
    return word_viccheda


def split_varna(
    text: str, technical: bool = True, flat: bool = False
) -> List[List[List[str]]] or List[str]:
    """Obtain the Varna decomposition of a Sanskrit (Devanagari) text

    Parameters
    ----------
    word : str
        Sanskrit (Devanagari) text to be split.
    technical : bool, optional
        If True, a split, vowels and vowel signs are treated independently
        which is more useful for analysis,
        The default is True.
    flat : bool, optional
        If True, a single list is returned instead of nested lists.
        The default is False.

    Returns
    -------
    List[List[List[str]]] or List[str]

        Varna decomposition of the text in a nested list format.
        Nesting Levels: Text -> Lines -> Words

        - Varna decomposition of each word is a List[char].
        - List of Varna decomposition of each word from a line.
        - List of Varna decomposition of each line from the text.

        If `flat=True`, Varna decomposition of the entire text is presented
        as a single list, also containing whitespace markers.
        Lines are separated by a newline character '\n' and words are
        separated by a space character ' '.
    """

    lines = split_lines(text.strip())
    viccheda = []
    num_lines = len(lines)
    for line_idx, line in enumerate(lines):
        words = line.split()
        line_viccheda = []
        num_words = len(words)
        for word_idx, word in enumerate(words):
            word_viccheda = split_varna_word(word, technical)
            if flat:
                line_viccheda.extend(word_viccheda)
                if word_idx != num_words - 1:
                    line_viccheda.append(" ")
            else:
                line_viccheda.append(word_viccheda)
        if flat:
            viccheda.extend(line_viccheda)
            if line_idx != num_lines - 1:
                viccheda.append("\n")
        else:
            viccheda.append(line_viccheda)
    return viccheda


def join_varna(viccheda: str, technical: bool = True) -> str:
    """
    Join Varna decomposition to form a Sanskrit (Devanagari) word

    Parameters
    ----------
    viccheda : list
        Viccheda output obtained by split_varna_word
        (or output of `split_varna` with `flat=True`)
    technical : bool
        Value of the same parameter passed to `split_varna_word`

    Returns
    -------
    s : str
        Sanskrit word
    """
    word = []
    i = 0
    while i < len(viccheda):
        curr_syl = viccheda[i]
        next_syl = ""
        if i < len(viccheda) - 1:
            next_syl = viccheda[i + 1]

        i += 1

        if curr_syl in [" ", "\n"]:
            word.append(curr_syl)
            continue

        if curr_syl[0] in ALL_SWARA + SPECIAL:
            word.append(curr_syl[0])
            if curr_syl[-1] in AYOGAVAAHA_COMMON:
                word.append(curr_syl[-1])
        if curr_syl[-1] == HALANTA:
            if next_syl in [" ", "\n"]:
                word.append(curr_syl)
                continue
            if next_syl == "":
                word.append(curr_syl)
                break
            if next_syl[-1] == HALANTA:
                word.append(curr_syl)
            if next_syl[0] in ALL_SWARA:
                i += 1
                word.append(curr_syl[:-1])
                if next_syl[0] != SWARA[0]:
                    word.append(marker_to_swara(next_syl[0]))
                if next_syl[-1] == VISARGA:
                    word.append(next_syl[-1])
            if next_syl in AYOGAVAAHA_COMMON:
                i += 1
                word.append(curr_syl[:-1] + next_syl)
            if next_syl in ARTIFICIAL_MATRA + ALL_MATRA:
                i += 1
                word.append(curr_syl[:-1])
                if next_syl != ARTIFICIAL_MATRA_A:
                    word.append(next_syl)
        if curr_syl in ARTIFICIAL_MATRA + ALL_MATRA + AYOGAVAAHA_COMMON:
            word.append(curr_syl)

    return "".join(word)


###############################################################################

###############################################################################
# Ucchaarana Sthaana Module
# ------------------------

STHAANA = {
    "S_K": ["अ", "आ"] + KANTHYA + ["ह"] + [VISARGA],
    "S_T": ["इ", "ई"] + TALAVYA + ["य", "श"],
    "S_M": ["ऋ", "ॠ"] + MURDHANYA + ["र", "ष"],
    "S_D": ["ऌ", "ॡ"] + DANTYA + ["ल", "स"],
    "S_O": ["उ", "ऊ"] + AUSHTHYA + [UPADHMANIYA],
    "S_N": VARGA_PANCHAMA + [ANUSWARA],
    "S_KT": ["ए", "ऐ"],
    "S_KO": ["ओ", "औ"],
    "S_DO": ["व"],
    "S_JM": [JIHVAAMULIYA],
}

STHAANA_NAMES = {
    "S_K": "कण्ठः",
    "S_T": "तालु",
    "S_M": "मूर्धा",
    "S_D": "दन्ताः",
    "S_O": "ओष्ठौ",
    "S_N": "नासिका",
    "S_KT": "कण्ठतालु",
    "S_KO": "कण्ठौष्ठम्",
    "S_DO": "दन्तौष्ठम्",
    "S_JM": "जिह्वामूलम्",
}

###############################################################################

AABHYANTARA = {
    "A_SP": VARGIYA,
    "A_ISP": ANTAHSTHA,
    "A_IVVT": USHMA + [JIHVAAMULIYA, UPADHMANIYA],
    "A_VVT": SWARA[1:] + [CHANDRABINDU, ANUSWARA, VISARGA],
    "A_SVT": SWARA[:1],
}

AABHYANTARA_NAMES = {
    "A_SP": "स्पृष्टः",
    "A_ISP": "ईषत्स्पृष्टः",
    "A_IVVT": "ईषद्विवृतः",
    "A_VVT": "विवृतः",
    "A_SVT": "संवृतः",
}

###############################################################################

BAAHYA = {
    "B_VVR": resolve_pratyaahaara("खर्")[0],
    "B_SVR": resolve_pratyaahaara("हश्")[0] + SWARA,
    "B_SW": resolve_pratyaahaara("खर्")[0],
    "B_ND": resolve_pratyaahaara("हश्")[0] + SWARA,
    "B_GH": resolve_pratyaahaara("हश्")[0] + SWARA,
    "B_AGH": resolve_pratyaahaara("खर्")[0],
    "B_AP": (
        VARGA_PRATHAMA
        + VARGA_TRITIYA
        + VARGA_PANCHAMA
        + resolve_pratyaahaara("यण्")[0]
    )
    + SWARA
    + [CHANDRABINDU, ANUSWARA],
    "B_MP": (VARGA_DWITIYA + VARGA_CHATURTHA + resolve_pratyaahaara("शल्")[0])
    + [VISARGA, JIHVAAMULIYA, UPADHMANIYA],
    "B_U": SWARA,
    "B_ANU": [s + ANUDATTA for s in SWARA],
    "B_SWA": [s + SWARITA for s in SWARA],
}

BAAHYA_NAMES = {
    "B_VVR": "विवारः",
    "B_SVR": "संवारः",
    "B_SW": "श्वासः",
    "B_ND": "नादः",
    "B_GH": "घोषः",
    "B_AGH": "अघोषः",
    "B_AP": "अल्पप्राणः",
    "B_MP": "महाप्राणः",
    "B_U": "उदात्तः",
    "B_ANU": "अनुदात्तः",
    "B_SWA": "स्वरितः",
}

###############################################################################

UCCHAARANA = dict(**STHAANA, **AABHYANTARA, **BAAHYA)
UCCHAARANA_NAMES = dict(**STHAANA_NAMES, **AABHYANTARA_NAMES, **BAAHYA_NAMES)

###############################################################################


def get_ucchaarana_vector(letter: str, abbrev=False) -> Dict[str, int]:
    """
    Get ucchaarana sthaana and prayatna based vector of a letter

    Parameters
    ----------
    letter : str
        Sanskrit letter
    abbrev : bool
        If True, the output will contain English abbreviations
        otherwise, the output will contain Sanskrit names.
        The default is False.

    Returns
    -------
    vector : Dict[str, int]
        One-hot vector indicating utpatti sthaana, aabhyantara prayatna and
        baahya prayatna of a letter
    """
    varna = letter.replace(HALANTA, "") if letter.endswith(HALANTA) else letter
    if abbrev:

        def ucchaarana_name(s):
            return s

    else:

        def ucchaarana_name(s):
            return UCCHAARANA_NAMES[s]

    vector = {ucchaarana_name(k): 0 for k in UCCHAARANA}
    for s, varna_list in UCCHAARANA.items():
        if varna in varna_list:
            vector[ucchaarana_name(s)] = 1

    return vector


def get_ucchaarana_vectors(
    word: str, abbrev: bool = False
) -> List[Tuple[str, Dict[str, int]]]:
    """
    Get ucchaarana sthaana and prayatna based vector of a word or text

    Parameters
    ----------
    word : str
        Sanskrit word (or text)
    abbrev : bool
        If True, the output will contain English abbreviations
        otherwise, the output will contain Sanskrit names.
        The default is False.

    Returns
    -------
    vectors : List[Tuple[str, Dict[str, int]]]
        List of (letter, vector)
    """
    letters = []
    for letter in split_varna_word(word, technical=False):
        if [v for v in AYOGAVAAHA_COMMON if v in letter]:
            letters.extend(letter)
        else:
            letters.append(letter)
    return [
        (letter, get_ucchaarana_vector(letter, abbrev)) for letter in letters
    ]


###############################################################################


def get_signature_letter(letter: str, abbrev: bool = False) -> Dict[str, str]:
    """
    Get ucchaarana sthaana and prayatna based signature of a letter

    Parameters
    ----------
    letter : str
        Sanskrit letter
    abbrev : bool
        If True, the output will contain English abbreviations
        otherwise, the output will contain Sanskrit names.
        The default is False.

    Returns
    -------
    signature : Dict[str, str]
        utpatti sthaana, aabhyantara prayatna and baahya prayatna of a letter
    """
    sthaana = get_ucchaarana_letter(letter, dimension=0, abbrev=abbrev)
    aabhyantara = get_ucchaarana_letter(letter, dimension=1, abbrev=abbrev)
    baahya = get_ucchaarana_letter(letter, dimension=2, abbrev=abbrev)

    signature = {
        "sthaana": sthaana,
        "aabhyantara": aabhyantara,
        "baahya": baahya,
    }
    return signature


def get_signature_word(
    word: str, abbrev: bool = False
) -> List[Tuple[str, Dict[str, str]]]:
    """
    Get ucchaarana sthaana and prayatna based signature of a word

    Parameters
    ----------
    word : str
        Sanskrit word (or text)
        Caution: If multiple words are provided,
        the spaces are not included in the output list.
    abbrev : bool
        If True, the output will contain English abbreviations
        otherwise, the output will contain Sanskrit names.
        The default is False.

    Returns
    -------
    List[Tuple[str, Dict[str, str]]]
        List of (letter, signature)

    """
    letters = []
    for letter in split_varna_word(word, technical=False):
        if [v for v in AYOGAVAAHA_COMMON if v in letter]:
            letters.extend(letter)
        else:
            letters.append(letter)
    return [
        (letter, get_signature_letter(letter, abbrev)) for letter in letters
    ]


def get_signature(
    text: str, abbrev: bool = False
) -> List[List[List[Tuple[str, Dict[str, str]]]]]:
    """
    Get ucchaarana list of a Sanskrit text

    Parameters
    ----------
    text : str
        Sanskrit text (can contain newlines, spaces)
    abbrev : bool
        If True, the output will contain English abbreviations
        otherwise, the output will contain Sanskrit names.
        The default is False.

    Returns
    -------
    List[List[List[Tuple[str, Dict[str, str]]]]]
        List of (letter, signature) for words in a nested list format
        Nesting Levels: Text -> Lines -> Words
    """
    lines = split_lines(text.strip())
    signature = []
    for line in lines:
        words = line.split()
        line_signature = []
        for word in words:
            word_signature = get_signature_word(word, abbrev)
            line_signature.append(word_signature)
        signature.append(line_signature)
    return signature


###############################################################################


def get_ucchaarana_letter(
    letter: str, dimension: int = 0, abbrev: bool = False
) -> str:
    """
    Get ucchaarana sthaana or prayatna of a letter

    Parameters
    ----------
    letter : str
        Sanskrit letter
    dimension : int
        0 : sthaana
        1 : aabhyantara prayatna
        2 : baahya prayatna
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Sanskrit names
        The default is False.

    Returns
    -------
    str
        ucchaarana sthaana or prayatna of a letter

    """
    varna = letter.replace(HALANTA, "") if letter.endswith(HALANTA) else letter
    ucchaarana = []
    _UCCHAARANA = [STHAANA, AABHYANTARA, BAAHYA]
    _NAMES = [STHAANA_NAMES, AABHYANTARA_NAMES, BAAHYA_NAMES]

    if abbrev:

        def ucchaarana_name(s):
            return s

        join_str = "-"
    else:

        def ucchaarana_name(s):
            return _NAMES[dimension][s]

        join_str = " "

    for s, varna_list in _UCCHAARANA[dimension].items():
        if varna in varna_list:
            ucchaarana.append(ucchaarana_name(s))

    if len(ucchaarana) > 1 and not abbrev:
        ucchaarana.append("च")

    return join_str.join(ucchaarana)


def get_ucchaarana_word(
    word: str, dimension: int = 0, abbrev: bool = False
) -> List[Tuple[str, str]]:
    """
    Get ucchaarana of a word

    Parameters
    ----------
    word : str
        Sanskrit word (or text)
        Caution:
            If multiple words are provided, the spaces are not included in
            the output list
    dimension : int
        0 : sthaana
        1 : aabhyantara prayatna
        2 : baahya prayatna
        The default is 0.
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Sanskrit names
        The default is False.
    Returns
    -------
    List[Tuple[str, str]]
        List of (letter, ucchaarana)

    """
    letters = []
    for letter in split_varna_word(word, technical=False):
        if [v for v in AYOGAVAAHA_COMMON if v in letter]:
            letters.extend(letter)
        else:
            letters.append(letter)
    return [
        (letter, get_ucchaarana_letter(letter, dimension, abbrev))
        for letter in letters
    ]


def get_ucchaarana(
    text: str, dimension: int = 0, abbrev: bool = False
) -> List[List[List[Tuple[str, str]]]]:
    """
    Get ucchaarana list of a Sanskrit text

    Parameters
    ----------
    text : str
        Sanskrit text (can contain newlines, spaces)
    dimension : int
        0 : sthaana
        1 : aabhyantara prayatna
        2 : baahya prayatna
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Sanskrit names
        The default is False.
    Returns
    -------
    List[List[List[Tuple[str, str]]]]
        List of (letter, ucchaarana) for words in a nested list format
        Nesting Levels: Text -> Lines -> Words
    """
    lines = split_lines(text.strip())
    ucchaarana = []
    for line in lines:
        words = line.split()
        line_ucchaarana = []
        for word in words:
            word_ucchaarana = get_ucchaarana_word(word, dimension, abbrev)
            line_ucchaarana.append(word_ucchaarana)
        ucchaarana.append(line_ucchaarana)
    return ucchaarana


###############################################################################


def get_sthaana_letter(letter: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana_letter for sthaana"""
    return get_ucchaarana_letter(letter, dimension=0, abbrev=abbrev)


def get_sthaana_word(word: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana_word for sthaana"""
    return get_ucchaarana_word(word, dimension=0, abbrev=abbrev)


def get_sthaana(text: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana for sthaana"""
    return get_ucchaarana(text, dimension=0, abbrev=abbrev)


# --------------------------------------------------------------------------- #


def get_aabhyantara_letter(letter: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana_letter for aabhyantara"""
    return get_ucchaarana_letter(letter, dimension=1, abbrev=abbrev)


def get_aabhyantara_word(word: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana_word for aabhyantara"""
    return get_ucchaarana_word(word, dimension=1, abbrev=abbrev)


def get_aabhyantara(text: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana for aabhyantara"""
    return get_ucchaarana(text, dimension=1, abbrev=abbrev)


# --------------------------------------------------------------------------- #


def get_baahya_letter(letter: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana_letter for baahya"""
    return get_ucchaarana_letter(letter, dimension=2, abbrev=abbrev)


def get_baahya_word(word: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana_word for baahya"""
    return get_ucchaarana_word(word, dimension=2, abbrev=abbrev)


def get_baahya(text: str, abbrev: bool = False):
    """Wrapper for get_ucchaarana for baahya"""
    return get_ucchaarana(text, dimension=2, abbrev=abbrev)


###############################################################################
