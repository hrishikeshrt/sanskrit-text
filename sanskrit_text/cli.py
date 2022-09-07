#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Console Script for :code:`sanskrit-text`"""

###############################################################################

import argparse
import sys

###############################################################################


def main():
    """Console Script for :code:`sanskrit-text`"""
    parser = argparse.ArgumentParser("Sanskrit Text Utility")
    parser.add_argument("_", nargs="*")
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Under Construction ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
