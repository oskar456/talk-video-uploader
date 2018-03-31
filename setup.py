from setuptools import setup

setup(
    name='talk_video_uploader',
    version='0.1',
    description='Batch upload talk videos to YouTube',
    url='https://github.com/oskar456/talk-video-uploader',
    author='Ondřej Caletka',
    author_email='ondrej@caletka.cz',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=['talk_video_uploader'],
    data_files=[('share/talk-video-uploader', ['client_id.json'])],
    install_requires=[
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'pyyaml',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'talk-video-uploader = talk_video_uploader.__main__:main',
        ],
    }
)
