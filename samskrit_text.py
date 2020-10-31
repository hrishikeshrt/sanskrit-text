#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 22:20:39 2018
Updated on Thu Oct 31 23:43:34 2020

@author: Hrishikesh Terdalkar
"""

import re
import warnings

###############################################################################


def ord_unicode(ch):
    return hex(ord(ch)).split('x')[1].zfill(4)


def chr_unicode(u):
    return chr(int(u, 16))


###############################################################################
# Alphabet of samskRta

MATRA = ['ा', 'ि', 'ी', 'ु',  'ू', 'ृ', 'ॄ', 'ॢ', 'ॣ', 'े', 'ै', 'ो', 'ौ', ]
SWARA = ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ॠ', 'ऌ', 'ॡ', 'ए', 'ऐ', 'ओ', 'औ']
KANTHYA = ['क', 'ख', 'ग', 'घ', 'ङ']
TALAVYA = ['च', 'छ', 'ज', 'झ', 'ञ']
MURDHANYA = ['ट', 'ठ', 'ड', 'ढ', 'ण']
DANTYA = ['त', 'थ', 'द', 'ध', 'न']
AUSHTHYA = ['प', 'फ', 'ब', 'भ', 'म']
ANTAHSTHA = ['य', 'र', 'ल', 'व']
USHMA = ['श', 'ष', 'स', 'ह']
VISHISHTA = ['ळ', 'ऱ']

VARGIYA = KANTHYA + TALAVYA + MURDHANYA + DANTYA + AUSHTHYA
VYANJANA = VARGIYA + ANTAHSTHA + USHMA + VISHISHTA

VARGA_PRATHAMA = [VARGIYA[i * 5] for i in range(5)]
VARGA_DWITIYA = [VARGIYA[i * 5 + 1] for i in range(5)]
VARGA_TRITIYA = [VARGIYA[i * 5 + 2] for i in range(5)]
VARGA_CHATURTHA = [VARGIYA[i * 5 + 3] for i in range(5)]
VARGA_PANCHAMA = [VARGIYA[i * 5 + 4] for i in range(5)]

OM = 'ॐ'
AVAGRAHA = 'ऽ'

SWARITA = '॑'
ANUDATTA = '॒'

CHANDRABINDU = 'ँ'
CHANDRABINDU_VIRAMA = 'ꣳ'
CHANDRABINDU_SPACING = 'ꣲ'

ANUSWARA = 'ं'
VISARGA = 'ः'
JIHVAAMULIYA = 'ᳵ'
UPADHMANIYA = 'ᳶ'

HALANTA = '्'
NUKTA = '़'
ABBREV = '॰'
DANDA = '।'
DOUBLE_DANDA = '॥'


EXTRA_MATRA = [CHANDRABINDU, ANUSWARA, VISARGA]
AYOGAVAAHA = EXTRA_MATRA + [JIHVAAMULIYA, UPADHMANIYA]

VEDIC_MATRA = [SWARITA, ANUDATTA]
SPECIAL = [AVAGRAHA, OM, NUKTA, CHANDRABINDU_VIRAMA, CHANDRABINDU_SPACING]
OTHER = [HALANTA]

VARNA = SWARA + VYANJANA
ALPHABET = VARNA + MATRA + AYOGAVAAHA + SPECIAL + OTHER + VEDIC_MATRA

SPACES = [' ', '\t', '\n', '\r']
PUNC = [DANDA, DOUBLE_DANDA, ABBREV]
GEN_PUNC = ['.', ',', ';', '', '"', "'", '`']

DIGITS = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९']

KSHA = 'क्ष'
JNA = 'ज्ञ'

###############################################################################


HOW_TO_WRITE = """
Unicode characters chan be typed directly from the keyboard as follows,
[Ctrl+Shift+u] [4-digit-unicode-identifier] [space]

