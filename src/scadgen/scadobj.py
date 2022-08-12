from __future__ import annotations
import contextlib
import abc
from typing import Generator, Optional

# The top level global context object.
_GENSCAD_GLOBAL_CONTEXT = None


def arg_value_to_str(v):
    '''Convert from Python to OpenSCAD representation.'''
    if v == True:
        return 'true'
    elif v == False:
        return 'false'
    elif isinstance(v, str):
        return '"' + str(v) + '"'
    else:
        return str(v)


def format_openscad_decl(keyword, depth, args, kwargs):
    '''Format an OpenSCAD keyword and args.'''
    str_args = [arg_value_to_str(a) for a in args]
    str_kwargs = [f'{k}={arg_value_to_str(v)}' for k, v in kwargs.items()]
    args = ', '.join(str_args+str_kwargs)
    return '  '*(depth-1) + f'{keyword}({args})'


def print_tree(o):
    '''Print the object tree rooted at a context object.'''
    print('  '*o.depth() + str(repr(o)))
    try:
        for module in o.modules:
            print_tree(module)
    except AttributeError:
        pass
    try:
        for child in o.objs:
            print_tree(child)
    except AttributeError:
        # ScadObj does not have a .objs member.
        pass


class ScadEntity(abc.ABC):
    '''Parent class for any object that generates an OpenSCAD statement.'''
    parent_entity: Optional[ScadEntity] = None

    def gen(self) -> str:
        lines = list(self._generate())
        # lines = [l + ' // depth: ' + str(self.depth()) for l in lines]
        return '\n'.join(lines)

    @abc.abstractmethod
    def _generate() -> Generator[str, None, None]:
        raise NotImplementedError()

    def depth(self):
        if self.parent_entity is None:
            return 0
        else:
            return 1 + self.parent_entity.depth()


class ScadContext(contextlib.AbstractContextManager, ScadEntity):
    '''Context manager.'''
    _NAME = '???'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.objs = []
        self.modules = []

    def __enter__(self):
        global _GENSCAD_GLOBAL_CONTEXT
        self.parent_entity = _GENSCAD_GLOBAL_CONTEXT
        if self.parent_entity is not None:
            self.parent_entity.add_obj(self)
        _GENSCAD_GLOBAL_CONTEXT = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global _GENSCAD_GLOBAL_CONTEXT
        _GENSCAD_GLOBAL_CONTEXT = self.parent_entity
        return False

    def __repr__(self) -> str:
        return(f'ScadContext_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def _generate(self) -> Generator[str, None, None]:
        for m in self.modules:
            yield m.gen()
        for o in self.objs:
            yield o.gen()

    def add_obj(self, obj: ScadEntity):
        self.objs.append(obj)

    def add_module(self, module: ScadModule):
        if self.parent_entity:
            self.parent_entity.add_module(module)
        else:
            if module._NAME not in [m._NAME for m in self.modules]:
                self.modules.append(module)
                module.parent_entity = self


class ScadModule(ScadContext):
    # TODO: Module parameters.
    def __init__(self, name, *args, **kwargs):
        super(ScadModule, self).__init__(*args, **kwargs)
        self._NAME = name
        self.parent_entity = _GENSCAD_GLOBAL_CONTEXT
        self.obj_cls = define_ScadObj(self._NAME)

    def __repr__(self) -> str:
        return(f'ScadModule_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def __call__(self, *args, **kwargs):
        # Calling a module inserts a ScadObj with that name.
        self.obj_cls(*args, **kwargs)
        # We also need to make sure the module and its dependencies are registered.
        _GENSCAD_GLOBAL_CONTEXT.add_module(self)
        for m in self.modules:
            _GENSCAD_GLOBAL_CONTEXT.add_module(m)

    def _generate(self) -> Generator[str, None, None]:
        yield '  ' * (self.depth()-1) + f'module {self._NAME}() {{'
        for o in self.objs:
            yield o.gen()
        yield '  ' * (self.depth()-1) + '}'


class ScadOperation(ScadContext):
    '''An OpenSCAD operation that acts on objects in its brace block.'''

    def __init__(self, *args, **kwargs):
        global _GENSCAD_GLOBAL_CONTEXT
        if not _GENSCAD_GLOBAL_CONTEXT:
            raise MissingScadContextException('No enclosing ScadContext.')
        super(ScadOperation, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.is_nested = False

    def __repr__(self) -> str:
        return(f'ScadOperation_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def _generate(self) -> Generator[str, None, None]:
        yield format_openscad_decl(self._NAME, self.depth(), self.args, self.kwargs) + ' {'
        for o in self.objs:
            yield o.gen()
        yield '  ' * (self.depth()-1) + '}'

    def __add__(self, o: ScadOperation):
        return ScadCompositeOperation(self, o)


class ScadCompositeOperation(ScadOperation):
    # Enables composite operations using '+' shorthand.
    def __init__(self, a, b, *args, **kwargs):
        super(ScadCompositeOperation, self).__init__(*args, **kwargs)
        self.a = a
        self.b = b
        self.a.objs = [self.b]
        self.b.parent_entity = self.a
        self.last = self.b

    def __repr__(self) -> str:
        return(f'ScadCompositeOperation({self.a}, {self.b})(args={self.args}, kwargs={self.kwargs})')

    def __add__(self, o: ScadOperation):
        self.last.add_obj(o)
        o.parent_entity = self.last
        self.last = o
        return self

    def add_obj(self, obj: ScadEntity):
        return self.b.add_obj(obj)

    def __enter__(self):
        global _GENSCAD_GLOBAL_CONTEXT
        self.a.parent_entity = _GENSCAD_GLOBAL_CONTEXT
        if self.a.parent_entity is not None:
            self.a.parent_entity.add_obj(self.a)
        _GENSCAD_GLOBAL_CONTEXT = self.last
        return self.last

    def __exit__(self, exc_type, exc_value, traceback):
        global _GENSCAD_GLOBAL_CONTEXT
        _GENSCAD_GLOBAL_CONTEXT = self.a.parent_entity
        return False


class ScadObj(ScadEntity):
    '''An OpenSCAD object, terminated by a semicolon (no brace block).'''
    _NAME = '???'

    def __init__(self, *args, **kwargs):
        global _GENSCAD_GLOBAL_CONTEXT
        if not _GENSCAD_GLOBAL_CONTEXT:
            raise MissingScadContextException('No enclosing ScadContext.')
        self.args = args
        self.kwargs = kwargs
        _GENSCAD_GLOBAL_CONTEXT.add_obj(self)
        self.parent_entity = _GENSCAD_GLOBAL_CONTEXT

    def __repr__(self) -> str:
        return(f'ScadObj_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def _generate(self) -> Generator[str, None, None]:
        yield format_openscad_decl(self._NAME, self.depth(), self.args, self.kwargs) + ';'


def define_ScadOperation(name):
    '''Helper function to define a named ScadOperation.'''
    class _ScadOperation(ScadOperation):
        _NAME = name
    return _ScadOperation


def define_ScadObj(name):
    '''Helper function to define a named ScadObj.'''
    class _ScadObj(ScadObj):
        _NAME = name
    return _ScadObj


class MissingScadContextException(Exception):
    pass
