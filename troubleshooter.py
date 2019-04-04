import argparse
import requests
import validators
import sys
import os
import json
import napalm
import time
from netaddr import *
from datetime import datetime
from collections import OrderedDict
from napalm.base.test.models import interface_counters, arp_table


requests.packages.urllib3.disable_warnings()
##########################################################

#####################################
########
#####################################
def define_network_variables(venue):
    
    global site_name,site_code,switch_username,switch_password,ise_host,switches
    global arp_table,mac_table,mac_table_access
    arp_table = {}
    mac_table = {}
    mac_table_access = {}
    
    with open("config/inventory.json") as file:
        file_json = json.load(file)
        for sites in file_json['Sites']:
            if sites['site_code'] == venue:
                switch_username = sites['switch_username']
                switch_password = sites['switch_password']
                site_name = sites['site_name']
                site_code = sites['site_code']
                switches = sites['switches']
    
    return 


#####################################
########
#####################################
def validate_interface(int):
    
    interface_gig = [
        "gigabitethernet",
        "gigabite",
        "gigabit",
        "gigeth",
        "giga",
        "gige",
        "gig",
        "gi"]
        
    interface_ten = [
        "tengigabitethernet",
        "tengigabite",
        "tengigabit",
        "tengigeth",
        "tenge",
        "teng",
        "ten",
        "te"]

    interface_vlan = [
        "vlan",
        "vla",
        "vl"]

    count = count1 = count2 = 0
    interface_new = "-"
    int = int.lower()
    
    for i in interface_gig:
        if (i in int) and count == 0 and count1 == 0 and count2 == 0: 
            interface_new = int.replace(i, 'GigabitEthernet')
            count +=1

    for i in interface_ten:
        if (i in int) and count == 0 and count1 == 0 and count2 == 0: 
            interface_new = int.replace(i, 'TenGigabitEthernet')
            count1 +=1

    for i in interface_vlan:
        if (i in int) and count == 0 and count1 == 0 and count2 == 0: 
            interface_new = int.replace(i, 'Vlan')
            count2 +=1

    if interface_new != "-":
        return interface_new
    else:
        print ("Invalid Interface! ")
        sys.exit()

    return


#####################################
########
#####################################
def bounce_interface(switch,interface):
    
    headers = {'Content-Type': 'application/yang-data+json','Accept': 'application/yang-data+json'}
    shut_int_json = OrderedDict([('ietf-interfaces:interface',OrderedDict([ ('name', interface), ('enabled', 'false') ]) )])
    no_shut_int_json = OrderedDict([('ietf-interfaces:interface',OrderedDict([ ('name', interface), ('enabled', 'true') ]) )])
    
    url = "https://"+switch+"/restconf/data/ietf-interfaces:interfaces/interface"    
    
    
    device = requests.patch(url, json=shut_int_json, auth=(switch_username, switch_password), headers=headers, verify=False)
    if device.status_code != 204:
        return ("{\"status\" : \"Switch Connection Failed!\", \"return_code\" : \"" + str(device.status_code) + "\"}")
    else:
        device = requests.patch(url, json=no_shut_int_json, auth=(switch_username, switch_password), headers=headers, verify=False)
        if device.status_code != 204:
            return ("{\"status\" : \"Switch Connection Failed!\", \"return_code\" : \"" + str(device.status_code) + "\"}")
        else:
            return ("{\"status\" : \"Interface "+interface+" bounced\", \"return_code\" : \"" + str(device.status_code) + "\"}")
                
    return 


#####################################
########
#####################################
def interface_run_config(switch,interface):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    cmd = ['show run interface '+interface+' | be interface']
    
    result = device.cli(cmd)

    # Close connection    
    device.close()
    
    return (result)


#####################################
########
#####################################
def interface_stats(switch,interface):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    interface_stats = '{ \"'+interface+'\" : {\"counters\": {},\"stats\": {} } }'
    interface_stats_json = json.loads(interface_stats)
    result = device.get_interfaces_counters()
    interface_stats_json[interface]['counters'] = result[interface]
    result = device.get_interfaces()
    interface_stats_json[interface]['stats'] = result[interface]

    # Close connection    
    device.close()
    
    return (interface_stats_json)


#####################################
########
#####################################
def find_interface_errors(switch):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    interface_error = '{}'
    interface_error_json = json.loads(interface_error)
    
    result = device.get_interfaces_counters()
    for i in result:
        if (result[i]['rx_errors'] != 0) or (result[i]['tx_errors'] != 0):
            interface_error_json[i] = result[i]
            
    # Close connection    
    device.close()
    
    return (interface_error_json)


