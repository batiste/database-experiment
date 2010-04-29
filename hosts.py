from http_utils import http, parse_request
import urllib2
import urllib
import socket
import cjson as json
from http_utils import http, parse_request

class HostNotFoundError(Exception):
    """Host not found"""
    pass

def host_address(port):
    return socket.gethostbyname(socket.gethostname()) + ':' + str(port)

def nb_active_hosts(host_pool):
    """The number of active host in the pool."""
    nb = 0
    for host in host_pool:
        if host['state'] == 'pooling' or host['state'] == 'alone':
            nb += 1
    return nb

def get_host_index(host_address, host_pool):
    """The numeric index of the host in the pool."""
    for host in host_pool:
        if my_address != host['address']:
            return host['index']
    raise HostNotFoundError


def migrate_clusters(my_address, host_pool):
    """Task that migrate every cluster from other server to
    this new one."""
    host_index = get_host_index(my_address)
    before = ClusterDistribution(nb_active_hosts(host_pool))
    now = ClusterDistribution(nb_active_hosts(host_pool)+1)
    needed_clusters = after.clusters_for_host(host_index)
    for cluster in needed_clusters:
        host = now.get_host_from_cluster(cluster)
        #TODO: get the cluster

def handle_hosts(env, response, host_pool):
    """Handle all the requests on this host"""
    
    method = env['REQUEST_METHOD']
    if method == 'GET':
        return http(response, str(host_pool))
        
    # post method signify a new host as to integrated to the pool
    # or a request to join a pool of hosts
        
    # handling a new server that want to register
    if env['PATH_INFO'].startswith('/hosts/register'):
        content = parse_request(env)
        new_host_address = content.get('address', [None])[0]

        # already registered, there is some already replicating? We need to stop here
        for host in host_pool:
            if host['address'] == new_host_address:
                return http(response, "This server is already in the pool.")
            if host['state'] == 'replicating':
                return http(response, "There is already a replicating server in the pool.")
        
        new_host = {
            'address':new_host_address,
            'index':len(host_pool),
            'state':'replicating',
        }

        for host in host_pool:
            if host['state'] == 'alone':
                host['state'] = 'pooling'
        
        # register the new host
        host_pool.append(new_host)
        return http(response, json.encode(host_pool))

    # handling the client that ask to join a pool
    if env['PATH_INFO'].startswith('/hosts/join'):

        if len(host_pool) > 1:
            return http(response, "Already in a pool.")

        content = parse_request(env)
        pool_address = content.get('pool_address', [None])[0]
        my_address = host_pool[0]['address']
        req = join_pool_request(my_address, pool_address)
        try:
            data = urllib2.urlopen(req)
        except urllib2.URLError, e:
            return http(response, "Join pool failed on %s %s" %
                (pool_address, e.message))
        pool = data.read()
        new_host_pool = json.decode(pool)
        for host in host_pool:
            host_pool.remove(host)
        for host in new_host_pool:
            host_pool.append(host)
            # notifiy all the other hosts that there is a new host in town
            # avoid deadly infinite loop
            if my_address != host['address']:
                req = join_pool_request(my_address, host['address'])
                data = urllib2.urlopen(req)

        #TODO: launch the cluster migration
            
        return http(response, json.encode(host_pool))

    return http(response, "Hu?")



def join_pool_request(address, pool_address):
    register_url = 'http://' + pool_address + '/hosts/register'
    values = {'address' : address}
    data = urllib.urlencode(values)
    return urllib2.Request(register_url, data)