from urllib.request import urlopen
import json
import time
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

BASE_URL = "https://cncstatsapibeta.azurewebsites.net/api"
TICKER_GAME_HISTORY_DEPTH = 3
REFRESH_RATE_SECS = 60

parser = argparse.ArgumentParser()
parser.add_argument('id')
parser.add_argument('--matches-ticker', dest='matches_ticker', action='store_true')
parser.add_argument('--player-stats', dest='player_stats', action='store_true')
args = parser.parse_args()
PLAYER_ID = args.id
MATCHES_TICKER_ENABLED = args.matches_ticker
PLAYER_STATS_ENABLED = args.player_stats

def write_ticker_to_file():
    ticker_file_name = "ticker.txt"
    logging.debug(f"Opening {ticker_file_name} for writing")
    ticker = open(ticker_file_name, "w+", encoding="utf-8")
    endpoint = f'{BASE_URL}/Player/{PLAYER_ID}/Matches'
    logging.debug(f"Getting latest matches from {endpoint}")
    last_games = urlopen(endpoint)
    last_games_json = json.loads(last_games.read())
    ticker_string = f""
    for x in range(0,TICKER_GAME_HISTORY_DEPTH):
        if last_games_json[x]['win'] == True:
            outcome = "WIN"
        else:
            outcome = "LOSS"

        if last_games_json[x]['pointsGained'] > 0:
            points = "↑%s pts" % int(last_games_json[x]['pointsGained'])
        else:
            points = "↓%s pts" % str(int(last_games_json[x]['pointsGained'])).replace("-","")
        
        timestamp = last_games_json[x]['starttime']
        # Some starttimes come back from the API with MS appended, some don't, we don't need them so always remove them
        if "." in timestamp:
            timestamp = timestamp.split(".", 1)[0]

        dt_timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        game_start_delta = datetime.now() - dt_timestamp
        game_end_time_secs = int(game_start_delta.total_seconds() - last_games_json[x]['matchDuration'])
        game_end_time_mins = int(game_end_time_secs / 60)

        ticker_string = ticker_string + f"{outcome} ({points}) vs {last_games_json[x]['opponentName']} {game_end_time_mins}m ago on {last_games_json[x]['mapName']}  | "
    
    logging.debug(f"Writing '{ticker_string}' to {ticker_file_name}")
    ticker.write(ticker_string)
    logging.debug(f"Closing {ticker_file_name}")
    ticker.close()

def write_player_stats_to_file():
    rank_file_name = "player_rank.txt"
    points_file_name = "player_points.txt"
    ratio_file_name = "player_win_ratio.txt"
    logging.debug(f"Opening {rank_file_name} for writing")
    rank_file = open(rank_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {points_file_name} for writing")
    points_file = open(points_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {ratio_file_name} for writing")
    ratio_file = open(ratio_file_name, "w+", encoding="utf-8")

    endpoint = f'{BASE_URL}/Player/{PLAYER_ID}'
    logging.debug(f"Getting stats from {endpoint}")
    player_stats = urlopen(endpoint)
    player_stats_json = json.loads(player_stats.read())
    player_rank = str(player_stats_json['position']['rank'])
    player_points = str(int(player_stats_json['position']['points']))
    player_ratio = f"{player_stats_json['position']['winPercentage']}"

    logging.debug(f"Writing {player_rank} to {rank_file_name}")
    rank_file.write(player_rank)
    logging.debug(f"Writing {player_points} to {points_file_name}")
    points_file.write(player_points)
    logging.debug(f"Writing {player_ratio} to {ratio_file_name}")
    ratio_file.write(player_ratio)

    logging.debug(f"Closing {rank_file_name}")
    rank_file.close()
    logging.debug(f"Closing {points_file_name}")
    points_file.close()
    logging.debug(f"Closing {ratio_file_name}")
    ratio_file.close()

def main():
    logging.debug('Matches ticker: %s' % (MATCHES_TICKER_ENABLED))
    logging.debug('Player stats: %s' % (PLAYER_STATS_ENABLED))
    logging.debug('API base: %s' % (BASE_URL))
    logging.debug('Player ID: %s' % (PLAYER_ID))
    while True:
        if MATCHES_TICKER_ENABLED == True:
            write_ticker_to_file()
        if PLAYER_STATS_ENABLED == True:
            write_player_stats_to_file()

        logging.info(f"Sleeping for {REFRESH_RATE_SECS} seconds")
        time.sleep(REFRESH_RATE_SECS)

if __name__ == "__main__":
    main()
