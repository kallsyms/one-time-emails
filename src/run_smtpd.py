import asyncio

from web import app
from smtp.queue_worker import queue_worker
from smtp.controller import Controller
from smtp.handler import ForwardingHandler

loop = asyncio.get_event_loop()

smtp_controller = Controller(ForwardingHandler(),
                             port=app.config.get('SMTPD_PORT', 25),
                             ident=app.config.get('SMTPD_GREETING'),
                             ssl_cert=app.config.get('SMTPD_SSL_CERT'),
                             ssl_key=app.config.get('SMTPD_SSL_KEY'))
smtp_controller.start()

queue_worker_task = loop.create_task(queue_worker())

loop.run_forever()
