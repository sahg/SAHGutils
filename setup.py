import os
import subprocess
from distutils.core import setup

try:
    if os.path.exists(".git"):
        s = subprocess.Popen(["git", "rev-parse", "HEAD"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = s.communicate()[0]
        GIT_REVISION = out.strip()
    else:
        GIT_REVISION = ""
except WindowsError:
    GIT_REVISION = ""

FULL_VERSION = '0.0.1dev'
if "dev" in FULL_VERSION:
    RELEASED = False
    VERSION = FULL_VERSION+GIT_REVISION[:7]
else:
    RELEASED = True
    VERSION = FULL_VERSION

def generate_version_py(filename):
    cnt = """\
# This file was autogenerated
version = '%s'
git_revision = '%s'
"""
    cnt = cnt % (VERSION, GIT_REVISION)

    f = open(filename, "w")
    try:
        f.write(cnt)
    finally:
        f.close()

setup(
    name='SAHGutils',
    version=VERSION,
    author='Scott Sinclair',
    author_email='scott.sinclair.za@gmail.com',
    packages=['sahgutils'],
    license='LICENSE.txt',
    description='Useful tools for data analysis and plots.',
    long_description=open('README.txt').read(),
)

if __name__ == '__main__':
    generate_version_py("sahgutils/__dev_version.py")
