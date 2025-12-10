#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Console interface for :code:`sanskrit-text`."""

###############################################################################

import argparse
import json
import sys

from . import clean, get_signature, get_syllables, get_ucchaarana, split_varna

###############################################################################


def _read_text_argument(text_arg: str | None) -> str:
    """Return text from argument or stdin if argument is missing."""
    if text_arg is not None:
        return text_arg
    return sys.stdin.read()


def _add_clean_subcommand(subparsers):
    parser = subparsers.add_parser(
        "clean", help="Clean Sanskrit (Devanagari) text."
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Input text. If omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--keep-punct",
        action="store_true",
        help="Keep punctuation characters.",
    )
    parser.add_argument(
        "--keep-digits",
        action="store_true",
        help="Keep Devanagari digits.",
    )
    parser.add_argument(
        "--no-spaces",
        action="store_true",
        help="Remove whitespace characters from the output.",
    )
    parser.add_argument(
        "--allow",
        default="",
        help="Additional characters to allow (string of characters).",
    )
    parser.set_defaults(func=_handle_clean)


def _handle_clean(args: argparse.Namespace) -> int:
    text = _read_text_argument(args.text)
    allow = list(args.allow) if args.allow else None
    result = clean(
        text,
        punct=bool(args.keep_punct),
        digits=bool(args.keep_digits),
        spaces=not bool(args.no_spaces),
        allow=allow,
    )
    print(result)
    return 0


def _add_syllables_subcommand(subparsers):
    parser = subparsers.add_parser(
        "syllables",
        help="Get syllables from Sanskrit (Devanagari) text.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Input text. If omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--technical",
        action="store_true",
        help="Use technical syllabification (at most one swara/vyanjana).",
    )
    parser.set_defaults(func=_handle_syllables)


def _handle_syllables(args: argparse.Namespace) -> int:
    text = _read_text_argument(args.text)
    result = get_syllables(text, technical=bool(args.technical))
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _add_split_varna_subcommand(subparsers):
    parser = subparsers.add_parser(
        "split-varna",
        help="Obtain varṇa decomposition of Sanskrit (Devanagari) text.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Input text. If omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--technical",
        action="store_true",
        help="Use technical decomposition (vowels and vowel signs split).",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Return a single flat list instead of nested lists.",
    )
    parser.set_defaults(func=_handle_split_varna)


def _handle_split_varna(args: argparse.Namespace) -> int:
    text = _read_text_argument(args.text)
    result = split_varna(
        text,
        technical=bool(args.technical),
        flat=bool(args.flat),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _add_ucchaarana_subcommand(subparsers):
    parser = subparsers.add_parser(
        "ucchaarana",
        help="Get ucchaarana (sthaana / prayatna) for text.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Input text. If omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="Dimension: 0=sthaana, 1=aabhyantara, 2=baahya. Default: 0.",
    )
    parser.add_argument(
        "--abbrev",
        action="store_true",
        help="Use English abbreviations instead of Sanskrit names.",
    )
    parser.set_defaults(func=_handle_ucchaarana)


def _handle_ucchaarana(args: argparse.Namespace) -> int:
    text = _read_text_argument(args.text)
    result = get_ucchaarana(
        text,
        dimension=int(args.dimension),
        abbrev=bool(args.abbrev),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _add_signature_subcommand(subparsers):
    parser = subparsers.add_parser(
        "signature",
        help="Get ucchaarana-based signature (sthaana, prayatna) for text.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Input text. If omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--abbrev",
        action="store_true",
        help="Use English abbreviations instead of Sanskrit names.",
    )
    parser.set_defaults(func=_handle_signature)


def _handle_signature(args: argparse.Namespace) -> int:
    text = _read_text_argument(args.text)
    result = get_signature(text, abbrev=bool(args.abbrev))
    print(json.dumps(result, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="skt", description="Sanskrit Text (Devanagari) Utility CLI."
    )
    subparsers = parser.add_subparsers(dest="command")

    _add_clean_subcommand(subparsers)
    _add_syllables_subcommand(subparsers)
    _add_split_varna_subcommand(subparsers)
    _add_ucchaarana_subcommand(subparsers)
    _add_signature_subcommand(subparsers)

    return parser


def main(argv=None) -> int:
    """Entry point for the :code:`skt` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
