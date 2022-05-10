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
        devtype = terms[2]

        host = device.split('.')[0].lower()
        if devtype == 'fw':
            ret = {host: dict(version='', hardware='')}
        else:
            ret = {host: dict(device_class='management tool', vendor='checkpoint', ip='', version='', hardware='', source='manual vm export')}

        try:
            with open('ckpm_devices.json', 'r') as json_file:
                ckpm_devices = json.load(json_file)
        except FileNotFoundError:
            ckpm_devices = dict()
        except Exception as e:
            print(str(e))
            return 0

        
        if host not in ckpm_devices:
            version = ''
            hardware = ''
            cpu_use = ''    
            mem_total = ''
            mem_free = ''
            disk_free = ''
            lics = []
            for cmd in results:
                if 'asset' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if devtype == 'fw':
                            if 'Model' in line:
                                hardware = line.split(':')[1].strip()
                                # hardware=line
                                break
                        else:
                            if 'Platform' in line:
                                hardware = line.split(':')[1].strip()
                                # hardware=line
                                break
                if 'version' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if 'Product version' in line:
                            version = line.split('Point')[1].strip()
                            # version=line
                            break                
                elif 'cpu' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if 'CPU Usage' in line:
                            cpu_use = line.split(':')[1].strip()
                            # cpu_use=line
                            break                
                elif 'memory' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if 'Total Real' in line:
                            mem_total = line.split(':')[1].strip()
                            # mem_total=line
                        elif 'Free Real' in line:
                            mem_free = line.split(':')[1].strip()
                            # mem_free=line
                elif 'disk' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if '/var/log' in line:
                            disk_free = line.split('|')[-2].strip()
                            # disk_free=line
                            break                
                elif 'cplic' in cmd['item']:
                    for line in cmd['stdout_lines']:
                        if 'CK-' in line:
                            lic = line[line.find('CK-'):]
                            if len(lic) > 0 and lic not in lics:
                                lics.append(lic)
            ret[host]['version'] = version
            ret[host]['hardware'] = hardware
            ret[host].update(cpu_use=cpu_use, mem_total=mem_total, mem_free=mem_free, disk_free=disk_free, license=lics)
            print(ret)
            ckpm_devices.update(ret)                
            with open('ckpm_devices.json', 'w') as json_file:
                json.dump(ckpm_devices, json_file)          

        return [ret]