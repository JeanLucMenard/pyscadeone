# Copyright (c) 2023-2023 ANSYS, Inc.
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
     .Parsing import Reader # type:ignore

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
    userOperatorOfAst
)
from .information import Information

from .parser import Parser

from ansys.scadeone.common.assets import SwanCode
import ansys.scadeone.swan as S

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
            except Exception as e:
                self._logger.Error("SwanLoader",
                                   f"Cannot load JSON information: {e}")
                data = None
        else:
            data = None

        if not isinstance(data, dict):
            self._logger.Error("SwanLoader",
                                f"Expecting a JSON dictionary")
            data = None
        return Information(data)

    def _parse(self, rule_fn, swan: SwanCode):
        """Call F# parser with a given rule

        Args:
            rule_fn: parser rule function
            swan (SwanCode): Swan code to pare

        Raises:
            ScadeOneException: in case of parser error

        Returns:
            result: parser value
        """
        # save current parser for pyofast methods
        Parser.set_current_parser(self)
        Parser.set_source(swan)
        ast = None
        try:
            result = rule_fn(swan.source, swan.content(), self._logger)
        except Reader.ParseError as e:
            raise ScadeOneException(f"Parser: {e.Message}")
        except Exception as e:
            raise ScadeOneException(f"Internal: {e}")
        return result

    def module_body(self, source: SwanCode) -> (S.ModuleBody, Information):
        """ Parse a Swan module from a SwanCode object.

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanCode
            Swan module (.swan)

        Returns
        -------
        (ModuleBody, Information)
            instance of ModuleBody and attached information
        """
        result = self._parse(Reader.parse_body, source)
        return (moduleOfAst(source.name, result.Item1),
                self._get_json(result.Item2))

    def module_interface(self, source: SwanCode) -> (S.ModuleInterface, Information):
        """ Parse a Swan interface from a SwanCode object.

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanCode
            Swan interface (.swani)

        Returns
        -------
        (ModuleInterface, Information)
            instance of ModuleInterface and attached information.
        """
        result = self._parse(Reader.parse_interface, source)
        return (interfaceOfAst(source.name, result.Item1),
                self._get_json(result.Item2))

    def declaration(self, source: SwanCode) -> S.Declaration:
        """Parse a Swan declaration:
          type, const, sensor, group, use, operator (signature or with body).

        Parameters
        ----------
        source : SwanCode
            Single Swan declaration

        Returns
        -------
        Declaration
            Corresponding declaration object
        """
        ast = self._parse(Reader.parse_declaration, source)
        return declarationOfAst(ast)

    def equation(self, source: SwanCode) -> S.Equation:
        """Parse a Swan equation.

        Parameters
        ----------
        source : SwanCode
            Swan equation text

        Returns
        -------
        Equation
            Corresponding Equation object
        """
        ast = self._parse(Reader.parse_equation, source)
        return equationOfAst(ast)

    def expression(self, source: SwanCode) -> S.expressions:
        """Parse a Swan expression

        Parameters
        ----------
        source : SwanCode
            Swan expression text

        Returns
        -------
        Expression
            Corresponding expression object
        """
        ast = self._parse(Reader.parse_expr, source)
        return expressionOfAst(ast)

    def scope_section(self, source: SwanCode) -> S.ScopeSection:
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

    def op_expr(self, source: SwanCode) -> S.OperatorExpression:
        """Parse a Swan operator expression

        Parameters
        ----------
        source : SwanCode
            Swan code for operator expression

        Returns
        -------
        OperatorExpression
            Instance of the operator expression object
        """
        ast = self._parse(Reader.parse_op_expr, source)
        return operatorExprOfAst(ast)

    def operator_block(self, source: SwanCode) -> Union[S.Operator, S.OperatorExpression]:
        """Parse a Swan operator block

        *operator_block* ::= *operator* | *op_expr*

        Parameters
        ----------
        source : SwanCode
            Swan code for operator block

        Returns
        -------
        Union[S.Operator, S.OperatorExpression]
            Instance of the *operator* or *op_expr*
        """
        ast = self._parse(Reader.parse_operator_block, source)
        return operatorBlockOfAst(ast)

    def user_operator(self, source: SwanCode) -> S.UserOperator:
        """Parse a Swan user operator

         Parameters
        ----------
        source : SwanCode
            Swan user operator text

        Returns
        -------
        S.UserOperator
            Instance of the user operator
        """
        ast = self._parse(Reader.parse_user_operator, source)
        return userOperatorOfAst(ast)
