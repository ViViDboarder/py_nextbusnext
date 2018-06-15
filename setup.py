from setuptools import setup, find_packages
setup(
    name='py_nextbus',
    version='0.1.0',
    author='Pierre Maris',
    description='Minimalistic Python client for the NextBus public API for real-time transit ' \
                'arrival data',
    test_suite='tests.py',
    url='https://github.com/pmaris/py_nextbus',
    packages=find_packages(),
    python_requires='>=3',
    classifiers=(
        "Programming Language :: Python :: 3.6 ",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
