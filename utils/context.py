#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2022/12/20 14:47
# FileName: 全局上下文

from contextvars import ContextVar, Token
from typing import Any, Dict


class Globals:
    __slots__ = ("_vars", "_reset_tokens")

    _vars: Dict[str, ContextVar]
    _reset_tokens: Dict[str, Token]

    def __init__(self) -> None:
        object.__setattr__(self, "_vars", {})
        object.__setattr__(self, "_reset_tokens", {})

    def reset(self) -> None:
        for _name, var in self._vars.items():
            try:
                var.reset(self._reset_tokens[_name])
            # ValueError will be thrown if the reset() happens in
            # a different context compared to the original set().
            # Then just set to None for this new context.
            except ValueError:
                var.set(None)

    def _ensure_var(self, item: str) -> None:
        if item not in self._vars:
            self._vars[item] = ContextVar(f"globals_context:{item}", default=None)
            self._reset_tokens[item] = self._vars[item].set(None)

    def __getattr__(self, item: str, default_value) -> Any:
        return self._vars[item].get() if item in self._vars else default_value

    def __setattr__(self, item: str, value: Any) -> None:
        self._ensure_var(item)
        self._vars[item].set(value)


def set_args(args, value):
    context.__setattr__(args, value)


def get_args(args, default_value=None):
    return context.__getattr__(args, default_value)


def reset():
    context.reset()


context = Globals()
