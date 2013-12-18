import https_shim

import json
import ssl
import unittest
import urllib
import urlparse


HOSTNAME = "entdir.utexas.edu"


class LookupTests(unittest.TestCase):
    def _connect(self, ssl_version=None, host='httpbin.org',
                 port='443', path='/post',
                 params=None, method='POST'):
        if params is None:
            params = {'parameterabc': 'abcvalue',
                      'parameterxyz': 'xyzvalue'}
        method = method.upper()
            
        errors = []

        if isinstance(ssl_version, int):
            conn = https_shim.HTTPSConnection(host, port,
                                              ssl_version=ssl_version)
        else:
            conn = https_shim.HTTPSConnection(host, port)
            
        conn.connect()
        encoded_params = urllib.urlencode(params)
        
        if method == 'GET':
            path = "{path}?{query}".format(path=path,
                                           query=encoded_params)
            conn.request(method, path)
        elif method == 'POST':
            conn.request(method, path, encoded_params)
        else:
            raise ValueError('Unsupported method')

        response = conn.getresponse()
        if not response.status == 200:
            errors.append("Bad Response Status of {0}: {1}"
                          .format(response.status, response.reason))
        text = response.read()
        jdata = json.loads(text)

        if method == 'GET':
            result_dict = jdata['args']
        elif method == 'POST':
            post_string = jdata['data']
            result_dict = urlparse.parse_qs(post_string)
        else:
            raise ValueError('Unsupported method.')
        
        for key, value in params.items():
            val_list = result_dict.get(key)
            if val_list is None:
                errors.append("Did not find key '{0}' in response.".format(key))
            elif not isinstance(val_list, (tuple, list)):
                if val_list != value:
                    errors.append("Did not find value '{0}' "
                                  "in response for key '{1}'."
                                  .format(value, key))
            elif len(val_list) < 1:
                errors.append("Did not find value for key '{0}'.".format(key))
            else:
                val = val_list[0]
                if val != value:
                    errors.append("Did not find value '{0}' "
                                  "in response for key '{1}'."
                                  .format(value, key))


        return jdata, errors

    def test_can_get_without_ssl_version(self):
        _, errors = self._connect(path='/get', method='GET')
        self.assertEqual(0, len(errors))

    def test_can_get_using_ssl_v23(self):
        _, errors = self._connect(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_SSLv23)
        self.assertEqual(0, len(errors))

    def test_can_get_using_ssl_v3(self):
        _, errors = self._connect(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_SSLv3)
        self.assertEqual(0, len(errors))

    def test_can_get_using_ssl_v1(self):
        _, errors = self._connect(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_TLSv1)
        self.assertEqual(0, len(errors))
    
    def test_can_post_without_ssl_version(self):
        _, errors = self._connect()
        self.assertEqual(0, len(errors))

    def test_can_post_using_ssl_v23(self):
        _, errors = self._connect(ssl_version=ssl.PROTOCOL_SSLv23)
        self.assertEqual(0, len(errors))

    def test_can_post_using_ssl_v3(self):
        _, errors = self._connect(ssl_version=ssl.PROTOCOL_SSLv3)
        self.assertEqual(0, len(errors))

    def test_can_post_using_ssl_v1(self):
        _, errors = self._connect(ssl_version=ssl.PROTOCOL_TLSv1)
        self.assertEqual(0, len(errors))
