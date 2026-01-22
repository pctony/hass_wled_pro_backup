import requests
import json
import os
import time
from datetime import datetime

# Supervisor API setup
TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_URL = "http://supervisor/core/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def get_options():
    try:
        with open("/data/options.json") as f:
            return json.load(f)
    except:
        return {}

def is_actually_wled(ip):
    try:
        # Check general info to verify it's a WLED device
        r = requests.get(f"http://{ip}/json/info", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('brand') == "WLED" or 'name' in data:
                return data.get('name', 'WLED-Device')
    except:
        pass
    return None

def get_wled_instances():
    print("Discovery: Scanning for WLED candidates...")
    try:
        r = requests.get(f"{HA_URL}/states", headers=HEADERS, timeout=20)
        r.raise_for_status()
        candidates = set()
        for s in r.json():
            eid = s.get('entity_id', '')
            if eid.startswith('sensor.') and ('ip' in eid or 'address' in eid):
                ip = s.get('state')
                if ip and len(ip.split('.')) == 4 and ip not in ['unknown', 'unavailable']:
                    candidates.add(ip)

        verified = []
        for ip in candidates:
            name = is_actually_wled(ip)
            if name:
                verified.append({"host": ip, "title": name})
        print(f"Discovery: Found {len(verified)} verified WLED devices.")
        return verified
    except Exception as e:
        print(f"Error: Discovery failed - {str(e)}")
        return []

def prune_old_backups(base_dir, days):
    now = time.time()
    cutoff = now - (days * 86400)
    if not os.path.exists(base_dir): return

    print(f"Cleanup: Checking for files older than {days} days...")
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for file in files:
            path = os.path.join(root, file)
            try:
                if os.stat(path).st_mtime < cutoff:
                    os.remove(path)
                    print(f"Cleanup: Deleted {file}")
            except: pass
        if not os.listdir(root) and root != base_dir:
            try: os.rmdir(root)
            except: pass

def run_backup_cycle():
    opts = get_options()
    instances = get_wled_instances()
    
    root_mount = opts.get('storage_root', 'share')
    sub_path = opts.get('storage_subfolder', 'wled_backups')
    full_base = os.path.join("/", root_mount, sub_path)
    
    now = datetime.now()
    iso_date_path = now.strftime("%Y/%m/%d") 
    timestamp_folder = now.strftime("%H%M%S")

    for dev in instances:
        safe_name = "".join([c if c.isalnum() else "_" for c in dev['title']])
        target_dir = os.path.join(full_base, safe_name, iso_date_path, timestamp_folder)
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            
            # WLED Backup Endpoints
            # cfg is best via /json/cfg
            # presets are most reliably captured via /presets.json directly
            tasks = {
                "cfg": f"http://{dev['host']}/json/cfg",
                "presets": f"http://{dev['host']}/presets.json"
            }

            for name, url in tasks.items():
                if name == "presets" and not opts.get("include_presets"):
                    continue
                try:
                    resp = requests.get(url, timeout=25) # Extra timeout for large preset files
                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                            if not data:
                                print(f"Info: [{dev['title']}] {name} is empty.")
                                continue
                            dest = os.path.join(target_dir, f"{name}.json")
                            with open(dest, 'w') as f:
                                json.dump(data, f, indent=4)
                            print(f"Success: [{dev['title']}] {name} saved.")
                        except ValueError:
                            # In some firmware versions, /presets.json returns raw text
                            dest = os.path.join(target_dir, f"{name}.json")
                            with open(dest, 'w') as f:
                                f.write(resp.text)
                            print(f"Success: [{dev['title']}] {name} (Raw) saved.")
                    else:
                        print(f"Warning: [{dev['title']}] {name} returned HTTP {resp.status_code}")
                except Exception as e:
                    print(f"Error: [{dev['title']}] {name} fetch failed - {str(e)}")
        except Exception as e:
            print(f"Error: [{dev['title']}] folder creation failed - {str(e)}")

    prune_old_backups(full_base, opts.get("retention_days", 30))

def main():
    print("--- WLED Pro Auto-Backup v1.6.2 Starting ---")
    while True:
        opts = get_options()
        run_backup_cycle()
        val = opts.get('interval_value', 24)
        unit = opts.get('interval_unit', 'hours')
        sleep_sec = val * 60 if unit == "minutes" else val * 86400 if unit == "days" else val * 3600
        print(f"Status: Waiting {val} {unit}...")
        time.sleep(sleep_sec)

if __name__ == "__main__":
    main()
