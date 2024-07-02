# Copyright (c) 2023-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
The information module handles the information provided in
a module body file or a module interface file after the
**__END__** token.

The information is given as a JSON array which leads to Python classes.
"""
from typing import Union, Optional
from collections import defaultdict


class InfoElement:
    """Class to store graphical information"""
    def __init__(self, name, data):
        self._data = defaultdict(dict)
        self._data.update(data)
        self._name = name

    @property
    def name(self) -> str:
        """Element name"""
        return self._name

    @property
    def children(self) -> dict:
        """Element children"""
        return self._data['Children']

    @property
    def properties(self) -> dict:
        """Element children"""
        return self._data['Properties']

class ModelTree(InfoElement):
    """Class handling the *layout* information, that is the graphical
       information"""
    Key = 'ModelTree'

    def __init__(self, info_data):
        super().__init__(ModelTree.Key, info_data)

    @property
    def version(self) -> Union[str, None]:
        """Version of ModelTree format"""
        if 'version' not in self.properties:
            return None
        return self.properties['version']


class Information:
    """Class to gather JSON information at end of a .swan/.swani

       Supports:

       - __getitem__: information['key']. If 'key' does not exist, create
                      an entry with a default dictionary
       - __contains__ : 'key' in information

    """
    def __init__(self, dictionary: Optional[dict] = None) -> None:
        self._info = defaultdict(dict)
        if dictionary:
            self._info.update(dictionary)

    @property
    def has_information(self) -> bool:
        """True when some information is available"""
        return bool(self._info)

    def __contains__(self, key: str):
        return key in self._info

    def __getitem__(self, key: str):
        """Return information with key *key*"""
        return self._info[key]

    @property
    def model_tree(self) -> ModelTree:
        "ModelTree information"

        if ModelTree.Key in self._info:
            return ModelTree(self._info[ModelTree.Key])
        return None
