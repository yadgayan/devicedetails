#!/usr/bin/env python3
# Author, David Martinez (@dx0xm)(david.martinez@spark.co.nz)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

EXAMPLES = """
  - name: Get show commands to get more info
    debug:
      msg: "{{ lookup('asr_getcommands',LISTOFSHOWRUNITEMS, CHOICE) }}"
"""

RETURN = """
  _raw:
    description:
      - Get extra show commands to run in a cisco ASR. Input list is a group of items from show run | i LABEL
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
import ipaddress, json

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        device = terms[0]
        results = terms[1]

        try:
            with open('f5_devices.json', 'r') as json_file:
                f5_devices = json.load(json_file)
        except FileNotFoundError:
            f5_devices = dict()
        except Exception as e:
            print(str(e))
            return 0

        host = device.split('.')[0].lower()
        candidates = {}
        if host not in f5_devices:
            active_conn = ''
            cpu_use = ''
            mem_use = ''
            tput_service_bsec =  ''
            tput_in_bsec =  ''
            tput_out_bsec =  ''
            for l in results:
                for idx, line in enumerate(l):
                    if 'Active Connections' in line:
                        active_conn = l[idx+2].split()[2].strip()
                    if 'System CPU Usage' in line:    
                        cpu_use = l[idx+2].split()[2].strip()
                    if 'TMM Memory Used' in line:
                        mem_use = line.split()[4].strip()
                    if 'TMM Alloc Memory' in line:
                        mem_use = l[idx+1].split()[4].strip() + ' of ' + line.split()[4].strip()
                    if 'Throughput(bits)' in line:
                        if 'Service' in l[idx+2]:
                            tput_service_bsec =  l[idx+2].split()[2].strip()
                            tput_in_bsec =  l[idx+3].split()[2].strip()
                            tput_out_bsec =  l[idx+4].split()[2].strip()
                        else:
                            tput_in_bsec =  l[idx+2].split()[2].strip()
                            tput_out_bsec =  l[idx+3].split()[2].strip()
            candidates.update({host: dict(cpu_use=cpu_use, mem_use=mem_use, disk_total='', disk_use='', disk_free='', 
                                          disk_total_root='', disk_use_root='', disk_total_var='', disk_use_var='',
                                          mem_free='', mem_total='', sessions='', tput_kbsec='', 
                                          active_conn=active_conn, tput_service_bsec=tput_service_bsec, tput_in_bsec=tput_in_bsec, tput_out_bsec=tput_out_bsec,
                                          conn_in='', conn_out='', tput_mbsec='', conn_client='', conn_server='')})
            f5_devices.update(candidates)                
            with open('f5_devices.json', 'w') as json_file:
                json.dump(f5_devices, json_file)             

        return [candidates]
