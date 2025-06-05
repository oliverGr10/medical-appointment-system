from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BaseEntity:

    def __post_init__(self):
        if not hasattr(self, 'id'):
            self.id = None
    
    id: Optional[int] = field(default=None, init=False)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id is not None and self.id == other.id
    
    def __hash__(self) -> int:
        return hash((self.__class__, self.id))
