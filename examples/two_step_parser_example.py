#!/usr/bin/env python3
"""Example demonstrating the TwoStepParser usage.

This example shows how to create a CLI tool with flexible global option positioning.
"""

from taskfile_help.two_step_parser import TwoStepParser


def main() -> None:
    """Main entry point for the example CLI."""
    # Create the parser
    parser = TwoStepParser(
        description="Example CLI tool with flexible global options"
    )
    
    # Add global options that can appear anywhere
    parser.add_global_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_global_argument(
        "--config", "-c",
        type=str,
        help="Configuration file path"
    )
    parser.add_global_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    
    # Add 'build' command
    build_cmd = parser.add_command(
        "build",
        help="Build the project",
        description="Build the project with optional optimization"
    )
    build_cmd.add_argument(
        "target",
        help="Build target (e.g., 'release', 'debug')"
    )
    build_cmd.add_argument(
        "--optimize",
        action="store_true",
        help="Enable optimizations"
    )
    
    # Add 'test' command
    test_cmd = parser.add_command(
        "test",
        help="Run tests",
        description="Run test suite with optional coverage"
    )
    test_cmd.add_argument(
        "patterns",
        nargs="*",
        help="Test patterns to match"
    )
    test_cmd.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage reporting"
    )
    
    # Add 'deploy' command
    deploy_cmd = parser.add_command(
        "deploy",
        help="Deploy the application",
        description="Deploy to specified environment"
    )
    deploy_cmd.add_argument(
        "environment",
        choices=["dev", "staging", "prod"],
        help="Deployment environment"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    print(f"Command: {args.command}")
    print(f"Verbose: {args.verbose}")
    print(f"Config: {args.config}")
    print(f"Output: {args.output}")
    print()
    
    if args.command == "build":
        print(f"Building target: {args.target}")
        print(f"Optimize: {args.optimize}")
    elif args.command == "test":
        print(f"Test patterns: {args.patterns}")
        print(f"Coverage: {args.coverage}")
    elif args.command == "deploy":
        print(f"Deploying to: {args.environment}")


if __name__ == "__main__":
    # Example usage:
    # python two_step_parser_example.py --verbose build release
    # python two_step_parser_example.py build release --verbose
    # python two_step_parser_example.py --config app.yml test unit --coverage
    # python two_step_parser_example.py test unit --coverage --config app.yml
    main()
