from typing import Dict, Union, List, Any

Json = Union[dict, str, list]
_IBDict = Dict[str, Any]
_Items = Union[_IBDict, str]
Schema = Dict[str, Union[_IBDict, List[_Items], str]]
