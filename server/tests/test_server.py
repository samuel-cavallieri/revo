
import pytest
import sys, os, time, datetime, logging
import requests as req
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')

import settings
from server import Server
from async_server import AsyncHTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer

class TestServerClass:
    """Server unit tests

       Logging should be configured in pytest.ini, or you should run pytest -q -c pytest_logs.ini
    """

    @pytest.fixture(scope='session',autouse=True)
    def http_server(self):
        """Fixture, starts HTTP server once per session"""
        logging.info("starting httpd")
        httpd = AsyncHTTPServer(settings.http_host, settings.http_port)
        yield httpd  # provide the fixture value
        logging.info("teardown httpd")
        httpd.stop(1)

    def test_put(self):
        """Tests HTTP put request method"""

        resp = req.put("http://127.0.0.1:8080/hello/Basil", data = '{ "dateOfBirth": "2014-05-01" }', headers={'Content-type': 'application/json'})
        assert 204==resp.status_code

    # A. If username's birthday is in N days: { "message": "Hello, <username>! Your birthday is in N day(s)" } 
    # B. If username's birthday is today: { "message": "Hello, <username>! Happy birthday!" }
    def test_get(self):
        """Tests HTTP get request method"""

        resp = req.get(settings.get_base_url()+"/hello/Basil")
        assert 200==resp.status_code

        today = datetime.date.today()
        date_of_birth = datetime.datetime(2014,5,1).date()
        next_birthday = datetime.datetime(today.year+1,date_of_birth.month,date_of_birth.day).date()
        days = (next_birthday - today).days

        if days>0 :
            assert '{ "message": "Hello, Basil! Your birthday is in %s day(s)" }' % str(days) == resp.text
        else :
            assert '{ "message": "Hello, Basil! Happy birthday!" }' == resp.text


    def test_put_another_user(self):
        """Tests HTTP put request method"""

        resp = req.put("http://127.0.0.1:8080/hello/Pafnuty", data = '{ "dateOfBirth": "1964-03-17" }', headers={'Content-type': 'application/json'})
        assert 204==resp.status_code

    def test_get_another_user(self):
        """Tests HTTP get request method"""

        resp = req.get(settings.get_base_url()+"/hello/Pafnuty")
        assert 200==resp.status_code

    def test_put_user_future_date(self):
        """Tests HTTP put request method"""

        resp = req.put("http://127.0.0.1:8080/hello/Pafnuty", data = '{ "dateOfBirth": "2100-01-01" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code

    def test_put_user_with_notexisting_date(self):
        """Tests HTTP put request method 2001 is not a leap year"""

        resp = req.put("http://127.0.0.1:8080/hello/Pafnuty", data = '{ "dateOfBirth": "2001-02-29" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code

    def test_put_user_with_leap_date(self):
        """Tests HTTP put request method 2000 is a leap year"""

        resp = req.put("http://127.0.0.1:8080/hello/Pafnuty", data = '{ "dateOfBirth": "2000-02-29" }', headers={'Content-type': 'application/json'})
        assert 204==resp.status_code

    def test_put_wrong_name(self):
        """Tests sending a malformed name"""

        resp = req.put(settings.get_base_url()+"/hello/Basil2", data = '{ "dateOfBirth": "2014-05-01" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code

    def test_put_wrong_path(self):
        """Tests sending a wrong path"""

        resp = req.put(settings.get_base_url()+"/goodbye/Basil", data = '{ "dateOfBirth": "2014-05-01" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code

    def test_put_broken_json(self):
        """Tests sending a malformed json"""

        resp = req.put(settings.get_base_url()+"/hello/Basil", data = '{ dateOfBirth": "2014-05-01" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code

    def test_put_wrong_date(self):
        """Tests sending a malformed date"""

        resp = req.put(settings.get_base_url()+"/hello/Basil", data = '{ "dateOfBirth": "xxx" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code

    def test_put_wrong_date_key(self):
        """Tests sending wrong JSON key"""

        resp = req.put(settings.get_base_url()+"/hello/Basil", data = '{ "dateOfBIRTH": "2014-05-01" }', headers={'Content-type': 'application/json'})
        assert 400==resp.status_code


    def test_get_missed_user(self):
        """Tests getting missed user"""

        resp = req.get(settings.get_base_url()+"/hello/Zeliboba")
        assert 404==resp.status_code

