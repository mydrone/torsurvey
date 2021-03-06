#!/usr/bin/env python
"""
  torsurvey.db - database abstraction
"""

import logging
import sqlite3 as lite

import config

class DbManager(object):
  conn = None

  def __init__(self, path_db=None):
    self.conn = lite.connect(path_db)
    self.conn.execute('pragma foreign_keys = on')
    self.conn.commit()
    self.cur = self.conn.cursor()

  def __del__(self):
    self.conn.close()

  def query(self, arg):
    self.cur.execute(arg)
    self.conn.commit()
    return self.cur

  def check_table(self, name):
    self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % (name))

  def getdb(self):
    con = lite.connect(DB_NAME)
    return con

  def init(self):
    self.cur.execute("CREATE TABLE IF NOT EXISTS sites (id INTEGER primary key, host text unique on conflict ignore, schema text, title text, content blob, status, integer, description text, checked integer, inserted integer)")
    logging.info('Database Initialized')
    return True

  def flush(self):
    self.cur.execute("DROP TABLE sites;")
    self.conn.commit()

  def get_site(self, url):
    c = self.conn.execute("SELECT * from sites where host=?", url)
    print c.fetchone()

  def get_all(self, deadonly=False):
    sql_query = "select id, host from sites order by checked asc, id asc"
    if deadonly:
      sql_query = "select id, host from sites where status!=200 order by checked asc, id asc"
    sites = []
    for row in self.cur.execute(sql_query):
      sites.append((row[0], row[1]))
    return sites

  def list(self):
    for r in self.cur.execute("select host, title from sites"):
      print "%s %s " % (r[0], r[1])

  def update_site(self, id, status_code, title, content, description):
    self.cur.execute("UPDATE sites SET status=?, title=?, description=?, content=?, checked=CURRENT_TIMESTAMP where ID=?", (status_code, title, description, content, id))
    self.conn.commit()
    for r in self.cur.execute("select last_insert_rowid(), changes();"):
      pass
    row_id, changed = r
    if changed:
      return row_id
    return False

  def update_site_status(self, id, status_code):
    self.cur.execute("UPDATE sites SET status=?, checked=CURRENT_TIMESTAMP where ID=?", (status_code, id))
    self.conn.commit()

  def minsert(self, urls):
    inserted = 0
    for u in urls:
      r = self.insert_site(u)
      if r:
        inserted = inserted + 1
        logging.info("Added %s" % u)
    logging.info("Inserted %d" % inserted)

  def insert_site(self, url, schema='http', title=None, content=None):
    self.cur.execute("INSERT INTO sites (host, schema, title, content, inserted) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (url, schema, title, content))
    self.conn.commit()
    for r in self.cur.execute("select last_insert_rowid(), changes();"):
      pass
    row_id, changed = r
    if changed:
      return row_id
    return False
    # return self.cur.lastrowid
    # sql = "INSERT INTO sites (host, schema, title, content, last) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)" % (url, schema, title, content)
    # self.query(sql)