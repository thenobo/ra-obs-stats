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
parser.add_argument('--session-stats', dest='session_stats', action='store_true')
parser.add_argument('--specify-session-start-time', dest='provided_session_start_time', type=str)
args = parser.parse_args()
PLAYER_ID = args.id
MATCHES_TICKER_ENABLED = args.matches_ticker
PLAYER_STATS_ENABLED = args.player_stats
SESSION_STATS_ENABLED = args.session_stats

def write_ticker_to_file(match_history):
    ticker_file_name = "ticker.txt"
    logging.debug(f"Opening {ticker_file_name} for writing")
    ticker = open(ticker_file_name, "w+", encoding="utf-8")
    last_games_json = match_history
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

        ticker_string = ticker_string + f"{outcome} ({points}) vs {last_games_json[x]['opponentName']} {game_end_time_mins}m ago on {last_games_json[x]['mapName']} | "
    
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

def write_session_stats_to_file(SESSION_START, match_history):
    session_games_played_file_name = "session_games_played.txt"
    session_points_change_file_name = "session_points_change.txt"
    logging.debug(f"Opening {session_games_played_file_name} for writing")
    session_games_played_file = open(session_games_played_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {session_points_change_file_name} for writing")
    session_points_change_file = open(session_points_change_file_name, "w+", encoding="utf-8")

    last_games_json = match_history
    matches_since_session_start = []
    first_match_of_session_found = False
    for match in last_games_json:
        timestamp = match['starttime']
        # Some starttimes come back from the API with MS appended, some don't, we don't need them so always remove them
        if "." in timestamp:
            timestamp = timestamp.split(".", 1)[0]

        dt_timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        if (SESSION_START<dt_timestamp):
            matches_since_session_start.append(match)
        elif first_match_of_session_found == True:
            break
        else:
            first_match_of_session_found = True
            matches_since_session_start.append(match)

    number_of_matches_since_session_start = len(matches_since_session_start)-1
    most_recent_match = matches_since_session_start[0]
    first_match_of_session = matches_since_session_start[number_of_matches_since_session_start]
    

    points_change_since_session_start = int(most_recent_match['playerPoints']-first_match_of_session['playerPoints'])
    logging.debug(f"Writing {number_of_matches_since_session_start} to {session_games_played_file_name}")
    session_games_played_file.write(str(number_of_matches_since_session_start))
    logging.debug(f"Writing {points_change_since_session_start} to {session_points_change_file_name}")
    session_points_change_file.write(str(points_change_since_session_start))
    logging.debug(f"Closing {session_games_played_file_name}")
    session_games_played_file.close()
    logging.debug(f"Closing {session_points_change_file_name}")
    session_points_change_file.close()

def get_match_history():
    endpoint = f'{BASE_URL}/Player/{PLAYER_ID}/Matches'
    logging.debug(f"Getting latest matches from {endpoint}")
    match_history = urlopen(endpoint)
    match_history_json = json.loads(match_history.read())
    logging.debug(f"Found {len(match_history_json)} matches")
    return match_history_json

def main():
    # Exit early if no features enabled
    if (MATCHES_TICKER_ENABLED == False) and (PLAYER_STATS_ENABLED == False) and (SESSION_STATS_ENABLED == False):
        logging.error("No features specified, provide one or more of --matches-ticker, --player-stats or --session-stats")
        exit(1)

    logging.debug('Matches ticker: %s' % (MATCHES_TICKER_ENABLED))
    logging.debug('Player stats: %s' % (PLAYER_STATS_ENABLED))
    logging.debug('Session stats: %s' % (SESSION_STATS_ENABLED))
    
    # If we're doing something which requires the match histort, prep variable
    if (MATCHES_TICKER_ENABLED == True) or (SESSION_STATS_ENABLED == True):
        match_history = None
    
    logging.debug('API base: %s' % (BASE_URL))
    logging.debug('Player ID: %s' % (PLAYER_ID))
    if args.provided_session_start_time:
        custom_start_time = args.provided_session_start_time
        dt_timestamp = datetime(datetime.today().year, datetime.today().month, datetime.today().day, int(custom_start_time.split(":")[0]), int(custom_start_time.split(":")[1]), 00)
        print("Using custom start time %s" % dt_timestamp)
        SESSION_START = dt_timestamp
    else:
        SESSION_START = datetime.utcnow()
    logging.debug('Session start: %s' % (SESSION_START))
    while True:
        if (MATCHES_TICKER_ENABLED == True) or (SESSION_STATS_ENABLED == True):
            match_history = get_match_history()
        if MATCHES_TICKER_ENABLED == True:
            write_ticker_to_file(match_history)
        if PLAYER_STATS_ENABLED == True:
            write_player_stats_to_file()
        if SESSION_STATS_ENABLED == True:
            write_session_stats_to_file(SESSION_START, match_history)
        
        logging.info(f"Sleeping for {REFRESH_RATE_SECS} seconds")
        time.sleep(REFRESH_RATE_SECS)

if __name__ == "__main__":
    main()
