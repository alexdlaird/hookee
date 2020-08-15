import time
import unittest

from future.utils import iteritems

from hookee.manager import Manager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


class ManagedTestCase(unittest.TestCase):
    REQUEST_FORM_DATA_BOUNDARY = "REQUEST_FORM_DATA_BOUNDARY"
    FORM_DATA_STARTING_PAYLOAD = '--{0}\r\nContent-Disposition: form-data; name=\\"'.format(REQUEST_FORM_DATA_BOUNDARY)
    FORM_DATA_MIDDLE_PAYLOAD = '\"\r\n\r\n'
    FORM_DATA_ENDING_PAYLOAD = '--{0}--'.format(REQUEST_FORM_DATA_BOUNDARY)

    def setUp(self):
        self.port = 5000
        self.manager = Manager.get_instance(self.port)

        self.manager.start()

        self.webhook_url = "{}/webhook".format(self.manager.tunnel.public_url)

    def tearDown(self):
        self.manager.stop()

        time.sleep(2)

    def generate_form_data_payload(self, data):
        payload = ""
        for key, value in iteritems(data):
            payload += '{0}{1}{2}{3}\r\n'.format(self.FORM_DATA_STARTING_PAYLOAD, key, self.FORM_DATA_MIDDLE_PAYLOAD,
                                                 value)
        payload += self.FORM_DATA_ENDING_PAYLOAD
        return payload
