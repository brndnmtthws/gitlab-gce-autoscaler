import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'click>=7.0',
    'requests>=2.21.0',
    'google-api-python-client>=1.7.8',
    'google-auth>=1.6.2',
    'google-auth-httplib2>=0.0.3',
]

setuptools.setup(
    name="gitlab-gce-autoscaler",
    version="0.1.3",
    author="Brenden Matthews",
    author_email="brenden@diddyinc.com",
    description="Very simple autoscaler for GCE instance groups & GitLab CI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brndnmtthws/gitlab-gce-autoscaler",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts':
        ['gitlab-gce-autoscaler=gitlab_gce_autoscaler.main:main'],
    },
    python_requires=">=3.5",
    install_requires=requires,
)
