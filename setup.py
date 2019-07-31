from setuptools import setup, find_packages
import os

version = '2.19'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


LONG_DESCRIP = """\
%s

%s
""" % (read("README.txt"),
       read("docs", "HISTORY.txt"))

setup(
    name='sixfeetup.utils',
    version=version,
    description="A collection of commonly used code snippets",
    long_description=LONG_DESCRIP,
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone zope utils',
    author='Six Feet Up, Inc.',
    author_email='info@sixfeetup.com',
    url='http://www.sixfeetup.com/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['sixfeetup'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
