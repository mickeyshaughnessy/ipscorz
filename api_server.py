import random, json

class api_server():
    def __init__(self):
        pass

    def on_get(self, req, resp):
        path = req.relative_uri
        if path == '/download':
            filename = 'ipscores.tgz'
            resp.status = falcon.HTTP_200
            resp.content_type = 'application/gzip'
            with open(filename, 'r') as f:
                resp.body = f.read()

        elif path == '/refresh':
            resp.body = json.dumps({"message" : "thanks"})
        elif path == '/configure':
            resp.body = json.dumps({"message" : "thanks"})

    def on_post(self, req, resp):
        path = req.relative_uri
        if path == '/api':
            pass
            # do the call to the locally running score server and return the result


if __name__ == "__main__":
    from wsgiref import simple_server

    server = api_server() 
    app = falcon.API()
    app.add_route('/download', api_server())
    app.add_route('/refresh', api_server())
    app.add_route('/configure', api_server())
    app.add_route('/api', api_server())
    httpd = simple_server.make_server('0.0.0.0', 8571, app)
    httpd.serve_forever()
