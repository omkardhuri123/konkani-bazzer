# kokanibazaar/__init__.py
# Only install pymysql as MySQLdb when pymysql is actually available.
# This allows the project to start correctly even when using SQLite.
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
