from setuptools import setup, find_packages

setup(
    name='rsession',
    version='0.1.0',
    description='Django session back-end persisting to Redis',
    author='Matthew Pontefract',
    author_email='matthew@zorinholdings.com',
    url='https://github.com/aquamatt/rsession/',
    keywords='django, sessions, redis',
    packages=find_packages(),
    package_data={'': []},
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
