#!/usr/bin/env python3
"""Validate the project structure and imports."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Core config imported successfully")
        
        # Test model imports
        from app.models.tunnel import CreateTunnelRequest
        from app.models.ingress import IngressRequest
        print("✅ Models imported successfully")
        
        # Test service imports
        from app.services.registry import TunnelRegistry
        from app.services.tunnel_service import TunnelService
        print("✅ Services imported successfully")
        
        # Test utility imports
        from app.utils.response import ORJSONResponse
        print("✅ Utils imported successfully")
        
        # Test middleware imports
        from app.middleware.cors import setup_cors
        from app.middleware.logging import setup_logging
        print("✅ Middleware imported successfully")
        
        print("\n🎉 All imports successful! Project structure is valid.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)