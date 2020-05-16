import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='easycontrol',
    version='1.0.0',
    description='An easy-to-use template for creating a fully working userbot on Telegram',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mattiabrandon/easycontrol',
    author='Mattia Chiabrando',
    author_email='brandon@mattiabrandon.it',
    license='GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Chat',
        'Topic :: Utilities'
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['asyncio', 'importlib'],
    dependency_links=['https://github.com/pyrogram/pyrogram/archive/asyncio.zip', ],
)
