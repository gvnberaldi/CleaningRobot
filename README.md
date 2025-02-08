# CleaningRobot
A Python-based RESTful API for controlling a cleaning robot in a grid environment. Supports setting maps, executing cleaning routines, handling obstacles, and storing session history.

## API Usage

To interact with the API, you can use the following `curl` commands:

### 1. Set Map

To upload a map file (in txt or json format):

```bash
curl -X POST -F "file=@your_map_file.[txt, json]" http://localhost:5000/set-map
```

### 2. Start a cleaning session

To start a cleaning session:

```bash
curl -X POST -F "file=@your_actions_file.[txt, json]" http://localhost:5000/clean
```
Where ```@your_actions_file.[txt, json]``` is a txt or json file containing a strating position and a ordered list of actions.
### 3. Download History

To download the history data in CSV format:

```bash
curl -o output.csv http://127.0.0.1:5000/history
```
