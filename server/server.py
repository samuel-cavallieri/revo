# Design and code a simple "Hello World" application that exposes the following HTTP-based APIs: 

# Description: Saves/updates the given user's name and date of birth in the database. 
# Request: PUT /hello/<username> { "dateOfBirth": "YYYY-MM-DD" } 
# Response: 204 No Content
 
# Note:
# <usemame> must contains only letters. 
# YYYY-MM-DD must be a date before the today date. 

# Description: Returns hello birthday message for the given user 
# Request: Get /hello/<username> 
# Response: 200 OK 

# Response Examples: 
# A. If username's birthday is in N days: { "message": "Hello, <username>! Your birthday is in N day(s)" } 
# B. If username's birthday is today: { "message": "Hello, <username>! Happy birthday!" } 

# Note: Use storage/database of your choice. The code should have at least one unit test. 

import sys, os.path, logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver, json, cgi, sqlite3, datetime
from urllib.parse import urlparse, parse_qs
import re

from .database import DB
from . import http_responses
from .http_exception import HTTPException

"""Example HTTP API server module"""
# https://stackoverflow.com/questions/18444395/basehttprequesthandler-with-custom-instance

class Server(BaseHTTPRequestHandler):
    """Simple HTTP API server"""

    def __init__(self, request, client_address, server):
        logging.info("Initializing a HTTP server")
        self.regex_username = re.compile("^/hello/([a-zA-Z]+)$")
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
    
    # Disable logging DNS lookups
    # Reverse DNS lookup may seriously slow down the server!
    def address_string(self):
        return str(self.client_address[0])

    def parse_request_path(self, path):
      """Parses a request path & validates it"""
      
      username_match = self.regex_username.search(path)
      if username_match == None :
          raise HTTPException(400, 'Path should conform /hello/<username> pattern. %s breaks this rule' % path)

      username = username_match.groups()[0]

    # fast, but less error proof code variant 
    #
    #   splitted_path = os.path.split(path)
    #   if len(splitted_path)>2 :
    #       raise Exception('Path should conform /hello/<username> pattern. %s breaks this rule' % username)

    #   username=splitted_path[1]

    #   if ''==username :
    #     raise Exception('Path should conform /hello/<username> pattern. %s breaks this rule' % username)

    #   # re.search('[a-zA-Z]', username) - less fast
    #   if not any(c.isalpha() for c in username) :
    #       raise Exception('<username> must contains only letters. %s does not conform with this rule' % username)

      return username

    def _send_response_code_and_headers(self, response_code, headers={}):
        """Returns code and sends HTTP headers"""

        short_msg, long_msg = http_responses.get_http_response_info(response_code)
        logging.debug('Returning response code %s.  %s. %s',str(response_code), short_msg, long_msg )

        self.send_response(response_code)

        for k, v in list(headers.items()):
            logging.debug('Sending header %s %s' % (k, v) )
            self.send_header(k, v)

        self.end_headers()

    def _send_response(self, code, message=''):
        """Sends headers with code and message"""
        self._send_response_code_and_headers(code, {})
        _, msg = http_responses.get_http_response_info(code)
        
        final_message = msg + '\n' + message
        self.wfile.write(final_message.encode())

    def _send_501_response(self, message=''):
        """Sends 501 error"""
        self._send_response(501, message)

    def _send_http_exception_response(self, ex):
        """Sends headers with code and message from HTTPException"""
        self._send_response(ex.code, ex.message)

    def do_HEAD(self):
        """Handles HEAD request"""
        logging.debug("Received HEAD request")
        self._set_headers()
        
    def get_greetings(self, username, days):
        """Returns greetings"""

        if days>0 :
            return '{ "message": "Hello, %s! Your birthday is in %s day(s)" }' % (username, str(days))
        else :
            return '{ "message": "Hello, %s! Happy birthday!" }' % username


    # Description: Returns hello birthday message for the given user 
    # Request: Get /hello/<username> 
    # Response: 200 OK 
    # Response Examples: 
    # A. If username's birthday is in N days: { "message": "Hello, <username>! Your birthday is in N day(s)" } 
    # B. If username's birthday is today: { "message": "Hello, <username>! Happy birthday!" }
    def do_GET(self):
        """Handles GET request"""

        try:
            # parse a request path & validate
            logging.debug("Received GET request %s", self.path)
            username = self.parse_request_path(self.path)

            c = DB.conn.cursor()

            # Read a user info
            query = """SELECT date_of_birth 
            FROM user_test 
            WHERE username = '%s' 
            """ % username

            cursor = c.execute(query)

            row = cursor.fetchone()

            if None == row :
                raise HTTPException(404, 'No username %s found in database.' % username)
            
            today = datetime.date.today()
            date_of_birth = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
            next_birthday = datetime.datetime(today.year+1,date_of_birth.month,date_of_birth.day).date()
            days = (next_birthday - today).days

            response = self.get_greetings(username, days)

            self._send_response_code_and_headers(200, {'Content-type': 'application/json'})
            self.wfile.write(response.encode())

        except HTTPException as e:
            logging.error(e.code_description_and_message)
            self._send_http_exception_response(e)
        except Exception as e:
            logging.error("Error: {0}".format(str(e.args[0])))
            self._send_501_response("Error {0}".format(str(e.args[0])))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            self._send_501_response()
            

    # Description: Saves/updates the given user's name and date of birth in the database. 
    # Request: PUT /hello/<username> { "dateOfBirth": "YYYY-MM-DD" } 
    # Response: 204 No Content
    # Note:
    # <usemame> must contains only letters. 
    # YYYY-MM-DD must be a date before the today date. 
    # https://github.com/enthought/Python-2.7.3/blob/master/Lib/BaseHTTPServer.py
    def do_PUT(self):
        """Handles PUT request"""
        logging.debug("Received PUT request")

        try:
            # read the message and convert it into a python dictionary
            length = int(self.headers['content-length'])

            raw_message = self.rfile.read(length)
            message = json.loads(raw_message)

            # parse a request path & validate
            username  = self.parse_request_path(self.path)

            if 'dateOfBirth' not in list(message.keys()):
               raise HTTPException(400, 'dateOfBirth not found.')

            try:
                datetime_of_birth = datetime.datetime.strptime(message["dateOfBirth"], '%Y-%m-%d')
                date_of_birth = datetime_of_birth.date()
            except ValueError as e:
                raise HTTPException(400, '%s must be a valid YYYY-MM_DD date.' % message["dateOfBirth"])

            if datetime.date.today() <= date_of_birth :
                raise HTTPException(400, '%s must be a date before the today date.' % date_of_birth.strftime('%Y-%m-%d'))

            c = DB.conn.cursor()

            # Upsert a user
            query = """INSERT OR REPLACE INTO user_test (username, date_of_birth) 
            VALUES ('%s', '%s')
            """ % (username,date_of_birth.strftime('%Y-%m-%d'))

            logging.info("Upsert a user with query %s" % query)

            try:
                c.execute(query)
                DB.conn.commit()
            except sqlite3.Error as e:
                logging.error("An error occurred:", e.args[0])
                self._send_501_response()

            self._send_response_code_and_headers(204)

        except json.JSONDecodeError as e:
            logging.error(e.msg)
            self._send_response(400,e.msg)
        except HTTPException as e:
            logging.error(e.code_description_and_message)
            self._send_http_exception_response(e)
        except Exception as e:
            logging.error("Error: {0}".format(str(e.args[0])))
            self._send_501_response("Error {0}".format(str(e.args[0])))
        except:
            logging.error("Unexpected error:", sys.exc_info()[0])
            self._send_501_response()