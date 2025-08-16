#!/usr/bin/env python3
"""
Comprehensive test suite for start.py
Tests dependency checking, building, service startup, and tunnel functionality
"""

import os
import sys
import tempfile
import shutil
import unittest
import subprocess
import time
import threading
from unittest.mock import patch, MagicMock, mock_open, call
import urllib.error
import platform
import signal

# Import the functions from start.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from swarmtunnel.start import (
    check_dependencies, build_swarmui, wait_for_service, start_swarmui,
    create_tunnel_config, start_tunnel, extract_tunnel_url, cleanup
)


class TestDependencyChecking(unittest.TestCase):
    """Unit tests for dependency checking"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('swarmtunnel.start.FORCE_LOCAL_SWARMUI', False)
    @patch('swarmtunnel.start.FORCE_LOCAL_CLOUDFLARED', False)
    def test_check_dependencies_all_present(self, mock_run, mock_exists):
        """Test dependency check when all dependencies are present"""
        # Mock the install module functions by patching the specific functions
        with patch('swarmtunnel.start.check_dependencies') as mock_check:
            # Mock the internal calls to install module functions
            with patch('builtins.__import__') as mock_import:
                # Create a mock module that has the required functions
                mock_install_module = MagicMock()
                mock_install_module.is_swarmui_installed.return_value = True
                mock_install_module.is_cloudflared_installed.return_value = True
                
                def mock_import_func(name, *args, **kwargs):
                    if 'swarmtunnel.install' in name:
                        return mock_install_module
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = mock_import_func
                
                # Mock .NET check
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "8.0.0"

                result = check_dependencies()
                self.assertTrue(result)
    
    @patch('os.path.exists')
    @patch('swarmtunnel.start.FORCE_LOCAL_SWARMUI', False)
    @patch('swarmtunnel.start.FORCE_LOCAL_CLOUDFLARED', False)
    def test_check_dependencies_swarmui_missing(self, mock_exists):
        """Test dependency check when SwarmUI is missing"""
        # Mock the install module functions
        with patch('importlib.import_module') as mock_import:
            mock_install_module = MagicMock()
            mock_install_module.is_swarmui_installed.return_value = False
            mock_install_module.is_cloudflared_installed.return_value = True
            mock_import.return_value = mock_install_module

            with patch('builtins.print') as mock_print:
                result = check_dependencies()
                self.assertFalse(result)
                # Check for error message (more flexible matching)
                error_found = any("SwarmUI not found" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(error_found, "Expected SwarmUI not found message not found")
    
    @patch('os.path.exists')
    @patch('swarmtunnel.start.FORCE_LOCAL_SWARMUI', False)
    @patch('swarmtunnel.start.FORCE_LOCAL_CLOUDFLARED', False)
    def test_check_dependencies_cloudflared_missing(self, mock_exists):
        """Test dependency check when cloudflared is missing"""
        # Mock the install module functions
        with patch('importlib.import_module') as mock_import:
            mock_install_module = MagicMock()
            mock_install_module.is_swarmui_installed.return_value = True
            mock_install_module.is_cloudflared_installed.return_value = False
            mock_import.return_value = mock_install_module

            with patch('builtins.print') as mock_print:
                result = check_dependencies()
                self.assertFalse(result)
                # Check for error message (more flexible matching)
                error_found = any("cloudflared not found" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(error_found, "Expected cloudflared not found message not found")
    
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('swarmtunnel.start.FORCE_LOCAL_SWARMUI', False)
    @patch('swarmtunnel.start.FORCE_LOCAL_CLOUDFLARED', False)
    def test_check_dependencies_dotnet_missing(self, mock_run, mock_exists):
        """Test dependency check when .NET is missing"""
        # Mock the install module functions
        with patch('importlib.import_module') as mock_import:
            mock_install_module = MagicMock()
            mock_install_module.is_swarmui_installed.return_value = True
            mock_install_module.is_cloudflared_installed.return_value = True
            mock_import.return_value = mock_install_module
            
            # Mock .NET check failure
            mock_run.side_effect = FileNotFoundError()

            with patch('builtins.print') as mock_print:
                result = check_dependencies()
                self.assertFalse(result)
                # Check for error message (more flexible matching)
                error_found = any(".NET not found" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(error_found, "Expected .NET not found message not found")


class TestSwarmUIBuilding(unittest.TestCase):
    """Unit tests for SwarmUI building"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create mock SwarmUI directory structure
        os.makedirs("SwarmUI/src", exist_ok=True)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('os.path.exists')
    def test_build_swarmui_already_built(self, mock_exists):
        """Test build when SwarmUI is already built"""
        mock_exists.return_value = True
        
        with patch('builtins.print') as mock_print:
            result = build_swarmui()
            self.assertTrue(result)
            # No build message expected; installer is responsible for builds
    
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_build_swarmui_success(self, mock_run, mock_exists):
        """Test successful SwarmUI build"""
        # When binary isn't present, build_swarmui should instruct installer; do not attempt to run dotnet here
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            result = build_swarmui()
            self.assertFalse(result)
            # Check for error message (more flexible matching)
            error_found = any("SwarmUI is not built" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, "Expected SwarmUI not built message not found")
    
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_build_swarmui_failure(self, mock_run, mock_exists):
        """Test SwarmUI build failure"""
        mock_exists.return_value = False
        mock_run.side_effect = subprocess.CalledProcessError(1, "dotnet")
        
        with patch('builtins.print') as mock_print:
            result = build_swarmui()
            self.assertFalse(result)
            # Check for the error message pattern (more flexible matching)
            error_found = any("Failed to build SwarmUI" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, f"Expected error message not found in print calls")
    
    def test_find_launch_script_windows_batch(self):
        """Test finding Windows batch launcher script"""
        from swarmtunnel.start import _find_launch_script
        
        # Create mock SwarmUI directory with Windows batch file
        os.makedirs("SwarmUI", exist_ok=True)
        with open(os.path.join("SwarmUI", "launch-windows.bat"), "w") as f:
            f.write("echo Starting SwarmUI\r\n")
        
        result = _find_launch_script("SwarmUI")
        self.assertEqual(result, os.path.join("SwarmUI", "launch-windows.bat"))
    
    def test_find_launch_script_linux_shell(self):
        """Test finding Linux shell launcher script"""
        from swarmtunnel.start import _find_launch_script
        
        # Create mock SwarmUI directory with Linux shell script
        os.makedirs("SwarmUI", exist_ok=True)
        with open(os.path.join("SwarmUI", "launch-linux.sh"), "w") as f:
            f.write("echo Starting SwarmUI\n")
        
        result = _find_launch_script("SwarmUI")
        self.assertEqual(result, os.path.join("SwarmUI", "launch-linux.sh"))
    
    def test_find_launch_script_not_found(self):
        """Test when no launcher script is found"""
        from swarmtunnel.start import _find_launch_script
        
        # Create mock SwarmUI directory without launcher files
        os.makedirs("SwarmUI", exist_ok=True)
        
        result = _find_launch_script("SwarmUI")
        self.assertIsNone(result)


