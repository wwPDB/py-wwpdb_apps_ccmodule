"""
File: DbSession.py  jdw

Simple mysql session wrapper.


Updates:
15-Mar-2016   RPS updated to accommodate parameter for database port number

"""

import MySQLdb
import sys
import os


class DbSession(object):
    """ Class to encapsulate rdbms DBI connection ...
    """
    def __init__(self, dbServer='mysql', dbHost=None, dbName=None, dbUser=None, dbPw=None, dbPort=None):

        if (str(dbServer).lower() not in ['mysql', 'db2']):
            sys.stderr.write("dbConnect: unsupported server %s\n" % dbServer)
            sys.exit(1)

        self.__dbServer = str(dbServer).lower()
        self.__setup(dbServer, dbHost, dbName, dbUser, dbPw, dbPort)
        self.__dbcon = None

    def __setup(self, dbServer, dbHost, dbName, dbUser, dbPw, dbPort):
        if (str(dbServer).lower() == 'mysql'):
            if (dbName is None):
                self.__dbName = os.getenv("MYSQL_DB_NAME")
            else:
                self.__dbName = dbName

            if (dbUser is None):
                self.__dbUser = os.getenv("MYSQL_DB_USER")
            else:
                self.__dbUser = dbUser

            if (dbPw is None):
                self.__dbPw = os.getenv("MYSQL_DB_PW")
            else:
                self.__dbPw = dbPw

            if (dbHost is None):
                self.__dbHost = os.getenv("MYSQL_DB_HOST")
            else:
                self.__dbHost = dbHost

            if (dbPort is None):
                self.__dbPort = os.getenv("MYSQL_DB_PORT")
                if self.__dbPort is None and self.__dbServer == 'mysql':
                    self.__dbPort = 3306  # MySQL default
            else:
                self.__dbPort = dbPort

    def connect(self):
        """ Consistent db connection open method...
        """
        if self.__dbServer == 'mysql':
            return self.__connectMysql()
        else:
            return None

    def close(self):
        """ Consistent db connection close method...
        """
        if self.__dbServer == 'mysql':
            self.__closeMysql()
        else:
            pass

    def __connectMysql(self):
        """ Consistent db connection method...
        """
        try:
            dbcon = MySQLdb.connect(db="%s" % self.__dbName,
                                    user="%s" % self.__dbUser,
                                    passwd="%s" % self.__dbPw,
                                    host="%s" % self.__dbHost,
                                    port=self.__dbPort)
        except:  # noqa: E722 pylint: disable=bare-except
            sys.stderr.write("dbConnect: Connection error server %s host %s dsn %s user %s pw %s port %s\n" %
                             (self.__dbServer, self.__dbHost, self.__dbName, self.__dbUser, self.__dbPw, self.__dbPort))
            sys.exit(1)

        return dbcon

    def __closeMysql(self):
        """ Consistent db close connection method...
        """
        self.__dbcon.close()
