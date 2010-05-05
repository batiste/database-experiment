from http_utils import http, parse_request
import urllib2
import urllib
import socket
import cjson as json
from http_utils import http, parse_request
from documents import store_document
from routing import ClusterDistribution
import gevent

WELCOME_POOL = "Welcome to the pool."

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
        if host_address != host['address']:
            return host['index']
    raise HostNotFoundError


def migrate_clusters(my_address, host_pool):
    """Task that migrate every needed clusters from other server to
    this new one."""
    host_index = get_host_index(my_address, host_pool)
    now = ClusterDistribution(nb_active_hosts(host_pool))
    after = ClusterDistribution(nb_active_hosts(host_pool)+1)
    needed_clusters = after.clusters_for_host(host_index)
    for cluster in needed_clusters:
        host_index = now.get_host_from_cluster(cluster)
        host_address = host_pool[host_index]['address']
        req = cluster_list_request(host_address, cluster)
        data = urllib2.urlopen(req)
        index_list = json.decode(data.read())
        for index in index_list:
            req = document_request(host_address, index)
            data = urllib2.urlopen(req)
            store_document(index, data.read())

    #todo:notify other servers
    print("Migration finished successfuly")

def handle_hosts(env, response, host_pool):
    """Handle all the requests on this host"""
    
    method = env['REQUEST_METHOD']
    if method == 'GET':
        return http(response, json.encode(host_pool))
        
    # post method signify a new host as to integrated to the pool
    # or a request to join a pool of hosts
        
    # handling a new server that want to enter the pool
    if env['PATH_INFO'].startswith('/hosts/register'):
        content = parse_request(env)
        new_host_address = content.get('address', [None])[0]

        # already registered, is some server already migrating? We need to stop here.
        for host in host_pool:
            if host['address'] == new_host_address:
                return http(response, "This server is already in the pool.")
            if host['state'] == 'migrating':
                return http(response, "There is already a migrating server in the pool.")
        
        new_host = {
            'address':new_host_address,
            'index':len(host_pool),
            'state':'migrating',
        }

        # if we were alone, we are now pooling.
        for host in host_pool:
            if host['state'] == 'alone':
                host['state'] = 'pooling'
        
        # register the new host
        host_pool.append(new_host)
        return http(response, WELCOME_POOL)

    if env['PATH_INFO'].startswith('/hosts/migration_finished'):
        content = parse_request(env)
        new_host_address = content.get('address', [None])[0]

        for host in host_pool:
            if host['state'] == 'migrating':
                if host['address'] != new_host_address:
                    raise "Wrong!"
                host['state'] = 'pooling'
        
        return http(response, WELCOME_POOL)

    # handling the client that ask to join a pool
    if env['PATH_INFO'].startswith('/hosts/join'):

        if len(host_pool) > 1:
            return http(response, "Already in a pool.")

        content = parse_request(env)
        pool_address = content.get('pool_address', [None])[0]
        my_address = host_pool[0]['address']

        if pool_address == my_address:
            return http(response, "That's silly.")
        
        req = get_pool_request(pool_address)
        try:
            data = urllib2.urlopen(req)
        except urllib2.URLError, e:
            return http(response, "Cannot get pool description.")

        
        new_pool = json.decode(data.read())
        
        # empty local host_pool
        for host in range(len(host_pool)):
            host_pool.pop(0)

        for host in new_pool:
            host_pool.append(host)

        # notifiy all the other hosts that there is a new host in town
        for host in new_pool:
            # avoid deadly infinite loop
            if my_address != host['address']:
                req = register_pool_request(my_address, host['address'])
                data = urllib2.urlopen(req)
                assert(data.read() == WELCOME_POOL)

        #TODO: launch the cluster migration
        migrate_clusters(my_address, host_pool)

        # notify all the hosts that the data migration was sucessful
        for host in new_pool:
            if my_address != host['address']:
                req = migration_finished_request(my_address, host['address'])
                data = urllib2.urlopen(req)
                assert(data.read() == WELCOME_POOL)

        # request everything again
        req = get_pool_request(pool_address)
        try:
            data = urllib2.urlopen(req)
        except urllib2.URLError, e:
            return http(response, "Cannot get pool description.")


        new_pool = json.decode(data.read())

        # empty local host_pool
        for host in range(len(host_pool)):
            host_pool.pop(0)

        assert(host_pool == [])

        for host in new_pool:
            host_pool.append(host)

        return http(response, json.encode(host_pool))

    return http(response, "handle_hosts:no routes")



def register_pool_request(address, pool_address):
    register_url = 'http://' + pool_address + '/hosts/register'
    values = {'address' : address}
    data = urllib.urlencode(values)
    return urllib2.Request(register_url, data)

def join_pool_request(address, pool_address):
    register_url = 'http://' + address + '/hosts/join'
    values = {'pool_address' : pool_address}
    data = urllib.urlencode(values)
    return urllib2.Request(register_url, data)

def get_pool_request(pool_address):
    register_url = 'http://' + pool_address + '/hosts/'
    return urllib2.Request(register_url)

def migration_finished_request(address, pool_address):
    register_url = 'http://' + pool_address + '/hosts/migration_finished'
    values = {'address' : address}
    data = urllib.urlencode(values)
    return urllib2.Request(register_url, data)

def cluster_list_request(host_address, index):
    clusters_url = 'http://' + host_address + '/clusters/'
    values = {'index' : index}
    data = urllib.urlencode(values)
    return urllib2.Request(clusters_url, data)

def document_request(host_address, index):
    document_url = 'http://' + host_address + '/documents/'
    values = {'index' : index}
    data = urllib.urlencode(values)
    return urllib2.Request(document_url, data)


