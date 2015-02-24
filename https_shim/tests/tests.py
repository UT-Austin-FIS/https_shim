import json
import ssl
import unittest
import urllib
import urlparse

from https_shim import HTTPSConnection
from mock import Mock, patch


class ConnectionError(RuntimeError):
    pass


class LookupTests(unittest.TestCase):

    def _connect_full(self,
                 ssl_version=None,
                 host='httpbin.org',
                 port='443',
                 path='/post',
                 params=None,
                 method='POST'):
        """
        _connect_full tests creating a connection where the ssl_version
        is not passed in at initialization, but in a subsequent call to
        HTTPSConnection.connect, and where the full panoply of
        HTTPSConnection methods are potentially used: connect, putrequest,
        putheader, endheaders, and send.
        """
        if params is None:
            params = {'parameterabc': 'abcvalue',
                      'parameterxyz': 'xyzvalue'
                     }
        method = method.upper()
        
        conn = self._create(host, port)
        conn.connect(ssl_version=ssl_version)

        encoded_params = urllib.urlencode(params)
        
        if method == 'GET':
            path = "{path}?{query}".format(path=path,
                                           query=encoded_params)
            conn.putrequest(method, path)
            conn.endheaders()
        elif method == 'POST':
            conn.putrequest(method, path)
            conn.putheader('Content-Length', len(encoded_params))
            conn.endheaders()
            conn.send(encoded_params)
        else:
            raise ConnectionError('Unsupported method')

        jdata = self._evaluate_response(conn)
        return self._evaluate_json(jdata, method, params)
    
    def _connect_with_request(self,
                              ssl_version=None,
                              host='httpbin.org',
                              port='443',
                              path='/post',
                              params=None,
                              method='POST'):
        """
        _connect_with_request tests creating a connection where
        ssl_version is passed to HTTPSConnection on initialization, and
        the HTTPSConnection.request method is used to make the connection.
        """
        if params is None:
            params = {'parameterabc': 'abcvalue',
                      'parameterxyz': 'xyzvalue'
                     }
        method = method.upper()
        
        conn = self._create(host, port, ssl_version)

        try:
            jdata = self._request(connection=conn,
                                  method=method,
                                  path=path,
                                  params=params)
        except ConnectionError as ce:
            return [str(ce)]
        else:
            return self._evaluate_json(jdata=jdata,
                                       method=method,
                                       params=params)

    def _create(self, host, port, ssl_version=None):
        if ssl_version is None:
            conn = HTTPSConnection(host, port, timeout=120)
            conn.set_debuglevel(1)
        else:
            conn = HTTPSConnection(host, port, ssl_version=ssl_version)
        return conn

    def _evaluate_json(self, jdata, method, params):
        errors = []
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
        return errors
    
    def _evaluate_response(self, connection):
        response = connection.getresponse()
        if not response.status == 200:
            raise ConnectionError("Bad Response Status of {0}: {1}"
                                  .format(response.status, response.reason))
        
        text = response.read()
        jdata = json.loads(text)
        return jdata

    def _request(self, connection, method, path, params):
        encoded_params = urllib.urlencode(params)
        
        if method == 'GET':
            path = "{path}?{query}".format(path=path,
                                           query=encoded_params)
            connection.request(method, path)
        elif method == 'POST':
            connection.request(method, path, encoded_params)
        else:
            raise ConnectionError('Unsupported method')

        return self._evaluate_response(connection)


    # Test parameter passing
    def test_ssl_version_in_init_is_used_in_request(self):
        version = Mock()
        real_method = HTTPSConnection._connect_with_ssl_version
        
        with patch.object(HTTPSConnection, '_connect_with_ssl_version')\
            as mock:
            conn = HTTPSConnection('httpbin.org', '443', ssl_version=version)
            # request will attempt to make the call, so we need to keep
            # it from failing
            def side_effect(version):
                return real_method(conn, ssl.PROTOCOL_TLSv1)

            mock.side_effect = side_effect
            
            conn.request('GET', '/get?foo=bar')
            mock.assert_called_with(version)

    def test_ssl_version_in_init_is_used_in_connect(self):
        version = Mock()
            
        with patch.object(HTTPSConnection, '_connect_with_ssl_version')\
            as mock:
            conn = HTTPSConnection('httpbin.org', '443')
            conn.connect(ssl_version=version)
            mock.assert_called_with(version)
                
    # End-to-end connectivity tests
    def test_can_get_without_version_connect_request(self):
        errors = self._connect_with_request(path='/get', method='GET')
        self.assertEqual(0, len(errors))

    def test_can_get_using_SSLv23_connect_request(self):
        errors = self._connect_with_request(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_SSLv23)
        self.assertEqual(0, len(errors))

    @unittest.skip('httpbin.org turned off SSLv3 support')
    def test_can_get_using_SSLv3_connect_request(self):
        errors = self._connect_with_request(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_SSLv3)
        self.assertEqual(0, len(errors))

    def test_can_get_using_TLSv1_connect_request(self):
        errors = self._connect_with_request(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_TLSv1)
        self.assertEqual(0, len(errors))
    
    def test_can_post_without_version_connect_request(self):
        errors = self._connect_with_request()
        self.assertEqual(0, len(errors))

    def test_can_post_using_SSLv23_connect_request(self):
        errors = self._connect_with_request(ssl_version=ssl.PROTOCOL_SSLv23)
        self.assertEqual(0, len(errors))

    @unittest.skip('httpbin.org turned off SSLv3 support')
    def test_can_post_using_SSLv3_connect_request(self):
        errors = self._connect_with_request(ssl_version=ssl.PROTOCOL_SSLv3)
        self.assertEqual(0, len(errors))

    def test_can_post_using_TLSv1_connect_request(self):
        errors = self._connect_with_request(ssl_version=ssl.PROTOCOL_TLSv1)
        self.assertEqual(0, len(errors))

    def test_can_get_without_version_connect_full(self):
        errors = self._connect_full(path='/get', method='GET')
        self.assertEqual(0, len(errors))

    def test_can_get_using_SSLv23_connect_full(self):
        errors = self._connect_full(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_SSLv23)
        self.assertEqual(0, len(errors))

    @unittest.skip('httpbin.org turned off SSLv3 support')
    def test_can_get_using_SSLv3_connect_full(self):
        errors = self._connect_full(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_SSLv3)
        self.assertEqual(0, len(errors))

    def test_can_get_using_TLSv1_connect_full(self):
        errors = self._connect_full(path='/get', method='GET',
                                  ssl_version=ssl.PROTOCOL_TLSv1)
        self.assertEqual(0, len(errors))
    
    def test_can_post_without_version_connect_full(self):
        errors = self._connect_full()
        self.assertEqual(0, len(errors))

    def test_can_post_using_SSLv23_connect_full(self):
        errors = self._connect_full(ssl_version=ssl.PROTOCOL_SSLv23)
        self.assertEqual(0, len(errors))

    @unittest.skip('httpbin.org turned off SSLv3 support')
    def test_can_post_using_SSLv3_connect_full(self):
        errors = self._connect_full(ssl_version=ssl.PROTOCOL_SSLv3)
        self.assertEqual(0, len(errors))

    def test_can_post_using_TLSv1_connect_full(self):
        errors = self._connect_full(ssl_version=ssl.PROTOCOL_TLSv1)
        self.assertEqual(0, len(errors))
