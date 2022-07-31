import unittest
import textwrap
import scadgen as s


class TestContext(unittest.TestCase):
    def test_context_basic(self):
        '''Test that we can enter/exit a context.'''
        with s.ScadContext():
            pass

    def test_basic_obj(self):
        '''Basic usage.'''
        with s.ScadContext() as model:
            s.cube(size=[10, 10, 10], center=False)
            with s.translate([100, 100, 100]):
                s.cube(size=[20, 20, 20], center=False)
        output = model.gen()
        self.assertEqual(output, textwrap.dedent('''\
            cube(size=[10, 10, 10], center=False);
            translate([100, 100, 100]) {
              cube(size=[20, 20, 20], center=False);
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
            cube(size=[25, 25, 25], center=False);
            translate([100, 0, 0]) {
              cube(size=[20, 20, 20], center=False);
              cylinder(100, r=5, center=True);
            }
            translate([200, 0, 0]) {
              cube(size=[20, 20, 20], center=False);
              cylinder(100, r=5, center=True);
            }
            translate([300, 0, 0]) {
              cube(size=[20, 20, 20], center=False);
              cylinder(100, r=5, center=True);
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
              cylinder(10, r=16, center=True);
              translate([0, 0, -10]) {
                cylinder(30, r=8, center=True);
              }
            }
            translate([200, 0, 0]) {
              cylinder(10, r=16, center=True);
              translate([0, 0, -10]) {
                cylinder(30, r=8, center=True);
              }
            }
            translate([300, 0, 0]) {
              cylinder(10, r=16, center=True);
              translate([0, 0, -10]) {
                cylinder(30, r=8, center=True);
              }
            }'''))
