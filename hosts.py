from http_utils import http, parse_request
import urllib2
import urllib

import cjson as json
from http_utils import http, parse_request

def host_id(hostname, port):
    return hostname + ':' + str(port)

def handle_hosts(env, response, host_pool):
    method = env['REQUEST_METHOD']
    if method == 'GET':
        return http(response, str(host_pool))
        
    # post method signify a new host as to integrated to the pool
    # or a request to join a pool of hosts
        
    # handling a new server that want to register
    if env['PATH_INFO'].startswith('/hosts/register'):
        content = parse_request(env)
        new_host_address = content.get('address', [None])[0]
        new_host = {'address':new_host_address, 'index':len(host_pool)}
        # already registred?
        for host in host_pool:
            if host['address'] == new_host_address:
                return http(response, json.encode(host_pool))

        # register the new host
        host_pool.append(new_host)
        return http(response, json.encode(host_pool))

    # handling the client that ask to join a pool
    if env['PATH_INFO'].startswith('/hosts/join'):

        if len(host_pool) > 1:
            return http(response, "<h1>Already in a pool</h1>")

        content = parse_request(env)
        pool_address = content.get('pool_address', [None])[0]
        my_address = host_pool[0]['address']
        req = join_pool_request(my_address, pool_address)
        try:
            data = urllib2.urlopen(req)
        except urllib2.URLError, e:
            return http(response, "Join pool failed on %s %d %s %s" %
                (register_url, e.code, e.msg, e.message))
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
            
        return http(response, json.encode(host_pool))

    return http(response, "Hu?")

def join_pool_request(address, pool_address):
    register_url = 'http://' + pool_address + '/hosts/register'
    values = {'address' : address}
    data = urllib.urlencode(values)
    return urllib2.Request(register_url, data)