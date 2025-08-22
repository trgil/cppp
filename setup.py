from setuptools import setup, find_packages

setup(
    name='cppp',
    version='1.0.0-alpha.1',
    description='A Python package for preprocessing C/C++ code',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Gil Treibush',
    url='https://github.com/trgil/cppp',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'setuptools>=42',  # Specify version if needed
    ],
    extras_require={
        'cli': [            # For running standalone
        ],
        'dev': [            # For development
            'pytest',       # For testing
            'flake8',       # For linting
            'sphinx',       # For documentation
        ],
    },
    python_requires='>=3.6',
)