from urllib.request import urlopen
import json
import time
import argparse
import logging
from datetime import datetime
from datetime import timedelta
import seaborn as sns # for data visualization
import pandas as pd # for data analysis
import matplotlib.pyplot as plt # for data visualization

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

BASE_URL = "https://cnc-stats-api.azurewebsites.net/api"
TICKER_GAME_HISTORY_DEPTH = 3
REFRESH_RATE_SECS = 60
SHORTNAME_MAP = {
    "Keep off the grass":"KOTG",
    "Path beyond":"Path",
    "Bullseye":"Bullseye",
    "Canyon":"Canyon",
    "Tournament ore rift":"Ore Rift",
    "Tournament arena":"Tourny Arena",
    "North by Northwest":"NBNW",
    "Arena Valley Extreme":"Arena Valley",
    }
parser = argparse.ArgumentParser()
parser.add_argument('id')
parser.add_argument('--matches-ticker', dest='matches_ticker', action='store_true')
parser.add_argument('--matches', dest='matches', action='store_true')
parser.add_argument('--short-ticker', dest='short_ticker', action='store_true')
parser.add_argument('--player-stats', dest='player_stats', action='store_true')
parser.add_argument('--session-stats', dest='session_stats', action='store_true')
parser.add_argument('--specify-session-start-time', dest='provided_session_start_time', type=str)
parser.add_argument('--session-stats-graphs', dest='session_stats_graphs', action='store_true')
args = parser.parse_args()
PLAYER_ID = args.id
MATCHES_TICKER_ENABLED = args.matches_ticker
PLAYER_STATS_ENABLED = args.player_stats
SESSION_STATS_ENABLED = args.session_stats
SHORT_TICKER_ENABLED = args.short_ticker
SESSION_STATS_GRAPHS_ENABLED = args.session_stats_graphs
MATCHES_ENABLED = args.matches

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
            points = "???%s pts" % int(last_games_json[x]['pointsGained'])
        else:
            points = "???%s pts" % str(int(last_games_json[x]['pointsGained'])).replace("-","")
        
        timestamp = last_games_json[x]['starttime']
        # Some starttimes come back from the API with MS appended, some don't, we don't need them so always remove them
        if "." in timestamp:
            timestamp = timestamp.split(".", 1)[0]

        dt_timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        game_start_delta = datetime.utcnow() - dt_timestamp
        game_end_time_secs = int(game_start_delta.total_seconds() - last_games_json[x]['matchDuration'])
        game_end_time_mins = int(game_end_time_secs / 60)

        if SHORT_TICKER_ENABLED:
            ticker_string = ticker_string + f"{outcome[0]} ({points}) vs {last_games_json[x]['opponentName']} {game_end_time_mins}m ago on {SHORTNAME_MAP[last_games_json[x]['mapName']]} | "
        else:    
            ticker_string = ticker_string + f"{outcome} ({points}) vs {last_games_json[x]['opponentName']} {game_end_time_mins}m ago on {last_games_json[x]['mapName']} | "
    
    logging.debug(f"Writing '{ticker_string}' to {ticker_file_name}")
    ticker.write(ticker_string)
    logging.debug(f"Closing {ticker_file_name}")
    ticker.close()

def write_session_points_to_graph(SESSION_START, match_history, player_name, session_start_time):
    last_games_json = match_history
    matches_since_session_start = []
    first_match_of_session_found = False
    last_match_index = -1
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
            last_match_index = int(list(last_games_json).index(match) + 1)
        if last_match_index != -1:
            matches_since_session_start.append(list(last_games_json)[last_match_index])

    number_of_matches_since_session_start = len(matches_since_session_start)-1
    match_labels = []
    points = []

    for x in range(0,number_of_matches_since_session_start):
        match_labels.append(x)

    for x in range(0,number_of_matches_since_session_start):
        points.append(int(matches_since_session_start[x]['playerPoints']))

    maxPoints = max(points)
    minPoints = min(points)

    points = points[::-1]
    plt.style.use("dark_background")
    for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
        plt.rcParams[param] = '0.9'  # very light grey
    for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
        plt.rcParams[param] = '#212946'  # bluish dark grey
    colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
    ]

    temp_df = pd.DataFrame({"points":points})
    fig, ax = plt.subplots()
    temp_df.plot(marker='o',color=colors, ax=ax, legend=False)
    # Redraw the data with low alpha and slighty increased linewidth:
    n_shades = 10
    diff_linewidth = 1.05
    alpha_value = 0.3 / n_shades

    for n in range(1, n_shades+1):

        temp_df.plot(marker='o',
                linewidth=2+(diff_linewidth*n),
                alpha=alpha_value,
                legend=False,
                ax=ax,
                color=colors)

    # Color the areas below the lines:
    for column, color in zip(temp_df, colors):
        ax.fill_between(x=temp_df.index,
                        y1=temp_df[column].values,
                        y2=[0] * len(temp_df),
                        color=color,
                        alpha=0.1)

    ax.grid(color='#2A3459')

    ax.set_xlim([ax.get_xlim()[0] - 0.2, ax.get_xlim()[1] + 0.2])  # to not have the markers cut off
    ax.set_ylim(minPoints - 50, maxPoints + 50)
    ax.set_xlabel("Game #")
    ax.set_title("%s (games since %s)" % (player_name, session_start_time))
    #sns.set_context("poster")
    sns.lineplot(y = "points", data=temp_df, legend=False)
    fig = plt.gcf()
    fig.set_size_inches(10,5)
    plt.savefig('session_points.png')
    plt.clf()
    plt.cla()
    plt.close()

