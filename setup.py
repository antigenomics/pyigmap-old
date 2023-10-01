from setuptools import setup, find_packages

setup(name='igmap',
      version='0.0.1',
      description='Extract and summarize antigen receptor gene rearrangements from sequencing data',
      long_description='text/markdown',
      url='https://github.com/antigenomics/pyigmap',
      author='Mikhail Shugay',
      author_email='mikhail.shugay@gmail.com',
      license='GPLv3',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Healthcare Industry',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Scientific/Engineering :: Medical Science Apps.',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.8',
      ],
      packages=find_packages(),
      package_data={
          'igmap': ['external/**/**/**']
      },
      include_package_data=True,
      entry_points={'console_scripts': [
          'igmap=igmap.__main__:main'
      ]})