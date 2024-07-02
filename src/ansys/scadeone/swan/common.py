# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains classes that are used by all the other
language-related modules.

It contains base classes for various language constructs.
"""
from abc import ABC
from collections import namedtuple
from enum import Enum, auto
from typing import List, Optional, Union, Any, Iterable
from typing_extensions import Self
import re

from ansys.scadeone.common.exception import ScadeOneException

# TODO: implement ANNOTATIONS
class SwanItem(ABC):
    """Base class for Scade objects"""
    def __init__(self) -> None:
        self._owner = None

    @property
    def owner(self) -> Self:
        """Owner of current Swan construct"""
        return self._owner

    @owner.setter
    def owner(self, owner: Self):
        """Set the owner of the Swan construct"""
        self._owner = owner

    @staticmethod
    def set_owner(owner: Self, items: Iterable[Self]):
        """Helper to set the owner of an Iterable of children of a construct"""
        for item in items:
            item.owner = owner

    def get_full_path(self) -> str:
        """Full path of Swan construct"""
        raise ScadeOneException(f"SwanItem.get_full_path(): not implemented for {type(self)}")

    @property
    def is_protected(self):
        """Tells if a construct item is syntactically protected with some markup
        and is stored as a string (without the markup)."""
        return False


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


class NumericRE:
    """Compiled regular expressions container. These expressions can be matched with
    some string and some expressions offers groups to extract parts.

    Attributes:

    TypedInteger: regular expressions for integers with post type (_i, _ui).
             Integer part is in the *value* group, type in the *type* group
             and size in *size* group

    TypeFloat: regular expression for floats with post type (_f).
           Mantissa is in the *mantissa* group, exponent in the *exp* group,
           type in the *type* group and size in *size* group

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
        """Match a string representing an integer and returns
        a description of that integer as a IntegerTuple.

        Parameters
        ----------
        string : str
            String representing an integer, with or without type information
        minus : bool
            True when the value is preceded with a '-' minus operator.

        Returns
        -------
        IntegerTuple or None
            If the string value matches NumericRE.TypedInteger pattern, an
            IntegerTuple is returned. It is a namedtuple with fields:

            - value: computed value,
            - is_bin, is_oct, is_hex, is_dec: flags set according to found type
            - is_signed: True when integer is signed
            - size: the size part.

            Note: if there is no type information, type is _i32
        """
        m = cls.TypedInteger.match(string)
        if not m:
            return None
        is_bin = m["value"].find("0b") != -1
        is_oct = m["value"].find("0o") != -1
        is_hex = m["value"].find("0x") != -1
        is_dec = not (is_bin or is_oct or is_hex)
        if m["type"]:
            print(m["type"])
            assert not (minus and m["type"] == "_ui")
            is_signed = m["type"] == "_i" or minus
            size = int(m["size"])
        else:
            is_signed = True
            size = 32
        value = -int(m["value"]) if minus else int(m["value"])
        return IntegerTuple(value, is_bin, is_oct, is_hex, is_dec, is_signed, size)

    @classmethod
    def is_integer(cls, string: str) -> bool:
        """Check whether a string is a Swan integer

        Parameters
        ----------
        string : str
            Integer value, as decimal, bin, octal, hexadecimal with
            or without type information

        Returns
        -------
        bool
            True when string is an integer
        """
        return cls.parse_integer(string) is not None

    @classmethod
    def parse_float(cls, string: str, minus: bool = False) -> Union[FloatTuple, None]:
        """Match a string representing a float and returns
        a description of that float as a FloatTuple.

        Parameters
        ----------
        string : str
            String representing an float, with or without type information
        minus : bool
            True when the value is preceded with a '-' minus operator.

        Returns
        -------
        FloatTuple or None
            If the string value matches NumericRE.TypedFloat pattern, an
            FloatTuple is returned. It is a namedtuple with fields:

            - value: computed value,
            - mantissa: the mantissa part
            - exp: the exponent part
            - size: the size part.

            Note: if there is no type information, type is _f32
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
        """Check whether a string is a Swan integer

        Parameters
        ----------
        string : str
            Integer value, as decimal, bin, octal, hexadecimal with
            or without type information

        Returns
        -------
        bool
            True when string is an integer
        """
        return cls.parse_float(string) is not None


class Markup:
    """Class defining the markups used by the Swan serialization."""
    NoMarkup = ""
    Syntax = "syntax"
    # syntax error in declaration, discriminate the declaration
    Var = "var"
    Group = "group"
    Sensor = "sensor"
    Const = "const"
    Type = "type"
    Use = "use"
    # operator signature in interface
    Signature = "signature"
    # user textual operator, or generic operator content
    Text = "text"
    # user textual operator with syntax error
    SyntaxText = "syntax_text"
    # empty body
    Empty = "empty"
    # protected instance id
    Inst = "inst"
    # operator expression
    OpExpr = "op_expr"
    # forward dimension
    Dim = "dim"

    @staticmethod
    def to_str(text: str,
               is_protected: bool = True,
               markup: str = None) -> str:
        """Return {markup%text%markup}"""
        if not is_protected:
            return text
        if markup is None:
            markup = Markup.Syntax
        return f"{{{markup}%{text}%{markup}}}"


class PredefinedTypes(Enum):
    """Predefined types"""
    Bool = auto()
    Char = auto()
    Int8 = auto()
    Int16 = auto()
    Int32 = auto()
    Int64 = auto()
    Uint8 = auto()
    Uint16 = auto()
    Uint32 = auto()
    Uint64 = auto()
    Float32 = auto()
    Float64 = auto()

    @staticmethod
    def to_str(value: Self):
        """Return the string corresponding to the PredefinedTypes value."""
        return value.name.lower()


class NumericKind(Enum):
    """Numeric kinds"""
    Numeric = auto()
    Integer = auto()
    Signed = auto()
    Unsigned = auto()
    Float = auto()

    @staticmethod
    def to_str(value: Self):
        return value.name.lower()

class Pragma:
    """Store a pragma"""
    PragmaRE = re.compile(r"pragma\s+(?P<key>\w+)\s(?P<val>.*)#end")

    def __init__(self, pragma: str) -> None:
        self._pragma = pragma

    def get_pragma(self) -> Union[dict, None]:
        """Extract pragma information as a tuple
           if pragma is valid, i.e.: #pragma key value#end

        Returns
        -------
            dict | None
            the dict {'key', 'value'} if pragma is valid, None else.
        """
        m = Pragma.PragmaRE.match(self._pragma)
        if not m:
            return None
        return {'key': m["key"], 'value': m["val"].strip()}

    def __str__(self) -> str:
        return self._pragma


# ========================================================
# Common Constructs, used by other constructs


class Identifier(SwanItem):
    """Class for identifier.

    An Identifier can be invalid if it has been protected while saving it
    for some reason. In that case, the property _is_valid_ is set to True.

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
            Identifier string
        pragmas : List[Pragma]
            List of pragmas
        comment : str, optional
            comment, can be multiline, by default None
        is_name : bool, optional
            True when Identifier is a name, aka 'Identifier
        """
        super().__init__()
        self._value = value
        self._pragmas = pragmas if pragmas else []
        self._comment = comment
        self._is_valid = Identifier.IdentifierRe.match(value) is not None
        self._is_name = is_name

    @property
    def is_valid(self) -> bool:
        """Return true when Identifier is valid."""
        return self._is_valid

    @property
    def is_protected(self) -> bool:
        """Return true when Identifier is valid."""
        return not self.is_valid

    @property
    def value(self) -> str:
        """Identifier as a string"""
        return f"'{self._value}" if self._is_name else self._value

    @property
    def is_name(self) -> bool:
        """Return true when Identifier is a name."""
        return self._is_name

    @property
    def pragmas(self) -> List[Pragma]:
        """List of pragmas (strings)"""
        return self._pragmas

    @property
    def comment(self) -> str:
        """Comment string"""
        return self._comment

    def __str__(self) -> str:
        if self.pragmas:
            pragmas = " ".join([str(p) for p in self.pragmas]) + " "
        else:
            pragmas = ""
        return f"{pragmas}{self.value}"


class PathIdentifier(SwanItem):
    """Path identifiers, i.e: P1::P2::Id
    The class manipulates the PathIdentifier as separate items.

    If the original path has been protected (given as a string) the property *is_valid*
    if False, and the path is considered to be a single string and *is_protected* is True

    path_id argument is:

    - a list of identifiers, for a valid path
    - a string if the path has been protected
    """

    # id { :: id} * regexp, with spaces included
    PathIdentifierRe = re.compile(
        r"""^[a-zA-Z]\w*   # identifier
                                  (?:\s*::\s*[a-zA-Z]\w*)*  # sequence of ('-' identifier)
                                  $""",
        re.ASCII | re.VERBOSE,
    )

    @classmethod
    def is_valid_path(cls, path: str) -> bool:
        """Check is *path* is a valid path identifier, i.e.
        *id {:: id}*, with possible spaces around '::'

        Parameters
        ----------
        path : str
            String containing the path identifier

        Returns
        -------
        bool
            True when path is valid
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
        """Check is *path* is a valid file path identifier, i.e.
        *id {- id}*, with no possible spaces around '-'.

        The path string is the basename of a module or an instance file.

        Parameters
        ----------
        path : str
            String containing the path identifier

        Returns
        -------
        bool
            True when path is valid
        """
        return cls.FilePathIdentifierRE.match(path)

    def __init__(self, path_id: Union[List[Identifier], str]) -> None:
        super().__init__()
        self._ids = path_id
        self._is_valid = isinstance(path_id, list)

    @property
    def is_valid(self) -> bool:
        """True when path is a sequence of Identifier"""
        return self._is_valid

    @property
    def is_protected(self) -> bool:
        """True when path is from a protected source, i.e. a string"""
        return not self.is_valid

    @property
    def ids(self) -> Union[List[Identifier], str]:
        """PathId as a list of Identifier, or a string if protected"""
        return self._ids

    @property
    def full_name(self):
        """Compute full name by joining name parts with '::'"""
        return self._ids if self.is_protected else "::".join([p.value for p in self._ids])

    @property
    def name(self):
        """Name part, that is the last item of a Path id"""
        return self._ids if self.is_protected else self._ids[-1].value

    @property
    def path(self) -> List[Identifier]:
        """The path without the name at the end"""
        return self._ids if self.is_protected else [p.value for p in self._ids][0:-2]

    @property
    def pragmas(self) -> List[Pragma]:
        """Pragmas associated with the path_id"""
        return [] if self.is_protected else self._ids[0].pragmas

    def __str__(self) -> str:
        if self.is_protected:
            return Markup.to_str(self.path)
        if self.pragmas:
            pragmas = " ".join(str(p) for p in self.pragmas) + " "
        else:
            pragmas = ""
        return f"{pragmas}{self.full_name}"


