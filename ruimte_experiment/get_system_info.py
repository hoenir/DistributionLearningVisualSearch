import platform
from pyglet.gl import gl_info as info

print info.get_renderer()
cpu_info = cpu_info.get_cpu_info()

sf = open('sysinfo.txt', 'w+')
sf.write('Version: ' + platform.python_version() + "\n")
sf.write('Compiler: ' + platform.python_compiler() + "\n")
sf.write('Build: ' + " ".join(platform.python_build()) + "\n")
sf.write('Normal: ' + platform.platform() + "\n")
sf.write('Aliased: ' + platform.platform(aliased=True) + "\n")
sf.write('Terse: ' + platform.platform(terse=True) + "\n")
sf.write('uname: ' + " ".join(platform.uname()) + "\n")
sf.write('system: ' + platform.system() + "\n")
sf.write('node: ' + platform.node() + "\n")
sf.write('release: ' + platform.release() + "\n")
sf.write('version: ' + platform.version() + "\n")
sf.write('machine: ' + platform.machine() + "\n")
sf.write('processor: ' + platform.processor() + "\n")
sf.write('CPU: %s \n' %cpu_info['brand'])
sf.close()
