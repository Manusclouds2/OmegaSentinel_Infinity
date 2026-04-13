import sqlite3

conn = sqlite3.connect('data/omega.db')
cur = conn.cursor()
cur.execute('SELECT username, hashed_password FROM users WHERE username = ?', ('admin',))
row = cur.fetchone()
print(f'Username: {row[0]}')
print(f'Hashed Password: {row[1]}')
conn.close()
