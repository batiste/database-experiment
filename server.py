#!/usr/bin/python
"""HTTP server example.

Uses libevent API directly and thus may be dangerous.
WSGI interface is a safer choice, see examples/wsgiserver.py.
"""
from gevent import wsgi
from documents import handle_documents
from hosts import handle_hosts, host_id
from http_utils import http, parse_request
from routing import ClusterDistribution
import os
import socket
fh = open('welcome.html', 'r')
welcome = fh.read()
fh.close()

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="config file path", metavar="CONFIG")
parser.add_option("-p", "--port", dest="port", default=8088, type="int",
                  help="port of the server", metavar="PORT")
parser.add_option("-d", "--directory", dest="directory", default='data',
                  help="directory where to save the documents")
(options, args) = parser.parse_args()

host = {'address':host_id(socket.gethostbyname(socket.gethostname()),
    options.port), 'index':0}
host_pool = [host]
distribution = ClusterDistribution(1)

def new_distribution():
    # create a new cluster_distribution
    distribution = ClusterDistribution(len(host_pool))

def app(env, response):

    if env['PATH_INFO'] == '/':
        homepage = '<br><br>'.join(
            [welcome,
            'Cluster distribution', str(distribution.distribution),
            'Host pool', str(host_pool)]
        )
        return http(response, homepage)

    if env['PATH_INFO'].startswith('/documents/'):
        return handle_documents(env, response, distribution)

    if env['PATH_INFO'].startswith('/hosts/'):
        hosts_reponse = handle_hosts(env, response, host_pool)
        new_distribution()
        return hosts_reponse

    return http(response, "Hu?")
    
print 'Serving on %d...' % options.port
wsgi.WSGIServer(('', options.port), app).serve_forever()

