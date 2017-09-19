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
            self.ser = serial.Serial('/dev/ttyACM1', timeout=0)

        def reset(self):
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            return True

        def write(self, data):
            def bytes(s):
                return ''.join(chr(x) for x in s)
            self.ser.write(b'{}'.format(bytes(data)))
            self.ser.flush()
            return True

        def read(self):
            try:
                return [ord(x) for x in self.ser.read(2048)]
            except:
                pass
            return ''

    server.register_instance(MyFuncs())

    # Run the server's main loop
    server.serve_forever()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
