from urllib.request import urlopen
import json
from datetime import datetime
import time
import argparse
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

BASE_URL = "https://cncstatsapibeta.azurewebsites.net/api"

parser = argparse.ArgumentParser()
parser.add_argument('id')
args = parser.parse_args()
PLAYER_ID = args.id

logging.info("Gathering stats for %s" % (PLAYER_ID))

while True:
    logging.info("Getting latest games from API")
    last_games = urlopen("%s/Player/%s/Matches" % (BASE_URL, PLAYER_ID))
    last_games_json = json.loads(last_games.read())
    logging.info("Writing latest games to files")
    map = open("map.txt", "w+", encoding="utf-8")
    opponent = open("opponent.txt", "w+", encoding="utf-8")
    points = open("points.txt", "w+", encoding="utf-8")
    for x in range(0,5):
        map.write("%s\n" % (last_games_json[x]['mapName']))
    for x in range(0,5):
        opponent.write("%s\n" % (last_games_json[x]['opponentName']))
    for x in range(0,5):
        points.write("%s\n" % (last_games_json[x]['pointsGained']))

    map.close()
    opponent.close()
    points.close()
    time.sleep(60)
