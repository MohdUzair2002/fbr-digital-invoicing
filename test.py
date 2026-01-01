import sqlite3

conn = sqlite3.connect("sellers.db")
cur = conn.cursor()

cur.execute("""
    UPDATE sellers
    SET seller_ntn_cnic = '4210118991071'
    WHERE id = 8
""")
 # change NTN and id as needed

conn.commit()
conn.close()