#####################################
########
#####################################
def find_interface_drops(switch):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    interface_error = '{}'
    interface_error_json = json.loads(interface_error)
    
    result = device.get_interfaces_counters()
    for i in result:
        if (result[i]['rx_discards'] != 0 and result[i]['rx_discards'] != -1 ) or (result[i]['tx_discards'] != 0 and result[i]['tx_discards'] != -1):
            interface_error_json[i] = result[i]
            
    # Close connection    
    device.close()
    
    return (interface_error_json)


#####################################
########
#####################################
def interface_qos_stats(switch,interface):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    cmd = ['show policy-map interface '+interface]
    
    result = device.cli(cmd)

    # Close connection    
    device.close()
    
    return (result)


#####################################
########
#####################################
def ping_test(switch,ip,source,vrf,count):
    
    int_ip = ''
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    if source != '':
        interface = device.get_interfaces_ip()
        for key in interface[source]['ipv4'].keys():
            int_ip = key

    if (int_ip != '') and (vrf != '') and (count != ''):
        result = device.ping(ip,source=int_ip,vrf=vrf,count=count)
    elif (int_ip != '') and (vrf != ''):
        result = device.ping(ip,source=int_ip,vrf=vrf)
    elif (int_ip != '') and (count != ''):
        result = device.ping(ip,source=int_ip,count=count)
    elif (vrf != '') and (count != ''):
        result = device.ping(ip,vrf=vrf,count=count) 
    elif (int_ip != ''):
        result = device.ping(ip,source=int_ip)
    elif (count != ''):
        result = device.ping(ip,count=count)
    elif (vrf != ''):
        result = device.ping(ip,vrf=vrf)
    else:
        result = device.ping(ip)
    
    # Close connection    
    device.close()
    
    return (result)


#####################################
########
#####################################
def get_mac(switch):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    result = device.get_mac_address_table()

    # Close connection    
    device.close()
    
    return (result)


#####################################
########
#####################################
def get_arp_cli(switch):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    result_vrf = device.get_network_instances()
    result_arp = {}

    for i in result_vrf:
        if i == 'default':
            cmd = 'show arp | ex Protocol'
        else:
            cmd = 'show arp vrf '+i+' | ex Protocol'
        cmds = []
        cmds.append(cmd)
        result = device.cli(cmds)
        list = result[cmd]
        result_arp[i] = []
        for item in list.split('\n'):
            x = item.split()
            if ('Incomplete' in x[3]):
                mac_add = '-'
            else:
                mac_add = EUI(x[3], dialect=mac_unix_expanded)
            value = {'ip' : x[1], 'mac': str(mac_add), 'vrf' : i }
            result_arp[i].append(value)

    # Close connection    
    device.close()
    
    return (result_arp)
    

#####################################
########
#####################################
def find_device(device,type):
    
    device = device.upper()
    result = '{ \"'+device+'\" : {\"result\": \"ERROR - Device NOT found.\" , \"ip\": \"-\" , \"vrf\": \"-\", \"mac\": \"-\", \"switch\": \"-\", \"interface\": \"-\", \"vlan\": \"-\" } }'
    result_json = json.loads(result)
    mac = ''

    if type == 'mac':
        result_json[device]['mac'] = device
        for i in arp_table:
            for entry in arp_table[i]:
                for item in arp_table[i][entry]:
                    if item['mac'] == device.lower(): 
                        result_json[device]['ip'] = item['ip']
                        result_json[device]['vrf'] = item['vrf']
                    
        for i in mac_table:
            switch_ip = i
            for entry in mac_table[i]:
                if entry['mac'] == device: 
                    if (not '/1/' in entry['interface']):
                        result_json[device]['switch'] = switch_ip
                        result_json[device]['result'] = "SUCCESS - Device "+device+" found."
                        result_json[device]['interface'] = entry['interface']
                        result_json[device]['vlan'] = entry['vlan']
        
        for i in mac_table_access:
            switch_ip = i
            for entry in mac_table_access[i]:
                if entry['mac'] == device: 
                    if (not '/1/' in entry['interface']):
                        result_json[device]['switch'] = switch_ip
                        result_json[device]['result'] = "SUCCESS - Device "+device+" found."
                        result_json[device]['interface'] = entry['interface']
                        result_json[device]['vlan'] = entry['vlan']
        
    elif type == 'ip':
        result_json[device]['ip'] = device 
        for i in arp_table:
            for entry in arp_table[i]:
                for item in arp_table[i][entry]:
                    if item['ip'] == device: 
                        result_json[device]['mac'] = item['mac']
                        result_json[device]['vrf'] = item['vrf']
                        mac = item['mac'].upper()
                    
        for i in mac_table:
            switch_ip = i
            for entry in mac_table[i]:
                if entry['mac'] == mac: 
                    if (not '/1/' in entry['interface']):
                        result_json[device]['interface'] = entry['interface']
                        result_json[device]['switch'] = switch_ip
                        result_json[device]['result'] = "SUCCESS - Device "+device+" found."
                        result_json[device]['vlan'] = entry['vlan']
        
        for i in mac_table_access:
            switch_ip = i
            for entry in mac_table_access[i]:
                if entry['mac'] == mac: 
                    if (not '/1/' in entry['interface']):
                        result_json[device]['interface'] = entry['interface']
                        result_json[device]['switch'] = switch_ip
                        result_json[device]['result'] = "SUCCESS - Device "+device+" found."
                        result_json[device]['vlan'] = entry['vlan']
                                                                                      
    else:
        result_json[device]['result'] = "ERROR - Invalid device type."    

    return (result_json)

