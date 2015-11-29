#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.00'

'''
Python client SDK for 
sina weibo ,
qzone connect,
douban 
API using OAuth 2.
authored by 
'''

import json
import time
import urllib
import urllib2
import logging
from urllib2 import HTTPError

def _obj_hook(pairs):
    '''
    convert json object to python object.
    '''
    o = JsonObject()
    for k, v in pairs.iteritems():
        o[str(k)] = v
    return o

class APIError(StandardError):
    '''
    raise APIError if got failed json message.
    '''
    def __init__(self, error_code, error, request, api_type = 'weibo'):
        self.error_code = error_code
        self.error = error
        self.request = request
        self.api_type = api_type
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s,api_type:%s' % (self.error_code, self.error, self.request, self.api_type)

class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

def _encode_params(**kw):
    '''
    Encode parameters.
    '''
    args = []
    for k, v in kw.iteritems():
        qv = v.encode('utf-8') if isinstance(v, unicode) else str(v)
        args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)

def _decode_param(arg):
    result = {}
    for item in arg.split('&'):
        k,v  = item.split('=')
        result[k] = v
    return _obj_hook(result)
        

def _encode_multipart(**kw):
    '''
    Build a multipart/form-data body with generated random boundary.
    '''
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            ext = ''
            filename = getattr(v, 'name', '')
            n = filename.rfind('.')
            if n != (-1):
                ext = filename[n:].lower()
            content = v.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % _guess_content_type(ext))
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary

_CONTENT_TYPES = { '.png': 'image/png', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.jpe': 'image/jpeg' }

def _guess_content_type(ext):
    return _CONTENT_TYPES.get(ext, 'application/octet-stream')

_HTTP_GET = 0
_HTTP_POST = 1
_HTTP_UPLOAD = 2

def _http_get(http_url, authorization=None, api_type='weibo', **kw):
    logging.info('GET %s' % http_url)
    return _http_call(http_url, _HTTP_GET, authorization, api_type, **kw)

def _http_post(http_url, authorization=None, api_type='weibo', **kw):
    logging.info('POST %s' % http_url)
    return _http_call(http_url, _HTTP_POST, authorization, api_type, **kw)

def _http_upload(http_url, authorization=None, api_type='weibo', **kw):
    logging.info('MULTIPART POST %s' % http_url)
    return _http_call(http_url, _HTTP_UPLOAD, authorization, api_type, **kw)

def _http_call(http_url, method, authorization = None, api_type='weibo', **kw):
    '''
    send an http request and expect to return a json object if no error.
    '''
    params = None
    boundary = None
    if method==_HTTP_UPLOAD:
        params, boundary = _encode_multipart(**kw)
    else:
        params = _encode_params(**kw)
    http_url = '%s?%s' % (http_url, params) if method==_HTTP_GET else http_url
    http_body = None if method==_HTTP_GET else params
    req = urllib2.Request(http_url, data=http_body)
    if authorization and api_type=='weibo':
        req.add_header('Authorization', 'OAuth2 %s' % authorization)
    if authorization and api_type=='douban':
        req.add_header('Authorization', 'Bearer %s' % authorization)
    if boundary:
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    try:
        resp = urllib2.urlopen(req)
    except HTTPError as e:
        raise APIError(e.code, 'http error reason %s'%e.read(), 'OAuth2 request', api_type)

    body = resp.read()
    if api_type=='weibo' or api_type=='douban':
        r = json.loads(body, object_hook=_obj_hook)
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, getattr(r, 'error', ''), getattr(r, 'request', ''))
    else:
        r = body
    return r

class HttpObject(object):

    def __init__(self, client, method, api_type='weibo'):
        self.client = client
        self.method = method
        self.api_type = api_type

    def __getattr__(self, attr):
        def wrap(**kw):
            if self.client.is_expires():
                raise APIError('21327', 'expired_token', attr)
            if self.api_type == 'weibo':
                return _http_call('%s%s.json' % (self.client.api_url, attr.replace('__', '/')), self.method, self.client.access_token, api_type='weibo', **kw)
            elif self.api_type == 'qzone':
                return _http_call('%s%s' % (self.client.api_url, attr.replace('__', '/')), self.method, self.client.access_token, api_type='weibo', **kw)
            elif self.api_type == 'douban':
                return _http_call('%s%s/%s' % (self.client.api_url, attr.replace('__', '/'), self.client.address), self.method, self.client.access_token,api_type='douban', **kw)

        return wrap

