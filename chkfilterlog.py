import socket
from ipwhois import IPWhois
import re
import sqlite3
import time
import json
import pandas as pd
import ipaddress
import requests
import argparse

def read_log_file() -> list:
    logfile = '/var/log/remote/192.168.1.1/filterlog.log'
    with open(logfile, 'r') as f:
        rawlogs = f.readlines()
    return rawlogs

def convert_logs_to_dataframe(rawlogs: list, asn_data: dict) -> pd.DataFrame:
    pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}) "
        r"(?P<log_hostname>\S+) filterlog\[(?P<pid>\d+)\]: "
        r"(?P<rule_number>\d+),(?P<subrule_number>\d*),(?P<anchor>\w*),(?P<tracker>\d+),"
        r"(?P<interface>\w+(\.\d{1,2})*),(?P<reason>[\w\(\)]+),(?P<action>[\w\(\)]+),"
        r"(?P<direction>[\w+\(\)]+),(?P<ip_ver>4),(?P<tos>0x[\da-fA-F]+),(?P<ecn>\w*),"
        r"(?P<ttl>\d+),(?P<id>\d+),(?P<offset>\d+),(?P<flags>\w+),(?P<protocol_id>\d{1,3}),"
        r"(?P<protocol_text>[\w\-+\.\/]*),(?P<length>\d+),"
        r"(?P<src_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}),"
        r"(?P<dest_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}),"
        r"(?P<src_port>\d{1,5})?,?(?P<dest_port>\d{1,5})?,?(?P<body>.*)$",
        flags=re.MULTILINE
    )
    rawdata = [re.match(pattern,k).groupdict() for k in rawlogs if re.match(pattern,k)]

    # Precompute address to ASN mapping for O(1) lookups
    address_to_asn = {addr: data['asn_info'] for data in asn_data.values() for addr in data['addresses']}

    for line in rawdata:
        line['src_asn'] = address_to_asn.get(line['src_address'], 'N/A')
        line['dest_asn'] = address_to_asn.get(line['dest_address'], 'N/A')

    df = pd.DataFrame([k for k in rawdata])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

def update_asn_data_ipinfo(df: pd.DataFrame) -> dict:
    asn_data = read_asn_data()
    known_addresses = {addr for data in asn_data.values() for addr in data['addresses']}

    for idx, address in enumerate(df['src_address']):
        asn_info = 'N/A'
        if str(address) in known_addresses:
            print(f"[{idx} / {len(df)}] Address {address} already exists in ASN data. Skipping update.")
            continue
        if asn_info == 'N/A':
            try:
                r = requests.get(f'http://ipinfo.io/{address}/org')
                time.sleep(0.2)  # Sleep to avoid hitting rate limits
            except Exception as e:
                print(f"[{idx} / {len(df)}] Error fetching ASN info for {address}: {e} {type(e)}")
        if r.status_code == 200:
            asn_info = r.text  # json().get('org', 'N/A')
            asn_key = asn_info.split()[0]  # Extract ASN number (e.g., "AS12345")
            if asn_key not in asn_data:
                asn_data[asn_key] = {}
                asn_data[asn_key]['asn_info'] = asn_info
                asn_data[asn_key]['addresses'] = []
            asn_data[asn_key]['addresses'].append(str(address))
            with open('asn_data.json', 'w') as f:
                json.dump(asn_data, f, indent=4)
            print(f"[{idx} / {len(df)}] Updated ASN data for {address}: {asn_info}")
        else:
            print(f"[{idx} / {len(df)}] Failed to fetch ASN info for {address}. Status code: {r.status_code} Response: {r.text}")
    return asn_data

