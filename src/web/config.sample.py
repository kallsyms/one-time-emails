import os


class Config():
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///mail.db')
    HOSTNAME = os.environ['HOSTNAME']
    SECRET_KEY = os.urandom(32)

    LDAP_PROVIDER_URL = os.environ['LDAP_URI']
    LDAP_PROTOCOL_VERSION = 3
    LDAP_BIND_DN = os.environ['LDAP_BIND_DN']

    SMTPD_PORT = int(os.environ.get('SMTPD_PORT', 25))
    SMTPD_GREETING = 'Totally Postfix.'
    SMTPD_SSL_CERT = os.environ.get('SSL_CERT', '')
    SMTPD_SSL_KEY = os.environ.get('SSL_KEY', '')
