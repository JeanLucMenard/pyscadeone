# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains classes that are used by all the other
language-related modules.

It contains base classes for various language constructs.
"""
from abc import ABC
from collections import namedtuple
from collections.abc import Iterable as abcIterable
from enum import Enum, auto
from typing import List, Optional, Union, Any, Iterable
from typing_extensions import Self
import re

from ansys.scadeone.common.exception import ScadeOneException


# TODO: implement ANNOTATIONS
class SwanItem(ABC):
    """Base class for Scade objects."""

    def __init__(self) -> None:
        self._owner = None

    @property
    def owner(self) -> Self:
        """Owner of current Swan construct."""
        return self._owner

    @owner.setter
    def owner(self, owner: Self):
        """Sets the owner of the Swan construct."""
        self._owner = owner

    @staticmethod
    def set_owner(owner: Self, children: Union[Self, Iterable[Self]]):
        """Helper to set *owner* as the owner of each item in the Iterable *items*."""
        if isinstance(children, abcIterable):
            for item in children:
                item.owner = owner
            return
        if children is not None:
            children.owner = owner

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        raise ScadeOneException(f"SwanItem.get_full_path(): not implemented for {type(self)}")

    @property
    def is_protected(self) -> bool:
        """Tells if a construct item is syntactically protected with some markup
        and is stored as a string (without the markup)."""
        return False

    @property
    def module(self) -> "ModuleBase":
        """Module containing the item

        Returns:
            ModuleBase: module container, see :py:class:`ModuleBody`
            and :py:class:`ModuleInterface`
        """
        if isinstance(self.owner, ModuleBase):
            return self.owner
        if self.owner is not None:
            return self.owner.module
        raise ScadeOneException("owner property is None")


class ModuleBase(SwanItem):
    """Base class for modules"""

    def __init__(self) -> None:
        super().__init__()


# ========================================================
# Miscellaneous general definitions
# Type for parsing an integer from a string.
# See class Numeric RE
IntegerTuple = namedtuple(
    "IntegerTuple", ["value", "is_bin", "is_oct", "is_hex", "is_dec", "is_signed", "size"]
)

# for parsing a float from a string
# see class Numeric RE
FloatTuple = namedtuple("FloatTuple", ["value", "mantissa", "exp", "size"])


class SwanRE:
    """Container of compiled regular expressions. These expressions can be matched with
    some strings. Some regular expressions use groups to extract parts.

    Attributes:

    TypedInteger: regular expressions for integers with post type (_i, _ui).
             Integer part is in the *value* group, type in the *type* group,
             and size in the *size* group.

    TypeFloat: regular expression for floats with post type (_f).
           Mantissa is in the *mantissa* group, exponent in the *exp* group,
           type in the *type* group, and size in the *size* group.

    """

    TypedInteger = re.compile(
        r"""
    (?P<value>                    # value group
     (?:0b[01]+)                  # binary
    |(?:0o[0-7]+)                 # octal
    |(?:0x[0-9a-fA-F]+)           # hexadecimal
    |(?:\d+))                     # decimal
    (?:(?P<type>_ui|_i)(?P<size>8|16|32|64))? # type group & size
    """,
        re.VERBOSE,
    )

    TypedFloat = re.compile(
        r"""
    (?P<value>                               # float part
    (?P<mantissa>(?:\d+\.\d*)|(?:\d*\.\d+))  # mantissa
    (?:[eE](?P<exp>[+-]?\d+))?)              # exponent
    (?:_f(?P<size>32|64))?                   # size
    """,
        re.VERBOSE,
    )

    @classmethod
    def parse_integer(cls, string: str, minus: bool = False) -> Union[IntegerTuple, None]:
        """Matches a string representing an integer and returns
        a description of that integer as an IntegerTuple.

        Parameters
        ----------
        string : str
            String representing an integer, with or without type information.
        minus : bool
            True when the value is preceded with a '-' minus operator.

        Returns
        -------
        IntegerTuple or None
            If the string value matches SwanRE.TypedInteger pattern, an
            IntegerTuple is returned. It is a namedtuple with fields:

            - *value*: computed value
            - *is_bin*, *is_oct*, *is_hex*, *is_dec*: flags set according to found type
            - *is_signed*: True when integer is signed
            - *size*: the size part

            Note: if there is no type information, type is _i32.
        """
        m = cls.TypedInteger.match(string)
        if not m:
            return None
        is_bin = m["value"].find("0b") != -1
        is_oct = m["value"].find("0o") != -1
        is_hex = m["value"].find("0x") != -1
        is_dec = not (is_bin or is_oct or is_hex)
        if m["type"]:
            assert not (minus and m["type"] == "_ui")
            is_signed = m["type"] == "_i" or minus
            size = int(m["size"])
        else:
            is_signed = True
            size = 32

        value = m["value"]
        if is_dec:
            value = int(value)
        elif is_bin:
            value = int(value[2:], 2)
        elif is_oct:
            value = int(value[2:], 8)
        elif is_hex:
            value = int(value[2:], 16)
        if minus:
            value = -value
        return IntegerTuple(value, is_bin, is_oct, is_hex, is_dec, is_signed, size)

    @classmethod
    def is_integer(cls, string: str) -> bool:
        """Check whether a string is a Swan integer.

        Parameters
        ----------
        string : str
            Integer value, as decimal, bin, octal, or hexadecimal, with
            or without type information.

        Returns
        -------
        bool
            True when string is an integer.
        """
        return cls.parse_integer(string) is not None

    @classmethod
    def parse_float(cls, string: str, minus: bool = False) -> Union[FloatTuple, None]:
        """Matches a string representing a float and returns
        a description of that float as a FloatTuple.

        Parameters
        ----------
        string : str
            String representing a float, with or without type information.
        minus : bool
            True when the value is preceded with a '-' minus operator.

        Returns
        -------
        FloatTuple or None
            If the string value matches SwanRE.TypedFloat pattern, a
            FloatTuple is returned. It is a namedtuple with fields:

            - *value*: computed value
            - *mantissa*: the mantissa part
            - *exp*: the exponent part
            - *size*: the size part

            Note: if there is no type information, type is _f32.
        """
        m = cls.TypedFloat.match(string)
        if not m:
            return None

        mantissa = m["mantissa"]
        exp = int(m["exp"]) if m["exp"] else 1
        size = int(m["size"]) if m["size"] else 32
        # We should use numpy for float32 / float64
        value = -float(m["value"]) if minus else float(m["value"])
        return FloatTuple(value, mantissa, exp, size)

    @classmethod
    def is_float(cls, string: str) -> bool:
        """Checks whether a string is a Swan integer.

        Parameters
        ----------
        string : str
            Integer value, as decimal, bin, octal, or hexadecimal, with
            or without type information.

        Returns
        -------
        bool
            True when string is an integer.
        """
        return cls.parse_float(string) is not None

    @classmethod
    def is_numeric(cls, string: str) -> bool:
        """Check whether a string a Swan numeric value,
        that is an integer of float value

        Args:
            string (str): string to check.

        Returns:
            bool: True if if string is a Swan numeric value
        """
        return cls.is_integer(string) or cls.is_float(string)

    CharRe = re.compile(r"(?:'[--~]'|\\x[0-9a-fA-F]{'1,2})$")

    @classmethod
    def is_char(cls, string: str) -> bool:
        """Check whether a string a Swan char value.

        Args:
            string (str): string to check.

        Returns:
            bool: True if if string is a Swan char value
        """
        return cls.CharRe.match(string) is not None

    BoolRe = re.compile("(?:true|false)$")

    @classmethod
    def is_bool(cls, string: str) -> bool:
        """Check whether a string a Swan boolean value.

        Args:
            string (str): string to check.

        Returns:
            bool: True if if string is a Swan char value
        """
        return cls.BoolRe.match(string) is not None


class Markup:
    """Class defining the markups used by the Swan serialization."""

    NoMarkup = ""
    #: General syntax error.
    Syntax = "syntax"
    #: Incorrect variable declaration.
    Var = "var"
    #: Incorrect group declaration.
    Group = "group"
    #: Incorrect sensor declaration.
    Sensor = "sensor"
    #: Incorrect const declaration.
    Const = "const"
    #: Incorrect type declaration.
    Type = "type"
    #: Incorrect use declaration.
    Use = "use"
    #: Incorrect operator signature in interface.
    Signature = "signature"
    #: Textual operator or generic operator content. The content is re-parsed by the API.
    Text = "text"
    #: Textual operator with syntax error.
    SyntaxText = "syntax_text"
    #: Empty instance block body. This is an invalid construct, but it is needed for the editor.
    Empty = "empty"
    #: Protected instance id.
    Inst = "inst"
    #: Operator expression. Specific markup for the editor. The content is re-parsed by the API.
    OpExpr = "op_expr"
    #: Incorrect forward dimension.
    Dim = "dim"

    @staticmethod
    def to_str(text: str, is_protected: bool = True, markup: str = None) -> str:
        """Returns {markup%text%markup}."""
        if not is_protected:
            return text
        if markup is None:
            markup = Markup.Syntax
        return f"{{{markup}%{text}%{markup}}}"


class NumericKind(Enum):
    """Numeric kinds for generic type constraints."""

    #: *numeric*
    Numeric = auto()
    #: *integer*
    Integer = auto()
    #: *signed*
    Signed = auto()
    #: *unsigned*
    Unsigned = auto()
    #: *float*
    Float = auto()

    @staticmethod
    def to_str(value: Self):
        return value.name.lower()


class Pragma:
    """Stores a pragma."""

    PragmaRE = re.compile(r"pragma\s+(?P<key>\w+)\s(?P<val>.*)#end")

    def __init__(self, pragma: str) -> None:
        self._pragma = pragma

    def get_pragma(self) -> Union[dict, None]:
        """Extracts pragma information as a tuple
        if pragma is valid, namely: #pragma key value#end.

        Returns
        -------
            dict | None
                The dict {'key', 'value'} if pragma is valid, None else.
        """
        m = Pragma.PragmaRE.match(self._pragma)
        if not m:
            return None
        return {"key": m["key"], "value": m["val"].strip()}

    def __str__(self) -> str:
        return self._pragma


# ========================================================
# Common Constructs, used by other constructs


class Identifier(SwanItem):
    """Class for identifier.

    An Identifier can be invalid if it was protected while saving it
    for some reason. In that case, the property *_is_valid_* is set to True.

    The class stores the pragmas associated with the Identifier.
    """

    IdentifierRe = re.compile(r"^[a-zA-Z]\w*$", re.ASCII)

    def __init__(
        self,
        value: str,
        pragmas: Optional[List[Pragma]] = None,
        comment: Optional[str] = None,
        is_name: Optional[bool] = False,
    ) -> None:
        """Identifier

        Parameters
        ----------
        value : str
            Identifier string.
        pragmas : List[Pragma]
            List of pragmas.
        comment : str, optional
            Comment, can be multiline, by default None.
        is_name : bool, optional
            True when Identifier is a name, aka. 'Identifier.
        """
        super().__init__()
        self._value = value
        self._pragmas = pragmas if pragmas else []
        self._comment = comment
        self._is_valid = Identifier.IdentifierRe.match(value) is not None
        self._is_name = is_name

    @property
    def is_valid(self) -> bool:
        """Returns true when Identifier is valid."""
        return self._is_valid

    @property
    def is_protected(self) -> bool:
        """Returns true when Identifier is valid."""
        return not self.is_valid

    @property
    def value(self) -> str:
        """Identifier as a string."""
        return f"'{self._value}" if self._is_name else self._value

    @property
    def is_name(self) -> bool:
        """Returns true when Identifier is a name."""
        return self._is_name

    @property
    def pragmas(self) -> List[Pragma]:
        """List of pragmas (strings)."""
        return self._pragmas

    @property
    def comment(self) -> str:
        """Comment string."""
        return self._comment

    def __str__(self) -> str:
        if self.pragmas:
            pragmas = " ".join([str(p) for p in self.pragmas]) + " "
        else:
            pragmas = ""
        return f"{pragmas}{self.value}"


class PathIdentifier(SwanItem):
    """Class for path identifiers, i.e: P1::Id.

    The class manipulates the PathIdentifier as separate items.

    If the original path was protected (given as a string), the property *is_valid*
    is False, and the path is considered to be a single string and *is_protected* is True.

    path_id argument is:

    - a list of identifiers, for a valid path.
    - a string if the path was protected.
    """

    def __init__(self, path_id: Union[List[Identifier], str]) -> None:
        super().__init__()
        self._ids = path_id
        self._is_valid = isinstance(path_id, list)

    # id { :: id} * regexp, with spaces included
    PathIdentifierRe = re.compile(
        r"""^[a-zA-Z]\w*   # identifier
                                  (?:\s*::\s*[a-zA-Z]\w*)*  # sequence of ('-' identifier)
                                  $""",
        re.ASCII | re.VERBOSE,
    )

    @classmethod
    def is_valid_path(cls, path: str) -> bool:
        """Checks if *path* is a valid path identifier, i.e.
        *id {:: id}*, with possible spaces around '::'.

        Parameters
        ----------
        path : str
            String containing the path identifier.

        Returns
        -------
        bool
            True when path is valid.
        """
        return cls.PathIdentifierRe.match(path)

    # id { - id} * regexp, with no spaces
    FilePathIdentifierRE = re.compile(
        r"""^[a-zA-Z]\w*   # identifier
                                    (?:-[a-zA-Z]\w*)*  # sequence of ('-' identifier)
                                    $""",
        re.ASCII | re.VERBOSE,
    )

    @classmethod
    def is_valid_file_path(cls, path: str) -> bool:
        """Checks if *path* is a valid file path identifier, i.e.
        *id {- id}*, with no possible spaces around '-'.

        The path string is the basename of a module or an instance file.

        Parameters
        ----------
        path : str
            String containing the path identifier.

        Returns
        -------
        bool
            True when path is valid.
        """
        return cls.FilePathIdentifierRE.match(path)

    @property
    def is_valid(self) -> bool:
        """True when path is a sequence of Identifier."""
        return self._is_valid

    @property
    def is_protected(self) -> bool:
        """True when path is from a protected source, i.e., a string."""
        return not self.is_valid

    @property
    def ids(self) -> Union[List[Identifier], str]:
        """PathId as a list of Identifier, or a string if protected."""
        return self._ids

    @property
    def as_string(self) -> str:
        """Computes name by joining name parts with '::'."""
        return self._ids if self.is_protected else "::".join([p.value for p in self._ids])

    @property
    def name(self):
        """Name part, that is the last item of a Path id."""
        return self._ids if self.is_protected else self._ids[-1].value

    @property
    def path(self) -> List[Identifier]:
        """The path without the name at the end."""
        return self._ids if self.is_protected else [p.value for p in self._ids][0:-2]

    @property
    def pragmas(self) -> List[Pragma]:
        """Pragmas associated with the path_id."""
        return [] if self.is_protected else self._ids[0].pragmas

    def __str__(self) -> str:
        if self.is_protected:
            return Markup.to_str(self.path)
        if self.pragmas:
            pragmas = " ".join(str(p) for p in self.pragmas) + " "
        else:
            pragmas = ""
        return f"{pragmas}{self.as_string}"


class ModuleItem(SwanItem):
    """Base class for module body item or module interface item"""

    def __init__(self) -> None:
        super().__init__()


class Declaration(SwanItem):
    """Base class for declarations."""

    def __init__(self, id: Identifier) -> None:
        super().__init__()
        self._id = id

    @property
    def identifier(self) -> Identifier:
        """Language item identifier."""
        return self._id

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        if self.owner is None:
            raise ScadeOneException("No owner")
        path = self.owner.get_full_path()
        id_str = self.identifier.value
        return f"{path}::{id_str}"


class Expression(SwanItem):
    """Base class for expressions."""

    def __init__(self) -> None:
        super().__init__()


class TypeExpression(SwanItem):
    """Base class for type expressions."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def is_defined(self) -> bool:
        """True if type expression is a predefined type"""
        return False