def update_asn_data_bgpkit(df: pd.DataFrame) -> dict:
    asn_data = read_asn_data()
    known_addresses = {addr for data in asn_data.values() for addr in data['addresses']}

    for idx, address in enumerate(df['src_address']):
        asn_info = 'N/A'
        if str(address) in known_addresses:
            print(f"[{idx} / {len(df)}] Address {address} already exists in ASN data. Skipping update.")
            continue
        if asn_info == 'N/A':
            try:
                r = requests.get(f'http://api.bgpkit.com/v3/utils/ip?ip={address}')
                time.sleep(0.2)  # Sleep to avoid hitting rate limits
            except Exception as e:
                print(f"[{idx} / {len(df)}] Error fetching ASN info for {address}: {e} {type(e)}")
        if r.status_code == 200:
            asn_info = r.json()
            asn_key = asn_info['asn']['name']
            if asn_key not in asn_data:
                asn_data[asn_key] = {}
                asn_data[asn_key]['asn_info'] = asn_info
                asn_data[asn_key]['addresses'] = []
            asn_data[asn_key]['addresses'].append(str(address))
            with open('asn_data.json', 'w') as f:
                json.dump(asn_data, f, indent=4)
            print(f"[{idx} / {len(df)}] Updated ASN data for {address}: {asn_info}")
        else:
            print(f"[{idx} / {len(df)}] Failed to fetch ASN info for {address}. Status code: {r.status_code} Response: {r.text}")
    return asn_data

