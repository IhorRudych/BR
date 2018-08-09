#! /usr/bin/env python

'''
'''

import serial
import argparse
import logging
import os
import socket
import zeroconf

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
    parser.add_argument("-H", "--host", default="", help="interface to serve rpc from")
    parser.add_argument("-p", "--port", default=8000, help="increase output verbosity")
    args = parser.parse_args()

    logger = logging.getLogger('xmlrpc')
    logger.setLevel(logging.ERROR)

    # create a file handler
    handler = logging.FileHandler('xmlrpc.log')
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    # Create server
    server = SimpleXMLRPCServer((args.host, args.port), requestHandler=RequestHandler)
    server.register_introspection_functions()

    class MyListener(object):

        def __init__(self):
            self.directory = {}

        def remove_service(self, zeroconf, type, name):
            if name in self.directory:
                print("Service %s removed" % (name,))
                del self.directory[name]

        def add_service(self, zeroconf, type, name):
            if 'axcend.bridge' in name:
                info = zeroconf.get_service_info(type, name)
                address = "{}".format(socket.inet_ntoa(info.address))
                print("Service %s added (%s)" % (name, address))
                self.directory[name] = {
                    'addr': address,
                    'port': info.port
                }

    zero = zeroconf.Zeroconf()
    listener = MyListener()
    browser = zeroconf.ServiceBrowser(zero, '_http._tcp.local.', listener)

    class MyFuncs:
        def __init__(self):
            self.ser = None
            path = '/dev/ttyACM.axcend'
            if os.path.exists(path):
                self.ser = serial.Serial(path, timeout=0, write_timeout=0)
            if self.ser is None:
                raise Exception('unable to locate /dev/ttyACM*')
            self.logger = logging.getLogger('xmlrpc')

        def reset(self):
            self.logger.info('RESET')
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            return True

        def echo(self, data):
            return data

        def list(self):
            results = []
            for name in listener.directory:
                item = {
		    'name': name,
                    'addr': listener.directory[name]['addr'],
                    'port': listener.directory[name]['port']
                }
                results.append(item)
            return results

        def write(self, data):
            def bytes(s):
                return ''.join(chr(x) for x in s)
            self.logger.info('WRITE {}'.format(data))
            retries = 2
            while retries:
                try:
                    self.ser.write(b'{}'.format(bytes(data)))
                    self.ser.flush()
                except:
                    self.logger.info('WRITE failure')
                    if self.ser is not None:
                        self.ser.close()
                    self.__init__()
                else:
                    break
                finally:
                    retries -= 1
            return True

        def read(self):
            retries = 2
            while retries:
                try:
                    data = [ord(x) for x in self.ser.read(2048)]
                    self.logger.info('READ {}'.format(data))
                except:
                    self.logger.info('READ failure')
                    if self.ser is not None:
                        self.ser.close()
                    self.__init__()
                else:
                    return data
                finally:
                    retries -= 1
            return []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.ser.close()

    with MyFuncs() as myfuncs:
        try:
            server.register_instance(myfuncs)
        except serial.serialutil.SerialException, e:
            print(e)
            return -1

        # Run the server's main loop
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
            zeroconf.close()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
