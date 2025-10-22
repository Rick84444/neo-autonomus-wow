from setuptools import setup, find_packages
setup(
  name="neo-autonomous-mock",
  version="0.1.0",
  description="Neo Autonomous – Mock backend + UI",
  packages=find_packages(),
  include_package_data=True,
  install_requires=["fastapi==0.115.2","uvicorn==0.30.1","pydantic==2.9.2"],
  entry_points={"console_scripts":["neo-mock=neo_mock.cli:main"]},
)
