import setuptools
import numpy
import os

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='pet_tutorial',
    version="0.0.0",
    author='Sebastian Achim Mueller',
    author_email='sebastianachimmueller@gmail.com',
    description='A merlict c89 tutorial on the example of a PET-scanner.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/relleums/pet_tutorial',
    packages=[
        'pet_tutorial'
    ],
    install_requires=[
        'setuptools>=18.0',
        'cython',
        'scipy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires='>=3',
    ext_modules=[
        setuptools.Extension(
            "pet_tutorial.merlict_c89",
            sources=[
                os.path.join(
                    'pet_tutorial', '_merlict_c89', '_wrap.pyx'),
                os.path.join(
                    'pet_tutorial', '_merlict_c89', '_wrap.c'),
            ],
            include_dirs=[numpy.get_include(), "pet_tutorial"],
            language="c",
        ),
    ],
)

