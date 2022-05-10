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
            virtual = results[1]
            selfip = results[2]
            tcpprofile = 0
            for idx, line in enumerate(virtual):
                if 'profiles {' in line:
                    counter = idx
                    end = virtual[idx]
                    while '}' not in end:
                        if '/tcp' in end:
                            tcpprofile +=1
                        counter += 1
                        if counter > len(virtual) - 1:
                            break
                        end = virtual[counter]
            allowall = 0
            for idx, line in enumerate(selfip):
                if 'allow-service all' in line:
                    allowall += 1

            candidates.update({host: dict(tcpprofile=tcpprofile, allowall=allowall)})
            f5_devices.update(candidates)                
            with open('f5_devices.json', 'w') as json_file:
                json.dump(f5_devices, json_file)             

        return [candidates]
