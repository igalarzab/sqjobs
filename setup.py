from setuptools import setup, find_packages

setup(
    name='sqjobs',
    version='0.5',
    url='https://github.com/igalarzab/sqjobs/',
    license='BSD',
    author='Jose Ignacio Galarza',
    author_email='igalarzab@gmail.com',
    description='Simple Queue Jobs (using SQS, Simple Queue Service, from AWS)',
    long_description='',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'boto==2.34.0',
    ],
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
