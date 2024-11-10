import sqlite3

conn = sqlite3.connect('garage.db')
c = conn.cursor()

def confirmTebexID(tbxId):
    c.execute('SELECT * FROM trust WHERE payment = ?', (tbxId,))
    vehicle = c.fetchone()
    if vehicle:
        return False
    return True