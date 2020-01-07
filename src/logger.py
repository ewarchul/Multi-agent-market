from collections.abc import Collection
from datetime import datetime
import os, sys


EVENT_LOGGER_INITIALIZED = 'Logger initialized'
EVENT_AGENT_KILLED = 'Agent killed'
EVENT_AGENT_STARTED = 'Agent started'
EVENT_AGENT_RESTARTED = 'Agent restarted'
EVENT_SYSTEM_INITIALIZED = 'System initialized'
EVENT_SYSTEM_CLOSE = 'System closing'
EVENT_CLI = 'CLI command received'
EVENT_EXCEPTION = 'Exception occurred'
EVENT_MESSAGE_SENT = 'Message sent'
EVENT_MESSAGE_RECEIVED = 'Message received'


EVENTS_ALL = {
    EVENT_LOGGER_INITIALIZED: (),
    EVENT_AGENT_KILLED: ('id',),
    EVENT_AGENT_STARTED: ('id', 'name', 'connections', 'jid', 'policy'),
    EVENT_AGENT_RESTARTED: ('id',),
    EVENT_SYSTEM_CLOSE: (),
    EVENT_CLI: ('command', 'args'),
    EVENT_EXCEPTION: ('where', 'type', 'exception'),
    EVENT_MESSAGE_SENT: ('sender', 'receiver', 'content'),
    EVENT_MESSAGE_RECEIVED: ('sender', 'receiver', 'content'),
}


logger = None


def initialize_default_logger(log_file):
    """

    :param log_file:
    """
    global logger
    streams = (sys.stdout, log_file) if log_file else sys.stdout,
    logger = Logger(streams, EVENTS_ALL)


class Logger(object):
    """ Logger class, for logging (and event handling)

    logger writes to streams in csv format
    columns:
    event id    timestamp   param1  param2  ...

    number of columns is determined by event with the largest number of parameters
    """
    SEPARATOR = '\t'
    ESCAPE = '"'
    LINE_SEPARATOR = os.linesep

    def __init__(self, to, events):
        """ Creates logger

        :param to: a stream or a list of streams that logger will write to
        :param events: a dict-like where for every event there is a sequence of parameter names
        """
        self.streams = to if isinstance(to, Collection) else [to]
        self.events = events
        self.handlers = {}
        self.columns_n = len(max(self.events.values(), key=len)) + 2

        if EVENT_LOGGER_INITIALIZED in events:
            self.log(EVENT_LOGGER_INITIALIZED)

    def register_event_handler(self, event, handler):
        """ Registers event handler for given event

        :param event: event for which the handler is registered
        :param handler: a function that accepts event and it's params as keyword args
        """
        if event in self.handlers:
            self.handlers[event].append(handler)
        else:
            self.handlers[event] = {handler}

    def remove_event_handler(self, event, handler):
        """ Removes event handler

        :param event: event for which handler will be removed
        :param handler: handler to remove
        """
        self.handlers[event].remove(handler)

    def log(self, event, **kwargs):
        """ Logs event.
        Writes csv line to all streams
        and calls all event handler

        :param event: event to log
        :param kwargs: event params
        """
        args = [kwargs.get(param, '') for param in self.events[event]]
        timestamp = datetime.now()

        self._write_fields(event, timestamp, *args)

        if event in self.handlers:
            for handler in self.handlers[event]:
                handler(event, **kwargs)

    def _write_fields(self, *columns):
        columns = [*columns, *['' for _ in range(self.columns_n - len(columns))]]
        columns = [self._escape_csv(c) for c in columns]

        line = self.SEPARATOR.join(columns)
        self._write(line)

    def _escape_csv(self, value):
        value = str(value)
        value.replace(self.ESCAPE, f'{self.ESCAPE}{self.ESCAPE}')
        if self.SEPARATOR in value or '\n' in value:
            value = f'{self.ESCAPE}{value}{self.ESCAPE}'

        return value

    def _write(self, line):
        for stream in self.streams:
            stream.write(f'{line}{self.LINE_SEPARATOR}')
