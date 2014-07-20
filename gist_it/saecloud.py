#!/usr/bin/python
import logging
import os
import cgi
import sys
import urllib
from urlparse import urlparse
import httplib
from tornado.log import app_log

jinja2 = None

_LOCAL_ = not os.environ.has_key('SERVER_SOFTWARE')
_DEBUG_ = True
_CACHE_ = False

import pylibmc

memcache = pylibmc.Client()

import gist_it
from gist_it import take_slice, cgi_escape

class FetchResponse(object):
    """docstring for FetchResponse"""
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        
def fetch(url, headers = {}):
    url_parts = urlparse(url)
    if url_parts.scheme == 'https':
        ConnectionClass = httplib.HTTPSConnection
    else:
        ConnectionClass = httplib.HTTPConnection
    connection = ConnectionClass(url_parts.netloc)
    connection.request('GET', url_parts.path, '', headers)
    response = connection.getresponse()
    if response.status in (301, 302):
        redirect_url = response.getheader('location')
        connection.close()
        return fetch(redirect_url, headers)
        
    data = response.read()
    connection.close()
    return FetchResponse(response.status, data)

def render_gist_html( base, gist, document ):
    if jinja2 is None:
        return
    result = jinja2.get_template( 'gist.jinja.html' ).render( cgi_escape = cgi_escape, base = base, gist = gist, document = document )
    return result

def render_gist_js( base, gist, gist_html  ):
    if jinja2 is None:
        return
    result = jinja2.get_template( 'gist.jinja.js' ).render( base = base, gist = gist, gist_html = gist_html )
    return result

def render_gist_js_callback( callback, gist, gist_html  ):
    return "%s( '%s', '%s' );" % ( callback, gist_html.encode( 'string_escape' ), gist.raw_path )

# dispatch == RequestHandler
def dispatch_test( dispatch ):
    dispatch.render_template( 'test.jinja.html', list =
        map( lambda _: ( _, 'github/robertkrimen/gist-it-example/raw/master/test.js?' + _ ), [
        # Standard
        ''
        # Without footer
        'footer=0',
        # Footer without "brought to you by" mention
        'footer=minimal',
        # Partial file
        'slice=3:10',
        # First line of file
        'slice=0',
        # Last line of file
        'slice=-1',
        # With no style request
        'style=0',
        # Documentation
        'slice=24:100',
        'slice=0:-2',
        'slice=0',
        ] )
    )

# dispatch == RequestHandler
def dispatch_test0( dispatch ):
    dispatch.render_template( 'test.jinja.html', list = [
        ( '', 'github/whittle/node-coffee-heroku-tutorial/raw/eb587185509ec8c2e728067d49f4ac2d5a67ec09/app.js' ),
        ( '', 'github/horstjens/ThePythonGameBook/blob/master/pygame/015_more_sprites.py' ),
        ]
    )

# dispatch == RequestHandler
def dispatch_gist_it( dispatch, location ):
    location = urllib.unquote( location )
    match = gist_it.Gist.match( location )
    dispatch.set_header('Content-Type', 'text/plain'); 
    if not match:
        dispatch.set_status( 404 )
        dispatch.write( 'Not Found' )
        dispatch.write( "\n" )
        return

    else:
        slice_option = dispatch.get_param( 'slice' )
        footer_option = dispatch.get_param( 'footer' )
        style_option = dispatch.get_param( 'style' )
        highlight_option = dispatch.get_param( 'highlight' )
        test = dispatch.get_param( 'test' )

        gist = gist_it.Gist.parse( location, slice_option = slice_option, footer_option = footer_option, style_option = style_option, highlight_option = highlight_option )
        if not gist:
            dispatch.set_status( 500 )
            dispatch.write( "Unable to parse \"%s\": Not a valid repository path?" % ( location ) )
            dispatch.write( "\n" )
            return
            
        if _CACHE_ and dispatch.get_param( 'flush' ):
            dispatch.write( memcache.delete( memcache_key ) )
            return

        memcache_key = gist.raw_url.encode('UTF-8')
        data = memcache.get( memcache_key )
        if data is None or not _CACHE_:
            base = dispatch.url_for()
            # For below, see: http://stackoverflow.com/questions/2826238/does-google-appengine-cache-external-requests
            response = fetch( gist.raw_url, headers = { 'Cache-Control': 'max-age=300' } )
            if response.status_code != 200:
                if response.status_code == 403:
                    dispatch.set_status( response.status_code )
                elif response.status_code == 404:
                    dispatch.set_status( response.status_code )
                else:
                    dispatch.set_status( 500 )
                dispatch.write( "Unable to fetch \"%s\": (%i)" % ( gist.raw_url, response.status_code ) )
                return
            else:
                # I believe GitHub always returns a utf-8 encoding, so this should be safe
                response_content = response.content.decode('utf-8')

                gist_content = take_slice( response_content, gist.start_line, gist.end_line )
                gist_html = str( render_gist_html( base, gist, gist_content ) ).strip()
                callback = dispatch.get_param( 'callback' );
                if callback != None and callback != '':
                    result = render_gist_js_callback( callback, gist, gist_html )
                else:
                    result = render_gist_js( base, gist, gist_html )
                result = str( result ).strip()
                data = result
                if test:
                    if test == 'json':
                        dispatch.set_header('Content-Type', 'application/json');
                        # "{ 'gist': '%s', 'content': '%s', 'html': '%s' }"%(gist.value(), gist_content, gist_html)
                        dispatch.write("{ 'gist': '%s', 'content': '%s', 'html': '%s' }"%(gist.value(), gist_content, gist_html))
                    elif False and test == 'example':
                        pass
                    else:
                        dispatch.set_header('Content-Type', 'text/plain' )
                        dispatch.write( gist_html )
                    return
                if _CACHE_:
                    memcache.add( memcache_key, data, 60 * 60 * 24 )

        dispatch.set_header('Content-Type', 'text/javascript')
        dispatch.write( data.decode('UTF-8') )
