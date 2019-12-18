import os

import unittest

from config import load_agent_config


def production_limit_fun(time, dt, arg1, arg2):
    return time, dt, arg1, arg2


TEST_CONFIG = os.path.join(os.path.split(__file__)[0], 'test_agent_config.yaml')


class TestAgentConfig(unittest.TestCase):
    def test_agent_config(self):
        config = load_agent_config(TEST_CONFIG)

        self.assertEqual(config.initial_resource, 1)
        self.assertEqual(config.storage_limit, 4)

    def test_agent_config_function(self):
        config = load_agent_config(TEST_CONFIG)
        time, dt, arg1, arg2 = config.production_limit(1, 2)
        self.assertEqual(time, 1)
        self.assertEqual(dt, 2)
        self.assertEqual(arg1, 3)
        self.assertEqual(arg2, 'a')

