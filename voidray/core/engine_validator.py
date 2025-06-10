
"""
VoidRay Engine Validator
Comprehensive system health checks and validation.
"""

import sys
import traceback
from typing import List, Dict, Any, Tuple
import pygame


class EngineValidator:
    """
    Validates engine systems and reports issues.
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.validation_results = {}
    
    def validate_all_systems(self) -> Tuple[bool, List[str]]:
        """
        Validate all engine systems.
        
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        # Core system validation
        core_valid, core_errors = self._validate_core_systems()
        errors.extend(core_errors)
        
        # Graphics validation
        gfx_valid, gfx_errors = self._validate_graphics_systems()
        errors.extend(gfx_errors)
        
        # Audio validation (optional)
        audio_valid, audio_errors = self._validate_audio_system()
        if not audio_valid:
            print("Audio validation warnings:", audio_errors)
        
        # Physics validation
        physics_valid, physics_errors = self._validate_physics_system()
        errors.extend(physics_errors)
        
        # Resource validation
        resource_valid, resource_errors = self._validate_resource_systems()
        errors.extend(resource_errors)
        
        return len(errors) == 0, errors
    
    def _validate_core_systems(self) -> Tuple[bool, List[str]]:
        """Validate core engine systems."""
        errors = []
        
        # Check engine instance
        if not self.engine:
            errors.append("Engine instance is None")
            return False, errors
        
        # Check pygame initialization
        if not pygame.get_init():
            errors.append("Pygame is not initialized")
        
        # Check screen
        if not hasattr(self.engine, 'screen') or not self.engine.screen:
            errors.append("Screen not initialized")
        
        # Check clock
        if not hasattr(self.engine, 'clock') or not self.engine.clock:
            errors.append("Clock not initialized")
        
        # Validate configuration
        if self.engine.width <= 0 or self.engine.height <= 0:
            errors.append(f"Invalid screen dimensions: {self.engine.width}x{self.engine.height}")
        
        if self.engine.target_fps <= 0:
            errors.append(f"Invalid target FPS: {self.engine.target_fps}")
        
        return len(errors) == 0, errors
    
    def _validate_graphics_systems(self) -> Tuple[bool, List[str]]:
        """Validate graphics and rendering systems.""" 
        errors = []
        
        # Check renderer
        if not hasattr(self.engine, 'renderer') or not self.engine.renderer:
            errors.append("Renderer not initialized")
            return False, errors
        
        # Test basic rendering functions
        try:
            self.engine.renderer.clear()
        except Exception as e:
            errors.append(f"Renderer clear() failed: {e}")
        
        try:
            # Test text rendering
            test_size = self.engine.renderer.get_text_size("test", 24)
            if not isinstance(test_size, tuple) or len(test_size) != 2:
                errors.append("Text size calculation failed")
        except Exception as e:
            errors.append(f"Text rendering test failed: {e}")
        
        return len(errors) == 0, errors
    
    def _validate_audio_system(self) -> Tuple[bool, List[str]]:
        """Validate audio system (non-critical)."""
        warnings = []
        
        if not hasattr(self.engine, 'audio_manager'):
            warnings.append("Audio manager not found")
            return False, warnings
        
        if not self.engine.audio_manager.available:
            warnings.append("Audio system not available (expected on some systems)")
        
        return True, warnings  # Audio is non-critical
    
    def _validate_physics_system(self) -> Tuple[bool, List[str]]:
        """Validate physics system."""
        errors = []
        
        if not hasattr(self.engine, 'physics_engine') or not self.engine.physics_engine:
            errors.append("Physics engine not initialized")
            return False, errors
        
        # Test basic physics functions
        try:
            collider_count = len(self.engine.physics_engine.colliders)
            if collider_count < 0:
                errors.append("Invalid collider count")
        except Exception as e:
            errors.append(f"Physics system test failed: {e}")
        
        return len(errors) == 0, errors
    
    def _validate_resource_systems(self) -> Tuple[bool, List[str]]:
        """Validate resource management systems."""
        errors = []
        
        # Check asset loader
        if not hasattr(self.engine, 'asset_loader') or not self.engine.asset_loader:
            errors.append("Asset loader not initialized")
        
        # Check resource manager
        if hasattr(self.engine, 'resource_manager') and self.engine.resource_manager:
            try:
                # Test resource manager
                memory_usage = self.engine.resource_manager.get_memory_usage()
                if not isinstance(memory_usage, dict):
                    errors.append("Resource manager get_memory_usage() should return a dictionary")
                elif memory_usage.get('total_memory_mb', 0) < 0:
                    errors.append("Invalid resource manager memory usage")
            except Exception as e:
                errors.append(f"Resource manager test failed: {e}")
        
        return len(errors) == 0, errors
    
    def run_performance_check(self) -> Dict[str, Any]:
        """Run basic performance checks."""
        results = {
            'fps_stable': True,
            'memory_usage_mb': 0,
            'object_count': 0,
            'warnings': []
        }
        
        try:
            # Check FPS
            current_fps = self.engine.get_fps()
            target_fps = self.engine.target_fps
            
            if current_fps < target_fps * 0.8:
                results['fps_stable'] = False
                results['warnings'].append(f"FPS below target: {current_fps:.1f}/{target_fps}")
            
            # Check object count
            if self.engine.current_scene:
                object_count = len(self.engine.current_scene.objects)
                results['object_count'] = object_count
                
                if object_count > 1000:
                    results['warnings'].append(f"High object count: {object_count}")
            
            # Check memory usage
            if hasattr(self.engine, 'resource_manager') and self.engine.resource_manager:
                memory_usage = self.engine.resource_manager.get_memory_usage()
                results['memory_usage_mb'] = memory_usage / 1024 / 1024
                
                if results['memory_usage_mb'] > 500:
                    results['warnings'].append(f"High memory usage: {results['memory_usage_mb']:.1f}MB")
        
        except Exception as e:
            results['warnings'].append(f"Performance check error: {e}")
        
        return results
    
    def generate_health_report(self) -> str:
        """Generate a comprehensive health report."""
        report_lines = [
            "VoidRay Engine Health Report",
            "=" * 30
        ]
        
        # System validation
        valid, errors = self.validate_all_systems()
        
        if valid:
            report_lines.append("✅ All systems validated successfully")
        else:
            report_lines.append("❌ System validation failed:")
            for error in errors:
                report_lines.append(f"  - {error}")
        
        # Performance check
        perf_results = self.run_performance_check()
        report_lines.append(f"\nPerformance Status:")
        report_lines.append(f"  FPS Stable: {'✅' if perf_results['fps_stable'] else '❌'}")
        report_lines.append(f"  Memory Usage: {perf_results['memory_usage_mb']:.1f}MB")
        report_lines.append(f"  Object Count: {perf_results['object_count']}")
        
        if perf_results['warnings']:
            report_lines.append("\nPerformance Warnings:")
            for warning in perf_results['warnings']:
                report_lines.append(f"  ⚠️ {warning}")
        
        # System info
        report_lines.append(f"\nSystem Information:")
        report_lines.append(f"  Python Version: {sys.version}")
        report_lines.append(f"  Pygame Version: {pygame.version.ver}")
        report_lines.append(f"  Engine Resolution: {self.engine.width}x{self.engine.height}")
        report_lines.append(f"  Target FPS: {self.engine.target_fps}")
        
        return "\n".join(report_lines)


def validate_engine(engine) -> bool:
    """
    Quick engine validation function.
    
    Returns:
        True if engine is healthy, False otherwise
    """
    validator = EngineValidator(engine)
    valid, errors = validator.validate_all_systems()
    
    if not valid:
        print("Engine validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    return valid


def print_engine_health_report(engine):
    """Print a detailed health report for the engine."""
    validator = EngineValidator(engine)
    report = validator.generate_health_report()
    print(report)
