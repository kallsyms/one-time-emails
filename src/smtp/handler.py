import datetime

from smtp.sender import send_mail
from web import app, db
from web.mail.models import *


REJECT = '550 Rejected'
OK = '250 OK'


class ForwardingHandler:
    async def handle_RCPT(self, server, session, envelope, address, options):
        envelope.rcpt_options.extend(options)

        address, domain = address.rsplit('@', 1)
        aliases = db.session.query(Alias).join(Domain).filter(Alias.alias == address, Domain.name == domain).all()

        if not aliases:
            # No such address(es) exists
            sys_stats = get_system_stats()
            sys_stats.rejected_addresses += 1
            db.session.commit()
            return REJECT

        for alias in aliases:
            if alias.expires is not None and datetime.datetime.utcnow() > alias.expires:
                # The address expired. Go ahead and mark as disabled.
                alias.enabled = False

            if not alias.enabled:
                # The address is disabled
                alias.num_rejected += 1
                db.session.commit()
                return REJECT

            envelope.rcpt_tos.append(alias.forward)
            alias.num_accepted += 1

        db.session.commit()

        return OK

    async def handle_DATA(self, server, session, envelope):
        sys_stats = get_system_stats()
        sys_stats.num_incoming += 1
        db.session.commit()

        for rcpt in envelope.rcpt_tos:
            if not send_mail(envelope.mail_from, rcpt, envelope.original_content):
                m = QueuedEmail(from_addr=envelope.mail_from, to_addr=rcpt, content=envelope.original_content)
                db.session.add(m)
                db.session.commit()

        return OK
