#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # Returns the response code from the status line
    def get_code(self, data):
        status_line = data.split("\r\n")[0]
        response_code = status_line.split(' ')[1]
        return int(response_code)

    def get_headers(self, data):
        # headers = data.split("\r\n\r\n")[0]
        return None

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        parsed_url = urlparse(url)
        path, hostname, port = parsed_url.path, parsed_url.hostname, parsed_url.port

        if port == None:
            port = 80
        if path == "":
            path = "/"

        # print("path = {}, host = {}, port = {}".format(path, hostname, port))

        return path, hostname, port

    def GET(self, url, args=None):
        code = 500
        body = ""

        # Parsing url passed
        path, host_name, port = self.parse_url(url)

        # Connecting socket
        self.connect(host_name, port)

        self.sendall(
            "GET {} HTTP/1.1\r\nHost: {}\r\nAccept: /*/\r\nConnection: close\r\n\r\n".format(path, host_name))

        socket_data = self.recvall(self.socket)

        code = self.get_code(socket_data)
        body = self.get_body(socket_data)
        # print(body)

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # Parsing url passed
        path, host_name, port = self.parse_url(url)

        # Connecting socket
        self.connect(host_name, port)

        if args == None:
            args = ''
        else:
            args = urlencode(args)

        response = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: /*/\r\nContent-Length: {}\r\nConnection: close\r\n\r\n".format(
            path, host_name, len(args)) + str(args)
        self.sendall(response)

        socket_data = self.recvall(self.socket)

        code = self.get_code(socket_data)
        body = self.get_body(socket_data)

        # print(body)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
