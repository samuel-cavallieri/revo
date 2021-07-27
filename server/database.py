import os.path, logging, sqlite3
import settings

class DB(object):
    """Implements sqlite database helper"""

    conn = None
    sqlite_file = settings.sqlite_file_path

    def __init__(self):
        """Initializes a database helper"""
        logging.info('Initializing a database')
        self._connect_db()


    def close(self):
        """Closes a database connection"""

        if DB.conn != None :
            logging.info('Closing the database connection')
            self._close_db_connection()


    def _connect_db(self):
        """Connects to a database, creates required tables"""

        logging.info('Connecting to database %s' % DB.sqlite_file)

        if DB.conn != None :
            logging.info('Database %s has already been opened' % DB.sqlite_file)
            return

        # Connecting to the database file
        DB.conn = sqlite3.connect(DB.sqlite_file)
        c = DB.conn.cursor()
        
        # Creating a new SQLite table, sqlite does not have DATE types
        logging.info('Creating tables if not exists')
        c.execute('CREATE TABLE IF NOT EXISTS user_test (username TEXT PRIMARY KEY, date_of_birth TEXT NOT NULL)')
        DB.conn.commit()

        c.execute('PRAGMA synchronous=FULL')

           
    def _close_db_connection(self):
        """Commits changes and closes the connection to a database file"""

        logging.info('Committing changes to database')
        DB.conn.commit()
        DB.conn.close()