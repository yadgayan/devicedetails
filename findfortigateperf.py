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

    #Getting passwords
    pass_obj1, error = pmp_object.get_credentials_for_account('FG-MDR-SDP001', 'admin')
    if error is not None:
        print(f'Cant get the password {error}')
        return 0
    pass_obj2, error = pmp_object.get_credentials_for_account('MDRCORFWL01', 'admin')
    if error is not None:
        print(f'Cant get the password {error}')
        return 0

    res = {}
    for d in ['fg-mdr-sdp001.mgmt.sdp.net.nz', 'fg-mdr-sdp002.mgmt.sdp.net.nz', 'mdrcorfwl01.mgmt.sdp.net.nz', 'mdrcorfwl02.mgmt.sdp.net.nz']:
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        if 'fg' in d:
            client.connect(d, username='admin', password=pass_obj1["PASSWORD"])
        else:
            client.connect(d, username='admin', password=pass_obj2["PASSWORD"])
        _, stdout, _ = client.exec_command('config global \n get system performance status')
        out = stdout.readlines()
        client.close()         
        cpu_use = ''
        mem_total = ''
        mem_use = ''
        tput_kbsec =  ''
        sessions = ''
        for line in out:
            if 'CPU states' in line:
                cpu_use = line.split(':')[1].strip()
            if 'Memory:' in line:
                mem_total = line.split(':')[1].split(',')[0].strip()
                mem_use = line.split(':')[1].split(',')[1].strip()
            if 'Average network usage:' in line:
                tput_kbsec =  line.split(':')[1].split(',')[-1].strip()
            if 'Average sessions:' in line:
                sessions =  line.split(':')[1].split(',')[-1].strip()

        host = d.split('.')[0].lower()
        print('#'*8)
        print(host)
        if len(cpu_use + mem_total + mem_use + tput_kbsec + sessions) > 0:
            res.update({host: dict(type='', disk_total='', disk_use='', disk_free='', 
                                   disk_total_root='', disk_use_root='', disk_total_var='', disk_use_var='', mem_free='',
                                   cpu_use=cpu_use, mem_total=mem_total, mem_use=mem_use, tput_kbsec=tput_kbsec, sessions=sessions)})
            print(res[host])
        else:
            print(out)

    with open('fortig_devices.json', 'w') as json_file:
        json.dump(res, json_file)               

if __name__ == "__main__":
    main()        