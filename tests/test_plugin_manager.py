from hookee.pluginmanager import PluginManager

from hookee.climanager import CliManager
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.9"


class TestPluginManager(HookeeTestCase):
    def setUp(self):
        super(TestPluginManager, self).setUp()

        self.cli_manager = CliManager(self.ctx)
        self.plugin_manager = PluginManager(self.cli_manager)

    def test_validate_plugin(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_not_conform_to_spec(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_no_plugin_type(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_no_run(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_wrong_args(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_no_blueprint(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_load_plugins(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN
