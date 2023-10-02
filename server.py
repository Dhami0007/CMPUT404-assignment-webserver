#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.data = self.data.decode().strip()

        components_list = self.data.split() # This is going to split the data received into its different components which we can assess as we go.

        # Now we are going to check if the path provided is a valid path 
        request_type = components_list[0]   # We are only handling GET requests
        requested_path = components_list[1] # Since path is our second element in the list of the components
        folder = "www"         # Since as a webserver, we only want to serve files that are in our folder www

        full_path = folder + requested_path # This is the path that we will eventually go finding

        # Now we are going to check the following parts of the request as per the requirements:
        # 1. If the request method is GET or not
        # 2. If the request has requested a valid path
        # 3. If we have the requested file or not
 
        if request_type == 'GET':
        # We will not be handling any other request types other than GET
        
            try:
                self.handlePath(full_path)
            
            except FileNotFoundError:
                self.handle404()
            
            except IOError:
                full_path += "/"
                self.handle301(full_path)
                self.handlePath(full_path)

        else:
            self.handle405()
    
    def handlePath(self, path):
    # This function will start the process of handling the path and will call other functions to deliver status codes
        
        if path[-1] == '/':
        # We are going to open index.html by default if the user has entered the directory
            path += 'index.html'

        print(f'The full path is {path}')
        file = open(path, "r")
        self.handle200(file, path)

    # THESE ARE THE STATUS CODES HANDLER

    def handle200(self, file, path):
    # This function will handle 200 status code case
        print("Handling 200")

        content = file.read()
        result = b'HTTP/1.1 200 OK\r\n'

        if ".html" in path[-5:len(path)]:
            result += b"Content-Type: text/html\r\n\r\n"

        elif ".css" in path[-5:len(path)]:
            result += b"Content-Type: text/css\r\n\r\n"

        print(f"Header sent:\n{result.decode()}")

        result += content.encode()
        self.request.sendall(result)
        print("-----------------------------------------------")

    def handle301(self, path):
    # This function will handle 301 status code case
        print("Handling 301")
        result = b"HTTP/1.1 301 Moved Permanently\r\n\r\n"
        result += f"Location: {path}\r\n\r\n".encode()
        self.request.sendall(result)

    def handle404(self):
    # This function will handle 404 status code case
        print("Handling 404")
        self.request.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
        print("-----------------------------------------------")

    def handle405(self):
    # This function will handle 405 status code case
        print("Handling 405")
        self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
        print("-----------------------------------------------")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()