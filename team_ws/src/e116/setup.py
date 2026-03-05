from setuptools import find_packages, setup

package_name = 'e116'

setup(
    name=package_name,
    version='0.0.0',
#    py_modules =['e116/e116_OLED'],
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/teleop.launch.py']),
        ('share/' + package_name + '/launch', ['launch/e116race.launch.py']),
        ('share/' + package_name + '/config', ['config/e116.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Rosa Zheng',
    maintainer_email='yrz218@lehigh.edu',
    description='Package for 1:16-scale autonomous-driving car',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'keyJoy = e116.keyJoy:main',
            'keyJoyTerminal = e116.keyJoyTerminal:main',
            'e116_OLED = e116.e116_OLED:main',
            'gap_follow = e116.gap_follow:main',	
            'e116_racecar = e116.e116_racecar:main'
        ],
    },
)
