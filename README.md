# zpool-monitor
Python script to monitor Zpool status and sends reports to Discord and by email using SendGrid.

There are 2 scripts here, the `zpool-status.py` script will send all notifications when it runs, even if everything is ok, so that you can be fully aware of the status.  The second script, `zpool-monitor-hourly.py` will only send alerts when there is an error present.  I set the "only on error" script to run hourly, and the other one to daily at a specific time.

### Setup Instructions:
1. Create venv: `python3 -m venv .`
2. Use that venv Python install to install dependencies: `./bin/pip install -r ./requirements.txt`
3. Configure the `.env` file.
4. Use that venv Python to run the scripts: `./bin/python zpool-status.py` -or- `./bin/python zpool-monitor-hourly.py`
5. Set either or both scripts to rin on a schedule: (first one is hourly, second is daily at 8:oopm)
```
0 * * * * /home/user/path/to/your/venv/zpool-monitor/bin/python /home/user/path/to/your/venv/zpool-monitor/zpool-monitor-hourly.py
0 20 * * * /home/user/path/to/your/venv/zpool-monitor/bin/python /home/user/path/to/your/venv/zpool-monitor/zpool-status.py
```
6. Profit!
