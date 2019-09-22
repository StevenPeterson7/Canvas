#!/usr/bin/env python 

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from io import BytesIO


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        f=open("index.html","r")
        self.end_headers()
        for i in f.read():
            self.wfile.write(i.encode())
        f.close()

    def do_POST(self):
        
        if(self.path == "/assignments"):
            os.popen(".\generateList.py")
            os.popen(".\Canvas2ics.py")
        if(self.path == "/email"):
            os.popen(".\sendEmail.py")
            
            
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)

        
        self.wfile.write("""<body onload="window.location.href = 'http://127.0.0.1:8080/'"></body>""".encode())
        
        #self.wfile.write(response.getvalue())

os.remove("index.html")
os.popen('copy ~index.html index.html')
httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
print("server up")
httpd.serve_forever()