from aiosmtpd.controller import Controller as BaseController
from aiosmtpd import smtp
import ssl


class Controller(BaseController):
    def __init__(self, *args, ident=smtp.__ident__, ssl_cert=None, ssl_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = '0.0.0.0'
        self.ident = ident
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key

    def factory(self):
        if self.ssl_cert and self.ssl_key:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(self.ssl_cert, self.ssl_key)
        else:
            context = None

        return smtp.SMTP(self.handler, enable_SMTPUTF8=self.enable_SMTPUTF8, ident=self.ident, tls_context=context)
