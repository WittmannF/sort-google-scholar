from setuptools import setup

# Function to read the requirements.txt file
def parse_requirements(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

setup(
    name='sortgs',
    version='1.0.4',
    author='Fernando Marcos Wittmann',
    #author_email='fernando.wittmann[at]gmail[dot]com',
    description='A Python tool to rank Google Scholar publications by citations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/WittmannF/sort-google-scholar',
    py_modules=['sortgs'],  # Assuming your script is named sortgs.py
    
    # Dynamically fetch dependencies from requirements.txt
    install_requires=parse_requirements('requirements.txt'),
    
    entry_points={
        'console_scripts': [
            'sortgs=sortgs:main',  # This line sets up the command line tool
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
