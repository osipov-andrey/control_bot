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
    ],
    extras_require={
        'dev': [
        ],
    },
    packages=find_packages(exclude=['tests']),

    include_package_data=True
)
