from setuptools import setup, find_packages

setup(
    name='nanodl',
    version='1.2.0.dev1',
    author='Henry Ndubuaku',
    author_email='ndubuakuhenry@gmail.com',
    description='A Jax-based library for designing and training transformer models from scratch.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hmunachi/nanodl',
    packages=find_packages(),
    install_requires=[
        'flax',
        'jax',
        'jaxlib',
        'optax',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='transformers jax machine learning deep learning pytorch tensorflow',
    python_requires='>=3.7',
)
