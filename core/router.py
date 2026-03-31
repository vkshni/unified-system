# Router
import sys
from pathlib import Path
import importlib

# Adding project root to Python Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from config.systems import SYSTEMS
from shared import ui_utils as ui


# Get system info
def get_system_info(system_name):

    if not system_exists(system_name):
        raise ValueError(f"System {system_name} not found")
    return SYSTEMS[system_name]


# Check if system exists
def system_exists(system_name):
    return system_name in SYSTEMS


# Check if system is protected
def is_protected(system_name):

    if not system_exists(system_name):
        return False
    return SYSTEMS[system_name]["protected"]


# Import module
def import_module(module_path):

    try:
        module = importlib.import_module(module_path)
        return module
    except ImportError as e:
        raise ImportError(f"Cannot import {module_path}: {e}")


# Route to shell
def route_to_shell(system_name):

    # Check if system exists
    if not system_exists(system_name):
        raise ValueError(f"System {system_name} not found")

    # Check if authentication required
    if is_protected(system_name):
        from auth.auth_manager import AuthService

        auth = AuthService()
        if not auth.is_authenticated:
            import getpass

            print(f"\n🔒 {SYSTEMS[system_name]['name']} requires authentication")
            password = getpass.getpass("Enter master password: ")

            try:
                if not auth.verify_master(password):
                    print("✗ Authentication failed")
                    return
            except ValueError as e:
                print(f"✗ {e}")
                return

    try:
        system_info = get_system_info(system_name)
        module = import_module(system_info["module"])

        # Call runshell()
        if not hasattr(module, "run_shell"):
            raise AttributeError(
                f"Module {system_info['module']} has no run_shell() function"
            )

        module.run_shell()

    except ImportError as e:
        raise ImportError(f"Error loading {system_name}: {e}")
    except Exception as e:
        raise ImportError(f"Error running {system_name}: {e}")


# Route to command
def route_to_command(system_name, args):

    # Check if system exists
    if not system_exists(system_name):
        raise ValueError(f"System {system_name} not found")

    # Check if authentication required
    if is_protected(system_name):
        from auth.auth_manager import AuthService

        auth = AuthService()

        if not auth.is_authenticated:
            print(f"✗ {SYSTEMS[system_name]['name']} requires authentication")
            print("  Please login first: python main.py <system>")
            return 1

    try:
        system_info = get_system_info(system_name)
        module = import_module(system_info["module"])

        # Call runshell()
        if not hasattr(module, "execute_command"):
            raise AttributeError(
                f"Module {system_info['module']} has no execute_command() function"
            )

        exit_code = module.execute_command(args)
        return exit_code if exit_code is not None else 0

    except ImportError as e:
        print(f"✗ Error loading {system_name}: {e}")
        return 1
    except Exception as e:
        print(f"✗ Error running command: {e}")
        return 1
