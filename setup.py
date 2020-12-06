from setuptools import setup

setup(
    name='portmanteau',
    version='0.1',
    py_modules=['portmanteau'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        portmanteau=portmanteau:cli
    ''',
)