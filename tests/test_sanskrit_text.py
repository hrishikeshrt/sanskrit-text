#!/usr/bin/env python
"""Tests for the `sanskrit-text` package."""

import json

import sanskrit_text as skt
from sanskrit_text import ARTIFICIAL_MATRA_A
from sanskrit_text.cli import main as cli_main


def test_ord_and_chr_unicode_roundtrip():
    """Unicode helper functions should be inverses for a basic character."""
    code = skt.ord_unicode("अ")
    assert code == "0905"
    assert skt.chr_unicode(code) == "अ"


def test_clean_basic_and_options():
    """Basic cleaning behaviour and option flags."""
    # By default, keep only Sanskrit letters and whitespace.
    assert skt.clean("अ b c १।") == "अ"

    # Keep punctuation and digits when requested.
    assert skt.clean("अ।", punct=True) == "अ।"
    assert skt.clean("अ१", digits=True) == "अ१"

    # Normalise whitespace while preserving lines.
    assert skt.clean("अ  \n  इ") == "अ\nइ"


def test_split_lines_basic():
    """Splitting on danda, double danda and newlines."""
    assert skt.split_lines("अ।आ॥इ\nई") == ["अ", "आ", "इ", "ई"]


def test_marker_swara_roundtrip():
    """Conversion between swara and matra / artificial matra."""
    # Simple swara/matra pair.
    assert skt.marker_to_swara("ा") == "आ"
    assert skt.swara_to_marker("आ") == "ा"

    # Artificial matra for अ.
    assert ARTIFICIAL_MATRA_A == "-अ"
    assert skt.marker_to_swara(ARTIFICIAL_MATRA_A) == "अ"
    assert skt.swara_to_marker("अ") == ARTIFICIAL_MATRA_A

    # Extended matra/swara pair.
    assert skt.marker_to_swara("ॆ") == "ऎ"
    assert skt.swara_to_marker("ऎ") == "ॆ"


def test_fix_anuswara_basic():
    """Anuswara before a vargiya consonant should become appropriate nasal."""
    assert skt.fix_anuswara("कंकि") == "कङ्कि"


def test_trim_matra_basic_cases():
    """trim_matra should safely trim trailing markers and matras."""
    # Empty and simple strings are unchanged where appropriate.
    assert skt.trim_matra("") == ""
    assert skt.trim_matra("क") == "क"

    # Trailing visarga / anuswara / halanta should be removed.
    assert skt.trim_matra("कः") == "क"
    assert skt.trim_matra("कं") == "क"
    assert skt.trim_matra("क्") == "क"

    # Trailing matra should be removed, optionally after removing markers.
    assert skt.trim_matra("का") == "क"
    assert skt.trim_matra("कां") == "क"
    assert skt.trim_matra("कि") == "क"
    assert skt.trim_matra("किं") == "क"


def test_syllables_and_varna_roundtrip():
    """Syllabification and varna split/join for a simple phrase."""
    text = "कवि भारतः"

    # Syllables.
    assert skt.get_syllables_word("कवि") == ["क", "वि"]
    assert skt.get_syllables(text) == [[["क", "वि"], ["भा", "र", "तः"]]]

    # Varna decomposition and join.
    flat_viccheda = skt.split_varna(text, flat=True)
    assert flat_viccheda == [
        "क्",
        "-अ",
        "व्",
        "ि",
        " ",
        "भ्",
        "ा",
        "र्",
        "-अ",
        "त्",
        "-अ",
        "ः",
    ]
    assert skt.join_varna(flat_viccheda) == text


def test_ucchaarana_basic():
    """Basic checks for ucchaarana helpers."""
    assert skt.get_ucchaarana_letter("क") == "कण्ठः"
    word_info = skt.get_ucchaarana_word("कवि")
    # First and last entries should match known values.
    assert word_info[0][0] == "क्"
    assert word_info[0][1] == "कण्ठः"
    assert word_info[-1][0] == "इ"
    assert word_info[-1][1] == "तालु"


def test_cli_clean_basic(capsys):
    """CLI: `clean` subcommand with direct argument."""
    exit_code = cli_main(["clean", "अ b १।"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "अ"


def test_cli_syllables_and_split_varna(capsys):
    """CLI: `syllables` and `split-varna` subcommands."""
    text = "कवि भारतः"

    # syllables (non-technical by default)
    exit_code = cli_main(["syllables", text])
    captured = capsys.readouterr()
    assert exit_code == 0
    syllables = json.loads(captured.out.strip())
    assert syllables == [[["क", "वि"], ["भा", "र", "तः"]]]

    # split-varna technical, flat output
    exit_code = cli_main(["split-varna", "--technical", "--flat", text])
    captured = capsys.readouterr()
    assert exit_code == 0
    viccheda = json.loads(captured.out.strip())
    assert viccheda == [
        "क्",
        "-अ",
        "व्",
        "ि",
        " ",
        "भ्",
        "ा",
        "र्",
        "-अ",
        "त्",
        "-अ",
        "ः",
    ]


def test_cli_ucchaarana_and_signature(capsys):
    """CLI: `ucchaarana` and `signature` subcommands."""
    text = "कवि"

    # ucchaarana, default dimension (0 = sthaana)
    exit_code = cli_main(["ucchaarana", text])
    captured = capsys.readouterr()
    assert exit_code == 0
    ucch = json.loads(captured.out.strip())
    # Structure: lines -> words -> [letter, description]
    assert ucch[0][0][0][0] == "क्"
    assert ucch[0][0][0][1] == "कण्ठः"

    # signature with full Sanskrit names
    exit_code = cli_main(["signature", text])
    captured = capsys.readouterr()
    assert exit_code == 0
    sig = json.loads(captured.out.strip())
    first_letter, first_sig = sig[0][0][0]
    assert first_letter == "क्"
    assert "sthaana" in first_sig
    assert "aabhyantara" in first_sig
    assert "baahya" in first_sig
