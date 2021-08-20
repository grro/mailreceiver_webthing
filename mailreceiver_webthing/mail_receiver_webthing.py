from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from mailreceiver_webthing.mailserver import MailServer
from email.utils import formatdate
import uuid
import tornado.ioloop
import logging
import threading



class MailReceiverThing(Thing):

    def __init__(self, description: str):
        Thing.__init__(
            self,
            'urn:dev:ops:mailreceiver-1',
            'MailReceiver',
            [],
            description
        )

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
        self.ioloop.add_callback(self.__update_props, mail)

    def __update_props(self, mail):
        self.mail.notify_of_external_update(mail)


def run_server(port: int, mail_server_port: int, description: str):

    mail_receiver_webthing = MailReceiverThing(description)

    mail_server = MailServer(mail_server_port, mail_receiver_webthing.on_message)
    threading.Thread(target=mail_server.start).start()

    thing = SingleThing(mail_receiver_webthing)
    server = WebThingServer(thing, port=port, disable_host_validation=True)
    try:
        logging.info('starting the server listing on ' + str(port))
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')
