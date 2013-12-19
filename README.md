https_shim
==========

Allows setting the SSL protocol suite (ssl.PROTOCOL_SSLv3, etc.) for a 
subclass of httplib.HTTPSConnection (Python 2.6/2.7). Borrows from 
http://stackoverflow.com/a/18671399/306262 but uses subclassing instead of monkey-
patching.

Example Usage
=============
```python
import https_shim
import ssl

conn = https_shim.HTTPSConnection('httpbin.org', '443', ssl_version=ssl.PROTOCOL_SSLv3)
conn.request('GET', '/get?foo=bar')
...

or

conn.https_shim.HTTPSConnection('httpbin.org', '443')
conn.connect(ssl_version=ssl.PROTOCOL_SSLv3)
...

```

See the tests if you want a few examples.

Testing
=======
You can run the tests with 

    nosetests https_shim

If you pip install with the extra "test_support", the packages needed for running the tests will
alsoo be installed (in particular, nose), e.g.,

    pip install -e <path-to-https-shim>[test_support]


