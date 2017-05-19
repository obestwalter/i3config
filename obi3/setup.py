from setuptools import find_packages, setup

setup(
    name='obi3',
    description="i3 config generation deamon",
    version='0.5.0.dev0',
    # entry_points={'console_scripts': ['']},
    install_requires=['inotify'],
    packages=find_packages()
)
