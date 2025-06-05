from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.value:
            raise ValueError("Email cannot be empty")
        
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, self.value):
            raise ValueError("Invalid email format")

    def __str__(self) -> str:
        return self.value
