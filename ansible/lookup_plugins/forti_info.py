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
        env = terms[2]
        ip = terms[3]
        host = device.split('.')[0].lower()
        fl = 'fortim_devices.json'
        source = ''
        if env == 'dmz':
            source = 'manual vm export'
        elif env == 'mgt':
            source = 'manual vm export'
        elif env == 'n4l':
            source = 'Tinus Head'
        
        if ip.count('.') != 3:
            ip = ''


        try:
            with open(fl, 'r') as json_file:
                forti_devices = json.load(json_file)
        except FileNotFoundError:
            forti_devices = dict()
        except Exception as e:
            print(str(e))
            return 0

        ret = {host: dict(device_class='management tool', vendor='fortinet', ip=ip, version='', hardware='', source=source)}
        if host not in forti_devices:
            version = ''
            hardware = ''
            cpu_use = ''    
            mem_total = ''
            mem_use = ''
            disk_use = ''
            disk_total = ''
            serial = ''
            for cmd in results:
                if 'status' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if 'Version' in line[0:10]:
                            version = line.split(':')[1].strip()
                        if 'Serial' in line:
                            serial = line.split(':')[1].strip()
                        if 'Platform Full' in line:
                            hardware = line.split(':')[1].strip()
                elif 'performance' in cmd['item']:
                    for idx, line in enumerate(cmd['stdout_lines']):
                        if 'CPU:' in line:
                            cpu_use = cmd['stdout_lines'][idx+1].split(':')[1].strip()
                        if 'Memory' in line:
                            mem_total = cmd['stdout_lines'][idx+1].split(':')[1].strip()
                            mem_use = cmd['stdout_lines'][idx+2].split(':')[1].strip().replace('\t', ' ')
                        if 'Hard Disk' in line:
                            disk_total = cmd['stdout_lines'][idx+1].split(':')[1].strip()
                            disk_use = cmd['stdout_lines'][idx+2].split(':')[1].strip().replace('\t', ' ')

            ret[host]['version'] = version
            ret[host]['hardware'] = hardware
            ret[host].update(serial=serial, cpu_use=cpu_use, mem_total=mem_total, mem_use=mem_use, disk_total=disk_total, disk_use=disk_use)

            forti_devices.update(ret)        
            with open(fl, 'w') as json_file:
                json.dump(forti_devices, json_file) 

        return [ret]
