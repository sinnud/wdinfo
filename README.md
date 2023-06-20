## NAS data manager

### NAS info
- We have two WD hard driver: `wdmycloud` and `mycloud-ejh1st`.

### Sync function
- When we have new files on `wdmycloud`, we like to copy to `mycloud-ejh1st`.
- If some files dropped from `wdmycloud`, we don't drop it from `mycloud-ejh1st`.

### Search function
- Allow to search files from `wdmycloud`.

### SQLite
- Use SQLite as database, which is simple one.
- sqlite3.OperationalError: unable to open database file
  - On unix I got that error when using the `~` shortcut for the user directory. Changing it to `/home/user` resolved the error.

### Gunicorn
- learn to use `gunicorn`.
- `conda install gunicorn`
- Create `wdinfoapp.py`.
- `gunicorn -w 4 wdinfoapp:app`
- Local machine web browser with URL `localhost:8000`
- In order to let another computer access it:
  - `gunicorn -w 4 -b 0.0.0.0:8000 wdinfoapp:app`
  - Another computer will use this computer IP instead of localhost: `192.168.86.144:8000`
- If one mission need more time, default setting will timeout
  - Set without timeout: `gunicorn -w 1 -b 0.0.0.0:8000 wdinfoapp:app --timeout 0`
  - Set timeout 0 means never timeout
  - We can set timeout with 120 which means it will timeout in 120 seconds (2 minutes)
  - Here change worker setting to 1 such that only one Gunicorn worker
- Shell command instead of web browser: `curl localhost:8000`

### Miniconda
- learn to use `conda` as Python ENV.
- Start from https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf
  - `conda create --name wdinfo python=3.10`
  - `conda activate wdinfo`