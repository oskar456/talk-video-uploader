from setuptools import setup
from pathlib import Path

readme = Path(__file__).with_name("README.rst").read_text()

setup(
    name='talk_video_uploader',
    version='0.1',
    description='Batch upload talk videos to YouTube',
    long_description=readme,
    long_description_content_type="text/x-rst",
    url='https://github.com/oskar456/talk-video-uploader',
    author='Ondřej Caletka',
    author_email='ondrej@caletka.cz',
    license='MIT',
    python_requires=">=3.6",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3 :: Only",
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
