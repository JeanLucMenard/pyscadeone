# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
Scade One Exception
-------------------

The class :py:class:`ScadeOneException` is used to raise an exception.
The message passed when raising the exception is passed to the
Scade One logger :py:class:`ScadeOneLogger`

"""
from ansys.scadeone.common.logger import LOGGER


class ScadeOneException(Exception):
    """ScadeOne API Exception.
       When raising a ScadeOneException it is automatically logged
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
        LOGGER.exception(message)
