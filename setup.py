from setuptools import find_packages, setup


module_name = 'core'

setup(
    name=module_name,
    version='0.0.1',
    author='Andrey Osipov',
    platforms='all',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'Operating System :: Win10',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    python_requires='>=3.7',
    install_requires=[
        "aioamqp~=0.14.0",
        "aiogram~=2.11.2",
        "aiohttp-sse~=2.0.0",
        "aiosqlite~=0.16.1",
        "aiohttp~=3.7.3",
        "alembic~=1.5.6",
        "Cerberus~=1.3.2",
        "defaultenv~=0.0.14",
        "PyYAML==5.3.1",
        "SQLAlchemy~=1.3.22",
        "setuptools~=53.0.0",
    ],
    extras_require={
        'dev': [
        ],
    },
    packages=find_packages(exclude=['tests']),
    data_files=[
        ("", ["core/config/logging.yml"]),
        ("", ["core/repository/alembic.ini"])
    ],

    include_package_data=True
)