#####################################
########
#####################################
def cable_test(switch,interface):
    
    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver('ios')
    # Define device connection:
    device = driver(hostname=str(switch), username=switch_username, password=switch_password)
    # Open connection
    device.open()
    
    test_cmd = ['test cable-diagnostics tdr interface '+interface]
    check_test_cmd = ['show cable-diagnostics tdr interface '+interface+" | beg Interface"]
    
    device.cli(test_cmd)
    time.sleep(5)
    result = device.cli(check_test_cmd)

    while "Not Completed" in result["show cable-diagnostics tdr interface "+interface+" | beg Interface"]:
        time.sleep(5)
        result = device.cli(check_test_cmd)

    # Close connection    
    device.close()

    result_bounce = bounce_interface(switch,interface)
    result_bounce_json = json.loads(result_bounce)

    if int(result_bounce_json['return_code']) == 204:
        final_result = '{}'
        final_result_json = json.loads(final_result)
        final_result_json['status'] = "Cable Test executed Successfully "
        final_result_json['content'] = result['show cable-diagnostics tdr interface '+interface+" | beg Interface"]
        return (final_result_json)
    else:
        final_result = '{}'
        final_result_json = json.loads(final_result)
        final_result_json['status'] = "Cable Test Failed "
        final_result_json['content'] = result['show cable-diagnostics tdr interface '+interface+" | beg Interface"]
        return (final_result_json)

    
    return 


