# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
Parser
------
This module contains the :py:class:`Parser` which is a proxy to the Scade One F# parser.
The _Parser_ class offers methods to parse a complete Swan code (interface or module),
or a declaration, or an expression.

It relies on the `ansys.scadeone.model.dotnet` and `ansys.scadeone.model.pyofast` modules
to interface with the dotnet DLLs and to transform F# data structure into the
`ansys.scadeone.swan` python classes.
"""
import logging
from typing import Union
import json

# dotnet configuration
import ansys.scadeone.model.dotnet # noqa

from ANSYS \
     .SONE \
     .Infrastructure \
     .Services \
     .Serialization \
     .BNF\
     .Parsing import Reader, ParserTools # type:ignore

from ANSYS.SONE.Core.Toolkit.Logging import ILogger # type:ignore

from ansys.scadeone.common.exception import ScadeOneException
from .pyofast import (
    moduleOfAst,
    interfaceOfAst,
    declarationOfAst,
    equationOfAst,
    expressionOfAst,
    scopeSectionOfAst,
    operatorExprOfAst,
    operatorBlockOfAst,
    operatorOfAst
)
from .information import Information

from .parser import Parser

from ansys.scadeone.common.storage import SwanStorage
import ansys.scadeone.swan as S

SwanVersion = ParserTools.SwanVersion
SwanTestVersion = ParserTools.SwanTestVersion

class ParserLogger(ILogger):
    """Logger class for the parser. An instance of the
    class is given to the F# parser to get the logging information
    in Python world.

    The class only implements the methods from ILogger that may be called
    from the parser.

    Parameters
    ----------
    ILogger : ILogger
        C# interface
    """
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    @property
    def logger(self):
        return self._logger

    # https://stackoverflow.com/questions/49736531/implement-a-c-sharp-interface-in-python-for-net
    __namespace__ = "MyPythonLogger"

    def _log(self, category, message, log_fn):
        log_fn(f"{category}: {message}")

    def Info(self, category, message):
        self._log(category, message, self.logger.info)

    def Warning(self, category, message):
        self._log(category, message, self.logger.warning)

    def Error(self, category, message):
        self._log(category, message, self.logger.error)

    def Exception(self, category, message):
        self._log(category, message, self.logger.exception)

    def Debug(self, category, message):
        self._log(category, message, self.logger.debug)


class SwanParser(Parser):
    """The parser class is a proxy to the F# methods implemented
        by the parser.
    """
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = ParserLogger(logger)

    def _get_json(self, string_opt) -> Information:
        """Return a JSON dict from the information string
           found in the Swan source

        Args:
            string_opt (F# string option): information data

        Returns:
            Information: data found.
        """

        if string_opt is not None:
            try:
                data = json.loads(string_opt.Value)
                if not isinstance(data, dict):
                    self._logger.Error("SwanLoader",
                                       "Expecting a JSON dictionary")
                    data = None
            except Exception as e:
                self._logger.Error("SwanLoader",
                                   f"Cannot load JSON information: {e}")
                data = None
        else:
            data = None

        return Information(data)

    def _parse(self, rule_fn, swan: SwanStorage):
        """Call F# parser with a given rule

        Args:
            rule_fn: parser rule function
            swan (SwanStorage): Swan code to pare

        Raises:
            ScadeOneException: in case of parser error

        Returns:
            result: parser value
        """
        # save current parser for pyofast methods
        Parser.set_current_parser(self)
        Parser.set_source(swan)

        try:
            result = rule_fn(swan.source, swan.content(), self._logger)
        except Reader.ParseError as e:
            raise ScadeOneException(f"Parser: {e.Message}")
        except Exception as e:
            raise ScadeOneException(f"Internal: {e}")
        return result

    def module_body(self, source: SwanStorage) -> tuple[S.ModuleBody, Information]:
        """ Parse a Swan module from a SwanStorage object.

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanStorage
            Swan module (.swan)

        Returns
        -------
        (ModuleBody, Information)
            instance of ModuleBody and attached information
        """
        result = self._parse(Reader.parse_body, source)
        return (moduleOfAst(source.name, result.Item1),
                self._get_json(result.Item2))

    def module_interface(self, source: SwanStorage) -> tuple[S.ModuleInterface, Information]:
        """ Parse a Swan interface from a SwanStorage object.

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanStorage
            Swan interface (.swani)

        Returns
        -------
        (ModuleInterface, Information)
            instance of ModuleInterface and attached information.
        """
        result = self._parse(Reader.parse_interface, source)
        return (interfaceOfAst(source.name, result.Item1),
                self._get_json(result.Item2))

    def declaration(self, source: SwanStorage) -> S.Declaration:
        """Parse a Swan declaration:
          type, const, sensor, group, use, operator (signature or with body).

        Parameters
        ----------
        source : SwanStorage
            Single Swan declaration

        Returns
        -------
        Declaration
            Corresponding declaration object
        """
        ast = self._parse(Reader.parse_declaration, source)
        return declarationOfAst(ast)

    def equation(self, source: SwanStorage) -> S.Equation:
        """Parse a Swan equation.

        Parameters
        ----------
        source : SwanStorage
            Swan equation text

        Returns
        -------
        Equation
            Corresponding Equation object
        """
        ast = self._parse(Reader.parse_equation, source)
        return equationOfAst(ast)

    def expression(self, source: SwanStorage) -> S.expressions:
        """Parse a Swan expression

        Parameters
        ----------
        source : SwanStorage
            Swan expression text

        Returns
        -------
        Expression
            Corresponding expression object
        """
        ast = self._parse(Reader.parse_expr, source)
        return expressionOfAst(ast)

    def scope_section(self, source: SwanStorage) -> S.ScopeSection:
        """Parse a Swan scope section

        Parameters
        ----------
        source : str
            Swan scope section text

        Returns
        -------
        ScopeSection
            Corresponding scope section object
        """
        ast = self._parse(Reader.parse_scope_section, source)
        return scopeSectionOfAst(ast)

    def op_expr(self, source: SwanStorage) -> S.OperatorExpression:
        """Parse a Swan operator expression

        Parameters
        ----------
        source : SwanStorage
            Swan code for operator expression

        Returns
        -------
        OperatorExpression
            Instance of the operator expression object
        """
        ast = self._parse(Reader.parse_op_expr, source)
        return operatorExprOfAst(ast)

    def operator_block(self, source: SwanStorage) -> Union[S.OperatorBase, S.OperatorExpression]:
        """Parse a Swan operator block

        *operator_block* ::= *operator* | *op_expr*

        Parameters
        ----------
        source : SwanStorage
            Swan code for operator block

        Returns
        -------
        Union[S.OperatorBase, S.OperatorExpression]
            Instance of the *operator* or *op_expr*
        """
        ast = self._parse(Reader.parse_operator_block, source)
        return operatorBlockOfAst(ast)

    def operator(self, source: SwanStorage) -> S.Operator:
        """Parse a Swan user operator

         Parameters
        ----------
        source : SwanStorage
            Swan user operator text

        Returns
        -------
        S.Operator
            Instance of the user operator
        """
        ast = self._parse(Reader.parse_user_operator, source)
        return operatorOfAst(ast)
