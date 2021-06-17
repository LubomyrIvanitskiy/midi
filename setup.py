from setuptools import setup

setup(
    name='midiwrapper',
    version='0.45',
    packages=[''],
    install_requires=[
        'pandas',
        'matplotlib',
        'numpy',
        'pretty_midi',
        'libfmp'
    ],
    url='https://github.com/LubomyrIvanitskiy/midi.git',
    license='',
    author='liubomyr.ivanitskyi',
    author_email='lubomyr.ivanitskiy@gmail.com',
    description='A helper for pretty_midi lib',
)
