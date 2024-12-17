from setuptools import setup, find_packages

setup(
    name='blurt-bee',
    version='0.1',
    author="jinhao Li",
    author_email="drainall@proton.me",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'blurt-bee=blurting.__main__:main',
        ],
    },
)
