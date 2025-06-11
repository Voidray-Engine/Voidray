
"""
VoidRay Engine Status Tool
Command-line tool for checking engine health.
"""

import sys
import os

# Add the parent directory to the path so we can import voidray
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import voidray
from voidray.core.engine_validator import print_engine_health_report


def main():
    """Main function for engine status check."""
    print("VoidRay Engine Status Check")
    print("=" * 30)
    
    try:
        # Configure a minimal engine for testing
        engine = voidray.configure(width=800, height=600, title="Status Check", fps=60)
        
        # Initialize systems without starting the game loop
        engine._initialize_systems()
        
        # Generate health report
        print_engine_health_report(engine)
        
        # Cleanup
        engine._cleanup()
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
