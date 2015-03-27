About
=====

Scripts for starting demo environment.

Getting Started
---------------

1. Run make to build **onedata/sl_builder:v2** docker
2. Prepare globalregistry rpm: `./make.py -i onedata/sl_builder:v2 rpm`
3. Prepare oneprovider rpm: `release/oneprovider_rpm.sh` inside **bamboos/feature/demo2** repo.
4. Edit **bamboos/docker/demo_up.py** input vars
5. Kill all dockers: `docker rm -fv $(docker ps -aq)`
6. Run: `python2 ./bamboos/docker/demo_up.py`
7. Add routes printed by the script to `/etc/hosts`
8. You may want to check logs, or attach to **gr.onedata.dev.docker**, **provider1.onedata.dev.docker** **provider2.onedata.dev.docker** dockers; installation takes a while
9. 'https://onedata.org' is up, 'https://provider1.onedata.dev.docker:9443' and 'https://provider2.onedata.dev.docker:9443' need registration.

NOTE:
onedata.org will redirect you to 'https://[alias].onedata.org/[...]'. You need either redirect this to adequate IP, or replace '[alias].onedata.org' with 'provider1.onedata.dev.docker' manually

