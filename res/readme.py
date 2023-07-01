
import sys, inspect, re, subprocess
sys.path.append('.')

def run(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f'{command}\n{result.stdout.rstrip()}'


def generate_docs(package, data=None, classname=None, text=[]):
    if data is None:
        __import__(package)
        mod = sys.modules[package]
        fn = lambda d: f'|{d}' if d[0].isupper() else d
        data = { k: getattr(mod, k) for k in sorted(dir(mod), key=fn) if k[0] != '_' }
    for k, fn in data.items():
        if k == '__module__': continue
        if k == '__weakref__': continue
        if k == '__dict__': continue
        if isinstance(fn, type):
            generate_docs(package, fn.__dict__, k, text)
        else:
            if not fn.__doc__:
                continue
            if isinstance(fn, property):
                text.append(f'<code>{classname}.<b>{k}</b></code>') # property
            else:
                signature = inspect.signature(fn)
                if k == '__init__':  # constructor
                    text.append(f'<code>class {package}.<b>{classname}</b>{signature}</code>  ')
                elif classname is None: # function
                    text.append(f'<code>{package}.<b>{k}</b>{signature}</code>  ')
                else:  # method
                    text.append(f'<code>{classname}.<b>{k}</b>{signature}</code>  ')
            inbody = True
            for ln in fn.__doc__.strip().splitlines():
                m_param = re.search(':param +(\w+) +(.*)', ln)
                m_return = re.search(':return +(.*)', ln)
                if m_param or m_return:
                    if inbody: text[-1] += '  '
                    inbody = False
                if m_param:
                    text.append(f'**{m_param.group(1)}** {m_param.group(2)}  ')
                elif m_return:
                    text.append(f'**returns** {m_return.group(1)}  ')
                else:
                    text.append(ln.strip())
            text.append('')
            if k == '__init__':
                text.append(f'Instances of the <code>{package}.<b>{classname}</b></code> class have the following methods:   ')
                text.append('')
    text = [ ln.replace('_', '\_') for ln in text ]
    return '\n'.join(text)


print(f"""\

![](res/cubeminus.png)

# csgstep

A constructive solid geometry python library for OpenCASCADE.  The API is based on the OpenSCAD and SolidPython API.  The library can read and write STEP files.

## Examples

Create a cube that has a sphere subtracted from it:

```python
from csgstep import cube, sphere
solid = cube(center=True) - sphere(.65)
solid.write_stl('cube.stl')    
solid.write_step('cube.stp')    
```

Create a helix:

```python
from csgstep import circle
pitch = .3
solid = circle(.1)
solid = solid.helix_extrude(r=8, h=3.1 * pitch, pitch=pitch, center=True)
solid.write_stl('helix.stl')    
solid.write_step('helix.stp')    
```
        
Create a pipe:

```python
from csgstep import circle
solid = circle(.2).spline_extrude([(0, 0, 0),(0, 1, 2),(0, 2, 3)])
solid.write_stl('pipe.stl')    
solid.write_step('pipe.stp')    
```

## Dependencies

The library depends on pythonocc-core and numpy.  To install pythonocc-core, I used anaconda and ran "conda install -c conda-forge pythonocc-core".

To install csgstep run "pip install ." in this directory, or the equivalent.  It will bring in numpy.

## Notes

All method functions (not properties) of Solid return a new Solid object.  So remember to always 
assign the result of a method, otherwise it will be lost.

The rotate method here is different from the OpenSCAD rotate method.  The first argument is the angle to rotate and the second argument is the vector to rotate around.

I also added a new extrude method called spline_extrude.  It takes a list of points as its only argument.  These points are converted into a cubic spline which is then used to extrude a solid.  An example of spline_extrude is the helix_extrude method which creates a helix from a solid.

# csgstep API

{generate_docs('csgstep')}
""")


