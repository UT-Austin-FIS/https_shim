import httplib
import socket
import ssl

class HTTPSConnection(httplib.HTTPSConnection):
    """
    This class is a subclass of HTTPSConnection. It allowss specifying
    an ssl version (really a protocol suite), giving a mechanism for
    working around bugs like that discussed at
    https://bugs.launchpad.net/ubuntu/+source/openssl/+bug/861137
    
    It is based on the first suggestions at
    http://stackoverflow.com/a/18671399/306262, but instead of monkey-
    patching we provide a new connect implementation in a subclass.
    """
    
    def __init__(self, *args, **kwargs):
        """
        The same parameters as in httplib.HTTPSConnection, with the addition
        of ssl_version: One of the SSL PROTOCOL versions defined in the
        ssl module (PROTOCOL_SSLV2, PROTOCOL_SSLv23, etc. Note the
        security warnings: SSL version 2 is insecure!
        """
        if len(args) > 4:
            self.ssl_version = args[4]
        else:
            try:
                self.ssl_version = kwargs.pop('ssl_version')
            except KeyError:
                self.ssl_version = None
        # HTTPSConnection is an old-style class, so no super()
        httplib.HTTPSConnection.__init__(self, *args[:4], **kwargs)

    def connect(self, ssl_version=None):
        """
        Connect to a host on a given (SSL) port.
        parameters:
            ssl_version: One of the SSL PROTOCOL versions defined in the
            ssl module (PROTOCOL_SSLV2, PROTOCOL_SSLv23, etc. Note the
            security warnings: SSL version 2 is insecure!
        """

        if ssl_version is None:
            vers = self.ssl_version
        else:
            vers = ssl_version
            
        return self._connect_with_ssl_version(vers)

    def _connect_with_ssl_version(self, ssl_version):

        if ssl_version is None:
            return httplib.HTTPSConnection.connect(self)

        # No source_address before Python 2.7
        if hasattr(self, 'source_address'):
            sock = socket.create_connection(
                        (self.host, self.port),
                        self.timeout,
                        getattr(self, 'source_address')
            )
        else:
            sock = socket.create_connection((self.host, self.port),
                                            self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ssl_version=ssl_version)
