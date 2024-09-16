from .FunctionalSupport import Unfinished, RASPTypeError, tokens_asis, \
    tokens_str, tokens_int, tokens_bool, tokens_float, indices
from .Evaluator import RASPFunction


class UndefinedVariable(Exception):
    def __init__(self, varname):
        super().__init__("Error: Undefined variable: "+varname)


class ReservedName(Exception):
    def __init__(self, varname):
        super().__init__("Error: Cannot set reserved name: "+varname)


class Environment:
    def __init__(self, parent_env=None, name=None, stealing_env=None):
        self.variables = {}
        self.name = name
        self.parent_env = parent_env
        self.stealing_env = stealing_env
        self.base_setup()  # nested envs can have them too. makes life simpler,
        # instead of checking if they have the constant_variables etc in get.
        # bit heavier on memory but no one's going to use this language for big
        # nested stuff anyway
        self.storing_in_constants = False

    def base_setup(self):
        self.constant_variables = {"tokens_asis": tokens_asis,
                                   "tokens_str": tokens_str,
                                   "tokens_int": tokens_int,
                                   "tokens_bool": tokens_bool,
                                   "tokens_float": tokens_float,
                                   "indices": indices,
                                   "True": True,
                                   "False": False}
        self.reserved_words = ["if", "else", "not", "and", "or", "out", "def",
                               "return", "range", "for", "in", "zip", "len",
                               "get"] + list(self.constant_variables.keys())

    def snapshot(self):
        res = Environment(parent_env=self.parent_env,
                          name=self.name, stealing_env=self.stealing_env)

        def carefulcopy(val):
            if isinstance(val, Unfinished) or isinstance(val, RASPFunction):
                return val  # non mutable, at least not through rasp commands
            elif (isinstance(val, float) or isinstance(val, int) or
                  isinstance(val, str) or isinstance(val, bool)):
                return val  # non mutable
            elif isinstance(val, list):
                return [carefulcopy(v) for v in val]
            else:
                raise RASPTypeError("environment contains element that is " +
                                    "not unfinished, rasp function, float, " +
                                    "int, string, bool, or list? :", val)
        res.constant_variables = {d: carefulcopy(
            self.constant_variables[d]) for d in self.constant_variables}
        res.variables = {d: carefulcopy(
            self.variables[d]) for d in self.variables}
        return res

    def make_nested(self, names_vars=[]):
        res = Environment(self, name=str(self.name) + "'")
        for n, v in names_vars:
            res.set_variable(n, v)
        return res

    def get_variable(self, name):
        if name in self.constant_variables:
            return self.constant_variables[name]
        if name in self.variables:
            return self.variables[name]
        if self.parent_env is not None:
            return self.parent_env.get_variable(name)
        raise UndefinedVariable(name)

    def _set_checked_variable(self, name, val):
        if self.storing_in_constants:
            self.constant_variables[name] = val
            self.reserved_words.append(name)
        else:
            self.variables[name] = val

    def set_variable(self, name, val):
        if name in self.reserved_words:
            raise ReservedName(name)

        self._set_checked_variable(name, val)
        if self.stealing_env is not None:
            if name.startswith("_") or name == "out":  # things we don't want
                # to steal
                return
            self.stealing_env.set_variable(name, val)

    def set_out(self, val):
        self.variables["out"] = val
