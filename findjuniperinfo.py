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

    pass_obj, error = pmp_object.get_credentials_for_account('temgen1', 'admin')
    if error is not None:
        print(f'Cant get the password {error}')
        return 0

    devices = [
        'mdrcorfwl09.mgmt.sdp.net.nz',
        'mdrcorfwl10.mgmt.sdp.net.nz',
        'wn1corfwl01.mgmt.sdp.net.nz',
        'wn1corfwl02.mgmt.sdp.net.nz',
        'wn1mgtfwl01.mgmt.sdp.net.nz',
        'wn1mgtfwl02.mgmt.sdp.net.nz',      
    ]
    res = {}
    for d in devices:
        host = d.split('.')[0].lower()
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(d, username='T820350', password=pass_obj["PASSWORD"])
        _, stdout, _ = client.exec_command('show version')
        out1 = stdout.readlines()
        _, stdout, _ = client.exec_command('show chassis routing-engine')
        out2 = stdout.readlines()
        client.close()
        version = ''
        hardware = ''
        for line in out1:
            if 'Model:' in line:
                hardware = line.split(':')[1].strip()
            if 'JUNOS Software Release' in line:
                version = line.split('[')[1].strip().replace(']','')
            if 'node1' in line:
                break
        cpu_use = ''
        mem_use = ''
        for line in out2:
            if 'Idle' in line:
                cpu_use = str(100 - int(line.split()[1].strip())) + ' %'
            if 'Memory utilization' in line:
                mem_use = line.split('Memory utilization')[1].strip().replace('percent','%')
            if 'node1' in line:
                break                

        
        print('#'*8)
        print(host)
        # [print(x) for x in out1]
        # [print(x) for x in out2]
        # if len(cpu_use + mem_total + mem_use + tput_kbsec + sessions) > 0:
        res.update({host: dict(vendor='juniper', ip='', version=version, hardware=hardware, source='Vishals head', cpu_use=cpu_use, mem_use=mem_use)})
        print(res[host])

    with open('juniper_devices.json', 'w') as json_file:
        json.dump(res, json_file)               

if __name__ == "__main__":
    main()        