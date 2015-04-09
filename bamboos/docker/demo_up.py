#!/usr/bin/env python

import os
from environment import common, docker

#===== input =======
sl_builder_image = 'onedata/sl_builder:v2'
builder_image = 'onedata/worker'

config_dir = '/home/kzemek/plgrid/dev_scripts/cfg'

globalregistry_pkg_dir = '/home/kzemek/plgrid/globalregistry/rel'
globalregistry_pkg_name = 'globalregistry-v2.1.0.64.g29c6ff5-1.x86_64.rpm'

provider_pkg_dir = '/home/kzemek/plgrid/bamboos/release/build'
provider_pkg_name = 'oneprovider-2.5.5-1.el6.x86_64.rpm'

direct_storage = '/home/kzemek/plgrid/oneclient/mnt'
username = 'plgkzemek' 
#===================

dns, dns_output = common.set_up_dns('auto', 'onedata')
gr_name = 'gr_onedata'
gr = docker.run(
    image=sl_builder_image,
    hostname='gr.onedata.dev.docker',
    detach=True,
    interactive=True,
    tty=True,
    workdir='/root',
    name=gr_name,
    volumes=[(globalregistry_pkg_dir, '/root/pkg', 'ro'),
             (config_dir, '/root/cfg', 'ro')],
    dns_list=dns,
    command='yum localinstall -y pkg/' + globalregistry_pkg_name + ' && sleep 5 && onepanel_admin --install /root/cfg/gr.cfg ; bash')

provider1 = docker.run(
    image=sl_builder_image,
    hostname='provider1.onedata.dev.docker',
    detach=True,
    interactive=True,
    tty=True,
    workdir='/root',
    name='provider1_onedata',
    volumes=[(provider_pkg_dir, '/root/pkg', 'ro'),
             (config_dir, '/root/cfg', 'ro'),
             (direct_storage, '/mnt', 'rw')],
    dns_list=dns,
    link={gr_name: 'onedata.org'},
    envs={'ONEPANEL_MULTICAST_ADDRESS': '238.255.0.1'},
    run_params=['--privileged=true'],
    command='useradd plgkzemek -G fuse;' + 'yum localinstall -y pkg/' + provider_pkg_name + '''
sleep 5
onepanel_admin --install /root/cfg/prov1.cfg
bash''')

provider2 = docker.run(
    image=sl_builder_image,
    hostname='provider2.onedata.dev.docker',
    detach=True,
    interactive=True,
    tty=True,
    workdir='/root',
    name='provider2_onedata',
    volumes=[(provider_pkg_dir, '/root/pkg', 'ro'),
             (config_dir, '/root/cfg', 'ro')],
    dns_list=dns,
    link={gr_name: 'onedata.org'},
    run_params=['--privileged=true'],
    command='yum localinstall -y pkg/' + provider_pkg_name + '''
sleep 5
onepanel_admin --install /root/cfg/prov2.cfg
bash''')

print '/etc/hosts entries:'
print docker.inspect('gr_onedata')['NetworkSettings']['IPAddress'], 'onedata.org'
print docker.inspect('provider1_onedata')['NetworkSettings']['IPAddress'], 'provider1.onedata.dev.docker'
print docker.inspect('provider2_onedata')['NetworkSettings']['IPAddress'], 'provider2.onedata.dev.docker'
print ''
print([gr, provider1, provider2])
