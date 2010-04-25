from cgi import parse_qs, escape

def http(response, content, code=200):
    if code == 200:
        response('200 OK', [('Content-Type', 'text/html')])
    if code == 404:
        response('404 Not Found', [('Content-Type', 'text/html')])
    return [content]

def parse_request(environ):
    # if we have a query string, we don't bother reading the content
    if environ['QUERY_STRING']:
        return parse_qs(environ['QUERY_STRING'])
    
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the query string will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)
    return parse_qs(request_body)
    

