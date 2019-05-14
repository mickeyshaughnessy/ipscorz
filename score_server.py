import random, json

class score_server():
    def __init__(self):
        pass

    def on_post(self, req, resp):
        path = req.relative_uri
        if path == '/score':
            resp.body = file 

    def on_post(self, req, resp):
        path = req.relative_uri
        if path == '/api':


if __name__ == "__main__":
    from wsgiref import simple_server
    import sys
    import falcon

    server = score_server() 
    app = falcon.API()
    app.add_route('/score', api_server())
    httpd = simple_server.make_server('0.0.0.0', int(sys.argv[1]), app)
    httpd.serve_forever()
