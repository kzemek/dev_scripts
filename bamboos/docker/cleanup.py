#!/usr/bin/env python

"""Cleans up Docker containers given by their name or id. Running containers are
killed first. Volumes are not removed automatically.

Run the script with -h flag to learn about script's running options.
"""

import argparse

from environment import docker


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='Clean up dockers.')

parser.add_argument(
    'docker_ids',
    action='store',
    nargs='*',
    help='IDs of dockers to be cleaned up')

args = parser.parse_args()

docker.remove(args.docker_ids, force=True)
