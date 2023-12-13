# Interview Test Task

Programming language: **Python**

- Automatic synchronization at specified intervals
- Detailed logging of changes made during synchronization
- Error handling for file copying and deletion


```
python3 interview.py -h
```

That command will output:

```
Synchronize two directories.

positional arguments:
  SOURCE_FOLDER   Path to the source folder
  REPLICA_FOLDER  Path to the replica folder
  INTERVAL_TIME   Interval time to check for changes
  LOG_FILE        Path to the log file

options:
  -h, --help      show this help message and exit
  -d, --days      Specify if the interval is in days
  -m, --minutes   Specify if the interval is in minutes
```

```
python3 interview.py <source_folder> <replica_folder> <[-d|-m] optional> <interval> <log_file>
```
