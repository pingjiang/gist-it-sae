import sys
import os
import urlparse
import tornado.web
from tornado.log import app_log
# from tornado.httpclient import AsyncHTTPClient


_LOCAL_ = not os.environ.has_key('SERVER_SOFTWARE')
_DEBUG_ = False or _LOCAL_
_CACHE_ = False

settings = {
    "debug": _DEBUG_,
}

sys.path.append( 'gist_it' )

import jinja2 as jinja2_
jinja2 = jinja2_.Environment( loader = jinja2_.FileSystemLoader( 'jinja2-assets' ) )

from gist_it import saecloud as gist_it_appengine
gist_it_appengine.jinja2 = jinja2

class RequestHandler( tornado.web.RequestHandler ):

    # called from gist_it.saecloud and views
    def url_for( self, *arguments ):
        parse = urlparse.urlparse( self.request.uri )
        path = ''
        if len( arguments ):
            path = posixpath.join( *arguments )
        return str( urlparse.urlunparse( ( parse.scheme, parse.netloc, path, '', '', '' ) ) )

    def get_param(self, key):
        return self.get_argument(key, None)
        
    def render_template( self, template_name, **arguments ):
        self.write( jinja2.get_template( template_name ).render( dispatch=self, **arguments ) )

class dispatch_index( RequestHandler ):
    def get( self ):
        self.render_template( 'index.jinja.html' )

class dispatch_test( RequestHandler ):
    def get( self ):
        return gist_it_appengine.dispatch_test( self )

class dispatch_test0( RequestHandler ):
    def get( self ):
        return gist_it_appengine.dispatch_test0( self )

class dispatch_gist_it( RequestHandler ):
    def get( self, location ):
        # app_log.error('gist_it: ' + location)
        return gist_it_appengine.dispatch_gist_it( self, location )

# application should be an instance of `tornado.web.Application`,
# and don't wrap it with `sae.create_wsgi_app`
application = tornado.web.Application([
    ( r'/', dispatch_index ),
    ( r'/assets/(.*)', tornado.web.StaticFileHandler, {'path':"L:/"}),
    ( r'/test', dispatch_test ),
    ( r'/test0', dispatch_test0 ),
    ( r'/xyzzy/(.*)', dispatch_gist_it ),
    ( r'(.*)', dispatch_gist_it ),
], **settings)

