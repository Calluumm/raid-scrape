import os
import subprocess
import sqlite3

api_token = "wynn api token, store here or in a .env ion car"
os.environ['WYNNCRAFT_API_TOKEN'] = api_token
print("API token set for all requests.")

scripts = {
    "publicprofile_list": r"c:\...\publicprofile_list.py",
    "process_raids": r"c:\...\process_raids.py",
    "store_character_data": r"c:\...\store_character_data.py",
    "infographic_maker": r"c:\...\infographic_maker.py"
}

file_name = "day15-6.csv"  # Taken from valor

print("Collecting public profiles")
subprocess.run(["python", scripts["publicprofile_list"], file_name], check=True)

print("Collecting raid deltas")
subprocess.run(["python", scripts["process_raids"]], check=True)

print("Collecting character data")
subprocess.run(["python", scripts["store_character_data"]], check=True)

print("Generating infographics")
subprocess.run(["python", scripts["infographic_maker"], file_name], check=True)

print("Clearing deltas")
confirm = input("Clear deltas? yes?").strip().lower()

if confirm == 'yes':
    db_path = r"c:\...\public_uuids.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE character_raids
    SET delta_nest_of_the_grootslangs = 0,
        delta_the_canyon_colossus = 0,
        delta_orphions_nexus_of_light = 0,
        delta_the_nameless_anomaly = 0
    """)
    conn.commit()
    conn.close()
    print("Deltas cleared successfully.")
else:
    print("Clearing deltas aborted.")

print("Daily pipeline completed successfully.")
