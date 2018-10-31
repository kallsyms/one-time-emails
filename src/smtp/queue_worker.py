import asyncio
import datetime

from smtp.sender import send_mail
from web import db
from web.mail.models import QueuedEmail


async def queue_worker():
    while True:
        for e in db.session.query(QueuedEmail).all():
            if send_mail(e.from_addr, e.to_addr, e.content):
                db.session.delete(e)
            else:
                e.last_retry_time = datetime.datetime.utcnow()

        db.session.commit()

        await asyncio.sleep(60)
