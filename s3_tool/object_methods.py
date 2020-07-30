from enum import Enum


class ObjectMethods(str, Enum):
    key = "key"
    last_modified = "last_modified"
    size = "size"
    owner = "owner"
