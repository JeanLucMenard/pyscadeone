# Copyright (c) 2023-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
from abc import ABC, abstractmethod
from typing import Union
from typing_extensions import Self

from ansys.scadeone.common.assets import SwanCode
import ansys.scadeone.swan as S
from .information import Information

class Parser(ABC):
    """The parser base class as a proxy to the F# methods implemented
        by the F# parser.
    """

    # Current parser in used. Set by derived class
    _CurrentParser = None

    @classmethod
    def get_current_parser(cls) -> Self:
        return cls._CurrentParser

    @classmethod
    def set_current_parser(cls, parser: Self):
        cls._CurrentParser = parser

    # Source of parsing
    _SwanSource = None

    @classmethod
    def get_source(cls) -> SwanCode:
        return cls._SwanSource

    @classmethod
    def set_source(cls, swan: SwanCode) -> SwanCode:
        cls._SwanSource = swan

    @abstractmethod
    def module_body(self, source: SwanCode) -> (S.ModuleBody, Information):
        """ Parse a Swan module from a SwanCode object

            The *content()* method is called to get the code.

            The *name* property is used to set the module identifier.

        Parameters
        ----------
        source : SwanCode
            Swan module (.swan)

        Returns
        -------
        (ModuleBody, Information):

            - Instance of a module
            - Attached information
        """
        pass

    @abstractmethod
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

            - Instance of a module interface
            - Attached information
        """
        pass

    @abstractmethod
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
            Instance Declaration object
        """
        pass

    @abstractmethod
    def equation(self, source: SwanCode) -> S.equations:
        """Parse a Swan equation.

        Parameters
        ----------
        source : SwanCode
            Swan equation text

        Returns
        -------
        Equation
            Instance of Equation object
        """
        pass

    @abstractmethod
    def expression(self, source: SwanCode) -> S.Expression:
        """Parse a Swan expression

        Parameters
        ----------
        source : SwanCode
            Swan expression text

        Returns
        -------
        Expression
            Instance of an expression object
        """

    @abstractmethod
    def scope_section(self, source: SwanCode) -> S.ScopeSection:
        """Parse a Swan scope section

        Parameters
        ----------
        source : str
            Swan scope section text

        Returns
        -------
        ScopeSection
            Instance of a scope section object
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass