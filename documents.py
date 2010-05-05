import cjson as json
import os
import hashlib
import urllib
from http_utils import http, parse_request

CHECK_VALID_JSON_DOCUMENT = True

def init_cluster_directories(storage, distribution):
    path = os.path.join(storage)
    if not os.path.exists(path):
        os.mkdir(path)
    for cluster in range(distribution.nb_clusters):
        path = os.path.join(storage, str(cluster))
        if not os.path.exists(path):
            os.mkdir(path)

def list_cluster(storage, cluster_index):
    return os.listdir(os.path.join(storage, str(cluster_index)))

def handle_clusters(env, response, distribution, storage):
    content = parse_request(env)
    index = content.get('index', [None])[0]
    return http(response, json.encode(list_cluster(storage, index)))
    

def handle_documents(env, response, distribution, storage):
    # get the content
    content = parse_request(env)
    index = content.get('index', [None])[0]
    document = content.get('document', [None])[0]

    if index:
        # take the 2 first hexa value to determine
        # in which cluster the data should be.
        # It works with 256 cluster only
        cluster_index = int(index[0:2], 16)
        target_host = distribution.get_host_from_cluster(cluster_index)
        if target_host != distribution.current_host:
            return http(response,
                "This document is not on this host but on host (%s)" % target_host)

    method = env['REQUEST_METHOD']

    if method == 'GET':
        if not index:
            return http(response, "Must provide  index (%s)" % index, code=404)

        try:
            document = read_document(storage, index)
        except IOError:
            return http(response, "Document not found.", code=404)
        return http(response, document)

    if method == 'POST':
        if not document:
            return http(response, "Must provide a json document.")
            
        if not index:
            index = create_index(document)
        try:
            store_document(storage, index, document)
        except json.DecodeError:
            return http(response, "Json is invalid.")
        return http(response, index)

    return http(response, "handle_documents:no routes")


def store_document(storage, index, document):
    cluster_index = str(int(index[0:2], 16))
    # to check the validity of the document on write
    if CHECK_VALID_JSON_DOCUMENT:
        json.decode(document)
    fh = open(os.path.join(storage, cluster_index, index), "wb")
    # simple os lock system
    #fcntl.lockf(fh, fcntl.LOCK_EX)
    fh.write(document)
    fh.close()
    #fcntl.lockf(fh, fcntl.LOCK_UN)

def read_document(storage, index):
    cluster_index = str(int(index[0:2], 16))
    fh = open(os.path.join(storage, cluster_index, index), "rb")
    doc = fh.read()
    fh.close()
    return doc

def create_index(document):
    m = hashlib.md5()
    m.update(document)
    return m.hexdigest()
