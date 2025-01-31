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
        # print ("Got a request of: %s\n" % self.data)
        self.data = self.data.decode().strip()

        components_list = self.data.split() # This is going to split the data received into its different components which we can assess as we go.

        # Now we are going to check if the path provided is a valid path 
        request_type = components_list[0]   # We are only handling GET requests
        requested_path = components_list[1] # Since path is our second element in the list of the components
        folder = "www"         # Since as a webserver, we only want to serve files that are in our folder www

        full_path = folder + requested_path # This is the path that we will eventually go finding
 
        if request_type == 'GET':
        # We will not be handling any other request types other than GET

            # Used https://docs.python.org/3/library/exceptions.html to handle File I/O exceptions
            try:
                self.handlePath(full_path)
            
            except FileNotFoundError:
            # This exception will occur when we will try to open a file that does not exist.
                self.handle404()
            
            # Used https://www.askpython.com/python/examples/handling-error-13-permission-denied#:~:text=Error%2013%3A%20Permission%20Denied%20in%20Python%20is%20an%20I%2FO,file%2C%20or%20having%20incorrect%20permissions.
            # to handle permission denied error
            except IOError:
            # This error will occur when we will encounter path to a directory instead
                full_path += "/"
                self.handle301(full_path)
                self.handlePath(full_path)

        else:
        # This will handle the case when we encounter any other request than GET
            self.handle405()
    
    def handlePath(self, path):
    # This function will start the process of handling the path
        
        if path[-1] == '/':
        # We are going to open index.html by default if the user has entered the directory
            path += 'index.html'

        if ".." in path:
            dirs = ["www","deep"]
            idx = 0
            path_comps = path.split('/')
            for comp in path_comps:
            # This is to handle situation when client tries to access directories outside "www"
                if comp in dirs:
                # comp is either "www" or "deep", get their index
                    idx = dirs.index(comp)
                elif comp == "..":
                # comp is .., then decrement index by 1
                    idx -= 1
                elif comp not in dirs:
                # if comp is not in dirs, break the loop and it will be handled as 404 by the program
                    break

                if idx < 0:
                # if index goes below 0, it means client tried accessing directories outside "www" 
                    self.handle404()
                    return

        file = open(path, "r")
        self.handle200(file, path)

    # THESE ARE THE STATUS CODES HANDLER
    # Used https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301 for information on the status codes

    def handle200(self, file, path):
    # This function will handle 200 status code case
        content = file.read()
        result = b'HTTP/1.1 200 OK\r\n'

        mime_type = path.split('.')[-1]     # mime type
        result += f"Content-Type: text/{mime_type}\r\n\r\n".encode()
        
        result += content.encode()
        self.request.sendall(result)

    def handle301(self, path):
    # This function will handle 301 status code case
        result = b"HTTP/1.1 301 Moved Permanently\r\n\r\n"
        result += f"Location: {path}\r\n\r\n".encode()
        self.request.sendall(result)

    def handle404(self):
    # This function will handle 404 status code case
        self.request.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')

    def handle405(self):
    # This function will handle 405 status code case
        self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()