Some of the characters can also be typed using m17n-sanskrit-itrans keyboard
(Package: https://launchpad.net/ubuntu/+source/ibus-m17n)
(File: /usr/share/m17n/sa-itrans.mim)


Notable Unicodes and Shortcuts
---
1cf6 for Upadhmaniya (ardhavisarga) -- pH
1cf2 for Jihvamuliya (ardhavisarga) -- kH
0951 for Swarita -- ''
0952 for Anudatta -- _
0901 for Chandrabindu -- .N
a8f2 for (stand-alone) Chandrabindu Spacing
093d for Avagraha -- .a
094d for Halanta -- .h

0950 for Om -- OM
a8e0 to a8e9 for Superscript 0-9
"""

###############################################################################

MAAHESHWARA_SUTRA = [
    ['अ', 'इ', 'उ', 'ण्'],
    ['ऋ', 'ऌ', 'क्'],
    ['ए', 'ओ', 'ङ्'],
    ['ऐ', 'औ', 'च्'],
    ['ह', 'य', 'व', 'र', 'ट्'],
    ['ल', 'ण्'],
    ['ञ', 'म', 'ङ', 'ण', 'न', 'म्'],
    ['झ', 'भ', 'ञ्'],
    ['घ', 'ढ', 'ध', 'ष्'],
    ['ज', 'ब', 'ग', 'ड', 'द', 'श्'],
    ['ख', 'फ', 'छ', 'ठ', 'थ', 'च', 'ट', 'त', 'व्'],
    ['क', 'प', 'य्'],
    ['श', 'ष', 'स', 'र्'],
    ['ह', 'ल्']
]

MAAHESHWARA_KRAMA = [varna for sutra in MAAHESHWARA_SUTRA for varna in sutra]

###############################################################################


def form_pratyaahaara(letters):
    varna_idx = []
    list_idx = []
    subtract = 0

    for idx, varna in enumerate(MAAHESHWARA_KRAMA):
        if HALANTA in varna:
            subtract += 1

        if varna in letters:
            varna_idx.append(idx - subtract)
            list_idx.append(idx)

    # if not consecutive None
    varna_idx = sorted(varna_idx)
    if varna_idx != list(range(varna_idx[0], varna_idx[-1] + 1)):
        warnings.warn("Cannot form a pratyaahara due to discontinuity.")
        return None

    if HALANTA not in MAAHESHWARA_KRAMA[list_idx[-1] + 1]:
        warnings.warn("Cannot form a pratyaahara due to end position.")
        return None

    aadi = MAAHESHWARA_KRAMA[list_idx[0]]
    antya = MAAHESHWARA_KRAMA[list_idx[-1] + 1]
    return f'{aadi}{antya}'


def resolve_pratyaahaara(pratyaahaara):
    aadi = pratyaahaara[0]
    antya = pratyaahaara[1:]

    possible_starts = []
    possible_ends = []

    for idx, varna in enumerate(MAAHESHWARA_KRAMA):
        if varna == aadi:
            possible_starts.append(idx)

    for idx, varna in enumerate(MAAHESHWARA_KRAMA):
        if varna == antya:
            possible_ends.append(idx)

    resolutions = [
        [MAAHESHWARA_KRAMA[idx]
         for idx in range(start, end)
         if HALANTA not in MAAHESHWARA_KRAMA[idx]]
        for start in possible_starts
        for end in possible_ends
        if start < end
    ]
    return resolutions

###############################################################################


def clean(text, punct=False, digits=False, spaces=True, allow=[]):
    '''
    Clean a line of samskRta text
        - punct: False (True means punctuations are kept)
        - digits: False (True means digits are kept)
        - spaces: True (we usually don't want to change this)
        - allow: list of characters to allow
    '''
    alphabet = ALPHABET + allow
    if spaces:
        alphabet += SPACES
    if punct:
        alphabet += PUNC + GEN_PUNC
    if digits:
        alphabet += DIGITS
    answer = ''.join(['' if c not in alphabet else c for c in text])
    answer = '\n'.join([' '.join(line.split())
                        for line in answer.split('\n') if line.strip()])
    return answer


def split_lines(text, pattern=r'[।॥\r\n]+'):
    return list(filter(None, re.split(pattern, text)))


def trim_matra(line):
    answer = line
    if line[-1] in [ANUSWARA, HALANTA, VISARGA]:
        answer = line[:-1]
    if answer[-1] in MATRA:
        answer = answer[:-1]
    return answer


###############################################################################


def matra_to_swara(m):
    """
    Convert the Matra to corresponding Swara
    """
    if m == '':
        return SWARA[0]

    try:
        m_idx = MATRA.index(m)
    except Exception:
        return None
    return SWARA[m_idx + 1]


def swara_to_matra(s):
    '''
    Convert a Swara to correponding Matra
    '''
    if s == SWARA[0]:
        return ''
    try:
        s_idx = SWARA.index(s)
    except Exception:
        return None
    return MATRA[s_idx - 1]

###############################################################################


def get_anunasik(ch):
    """
    Get appropriate anunasik from the character's group
    """
    MA = AUSHTHYA[4]
    if ch == '':
        return MA
    if ch in VYANJANA:
        i = VYANJANA.index(ch)
        if i < 25:
            return VYANJANA[int(i/5) * 5 + 4]
        else:
            return ANUSWARA
    else:
        return ANUSWARA


def fix_anuswara(text):
    output_chars = []
    if text:
        for idx in range(len(text) - 1):
            char = text[idx]
            next_char = text[idx + 1]
            if char == ANUSWARA and next_char in VARGIYA:
                anunasika = get_anunasik(next_char)
                output_chars.append(anunasika)
                output_chars.append(HALANTA)
            else:
                output_chars.append(char)
        output_chars.append(text[-1])
    return ''.join(output_chars)

###############################################################################


def get_syllables_word(word, technical=False):
    """
    Get syllables from a Samskrit word
    @params:
        word: word to get syllables from
        technical: (boolean)
                    if True, ensures that each element contains at most
                    one Swara or Vyanjana
    """
    word = clean(word, spaces=False)
    wlen = len(word)
    word_syllables = []

    current = ''
    i = 0
    while i < wlen:
        curr_ch = word[i]
        current += curr_ch
        i += 1
        # words split to start at START_CHARS
        start_chars = VARNA + SPECIAL
        if technical:
            start_chars += EXTRA_MATRA
        while i < wlen and word[i] not in start_chars:
            current += word[i]
            i += 1
        if current[-1] != HALANTA or i == wlen or technical:
            word_syllables.append(current)
            current = ''
    return word_syllables


def get_syllables(text, technical=False):
    """
    Get syllables from a Samskrit text
    @params:
        word: word to get syllables from
        technical: (boolean)
                    if True, ensures that each element contains at most
                    one Swara or Vyanjana
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


def split_varna_word(word, technical=True):
    """
    Give a Varna decomposition of a Samskrit word
    @params:
        word: word to be split
        technical: (boolean)
                    if True would give split more useful for analysis
    @return:
        viccheda: list of list of lists
            Viccheda of each word is a list.
            - List of Viccheda of each word from a line
            - List of Viccheda of each line from the text
    """
    word_syllables = get_syllables_word(word, True)
    word_viccheda = []
    for syllable in word_syllables:
        if syllable[0] in SWARA:
            word_viccheda.append(syllable[0])
            if len(syllable) > 1:
                word_viccheda.append(syllable[1])
            if len(syllable) > 2:
                word_viccheda.append(syllable[2:])
        elif syllable[0] in VYANJANA:
            word_viccheda.append(syllable[0] + HALANTA)
            if len(syllable) == 1:
                word_viccheda.append('-' + SWARA[0])
            if len(syllable) > 1:
                if syllable[1] in EXTRA_MATRA:
                    word_viccheda.append('-' + SWARA[0])
                if syllable[1] != HALANTA:
                    word_viccheda.append(syllable[1])
            if len(syllable) > 2:
                word_viccheda.append(syllable[2:])
        else:
            word_viccheda.append(syllable)

    if not technical:
        real_word_viccheda = []
        for i in range(len(word_viccheda)):
            if word_viccheda[i] in MATRA:
                m_idx = MATRA.index(word_viccheda[i])
                real_word_viccheda.append(SWARA[m_idx + 1])
            elif word_viccheda[i] == '-' + SWARA[0]:
                real_word_viccheda.append(word_viccheda[i][1])
            elif word_viccheda[i] in [CHANDRABINDU, ANUSWARA]:
                next_ch = ''
                if i < len(word_viccheda) - 1:
                    next_ch = word_viccheda[i+1][0]
                nasal = get_anunasik(next_ch)
                if nasal != ANUSWARA:
                    nasal += HALANTA
                real_word_viccheda.append(nasal)
            elif word_viccheda[i] == VISARGA:
                real_word_viccheda[-1] += VISARGA
            else:
                real_word_viccheda.append(word_viccheda[i])
        word_viccheda = real_word_viccheda
    return word_viccheda


def split_varna(text, technical=True):
    """
    Give a Varna decomposition of a Samskrit text
    @params:
        text: text to be split
        technical: (boolean)
                    if True would give split more useful for analysis
    @return:
        viccheda: list of list of lists
            Viccheda of each word is a list.
            - List of Viccheda of each word from a line
            - List of Viccheda of each line from the text
    """

    lines = split_lines(text.strip())
    viccheda = []
    for line in lines:
        words = line.split()
        line_viccheda = []
        for word in words:
            word_viccheda = split_varna_word(word, technical)
            line_viccheda.append(word_viccheda)
        viccheda.append(line_viccheda)
    return viccheda


def join_varna(viccheda, technical=False):
    """
    Join Varna decomposition to form a Samskrit word

    Parameters
    ----------
    viccheda : list
        Viccheda output obtained by split_varna_word
    technical : bool
        Value of the same parameter passed to split_varna_word

    Returns
    -------
    s : str
        Samskrit word
    """
    word = []
    i = 0
    while i < len(viccheda):
        curr_syl = viccheda[i]
        next_syl = ''
        if i < len(viccheda) - 1:
            next_syl = viccheda[i+1]
        i += 1
        if curr_syl[0] in SWARA + SPECIAL:
            word.append(curr_syl[0])
            if curr_syl[-1] == VISARGA:
                word.append(curr_syl[-1])
        if curr_syl[-1] == HALANTA:
            if next_syl == '':
                word.append(curr_syl)
                break
            if next_syl[-1] == HALANTA:
                word.append(curr_syl)
            if next_syl[0] in SWARA:
                i += 1
                word.append(curr_syl[:-1])
                if next_syl[0] != SWARA[0]:
                    s_idx = SWARA.index(next_syl[0])
                    matra = MATRA[s_idx - 1]
                    word.append(matra)
                if next_syl[-1] == VISARGA:
                    word.append(next_syl[-1])
            if next_syl in EXTRA_MATRA:
                i += 1
                word.append(curr_syl[:-1] + next_syl)
            if next_syl in MATRA + ['-अ']:
                i += 1
                word.append(curr_syl[:-1])
                if next_syl != '-अ':
                    word.append(next_syl)
        if curr_syl in MATRA + ['-अ'] + EXTRA_MATRA:
            word.append(curr_syl)

    return ''.join(word)

###############################################################################

###############################################################################
# Uccharana Sthaana Module
# ------------------------


STHAANA_NAMES = {
    'K': 'कण्ठः',
    'T': 'तालु',
    'M': 'मूर्धा',
    'D': 'दन्ताः',
    'O': 'ओष्ठौ',
    'N': 'नासिका',
    'KT': 'कण्ठतालु',
    'KO': 'कण्ठौष्ठम्',
    'DO': 'दन्तौष्ठम्',
    'JM': 'जिह्वामूलम्'
}

STHAANA = {
    'K': ['अ', 'आ', 'क्', 'ख्', 'ग्', 'घ्', 'ङ्', 'ह्', VISARGA],
    'T': ['इ', 'ई', 'च्', 'छ्', 'ज्', 'झ्', 'ञ्', 'य्', 'श्'],
    'M': ['ऋ', 'ॠ', 'ट्', 'ठ्', 'ड्', 'ढ्', 'ण्', 'र्', 'ष्'],
    'D': ['ऌ', 'त्', 'थ्', 'द्', 'ध्', 'न्', 'ल्', 'स्'],
    'O': ['उ', 'ऊ', 'प्', 'फ्', 'ब्' 'भ्', 'म्', UPADHMANIYA],
    'N': ['ङ्', 'ञ्', 'ण्', 'न्', 'म्', ANUSWARA],
    'KT': ['ए', 'ऐ'],
    'KO': ['ओ', 'औ'],
    'DO': ['व्'],
    'JM': [JIHVAAMULIYA]
}

###############################################################################

AABHYANTARA = {
    'SP': [v + HALANTA for v in VARGIYA],
    'ISP': [v + HALANTA for v in ANTAHSTHA],
    'IVV': [v + HALANTA for v in USHMA] + [JIHVAAMULIYA, UPADHMANIYA],
    'VV': SWARA[1:] + [CHANDRABINDU, ANUSWARA, VISARGA],
    'SV': SWARA[:1]
}

AABHYANTARA_NAMES = {
    'SP': 'स्पृष्टः',
    'ISP': 'ईषत्स्पृष्टः',
    'IVV': 'ईषद्विवृतः',
    'VV': 'विवृतः',
    'SV': 'संवृतः'
}

###############################################################################

BAAHYA = {
    'VV': [v + HALANTA for v in resolve_pratyaahaara('खर्')[0]],
    'SV': [v + HALANTA for v in resolve_pratyaahaara('हश्')[0]],
    'SH': [v + HALANTA for v in resolve_pratyaahaara('खर्')[0]],
    'N': [v + HALANTA for v in resolve_pratyaahaara('हश्')[0]],
    'GH': [v + HALANTA for v in resolve_pratyaahaara('हश्')[0]],
    'AGH': [v + HALANTA for v in resolve_pratyaahaara('खर्')[0]],
    'AP': [
        v + HALANTA
        for v in (VARGA_PRATHAMA +
                  VARGA_TRITIYA +
                  VARGA_PANCHAMA +
                  resolve_pratyaahaara('यण्')[0])
    ] + [CHANDRABINDU, ANUSWARA],
    'MP': [
        v + HALANTA
        for v in (VARGA_DWITIYA +
                  VARGA_CHATURTHA +
                  resolve_pratyaahaara('शल्')[0])
    ] + [VISARGA, JIHVAAMULIYA, UPADHMANIYA],
    'U': SWARA,
    'ANU': [s + ANUDATTA for s in SWARA],
    'SWA': [s + SWARITA for s in SWARA]
}

BAAHYA_NAMES = {
    'VV': 'विवारः',
    'SV': 'संवारः',
    'SH': 'श्वासः',
    'N': 'नादः',
    'GH': 'घोषः',
    'AGH': 'अघोषः',
    'AP': 'अल्पप्राणः',
    'MP': 'महाप्राणः',
    'U': 'उदात्तः',
    'ANU': 'अनुदात्तः',
    'SWA': 'स्वरितः'
}

###############################################################################


def get_signature_letter(letter, abbrev=False):
    """
    Get uccharana sthaana and prayatna based signature of a letter

    Parameters
    ----------
    letter : str
        Samskrit letter
        I case of Vyanjana, it must contain the HALANTA symbol as well
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Samskrit names
        The default is False.

    Returns
    -------
    signature : dict
        utpatti sthaana, aabhyantara prayatna and baahya prayatna of a letter
    """

    sthaana = get_ucchaarana_letter(letter, dimension=0, abbrev=abbrev)
    aabhyantara = get_ucchaarana_letter(letter, dimension=1, abbrev=abbrev)
    baahya = get_ucchaarana_letter(letter, dimension=2, abbrev=abbrev)

    signature = {
        'sthaana': sthaana,
        'aabhyantara': aabhyantara,
        'baahya': baahya
    }
    return signature


def get_ucchaarana_letter(letter, dimension=0, abbrev=False):
    """
    Get uccharana sthaana or prayatna of a letter

    Parameters
    ----------
    letter : str
        Samskrit letter
        In case of Vyanjana, it must contain the HALANTA symbol as well
    dimension : int
        0 : sthaana
        1 : aabhyantara prayatna
        2 : baahya prayatna
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Samskrit names
        The default is False.

    Returns
    -------
    str
        uccharana sthaana or prayatna of a letter

    """
    ucchaarana = []
    DICTS = [STHAANA, AABHYANTARA, BAAHYA]
    NAMES = [STHAANA_NAMES, AABHYANTARA_NAMES, BAAHYA_NAMES]

    if abbrev:
        def uccharana_name(s):
            return s
        join_str = '-'
    else:
        def uccharana_name(s):
            return NAMES[dimension][s]
        join_str = ' '

    for s, letter_list in DICTS[dimension].items():
        if letter in letter_list:
            ucchaarana.append(uccharana_name(s))

    if len(ucchaarana) > 1 and not abbrev:
        ucchaarana.append('च')

    return join_str.join(ucchaarana)


def get_ucchaarana_word(word, dimension=0, abbrev=False):
    """
    Get uccharana of a word

    Parameters
    ----------
    word : str
        Samskrit word (or text)
        Caution:
            If multiple words are provided, the spaces are not included in
            the output list
    dimension : int
        0 : sthaana
        1 : aabhyantara prayatna
        2 : baahya prayatna
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Samskrit names
        The default is False.
    Returns
    -------
    list
        List of (letter, uccharana)

    """
    letters = []
    for letter in split_varna_word(word, technical=False):
        if VISARGA in letter:
            letters.extend(letter)
        else:
            letters.append(letter)
    return [
        (letter, get_ucchaarana_letter(letter, dimension, abbrev))
        for letter in letters
    ]


def get_ucchaarana(text, dimension=0, abbrev=False):
    """
    Get uccharana list of a Samskrit text

    Parameters
    ----------
    text : str
        Samskrit text (can contain newlines, spaces)
    dimension : int
        0 : sthaana
        1 : aabhyantara prayatna
        2 : baahya prayatna
    abbrev : bool
        If True,
            The output will contain English abbreviations
        Otherwise,
            The output will contain Samskrit names
        The default is False.
    Returns
    -------
    list
        List of (letter, uccharana) for words in a nested list manner
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


def get_sthaana_letter(letter, abbrev=False):
    """Wrapper for get_ucchaarana_letter for sthaana"""
    return get_ucchaarana_letter(letter, dimension=0, abbrev=abbrev)


def get_sthaana_word(word, abbrev=False):
    """Wrapper for get_ucchaarana_word for sthaana"""
    return get_ucchaarana_word(word, dimension=0, abbrev=abbrev)


def get_sthaana(text, abbrev=False):
    """Wrapper for get_ucchaarana for sthaana"""
    return get_ucchaarana(text, dimension=0, abbrev=abbrev)

# --------------------------------------------------------------------------- #


def get_aabhyantara_letter(letter, abbrev=False):
    """Wrapper for get_ucchaarana_letter for aabhyantara"""
    return get_ucchaarana_letter(letter, dimension=1, abbrev=abbrev)


def get_aabhyantara_word(word, abbrev=False):
    """Wrapper for get_ucchaarana_word for aabhyantara"""
    return get_ucchaarana_word(word, dimension=1, abbrev=abbrev)


def get_aabhyantara(text, abbrev=False):
    """Wrapper for get_ucchaarana for aabhyantara"""
    return get_ucchaarana(text, dimension=1, abbrev=abbrev)

# --------------------------------------------------------------------------- #


def get_baahya_letter(letter, abbrev=False):
    """Wrapper for get_ucchaarana_letter for baahya"""
    return get_ucchaarana_letter(letter, dimension=2, abbrev=abbrev)


def get_baahya_word(word, abbrev=False):
    """Wrapper for get_ucchaarana_word for baahya"""
    return get_ucchaarana_word(word, dimension=2, abbrev=abbrev)


def get_baahya(text, abbrev=False):
    """Wrapper for get_ucchaarana for baahya"""
    return get_ucchaarana(text, dimension=2, abbrev=abbrev)

###############################################################################
