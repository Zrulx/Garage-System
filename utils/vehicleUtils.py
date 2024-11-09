import sqlite3

conn = sqlite3.connect("garage.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS trust
          (spawncode TEXT, owner_id INT, type TEXT, file_link TEXT)''')

def registerVehicle(owner_id: int, type: str):
    c.execute("INSERT INTO trust (owner_id, type) VALUES (?, ?)", (owner_id, type))
    conn.commit()


def getAllUserVehicles(user):
    print(user.id)
    c.execute("SELECT * FROM trust WHERE owner_id = ?", (user.id,))
    vehicles = c.fetchall()
    print(vehicles)
    return vehicles