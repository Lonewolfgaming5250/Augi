"""Device Diagnostic Module for AI Assistant"""
import platform
import psutil
import shutil
import socket
import sys
import os

class DeviceDiagnostic:
    """Runs a full diagnostic check on the host device."""
    def __init__(self):
        self.results = {}
        self.recommendations = []

    def run_all(self):
        self.results['os'] = self.check_os()
        self.results['hardware'] = self.check_hardware()
        self.results['disk'] = self.check_disk()
        self.results['memory'] = self.check_memory()
        self.results['network'] = self.check_network()
        self.results['python'] = self.check_python()
        self.results['env'] = self.check_env()
        self.recommendations = self.suggest_fixes()
        return self.results, self.recommendations

    def check_os(self):
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }

    def check_hardware(self):
        return {
            'cpu_count': psutil.cpu_count(logical=True),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }

    def check_disk(self):
        usage = shutil.disk_usage(os.path.expanduser("~"))
        return {
            'total_gb': round(usage.total / (1024**3), 2),
            'used_gb': round(usage.used / (1024**3), 2),
            'free_gb': round(usage.free / (1024**3), 2),
            'percent_used': round(usage.used / usage.total * 100, 2)
        }

    def check_memory(self):
        mem = psutil.virtual_memory()
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'percent_used': mem.percent
        }

    def check_network(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = None
        return {
            'hostname': socket.gethostname(),
            'ip': ip,
            'interfaces': psutil.net_if_addrs()
        }

    def check_python(self):
        return {
            'version': sys.version,
            'executable': sys.executable,
            'modules': sorted(list(sys.modules.keys()))
        }

    def check_env(self):
        return dict(os.environ)

    def suggest_fixes(self):
        fixes = []
        disk = self.results.get('disk', {})
        mem = self.results.get('memory', {})
        if disk and disk['percent_used'] > 90:
            fixes.append('Disk usage is above 90%. Consider freeing up space or upgrading your drive.')
        if mem and mem['percent_used'] > 90:
            fixes.append('Memory usage is above 90%. Close unused applications or consider adding more RAM.')
        if not self.results['network']['ip']:
            fixes.append('No network IP detected. Check your network connection or adapter.')
        # Add more recommendations as needed
        return fixes

if __name__ == "__main__":
    diag = DeviceDiagnostic()
    results, recommendations = diag.run_all()
    print("DEVICE DIAGNOSTIC RESULTS:")
    for key, val in results.items():
        print(f"\n{key.upper()}:")
        print(val)
    if recommendations:
        print("\nRECOMMENDATIONS:")
        for rec in recommendations:
            print(f"- {rec}")
    else:
        print("\nNo critical issues detected.")