def query_bgp_tools(ip: str) -> str:
    """Query bgp.tools on port 43 (whois) for an IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect(("bgp.tools", 43))
            s.sendall((ip + "\n").encode('utf-8'))

            # Receive the response
            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
            return response.decode('utf-8').strip()

    except Exception as e:
        return f"Error: {e} {type(e)}"

def get_networks(df: pd.DataFrame) -> dict:
    networks = {}
    for address_ in df['src_address']:
        address = ipaddress.IPv4Address(address_)
        if address.is_private:
            print(f'Skipping private address: {address}')
            continue
        network = ipaddress.IPv4Network(f"{address}/24", strict=False)
        if str(network) not in networks:
            networks[str(network)] = {'addresses': {}}
            networks[str(network)]['addresses'][address_] = {'src_address': str(address), 'count': 1}
        else:
            previous_count = 0
            if address_ not in networks[str(network)]['addresses']:
                networks[str(network)]['addresses'][address_] = {'src_address': str(address), 'count': 1}
            else:
                previous_count = networks[str(network)]['addresses'][address_]['count']  # if address in networks[network]['addresses'] else 0
                count = previous_count + 1
                print(f"Network {network} already exists. Address {address} count updated to {count}.")
                networks[str(network)]['addresses'][address_] = {'src_address': str(address), 'count': count}
                if count > 10:
                    print(f"Network {network} has {count} blocked addresses: {networks[str(network)]['addresses']}")
    df_networks = pd.DataFrame([{'network': k, 'host_count': len(v['addresses']), 'addresses': v['addresses']} for k,v in networks.items()])
    return df_networks

def read_asn_data() -> dict:
    asn_data = {}
    try:
        with open('asn_data.json', 'r') as f:
            asn_data = json.load(f)
    except Exception as e:
        print(f"Error loading ASN data: {e} {type(e)}")
    return asn_data

def save_to_db(args: argparse.Namespace, df: pd.DataFrame, tablename: str):
    conn = sqlite3.connect(args.db_file)
    df.to_sql(tablename, conn, if_exists='replace', index=False)
    conn.close()
    print(f'Saved DataFrame to database {args.db_file} in table {tablename} with {len(df)} entries.')

def load_from_db(args: argparse.Namespace, tablename: str) -> pd.DataFrame:
    df = pd.DataFrame()
    try:
        conn = sqlite3.connect(args.db_file)
        # Parse 'timestamp' as dates natively so it matches the types of new logs
        df = pd.read_sql_query(f"SELECT * FROM {tablename}", conn, parse_dates=['timestamp'])
        # Clean up any previously saved pandas index columns to avoid duplicates
        drop_cols = [c for c in ['index', 'level_0'] if c in df.columns]
        if drop_cols:
            df = df.drop(columns=drop_cols)
        conn.close()
    except Exception as e:
        print(f"Error loading data from database: {e} {type(e)}")
    return df

def get_args():
    parser = argparse.ArgumentParser(description='Process filter log data.')
    parser.add_argument('--update_asn', action='store_true', help='Update ASN data for blocked source addresses', default=False)
    parser.add_argument('--readlogs', action='store_true', help='Read and process log file', default=False)
    parser.add_argument('--logfile', type=str, default='/var/log/remote/filterlog.log', help='Path to the filter log file')
    parser.add_argument('--read_db', action='store_true', help='Read processed data from database instead of log file', default=False)
    parser.add_argument('--db_file', type=str, default='filterlog.db', help='database file')
    return parser.parse_args()

def asn_lookup(address, asn_data) -> str:
    asn_info = 'N/A'
    for asn_key, asn_entry in asn_data.items():
        if address in asn_entry['addresses']:
            asn_info = asn_entry['asn_info']
            break
    return asn_info

if __name__ == "__main__":
    args = get_args()
    asn_data = read_asn_data()
    print(f"Current ASN data entries: {len(asn_data)}")
    if args.update_asn:
        rawlogs = read_log_file()
        print(f'Total log entries: {len(rawlogs)}')
        df = convert_logs_to_dataframe(rawlogs, asn_data)
        print(f'Total log entries after conversion to DataFrame: {len(df)}')
        if args.read_db:
            old_df = load_from_db(args, 'filterlog')
            print(f'Total log entries loaded from database: {len(old_df)}')
            df = pd.concat([old_df, df]).drop_duplicates().reset_index(drop=True)
            print(f'Total log entries after merging with database: {len(df)}')
        save_to_db(args, df, 'filterlog')
        src_address_blocked_df = df[(df['action'] == 'block') & (df['interface'] == 'igb0.4')].groupby(['src_address'], sort=False).agg(count=('src_address','count')).reset_index()
        asn_data = update_asn_data_ipinfo(src_address_blocked_df)
        print(f"Updated ASN data entries: {len(asn_data)}")
    if args.readlogs:
        rawlogs = read_log_file()
        print(f'Total log entries: {len(rawlogs)}')
        df = convert_logs_to_dataframe(rawlogs, asn_data)
        print(f'Total log entries after conversion to DataFrame: {len(df)}')
        if args.read_db:
            old_df = load_from_db(args, 'filterlog')
            print(f'Total log entries loaded from database: {len(old_df)}')
            df = pd.concat([old_df, df]).drop_duplicates().reset_index(drop=True)
            print(f'Total log entries after merging with database: {len(df)}')
        save_to_db(args, df, 'filterlog')
        # src_address_blocked_df = df[(df['action'] == 'block') & (df['interface'] == 'igb0.4')].groupby(['src_address'], sort=False).agg(count=('src_address','count')).reset_index()
        src_address_blocked_df = df[(df['action'] == 'block') & (df['interface'] == 'igb0.4')].groupby(['src_address', 'src_asn'], sort=False).agg(count=('src_address','count')).reset_index()
        print(f'Unique blocked source addresses: {len(src_address_blocked_df)} from {len(df)} total log entries')
        print(src_address_blocked_df.sort_values(by='count',ascending=False).head(20))

        df_networks = get_networks(src_address_blocked_df)
        print(f'Unique /24 Networks: {len(df_networks)} from {len(src_address_blocked_df)} blocked source addresses')
        print(df_networks[df_networks['host_count'] > 5].sort_values(by='host_count', ascending=False).head(20))

        # nets = list(set([ipaddress.IPv4Network('.'.join(k.split('.')[:3])+'.0/24') for k in list(src_address_blocked_df.groupby(['src_address']).count().reset_index()['src_address'])]))
        # collapsed_nets = [k for k in ipaddress.collapse_addresses(nets)]
        # print(f'Collapsed Networks: {len(collapsed_nets)} from {len(nets)} original /24 networks')
