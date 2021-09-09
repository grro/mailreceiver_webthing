from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from mailreceiver_webthing.mailserver import MailServer
from email.utils import formatdate
import re
import uuid
import tornado.ioloop
import logging
import threading



class MailReceiverThing(Thing):

    def __init__(self, to_pattern, description: str):
        Thing.__init__(
            self,
            'urn:dev:ops:mailreceiver-1',
            'MailReceiver',
            [],
            description
        )

        self.to_pattern = Value(to_pattern)
        self.add_property(
            Property(self,
                     'to_pattern',
                     self.to_pattern,
                     metadata={
                         'title': 'to pattern',
                         'type': 'string',
                         'description': 'the to pattern that has to be matched for receiver',
                         'readOnly': False,
                     }))

        self.log = Value("")
        self.add_property(
            Property(self,
                     'log',
                     self.log,
                     metadata={
                         'title': 'log',
                         'type': 'string',
                         'description': 'log of newly received mails',
                         'readOnly': True,
                     }))

        self.mail = Value("")
        self.add_property(
            Property(self,
                     'mail',
                     self.mail,
                     metadata={
                         'title': 'mail',
                         'type': 'string',
                         'description': 'the mail message',
                         'readOnly': True,
                     }))

        self.ioloop = tornado.ioloop.IOLoop.current()

    def on_message(self, peer, mailfrom, rcpttos, data):
        mail = "Received: from " + peer[0] + ":" + str(peer[1]) + " by mail-receiver id " + str(uuid.uuid4()) + "\n for " + \
               ", ".join(rcpttos) + "; " + formatdate(localtime=True) + "\n" + data.decode("ascii")
        self.ioloop.add_callback(self.__update_props, peer, mailfrom, rcpttos, mail)

    def __update_props(self, peer, mailfrom, rcpttos, mail):
        from_pattern = self.to_pattern.get().strip()
        matched = False
        if len(from_pattern) <= 0:
            matched = True
        else:
            pattern = re.compile(self.to_pattern.get())
            for rcptto in rcpttos:
                if pattern.match(rcptto):
                    matched = True
                else:
                    logging.info('ignoring receiver address' + rcptto)
        if matched:
            self.mail.notify_of_external_update(mail)

        log_entries = list(self.log.get().split(", "))
        operation = "ACCEPTED" if matched else "IGNORED "
        log_entries.append("[" + formatdate(localtime=True) + "] " + operation + "  " + mailfrom + " (" + peer[0] + ":" + str(peer[1]) + ")  ->  " + ", ".join(rcpttos))
        if len(log_entries) > 50:
            log_entries = log_entries[:50]
        self.log.notify_of_external_update(', '.join(log_entries))


def run_server(port: int, mail_server_port: int, to_pattern: str, description: str):
    mail_receiver_webthing = MailReceiverThing(to_pattern, description)

    mail_server = MailServer(mail_server_port, mail_receiver_webthing.on_message)
    threading.Thread(target=mail_server.start).start()

    thing = SingleThing(mail_receiver_webthing)
    server = WebThingServer(thing, port=port, disable_host_validation=True)
    try:
        logging.info('starting the server listing on ' + str(port) + " (to_pattern=" + to_pattern + ")")
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')
