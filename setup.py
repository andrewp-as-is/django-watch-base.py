import setuptools

setuptools.setup(
    name='django-watch-base',
    version='2020.7.1',
    install_requires=open('requirements.txt').read().splitlines(),
    packages=setuptools.find_packages()
)
