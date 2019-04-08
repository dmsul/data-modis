from setuptools import setup, find_packages


dependencies = [
]

setup(
    name='modis',
    version='0.0.1',
    description='Easy access to MODIS data.',
    url='http://github.com/dmsul/modis',
    author='Daniel M. Sullivan',
    packages=find_packages(),
    tests_require=[
        'pytest',
    ],
    package_data={'modis': ["py.typed"]},
    install_requires=dependencies,
    zip_safe=False,
    license='BSD'
)
