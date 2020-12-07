import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='algo-portfolio-management',
    version='0.0.1',
    author='Vinyou Tamprateep',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifies=None,
    python_requires='>=3.6',
)