class GroupTypeExpression(SwanItem):
    """Base class for group type expressions."""

    def __init__(self) -> None:
        super().__init__()


class Luid(SwanItem):
    """Class for LUID support: '#' is not kept if passed to the constructor."""

    LuidRE = re.compile(r"#?\w[-\w]*$")

    def __init__(self, luid: str) -> None:
        super().__init__()
        self._luid = luid[1:] if luid[0] == "#" else luid

    @property
    def value(self) -> str:
        """Luid value as a string."""
        return self._luid

    @staticmethod
    def is_valid(luid: str) -> bool:
        """True when a LUID is # LUID_CHAR+ with LUID_CHAR = ALPHANUMERIC | -."""
        return Luid.LuidRE.match(luid)

    def __str__(self) -> str:
        return "#" + self.value


class Variable(SwanItem):
    """Base class for Variable and ProtectedVariable."""

    def __init__(self) -> None:
        super().__init__()


class Equation(SwanItem):
    """Base class for equations."""

    def __init__(self) -> None:
        super().__init__()


# =============================================
# Protected Items
# =============================================


class ProtectedItem(SwanItem):
    """Base class for protected data. A protected data
    is a piece of Swan code enclosed between markups, mostly to store
    syntactically incorrect code. A protected data is enclosed within the pair
    ``{markup%`` .. ``%markup}``, where *markup* is defined by the
    regular expression: ['a'-'z' 'A'-'Z' 0-9 _]*.

    See :py:class:`Markup` for existing markups.
    """

    def __init__(self, data: str, markup: Optional[str] = Markup.Syntax) -> None:
        super().__init__()
        self._markup = markup
        self._data = data

    @property
    def is_protected(self):
        """Tells if item is syntactically protected and provided as a string."""
        return True

    def has_markup(self, markup: str) -> bool:
        """Checks if protected data has the specified *markup*.

        Parameters
        ----------
        markup : str
            String markup.

        Returns
        -------
        result: bool
            True when instance markup is same as parameter.
        """
        return self._markup == markup

    @property
    def data(self) -> str:
        """Protected data between markups.

        Returns
        -------
        str
            Protected data.
        """
        return self._data

    @property
    def markup(self) -> str:
        """Protection markup.

        Returns
        -------
        str
            Markup string.
        """
        return self._markup

    def __str__(self) -> str:
        return Markup.to_str(self.data, markup=self.markup)


def to_str_comma_list(l: List[Any]) -> str:
    """Generates a string which is the join of a list item
       separated by a comma.

    Parameters
    ----------
    l : List[Any]
        A list which items supports the str() function.

    Returns
    -------
    str
        resulting string
    """
    return ", ".join([str(i) for i in l])


def to_str_semi_list(l: List[Any]) -> str:
    """Generates a string which is the join of a list items
       separated by a semicolon.

    Parameters
    ----------
    l : List[Any]
        A list which items supports the str() function.

    Returns
    -------
    str
        Resulting string.
    """
    return "; ".join([str(i) for i in l])
