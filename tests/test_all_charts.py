# -*- coding: utf-8 -*-
"""
Unit test suite verifying all 6 chart generators execute cleanly and create valid PNG files.
"""

import os
import unittest
from ai_chart_toolkit import execute_chart_tool

class TestAIChartToolkit(unittest.TestCase):
    output_dir = "test_output"

    @classmethod
    def setUpClass(cls):
        os.makedirs(cls.output_dir, exist_ok=True)

    def test_01_flowchart(self):
        res = execute_chart_tool("flowchart", {
            "title": "Test Flowchart",
            "stages": [
                {"header": "STAGE 1", "blocks": [{"label": "Sensor A", "type": "input"}]},
                {"header": "STAGE 2", "blocks": [{"label": "Local LLM", "type": "ai_model"}]},
                {"header": "STAGE 3", "blocks": [{"label": "Relay Actuator", "type": "output"}]}
            ],
            "output_dir": self.output_dir
        })
        self.assertTrue(res["success"], res.get("error"))
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_02_hierarchy(self):
        res = execute_chart_tool("hierarchy", {
            "title": "Test Hierarchy",
            "root_node": {
                "name": "Master Node",
                "desc": "Controller",
                "children": [
                    {"name": "Worker 1", "desc": "Worker"},
                    {"name": "Worker 2", "desc": "Worker"}
                ]
            },
            "output_dir": self.output_dir
        })
        self.assertTrue(res["success"], res.get("error"))
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_03_donut(self):
        res = execute_chart_tool("donut", {
            "title": "Test Donut",
            "center_text": "$50k",
            "data": [
                {"label": "Direct", "value": 60},
                {"label": "Indirect", "value": 40}
            ],
            "output_dir": self.output_dir
        })
        self.assertTrue(res["success"], res.get("error"))
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_04_pie(self):
        res = execute_chart_tool("pie", {
            "title": "Test Pie",
            "data": [
                {"label": "Part A", "value": 30},
                {"label": "Part B", "value": 70}
            ],
            "output_dir": self.output_dir
        })
        self.assertTrue(res["success"], res.get("error"))
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_05_rings(self):
        res = execute_chart_tool("rings", {
            "title": "Test Rings",
            "metrics": [
                {"label": "Ring 1", "pct": 80},
                {"label": "Ring 2", "pct": 45}
            ],
            "output_dir": self.output_dir
        })
        self.assertTrue(res["success"], res.get("error"))
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_06_gauge(self):
        res = execute_chart_tool("gauge", {
            "title": "Test Gauge",
            "value": 54.2,
            "min_val": 0,
            "max_val": 100,
            "unit": "°C",
            "output_dir": self.output_dir
        })
        self.assertTrue(res["success"], res.get("error"))
        self.assertTrue(os.path.exists(res["output_path"]))

if __name__ == "__main__":
    unittest.main()
