import dns.resolver
import dns.exception
import logging
import smtplib

from web import app

logger = logging.getLogger('smtpd.sender')


def send_mail_to_host_port(from_addr, to_addr, content, host, port):
    try:
        s = smtplib.SMTP(host, port, app.config['HOSTNAME'], timeout=10)
    except (OSError, smtplib.SMTPException) as e:  # OSError catches socket exceptions
        logger.info("Socket exception while connecting to %s:%d : %s", host, port, e)
        return False

    # Attempt to use STARTTLS
    try:
        s.starttls()
    except smtplib.SMTPResponseException:
        pass

    try:
        s.sendmail(from_addr, to_addr, content)
        return True
    except (OSError, smtplib.SMTPException) as e:  # OSError catches socket exceptions
        logger.info("Socket exception while sending to %s:%d : %s", host, port, e)
        return False
    finally:
        s.quit()


def _send_mail(from_addr, to_addr, content):
    mx_records = []
    a_records = []

    dst_domain = to_addr.rsplit('@', 1)[1]

    # Get MX records...
    try:
        mx_records = dns.resolver.query(dst_domain, 'MX')
    except dns.resolver.NoAnswer:
        # ... or if none exist, A records for the destination domain.
        try:
            a_records = dns.resolver.query(dst_domain, 'A')
        except dns.exception.DNSException as e:
            logger.info("Error resolving A records for %s: %s", dst_domain, e)
            return False
    except dns.exception.DNSException as e:
        logger.info("Error resolving MX records for %s: %s", dst_domain, e)
        return False

    mx_records = sorted(mx_records, key=lambda a: a.preference)
    hosts = [mx.exchange.to_text() for mx in mx_records] + [a.to_text() for a in a_records]

    for host in hosts:
        if send_mail_to_host_port(from_addr, to_addr, content, host, 587) or \
                send_mail_to_host_port(from_addr, to_addr, content, host, 25):
            return True

    return False


def send_mail(from_addr, to_addr, content):
    try:
        return _send_mail(from_addr, to_addr, content)
    except Exception as e:
        logging.warning("Unhandled warning while sending mail: %s", e)
        return False
