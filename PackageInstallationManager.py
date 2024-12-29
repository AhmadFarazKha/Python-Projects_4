import subprocess
import os
import sys
import venv

class PackageManager:
    def __init__(self):
        self.installed_packages = {}  # Track installed packages and versions

    def create_virtual_environment(self, env_name):
        try:
            venv.create(env_name, with_pip=True)
            print(f"Virtual environment '{env_name}' created successfully.")
            if sys.platform == "win32":
                activate_script = os.path.join(env_name, "Scripts", "activate")
            else:
                activate_script = os.path.join(env_name, "bin", "activate")
            print(f"Activate the environment using: {activate_script}")
        except Exception as e:
            print(f"Error creating virtual environment: {e}")

    def install_package(self, package_name, version=None):
        install_command = [sys.executable, "-m", "pip", "install"]
        if version:
            install_command.append(f"{package_name}=={version}")
        else:
            install_command.append(package_name)

        try:
            subprocess.check_call(install_command)
            print(f"Package '{package_name}' installed successfully.")
            self.track_package(package_name, version)
        except subprocess.CalledProcessError as e:
            print(f"Error installing package '{package_name}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def uninstall_package(self, package_name):
        uninstall_command = [sys.executable, "-m", "pip", "uninstall", "-y", package_name]
        try:
            subprocess.check_call(uninstall_command)
            print(f"Package '{package_name}' uninstalled successfully.")
            self.untrack_package(package_name)
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling package '{package_name}': {e}")

    def track_package(self, package_name, version):
        try:
            import importlib
            package = importlib.import_module(package_name)
            if hasattr(package, '__version__'):
                self.installed_packages[package_name] = package.__version__
            elif version:
                self.installed_packages[package_name] = version
            else:
                self.installed_packages[package_name] = "Version information not available"
        except ImportError:
            print(f"Could not automatically determine version of {package_name}")
            if version:
                self.installed_packages[package_name] = version
            else:
                self.installed_packages[package_name] = "Version information not available"

    def untrack_package(self, package_name):
        if package_name in self.installed_packages:
            del self.installed_packages[package_name]

    def list_installed_packages(self):
        if self.installed_packages:
            print("Installed packages:")
            for package, version in self.installed_packages.items():
                print(f"- {package}: {version}")
        else:
            print("No packages installed.")

# Example Usage
manager = PackageManager()

manager.create_virtual_environment("my_env") # Create a Virtual Environment

# Activate the virtual environment before installing packages
# Windows: my_env\Scripts\activate
# Linux/macOS: source my_env/bin/activate

manager.install_package("requests")
manager.install_package("numpy", "1.23.0") # Install a specific version
manager.list_installed_packages()
manager.uninstall_package("numpy")
manager.list_installed_packages()
manager.install_package("nonexistent_package") # Example of handling installation failure
