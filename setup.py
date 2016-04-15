import imp

from setuptools import setup, find_packages

metadata = imp.load_source('metadata', 'sqjobs/metadata.py')

setup(
    name=metadata.__uname__,
    version=metadata.__version__,
    url=metadata.__url__,
    license=metadata.__license__,
    author=metadata.__author__,
    author_email=metadata.__email__,
    description=metadata.__long_name__,
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': ['sqjobs = sqjobs.cli:main']
    },
    install_requires=[req.strip() for req in open('requirements/base.txt').readlines()],
    classifiers=[
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',
    ]
)
