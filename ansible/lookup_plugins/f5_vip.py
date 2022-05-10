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
        invip = terms[0]
        device = terms[1]
        results = terms[2]

        if ',' in invip:
            words = invip.split(',')
            vips = [x for x in words if len(x) > 0]
        else:
            vips = [invip]

        try:
            with open('vip_data.json', 'r') as json_file:
                vip_data = json.load(json_file)
        except FileNotFoundError:
            vip_data = dict()
            for vip in vips:
                vip_data.update({vip: []})
        except Exception as e:
            print(str(e))
            return 0

        host = device.split('.')[0].lower()
        virtual = results[1]
        changes = []
        for line in virtual:
            if 'destination' in line:
                for vip in vips:
                    if f'{vip}:' in line:
                        vip_data[vip].append(dict(host=host, details=line))
                        changes.append(line)
        if changes:              
            with open('vip_data.json', 'w') as json_file:
                json.dump(vip_data, json_file)             

        return changes
