import atoma
import requests
import argparse

def main():
    arg_parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    arg_parser.add_argument(
        '-s', "--source", action="store", required=True, help="The source feed to tweet"
    )

    arg_parser.add_argument(
        '-f', "--frequency", action="store", default="d", choices=['m', 'h', 'd', 'w'], help="The timeframe to check for posts. Can be 'm', 'h', 'd', or 'w' for minute, hour, day, and week respectively."
    )

    args = arg_parser.parse_args()




main()
