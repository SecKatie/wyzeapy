from enum import Enum


class RunActionListRequestActionListItemActionKey(str, Enum):
    SET_MESH_PROPERTY = "set_mesh_property"

    def __str__(self) -> str:
        return str(self.value)
