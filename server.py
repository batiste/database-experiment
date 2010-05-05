#!/usr/bin/python
"""HTTP server example.

Uses libevent API directly and thus may be dangerous.
WSGI interface is a safer choice, see examples/wsgiserver.py.
"""
from gevent import wsgi
from documents import handle_documents, init_cluster_directories, handle_clusters
from hosts import handle_hosts, host_address, nb_active_hosts
from http_utils import http, parse_request
from routing import ClusterDistribution
import os

fh = open('welcome.html', 'r')
welcome = fh.read()
fh.close()

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="config file path", metavar="CONFIG")
parser.add_option("-p", "--port", dest="port", default=8080, type="int",
                  help="port of the server.", metavar="PORT")
parser.add_option("-d", "--cluster-distribution", dest="distribution", type="int", default=256,
                  help="amount of clusters wanted in the distribution.")
(options, args) = parser.parse_args()

host = {'address':host_address(options.port), 'index':0, 'state':'alone'}
host_pool = [host]
distribution = ClusterDistribution(1)
init_cluster_directories(distribution)

def new_distribution():
    # create a new cluster_distribution, distribution is according to
    # the number of active hosts
    distribution = ClusterDistribution(
        nb_active_hosts(host_pool),
        nb_clusters=options.distribution
    )

def app(env, response):

    if env['PATH_INFO'].startswith('/documents'):
        return handle_documents(env, response, distribution)

    if env['PATH_INFO'] == '/':
        homepage = '<br><br>'.join(
            [welcome,
            'Cluster distribution', str(distribution.distribution),
            'Host pool', str(host_pool)]
        )
        return http(response, homepage)

    if env['PATH_INFO'].startswith('/clusters'):
        return handle_clusters(env, response, distribution)

    if env['PATH_INFO'].startswith('/hosts'):
        hosts_reponse = handle_hosts(env, response, host_pool)
        new_distribution()
        return hosts_reponse

    return http(response, "app:no routes")
    
print 'Serving on %d...' % options.port
wsgi.WSGIServer(('', options.port), app).serve_forever()

