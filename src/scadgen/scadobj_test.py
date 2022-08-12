import unittest
import textwrap
import scadgen as s


class TestModule(unittest.TestCase):

    def test_basic_module(self):
        '''Basic module usage.'''
        with s.ScadModule(name='cylcube') as cylcube:
            # A module comprising a cylinder with a cube stacked on top of it
            s.cylinder(20, r=20)
            with s.translate([0, 0, 25]):
                s.cube(size=[10, 10, 10], center=True)
        with s.ScadContext() as model:
            cylcube()
            with s.translate([100, 0, 0]):
                cylcube()
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            module cylcube() {
              cylinder(20, r=20);
              translate([0, 0, 25]) {
                cube(size=[10, 10, 10], center=true);
              }
            }
            cylcube();
            translate([100, 0, 0]) {
              cylcube();
            }'''))

    def test_dependent_module(self):
        '''A module that depends on another module.'''
        with s.ScadModule(name='cylcube') as cylcube:
            s.cylinder(20, r=20)
            with s.translate([0, 0, 25]):
                s.cube(size=[10, 10, 10], center=True)
        with s.ScadModule(name='doublecylcube') as doublecylcube:
            cylcube()
            with s.translate([0, 0, 30]):
                cylcube()
        with s.ScadContext() as model:
            doublecylcube()
            with s.translate([100, 0, 0]):
                doublecylcube()
        output = model.gen()
        # print('_____ model tree _____ ')
        # s.print_tree(model)
        # print('_____ model output _____ ')
        # print(output)
        self.assertEqual(output, textwrap.dedent('''\
            module doublecylcube() {
              cylcube();
              translate([0, 0, 30]) {
                cylcube();
              }
            }
            module cylcube() {
              cylinder(20, r=20);
              translate([0, 0, 25]) {
                cube(size=[10, 10, 10], center=true);
              }
            }
            doublecylcube();
            translate([100, 0, 0]) {
              doublecylcube();
            }'''))


class TestContext(unittest.TestCase):

    def test_context_basic(self):
        '''Test that we can enter/exit a context.'''
        with s.ScadContext():
            pass

    def test_object_no_context(self):
        with self.assertRaises(s.MissingScadContextException):
            s.cube(size=[10, 10, 10], center=False)

    def test_operation_no_context(self):
        with self.assertRaises(s.MissingScadContextException):
            with s.translate([10, 10, 10]):
                pass

    def test_basic_obj(self):
        '''Basic usage.'''
        with s.ScadContext() as model:
            s.cube(size=[10, 10, 10], center=False)
            with s.translate([100, 100, 100]):
                s.cube(size=[20, 20, 20], center=False)
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            cube(size=[10, 10, 10], center=false);
            translate([100, 100, 100]) {
              cube(size=[20, 20, 20], center=false);
            }'''))

    def test_basic2_obj(self):
        '''Slightly more complex basic usage.'''
        with s.ScadContext() as model:
            s.cube(size=[25, 25, 25], center=False)
            for x in [100, 200, 300]:
                with s.translate([x, 0, 0]):
                    s.cube(size=[20, 20, 20], center=False)
                    s.cylinder(100, r=5, center=True)
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            cube(size=[25, 25, 25], center=false);
            translate([100, 0, 0]) {
              cube(size=[20, 20, 20], center=false);
              cylinder(100, r=5, center=true);
            }
            translate([200, 0, 0]) {
              cube(size=[20, 20, 20], center=false);
              cylinder(100, r=5, center=true);
            }
            translate([300, 0, 0]) {
              cube(size=[20, 20, 20], center=false);
              cylinder(100, r=5, center=true);
            }'''))

    def test_function_obj(self):
        '''Nested translates and a helper function.'''
        def helper_fn():
            s.cylinder(10, r=16, center=True)
            with s.translate([0, 0, -10]):
                s.cylinder(30, r=8, center=True)

        with s.ScadContext() as model:
            for x in [100, 200, 300]:
                with s.translate([x, 0, 0]):
                    helper_fn()
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            translate([100, 0, 0]) {
              cylinder(10, r=16, center=true);
              translate([0, 0, -10]) {
                cylinder(30, r=8, center=true);
              }
            }
            translate([200, 0, 0]) {
              cylinder(10, r=16, center=true);
              translate([0, 0, -10]) {
                cylinder(30, r=8, center=true);
              }
            }
            translate([300, 0, 0]) {
              cylinder(10, r=16, center=true);
              translate([0, 0, -10]) {
                cylinder(30, r=8, center=true);
              }
            }'''))


class TestValueconversion(unittest.TestCase):

    def test_value_conversion(self):
        '''Param value conversion from Python to OpenSCAD'''
        with s.ScadContext() as model:
            s.cube(size=[10, 10, 10], center=False,
                   some_str_arg='foo', some_float_arg=0.333)
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            cube(size=[10, 10, 10], center=false, some_str_arg="foo", some_float_arg=0.333);'''))

    def test_value_conversion_args(self):
        '''Param string conversion.'''
        with s.ScadContext() as model:
            with s.color("blue"):
                s.cube()
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            color("blue") {
              cube();
            }'''))


class TestCompositeOperation(unittest.TestCase):
    def test_context_add(self):
        '''Ability to use the + operator with ScadContexts as a shorthand.'''
        # The basic syntax, using nested contexts.
        with s.ScadContext() as model1:
            with s.translate([1, 1, 1]):
                with s.translate([2, 2, 2]):
                    with s.translate([3, 3, 3]):
                        s.cube()
        # Adding operations as a shorthand.
        with s.ScadContext() as model2:
            with s.translate([1, 1, 1]) + s.translate([2, 2, 2]) + s.translate([3, 3, 3]):
                s.cube()
        self.assertEqual(model1.gen(), model2.gen())
