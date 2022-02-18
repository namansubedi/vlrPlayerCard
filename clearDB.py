#python script to clear the saveInfo.db database
import sqlite3

con = sqlite3.connect('saveInfo.db')
cur = con.cursor()
cur.execute(''' DELETE FROM saveInfo ''')

con.commit()
con.close()
