from __future__ import annotations

import importlib
import types
import typing

if typing.TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


class ModuleError(Exception):
    @typing.overload
    def __init__(self, message: str, *, spec: ModuleSpec, original: Exception | None = None):
        ...

    @typing.overload
    def __init__(self, message: str, *, module: types.ModuleType, original: Exception | None = None):
        ...

    def __init__(
        self,
        message: str,
        *,
        module: types.ModuleType | None = None,
        spec: ModuleSpec | None,
        original: Exception | None = None,
    ):
        super().__init__(message)

        self.original = self.__cause__ = original

        if not module and spec:
            self.spec = spec
            self.module: types.ModuleType = importlib.util.module_from_spec(spec)
        elif module and not spec:
            self.module = module
            self.spec: ModuleSpec = importlib.util.find_spec(module.__name__)
        elif module and spec:
            self.module = module
            self.spec = spec


class ModuleNotFound(ModuleError):
    pass


class ModuleAlreadyLoaded(ModuleError):
    pass


class ModuleFailed(ModuleError):
    pass
