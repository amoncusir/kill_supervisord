# kill Supervisord #

Simple project to host a Supervisord Event listener

## Download

```bash
wget https://github.com/amoncusir/kill_supervisord/releases/download/1.0/kill_superd.py
```

## What is it and how it work?

It's a simple script written in Python (+2.7) that implements the `Event Listener` interface of Supervisord.
[See this link for more details](http://supervisord.org/events.html).

The main propose is to kill the Supervisord when the assigned process dies. This helps in the Docker environments when
need pass to Docker the life-cycle of a service.

This script has two ways to kill the Supervisord process.
- **The Normal and recommended** way is getting the PID number from the `.pid` file, to default
`/var/run/supervisord.pid` and send the `SIGQUIT` kill signal.
- **The force way** is using the Docker API, sending the kill command
([See Docker API](https://docs.docker.com/engine/api/v1.40/#operation/ContainerKill))

## Usage

Help info:

```text
usage: kill_superd.py [-h] [-f] [-l] [-p PID_PATH] [-n NAME]

SupervisorD Event listener: Killer

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           Force kill container using Docker API
  -l, --last-resource   Force kill container if have any error when try to
                        kill using PID signal
  -p PID_PATH, --pid-path PID_PATH
                        Supervisord pid path
  -n NAME, --name NAME  Process name to stop
```

Default values:

```text
-f, --force                -> False
-l, --last-resource        -> True
-p PID_PATH, --pid-path    -> '/var/run/supervisord.pid'
-n NAME, --name NAME       -> mainprocess
```

In Supervisord config:

```ini
; Event listener to watch the main process and kill supervisord if it dies
[eventlistener:superkiller]
command=python /<path_to_script>/kill_superd.py <optional args>
events=PROCESS_STATE_EXITED,PROCESS_STATE_FATAL,PROCESS_STATE_UNKNOWN
startsecs=0
```

## Example Configuration:



```ini
[supervisord]
logfile=/var/log/supervisord/supervisord.log
childlogdir=/var/log/supervisord/
pidfile=/var/run/supervisord.pid
loglevel=debug
nodaemon=true

[eventlistener:superkiller]
command=python /usr/local/bin/kill_superd.py -n longping ; NOTE: The name of the process is the name of program!
events=PROCESS_STATE_EXITED,PROCESS_STATE_FATAL,PROCESS_STATE_UNKNOWN
startsecs=0

[program:longping]
command=ping -c 20 8.8.8.8
; process_name=longping ; Using the attribute process_name can set to many programs the same name!
autostart=true
autorestart=false
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
startsecs=0

[program:shortping]
command=ping -c 5 1.1.1.1
; process_name=longping ; Using the attribute process_name can set to many programs the same name!
autostart=true
autorestart=false
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
startsecs=0
```
 
