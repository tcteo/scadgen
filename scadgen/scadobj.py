import contextlib
import abc
from typing import Generator

# The top level global context object.
_GENSCAD_GLOBAL_CONTEXT = None


def format_openscad_decl(keyword, depth, args, kwargs):
    '''Format an OpenSCAD keyword and args.'''
    str_args = [str(a) for a in args]
    str_kwargs = [f'{k}={v}' for k, v in kwargs.items()]
    args = ', '.join(str_args+str_kwargs)
    return '  '*(depth-1) + f'{keyword}({args})'


def print_tree(o, level=0):
    '''Print the object tree rooted at a context object.'''
    print('  '*level + str(repr(o)))
    try:
        for child in o.objs:
            print_tree(child, level=level+1)
    except AttributeError:
        # ScadObj does not have a .objs member.
        pass


class ScadEntity(abc.ABC):
    '''Parent entity for any object that generates an OpenSCAD statement.'''

    def gen(self) -> str:
        return '\n'.join(list(self._generate()))

    @abc.abstractmethod
    def _generate() -> Generator[str, None, None]:
        raise NotImplementedError()


class ScadContext(contextlib.AbstractContextManager, ScadEntity):
    '''Context manager.'''
    _NAME = '???'

    def __init__(self, *args, **kwargs):
        self.depth = 0
        self.args = args
        self.kwargs = kwargs
        self.objs = []

    def __enter__(self):
        global _GENSCAD_GLOBAL_CONTEXT
        self.genscad_parent_obj = _GENSCAD_GLOBAL_CONTEXT
        if self.genscad_parent_obj is not None:
            self.genscad_parent_obj.add_obj(self)
            self.depth = self.genscad_parent_obj.depth+1
        _GENSCAD_GLOBAL_CONTEXT = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global _GENSCAD_GLOBAL_CONTEXT
        _GENSCAD_GLOBAL_CONTEXT = self.genscad_parent_obj
        return False

    def __repr__(self) -> str:
        return(f'ScadContext_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def add_obj(self, obj: ScadEntity):
        self.objs.append(obj)

    def _generate(self) -> Generator[str, None, None]:
        for o in self.objs:
            yield o.gen()


class ScadOperation(ScadContext):
    '''An OpenSCAD operation that acts on objects in its brace block.'''

    def __init__(self, *args, **kwargs):
        super(ScadOperation, self).__init__(*args, **kwargs)
        global _GENSCAD_GLOBAL_CONTEXT
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return(f'ScadOperation_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def _generate(self) -> Generator[str, None, None]:
        yield format_openscad_decl(self._NAME, self.depth, self.args, self.kwargs) + ' {'
        for o in self.objs:
            yield o.gen()
        yield '  ' * (self.depth-1) + '}'


class ScadObj(ScadEntity):
    '''An OpenSCAD object, terminated by a semicolon (no brace block).'''
    _NAME = '???'

    def __init__(self, *args, **kwargs):
        global _GENSCAD_GLOBAL_CONTEXT
        self.args = args
        self.kwargs = kwargs
        self.depth = _GENSCAD_GLOBAL_CONTEXT.depth+1
        _GENSCAD_GLOBAL_CONTEXT.add_obj(self)

    def __repr__(self) -> str:
        return(f'ScadObj_{self._NAME}(args={self.args}, kwargs={self.kwargs})')

    def _generate(self) -> Generator[str, None, None]:
        yield format_openscad_decl(self._NAME, self.depth, self.args, self.kwargs) + ';'


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
