import os
import csv
import time
import requests
import sqlite3
import sys
from requests.adapters import HTTPAdapter, Retry
from urllib3.util.ssl_ import create_urllib3_context

class TLSAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = create_urllib3_context()
        self.ssl_context.options |= 0x4
        self.ssl_context.options |= 0x8 

if len(sys.argv) < 2:
    print("csv from pipeline")
    exit()

file_name = sys.argv[1]
directory = r"c:\..."
file_path = os.path.join(directory, file_name)
db_path = os.path.join(directory, "public_uuids.db")
api_url = "https://api.wynncraft.com/v3/player/{uuid}"
rate_limit = 100 #can make 120 if you want

if not os.path.exists(file_path):
    print(f"File '{file_name}' does not exist in the directory: {directory}")
    exit()

with open(file_path, mode='r') as csv_file:
    reader = csv.DictReader(csv_file)
    uuids = set(row['uuid'] for row in reader if 'uuid' in row)

print(f"Found {len(uuids)} unique UUIDs in today's list.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS public_uuids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL
)
""")
conn.commit()

cursor.execute("DELETE FROM public_uuids WHERE uuid NOT IN ({})".format(",".join("?" for _ in uuids)), tuple(uuids))
conn.commit()
print("Removed rows for UUIDs not in today's list.")

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504]) #My parents house internet gives SSL errors idk why
session.mount("https://", TLSAdapter())
session.mount("https://", HTTPAdapter(max_retries=retries))

api_token = os.environ.get('WYNNCRAFT_API_TOKEN')
if api_token:
    session.headers.update({'Authorization': f'Bearer {api_token}'})
    print("Using API token for enhanced rate limits.")
    rate_limit = 120
else:
    print("No API token found - using standard rate limits.")
    rate_limit = 100

request_count = 0
start_time = time.time()

for index, uuid in enumerate(uuids):
    cursor.execute("SELECT 1 FROM public_uuids WHERE uuid = ?", (uuid,))
    row = cursor.fetchone()
    if row:
        print(f"UUID {uuid} already exists in the database. Skipping API request.")
        continue

    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            response = session.get(api_url.format(uuid=uuid), timeout=10)
            request_count += 1
            
            if response.status_code == 429:
                wait_time = 60 
                print(f"Rate limited (429) for UUID {uuid}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retry_count += 1
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch data for UUID: {uuid}. Status code: {response.status_code}")
                break
            else:
                break
                
        except requests.exceptions.SSLError as e:
            print(f"SSL error for UUID {uuid}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request error for UUID {uuid}: {e}")
            break
    
    if retry_count >= max_retries:
        print(f"Max retries exceeded for UUID {uuid}. Skipping.")
        continue
    
    if response.status_code != 200:
        continue

    data = response.json()
    
    restrictions = data.get('restrictions', {})
    main_access = restrictions.get('mainAccess', True)  
    
    if main_access == False:
        try:
            cursor.execute("""
            INSERT INTO public_uuids (uuid)
            VALUES (?)
            """, (uuid,))
            conn.commit()
            print(f"UUID {uuid} has a public profile and was added to the database.")
        except sqlite3.Error as e:
            print(f"Error inserting UUID {uuid} into database: {e}")
    else:
        print(f"UUID {uuid} has a restricted profile (mainAccess: true). Skipping.")
    elapsed_time = time.time() - start_time
    if request_count >= rate_limit and elapsed_time < 60:
        sleep_time = 60 - elapsed_time
        print(f"Rate limit approaching. Made {request_count} requests in {elapsed_time:.1f}s. Sleeping for {sleep_time:.1f} seconds...")
        time.sleep(sleep_time)
        request_count = 0
        start_time = time.time()

conn.close()
print(f"Public UUIDs saved to the database at {db_path}.")
