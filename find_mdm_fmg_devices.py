
from cpapi import APIClient, APIClientArgs
from si_automation.fortimanager.FortimanagerFunctions import FortimanagerFunctions
from si_automation.pmp.pmp import pmp
import os, sys, ipaddress, json

def get_subnet(ip, mask):
    try:
        ipobject = ipaddress.ip_network(ip + '/' + mask, strict=False)
        return ipobject
    except Exception as e:
        print('Problems found with given IP addresses: ' + str(e))
        return None


def main():
    # if len(sys.argv) == 2:
    #     inputip = sys.argv[1]
    # else:
    #     print('Wrong number of arguments. 1 expected') 
    #     return 0
    #inputip = '210.54.52.70'
    # try:
    #     ip = ipaddress.IPv4Address(inputip)
    # except Exception as e:
    #     print(str(e))
    #     return 0
    

    #PMP setup
    PMP_TOKEN = os.environ['PMP_TOKEN']
    PMP_URL = os.environ['PMP_URL']
    pmp_object = pmp(PMP_URL, PMP_TOKEN)
    if pmp_object.error is not None:
        print(pmp_object.error)
        return 0     

    #START WITH SMF/SDP MDM
    username = 'apiuser'
    api_server = '210.54.52.12'
    pass_obj, error = pmp_object.get_credentials_for_account('CKPMDMMGT001', username)
    if error is not None:
        print("Error retrieving password from PMP: " + str(error))
        return 0    
    password = pass_obj['PASSWORD'] 

    client_args = APIClientArgs(server=api_server, fingerprint='7C50C3CC266062FE821647EDFFF4EDB320E5008D')

    with APIClient(client_args) as client:
        login_res = client.login(username, password)

        if login_res.success is False:
            print("Login failed:\n{}".format(login_res.error_message))
            exit(0)

        show_hosts_res = client.api_query("show-gateways-and-servers", 'full')
        if show_hosts_res.success is False:
            print("Failed to get the list of all host objects:\n{}".format(show_hosts_res.error_message))
            exit(0)

    candidates = {}
    ckpclusters = {}
    for host in show_hosts_res.data:
        if host['type'] != 'checkpoint-host':
            if host.get('cluster-member-names'):
                ckpclusters.update({host['name']: dict(members=host['cluster-member-names'],version=host.get('version', "NA"),hardware=host.get('hardware', "NA"))})
            else:
                candidates.update({host['name'].lower(): dict(device_class='firewall', vendor='checkpoint', version=host.get('version', "NA"), hardware=host.get('hardware', "NA"), serial='', license='', ip=host.get('ipv4-address', 'NA'), source='CKPMDMMGT001')})
    #add data of clusters            
    for _,clusterinfo in ckpclusters.items():
        version = clusterinfo['version']
        hardware = clusterinfo['hardware']
        members = clusterinfo['members']
        for member in members:
            candidates[member.lower()]['version'] = version
            candidates[member.lower()]['hardware'] = hardware


    #FOLLOW WITH SMF/SDP FMG
    apiuser = 'apiadmin'
    pass_obj, error = pmp_object.get_credentials_for_account('FORTNFMGT001', apiuser)
    if error is not None:
        print("Error retrieving FMG password from PMP: " + str(error))
        return 0

    fmg = FortimanagerFunctions(apiuser, pass_obj['PASSWORD'], '210.54.52.118')
    if fmg.fmg_connector.error is not None:
        print("Error. Connection to FMG Failed: " + str(fmg.fmg_connector.error))
    
    devdata, deverror, devfresp = fmg.execute_custom_url("/dvmdb/device", 'get',
            verbose=True, extra_params_keys={'option':'extra info'})
    if deverror is None:
        for dev in devdata:
            if 'os_ver' in dev and 'mr' in dev and 'patch' in dev:
                major = str(round(float(dev['os_ver'])))
                mr =  str(dev['mr'])
                patch = str(dev['patch']) if dev['patch'] > 0 else '0'
                version = f'{major}.{mr}.{patch}'
            else:
                version = 'NA'
            if dev['ha_mode'] == 'standalone':
                candidates.update({dev['name'].lower(): dict(device_class='firewall', vendor='fortinet', version=version, hardware=dev.get('platform_str', "NA"), serial=dev.get('sn', "NA"), license='', ip=dev.get('ip', 'NA'), source='FORTNFMGT001')})
            else:
                for member in dev['ha_slave']:
                    candidates.update({member['name'].lower(): dict(device_class='firewall', vendor='fortinet', version=version, hardware=dev.get('platform_str', "NA"), serial=member.get('sn', "NA"), license='', ip=dev.get('ip', 'NA'), source='FORTNFMGT001')})
    else:
        print('Error getting interface data for device '  + str(devfresp) )          

    # for name, det in candidates.items():
    #     print(name, det)
    with open('mdm_fmg_devices.json', 'w') as json_file:
        json.dump(candidates, json_file)      
    
if __name__ == "__main__":
    main()