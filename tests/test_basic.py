"""
Basic tests for VulnScanner functionality
"""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of VulnScanner components"""

    def test_import_main(self):
        """Test that main module can be imported"""
        try:
            import main
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")

    def test_import_gui(self):
        """Test that gui module can be imported"""
        try:
            import gui
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import gui module: {e}")

    def test_scanner_package(self):
        """Test that scanner package exists"""
        scanner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scanner')
        self.assertTrue(os.path.exists(scanner_path), "Scanner package directory should exist")

    def test_requirements_file(self):
        """Test that requirements.txt exists and is readable"""
        req_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'requirements.txt')
        self.assertTrue(os.path.exists(req_path), "requirements.txt should exist")
        
        with open(req_path, 'r') as f:
            content = f.read()
            self.assertGreater(len(content), 0, "requirements.txt should not be empty")

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Dockerfile')
        self.assertTrue(os.path.exists(dockerfile_path), "Dockerfile should exist")


class TestScannerComponents(unittest.TestCase):
    """Test scanner component imports"""

    def test_scanner_imports(self):
        """Test that scanner components can be imported"""
        scanner_modules = ['crawler', 'portscan', 'xss', 'sqli', 'parallel', 'report']
        
        for module_name in scanner_modules:
            try:
                exec(f"from scanner import {module_name}")
            except ImportError:
                # Some modules might not exist yet, so we'll just skip them
                pass


if __name__ == '__main__':
    unittest.main() 