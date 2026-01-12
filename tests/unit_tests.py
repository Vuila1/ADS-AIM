#!/usr/bin/env python3
"""
Unit tests for ADS Aimbot components
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAimbotComponents(unittest.TestCase):
    
    def test_config_structure(self):
        """Test that config file has correct structure"""
        import json
        
        config_path = os.path.join("lib", "config", "config.json")
        self.assertTrue(os.path.exists(config_path), "Config file should exist")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required = ['detection', 'aim', 'trigger', 'input', 'visualization']
        for section in required:
            self.assertIn(section, config, f"Missing section: {section}")
    
    def test_screen_resolution(self):
        """Test screen resolution detection"""
        import ctypes
        
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
        
        self.assertIsInstance(width, int)
        self.assertIsInstance(height, int)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
    
    def test_menu_options(self):
        """Test menu options structure"""
        # This is a placeholder for menu testing
        # In actual implementation, would test menu rendering
        self.assertTrue(True)
    
    def test_coordinate_calculation(self):
        """Test coordinate transformation calculations"""
        # Test center calculation
        screen_x = 1920
        screen_y = 1080
        center_x = screen_x // 2
        center_y = screen_y // 2
        
        self.assertEqual(center_x, 960)
        self.assertEqual(center_y, 540)
        
        # Test FOV box calculation
        fov = 350
        left = (screen_x - fov) // 2
        top = (screen_y - fov) // 2
        
        self.assertEqual(left, 785)
        self.assertEqual(top, 365)
    
    def test_smoothing_calculation(self):
        """Test smoothing algorithm"""
        # Test basic smoothing
        import math
        
        target_x, target_y = 100, 100
        last_x, last_y = 0, 0
        smooth_factor = 0.5
        
        dx = target_x - last_x
        dy = target_y - last_y
        
        smoothed_x = last_x + dx * smooth_factor
        smoothed_y = last_y + dy * smooth_factor
        
        self.assertEqual(smoothed_x, 50)
        self.assertEqual(smoothed_y, 50)
        
        # Test distance calculation
        distance = math.sqrt(dx**2 + dy**2)
        self.assertAlmostEqual(distance, 141.421, places=3)

class TestImportModules(unittest.TestCase):
    """Test that all required modules can be imported"""
    
    def test_import_core_modules(self):
        """Test core module imports"""
        modules = [
            'cv2',
            'torch',
            'numpy',
            'mss',
            'win32api',
            'termcolor',
            'json',
            'math',
            'os',
            'sys',
            'time',
            'random'
        ]
        
        for module in modules:
            try:
                __import__(module)
                self.assertTrue(True, f"{module} imported successfully")
            except ImportError as e:
                self.fail(f"Failed to import {module}: {e}")

if __name__ == '__main__':
    unittest.main()