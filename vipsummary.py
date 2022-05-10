#!/usr/bin/env python3
# Author, David Martinez (@dx0xm)(david.martinez@spark.co.nz)
import json, sys, os

def main():

    try:
        with open('vip_data.json', 'r') as json_file:
            vip_data = json.load(json_file)
    except Exception as e:
        print(str(e))
        return 0
    
    if vip_data:
        for vip, details in vip_data.items():
            print('#'*8)
            print(f'VIP: {vip}')
            [print('....', d) for d in details]

if __name__ == "__main__":
    main()        