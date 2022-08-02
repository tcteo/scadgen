from scadgen import scadobj

ScadContext = scadobj.ScadContext
ScadModule = scadobj.ScadModule
MissingScadContextException = scadobj.MissingScadContextException

circle = scadobj.define_ScadObj('circle')
square = scadobj.define_ScadObj('square')
polygon = scadobj.define_ScadObj('polygon')
text = scadobj.define_ScadObj('text')
projection = scadobj.define_ScadOperation('projection')

sphere = scadobj.define_ScadObj('sphere')
cube = scadobj.define_ScadObj('cube')
cylinder = scadobj.define_ScadObj('cylinder')
polyhedron = scadobj.define_ScadObj('polyhedron')
linear_extrude = scadobj.define_ScadOperation('linear_extrude')
rotate_extrude = scadobj.define_ScadOperation('rotate_extrude')

translate = scadobj.define_ScadOperation('translate')
rotate = scadobj.define_ScadOperation('rotate')
scale = scadobj.define_ScadOperation('scale')
resize = scadobj.define_ScadOperation('resize')
mirror = scadobj.define_ScadOperation('mirror')
multmatrix = scadobj.define_ScadOperation('multmatrix')
color = scadobj.define_ScadOperation('color')
offset = scadobj.define_ScadOperation('offset')
hull = scadobj.define_ScadOperation('hull')
minkowski = scadobj.define_ScadOperation('minkowski')

union = scadobj.define_ScadOperation('union')
difference = scadobj.define_ScadOperation('difference')
intersection = scadobj.define_ScadOperation('intersection')

print_tree = scadobj.print_tree
