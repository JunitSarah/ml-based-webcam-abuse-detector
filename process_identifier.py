"""
Process Identifier Module
Identifies which process is currently accessing the webcam
"""

import psutil
import os
import hashlib
from datetime import datetime
import logging


class ProcessIdentifier:
    """
    Identifies and tracks processes using the webcam
    """
    
    def __init__(self):
        """Initialize the process identifier"""
        self.cache = {}  # Cache process information to avoid repeated lookups
        self.logger = self._setup_logger()
        self.logger.info("ProcessIdentifier initialized")
    
    def _setup_logger(self):
        """Set up logging for this module"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename='logs/process_identifier.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def get_all_processes(self):
        """
        Get information about all running processes
        
        Returns: 
            List of process dictionaries
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'exe': pinfo['exe'],
                    'username': pinfo['username']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Some processes can't be accessed (system processes, etc.)
                pass
        return processes
    
    def get_processes_using_camera(self):
        """
        Find processes that are currently using the webcam
        
        Returns: 
            List of process information dictionaries
        """
        camera_processes = []
        self.logger.info("Scanning for processes using camera...")
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                if self._is_using_camera(proc):
                    process_info = self._extract_process_info(proc)
                    if process_info:
                        camera_processes.append(process_info)
                        self.logger.info(f"Found camera process: {process_info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return camera_processes
    
    def _is_using_camera(self, proc):
        """
        Check if a specific process is using the camera
        
        Methods:
        1. Check open file handles for video devices
        2. Check against known camera applications
        3. Check for specific DLLs loaded (Windows)
        """
        try:
            process_name = proc.info['name'].lower()
            
            # Method 1: Check against known camera applications
            # This is the most reliable method for now
            camera_apps = [
                'zoom', 'teams', 'skype', 'chrome', 'firefox',
                'obs', 'discord', 'slack', 'camera', 'webcam',
                'meet', 'webex', 'facetime', 'whatsapp'
            ]
            
            if any(app in process_name for app in camera_apps):
                # Additional verification: check if process has network activity
                # Camera apps usually have network connections
                try:
                    connections = proc.connections(kind='inet')
                    if len(connections) > 0:
                        return True
                except:
                    # Even without network check, if it's a known app, flag it
                    return True
            
            # Method 2: Check open files (works on Linux/Mac better than Windows)
            try:
                open_files = proc.open_files()
                for file in open_files:
                    file_path = file.path.lower()
                    if 'video' in file_path or 'camera' in file_path:
                        return True
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error checking process: {e}")
        
        return False
    
    def _extract_process_info(self, proc):
        """
        Extract detailed information about a process
        
        Returns: 
            Dictionary with process details
        """
        try:
            info = proc.info
            exe_path = info.get('exe', 'Unknown')
            
            # Get memory info
            try:
                memory_info = proc.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)  # Convert bytes to MB
            except:
                memory_mb = 0
            
            # Get CPU usage
            try:
                cpu_percent = proc.cpu_percent(interval=0.1)
            except:
                cpu_percent = 0
            
            process_data = {
                'pid': info['pid'],
                'name': info['name'],
                'exe_path': exe_path,
                'username': info.get('username', 'Unknown'),
                'exe_hash': self._get_file_hash(exe_path) if exe_path != 'Unknown' else None,
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': round(cpu_percent, 2),
                'memory_mb': round(memory_mb, 2)
            }
            
            return process_data
            
        except Exception as e:
            self.logger.error(f"Error extracting process info: {e}")
            return None
    
    def _get_file_hash(self, filepath):
        """
        Calculate SHA256 hash of the executable file
        This helps identify if the file has been modified (malware detection)
        """
        if not filepath or not os.path.exists(filepath):
            return None
        
        # Check cache first
        if filepath in self.cache:
            return self.cache[filepath]
        
        try:
            sha256_hash = hashlib.sha256()
            
            # Read file in chunks to handle large files
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            file_hash = sha256_hash.hexdigest()
            
            # Cache the result
            self.cache[filepath] = file_hash
            return file_hash
            
        except Exception as e:
            self.logger.error(f"Error calculating hash for {filepath}: {e}")
            return None
    
    def get_network_activity(self, pid):
        """
        Get network connections for a specific process
        This helps detect if the process is sending data over the network
        """
        try:
            proc = psutil.Process(pid)
            connections = proc.connections(kind='inet')
            network_info = []
            
            for conn in connections:
                connection_data = {
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'type': 'TCP' if conn.type == 1 else 'UDP'
                }
                network_info.append(connection_data)
            
            return network_info
            
        except Exception as e:
            self.logger.error(f"Error getting network activity for PID {pid}: {e}")
            return []
    
    def is_trusted_application(self, process_name):
        """
        Check if a process is in the trusted applications list
        """
        trusted_apps = [
            'zoom.exe', 'zoomus.exe',
            'teams.exe', 'ms-teams.exe',
            'skype.exe',
            'chrome.exe',
            'firefox.exe',
            'camera.exe',
            'obs64.exe', 'obs32.exe',
            'discord.exe',
            'slack.exe'
        ]
        return process_name.lower() in trusted_apps


# Test this basic version
if __name__ == "__main__":
    identifier = ProcessIdentifier()
    print("ProcessIdentifier created successfully!")
    
    # Get all processes
    all_processes = identifier.get_all_processes()
    print(f"Found {len(all_processes)} running processes")
    
    # Show first 5 processes
    print("\nFirst 5 processes:")
    for proc in all_processes[:5]:
        print(f"PID: {proc['pid']}, Name: {proc['name']}")
    
    # Check for camera usage
    print("\nScanning for camera usage...")
    camera_processes = identifier.get_processes_using_camera()
    
    if camera_processes:
        print(f"\nFound {len(camera_processes)} process(es) using camera:")
        for proc in camera_processes:
            print(f"\nProcess: {proc['name']}")
            print(f"  PID: {proc['pid']}")
            print(f"  User: {proc['username']}")
            print(f"  CPU: {proc['cpu_percent']}%")
            print(f"  Memory: {proc['memory_mb']} MB")
            print(f"  Path: {proc['exe_path']}")
            if proc['exe_hash']:
                print(f"  Hash: {proc['exe_hash']}")
    else:
        print("No processes currently using camera detected.")