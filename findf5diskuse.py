#!/usr/bin/env python3
# Author, David Martinez (@dx0xm)(david.martinez@spark.co.nz)
import os, socket, json
from si_automation.pmp.pmp import pmp
from paramiko import SSHClient, AutoAddPolicy

def sshcommand(host, username, password):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(host, username=username, password=password)
    channel = client.invoke_shell()
    channel.settimeout(10)
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')
    out = []
    try:
        stdin.write('''
        bash
        df -h
        exit
        quit
        ''')
        # print(stdout.read())
        out = [str(x, encoding="utf-8") for x in stdout.readlines()]
    except socket.timeout:
        print(f'Timeout triggered for {host}')

    stdout.close()
    stdin.close()
    client.close()

    return out

def main():

    PMP_TOKEN = os.environ['PMP_TOKEN']
    PMP_URL = os.environ['PMP_URL']
    #PMP setup
    pmp_object = pmp(PMP_URL, PMP_TOKEN)
    if pmp_object.error is not None:
        print(pmp_object.error)
        return 0

    devices = [
        'mdrcorlbs09.mgmt.sdp.net.nz',
        'mdrcorlbs10.mgmt.sdp.net.nz',
        'mdrhzblbs03.mgmt.sdp.net.nz',
        'mdrhzblbs04.mgmt.sdp.net.nz',
        'mdrcorlbs11.mgmt.sdp.net.nz',
        'mdrcorlbs12.mgmt.sdp.net.nz',
        'mdrcorlbs13.mgmt.sdp.net.nz',
        'mdrcorlbs14.mgmt.sdp.net.nz',
        'wn1corlbs05.mgmt.sdp.net.nz',
        'wn1corlbs06.mgmt.sdp.net.nz',
        'n4ldmzvpn011.mgmt.sdp.net.nz',
        'n4ldmzvpn012.mgmt.sdp.net.nz',
        'adcnaalbs001.mgmt.sdp.net.nz',
        'adcnaalbs002.mgmt.sdp.net.nz',
        'mdrdmzvpn09.mgmt.sdp.net.nz',
        'mdrdmzvpn10.mgmt.sdp.net.nz',
        'mdrdmzvpn015.mgmt.sdp.net.nz',
        'mdrdmzvpn016.mgmt.sdp.net.nz',
        'mdrdmzvpn017.mgmt.sdp.net.nz',
        'mdrdmzvpn018.mgmt.sdp.net.nz',
        'mdrcorlbs15.mgmt.sdp.net.nz',
        'mdrcorlbs16.mgmt.sdp.net.nz',
        'mdrcorlbs17.mgmt.sdp.net.nz',
        'mdrcorlbs18.mgmt.sdp.net.nz',
        # 'mdrcorlbs08.mgmt.sdp.net.nz',
        # 'wn1corlbs03.mgmt.sdp.net.nz',
        # 'wn1corlbs04.mgmt.sdp.net.nz',
    ]

    #Getting passwords
    pass_obj, error = pmp_object.get_credentials_for_account('temgen1', 'admin')
    if error is not None:
        print(f'Cant get the password {error}')
        return 0
    res = {}
    for d in devices:
        host = d.split('.')[0].lower()
        out = sshcommand(d, 'T820350', pass_obj["PASSWORD"])
        disk_total_root = ''
        disk_use_root = ''
        disk_total_var = ''
        disk_use_var = ''
        for idx, line in enumerate(out):
            if 'root' in line:
                if '% /' in line:
                    words = line.split()
                    disk_total_root = words[1].strip()
                    disk_use_root = words[2].strip() + ' ' + words[4].strip()
                else:
                    disk_total_root = out[idx+1].split()[0].strip()
                    disk_use_root = out[idx+1].split()[1].strip() + ' ' + out[idx+1].split()[-2].strip()
            if '_var' in line:
                if '% /' in line:
                    words = line.split()
                    disk_total_var = words[1].strip()
                    disk_use_var = words[2].strip() + ' ' + words[4].strip()
                else:
                    disk_total_var = out[idx+1].split()[0].strip()
                    disk_use_var = out[idx+1].split()[1].strip() + ' ' + out[idx+1].split()[-2].strip()
        print('#'*8)
        print(d)
        # [print(x) for x in out]
        # if len(disk_total_root + disk_use_root + disk_total_var + disk_use_var) > 0:
        res.update({host: dict(disk_total_root=disk_total_root, disk_use_root=disk_use_root, disk_total_var=disk_total_var, disk_use_var=disk_use_var)})
        print(res[host])
        # else:
        #     print(out)

    with open('f5_devices.json', 'w') as json_file:
        json.dump(res, json_file)            

if __name__ == "__main__":
    main()        