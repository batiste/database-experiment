import cjson as json
import os
import md5
import urllib
from http_utils import http, parse_request

def handle_documents(env, response, distribution):
    # get the content
    content = parse_request(env)
    index = content.get('index', [None])[0]
    document = content.get('document', [None])[0]

    if index:
        # take the 2 first hexa value to determine
        # in which cluster the data should be.
        # It works with 256 cluster only
        dec_index = int(index[0:2], 16)
        target_host = distribution.get_host_from_cluster(dec_index)
        if target_host != distribution.current_host:
            return http(response,
                'This document is not on this host but on host (%s)' % target_host)

    method = env['REQUEST_METHOD']

    if method == 'GET' and not index:
        return http(response,
            'Must provide  index (%s)' % index)
    if method == 'POST' and not document:
        return http(response, 'Must provide json document.')

    if method == 'POST':
        if not index:
            index = create_index(document)
        try:
            store_document(index, document)
        except json.DecodeError:
            return http(response, 'Json is invalid.<br>'+document)
        return http(response, index)

    if method == 'GET':
        try:
            document = read_document(index)
        except IOError:
            return http(response, "Document not found.", code=404)
        return http(response, document)


def store_document(index, document):
    # to check the validity of the document
    json.encode(json.decode(document))
    fh = open(os.path.join('data', index), "wb")
    # simple os lock system
    #fcntl.lockf(fh, fcntl.LOCK_EX)
    fh.write(document)
    fh.close()
    #fcntl.lockf(fh, fcntl.LOCK_UN)

def read_document(index):
    fh = open(os.path.join('data', index), "rb")
    doc = fh.read()
    fh.close()
    return doc

def create_index(document):
    m = md5.new()
    m.update(document)
    return m.hexdigest()
