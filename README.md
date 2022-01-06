# ra-obs-stats

Running this script will grab various statistics from cncstats, at regular intervals, and output them into text files which can be used in (SL)OBS. It's written in Python, so Python 3.8+ must be installed before running it.

## Quick start guide

### Get the script ready

* Download and install Python from **[here](https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe)**
  * Make sure 'Add Python 3.10 to PATH' checkbox is selected before pressing 'Install Now'
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
    * ![](https://i.imgur.com/y9BsFiK.png)
  * Press next and then 'Finish'.
  * Double click the shortcut you just created, you should see something similar to this
    * ![](https://i.imgur.com/42gTsIw.png)
  * In the location where you downloaded `ra-obs-stats.py` you should see some text files produced by the script
    * ![](https://i.imgur.com/bDesnvr.png)

### Add the text files to (SL)OBS

* In SL(OBS) add a new Text (GDI+) source to your scene
  * ![](https://i.imgur.com/k0rINVM.png)
* In the 'Settings for Text (GDI+)' window, tick 'Read from File' and select 'Browse'
  * ![](https://i.imgur.com/bU4bT5t.png)
  * Browse to the location of the text file outputs (in the same directory as `ra-stats-obs.py`)
    * ![](https://i.imgur.com/CThLb6M.png)
  * Repeat the above for each statistic you want to show
