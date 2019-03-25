from distutils.core import setup
from setuptools import find_packages

setup(name='db',  # 包名
      version='1.0.0',  # 版本号
      description='',
      long_description='',
      author='',
      author_email='',
      url='',
      license='',
      install_requires=['pandas >=0.23.4',
                        'pyodbc >=4.0.24',],
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Topic :: Utilities'
      ],
      requires=[
      ],
      keywords='',
      packages=find_packages('src'),  # 必填
      package_dir={'': 'src'},  # 必填
      include_package_data=True,
      )