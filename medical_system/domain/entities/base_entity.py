from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BaseEntity:
    # En Python 3.13+, los campos sin valor predeterminado deben ir primero
    # Por eso movemos id al final con un valor por defecto None
    
    def __post_init__(self):
        # Inicializamos el ID si no está definido
        if not hasattr(self, 'id'):
            self.id = None
    
    id: Optional[int] = field(default=None, init=False)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id is not None and self.id == other.id
    
    def __hash__(self) -> int:
        return hash((self.__class__, self.id))
