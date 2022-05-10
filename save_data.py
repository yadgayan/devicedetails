#!/usr/bin/env python3
# Author, David Martinez (@dx0xm)(david.martinez@spark.co.nz)
import json, sys, os, datetime
from pymongo import MongoClient
from si_automation.pmp.pmp import pmp

def main():

    PMP_TOKEN = os.environ['PMP_TOKEN']
    PMP_URL = os.environ['PMP_URL']

    #Mongo Database Variables
    mongo_pmp_resource = 'sidb_admin'
    mongo_username = 'admin'
    database_name = 'infrastructure'
    database_server = 'srv-sidb'
    collection = 'sdp'

    #PMP setup
    pmp_object = pmp(PMP_URL, PMP_TOKEN)
    if pmp_object.error is not None:
        print(pmp_object.error)
        return 0

    #Getting Mongo passwords
    pass_obj, error = pmp_object.get_credentials_for_account(mongo_pmp_resource, mongo_username)
    if error is not None:
        print(f'Cant get the password for {mongo_username}, refer to {error}')
        return 0

    client = MongoClient(f'mongodb://{mongo_username}:{pass_obj["PASSWORD"]}@{database_server}')

    files = ['mdm_fmg_devices.json', 'f5_devices.json', 'ckpm_devices.json', 'fortim_devices.json', 
             'fortid_devices.json', 'fortin_devices.json', 'fortig_devices.json', 'proxy_devices.json', 'juniper_devices.json']
    filesdata = []
    for fl in files:
        try:
            with open(fl, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = dict()
        except Exception as e:
            print(str(e))
            return 0
        filesdata.append(dict(name=fl, data=data))
  
    todb = []
    for obj in filesdata:
        for k,v in obj['data'].items():
            d = dict(name=k, updated=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            d.update(v)
            todb.append(d)

    if todb:
        for d in todb:
            try:
                database = client[database_name]
                col = database[collection]
                entry = col.find_one({'name': d['name']})
                if entry:
                    if col.find_one_and_update({'name': d['name']}, {"$set": d}):
                        print(f'{d["name"]} updated successfully')
                    else:
                        print(f'Error: Could not update {d["name"]}')
                        print(d)
                else:
                    new_id = col.insert_one(d)
                    if new_id.acknowledged:                    
                        print(f'{d["name"]} added successfully to database')
                    else:
                        print(f'Error: Could not add {d["name"]} to database')
                        print(d)
            except Exception as e:     
                print(f'Error - {str(e)}')
                print(d)
        client.close()   
    # for name, v in ckpm_devices.items():
    #     print(name.lower(), v)    

if __name__ == "__main__":
    main()        