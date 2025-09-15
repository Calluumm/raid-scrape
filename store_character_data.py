import sqlite3
import requests
from requests.adapters import HTTPAdapter, Retry
from urllib3.util.ssl_ import create_urllib3_context
from datetime import datetime
import time
import os

db_path = r"c:\...\public_uuids.db"
character_api_url = "https://api.wynncraft.com/v3/player/{primary_uuid}/characters/{character_uuid}"
abilities_api_url = "https://api.wynncraft.com/v3/player/{primary_uuid}/characters/{character_uuid}/abilities"
archetype_nodes = {
    "helicopter": "Boltslinger",  # archer
    "manaTrap": "Trapper",        # archer
    "concentration": "Sharpshooter",  # archer
    "nightcloakKnives": "Shadestepper",  # assassin
    "maliciousMockery": "Trickster",      # assassin
    "lacerate": "Acrobat",        # assassin
    "timeDilation": "Riftwalker",  # mage
    "ophanim": "Lightbender",     # mage
    "arcaneTransfer": "Arcanist",  # mage
    "jungleSlayer": "Summoner",   # shaman
    "maskOfTheAwakened": "Ritualist",  # shaman
    "bloodPool": "Acolyte",       # shaman
    "betterEnragedBlow": "Fallen",  # warrior
    "roundabout": "Battle Monk",  # warrior
    "heavenlyTrumpet": "Paladin"  # warrior
}

class TLSAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = create_urllib3_context()
        self.ssl_context.options |= 0x4
        self.ssl_context.options |= 0x8 

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

session = requests.Session()
session.mount("https://", TLSAdapter())
session.mount("https://", HTTPAdapter(max_retries=retries))

api_token = os.environ.get('WYNNCRAFT_API_TOKEN')
if api_token:
    session.headers.update({'Authorization': f'Bearer {api_token}'})
    print("Using API token for enhanced rate limits.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
SELECT character_uuid, primary_uuid,
       delta_nest_of_the_grootslangs,
       delta_the_canyon_colossus,
       delta_orphions_nexus_of_light,
       delta_the_nameless_anomaly
FROM character_raids
WHERE delta_nest_of_the_grootslangs != 0
   OR delta_the_canyon_colossus != 0
   OR delta_orphions_nexus_of_light != 0
   OR delta_the_nameless_anomaly != 0
""")
changed_characters = cursor.fetchall()

request_count = 0
rate_limit = 100 #can make 120

for character_uuid, primary_uuid, delta_nest, delta_canyon, delta_orphion, delta_nameless in changed_characters:
    if request_count >= rate_limit:
        print("Rate limit reached. Sleeping for 60 seconds...")
        time.sleep(60)
        request_count = 0

    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            response = session.get(character_api_url.format(primary_uuid=primary_uuid, character_uuid=character_uuid), timeout=10)
            request_count += 1
            
            if response.status_code == 429:
                wait_time = 60
                print(f"Rate limited (429) for character {character_uuid}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retry_count += 1
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch skill points for character {character_uuid}. Status code: {response.status_code}")
                break
            else:
                break
                
        except requests.exceptions.SSLError as e:
            print(f"SSL error for character {character_uuid}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request error for character {character_uuid}: {e}")
            break
    
    if retry_count >= max_retries:
        print(f"Max retries exceeded for character {character_uuid}. Skipping.")
        continue
    
    if response.status_code != 200:
        continue

    character_data = response.json()
    
    if not character_data or not isinstance(character_data, dict):
        print(f"Invalid character data for {character_uuid}: {character_data}")
        continue
    
    skill_points = character_data.get("skillPoints", {})
    
    if skill_points is None:
        print(f"No skill points data for character {character_uuid}")
        skill_points = {}
    
    strength = skill_points.get("strength", 0)
    dexterity = skill_points.get("dexterity", 0)
    intelligence = skill_points.get("intelligence", 0)
    defense = skill_points.get("defense", 0)
    agility = skill_points.get("agility", 0)
    class_type = character_data.get("type", "Unknown")

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = session.get(abilities_api_url.format(primary_uuid=primary_uuid, character_uuid=character_uuid), timeout=10)
            request_count += 1
            
            if response.status_code == 429:
                wait_time = 60
                print(f"Rate limited (429) for abilities {character_uuid}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retry_count += 1
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch abilities for character {character_uuid}. Status code: {response.status_code}")
                break
            else:
                break
                
        except requests.exceptions.RetryError as e:
            print(f"Max retries exceeded for abilities {character_uuid}: {e}")
            break
        except requests.exceptions.SSLError as e:
            print(f"SSL error for abilities {character_uuid}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request error for abilities {character_uuid}: {e}")
            break
    
    if retry_count >= max_retries or response.status_code != 200:
        print(f"Skipping abilities for character {character_uuid}, using archetype N/A")
        archetype = "N/A"
    else:
        abilities_data = response.json()
        archetype = "N/A"

        if isinstance(abilities_data, list):
            for ability in abilities_data:
                if ability.get("type") == "ability":
                    ability_id = ability.get("id")
                    if ability_id in archetype_nodes:
                        archetype = archetype_nodes[ability_id]
                        break
                    family = ability.get("family", [])
                    for family_id in family:
                        if family_id in archetype_nodes:
                            archetype = archetype_nodes[family_id]
                            break
        else:
            print(f"Unexpected abilities data format for character {character_uuid}: {abilities_data}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute("""
        INSERT INTO character_data (
            character_uuid,
            primary_uuid,
            strength,
            dexterity,
            intelligence,
            defense,
            agility,
            archetype,
            delta_nest_of_the_grootslangs,
            delta_the_canyon_colossus,
            delta_orphions_nexus_of_light,
            delta_the_nameless_anomaly,
            class_type,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_uuid,
            primary_uuid,
            strength,
            dexterity,
            intelligence,
            defense,
            agility,
            archetype,
            delta_nest,
            delta_canyon,
            delta_orphion,
            delta_nameless,
            class_type,
            timestamp
        ))
        conn.commit()
        print(f"Stored data for character {character_uuid} (Primary UUID: {primary_uuid}).")
    except sqlite3.Error as e:
        print(f"Error storing data for character {character_uuid}: {e}")

conn.close()
print("Character data processing complete.")