class Declaration(SwanItem):
    """Base class for declarations"""

    def __init__(self, id: Identifier) -> None:
        super().__init__()
        self._id = id

    @property
    def identifier(self) -> Identifier:
        """Language item identifier"""
        return self._id

    def get_full_path(self) -> str:
        """Full path of Swan construct"""
        if self.owner is None:
            raise ScadeOneException("No owner")
        path = self.owner.get_full_path()
        id_str = self.identifier.value
        return f"{path}::{id_str}"


class Expression(SwanItem):
    """Base class for expressions"""

    def __init__(self) -> None:
        super().__init__()


class TypeExpression(SwanItem):
    """Base class for type expressions"""

    def __init__(self) -> None:
        super().__init__()


class GroupTypeExpression(SwanItem):
    """Base class for group type expressions"""

    def __init__(self) -> None:
        super().__init__()


class Luid(SwanItem):
    """Class for LUID support
    '#' is not kept if passed to the constructor
    """
    LuidRE = re.compile(r"#?\w[-\w]*$")

    def __init__(self, luid: str) -> None:
        super().__init__()
        self._luid = luid[1:] if luid[0] == "#" else luid

    @property
    def value(self) -> str:
        """Luid value as a string"""
        return self._luid

    @staticmethod
    def is_valid(luid: str) -> bool:
        """True when a LUID is # LUID_CHAR+ with LUID_CHAR = ALPHANUMERIC | -"""
        return Luid.LuidRE.match(luid)

    def __str__(self) -> str:
        return "#" + self.value


