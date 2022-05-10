#!/usr/bin/env python3
# Author, David Martinez (@dx0xm)(david.martinez@spark.co.nz)
import os, json
from si_automation.pmp.pmp import pmp
from paramiko import SSHClient, AutoAddPolicy

def main():

    PMP_TOKEN = os.environ['PMP_TOKEN']
    PMP_URL = os.environ['PMP_URL']
    #PMP setup
    pmp_object = pmp(PMP_URL, PMP_TOKEN)
    if pmp_object.error is not None:
        print(pmp_object.error)
        return 0

    devices = [
        'sibnaasma002.dmz.sdp.net.nz',
        'sibnaasma003.dmz.sdp.net.nz',
        'sibnaasma007.dmz.sdp.net.nz',
        'sibnaasma008.dmz.sdp.net.nz',
        'sibnaasma009.dmz.sdp.net.nz',
        'sibnaasma011.dmz.sdp.net.nz',
        'sibnaawsa002.dmz.sdp.net.nz',
        'sibnaawsa003.dmz.sdp.net.nz',
        'sibnaawsa007.dmz.sdp.net.nz',
        'sibnaawsa008.dmz.sdp.net.nz',
        'sibnaawsa009.dmz.sdp.net.nz',
        'sibnaawsa011.dmz.sdp.net.nz',
        'cwsnaawsa099.mgmt.sdp.net.nz',        
    ]
    res = {}
    for d in devices:
        host = d.split('.')[0].lower()
        if d == 'cwsnaawsa099.mgmt.sdp.net.nz':
            username = 'T820350'
            pass_obj, error = pmp_object.get_credentials_for_account('temgen1', 'admin')
            if error is not None:
                print(f'Cant get the password {error}')
                continue
        else:
            username = 'admin'
            pass_obj, error = pmp_object.get_credentials_for_account(host.upper(), 'admin')
            if error is not None:
                print(f'Cant get the password {error}')
                continue

        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(d, username=username, password=pass_obj["PASSWORD"])
        _, stdout, _ = client.exec_command('status detail')
        out1 = stdout.readlines()
        _, stdout, _ = client.exec_command('version')
        out2 = stdout.readlines()
        client.close()
        version = ''
        hardware = ''
        serial = ''
        for line in out2:
            if 'Model:' in line:
                hardware = line.split(':')[1].strip()
            if 'Version:' in line:
                version = line.split(':')[1].strip()
            if 'Serial' in line:
                serial = line.split(':')[1].strip()
        cpu_use = ''
        mem_use = ''
        disk_use = '' 
        conn_in = ''
        conn_out = ''
        tput_mbsec = ''
        conn_client = ''
        conn_server = ''
        if 'sma' in host:
            for line in out1:
                if 'Total' in line:
                    cpu_use = line.split()[1].strip()
                if 'RAM Utilization' in line:
                    mem_use = line.split()[-1].strip()
                if 'Logging Disk Usage' in line:
                    disk_use =  line.split()[-1].strip()
                if 'Current Inbound Conn' in line:
                    conn_in =  line.split()[-1].strip()
                if 'Current Outbound Conn' in line:
                    conn_out =  line.split()[-1].strip()
        else:
            for idx, line in enumerate(out1):
                if 'CPU' in line:
                    cpu_use = line.split()[1].strip()
                if 'RAM' in line:
                    mem_use = line.split()[1].strip()
                if 'Reporting/Logging' in line:
                    disk_use =  line.split()[-1].strip()
                if 'Bandwidth (Mbps):' in line:
                    tput_mbsec =  out1[idx+3].split()[-1].strip()
                if 'Connections:' in line:
                    conn_client =  out1[idx+3].split()[-1].strip()
                    conn_server =  out1[idx+4].split()[-1].strip()


        
        print('#'*8)
        print(host)
        #[print(x) for x in out]
        # if len(cpu_use + mem_total + mem_use + tput_kbsec + sessions) > 0:
        if 'wsa' in host:
            res.update({host: dict(device_class='proxy', vendor='cisco', version=version, hardware=hardware, ip='', source='Grants head', serial=serial, cpu_use=cpu_use, mem_use=mem_use, disk_use=disk_use,
                                conn_in=conn_in, conn_out=conn_out, tput_mbsec=tput_mbsec, conn_client=conn_client, conn_server=conn_server )})
        else:
            res.update({host: dict(device_class='management tool', vendor='cisco', version=version, hardware=hardware, ip='', source='Grants head', serial=serial, cpu_use=cpu_use, mem_use=mem_use, disk_use=disk_use,
                                conn_in=conn_in, conn_out=conn_out, tput_mbsec=tput_mbsec, conn_client=conn_client, conn_server=conn_server )})

        print(res[host])
        # else:
        #     print(out)

    with open('proxy_devices.json', 'w') as json_file:
        json.dump(res, json_file)               

if __name__ == "__main__":
    main()        