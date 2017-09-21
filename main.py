#! /usr/bin/env python

'''
'''

import serial
import argparse
import logging

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler, object):
    rpc_paths = ('/RPC2',)

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('xmlrpc')
        super(RequestHandler, self).__init__(request, client_address, server)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")        
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleXMLRPCRequestHandler.end_headers(self)

    def log_message(self, format, *args):
        s = '{} - {}'.format(self.client_address[0], format % args)
        self.logger.info(s)

def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8000, help="increase output verbosity")
    args = parser.parse_args()

    logger = logging.getLogger('xmlrpc')
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler('xmlrpc.log')
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    # Create server
    server = SimpleXMLRPCServer(("localhost", args.port), requestHandler=RequestHandler)
    server.register_introspection_functions()

    class MyFuncs:
        def __init__(self):
            self.ser = serial.Serial('/dev/ttyACM1', timeout=0)
            self.logger = logging.getLogger('xmlrpc')

        def reset(self):
            self.logger.info('RESET')
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            return True

        def write(self, data):
            def bytes(s):
                return ''.join(chr(x) for x in s)
            self.logger.info('WRITE {}'.format(data))
            self.ser.write(b'{}'.format(bytes(data)))
            self.ser.flush()
            return True

        def read(self):
            try:
                data = [ord(x) for x in self.ser.read(2048)]
                self.logger.info('READ {}'.format(data))
                return data
            except:
                pass
            return []

    server.register_instance(MyFuncs())

    # Run the server's main loop
    server.serve_forever()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
