# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="ai-chart-toolkit",
    version="1.0.1",
    description="Universal Blueprint & Visual Diagram Generator for AI Agents, Local LLMs, and Cloud APIs.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "ai_chart_toolkit": ["assets/*"],
    },
    include_package_data=True,
    install_requires=[
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-chart = ai_chart_toolkit.tool:main",
            "ai-chart-mcp = ai_chart_toolkit.mcp_server:main",
            "ai-chart-api = ai_chart_toolkit.api_server:main",
        ],
    },
    python_requires=">=3.8",
)
