# scadgen

A Python library for generating OpenSCAD 3D models.

## Installation

```shell
$ pip install scadgen
```

## Usage

A model starts life as a `ScadContext` context manager. We call some functions to add objects to the context, and then call `gen()` to generate the model:

```python
import scadgen as s  # Not repeated in subsequent examples for brevity.
with s.ScadContext() as model:
    s.cube(size=[10, 10, 10], center=False)
output = model.gen()
```

Output:

```
cube(size=[10, 10, 10], center=false);
```

### Operations are contexts

Here, we nest a `cube` inside a `translate` context:

```python
with s.ScadContext() as model:
    s.cube(size=[10, 10, 10], center=False)
    with s.translate([100, 100, 100]):
        s.cube(size=[20, 20, 20], center=False)
output = model.gen()
```

Output:

```
cube(size=[10, 10, 10], center=false);
translate([100, 100, 100]) {
  cube(size=[20, 20, 20], center=false);
}
```

### Operations can be nested

```python
with s.ScadContext() as model:
    with s.translate([100, 100, 100]):
        s.cube(size=[10, 10, 10], center=False)
        with s.translate([50, 50, 50]):
          s.cube(size=[20, 20, 20], center=False)
output = model.gen()
```

Output:

```
translate([100, 100, 100]) {
  cube(size=[10, 10, 10], center=false);
  translate([50, 50, 50]) {
    cube(size=[20, 20, 20], center=false);
  }
}
```

### Using Python loops

```python
with s.ScadContext() as model:
    s.cube(size=[25, 25, 25], center=False)
    for x in [100, 200, 300]:
        with s.translate([x, 0, 0]):
            s.cube(size=[20, 20, 20], center=False)
            s.cylinder(100, r=5, center=True)
output = model.gen()
```

Output:

```
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
```

### Using Python functions

```python
def helper_fn():
    s.cylinder(10, r=16, center=True)
    with s.translate([0, 0, -10]):
        s.cylinder(30, r=8, center=True)

with s.ScadContext() as model:
    for x in [100, 200, 300]:
        with s.translate([x, 0, 0]):
            helper_fn()
output = model.gen()
```

Output:

```
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
}
```

### Operator composition

Operations can be composed with the `+` operator. These two code snippets produce the same model output.

```python
with s.ScadContext() as model1:
    with s.translate([1, 1, 1]):
        with s.translate([2, 2, 2]):
            with s.translate([3, 3, 3]):
                s.cube()
```

```python
with s.ScadContext() as model2:
    with s.translate([1, 1, 1]) + s.translate([2, 2, 2]) + s.translate([3, 3, 3]):
        s.cube()
```
