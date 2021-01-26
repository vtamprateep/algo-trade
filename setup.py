import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='algo_trade',
    version='0.1.0',
    author='Vinyou Tamprateep',
    description='Small package to test and implement portfolio trading algorithms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vtamprateep/algo-trade',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)