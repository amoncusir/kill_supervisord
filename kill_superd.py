#!/usr/bin/env python

# Supervidord event listener
# See http://supervisord.org/events.html#event-listener-notification-protocol
#

import sys
import os
import signal
import argparse
import docker
from supervisor.childutils import listener


def write_stdout(message):
    """Only eventlistener protocol messages may be sent to stdout"""
    sys.stdout.write(message)
    sys.stdout.flush()


def write_stderr(message):
    sys.stderr.write(message + '\n')
    sys.stderr.flush()


def set_ready_state():
    """Transition from ACKNOWLEDGED to READY"""
    write_stdout('READY\n')


def set_success_state():
    """transition from READY to ACKNOWLEDGED"""
    write_stdout('RESULT 2\nOK')


def set_failed_state():
    """transition from READY to ACKNOWLEDGED"""
    write_stdout('RESULT 4\nFAIL')


def get_container_id():
    with open('/proc/1/cpuset', 'r') as cpu_set:
        return cpu_set.readline().replace('\n', '').split('/')[2]


def can_access_docker_api():
    return os.path.exists('/var/run/docker.sock')


def kill_docker_container():
    container_id = get_container_id()
    write_stderr("Kill container with ID: {}".format(container_id))

    client = docker.from_env()
    container = client.containers.get(container_id)
    container.kill()


def main(pid_file_path, last_resource, process_name, force):

    # Standard spec.
    while True:

        # For debug proposes and wait event data
        # because this script only is called when the main program dies
        headers, body = listener.wait(sys.stdin, sys.stdout)
        body = dict([pair.split(":") for pair in body.split(" ")])

        write_stderr("Headers: %r" % repr(headers))
        write_stderr("Body: %r" % repr(body))

        if process_name == body['processname']:

            write_stderr("Init Kill Supervisord...")

            if not can_access_docker_api():
                write_stderr('WARN: Can not force kill the docker container!')

            try:
                if force and can_access_docker_api():
                    write_stderr("Force kill container")
                    kill_docker_container()

                else:
                    with open(pid_file_path, 'r') as pid_file:
                        pid = int(pid_file.readline())
                        write_stderr("Kill PID {}".format(pid))
                        os.kill(pid, signal.SIGQUIT)

            except Exception as e:
                write_stderr('Could not kill supervisord: ' + str(e))

                if last_resource and can_access_docker_api():
                    write_stderr("Force kill container")
                    kill_docker_container()

        else:

            write_stderr("Ignore the process died...")

        # Set success state to not enter in an infinite loop
        set_success_state()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SupervisorD Event listener: Killer")
    parser.add_argument('-f', '--force', help='Force kill container using Docker API',
                        default=False, action='store_true')
    parser.add_argument('-l', '--last-resource', help='Force kill container if have any error when try to kill using '
                                                      'PID signal',
                        default=True, action='store_true')
    parser.add_argument('-p', '--pid-path', help='Supervisord pid path', default='/var/run/supervisord.pid')
    parser.add_argument('-n', '--name', help='Process name to stop', default='mainprocess')

    args = parser.parse_args()

    main(args.pid_path, args.last_resource, args.name, args.force)
