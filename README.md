# ra-obs-stats

Running this script will grab various statistics from the cncstats API, at regular intervals, and output them into text files which can be used in (SL)OBS.

A few notes before you get started:

* The script is written in Python, so you need Python installed to run it. **You only need to do this once** (the quick start guide will walk you through it).
* You **should** run the script before you start streaming. If you don't, you'll see stale stats in your text boxes in OBS. It will work fine if you start the script after you start streaming.
  * If you follow the quick start guide, you'll just need to double click the shortcut on your desktop
* You **should** stop the script when you finish your stream, by closing the script window, as not to waste resources via the cncstats API.

## Options

* `--player-stats` writes players rank, points and win/loss ratio to `player_rank.txt`, `player_points.txt` and `player_win_ratio.txt`
* `--matches-ticker` writes a summary of the last 3 games played to `ticker.txt`
* `--session-stats` writes the number of games played and points difference since the beginning of the session (session starts when the script starts) to `session_games_played.txt` and `session_points_change.txt`

## Quick start guide

### Get the script ready

* Download and install Python from **[here](https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe)**
  * **Make sure 'Add Python 3.10 to PATH' checkbox is selected before pressing 'Install Now'**
  * ![install_python](https://i.imgur.com/So6mfwM.png)
  * Ensure that `python` is available by opening Windows Command Prompt
    * Click start, type `cmd` and press enter (or click `Command Prompt`)
    * In the command prompt, type `python`, you should see...
    * ![](https://i.imgur.com/xrdSugB.png)
    * Type `exit()` and press enter to close python
* Download `ra-obs-stats.py` from **[here](https://raw.githubusercontent.com/thenobo/ra-obs-stats/main/ra-obs-stats.py)** (right click -> 'Save link as')
* Right click on your desktop and create a new shortcut
  * ![](https://i.imgur.com/DkpLW8I.png)
  * Click 'Browse' and find `ra-obs-stats.py` which you downloaded
    * ![](https://i.imgur.com/5q5hngY.png)
  * Add the options to the script depending on what you want the script to provide
    * Put the options at the very end of the text in the `Type the location of the item` box. Either after the `.py` or `.py"`
    * You **must** provide your player ID (which can be found via [cncstats](http://cnc-stats.azurewebsites.net/) or [cnc.community](https://cnc.community/command-and-conquer-remastered/leaderboard/red-alert) websites)
      * ![](https://i.imgur.com/MsNkFSs.png)
    * You must also provide **at least one** of the following options `--player-stats`, `--matches-ticker` or `--session-stats`
    * ![](https://i.imgur.com/y9BsFiK.png)
    * Your text box should look like one of the following examples:
      * `C:\Users\nobo\Downloads\ra-obs-stats.py --player-stats 76561199198631818`
      * `"C:\Users\the nobo\Downloads\ra-obs-stats.py" --player-stats 76561199198631818`
      * `"C:\Users\the nobo\Downloads\ra-obs-stats.py" --player-stats --matches-ticker --session-stats 76561199198631818`
  * Press next and then 'Finish'.
  * Double click the shortcut you just created, you should see something similar to this
    * ![](https://i.imgur.com/42gTsIw.png)
  * In the location where you downloaded `ra-obs-stats.py` you should see some text files produced by the script. These text files will change depending on the options you passed to the script (`--player-stats`, `--matches-ticker` etc)
    * ![](https://i.imgur.com/bDesnvr.png)

### Add the text files to (SL)OBS

* In SL(OBS) add a new Text (GDI+) source to your scene
  * ![](https://i.imgur.com/k0rINVM.png)
* In the 'Settings for Text (GDI+)' window, tick 'Read from File' and select 'Browse'
  * ![](https://i.imgur.com/bU4bT5t.png)
  * Browse to the location of the text file outputs (in the same directory as `ra-stats-obs.py`)
    * ![](https://i.imgur.com/CThLb6M.png)
  * Repeat the above for each statistic you want to show
