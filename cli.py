#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# some code from https://github.com/flopp/GpxTrackPoster

import argparse
import os
import sys
from datetime import datetime

from github_poster import poster, drawer
from github_poster.utils import parse_years
from loader import DuolingoLoader, ShanBayLoader, StravaLoader, CiChangLoader, NSLoader

LOADER_DICT = {
    "duolingo": DuolingoLoader,
    "shanbay": ShanBayLoader,
    "strava": StravaLoader,
    "cichang": CiChangLoader,
    "ns": NSLoader,
}

# TODO refactor
UNIT_DICT = {
    "duolingo": "XP",
    "shanbay": "day",
    "strava": "km",
    "gpx": "km",
    "cichang": "words",
    "ns": "mins",
}

TYPES = '", "'.join(LOADER_DICT.keys())


def main():
    """Handle command line arguments and call other modules as needed."""
    p = poster.Poster()
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--type",
        metavar="TYPE",
        default="duolingo",
        choices=LOADER_DICT.keys(),
        help=f'Type of poster to create (default: "duolingo", available: "{TYPES}").',
    )
    args_parser.add_argument(
        "--gpx-dir",
        dest="gpx_dir",
        metavar="DIR",
        type=str,
        default=".",
        help="Directory containing GPX files (default: current directory).",
    )
    args_parser.add_argument(
        "--output",
        metavar="FILE",
        type=str,
        default="poster.svg",
        help='Name of generated SVG image file (default: "poster.svg").',
    )
    args_parser.add_argument(
        "--year",
        metavar="YEAR",
        type=str,
        default=str(datetime.now().year),
        help='Filter tracks by year; "NUM", "NUM-NUM", "all" (default: all years)',
    )
    args_parser.add_argument(
        "--title", metavar="TITLE", type=str, help="Title to display."
    )
    args_parser.add_argument(
        "--me",
        metavar="NAME",
        type=str,
        default="Joey",
        help='Athlete name to display (default: "Joey").',
    )
    args_parser.add_argument(
        "--background-color",
        dest="background_color",
        metavar="COLOR",
        type=str,
        default="#222222",
        help='Background color of poster (default: "#222222").',
    )
    args_parser.add_argument(
        "--track-color",
        dest="track_color",
        metavar="COLOR",
        type=str,
        default="#4DD2FF",
        help='Color of tracks (default: "#4DD2FF").',
    )
    args_parser.add_argument(
        "--track-color2",
        dest="track_color2",
        metavar="COLOR",
        type=str,
        help="Secondary color of tracks (default: none).",
    )
    args_parser.add_argument(
        "--text-color",
        dest="text_color",
        metavar="COLOR",
        type=str,
        default="#FFFFFF",
        help='Color of text (default: "#FFFFFF").',
    )
    args_parser.add_argument(
        "--special-color",
        dest="special_color",
        metavar="COLOR",
        default="yellow",
        help='Special track color (default: "yellow").',
    )
    args_parser.add_argument(
        "--special-color2",
        dest="special_color2",
        metavar="COLOR",
        default="red",
        help="Secondary color of special tracks (default: red).",
    )
    args_parser.add_argument(
        "--special-number1",
        dest="special_number1",
        type=float,
        default=0,
        help="Special number 1",
    )
    args_parser.add_argument(
        "--special-number2",
        dest="special_number2",
        type=float,
        default=0,
        help="Special number 2",
    )

    # strava
    args_parser.add_argument(
        "--strava_client_id",
        dest="strava_client_id",
        type=str,
        default="",
        help="",
    )
    args_parser.add_argument(
        "--strava_client_secret",
        dest="strava_client_secret",
        type=str,
        default="",
        help="",
    )
    args_parser.add_argument(
        "--strava_refresh_token",
        dest="strava_refresh_token",
        type=str,
        default="",
        help="",
    )
    # duolingo
    args_parser.add_argument(
        "--duolingo_user_name",
        dest="duolingo_user_name",
        type=str,
        default="",
        help="",
    )
    # shanbay
    args_parser.add_argument(
        "--shanbay_user_name",
        dest="shanbay_user_name",
        type=str,
        default="",
        help="",
    )

    # cichang
    args_parser.add_argument(
        "--cichang_user_name",
        dest="cichang_user_name",
        type=str,
        default="",
        help="",
    )
    args_parser.add_argument(
        "--cichang_password",
        dest="cichang_password",
        type=str,
        default="",
        help="",
    )

    # nintendo setting
    args_parser.add_argument(
        "--ns_device_id",
        dest="ns_device_id",
        type=str,
        default="",
        help="",
    )
    args_parser.add_argument(
        "--ns_smart_device_id",
        dest="ns_smart_device_id",
        type=str,
        default="",
        help="",
    )
    args_parser.add_argument(
        "--ns_session_token",
        dest="ns_session_token",
        type=str,
        default="",
        help="",
    )

    args = args_parser.parse_args()

    p.athlete = args.me
    if args.title:
        p.title = args.title
    else:
        p.title = "Yihong0618 " + str(args.type).upper()

    p.colors = {
        "background": args.background_color,
        "track": args.track_color,
        "track2": args.track_color2 or args.track_color,
        "special": args.special_color,
        "special2": args.special_color2 or args.special_color,
        "text": args.text_color,
    }
    p.units = UNIT_DICT.get(args.type, "times")
    from_year, to_year = parse_years(args.year)
    d = LOADER_DICT.get(args.type, "duolingo")(
        from_year, to_year, **dict(args._get_kwargs())
    )
    tracks, years = d.get_all_track_data()
    p.special_number = {
        "special_number1": d.special_number1,
        "special_number2": d.special_number2,
    }

    if args.special_number1:
        p.special_number["special_number1"] = args.special_number1
    if args.special_number2:
        p.special_number["special_number2"] = args.special_number2
    p.set_tracks(tracks, years)
    p.height = 55 + len(p.years) * 43
    p.draw(drawer.Drawer(p), str(args.type) + ".svg")


if __name__ == "__main__":
    main()
