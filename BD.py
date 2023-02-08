from sqlite3 import *

conn = connect("data.sqlite")
cur = conn.cursor()
cur.executescript("create table messages (id_channel int, id_embed int, id_server int, link text)")
cur.close()
conn.close()
