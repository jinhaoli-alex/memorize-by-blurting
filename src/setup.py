from setuptools import setup, find_packages

setup(
    name='memorize-by-blurting',
    version='0.1',
    author="jinhao Li",
    author_email="alexlee7172@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'blurt-bee=blurting.__main__:main',
        ],
    },
)
