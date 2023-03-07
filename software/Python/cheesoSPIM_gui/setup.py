from setuptools import setup
from setuptools import find_packages
packages =find_packages(exclude=['test'])

setup(name='cheesoSPIM_gui',
      version="0.1.0",
      description="Drive cheesoSPIM",
      author='Rusty Nicovich',
      author_email='rusty@cajalneuro.com',
      packages = ['cheesoSPIM_gui', 'cheesoSPIM_gui.gui', 'cheesoSPIM_gui.utilities'],
      include_package_data=True,
      install_requires=[])
	  
# ^ incomplete list of required packages.