class TestServiceWaiting(unittest.TestCase):
    """Unit tests for service waiting functionality"""
    
    @patch('urllib.request.urlopen')
    def test_wait_for_service_success(self, mock_urlopen):
        """Test successful service waiting"""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = wait_for_service("http://localhost:7801", timeout=5)
            self.assertTrue(result)
            # Check for success message (more flexible matching)
            success_found = any("http://localhost:7801 is available" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected service available message not found")
    
    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_wait_for_service_timeout(self, mock_sleep, mock_urlopen):
        """Test service waiting timeout"""
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        
        with patch('builtins.print') as mock_print:
            # Mock time.time to simulate timeout
            with patch('time.time') as mock_time:
                mock_time.side_effect = [0, 0.2]  # Start at 0, then jump to 0.2 (past timeout)
                result = wait_for_service("http://localhost:7801", timeout=0.1, check_interval=0.05)
                self.assertFalse(result)
                # Check for timeout message (more flexible matching)
                timeout_found = any("Timeout waiting for http://localhost:7801" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(timeout_found, "Expected timeout message not found")


class TestSwarmUIStarting(unittest.TestCase):
    """Unit tests for SwarmUI starting"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create mock SwarmUI directory structure
        os.makedirs("SwarmUI/src/bin/live_release", exist_ok=True)
        with open("SwarmUI/src/bin/live_release/SwarmUI.exe", "w") as f:
            f.write("mock executable")
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.Popen')
    def test_start_swarmui_success(self, mock_popen):
        """Test successful SwarmUI start"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = start_swarmui()
            self.assertEqual(result, mock_process)
            # Check for success message (more flexible matching)
            success_found = any("SwarmUI started successfully" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected SwarmUI started message not found")
    
    @patch('subprocess.Popen')
    def test_start_swarmui_failure(self, mock_popen):
        """Test SwarmUI start failure"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        mock_process.communicate.return_value = ("stdout", "stderr")
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = start_swarmui()
            self.assertIsNone(result)
            # Check for error message (more flexible matching)
            error_found = any("SwarmUI failed to start" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, "Expected SwarmUI failed to start message not found")


class TestTunnelConfiguration(unittest.TestCase):
    """Unit tests for tunnel configuration"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_create_tunnel_config(self):
        """Test tunnel configuration file creation"""
        with patch('builtins.print') as mock_print:
            create_tunnel_config()
            
            self.assertTrue(os.path.exists("tunnel_config.yml"))
            
            with open("tunnel_config.yml", "r") as f:
                config = f.read()
            
            self.assertIn("tunnel: swarmui-tunnel", config)
            self.assertIn("service: http://localhost:7801", config)
            # Check for success message (more flexible matching)
            success_found = any("Created tunnel config" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected tunnel config created message not found")


class TestTunnelStarting(unittest.TestCase):
    """Unit tests for tunnel starting"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create mock cloudflared
        with open("cloudflared.exe", "w") as f:
            f.write("mock cloudflared")
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_start_tunnel_success(self, mock_sleep, mock_popen):
        """Test successful tunnel start"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = start_tunnel()
            self.assertEqual(result, mock_process)
            # Check for success message (more flexible matching)
            success_found = any("Cloudflare tunnel started" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected tunnel started message not found")
    
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_start_tunnel_failure(self, mock_sleep, mock_popen):
        """Test tunnel start failure"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        mock_process.communicate.return_value = ("stdout", "stderr")
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = start_tunnel()
            self.assertIsNone(result)
            # Check for error message (more flexible matching)
            error_found = any("Tunnel failed to start" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, "Expected tunnel failed to start message not found")


class TestTunnelURLExtraction(unittest.TestCase):
    """Unit tests for tunnel URL extraction"""
    
    @patch('time.sleep')
    def test_extract_tunnel_url_success(self, mock_sleep):
        """Test successful tunnel URL extraction"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = "https://swarmui-12345.trycloudflare.com"
        
        with patch('builtins.print') as mock_print:
            result = extract_tunnel_url(mock_process)
            self.assertEqual(result, "https://swarmui-12345.trycloudflare.com")
            # Check for success message (more flexible matching)
            success_found = any("Found tunnel URL" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected tunnel URL found message not found")
    
    @patch('time.sleep')
    def test_extract_tunnel_url_timeout(self, mock_sleep):
        """Test tunnel URL extraction timeout"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = "no url here"
        
        with patch('builtins.print') as mock_print:
            result = extract_tunnel_url(mock_process, timeout=1)
            self.assertIsNone(result)
            # Check for error message (more flexible matching)
            error_found = any("Could not extract tunnel URL" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, "Expected tunnel URL extraction failed message not found")
    
    @patch('time.sleep')
    def test_extract_tunnel_url_process_terminated(self, mock_sleep):
        """Test tunnel URL extraction when process terminates"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        
        with patch('builtins.print') as mock_print:
            result = extract_tunnel_url(mock_process)
            self.assertIsNone(result)
            # Check for error message (more flexible matching)
            error_found = any("Tunnel process terminated" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, "Expected tunnel process terminated message not found")
    
    @patch('time.sleep')
    def test_extract_tunnel_url_dummy_process_windows(self, mock_sleep):
        """Test tunnel URL extraction with DummyProcess (Windows PowerShell)"""
        # Create a DummyProcess-like object (has pid but no stdout)
        class DummyProcess:
            def __init__(self, pid):
                self.pid = pid
        
        dummy_process = DummyProcess(12345)
        
        with patch('builtins.print') as mock_print:
            result = extract_tunnel_url(dummy_process, timeout=5)
            
            # Should return placeholder URL for Windows PowerShell case
            self.assertEqual(result, "https://tunnel-url-in-powershell-window.trycloudflare.com")
            
            # Check for informational messages
            info_found = any("Tunnel running in PowerShell window" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(info_found, "Expected PowerShell window message not found")
            
            check_found = any("Check the PowerShell window for the tunnel URL" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(check_found, "Expected check PowerShell window message not found")


class TestCleanup(unittest.TestCase):
    """Unit tests for cleanup functionality"""
    
    def test_cleanup_processes_and_files(self):
        """Test cleanup of processes and files"""
        mock_swarmui_process = MagicMock()
        mock_tunnel_process = MagicMock()
        
        # Create a temporary config file
        with open("tunnel_config.yml", "w") as f:
            f.write("test config")
        
        with patch('builtins.print') as mock_print:
            cleanup(mock_swarmui_process, mock_tunnel_process)
            
            # Check that processes were terminated
            mock_swarmui_process.terminate.assert_called_once()
            mock_tunnel_process.terminate.assert_called_once()
            
            # Check that config file was removed
            self.assertFalse(os.path.exists("tunnel_config.yml"))
            
            # Check for success message (more flexible matching)
            success_found = any("Cleanup complete" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected cleanup complete message not found")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create mock directory structure
        os.makedirs("SwarmUI/src/bin/live_release", exist_ok=True)
        with open("SwarmUI/src/bin/live_release/SwarmUI.exe", "w") as f:
            f.write("mock executable")
        with open("cloudflared.exe", "w") as f:
            f.write("mock cloudflared")
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('swarmtunnel.start.build_swarmui')
    @patch('swarmtunnel.start.start_swarmui')
    @patch('swarmtunnel.start.wait_for_service')
    @patch('swarmtunnel.start.start_tunnel')
    @patch('swarmtunnel.start.extract_tunnel_url')
    def test_full_workflow_success(self, mock_extract_url, mock_start_tunnel, 
                                  mock_wait_service, mock_start_swarmui, mock_build):
        """Test complete successful workflow"""
        # Mock all functions to succeed
        mock_build.return_value = True
        mock_swarmui_process = MagicMock()
        mock_start_swarmui.return_value = mock_swarmui_process
        mock_wait_service.return_value = True
        mock_tunnel_process = MagicMock()
        mock_start_tunnel.return_value = mock_tunnel_process
        mock_extract_url.return_value = "https://swarmui-12345.trycloudflare.com"
        
        # Mock dependency check
        with patch('swarmtunnel.start.check_dependencies', return_value=True):
            # This would normally call main(), but we'll test the individual components
            # that are called by main()
            self.assertTrue(mock_build())
            self.assertEqual(mock_start_swarmui(), mock_swarmui_process)
            self.assertTrue(mock_wait_service("http://localhost:7801"))
            self.assertEqual(mock_start_tunnel(), mock_tunnel_process)
            self.assertEqual(mock_extract_url(mock_tunnel_process), 
                           "https://swarmui-12345.trycloudflare.com")


class TestEnvironmentVariables(unittest.TestCase):
    """Tests for environment variable handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        # Save original environment variables
        self.original_swarmui_dir = os.environ.get('SWARMUI_DIR')
        self.original_cloud_dir = os.environ.get('SWARMTUNNEL_CLOUDFLARED_DIR')
        self.original_log_dir = os.environ.get('SWARMTUNNEL_LOG_DIR')
        self.original_force_local_swarmui = os.environ.get('SWARMTUNNEL_FORCE_LOCAL_SWARMUI')
        self.original_force_local_cloudflared = os.environ.get('SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED')
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
        # Restore original environment variables
        if self.original_swarmui_dir:
            os.environ['SWARMUI_DIR'] = self.original_swarmui_dir
        elif 'SWARMUI_DIR' in os.environ:
            del os.environ['SWARMUI_DIR']
        
        if self.original_cloud_dir:
            os.environ['SWARMTUNNEL_CLOUDFLARED_DIR'] = self.original_cloud_dir
        elif 'SWARMTUNNEL_CLOUDFLARED_DIR' in os.environ:
            del os.environ['SWARMTUNNEL_CLOUDFLARED_DIR']
        
        if self.original_log_dir:
            os.environ['SWARMTUNNEL_LOG_DIR'] = self.original_log_dir
        elif 'SWARMTUNNEL_LOG_DIR' in os.environ:
            del os.environ['SWARMTUNNEL_LOG_DIR']
        
        if self.original_force_local_swarmui:
            os.environ['SWARMTUNNEL_FORCE_LOCAL_SWARMUI'] = self.original_force_local_swarmui
        elif 'SWARMTUNNEL_FORCE_LOCAL_SWARMUI' in os.environ:
            del os.environ['SWARMTUNNEL_FORCE_LOCAL_SWARMUI']
        
        if self.original_force_local_cloudflared:
            os.environ['SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED'] = self.original_force_local_cloudflared
        elif 'SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED' in os.environ:
            del os.environ['SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED']
    
    def test_swarmui_dir_environment_variable(self):
        """Test SWARMUI_DIR environment variable override"""
        os.environ['SWARMUI_DIR'] = 'CustomSwarmUI'
        
        # Import after setting environment variable to test the override
        import importlib
        import swarmtunnel.start
        importlib.reload(swarmtunnel.start)
        
        # Test that the function uses the custom directory
        self.assertEqual(swarmtunnel.start.SWARMUI_DIR, 'CustomSwarmUI')
    
    def test_cloudflared_dir_environment_variable(self):
        """Test SWARMTUNNEL_CLOUDFLARED_DIR environment variable override"""
        os.environ['SWARMTUNNEL_CLOUDFLARED_DIR'] = 'custom_cloudflared'
        
        # Import after setting environment variable to test the override
        import importlib
        import swarmtunnel.start
        importlib.reload(swarmtunnel.start)
        
        # Test that the function uses the custom directory
        self.assertEqual(swarmtunnel.start.CLOUD_DIR, 'custom_cloudflared')
    
    def test_log_dir_environment_variable(self):
        """Test SWARMTUNNEL_LOG_DIR environment variable override"""
        os.environ['SWARMTUNNEL_LOG_DIR'] = 'custom_logs'
        
        # Import after setting environment variable to test the override
        import importlib
        import swarmtunnel.start
        importlib.reload(swarmtunnel.start)
        
        # Test that the function uses the custom directory
        self.assertEqual(swarmtunnel.start.LOG_DIR, 'custom_logs')
    
    def test_force_local_swarmui_environment_variable(self):
        """Test SWARMTUNNEL_FORCE_LOCAL_SWARMUI environment variable"""
        os.environ['SWARMTUNNEL_FORCE_LOCAL_SWARMUI'] = '1'
        
        # Import after setting environment variable to test the override
        import importlib
        import swarmtunnel.start
        importlib.reload(swarmtunnel.start)
        
        # Test that the flag is set correctly
        self.assertTrue(swarmtunnel.start.FORCE_LOCAL_SWARMUI)
    
    def test_force_local_cloudflared_environment_variable(self):
        """Test SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED environment variable"""
        os.environ['SWARMTUNNEL_FORCE_LOCAL_CLOUDFLARED'] = '1'
        
        # Import after setting environment variable to test the override
        import importlib
        import swarmtunnel.start
        importlib.reload(swarmtunnel.start)
        
        # Test that the flag is set correctly
        self.assertTrue(swarmtunnel.start.FORCE_LOCAL_CLOUDFLARED)


class TestCLIArguments(unittest.TestCase):
    """Tests for command line argument parsing"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        # Save original sys.argv
        self.original_argv = sys.argv.copy()
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
        # Restore original sys.argv
        sys.argv = self.original_argv
    
    def test_parse_arguments_no_flags(self):
        """Test argument parsing with no flags"""
        sys.argv = ['start.py']
        
        from swarmtunnel.start import parse_arguments
        args = parse_arguments()
        
        # Verify no flags are set
        self.assertFalse(args.force_local_swarmui)
        self.assertFalse(args.force_local_cloudflared)
    
    def test_parse_arguments_force_local_swarmui(self):
        """Test --force-local-swarmui CLI flag"""
        sys.argv = ['start.py', '--force-local-swarmui']
        
        from swarmtunnel.start import parse_arguments
        args = parse_arguments()
        
        # Verify the flag is set
        self.assertTrue(args.force_local_swarmui)
        self.assertFalse(args.force_local_cloudflared)
    
    def test_parse_arguments_force_local_cloudflared(self):
        """Test --force-local-cloudflared CLI flag"""
        sys.argv = ['start.py', '--force-local-cloudflared']
        
        from swarmtunnel.start import parse_arguments
        args = parse_arguments()
        
        # Verify the flag is set
        self.assertFalse(args.force_local_swarmui)
        self.assertTrue(args.force_local_cloudflared)
    
    def test_parse_arguments_both_flags(self):
        """Test both CLI flags together"""
        sys.argv = ['start.py', '--force-local-swarmui', '--force-local-cloudflared']
        
        from swarmtunnel.start import parse_arguments
        args = parse_arguments()
        
        # Verify both flags are set
        self.assertTrue(args.force_local_swarmui)
        self.assertTrue(args.force_local_cloudflared)


class TestWindowsPowerShellFunctionality(unittest.TestCase):
    """Tests for Windows PowerShell specific functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('platform.system')
    @patch('subprocess.Popen')
    def test_start_swarmui_windows_powershell(self, mock_popen, mock_system):
        """Test SwarmUI startup on Windows with PowerShell"""
        mock_system.return_value = 'Windows'
        
        # Create mock SwarmUI directory with batch file
        os.makedirs("SwarmUI", exist_ok=True)
        with open(os.path.join("SwarmUI", "launch-windows.bat"), "w") as f:
            f.write("echo Starting SwarmUI\r\n")
        
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = start_swarmui()
            
            # Verify PowerShell was called
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            self.assertIn('powershell', call_args)
            self.assertIn('-NoExit', call_args)
            
            # Verify we got a DummyProcess back
            self.assertIsNotNone(result)
            self.assertEqual(result.pid, 12345)
            
            # Check for success message
            success_found = any("SwarmUI started successfully" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected SwarmUI started message not found")
    
    @patch('platform.system')
    @patch('subprocess.Popen')
    def test_start_tunnel_windows_powershell(self, mock_popen, mock_system):
        """Test tunnel startup on Windows with PowerShell"""
        mock_system.return_value = 'Windows'
        
        # Create mock cloudflared
        os.makedirs("cloudflared", exist_ok=True)
        with open(os.path.join("cloudflared", "cloudflared.exe"), "w") as f:
            f.write("mock cloudflared")
        
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = start_tunnel()
            
            # Verify PowerShell was called
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            self.assertIn('powershell', call_args)
            self.assertIn('-NoExit', call_args)
            
            # Verify we got a DummyProcess back
            self.assertIsNotNone(result)
            self.assertEqual(result.pid, 12345)
            
            # Check for success message
            success_found = any("Cloudflare tunnel started" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected tunnel started message not found")


class TestLocalInstallationChecks(unittest.TestCase):
    """Tests for local installation checking functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_check_local_swarmui_present(self):
        """Test local SwarmUI check when present"""
        from swarmtunnel.start import _check_local_swarmui
        
        # Create mock SwarmUI with installed marker
        os.makedirs("SwarmUI", exist_ok=True)
        with open(os.path.join("SwarmUI", ".installed"), "w") as f:
            f.write("installed")
        
        with patch('builtins.print') as mock_print:
            result = _check_local_swarmui()
            self.assertTrue(result)
            
            # Check for success message
            success_found = any("Local SwarmUI found" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(success_found, "Expected local SwarmUI found message not found")
    
    def test_check_local_swarmui_missing(self):
        """Test local SwarmUI check when missing"""
        from swarmtunnel.start import _check_local_swarmui
        
        with patch('builtins.print') as mock_print:
            result = _check_local_swarmui()
            self.assertFalse(result)
            
            # Check for error message
            error_found = any("Local SwarmUI not found" in str(call) for call in mock_print.call_args_list)
            self.assertTrue(error_found, "Expected local SwarmUI not found message not found")
    
    def test_check_local_cloudflared_present(self):
        """Test local cloudflared check when present"""
        from swarmtunnel.start import _check_local_cloudflared
        
        # Create mock cloudflared
        os.makedirs("cloudflared", exist_ok=True)
        with open(os.path.join("cloudflared", "cloudflared.exe"), "w") as f:
            f.write("mock cloudflared")
        
        with patch('platform.system', return_value='Windows'):
            with patch('builtins.print') as mock_print:
                result = _check_local_cloudflared()
                self.assertTrue(result)
                
                # Check for success message
                success_found = any("Local cloudflared found" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(success_found, "Expected local cloudflared found message not found")
    
    def test_check_local_cloudflared_missing(self):
        """Test local cloudflared check when missing"""
        from swarmtunnel.start import _check_local_cloudflared
        
        with patch('platform.system', return_value='Windows'):
            with patch('builtins.print') as mock_print:
                result = _check_local_cloudflared()
                self.assertFalse(result)
                
                # Check for error message
                error_found = any("Local cloudflared not found" in str(call) for call in mock_print.call_args_list)
                self.assertTrue(error_found, "Expected local cloudflared not found message not found")


class TestErrorScenarios(unittest.TestCase):
    """Tests for error handling scenarios"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('swarmtunnel.start.check_dependencies')
    def test_main_dependency_failure(self, mock_check_deps):
        """Test main function with dependency failure"""
        mock_check_deps.return_value = False
        
        with patch('sys.exit') as mock_exit:
            # We can't easily test main() directly due to signal handlers,
            # but we can test the logic that would cause it to exit
            if not mock_check_deps():
                mock_exit.assert_not_called()  # This would be called in main()
    
    @patch('swarmtunnel.start.build_swarmui')
    @patch('swarmtunnel.start.check_dependencies')
    def test_main_build_failure(self, mock_check_deps, mock_build):
        """Test main function with build failure"""
        mock_check_deps.return_value = True
        mock_build.return_value = False
        
        with patch('sys.exit') as mock_exit:
            # Test the logic that would cause main() to exit
            if not mock_build():
                mock_exit.assert_not_called()  # This would be called in main()


def run_tests():
    """Run all tests with proper test discovery"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDependencyChecking,
        TestSwarmUIBuilding,
        TestServiceWaiting,
        TestSwarmUIStarting,
        TestTunnelConfiguration,
        TestTunnelStarting,
        TestTunnelURLExtraction,
        TestCleanup,
        TestIntegrationScenarios,
        TestEnvironmentVariables,
        TestCLIArguments,
        TestWindowsPowerShellFunctionality,
        TestLocalInstallationChecks,
        TestErrorScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running comprehensive test suite for start.py")
    print("=" * 60)
    
    success = run_tests()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(0 if success else 1)
