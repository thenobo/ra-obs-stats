from urllib.request import urlopen
import json
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

logging.info('Gathering stats for %s from {BASE_URL}', PLAYER_ID)

while True:
    logging.info("Getting latest games from API")
    print(f'{BASE_URL}/Player/{PLAYER_ID}/Matches')
    last_games = urlopen(f'{BASE_URL}/Player/{PLAYER_ID}/Matches')
    last_games_json = json.loads(last_games.read())
    logging.info("Writing latest games to files")
    map = open("map.txt", "w+", encoding="utf-8")
    opponent = open("opponent.txt", "w+", encoding="utf-8")
    points = open("points.txt", "w+", encoding="utf-8")
    for x in range(0,5):
        mapName = last_games_json[x]['mapName']
        map.write(f'{mapName}\n')
    for x in range(0,5):
        opponentName = last_games_json[x]['opponentName']
        opponent.write(f'{opponentName}\n')
    for x in range(0,5):
        pointsGained = last_games_json[x]['pointsGained']
        points.write(f'{pointsGained}\n')

    map.close()
    opponent.close()
    points.close()
    time.sleep(60)
