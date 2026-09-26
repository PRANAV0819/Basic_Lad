# config/__init__.py
# Enable PyMySQL to act as the MySQLdb driver for Django
import pymysql

pymysql.install_as_MySQLdb()
