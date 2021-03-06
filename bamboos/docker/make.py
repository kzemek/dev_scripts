#!/usr/bin/env python

"""Runs a command in a dockerized development environment. The files are copied
from 'source directory' to 'output directory' and then the command is ran.
The copy operation is optimized, so that only new and changed files are copied.
The script uses user's SSH keys in case dependency fetching is needed.

Unknown arguments will be passed to the command.

Run the script with -h flag to learn about script's running options.
"""

from os.path import expanduser
import argparse
import os
import platform
import sys

from environment import docker


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='Run a command inside a dockerized development environment.')

parser.add_argument(
    '-i', '--image',
    action='store',
    default='onedata/builder:v5',
    help='docker image to use for building',
    dest='image')

parser.add_argument(
    '-s', '--src',
    action='store',
    default=os.getcwd(),
    help='source directory to run make from',
    dest='src')

parser.add_argument(
    '-d', '--dst',
    action='store',
    default=None,
    help='destination directory where the build will be stored; defaults '
          'to source dir if unset',
    dest='dst')

parser.add_argument(
    '-k', '--keys',
    action='store',
    default=expanduser("~/.ssh"),
    help='directory of ssh keys used for dependency fetching',
    dest='keys')

parser.add_argument(
    '-r', '--reflect-volume',
    action='append',
    default=[],
    help="host's paths to reflect in container's filesystem",
    dest='reflect')

parser.add_argument(
    '-c', '--command',
    action='store',
    default='make',
    help='command to run in the container',
    dest='command')

parser.add_argument(
    '-w', '--workdir',
    action='store',
    default=None,
    help='path to the working directory; defaults to destination dir if unset',
    dest='workdir'
)

[args, pass_args] = parser.parse_known_args()
home = expanduser('~')

destination = args.dst if args.dst else args.src
workdir = args.workdir if args.workdir else destination

command = '''
import os, shutil, subprocess, sys

os.environ['HOME'] = '{home}'

ssh_home = '/root/.ssh'
if {shed_privileges}:
    subprocess.call(['useradd', '--create-home', '--uid', '{uid}', 'maketmp'])
    ssh_home = '/home/maketmp/.ssh'
    os.setregid({gid}, {gid})
    os.setreuid({uid}, {uid})

if '{src}' != '{dst}':
    ret = subprocess.call(['rsync', '--archive', '/tmp/src/', '{dst}'])
    if ret != 0:
        sys.exit(ret)

shutil.copytree('/tmp/keys', ssh_home)
for root, dirs, files in os.walk(ssh_home):
    for dir in dirs:
        os.chmod(os.path.join(root, dir), 0o700)
    for file in files:
        os.chmod(os.path.join(root, file), 0o600)

sh_command = 'eval $(ssh-agent) > /dev/null; ssh-add 2>&1; {command} {params}'
ret = subprocess.call(['sh', '-c', sh_command])
sys.exit(ret)
'''
command = command.format(
    command=args.command,
    params=' '.join(pass_args),
    uid=os.geteuid(),
    gid=os.getegid(),
    src=args.src,
    dst=destination,
    home=home,
    shed_privileges=(platform.system() == 'Linux'))

reflect = [(home, 'ro'), (destination, 'rw')]
reflect.extend(zip(args.reflect, ['rw'] * len(args.reflect)))

ret = docker.run(tty=True,
                 interactive=True,
                 rm=True,
                 reflect=reflect,
                 volumes=[(args.keys, '/tmp/keys', 'ro'),
                          (args.src, '/tmp/src', 'ro')],
                 workdir=workdir,
                 image=args.image,
                 command=['python', '-c', command])
sys.exit(ret)
