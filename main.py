#! /usr/bin/env python

'''
'''

import serial

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")        
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleXMLRPCRequestHandler.end_headers(self)

def main(args):

    # Create server
    server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler)
    server.register_introspection_functions()

    class MyFuncs:
        def __init__(self):
            self.ser = serial.Serial('/dev/ttyACM1', timeout=1)

        def write(self, cmd):
            print(cmd)
            self.ser.write(b'{}\r\n'.format(cmd))
            self.ser.flush()
            return self.ser.read(255)

    server.register_instance(MyFuncs())

    # Run the server's main loop
    server.serve_forever()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