class Variable(SwanItem):
    """Base class for Variable and ProtectedVariable"""

    def __init__(self) -> None:
        super().__init__()


class Equation(SwanItem):
    """Base class for equations"""

    def __init__(self) -> None:
        super().__init__()


class ScopeSection(SwanItem):
    """Base class for scopes"""

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def to_str(cls,
               section: str,
               items: List[Any],
               end: Optional[str] = ";") -> str:
        """Print *section* name with its list of *items*, one per line,
        ended with *sep* string"""
        item_str = "\n".join([f"    {item}{end}" for item in items])
        return f"{section}\n{item_str}"


class Scope(SwanItem):
    """Scope definition: *data_def* ::= *scope*, where *scope* ::= { {{*scope_section*}} }"""

    def __init__(self, scope_sections: List[ScopeSection]) -> None:
        super().__init__()
        self._sections = scope_sections

    @property
    def sections(self) -> List[ScopeSection]:
        """Scope sections"""
        return self._sections

    def __str__(self) -> str:
        sections = "\n".join([str(section) for section in self.sections])
        return f"{{\n{sections}\n}}"

# =============================================
# Protected Items
# =============================================


class ProtectedItem(SwanItem):
    """Base class for protected data"""

    def __init__(self, data: str, markup: Optional[str] = Markup.Syntax) -> None:
        super().__init__()
        self._markup = markup
        self._data = data

    @property
    def is_protected(self):
        """Tells if item is syntactically protected and provided as a string"""
        return True

    def has_markup(self, markup: str) -> bool:
        """Check is protected data has the given *markup*

        Parameters
        ----------
        markup : str
            String markup.

        Returns
        -------
        result: bool
            True when protected data has the same markup.
        """
        return self._markup == markup

    @property
    def data(self) -> str:
        """Protected data between markups

        Returns
        -------
        str
            Protected data
        """
        return self._data

    @property
    def markup(self) -> str:
        """Protection markup

        Returns
        -------
        str
            Markup string
        """
        return self._markup

    def __str__(self) -> str:
        return Markup.to_str(self.data, markup=self.markup)


def to_str_comma_list(l: List[Any]) -> str:
    """Generates a string which is the join of a list items
       separated by a comma.

    Parameters
    ----------
    l : List[Any]
        A list which items supports the str() function

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
        A list which items supports the str() function

    Returns
    -------
    str
        resulting string
    """
    return "; ".join([str(i) for i in l])
