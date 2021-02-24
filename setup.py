from setuptools import setup


setup(name='pygpsnmea',
      version='2021.2',
      description='a Python 3 GPS NMEA 0183 decoder',
      author='Thomas W Whittam',
      url='https://github.com/tww-software/py_gps_nmea',
      license='MIT',
      packages=['pygpsnmea', 'pygpsnmea.sentences', 'pygpsnmea.gui'],
      install_requires=['pyserial'],
      include_package_data=True,
      zip_safe=False
)

