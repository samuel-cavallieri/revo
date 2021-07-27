import time, threading, logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from server import Server
from database import DB

class AsyncHTTPServer(object):
    """Asynchronous HTTP server"""
 
    def __init__(self, http_host='', http_port=8080, asyncronous=True ):
        """Initializes asynchronous HTTP server"""

        logging.info('Initializing AsyncHTTPServer')

        self.asyncronous = asyncronous
        self.my_server=Server
        self.httpd = HTTPServer((http_host, http_port), Server)

        if self.asyncronous :
            logging.info('Starting a new thread for HTTPServer')
            self._thread = threading.Thread(target=self.do_server_forever)
            self._thread.daemon = True
            self._thread.start()
        else :
            logging.info('Starting HTTPServer in single thread mode')
            self.do_server_forever()

    def do_server_forever(self):
        """Connects to a database and starts HTTP server"""

        db = DB()
        self.httpd.serve_forever()

    def stop(self, timeout):
        """Stops a HTTP server"""

        logging.info('Stopping HTTPServer')
        self.httpd.socket.close()
        if self.asyncronous :
            self._thread.join(timeout)