def write_player_stats_to_file(player_rank, player_points, player_ratio):
    rank_file_name = "player_rank.txt"
    points_file_name = "player_points.txt"
    ratio_file_name = "player_win_ratio.txt"
    logging.debug(f"Opening {rank_file_name} for writing")
    rank_file = open(rank_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {points_file_name} for writing")
    points_file = open(points_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {ratio_file_name} for writing")
    ratio_file = open(ratio_file_name, "w+", encoding="utf-8")

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

def write_session_stats_to_file(SESSION_START, match_history, session_start_player_stats, player_stats):
    session_games_played_file_name = "session_games_played.txt"
    session_points_change_file_name = "session_points_change.txt"
    session_rank_change_file_name = "session_rank_change.txt"
    logging.debug(f"Opening {session_games_played_file_name} for writing")
    session_games_played_file = open(session_games_played_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {session_points_change_file_name} for writing")
    session_points_change_file = open(session_points_change_file_name, "w+", encoding="utf-8")
    logging.debug(f"Opening {session_rank_change_file_name} for writing")
    session_rank_change_file = open(session_rank_change_file_name, "w+", encoding="utf-8")

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
    rank_change_since_session_start = (int(session_start_player_stats['player_rank'])-int(player_stats['player_rank']))

    logging.debug(f"Writing {number_of_matches_since_session_start} to {session_games_played_file_name}")
    session_games_played_file.write(str(number_of_matches_since_session_start))
    logging.debug(f"Writing {points_change_since_session_start} to {session_points_change_file_name}")
    session_points_change_file.write(str(points_change_since_session_start))
    logging.debug(f"Writing {rank_change_since_session_start} to {session_rank_change_file_name}")
    session_rank_change_file.write(str(rank_change_since_session_start))
    logging.debug(f"Closing {session_games_played_file_name}")
    session_games_played_file.close()
    logging.debug(f"Closing {session_points_change_file_name}")
    session_points_change_file.close()
    logging.debug(f"Closing {session_rank_change_file_name}")
    session_rank_change_file.close()

def get_player_stats(id):
    endpoint = f'{BASE_URL}/Player/{PLAYER_ID}'
    logging.debug(f"Getting stats from {endpoint}")
    player_stats = urlopen(endpoint)
    player_stats_json = json.loads(player_stats.read())
    player_rank = str(player_stats_json['position']['rank'])
    player_points = str(int(player_stats_json['position']['points']))
    player_ratio = f"{player_stats_json['position']['winPercentage']}"
    player_name = f"{player_stats_json['position']['name']}"
    return({'player_rank':player_rank, 'player_points':player_points, 'player_ratio':player_ratio, 'player_name':player_name})

def get_match_history(limit=None):
    if limit != None:
        endpoint = f'{BASE_URL}/Player/{PLAYER_ID}/Matches?limit={limit}'
    else:
        endpoint = f'{BASE_URL}/Player/{PLAYER_ID}/Matches'
    logging.debug(f"Getting latest matches from {endpoint}")
    match_history = urlopen(endpoint)
    match_history_json = json.loads(match_history.read())
    logging.debug(f"Got {len(match_history_json)} matches")
    return match_history_json

def write_matches_to_file(match_history):
    matches_file_name = "matches.txt"
    logging.debug(f"Opening {matches_file_name} for writing")
    matches = open(matches_file_name, "w+", encoding="utf-8")
    last_games_json = match_history
    matches_string = f""
    for x in range(0,TICKER_GAME_HISTORY_DEPTH):
        if last_games_json[x]['win'] == True:
            outcome = "WIN"
        else:
            outcome = "LOSS"

        if last_games_json[x]['pointsGained'] > 0:
            points = "???%s pts" % int(last_games_json[x]['pointsGained'])
        else:
            points = "???%s pts" % str(int(last_games_json[x]['pointsGained'])).replace("-","")
        
        timestamp = last_games_json[x]['starttime']
        # Some starttimes come back from the API with MS appended, some don't, we don't need them so always remove them
        if "." in timestamp:
            timestamp = timestamp.split(".", 1)[0]

        dt_timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        game_start_delta = datetime.utcnow() - dt_timestamp
        game_end_time_secs = int(game_start_delta.total_seconds() - last_games_json[x]['matchDuration'])
        game_end_time_mins = int(game_end_time_secs / 60)
        matches_string = matches_string + f"{game_end_time_mins}m ago {outcome} ({points}) vs {last_games_json[x]['opponentName']} on {last_games_json[x]['mapName']} \n"

    logging.debug(f"Writing '{matches_string}' to {matches_file_name}")
    matches.write(matches_string)
    logging.debug(f"Closing {matches_file_name}")
    matches.close()

def main():
    APP_START_TIME = datetime.now()
    RECONFIRMATION_TIMEOUT_HOURS = 6
    reconfirmation_timeout = datetime.now() + timedelta(hours=RECONFIRMATION_TIMEOUT_HOURS)

    # Exit early if no features enabled
    if (MATCHES_TICKER_ENABLED == False) and (PLAYER_STATS_ENABLED == False) and (SESSION_STATS_ENABLED == False) and (SESSION_STATS_GRAPHS_ENABLED == False) and (MATCHES_ENABLED == False):
        logging.error("No features specified, provide one or more of --matches-ticker, --player-stats or --session-stats")
        exit(1)

    logging.debug('Matches ticker: %s' % (MATCHES_TICKER_ENABLED))
    logging.debug('Player stats: %s' % (PLAYER_STATS_ENABLED))
    logging.debug('Session stats: %s' % (SESSION_STATS_ENABLED))
    logging.debug('Session stats graphs: %s' % (SESSION_STATS_GRAPHS_ENABLED))
    logging.debug('Matches stats: %s' % (MATCHES_ENABLED))
    
    # If we're doing something which requires the match histort, prep variable
    if (MATCHES_TICKER_ENABLED == True) or (SESSION_STATS_ENABLED == True) or (MATCHES_ENABLED == True):
        match_history = None
    
    session_start_player_stats = get_player_stats(PLAYER_ID)

    logging.debug('API base: %s' % (BASE_URL))
    logging.debug('Player ID: %s' % (PLAYER_ID))
    if args.provided_session_start_time:
        custom_start_time = args.provided_session_start_time
        dt_timestamp = datetime(int(custom_start_time.split(":")[0]), int(custom_start_time.split(":")[1]), int(custom_start_time.split(":")[2]), int(custom_start_time.split(":")[3]), int(custom_start_time.split(":")[4]), 00)
        print("Using custom start time %s" % dt_timestamp)
        SESSION_START = dt_timestamp
    else:
        SESSION_START = datetime.utcnow()
    logging.debug('Session start: %s' % (SESSION_START))
    logging.debug('App start time: %s' % (APP_START_TIME))
    while True:
        timeout_exceeded = datetime.now() > reconfirmation_timeout
        logging.debug('Timeout exceeded: %s. Current time: %s. Timeout: %s' % (timeout_exceeded, datetime.now(), reconfirmation_timeout))
        if timeout_exceeded:
            input("\n\nAre you still streaming? Press any key to continue updating stats...")
            reconfirmation_timeout = datetime.now() + timedelta(hours=RECONFIRMATION_TIMEOUT_HOURS)
        player_stats = get_player_stats(PLAYER_ID)
        if ((MATCHES_TICKER_ENABLED == True) or (MATCHES_ENABLED == True)) and ((SESSION_STATS_ENABLED == False) and (SESSION_STATS_GRAPHS_ENABLED == False)):
            match_history = get_match_history(TICKER_GAME_HISTORY_DEPTH)
        elif((SESSION_STATS_ENABLED == True) or (SESSION_STATS_GRAPHS_ENABLED == True)):
            match_history = get_match_history()
        if MATCHES_TICKER_ENABLED == True:
            write_ticker_to_file(match_history)
        if MATCHES_ENABLED == True:
            write_matches_to_file(match_history)
        if PLAYER_STATS_ENABLED == True:
            write_player_stats_to_file(player_stats['player_rank'], player_stats['player_points'], player_stats['player_ratio'])
        if SESSION_STATS_ENABLED == True:
            write_session_stats_to_file(SESSION_START, match_history, session_start_player_stats, player_stats)
        if SESSION_STATS_GRAPHS_ENABLED == True:
            write_session_points_to_graph(SESSION_START, match_history, session_start_player_stats['player_name'], SESSION_START)
        
        logging.info(f"Sleeping for {REFRESH_RATE_SECS} seconds")
        time.sleep(REFRESH_RATE_SECS)

if __name__ == "__main__":
    main()
