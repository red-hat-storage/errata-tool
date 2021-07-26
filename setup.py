import os
import re
import subprocess
from setuptools import setup, find_packages, Command
try:
    # Python 2 backwards compat
    from __builtin__ import raw_input as input
except ImportError:
    pass

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme).read()


def read_module_contents():
    with open('errata_tool/__init__.py') as app_init:
        return app_init.read()


def read_spec_contents():
    with open('python-errata-tool.spec') as spec:
        return spec.read()


module_file = read_module_contents()
metadata = dict(re.findall(r"__([a-z]+)__\s*=\s*'([^']+)'", module_file))
version = metadata['version']


class BumpCommand(Command):
    """ Bump the __version__ number and commit all changes. """

    user_options = [('version=', 'v', 'version number to use')]

    def initialize_options(self):
        new_version = metadata['version'].split('.')
        new_version[-1] = str(int(new_version[-1]) + 1)  # Bump the final part
        self.version = ".".join(new_version)

    def finalize_options(self):
        pass

    def run(self):

        print('old version: %s  new version: %s' %
              (metadata['version'], self.version))
        try:
            input('Press enter to confirm, or ctrl-c to exit >')
        except KeyboardInterrupt:
            raise SystemExit("\nNot proceeding")

        old = "__version__ = '%s'" % metadata['version']
        new = "__version__ = '%s'" % self.version
        module_file = read_module_contents()
        with open('errata_tool/__init__.py', 'w') as fileh:
            fileh.write(module_file.replace(old, new))

        old = 'Version:        %s' % metadata['version']
        new = 'Version:        %s' % self.version
        spec_file = read_spec_contents()
        with open('python-errata-tool.spec', 'w') as fileh:
            fileh.write(spec_file.replace(old, new))

        # Commit everything with a standard commit message
        cmd = ['git', 'commit', '-a', '-m', 'version %s' % self.version]
        print(' '.join(cmd))
        subprocess.check_call(cmd)


class ReleaseCommand(Command):
    """ Tag and push a new release. """

    user_options = [('sign', 's', 'GPG-sign the Git tag and release files')]

    def initialize_options(self):
        self.sign = False

    def finalize_options(self):
        pass

    def run(self):
        # Create Git tag
        tag_name = 'v%s' % version
        cmd = ['git', 'tag', '-a', tag_name, '-m', 'version %s' % version]
        if self.sign:
            cmd.append('-s')
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push Git tag to origin remote
        cmd = ['git', 'push', 'origin', tag_name]
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push master to the remote
        cmd = ['git', 'push', 'origin', 'master']
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Create source package
        cmd = ['python', 'setup.py', 'sdist']
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        tarball = 'dist/%s-%s.tar.gz' % ('errata-tool', version)

        # GPG sign
        if self.sign:
            cmd = ['gpg2', '-b', '-a', tarball]
            print(' '.join(cmd))
            subprocess.check_call(cmd)

        # Upload
        cmd = ['twine', 'upload', tarball]
        if self.sign:
            cmd.append(tarball + '.asc')
        print(' '.join(cmd))
        subprocess.check_call(cmd)


setup(
    name='errata-tool',
    description='Python API for Red Hat Errata Tool',
    packages=find_packages(),
    author='Ken Dreyer',
    author_email='kdreyer@redhat.com',
    scripts=['bin/errata-tool'],
    url='https://github.com/red-hat-storage/errata-tool',
    version=metadata['version'],
    license='MIT',
    zip_safe=False,
    keywords='packaging, build',
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'jsonpath_rw',
        'pyyaml',
        'requests',
        'requests_gssapi',
        'six',
    ],
    cmdclass={'bump': BumpCommand, 'release': ReleaseCommand},
)
