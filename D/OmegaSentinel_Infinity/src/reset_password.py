import sqlite3

conn = sqlite3.connect('data/omega.db')
cur = conn.cursor()
hashed_password = '$pbkdf2-sha256$29000$ujfmnPPeGwMAICQEIKS09g$5I7q.bAGS31ewo/NYbpevLTYJ0A1x4GLSGjEbHDAHko'
cur.execute('UPDATE users SET hashed_password = ? WHERE username = ?', (hashed_password, 'admin'))
conn.commit()
conn.close()
print('✓ Password reset to: admin / letmein')
