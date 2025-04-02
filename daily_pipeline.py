import os
import subprocess
import sqlite3

scripts = {
    "publicprofile_list": r"c:\Users\Student\Desktop\wynn programs\publicprofile_list.py",
    "process_raids": r"c:\Users\Student\Desktop\wynn programs\raiddays\process_raids.py",
    "store_character_data": r"c:\Users\Student\Desktop\wynn programs\raiddays\store_character_data.py"
}
print("Collecting public profiles")
subprocess.run(["python", scripts["publicprofile_list"]], check=True)
print("Collecting raid deltas")
subprocess.run(["python", scripts["process_raids"]], check=True)
print("Collecting character data")
subprocess.run(["python", scripts["store_character_data"]], check=True)
print("Clearing deltas")
db_path = r"c:\Users\Student\Desktop\wynn programs\raiddays\public_uuids.db"
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

print("Daily pipeline completed successfully.")