#####################################
########
#####################################
def main ():

    mac=ip=switch=interface=vrf=count=source = ''
  
    parser = argparse.ArgumentParser(usage='%(prog)s -a [action] -l [location] [optional arguments]', formatter_class=argparse.RawTextHelpFormatter)
    required = parser.add_argument_group('Required', 'Required Arguments')
    required.add_argument("-a", action="store", dest="action", required=True, help="""[ping|test_cable|int_config|qos_stats|bounce|find]
    ping - Ping device from Core Switch.
    test_cable - Run cable test from switch.
    int_config - Display interface configuration.
    qos_stats - Display QoS statistics from interface.
    int_stats - Display Interface statistics.
    bounce - Bounve switch interface.
    find - Find endpoint in the Network.
    find_errors - Find Interfaces in the Network with errors.
    find_drops - Find Interfaces in the Network with dropped packets.""")
    required.add_argument("-l", action="store", dest="location", required=True, help="ISE deployment witch to connect.")
    optional = parser.add_argument_group('Optional', 'Optional Arguments')
    optional.add_argument("-mac", action="store", dest="mac", help="Endpoint MAC Address. ")
    optional.add_argument("-ip", action="store", dest="ip", help="Endpoint IP Address. ")
    optional.add_argument("-sw", action="store", dest="switch", help="Switch IP Address. ")
    optional.add_argument("-int", action="store", dest="interface", help="Interface Name. ")
    optional.add_argument("-vrf", action="store", dest="vrf", help="VRF Name to source PING. ")
    optional.add_argument("-c", action="store", dest="count", help="Amount of PING packets. ")
    optional.add_argument("-src", action="store", dest="source", help="Source Interface for PING. ")


    options = parser.parse_args()

    if options.location:
        define_network_variables(options.location)

    if options.mac:
        if validators.mac_address(options.mac):
            mac = options.mac
        else:
            print ("Invalid MAC Address! ")
            sys.exit()
    
    if options.ip:
        if validators.ipv4(options.ip):
            ip = options.ip
        else:
            print ("Invalid IP Address! ")
            sys.exit()

    if options.switch:
        i=0
        if validators.ipv4(options.switch):
            switch = options.switch
            for device in switches:
                if device['switch_ip'] == switch:
                    i =1
            if i != 1:
                print ("Switch IP Address, does not exist in this location!")
                sys.exit()
        else:
            print ("Invalid Switch IP Address! ")
            sys.exit()

    if options.interface:
        interface = validate_interface(options.interface)

    if options.source:
        source = options.source

    if options.vrf:
        vrf = options.vrf

    if options.count:
        count = options.count
          
                
    if options.action:
        if options.action == 'ping':
            if ip:
                ping_result = '{}'
                ping_result_json = json.loads(ping_result)
                if switch:
                    ping_result_json[switch] = ping_test(switch,ip,source,vrf,count)
                    #print(ping_result_json)
                    print(json.dumps(ping_result_json, indent=4, sort_keys=True))
                else:
                    for i in switches:
                        if i['switch_group'] == "core":
                            ping_result_json[i['switch_ip']] = ping_test(i['switch_ip'],ip,source,vrf,count)
                    #print(ping_result_json)
                    print(json.dumps(ping_result_json, indent=4, sort_keys=True))
            else:
                print ("Invalid Options! ping requires -ip. Addtional options  -sw, -vrf, -src, -c are optional.")
                sys.exit()
                
                
        elif options.action == 'test_cable':
            if switch and interface:
                test_result = cable_test(switch,interface)
                print(json.dumps(test_result, indent=4, sort_keys=True))
                #print(test_result)
            else:
                print ("Invalid Options! Cable test requires -sw and -int options.")
                sys.exit()

                
        elif options.action == 'int_config':
            if switch and interface:
                result_int_config = interface_run_config(switch,interface)
                result = '{}'
                result_json = json.loads(result)
                for i in result_int_config:
                    result_json[interface] = result_int_config[i]
                print(json.dumps(result_json, indent=4, sort_keys=True))
            else:
                print ("Invalid Options! Show run Interface config requires -sw and -int options.")
                sys.exit()

                
        elif options.action == 'qos_stats':
            if switch and interface:
                result_qos_stats = interface_qos_stats(switch,interface)
                result = '{}'
                result_json = json.loads(result)
                for i in result_qos_stats:
                    result_json[interface] = result_qos_stats[i]
                print(json.dumps(result_json, indent=4, sort_keys=True))
                
            else:
                print ("Invalid Options! QoS Statistics requires -sw and -int options.")
                sys.exit()

        elif options.action == 'arp':
            if switch:
                result_rest_arp = get_arp_cli(switch)
                print(json.dumps(result_rest_arp, indent=4, sort_keys=True))

            else:
                print ("Invalid Options! Find endpoint requires -mac or -ip options.")
                sys.exit()

                            
        elif options.action == 'int_stats':
            if switch and interface:
                result_int_stats = interface_stats(switch,interface)
                print(json.dumps(result_int_stats, indent=4, sort_keys=True))
                #print(result_int_stats[interface]['counters'])
            else:
                print ("Invalid Options! Interface Statistics requires -sw and -int options.")
                sys.exit()

                            
        elif options.action == 'bounce':
            if switch and interface:
                result_bounce = bounce_interface(switch,interface)
                print(result_bounce)
            else:
                print ("Invalid Options! Bounce requires -sw and -int options.")
                sys.exit()

        
        elif options.action == 'find':
            if mac or ip:
                if switch:
                    if ip:
                        ping_result = ping_test(switch,ip,source,vrf,count)
                    arp_table[switch] = get_arp_cli(switch)
                    mac_table[switch] = get_mac(switch)
                else:
                    for i in switches:
                        if ip:
                            ping_result = ping_test(i['switch_ip'],ip,source,vrf,count)
                        arp_table[i['switch_ip']] = get_arp_cli(i['switch_ip'])
                        temp_table = get_mac(i['switch_ip'])
                        mac_table[i['switch_ip']] = temp_table
                        if i['switch_group'] == 'access':
                            mac_table_access[i['switch_ip']] = temp_table

                if mac:
                    result = find_device(mac,"mac")
                elif ip:
                    result = find_device(ip,"ip")
                    
                print(json.dumps(result, indent=4, sort_keys=True))
                                    
            else:
                print ("Invalid Options! Find endpoint requires -mac or -ip options.")
                sys.exit()

        elif options.action == 'find_errors':
            result_int_error = '{}'
            result_int_error_json = json.loads(result_int_error)
            
            if switch:
                result_int_error_json[switch] = find_interface_errors(switch)
                print(json.dumps(result_int_error_json, indent=4, sort_keys=True))
            else:
                for i in switches:
                    result_int_error_json[i['switch_ip']] = find_interface_errors(i['switch_ip'])
                
                print(json.dumps(result_int_error_json, indent=4, sort_keys=True))

        elif options.action == 'find_drops':
            result_int_drops = '{}'
            result_int_drops_json = json.loads(result_int_drops)
            
            if switch:
                result_int_drops_json[switch] = find_interface_drops(switch)
                print(json.dumps(result_int_drops_json, indent=4, sort_keys=True))
            else:
                for i in switches:
                    result_int_drops_json[i['switch_ip']] = find_interface_drops(i['switch_ip'])
                
                print(json.dumps(result_int_drops_json, indent=4, sort_keys=True))


        else:
            print ("Invalid Action!")
            

    return

main()