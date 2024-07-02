# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
Logging
-------
The `ScadeOneLogger` class creates a singleton which is accessed using
`logger.LOG` object.

The logger is part of the `ScadeOne` application instance.
"""

import logging
# From: https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook


class ScadeOneLogger:

    _Logger = None

    @staticmethod
    def Logger() -> logging.Logger:
        if ScadeOneLogger._Logger is None:
            # Initialize a logger for Scade One
            logger = logging.getLogger('ScadeOneLogger')
            logger.setLevel(logging.DEBUG)

            # create file handler which logs even debug messages
            fh = logging.FileHandler('pyscadeone.log')
            fh.setLevel(logging.DEBUG)
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            # create formatter and add it to the handlers
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            formatter = logging.Formatter(format)
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(fh)
            logger.addHandler(ch)
            ScadeOneLogger._Logger = logger
        return ScadeOneLogger._Logger


LOGGER = ScadeOneLogger.Logger()
