from typing import Any, Dict, Optional, cast

from pydantic import BaseModel

from dubdub import Token, dataclass


class Environment(BaseModel):
    values: Dict[str, Any] = {}
    enclosing: Optional["Environment"] = None

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def access(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values.get(name.lexeme)

        if self.enclosing is not None:
            return self.enclosing.access(name)

        raise RuntimeError(f"Undefined variable '{name.lexeme}'")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise RuntimeError(f"Undefined variable '{name.lexeme}'")

    def ancestor(self, distance: int) -> "Environment":
        environment: Optional["Environment"] = self
        for _ in range(distance):
            if environment is not None:
                environment = environment.enclosing
        return cast(Environment, environment)

    def get_at(self, distance: int, name: str) -> None:
        self.ancestor(distance).values.get(name, None)

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value
