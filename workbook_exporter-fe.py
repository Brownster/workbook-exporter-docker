import sys
import tempfile
import pandas as pd
import oyaml as yaml
from collections import OrderedDict
from ruamel.yaml import YAML
from werkzeug.utils import secure_filename
import time
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
import shutil
import os
import logging
import werkzeug.exceptions

global listen_port_var
output_path = None
selected_exporter_names = []

#######################################################   START OF EXPORTER FUNCTIONS   ###################################################################

############################################################ Exporter_WFODB  #####################################################################

def exporter_wfodb(file_path, output_file, output_dir):
    exporter_generic('exporter_wfodb', file_path, output_file, output_dir)

############################################################ Exporter_PC5  #####################################################################

def exporter_pc5(file_path, output_file, output_dir):
    exporter_generic('exporter_pc5', file_path, output_file, output_dir)

############################################################ EXPORTER_AMS  #####################################################################

def exporter_ams(file_path, output_file, output_dir):
    exporter_generic('exporter_ams', file_path, output_file, output_dir)

############################################################ EXPORTER_MPP  #####################################################################

def exporter_mpp(file_path, output_file, output_dir):
    exporter_generic('exporter_mpp', file_path, output_file, output_dir)

############################################################ EXPORTER_IQ  #####################################################################

def exporter_iq(file_path, output_file, output_dir):
    exporter_generic('exporter_iq', file_path, output_file, output_dir)

############################################################ EXPORTER_IPO  #####################################################################

def exporter_ipo(file_path, output_file, output_dir):
    exporter_generic('exporter_ipo', file_path, output_file, output_dir)

############################################################ EXPORTER_AAM #####################################################################

def exporter_aam(file_path, output_file, output_dir):
    exporter_generic('exporter_aam', file_path, output_file, output_dir)

############################################################ EXPORTER_VOICEPORTAL #####################################################################

def exporter_voiceportal(file_path, output_file, output_dir):
    exporter_generic('exporter_voiceportal', file_path, output_file, output_dir)

############################################################ EXPORTER_CALLBACK #####################################################################
 
def exporter_callback(file_path, output_file, output_dir):
    exporter_generic('exporter_callback', file_path, output_file, output_dir)

########################################################   exporter_BREEZE   ############################################################

def exporter_breeze(file_path, output_file, output_dir):
    exporter_generic('exporter_breeze', file_path, output_file, output_dir)

###############################################################  exporter_CMS  #############################################################

def exporter_cms(file_path, output_file, output_dir):
    exporter_generic('exporter_cms', file_path, output_file, output_dir)

############################################################  EXPORTER_SM  ################################################################################

def exporter_sm(file_path, output_file, output_dir):
    exporter_generic('exporter_sm', file_path, output_file, output_dir)
    
############################################################  EXPORTER_AES  ################################################################################

def exporter_aes(file_path, output_file, output_dir):
    exporter_generic('exporter_aes', file_path, output_file, output_dir)

