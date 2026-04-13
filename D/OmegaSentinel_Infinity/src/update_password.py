import sqlite3

conn = sqlite3.connect('data/omega.db')
cur = conn.cursor()
hashed_password = '$pbkdf2-sha256$29000$rvUewzhHaA3hnDMGQAhhLA$5n8EF3lgUaIQldY514EsQzM'
cur.execute('UPDATE users SET hashed_password = ? WHERE username = ?', (hashed_password, 'admin'))
conn.commit()
conn.close()
print('✓ Password updated successfully!')
print('New credentials: admin / admin12345')
