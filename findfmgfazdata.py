
from si_automation.fortimanager.FortimanagerFunctions import FortimanagerFunctions
from si_automation.fortianalyzer.FortianalyzerFunctions import FortianalyzerFunctions
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
    #PMP setup
    PMP_TOKEN = os.environ['PMP_TOKEN']
    PMP_URL = os.environ['PMP_URL']
    pmp_object = pmp(PMP_URL, PMP_TOKEN)
    if pmp_object.error is not None:
        print(pmp_object.error)
        return 0     

    GW = {
        'FORTNFANA001': dict(ip='210.54.52.119', password=''),
          'FORTNFMGT001': dict(ip='210.54.52.118', password=''),
            'FORNAAANA101': dict(ip='10.245.4.22', password=''),
            'FORNAAANA201': dict(ip='10.245.4.38', password=''),
            'FORNAAFMG101': dict(ip='10.245.4.20', password=''),
            'FORNAAFMG202': dict(ip='10.245.4.36', password=''),
            'MDRN4LFORTvMGT01': dict(ip='10.241.130.110', password=''),
            'MDRN4LFORTIpANA01': dict(ip='10.241.130.114', password=''),
            'MDRN4LFORTIpANA02': dict(ip='10.241.130.115', password=''),
            'wn1n4lfortpana01': dict(ip='10.249.130.7', password=''),
            'wn1n4lfortpana02': dict(ip='10.249.130.8', password=''),
          }     
   
    #PMP setup
    username = 'apiadmin'
    pwd = ''
    n4l = ''
    candidates = {}
    if pmp_object.error is not None:
        print(pmp_object.error)
        return 0 
    for k,v in GW.items():
        if 'n4l' in k.lower():
            source = 'Tinus Head'
            if k == 'MDRN4LFORTvMGT01':
                pass_obj, error = pmp_object.get_credentials_for_account(k, username)
                if error is not None:
                    print(f"Error retrieving {k} password from PMP: " + str(error))
                    return 0         
                pwd = pass_obj['PASSWORD']
                n4l = pwd
            else:
                pwd = n4l
        else:
            source = 'manual vm export'        
            pass_obj, error = pmp_object.get_credentials_for_account(k, username)
            if error is not None:
                print(f"Error retrieving {k} password from PMP: " + str(error))
                return 0
            pwd = pass_obj['PASSWORD']

        if 'ana' in k.lower():
            obj = FortianalyzerFunctions(username, pass_obj['PASSWORD'], v['ip'])
        else:
            obj = FortimanagerFunctions(username, pass_obj['PASSWORD'], v['ip'])



        version = ''
        hardware = ''
        cpu_use = ''    
        mem_total = ''
        mem_use = ''
        disk_use = ''
        disk_total = ''
        serial = ''
        try:
            pdata, perror, pfresp = obj.execute_custom_url('/cli/global/system/performance', 'get')
            if perror is None:
                # print(k, len(pdata))
                cpu_use = pdata['CPU']['Used']
                mem_total = pdata['Memory']['Total']
                mem_use = pdata['Memory']['Used']
                disk_use = pdata['Hard Disk']['Used']
                disk_total = pdata['Hard Disk']['Total']
            else:
                print(k, 'error', pfresp)
            sdata, serror, sfresp = obj.execute_custom_url('/cli/global/system/status', 'get')
            if serror is None:
                # print(k, len(sdata))
                version = sdata['Version']
                hardware = sdata['Platform Full Name']
                serial = sdata['Serial Number']
            else:
                print(k, 'error', sfresp)
        except Exception as e:
            print(k, 'error', e)

        # print(k, dict(device_class='management tool', vendor='fortinet', ip=v['ip'], version=version, hardware=hardware, source=source, serial=serial, cpu_use=cpu_use, mem_total=mem_total, mem_use=mem_use, disk_total=disk_total, disk_use=disk_use) )
        candidates.update({k.lower(): dict(device_class='management tool', vendor='fortinet', ip=v['ip'], version=version, hardware=hardware, source=source, serial=serial, cpu_use=cpu_use, mem_total=mem_total, mem_use=mem_use, disk_total=disk_total, disk_use=disk_use)})
        
    with open('fortim_devices.json', 'w') as json_file:
        json.dump(candidates, json_file)      
    
if __name__ == "__main__":
    main()