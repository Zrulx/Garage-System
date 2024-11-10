import sqlite3
import requests
import json

conn = sqlite3.connect("garage.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS trust
          (spawncode TEXT, owner_id INT, type TEXT, file_link TEXT, payment TEXT, status TEXT, trust TEXT, ace TEXT, friend_slots INT, locked BOOL DEFAULT '0')''')

def registerVehicle(owner_id: int, type: str, payment: str = None):
    c.execute("INSERT INTO trust (owner_id, type, payment, status) VALUES (?, ?, ?, ?)", (owner_id, type, payment, 'Registered'))
    conn.commit()
    sendTrustToFivem()

def getSpecificUserVehicle(spawncode=None, tbxID=None):
    if spawncode:
        c.execute('SELECT * FROM trust WHERE spawncode = ?', (spawncode))
        vehicle = c.fetchone
    elif tbxID:
        c.execute('SELECT * FROM trust WHERE payment = ?', (tbxID))
        vehicle = c.fetchone
    return vehicle

def getAllUserVehicles(user):
    c.execute("SELECT * FROM trust WHERE owner_id = ?", (user.id,))
    vehicles = c.fetchall()
    return vehicles

def getAllVehicles():
    c.execute("SELECT * FROM trust")
    vehicles = c.fetchall()
    return vehicles

def updateVehicleSpawnCode(selectedVeh, spawncode):
    c.execute("UPDATE trust SET spawncode = ? WHERE owner_id = ? AND type = ? AND payment = ?", (spawncode, selectedVeh[1], selectedVeh[2], selectedVeh[4]))
    conn.commit()
    sendTrustToFivem()

def addFriend(slot, user_id):
    spawncode, owner_id, type, file_link, payment, status, trust, ace, friend_slots, locked = slot
    c.execute('''SELECT trust FROM trust WHERE spawncode = ? AND owner_id = ?''', (spawncode, owner_id))
    result = c.fetchone()

    if result:
        trust_list = result[0]
        if trust_list:
            if str(user_id) in trust_list.split(", "):
                return False
            trust_list = trust_list + ", " + str(user_id)
        else:
            trust_list = str(user_id)

        c.execute('''UPDATE trust SET trust = ? WHERE spawncode = ? AND owner_id = ?''', 
                  (trust_list, spawncode, owner_id))
    else:
        c.execute('''INSERT INTO trust (spawncode, owner_id, trust) VALUES (?, ?, ?)''', 
                  (spawncode, owner_id, str(user_id)))

    conn.commit()
    sendTrustToFivem()
    return True

def sendTrustToFivem():
    c.execute("SELECT spawncode, owner_id, trust, ace, locked FROM TRUST")
    vehicles = c.fetchall()

    # Convert to list of dictionaries for JSON serialization
    vehicles_dict = [
        {"spawncode": vehicle[0], "owner_id": vehicle[1], "trust": vehicle[2], "ace": vehicle[3], "locked": vehicle[4]}
        for vehicle in vehicles
    ]

    headers = {'Content-Type': 'application/json'}
    url = 'http://58.161.167.48:30120/Garage-System/updateTrustList'

    try:
        # Send the JSON data using the 'json' parameter
        response = requests.post(url, json=vehicles_dict, headers=headers)
        
        if response.status_code == 200:
            # print("Successfully sent trust list to FiveM server.")
            pass
        else:
            print(f"Failed to send trust list. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")