####################################################    EXPORTER_LINUX    #############################################################
def exporter_linux(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    new_entries = []
    sorted_yaml_output =[]
    try:
        flash("Exporter Linux called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_linux')
    output_path = os.path.join(output_dir, output_file)

    if df_filtered.empty:
        flash("No rows matching exporter_linux condition found")
        return

    # Initialize exporter_linux key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_linux', OrderedDict())])

    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        listen_port = row['OS-Listen-Port']
        ssh_username = row.get('ssh_username', 'put your username here')
        ssh_password = row.get('ssh_password', 'put your password here')

        if ip_exists_in_yaml('exporter_linux', ip_address, output_path=output_path):
            flash(f"IP {ip_address} already exists in the YAML file.")
            continue

        if hostname not in yaml_output.get('exporter_linux', {}):
            yaml_output['exporter_linux'][hostname] = OrderedDict()

        yaml_output['exporter_linux'][hostname]['ip_address'] = ip_address
        yaml_output['exporter_linux'][hostname]['listen_port'] = int(listen_port) if not pd.isna(listen_port) else int(default_listen_port)
        yaml_output['exporter_linux'][hostname]['location'] = location
        yaml_output['exporter_linux'][hostname]['country'] = country
        yaml_output['exporter_linux'][hostname]['username'] = ssh_username
        yaml_output['exporter_linux'][hostname]['password'] = ssh_password

        new_entries.append(row)

    # Load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)
    # Sort the YAML data by hostname before writing it to the output file
    sorted_yaml_output = OrderedDict(sorted(yaml_output['exporter_linux'].items(), key=lambda x: x[0]))
    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_linux', existing_yaml_output, new_entries, yaml_output, output_path)

######################################################  EXPORTER_BlackBox  #############################################################

def exporter_blackbox(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    yaml_output = OrderedDict([('exporter_blackbox', OrderedDict())])
    try:
        flash("Exporter Blackbox called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = df[(df['icmp'] == True) & (df['ssh-banner'] == True)]
    output_path = os.path.join(output_dir, output_file)

    if df_filtered.empty:
        flash("No rows matching exporter_blackbox condition found")
        return    
    

    # Create an empty dictionary to store the YAML output
    yaml_output = OrderedDict([('exporter_blackbox', OrderedDict())])

    output_path = os.path.join(output_dir, output_file)

    # Initialize new_entries list
    new_entries = []    
    
    
    # Iterate over rows in filtered dataframe
    for index, row in df.iterrows():
        exporter_name = 'exporter_blackbox'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
    
        if hostname not in yaml_output.get(exporter_name, {}):
            yaml_output[exporter_name][hostname] = {}
    
        if ip_address not in yaml_output[exporter_name][hostname]:
            yaml_output[exporter_name][hostname][ip_address] = {}
        
        yaml_output[exporter_name][hostname][ip_address]['location'] = location
        yaml_output[exporter_name][hostname][ip_address]['country'] = country
    
        if row['icmp']:
            yaml_output[exporter_name][hostname][ip_address]['module'] = 'icmp'
        
        if row['ssh-banner']:
            yaml_output[exporter_name][hostname][f'{ip_address}:22'] = {
                 'module': 'ssh_banner',
                 'location': location,
                 'country': country
        }

        new_entries.append(row)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    output_path = os.path.join(output_dir, output_file)
    existing_yaml_output = load_existing_yaml(output_path)

    process_exporter('exporter_blackbox', existing_yaml_output, new_entries, yaml_output, output_path)

########################################################  EXPORTER_SSL  ##################################################################

def exporter_ssl(file_path, output_file, output_dir):
    yaml_output = OrderedDict([('exporter_ssl', OrderedDict())])
    try:
        flash("Exporter SSL called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    # Filter the data based on the condition
    df_filtered = df[df['Exporter_SSL'] == True]

    # Create an empty dictionary to store the YAML output
    yaml_output = OrderedDict([('exporter_ssl', OrderedDict())])

    # Initialize exporter_ssl key in the YAML dictionary
    yaml_output['exporter_ssl'] = {}

    output_path = os.path.join(output_dir, output_file)

    # Initialize new_entries list
    new_entries = []
    # Loop through the filtered data and add to the dictionary
    for _, row in df_filtered.iterrows():
        exporter_name = 'exporter_ssl'
        fqdn = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        exporter_app = row['Exporter_name_app']

        # Set default listen_port to 443 and change it to 8443 if exporter_ssl is specified
        listen_port = 8443 if exporter_app == 'exporter_ssl' else 443

        # Check for duplicate entries
        if ip_exists_in_yaml(exporter_name, ip_address, output_path):
            continue

        if exporter_name not in yaml_output:
            yaml_output[exporter_name] = {}
        if fqdn not in yaml_output[exporter_name]:
            yaml_output[exporter_name][fqdn] = {}
        yaml_output[exporter_name][fqdn] = {
            'ip_address': ip_address,
            'listen_port': listen_port,
            'location': location,
            'country': country,
        }

        new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)  
    # Write the YAML data to a file, either appending to an existing file or creating a new file
    process_exporter('exporter_ssl', existing_yaml_output, new_entries, yaml_output, output_path)

##############################################################   exporter_WINDOWS   ########################################################
   
def exporter_windows(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    try:
        flash("Exporter Windows called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_windows')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_windows key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_windows', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_windows'
        fqdn = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if fqdn not in yaml_output[exporter_name]:
            yaml_output[exporter_name][fqdn] = {}

        yaml_output[exporter_name][fqdn]['ip_address'] = ip_address
        yaml_output[exporter_name][fqdn]['listen_port'] = 9182  # Set to default listen port for Windows
        yaml_output[exporter_name][fqdn]['location'] = location
        yaml_output[exporter_name][fqdn]['country'] = country

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_windows', existing_yaml_output, new_entries, yaml_output, output_path)
  
 ##########################################################   exporter_VERINT   ###############################################################

def exporter_verint(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    yaml_output = OrderedDict([('exporter_verint', OrderedDict())])
    try:
        flash("Exporter Verint called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_verint')
    output_path = os.path.join(output_dir, output_file)

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_verint'
        fqdn = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if fqdn not in yaml_output[exporter_name]:
            yaml_output[exporter_name][fqdn] = {}

        yaml_output[exporter_name][fqdn]['ip_address'] = ip_address
        yaml_output[exporter_name][fqdn]['listen_port'] = 9182
        yaml_output[exporter_name][fqdn]['location'] = location
        yaml_output[exporter_name][fqdn]['country'] = country

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_verint', existing_yaml_output, new_entries, yaml_output, output_path)
               
#######################################################   AVAYA SBC   ####################################################################

def exporter_avayasbc(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    yaml_output = {'exporter_avayasbc': {}}
    try:
        flash("Exporter SBC called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_avayasbc')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_avayasbc key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_avayasbc', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_avayasbc'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        snmp_version = row.get('snmp_version', 'v2')
        snmp_user = row.get('snmp_user', None)
        snmp_pass = row.get('snmp_password', None)

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        if ip_address not in yaml_output[exporter_name][hostname]:
            yaml_output[exporter_name][hostname]= {}

            listen_port = row.get('App-Listen-Port', default_listen_port)
            if listen_port == default_listen_port:
                 default_listen_port += 1
            yaml_output[exporter_name][hostname]['ip_address'] = ip_address
            yaml_output[exporter_name][hostname]['listen_port'] = int(row['App-Listen-Port'])
            yaml_output[exporter_name][hostname]['location'] = location
            yaml_output[exporter_name][hostname]['country'] = country
            
            if snmp_version == 'v3' and snmp_user is not None:
                yaml_output[exporter_name][hostname]['username'] = snmp_user
                yaml_output[exporter_name][hostname]['privacy_protocol'] = 'aes'
                yaml_output[exporter_name][hostname]['privacy_passphrase'] = snmp_pass
                yaml_output[exporter_name][hostname]['auth_protocol'] = 'sha'
                yaml_output[exporter_name][hostname]['auth_passphrase'] = snmp_pass
            else:
                yaml_output[exporter_name][hostname]['username'] = 'ipcs'

            new_entries.append(row)

    # Load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)
    # Write the YAML data to a file, either appending to an existing file or creating a new file
    process_exporter('exporter_avayasbc', existing_yaml_output, new_entries, yaml_output, output_path)


###########################################   exporter_GATEWAY   ####################################################################

def exporter_gateway(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter Gateway called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_gateway')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_gateway key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_gateway', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_gateway'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        if ip_address not in yaml_output[exporter_name][hostname]:
            yaml_output[exporter_name][hostname] = {}

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1
        yaml_output[exporter_name][hostname]['ip_address'] = ip_address
        yaml_output[exporter_name][hostname]['listen_port'] = int(row['App-Listen-Port'])

        yaml_output[exporter_name][hostname]['location'] = location
        yaml_output[exporter_name][hostname]['country'] = country
        
        snmp_version = row.get('snmp_version', 2)
        yaml_output[exporter_name][hostname]['snmp_version'] = snmp_version

        if snmp_version == 3:
            yaml_output[exporter_name][hostname]['username'] = row['snmp_user']
            yaml_output[exporter_name][hostname]['privacy_protocol'] = 'aes'
            yaml_output[exporter_name][hostname]['privacy_passphrase'] = row.get('snmp_password', 'default_passphrase')
            yaml_output[exporter_name][hostname]['auth_protocol'] = 'sha'
            yaml_output[exporter_name][hostname]['auth_passphrase'] = row.get('snmp_password', 'default_passphrase')
        else:
            if 'comm_string' in df.columns and not pd.isna(row['comm_string']):
                yaml_output[exporter_name][hostname]['community'] = row['comm_string']
            else:
                yaml_output[exporter_name][hostname]['community'] = 'ENC'

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)  # Add this line to load existing YAML data
    # Write the YAML data to a file, either appending to an existing file or creating a new file
    process_exporter('exporter_gateway', existing_yaml_output, new_entries, yaml_output, output_path)


#######################################################  EXPORTER_TCTI       ############################################################

def exporter_tcti(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter TCTI called")

        df = read_input_file(file_path)

    except Exception as e:
        log(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_tcti')
    output_path = os.path.join(output_dir, output_file)
    yaml_output = OrderedDict([('exporter_tcti', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml('exporter_tcti', ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output['exporter_tcti']:
            yaml_output['exporter_tcti'][hostname] = {}

        jmx_ports_present = 'jmx_ports' in row.index
        if jmx_ports_present and not pd.isna(row['jmx_ports']) and row['jmx_ports']:
            ports = [int(port) for port in row['jmx_ports'].split(',')]
        else:
            ports = [8080, 8081]

        for port in ports:
            if port not in yaml_output['exporter_tcti'][hostname]:
                yaml_output['exporter_tcti'][hostname][int(port)] = {} # Changed this line

            yaml_output['exporter_tcti'][hostname][int(port)]['ip_address'] = ip_address
            yaml_output['exporter_tcti'][hostname][int(port)]['location'] = location
            yaml_output['exporter_tcti'][hostname][int(port)]['country'] = country
            new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)          
    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_tcti', existing_yaml_output, new_entries, yaml_output, output_path)

########################################################## EXPORTER_JMX #####################################################################
def exporter_jmx(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter JMX called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_jmx')
    output_path = os.path.join(output_dir, output_file)
    yaml_output = OrderedDict([('exporter_jmx', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml('exporter_jmx', ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output['exporter_jmx']:
            yaml_output['exporter_jmx'][hostname] = {}

        jmx_ports_present = 'jmx_ports' in row.index
        if jmx_ports_present and not pd.isna(row['jmx_ports']) and row['jmx_ports']:
            ports = [int(port) for port in row['jmx_ports'].split(',')]
        else:
            ports = [8080, 8081]

        for port in ports:
            if port not in yaml_output['exporter_jmx'][hostname]:
                yaml_output['exporter_jmx'][hostname][int(port)] = {} # Changed this line

            yaml_output['exporter_jmx'][hostname][int(port)]['ip_address'] = ip_address
            yaml_output['exporter_jmx'][hostname][int(port)]['location'] = location
            yaml_output['exporter_jmx'][hostname][int(port)]['country'] = country
            new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)          
    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_jmx', existing_yaml_output, new_entries, yaml_output, output_path)

######################################################## EXPORTER_VMWARE #######################################################################

def exporter_vmware(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    yaml_output = OrderedDict([('exporter_vmware', OrderedDict())])
    try:
        flash("Exporter vmware called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_vmware')
    output_path = os.path.join(output_dir, output_file)

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml('exporter_vmware', ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output['exporter_vmware']:
            yaml_output['exporter_vmware'][hostname] = {}

        if pd.isna(row['App-Listen-Port']):
            yaml_output['exporter_vmware'][hostname]['listen_port'] = 9272
        else:
            yaml_output['exporter_vmware'][hostname]['listen_port'] = int(row['App-Listen-Port'])

        yaml_output['exporter_vmware'][hostname]['ip_address'] = ip_address
        yaml_output['exporter_vmware'][hostname]['location'] = location
        yaml_output['exporter_vmware'][hostname]['country'] = country
        yaml_output['exporter_vmware'][hostname]['username'] = 'put your username here'
        yaml_output['exporter_vmware'][hostname]['password'] = 'put your password here'

        new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)  

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_vmware', existing_yaml_output, new_entries, yaml_output, output_path)

################################################################ EXPORTER_KAFKA ###############################################################

def exporter_kafka(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    new_entries = []

    try:
        flash("Exporter Exporter Kafka  called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_kafka')
    output_path = os.path.join(output_dir, output_file)

    if df_filtered.empty:
        log("No rows matching exporter_kafka condition found")
        return

    # Initialize exporter_kafka key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_kafka', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        output_path = os.path.join(output_dir, output_file)
        if ip_exists_in_yaml('exporter_kafka', ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output.get('exporter_kafka', {}):
            yaml_output['exporter_kafka'][hostname] = {}

        yaml_output['exporter_kafka'][hostname]['ip_address'] = ip_address
        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1
        yaml_output[exporter_kafka][hostname][ip_address]['listen_port'] = int(row['App-Listen-Port'])
        yaml_output['exporter_kafka'][hostname]['location'] = location
        yaml_output['exporter_kafka'][hostname]['country'] = country
        yaml_output['exporter_kafka'][hostname]['kafka_port'] = 9092

        new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)  

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_kafka', existing_yaml_output, new_entries, yaml_output, output_path)

############################################################ EXPORTER_DRAC ############################################################################

def exporter_drac(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    # Initialize exporter_kafka key in the YAML dictionary
    yaml_output = {'exporter_drac': {}}

    try:
        flash("Exporter DRAC called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_drac')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_drac key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_drac', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml('exporter_drac', ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output['exporter_drac']:
            yaml_output['exporter_drac'][hostname] = {}

        yaml_output['exporter_drac'][hostname]['ip_address'] = ip_address
        yaml_output['exporter_drac'][hostname]['listen_port'] = 623
        yaml_output['exporter_drac'][hostname]['location'] = location
        yaml_output['exporter_drac'][hostname]['country'] = country
        yaml_output['exporter_drac'][hostname]['snmp_version'] = 2
        yaml_output['exporter_drac'][hostname]['community'] = row.get('comm_string', 'ENC')

        new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)  

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_drac', existing_yaml_output, new_entries, yaml_output, output_path)

##################################################### exporter_genesyscloud ##########################################################################

def exporter_genesyscloud(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    new_entries = []
    sorted_yaml_output = []
    try:
        flash("Exporter Genesys Cloud called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_genesyscloud')
    output_path = os.path.join(output_dir, output_file)

    if df_filtered.empty:
        log("No rows matching exporter_genesyscloud condition found")
        return

    # Initialize exporter_genesyscloud key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_genesyscloud', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        listen_port = int(row['App-Listen-Port']) 
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        comm_string = row.get('comm_string', 'public')

        if ip_exists_in_yaml('exporter_genesyscloud', ip_address, output_path=output_path):
            continue

        extra_args = (" --client.managed --billing.enabled --billing.frequency30m --usage.enabled --usage.frequency12h --client.first-day-of-month22 --mos.enabled --mos.bandceilingcritical2.59999 --mos.bandceilingbad3.59999--mos.bandceilingwarning3.09999 --mos.bandceilinggood3.99999")


        yaml_output['exporter_genesyscloud'][hostname] = OrderedDict([
            ('listen_port', listen_port),
            ('extra_args', extra_args),
            ('client_id', 'ENC[PKCS7...]'),
            ('client_secret', 'ENC[PKCS7...]'),
            ('client_basepath', 'https://api.mypurecloud.ie'),
            ('ip_address', ip_address),
            ('location', location),
            ('country', country),
            ('community', comm_string)
        ])

        new_entries.append(row)

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_genesyscloud', existing_yaml_output, new_entries, yaml_output, output_path)


################################################################### EXPORTER_ACM #####################################################################

def exporter_acm(file_path, output_file, output_dir):
    global default_listen_port
    global output_path
    new_entries = []
    sorted_yaml_output =[]
    try:
        flash("Exporter ACM called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_acm')
    output_path = os.path.join(output_dir, output_file)

    if df_filtered.empty:
        log("No rows matching exporter_acm condition found")
        return

    # Initialize exporter_acm key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_acm', OrderedDict())])

    for index, row in df_filtered.iterrows():
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        listen_port = row['App-Listen-Port']
        ssh_username = row.get('ssh_username', 'put your username here')
        ssh_password = row.get('ssh_password', 'put your password here')

        if ip_exists_in_yaml('exporter_acm', ip_address, output_path=output_path):
            log(f"IP {ip_address} already exists in the YAML file.")
            continue

        if hostname not in yaml_output.get('exporter_acm', {}):
            yaml_output['exporter_acm'][hostname] = OrderedDict()

        yaml_output['exporter_acm'][hostname]['ip_address'] = ip_address
        yaml_output['exporter_acm'][hostname]['listen_port'] = int(listen_port) if not pd.isna(listen_port) else int(default_listen_port)
        if 'lsp' in hostname.lower():
            yaml_output['exporter_acm'][hostname]['type'] = 'lsp'
        elif 'ess' in hostname.lower():
            yaml_output['exporter_acm'][hostname]['type'] = 'ess'
        else:
            yaml_output['exporter_acm'][hostname]['type'] = 'acm'
        yaml_output['exporter_acm'][hostname]['location'] = location
        yaml_output['exporter_acm'][hostname]['country'] = country
        yaml_output['exporter_acm'][hostname]['username'] = ssh_username
        yaml_output['exporter_acm'][hostname]['password'] = ssh_password

        new_entries.append(row)

    # Load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)
    # Sort the YAML data by hostname before writing it to the output file
    sorted_yaml_output = OrderedDict(sorted(yaml_output['exporter_acm'].items(), key=lambda x: x[0]))
    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_acm', existing_yaml_output, new_entries, yaml_output, output_path)

################################################################## WEBLM_EXPORTER ##############################################################################

def exporter_weblm(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter Weblm called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_weblm')

    if df_filtered.empty:
        flash("No rows matching exporter_weblm condition found")
        return

    output_path = os.path.join(output_dir, output_file)

    hostname = df_filtered['FQDN'].iloc[0]

    # Initialize exporter_weblm key in the YAML dictionary
    yaml_output['exporter_weblm'][hostname] = OrderedDict()

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        listen_port = row['App-Listen-Port']
        ssh_username = row.get('ssh_username', 'put your username here')
        ssh_password = row.get('ssh_password', 'put your password here')

        if ip_exists_in_yaml('exporter_weblm', ip_address, output_dir=output_dir, output_file=output_file):
            continue

        yaml_output['exporter_weblm'][hostname]['ip_address'] = ip_address
        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1
        yaml_output[exporter_weblm][hostname][ip_address]['listen_port'] = int(row['App-Listen-Port'])
        yaml_output['exporter_weblm'][hostname]['location'] = location
        yaml_output['exporter_weblm'][hostname]['country'] = country
        yaml_output['exporter_weblm'][hostname]['data_path'] = '/opt/Avaya/tomcat/webapps/WebLM/data/'
        yaml_output['exporter_weblm'][hostname]['username'] = ssh_username
        yaml_output['exporter_weblm'][hostname]['password'] = ssh_password

        new_entries.append(row)

    # Load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)  

    process_exporter('exporter_weblm', existing_yaml_output, new_entries, yaml_output, output_path)



############################################################## Exporter Network #####################################################################

def exporter_network(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter Network called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_network')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_network key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_network', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_network'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        if ip_address not in yaml_output[exporter_name][hostname]:
            yaml_output[exporter_name][hostname] = {}

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1
        yaml_output[exporter_name][hostname]['ip_address'] = ip_address
        yaml_output[exporter_name][hostname]['listen_port'] = int(row['App-Listen-Port'])

        yaml_output[exporter_name][hostname]['location'] = location
        yaml_output[exporter_name][hostname]['country'] = country
        yaml_output[exporter_name][hostname]['snmp_version'] = 3
        yaml_output[exporter_name][hostname]['username'] = row['snmp_user']
        yaml_output[exporter_name][hostname]['privacy_protocol'] = 'aes'
        yaml_output[exporter_name][hostname]['privacy_passphrase'] = row.get('snmp_password', 'default_passphrase')
        yaml_output[exporter_name][hostname]['auth_protocol'] = 'sha'
        yaml_output[exporter_name][hostname]['auth_passphrase'] = row.get('snmp_password', 'default_passphrase')

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)  # Add this line to load existing YAML data
    # Write the YAML data to a file, either appending to an existing file or creating a new file
    process_exporter('exporter_network', existing_yaml_output, new_entries, yaml_output, output_path)



############################################################### Exporter AAEP #####################################################################################
def exporter_aaep(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter AAEP called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_aaep')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_aaep key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_aaep', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_aaep'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        snmp_version = row.get('snmp_version', '2')
        snmp_user = row.get('snmp_user', '')

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        yaml_output[exporter_name][hostname]['ip_address'] = ip_address

        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1
        yaml_output[exporter_name][hostname]['listen_port'] = int(listen_port)

        yaml_output[exporter_name][hostname]['location'] = location
        yaml_output[exporter_name][hostname]['country'] = country
        yaml_output[exporter_name][hostname]['snmp_version'] = snmp_version

        if snmp_version == '3':
            yaml_output[exporter_name][hostname]['username'] = snmp_user
            yaml_output[exporter_name][hostname]['privacy_protocol'] = 'aes'
            yaml_output[exporter_name][hostname]['privacy_passphrase'] = 'Sab10maas'
            yaml_output[exporter_name][hostname]['auth_protocol'] = 'sha'
            yaml_output[exporter_name][hostname]['auth_passphrase'] = 'Sab10maas'
        else:
            if 'comm_string' in df.columns and not pd.isna(row['comm_string']):
                yaml_output[exporter_name][hostname]['community'] = row['comm_string']
            else:
                yaml_output[exporter_name][hostname]['community'] = 'ENC'

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)
    # Write the YAML data to a file, either appending to an existing file or creating a new file
    process_exporter('exporter_aaep', existing_yaml_output, new_entries, yaml_output, output_path)



############################################################### Exporter PfSense  ##########################################################################

def exporter_pfsense(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter pfSense called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_pfsense')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_pfsense key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_pfsense', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_pfsense'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        snmp_version = row.get('snmp_version', '2')
        snmp_user = row.get('snmp_user', '')

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        if ip_address not in yaml_output[exporter_name][hostname]:
            yaml_output[exporter_name][hostname] = {}

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1
        yaml_output[exporter_name][hostname]['ip_address'] = ip_address
        yaml_output[exporter_name][hostname]['listen_port'] = int(row['App-Listen-Port'])

        yaml_output[exporter_name][hostname]['location'] = location
        yaml_output[exporter_name][hostname]['country'] = country
        yaml_output[exporter_name][hostname]['snmp_version'] = snmp_version

        if snmp_version == '3':
            yaml_output[exporter_name][hostname]['username'] = snmp_user
            yaml_output[exporter_name][hostname]['privacy_protocol'] = 'aes'
            yaml_output[exporter_name][hostname]['privacy_passphrase'] = 'Sab10maas'
            yaml_output[exporter_name][hostname]['auth_protocol'] = 'sha'
            yaml_output[exporter_name][hostname]['auth_passphrase'] = 'Sab10maas'
        else:
            if 'comm_string' in df.columns and not pd.isna(row['comm_string']):
                yaml_output[exporter_name][hostname]['community'] = row['comm_string']
            else:
                yaml_output[exporter_name][hostname]['community'] = 'ENC'

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)
    # Write the YAML data to a file, either appending to an existing file or creating a new file
    process_exporter('exporter_pfsense', existing_yaml_output, new_entries, yaml_output, output_path)



################################################################ Exporter AIC  ################################################################

def exporter_aic(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter AIC called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_aic')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_aic key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_aic', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_aic'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        yaml_output[exporter_name][hostname]['ip_address'] = ip_address

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1

        yaml_output[exporter_name][hostname]['listen_port'] = int(listen_port)
        yaml_output[exporter_name][hostname]['location'] = location
        yaml_output[exporter_name][hostname]['country'] = country

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_aic', existing_yaml_output, new_entries, yaml_output, output_path)


################################################################# EXPORTER OCEANA MONITOR  ###############################################################

def exporter_oceanamonitor(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter OceanaMonitor called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_oceanamonitor')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_oceanamonitor key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_oceanamonitor', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_oceanamonitor'
        fqdn = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if fqdn not in yaml_output[exporter_name]:
            yaml_output[exporter_name][fqdn] = {}

        yaml_output[exporter_name][fqdn]['ip_address'] = ip_address

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1

        yaml_output[exporter_name][fqdn]['listen_port'] = int(listen_port)
        yaml_output[exporter_name][fqdn]['location'] = location
        yaml_output[exporter_name][fqdn]['country'] = country

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_oceanamonitor', existing_yaml_output, new_entries, yaml_output, output_path)


############################################################## EXPORTER AUDIO CODE SBC ######################################################################

def exporter_audiocodesbc(file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash("Exporter AudioCodesBC called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_audiocodesbc')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_audiocodesbc key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_audiocodesbc', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_audiocodesbc'
        hostname = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']
        snmp_version = row.get('snmp_version', 2)

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if hostname not in yaml_output[exporter_name]:
            yaml_output[exporter_name][hostname] = {}

        yaml_output[exporter_name][hostname]['ip_address'] = ip_address
        yaml_output[exporter_name][hostname]['listen_port'] = int(row.get('App-Listen-Port', default_listen_port.get()))
        yaml_output[exporter_name][hostname]['location'] = location
        yaml_output[exporter_name][hostname]['country'] = country
        yaml_output[exporter_name][hostname]['snmp_version'] = snmp_version

        if 'comm_string' in df.columns and not pd.isna(row['comm_string']):
            yaml_output[exporter_name][hostname]['community'] = row['comm_string']
        else:
            yaml_output[exporter_name][hostname]['community'] = 'ENC'

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_audiocodesbc', existing_yaml_output, new_entries, yaml_output, output_path)


########################################################### EXPORTER BAAS ##############################################################################

def exporter_baas(file_path, output_file, output_dir):
    global default_listen_port

    try:
        flash("Exporter BaaS called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_baas')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_baas key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_baas', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_baas'
        fqdn = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if fqdn not in yaml_output[exporter_name]:
            yaml_output[exporter_name][fqdn] = {}

        yaml_output[exporter_name][fqdn]['ip_address'] = ip_address

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1

        yaml_output[exporter_name][fqdn]['listen_port'] = int(listen_port)
        yaml_output[exporter_name][fqdn]['location'] = location
        yaml_output[exporter_name][fqdn]['country'] = country
        yaml_output[exporter_name][fqdn]['username'] = 'maas'
        yaml_output[exporter_name][fqdn]['extra_args'] = " --backup.timeout=30s --backup.frequency=1m "

        ssh_password_present = 'ssh_password' in row
        if ssh_password_present and not pd.isna(row['ssh_password']):
            yaml_output[exporter_name][fqdn]['password'] = row['ssh_password']
        else:
            yaml_output[exporter_name][fqdn]['password'] = 'ENC'

        yaml_output[exporter_name][fqdn]['bucket'] = 's3://<s2bucket>'

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_baas', existing_yaml_output, new_entries, yaml_output, output_path)


############################################################# Exporter Redis ###################################################################################

def exporter_redis(file_path, output_file, output_dir):
    global default_listen_port

    try:
        log("Exporter Redis called")

        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, 'exporter_redis')
    output_path = os.path.join(output_dir, output_file)

    # Initialize exporter_redis key in the YAML dictionary
    yaml_output = OrderedDict([('exporter_redis', OrderedDict())])

    # Iterate over rows in filtered dataframe
    new_entries = []
    for index, row in df_filtered.iterrows():
        exporter_name = 'exporter_redis'
        fqdn = row['FQDN']
        ip_address = row['IP Address']
        location = row['Location']
        country = row['Country']

        if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
            continue

        if fqdn not in yaml_output[exporter_name]:
            yaml_output[exporter_name][fqdn] = {}

        yaml_output[exporter_name][fqdn]['ip_address'] = ip_address

        # Use default_listen_port if 'App-Listen-Port' is not available
        listen_port = row.get('App-Listen-Port', default_listen_port)
        if listen_port == default_listen_port:
            default_listen_port += 1

        yaml_output[exporter_name][fqdn]['listen_port'] = int(listen_port)
        yaml_output[exporter_name][fqdn]['location'] = location
        yaml_output[exporter_name][fqdn]['country'] = country
        yaml_output[exporter_name][fqdn]['debug'] = True
        yaml_output[exporter_name][fqdn]['application'] = "Verint Mobile Gateway"

        new_entries.append(row)

    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter('exporter_redis', existing_yaml_output, new_entries, yaml_output, output_path)


################################################# ADD SNMP ARGS ########################################

def add_snmp_args(file_path, output_file):
    global output_path
    output_dir = tempfile.gettempdir()
    output_path = os.path.join(output_dir, output_file)

    try:
        flash("Add SNMP Args called")
        df = read_input_file(file_path)

    except Exception as e:
        log(f"Error: {e}")
        return

    snmp_args_string = 'trap_extra_args: " --snmp.version 3 --snmp.username username --snmp.privacy-protocol aes --snmp.privacy-passphrase password --snmp.auth-protocol sha --snmp.auth-passphrase password"'

    # Add this line to load existing YAML data
    existing_yaml_output = load_existing_yaml(output_path)

    # Insert the new SNMP args string at the top of the YAML file
    with open(output_path, 'r') as file:
        original_content = file.read()

    with open(output_path, 'w') as file:
        file.write(snmp_args_string + '\n' + original_content)

    flash(f"SNMP Args added to the top of the Yaml{output_path}")

######################################################## exporter_generic ###############################################################################

def exporter_generic(exporter_name, file_path, output_file, output_dir):
    global default_listen_port
    global output_path

    try:
        flash(f"Exporter {exporter_name} called")
        df = read_input_file(file_path)

    except Exception as e:
        flash(f"Error: {e}")
        return

    df_filtered = filter_rows_by_exporter(df, exporter_name)
    output_path = os.path.join(output_dir, output_file)

    yaml_output = {exporter_name: {}}

    for index, row in df_filtered.iterrows():
        process_row_generic(exporter_name, row, yaml_output, default_listen_port)

    new_entries = df_filtered.to_dict('records')
    existing_yaml_output = load_existing_yaml(output_path)

    # Write the YAML data to a file, either updating the existing file or creating a new file
    process_exporter(exporter_name, existing_yaml_output, new_entries, yaml_output, output_path)


###########################################################   process_row_generic   ###################################################################

def process_row_generic(exporter_name, row, yaml_output, default_listen_port):
    hostname = row['FQDN']
    ip_address = row['IP Address']
    location = row['Location']
    country = row['Country']

    if ip_exists_in_yaml(exporter_name, ip_address, output_path=output_path):
        return

    if hostname not in yaml_output[exporter_name]:
        yaml_output[exporter_name][hostname] = OrderedDict()

    # Use default_listen_port if 'App-Listen-Port' is not available
    listen_port = row.get('App-Listen-Port', default_listen_port)
    if listen_port == default_listen_port:
        default_listen_port += 1

    yaml_output[exporter_name][hostname]['ip_address'] = ip_address
    yaml_output[exporter_name][hostname]['listen_port'] = int(listen_port)
    yaml_output[exporter_name][hostname]['location'] = location
    yaml_output[exporter_name][hostname]['country'] = country

    ssh_username_present = 'ssh_username' in row
    ssh_password_present = 'ssh_password' in row

    # Use the values from the optional headers if present, otherwise use the placeholders
    if ssh_username_present and not pd.isna(row['ssh_username']):
        yaml_output[exporter_name][hostname]['username'] = row['ssh_username']
    else:
        yaml_output[exporter_name][hostname]['username'] = 'root'

    if ssh_password_present and not pd.isna(row['ssh_password']):
        yaml_output[exporter_name][hostname]['password'] = row['ssh_password']
    else:
        yaml_output[exporter_name][hostname]['password'] = 'ENC'

#####################################################   filter_rows_by_exporter   ################################################################

def filter_rows_by_exporter(df, exporter_name):
    os_exporters = ['exporter_linux', 'exporter_windows', 'exporter_verint', 'exporter_vmware']
    
    if exporter_name in os_exporters:
        column_name = 'Exporter_name_os'
    else:
        column_name = 'Exporter_name_app'
    
    return df[df[column_name] == exporter_name]

#####################################################     read input file    ##########################################################################

def read_input_file(file_path):
    # Check if file is CSV or Excel
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == '.csv':
        # Read CSV file into pandas
        df = pd.read_csv(file_path, skiprows=6, low_memory=False)
    elif file_extension in ['.xlsx', '.xls']:
        # Read Excel file into pandas
        df = pd.read_excel(file_path, sheet_name='Sheet2', skiprows=range(0, 6))
    else:
        raise ValueError("Invalid file type. Only CSV and Excel files are supported.")
    return df

################################################### write to Yaml file and print.F   #################################################################

def process_exporter(exporter_name, existing_yaml_output, new_entries, yaml_output, output_path):
    # Write the YAML data to a file, either updating the existing file or creating a new file
    if new_entries:
        # Sort the YAML data by hostname before writing it to the output file
        sorted_yaml_output = OrderedDict(sorted(yaml_output.items(), key=lambda x: x[0]))
        # write to the output file
        write_yaml(existing_yaml_output, sorted_yaml_output, output_path)
        flash(f"{exporter_name} completed")
        flash(f"Total number of hosts processed: {len(new_entries)}")
    else:
        flash(f"{exporter_name} completed - nothing to do")

########################################################## load existing yaml  ###########################################################################

def load_existing_yaml(output_path):
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            existing_yaml_output = yaml.safe_load(f)
            return existing_yaml_output if existing_yaml_output is not None else {}
    return {}

################################################    Check if IP in Yaml exists in filetered csv  #########################################################

def ip_exists_in_yaml(exporter_name, ip_address, output_path):
    """
    Check if the given IP address already exists in the YAML file for the given exporter
    """
    if not os.path.exists(output_path):
        return False

    with open(output_path, 'r') as f:
        yaml_output = yaml.safe_load(f)
        if yaml_output is not None and exporter_name in yaml_output:
            for hostname, ip_data in yaml_output[exporter_name].items():
                if 'ip_address' in ip_data and ip_data['ip_address'] == ip_address:
                    return True
    return False

######################################################      Write Yaml    ################################################################################

def write_yaml(existing_yaml_output, yaml_output, output_path):
    # Update the existing YAML data with the new entries
    for key, value in yaml_output.items():
        if key not in existing_yaml_output:
            existing_yaml_output[key] = {}
        existing_yaml_output[key].update(value)

    # Write the updated YAML data back to the file
    with open(output_path, 'w', encoding='utf8') as f:
        yaml.dump(existing_yaml_output, f, allow_unicode=True)

########

def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))

yaml.add_representer(OrderedDict, dict_representer)
yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, dict_constructor)

#######################################################   MAIN SECTION   ##################################################################################
def run_exporters(selected_exporter_names, output_file, output_dir, file_path):
    global default_listen_port

    # Get the starting value for the listen port
    try:
        default_listen_port = int(request.form.get('default_listen_port', '6001'))  # Replace '6001' with your desired default port number
    except ValueError:
        flash('Error', 'Please enter a valid starting value for the listen port')
        return


    # Validate inputs
    if not file_path or not output_file or not output_dir:
        flash('Error', 'Please enter all fields')
        return

    # Check if any exporters were selected
    if not selected_exporter_names:
        flash('Error', 'Please select at least one exporter')
        return

    # Run selected exporters
    if 'all' in selected_exporter_names:
        flash('Running all exporters .. this will take a moment')
        run_scripts(['exporter_linux', 'exporter_blackbox', 'exporter_breeze', 'exporter_aes', 'exporter_sm', 'exporter_avayasbc', 'exporter_gateway', 'exporter_verint', 'exporter_windows', 'exporter_ssl', 'exporter_cms', 'exporter_acm', 'exporter_jmx', 'exporter_weblm', 'exporter_vmware', 'exporter_kafka', 'exporter_callback', 'exporter_drac', 'exporter_genesyscloud', 'exporter_tcti'], file_path, output_file, output_dir)
    else:
        for exporter_name in selected_exporter_names:
            if exporter_name == 'exporter_linux':
                flash("Running exporter_linux")
                exporter_linux(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_blackbox':
                flash("Running exporter_blackbox")
                exporter_blackbox(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_ssl':
                flash("Running exporter_ssl")
                exporter_ssl(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_aes':
                flash("Running exporter_aes")
                exporter_aes(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_cms':
                flash("Running exporter_cms")
                exporter_cms(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_windows':
                flash("Running exporter_windows")
                exporter_windows(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_avayasbc':
                flash("Running exporter_avayasbc")
                exporter_avayasbc(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_verint':
                flash("Running exporter_verint")
                exporter_verint(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_gateway':
                flash("Running exporter_gateway")
                exporter_gateway(file_path, output_file, output_dir) 
            elif exporter_name == 'exporter_breeze':
                flash("Running exporter_breeze")
                exporter_breeze(file_path, output_file, output_dir) 
            elif exporter_name == 'exporter_sm':
                flash("Running exporter_sm")
                exporter_sm(file_path, output_file, output_dir) 
            elif exporter_name == 'exporter_acm':
                flash("Running exporter_acm")
                exporter_acm(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_jmx':
                flash("Running exporter_jmx")
                exporter_jmx(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_weblm':
                flash("Running exporter_weblm")
                exporter_weblm(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_vmware':
                flash("Running exporter_vmware")
                exporter_vmware(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_kafka':
                flash("Running exporter_kafka")
                exporter_kafka(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_callback':
                flash("Running exporter_callback")
                exporter_callback(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_drac':
                flash("Running exporter_drac")
                exporter_drac(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_genesyscloud':
                flash("Running exporter_genesyscloud")
                exporter_genesyscloud(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_tcti':
                flash("Running exporter_tcti")
                exporter_tcti(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_network':
                flash("Running exporter_network")
                exporter_network(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_aaep':
                flash("Running exporter_aaep")
                exporter_aaep(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_pfsense':
                flash("Running exporter_pfsense")
                exporter_pfsense(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_aic':
                flash("Running exporter_aic")
                exporter_aic(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_voiceportal':
                flash("Running exporter_voiceportal")
                exporter_voiceportal(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_aam':
                flash("Running exporter_aam")
                exporter_aam(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_ipo':
                flash("Running exporter_ipo")
                exporter_ipo(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_iq':
                flash("Running exporter_iq")
                exporter_iq(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_mpp':
                flash("Running exporter_mpp")
                exporter_mpp(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_ams':
                flash("Running exporter_ams")
                exporter_ams(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_pc5':
                flash("Running exporter_pc5")
                exporter_pc5(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_wfodb':
                flash("Running exporter_wfodb")
                exporter_wfodb(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_audiocodesbc':
                flash("Running exporter_audiocodesbc")
                exporter_audiocodesbc(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_baas':
                flash("Running exporter_baas")
                exporter_baas(file_path, output_file, output_dir)
            elif exporter_name == 'exporter_redis':
                flash("Running exporter_redis")
                exporter_redis(file_path, output_file, output_dir)
            elif exporter_name == 'add_snmp_args':
                flash("Adding snmp v3 extra_args to top of YAML")
                add_snmp_args(file_path, output_file)


    # Show success message
    flash('Success', 'Exporters completed')

default_listen_port = []

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'docx', 'yaml', 'yml'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.secret_key = "your_secret_key"

# Your exporter functions should be imported here
# from your_exporters_module import ...


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the CSV file is selected
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            session['csv_file_path'] = file_path

            # Check if an existing YAML file is provided
            if 'existing_yaml' in request.files and request.files['existing_yaml'].filename != '':
                existing_yaml_file = request.files['existing_yaml']
                if allowed_file(existing_yaml_file.filename):
                    existing_yaml_filename = secure_filename(existing_yaml_file.filename)
                    existing_yaml_path = os.path.join(app.config['UPLOAD_FOLDER'], existing_yaml_filename)
                    existing_yaml_file.save(existing_yaml_path)
                    session['existing_yaml_path'] = existing_yaml_path
                else:
                    flash('Invalid existing YAML file')
                    return redirect(request.url)

            return redirect(url_for('process_file'))

        else:
            flash('Invalid file format')
            return redirect(request.url)

    return render_template('upload.html')


LOG_FILE = 'app_logs.txt'

@app.route('/get_logs', methods=['GET'])
def get_logs():
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            log_data = log_file.read()
            return log_data
    return ''

# In your Flask application
app_log = []

def log(message, message_type=None):
    if message_type:
        formatted_message = f"{message_type}: {message}"
    else:
        formatted_message = message
    app_log.append(formatted_message)

@app.route('/process', methods=['GET', 'POST'])
def process_file():
    if request.method == 'POST':
        # Collect variables from the form
        selected_exporter_names = request.form.getlist('exporters')
        output_file = f"{os.path.splitext(os.path.basename(session['csv_file_path']))[0]}_output.yaml"
        output_dir = app.config['UPLOAD_FOLDER']

        run_exporters(selected_exporter_names,output_file, output_dir, session['csv_file_path'])

        # Redirect to the download page
        return redirect(url_for('download', file_name=output_file))

    return render_template('process.html')


@app.route('/finish_and_clean', methods=['POST'])
def finish_and_clean():
    # Delete all files in the /tmp/ directory
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    # Redirect the user back to the index page
    return redirect(url_for('upload_file'))

########## error handling

@app.errorhandler(KeyError)
def handle_key_error(e):
    app.logger.exception("A KeyError occurred")
    error_message = f"A KeyError occurred: {e}"
    return render_template("error.html", error_message=error_message), 400

@app.errorhandler(ValueError)
def handle_value_error(e):
    error_message = f"A ValueError occurred: {e}"
    return render_template("error.html", error_message=error_message), 400

@app.errorhandler(FileNotFoundError)
def handle_file_not_found_error(e):
    error_message = f"A FileNotFoundError occurred: {e}"
    return render_template("error.html", error_message=error_message), 404

@app.errorhandler(OSError)
def handle_os_error(e):
    error_message = f"An OSError occurred: {e}"
    return render_template("error.html", error_message=error_message), 500

@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_request_entity_too_large(e):
    error_message = f"File size exceeds the allowed limit: {e}"
    return render_template("error.html", error_message=error_message), 413

@app.errorhandler(Exception)
def handle_generic_error(e):
    error_message = f"An unexpected error occurred: {e}"
    app.logger.exception("An unexpected error occurred")
    return render_template("error.html", error_message=error_message), 500
############ end of error handling


@app.route('/terminal')
def terminal():
    return render_template('terminal.html')


@app.route('/download/<file_name>')
def download(file_name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

if __name__ == '__main__':
    app.run(debug=True, port=8000)
