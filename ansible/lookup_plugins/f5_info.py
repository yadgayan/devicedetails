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
        devtype = terms[1]
        results = terms[2]

        try:
            with open('f5_devices.json', 'r') as json_file:
                f5_devices = json.load(json_file)
        except FileNotFoundError:
            f5_devices = dict()
        except Exception as e:
            print(str(e))
            return 0

        host = device.split('.')[0]
        candidates = {}
        if host.lower() not in f5_devices:
            if devtype in ['normal', 'special']:
                candidates.update({host.lower(): dict(device_class='loadbalancer', vendor='f5', version=results['product_version'], hardware=results['platform'], serial='', license='', ip='', source='Oscars Head', type=results["marketing_name"])})
            else:
                version = ''
                hardware = ''
                subtype = ''
                for l in results:
                    if l[0] == 'Sys::Version':
                        version = l[3].split('Version')[1].strip()
                    elif l[0] == 'Sys::Hardware':
                        for idx, line in enumerate(l):
                            if "Platform" == line:
                                subtype = l[idx+1].split('Name')[1].strip()
                            elif "System Information" == line:
                                hardware = l[idx+1].split('Type')[1].strip()
                candidates.update({host.lower(): dict(device_class='loadbalancer', vendor='f5',  version=version, hardware=hardware, serial='', license='', ip='', source='Oscars Head', type=subtype)})
            if candidates:
                f5_devices.update(candidates)                
                with open('f5_devices.json', 'w') as json_file:
                    json.dump(f5_devices, json_file)             

        return [candidates]
