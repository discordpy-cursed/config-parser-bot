from __future__ import annotations

import importlib
import types
import typing

if typing.TYPE_CHECKING:
    import importlib.util
    from importlib.machinery import ModuleSpec


class ModuleError(Exception):
    @typing.overload
    def __init__(self, message: str):
        ...

    @typing.overload
    def __init__(
        self,
        message: str,
        *,
        module: types.ModuleType | None = None,
        spec: ModuleSpec | None = None,
        original: Exception | None = None,
    ):
        ...

    def __init__(
        self,
        message: str,
        *,
        module: types.ModuleType | None = None,
        spec: ModuleSpec | None = None,
        original: Exception | None = None,
    ):
        super().__init__(message)

        self.message = message
        self.original = self.__cause__ = original

        if not module and spec:
            self.spec = spec
            self.module: types.ModuleType = importlib.util.module_from_spec(spec)
        elif module and not spec:
            self.module = module
            self.spec = importlib.util.find_spec(module.__name__)
        elif module and spec:
            self.module = module
            self.spec = spec


class ModuleNotFound(ModuleError):
    pass


class ModuleAlreadyLoaded(ModuleError):
    pass


class ModuleFailed(ModuleError):
    pass