class APIClient(object):
    '''
    API client using synchronized invocation.
    '''
    def __init__(self, app_key, app_secret, redirect_uri=None, response_type='code', api_type='weibo'):
        self.address = ''
        self.client_id = app_key
        self.client_secret = app_secret
        self.redirect_uri = redirect_uri
        self.response_type = response_type 
        if api_type == 'weibo':
            self.auth_url = 'https://api.weibo.com/oauth2/'
            self.api_url = 'https://api.weibo.com/2/'
        elif api_type == 'qzone':
            self.auth_url = 'https://graph.qq.com/oauth2.0/'
            self.api_url = 'https://graph.qq.com/'
        elif api_type == 'douban':
            self.auth_url = 'https://www.douban.com/service/auth2/'
            self.api_url = 'https://api.douban.com/'
        self.api_type = api_type
        self.access_token = None
        self.expires = 0.0
        if api_type=='weibo':
            self.get = HttpObject(self, _HTTP_GET)
            self.post = HttpObject(self, _HTTP_POST)
            self.upload = HttpObject(self, _HTTP_UPLOAD)
        elif api_type=='qzone':
            self.get = HttpObject(self, _HTTP_GET, api_type=api_type)
            self.post = HttpObject(self, _HTTP_POST, api_type=api_type)
            self.upload = HttpObject(self, _HTTP_UPLOAD, api_type=api_type)
        elif api_type=='douban':
            self.get = HttpObject(self, _HTTP_GET, api_type=api_type)
            self.post = HttpObject(self, _HTTP_POST, api_type=api_type)
            self.upload = HttpObject(self, _HTTP_UPLOAD, api_type=api_type)

    def set_access_token(self, access_token, expires_in):
        self.access_token = str(access_token)
        self.expires = float(expires_in) + time.time()

    def set_third_party_id(self, third_party_id):
        self.third_party_id = third_party_id

    def get_authorize_url(self, redirect_uri=None, display='default'):
        '''
        return the authroize url that should be redirect.
        '''
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError('21305', 'Parameter absent: redirect_uri', 'OAuth2 request', self.api_type)
        if self.api_type == 'weibo':
            return '%s%s?%s' % (self.auth_url, 'authorize', _encode_params(client_id = self.client_id, response_type = 'code', redirect_uri = redirect,with_offical_account=1))
        elif self.api_type == 'qzone':
            return '%s%s?%s' % (self.auth_url, 'authorize', _encode_params(client_id = self.client_id, response_type = 'code', redirect_uri = redirect, scope='get_user_info,add_topic,upload_pic,add_share,check_page_fans,do_like,get_info,get_other_info,get_fanslist,get_idolist,add_idol,qplus_add_feeds,qplus_add_push_connect'))
        else:
            return '%s%s?%s' % (self.auth_url, 'auth', _encode_params(client_id = self.client_id, response_type = 'code', redirect_uri = redirect))



    def request_access_token(self, code, redirect_uri=None):
        '''
        return access token as object: {"access_token":"your-access-token","expires_in":12345678}, expires_in is standard unix-epoch-time
        '''
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError('21305', 'Parameter absent: redirect_uri', 'OAuth2 request')

        if self.api_type == 'weibo':
            r = _http_post('%s%s' % (self.auth_url, 'access_token'), \
                    api_type='weibo',
                    client_id = self.client_id, \
                    client_secret = self.client_secret, \
                    redirect_uri = redirect, \
                    code = code,\
                    grant_type = 'authorization_code')
            self.set_third_party_id(r.uid)

        elif self.api_type == 'qzone':
            r = _http_post('%s%s' % (self.auth_url, 'token'), \
                    api_type='qzone',
                    client_id = self.client_id, \
                    client_secret = self.client_secret, \
                    redirect_uri = redirect, \
                    code = code, \
                    state = '123456',####random string to prevoid CSRF attack\
                    grant_type = 'authorization_code')
            if 'error' in r:
                raise APIError('400', 'access_token request failed', 'OAuth2 request', self.api_type)
            r = _decode_param(r)
        elif self.api_type == 'douban':
            r = _http_post('%s%s' % (self.auth_url, 'token'), \
                    api_type='douban',
                    client_id = self.client_id, \
                    client_secret = self.client_secret, \
                    redirect_uri = redirect, \
                    code = code, \
                    grant_type = 'authorization_code')
            self.set_third_party_id(r.douban_user_id)
        self.set_access_token(r.access_token, r.expires_in)
        return r

    def request_openid(self):
        r = _http_get('%s%s' % (self.auth_url,'me'),
            api_type = 'qzone',
            access_token = self.access_token
        )
        r = r[10:-4]
        try:
            r = json.loads(r, object_hook=_obj_hook)
            self.set_third_party_id(r.openid)
        except:
            raise APIError('400', 'openid request failed', 'OAuth2 request', self.api_type)
        return r

    def is_expires(self):
        return not self.access_token or time.time() > self.expires

    def __getattr__(self, attr):
        return getattr(self.get, attr)

    def get_user_info(self):
        ####TODO ADD TRY CATCH
        info = {}
        response = None
        name = 'None'
        description = ''
        avatar = ''
        if self.api_type == 'weibo':
            response = self.get.users__show(uid = self.third_party_id)
            name = response.screen_name
            description = response.description
            avatar = response.avatar_large

        elif self.api_type == 'douban':
            self.address = '@me'
            response = self.get.people(alt='json')
            name = response.title.get('$t')
            avatar = response.link[2].get('@href')
            loc = avatar.find(self.third_party_id)
            if 'user_normal' in avatar:
                avatar = None
            elif loc > 0:
                avatar = avatar[:loc] + 'l' + avatar[loc:]
            description = response.content.get('$t')

        elif self.api_type == 'qzone':
            self.request_openid()
            response = self.get.user__get_user_info(access_token = self.access_token , oauth_consumer_key = self.client_id, openid = self.third_party_id)
            name = response.nickname
            avatar = response.figureurl_2
            description = '' 

        info['name'] = name
        info['avatar'] = avatar
        info['description'] = description
        info['uid'] = self.third_party_id
        info['type'] = self.api_type
        return info


    def add_social_share(self, txt, pic_url, url='', summary=''):
        if self.api_type == 'weibo':
            self.upload.statuses__upload(status = txt, pic = pic_url)
        elif self.api_type == 'douban':
            self.upload.shuo__statuses(source = self.access_token, text = txt, image = pic_url, attachments='''{"media": [{ "type": "image","href": "%s"},]}'''% url)
        elif self.api_type == 'qzone':
            self.post.share__add_share(access_token=self.access_token, oauth_consumer_key=self.client_id, openid=self.third_party_id, title=txt, url = url, images = pic_url, summary=summary)
