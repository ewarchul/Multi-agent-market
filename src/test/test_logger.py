import unittest
import os

import logger


class TestStream:
    def __init__(self):
        self.log = []

    def write(self, line):
        self.log.append(line)

    def flush(self):
        pass


class TestLogger(unittest.TestCase):
    def test_logger_basic(self):
        events = {
            'e1': ['param1'],
            'e2': ['param2'],
        }
        stream = TestStream()

        l = logger.Logger(stream, events)

        l.log('e1', param1='val1')
        l.log('e2', param2='val2')
        l.log('e1', param1='val3')

        self.assertEqual(len(stream.log), 3)
        self.assertTrue(stream.log[0].startswith('e1\t'))
        self.assertTrue(stream.log[0].endswith('\tval1\n'))
        self.assertTrue(stream.log[1].startswith('e2\t'))
        self.assertTrue(stream.log[1].endswith('\tval2\n'))
        self.assertTrue(stream.log[2].startswith('e1\t'))
        self.assertTrue(stream.log[2].endswith('\tval3\n'))

    def test_logger_different_params_n(self):
        events = {
            'e1': ['param1'],
            'e2': ['param2', 'param3'],
        }
        stream = TestStream()

        l = logger.Logger(stream, events)

        l.log('e1', param1='val1')
        l.log('e2', param2='val2', param3='val4')
        l.log('e1', param1='val3')

        self.assertEqual(len(stream.log), 3)
        self.assertTrue(stream.log[0].startswith('e1\t'))
        self.assertTrue(stream.log[0].endswith('\tval1\t\n'))
        self.assertTrue(stream.log[1].startswith('e2\t'))
        self.assertTrue(stream.log[1].endswith('\tval2\tval4\n'))
        self.assertTrue(stream.log[2].startswith('e1\t'))
        self.assertTrue(stream.log[2].endswith('\tval3\t\n'))

    def test_logger_event_handler(self):
        events = {
            'e1': ['param1'],
            'e2': ['param2'],
        }
        stream = TestStream()

        called = 0

        def handler(event, param2):
            nonlocal called
            self.assertEqual(event, 'e2')
            self.assertEqual(param2, 'val2')
            called += 1

        l = logger.Logger(stream, events)
        l.register_event_handler('e2', handler)

        l.log('e1', param1='val1')
        l.log('e2', param2='val2')

        self.assertEqual(called, 1)
