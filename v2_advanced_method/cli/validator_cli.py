"""Command-line interface for network validation tools."""

import argparse
import sys
import os
from typing import Optional
import json
from pathlib import Path

from ..converter.network_converter import NetworkConverter
from ..validation.network_validator import NetworkValidator
from .visualization.network_visualizer import NetworkVisualizer

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Road Network Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a network file
  python -m src.cli.validator_cli validate network.xml
  
  # Validate and visualize results
  python -m src.cli.validator_cli validate --visualize network.xml
  
  # Convert and validate a network file
  python -m src.cli.validator_cli convert --validate network.xml
  
  # Visualize network statistics
  python -m src.cli.validator_cli visualize --stats network.xml
        """
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a network file")
    validate_parser.add_argument("input_file", help="Input network file")
    validate_parser.add_argument("--visualize", action="store_true",
                               help="Visualize validation results")
    validate_parser.add_argument("--output", help="Output file for visualization")
    validate_parser.add_argument("--strict", action="store_true",
                               help="Treat warnings as errors")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a network file")
    convert_parser.add_argument("input_file", help="Input network file")
    convert_parser.add_argument("--output", help="Output file for converted network")
    convert_parser.add_argument("--validate", action="store_true",
                              help="Validate after conversion")
    convert_parser.add_argument("--visualize", action="store_true",
                              help="Visualize after conversion")
    
    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Visualize network")
    visualize_parser.add_argument("input_file", help="Input network file")
    visualize_parser.add_argument("--output", help="Output file for visualization")
    visualize_parser.add_argument("--stats", action="store_true",
                                help="Show network statistics")
    visualize_parser.add_argument("--labels", action="store_true",
                                help="Show edge and junction labels")
    visualize_parser.add_argument("--color-by", choices=["speed", "priority", "function"],
                                default="speed", help="Attribute to color edges by")
    visualize_parser.add_argument("--density", action="store_true",
                                help="Show network density")
    visualize_parser.add_argument("--speed-dist", action="store_true",
                                help="Show speed distribution")
    
    return parser.parse_args()

def validate_network(input_file: str, visualize: bool = False,
                    output_file: Optional[str] = None,
                    strict: bool = False) -> int:
    """Validate a network file.
    
    Args:
        input_file: Path to input network file
        visualize: Whether to visualize results
        output_file: Output file for visualization
        strict: Whether to treat warnings as errors
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Load network data
        with open(input_file, 'r') as f:
            network_data = json.load(f)
        
        # Validate network
        validator = NetworkValidator()
        result = validator.validate_network(network_data)
        
        # Print validation results
        if result.errors:
            print("Validation Errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("\nValidation Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        # Visualize if requested
        if visualize:
            visualizer = NetworkVisualizer()
            visualizer.visualize_validation_results(result, output_file)
        
        # Return appropriate exit code
        if result.errors or (strict and result.warnings):
            return 1
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def convert_network(input_file: str, output_file: Optional[str] = None,
                   validate: bool = False, visualize: bool = False) -> int:
    """Convert a network file.
    
    Args:
        input_file: Path to input network file
        output_file: Output file for converted network
        validate: Whether to validate after conversion
        visualize: Whether to visualize after conversion
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Convert network
        converter = NetworkConverter()
        network_data = converter.convert_network(input_file)
        
        # Save converted network
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(network_data, f, indent=2)
        
        # Validate if requested
        if validate:
            return validate_network(input_file, visualize, output_file)
        
        # Visualize if requested
        if visualize:
            visualizer = NetworkVisualizer()
            visualizer.visualize_network(network_data, output_file)
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def visualize_network(input_file: str, output_file: Optional[str] = None,
                     show_stats: bool = False, show_labels: bool = False,
                     color_by: str = "speed", show_density: bool = False,
                     show_speed_dist: bool = False) -> int:
    """Visualize a network.
    
    Args:
        input_file: Path to input network file
        output_file: Output file for visualization
        show_stats: Whether to show network statistics
        show_labels: Whether to show edge and junction labels
        color_by: Attribute to color edges by
        show_density: Whether to show network density
        show_speed_dist: Whether to show speed distribution
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Load network data
        with open(input_file, 'r') as f:
            network_data = json.load(f)
        
        # Create visualizer
        visualizer = NetworkVisualizer()
        
        # Visualize network
        if show_density:
            visualizer.visualize_network_density(output_file)
        elif show_speed_dist:
            visualizer.visualize_speed_distribution(output_file)
        else:
            visualizer.visualize_network(network_data, output_file,
                                       show_statistics=show_stats,
                                       show_labels=show_labels,
                                       color_by=color_by)
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    if args.command == "validate":
        return validate_network(args.input_file, args.visualize,
                              args.output, args.strict)
    
    elif args.command == "convert":
        return convert_network(args.input_file, args.output,
                             args.validate, args.visualize)
    
    elif args.command == "visualize":
        return visualize_network(args.input_file, args.output,
                               args.stats, args.labels,
                               args.color_by, args.density,
                               args.speed_dist)
    
    else:
        print("Error: No command specified", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 