__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import json
import os
from unittest import mock

from flask import Flask, Response, request

from hookee import HookeeManager, util
from hookee.pluginmanager import PluginManager
from tests.testcase import HookeeTestCase


class TestUtil(HookeeTestCase):
    def setUp(self):
        super(TestUtil, self).setUp()

        self.hookee_manager = HookeeManager()
        self.plugin_manager = PluginManager(self.hookee_manager)
        self.plugin = self.plugin_manager.get_plugin("request_url_info")

    def test_get_functions(self):
        # WHEN
        funcs = util.get_functions(self.plugin.module)

        # THEN
        self.assertEqual(funcs, ["run", "setup"])

    def get_args(self):
        # WHEN
        args = util.get_args(self.plugin.module.run)

        # THEN
        self.assertEqual(args, ["request"])

    def test_print_xml_formats_twiml(self):
        # GIVEN
        print_util = self.hookee_manager.print_util

        # WHEN
        with mock.patch.object(print_util, "print_basic") as mock_print_basic:
            print_util.print_xml("Body", "<Response><Message>Thanks!</Message></Response>")

        # THEN
        mock_print_basic.assert_called_once_with(
            "Body: <?xml version=\"1.0\" ?>\n<Response>\n\t<Message>Thanks!</Message>\n</Response>\n", color=mock.ANY)

    def test_print_xml_invalid_printed_as_is(self):
        # GIVEN
        print_util = self.hookee_manager.print_util

        # WHEN
        with mock.patch.object(print_util, "print_basic") as mock_print_basic:
            print_util.print_xml("Body", "<Response><Unclosed>")

        # THEN
        mock_print_basic.assert_called_once_with("Body: <Response><Unclosed>", color=mock.ANY)

    def test_save_request_saves_streamed_str_chunks(self):
        # GIVEN
        save_dir = os.path.join(self.config_dir, "requests")
        response = Response(iter(["data: event 0\n\n", "data: event 1\n\n"]))

        # WHEN
        with Flask(__name__).test_request_context("/stream"):
            path = util.save_request(request, response, save_dir)
            streamed = list(response.response)

        # THEN
        self.assertEqual(streamed, ["data: event 0\n\n", "data: event 1\n\n"])
        with open(path) as f:
            saved = json.load(f)
        self.assertEqual(saved["response"]["body"], "data: event 0\n\ndata: event 1\n\n")

    def test_is_xml_without_mimetype(self):
        # WHEN
        xml = util.is_xml(None)

        # THEN
        self.assertFalse(xml)
