#!/usr/bin/env python3
"""
Agentic Blog Generation - Command Line Script

This script provides a simple command-line interface to run the agentic blog generation workflow.
It takes a prompt as input and generates a highly detailed, structured blog post using iterative refinement agents.

Usage:
    python3 run_agentic_blog.py --prompt "Your blog post topic here"
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, Any
import argparse

# Add the current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from agent.orchestrator import BlogGenerationOrchestrator
from agent.config import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logs_dir / 'agentic_blog.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate blog posts using an agentic LLM workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 run_agentic_blog.py --prompt "Describe how AI can use its own writing as source material for creative self-iteration"

    python3 run_agentic_blog.py --prompt "The future of machine learning" --style technical --length long

Advanced usage:
    python3 run_agentic_blog.py \\
        --prompt "Sustainable energy solutions" \\
        --categories "Environment,Technology" \\
        --tags "renewable,innovation" \\
        --keywords "solar,wind,hydrogen" \\
        --style professional \\
        --length medium \\
        --tone educational
        """
    )

    parser.add_argument(
        '--prompt', '-p',
        required=True,
        help='The blog post topic or prompt to generate content for'
    )

    parser.add_argument(
        '--style', '-s',
        choices=['technical', 'casual', 'professional'],
        default='technical',
        help='Writing style (default: technical)'
    )

    parser.add_argument(
        '--length', '-l',
        choices=['short', 'medium', 'long'],
        default='medium',
        help='Content length (default: medium)'
    )

    parser.add_argument(
        '--categories', '-c',
        help='Comma-separated categories for the post'
    )

    parser.add_argument(
        '--tags', '-t',
        help='Comma-separated tags for the post'
    )

    parser.add_argument(
        '--keywords', '-k',
        help='Comma-separated keywords to incorporate naturally'
    )

    parser.add_argument(
        '--tone',
        choices=['informative', 'persuasive', 'educational'],
        default='informative',
        help='Content tone (default: informative)'
    )

    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum refinement iterations (default: 5)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate setup without actually generating content'
    )

    return parser.parse_args()


def create_generation_spec(args) -> Dict[str, Any]:
    """Create generation specification from parsed arguments."""
    # Word count ranges for different lengths
    word_counts = {
        'short': (600, 1000),
        'medium': (1000, 1500),
        'long': (1500, 2500)
    }

    spec_data = {
        'topic': args.prompt,
        'style': args.style,
        'length': args.length,
        'tone': args.tone,
        'min_words': word_counts[args.length][0],
        'max_words': word_counts[args.length][1]
    }

    # Add optional arrays with defaults
    if args.categories:
        spec_data['categories'] = [cat.strip() for cat in args.categories.split(',')]
    else:
        # Default categories based on content analysis could be added here
        spec_data['categories'] = ["Biography", "Social Impact"]

    if args.tags:
        spec_data['tags'] = [tag.strip() for tag in args.tags.split(',')]
    else:
        # Default tags based on topic
        spec_data['tags'] = ["personal transformation", "philanthropy", "community building"]

    if args.keywords:
        spec_data['keywords'] = [kw.strip() for kw in args.keywords.split(',')]

    return spec_data


async def run_agentic_workflow(spec_data: Dict[str, Any], max_iterations: int = 5) -> bool:
    """Execute the complete agentic blog generation workflow."""
    try:
        # Initialize orchestrator with custom config
        config_override = {
            'max_refinement_iterations': max_iterations
        }

        orchestrator = BlogGenerationOrchestrator(config_override)

        print("🤖 Starting Agentic Blog Generation Workflow...")
        print(f"📝 Topic: {spec_data['topic']}")
        print(f"🎨 Style: {spec_data['style']}, Length: {spec_data['length']}, Tone: {spec_data['tone']}")
        print(f"📊 Word range: {spec_data['min_words']}-{spec_data['max_words']}")
        print()

        print("🔍 Phase 1: Retrieving relevant context from knowledge base...")
        # The orchestrator handles the detailed progress logging

        # Execute the workflow
        result = await orchestrator.generate_blog_post(spec_data['topic'], spec_data)

        print()
        if result.success:
            print("🎉 SUCCESS: Blog post generated and saved!")
            print(f"📄 File: {result.file_path}")
            print(f"🔄 Iterations completed: {result.iterations}")

            # Show preview
            if result.final_content and 'content' in result.final_content:
                content = result.final_content['content']
                word_count = result.final_content.get('word_count', 0)
                print(f"📊 Final word count: {word_count}")

                # First few lines preview
                lines = content.split('\n')[:10]
                preview = '\n'.join(lines)
                if len(content.split('\n')) > 10:
                    preview += '\n...'

                print("\n📖 Content Preview:")
                print("-" * 50)
                print(preview)
                print("-" * 50)

            print()
            print("✅ Post has been automatically ingested into the knowledge base")
            print("🔍 Future blog posts can now reference this content")

            return True
        else:
            print("❌ FAILED: Blog generation unsuccessful")
            print(f"💥 Error: {result.error}")
            if hasattr(result, 'iterations') and result.iterations:
                print(f"🔄 Stopped after {result.iterations} iterations")
            return False

    except Exception as e:
        logger.exception("Workflow execution failed")
        print(f"💥 CRITICAL ERROR: {str(e)}")
        return False


async def validate_setup():
    """Validate that the system is properly configured."""
    print("🔧 Validating Agentic Blog Generation Setup...")
    print()

    checks = []

    # Check Python modules
    try:
        import agent.orchestrator
        import agent.agents
        import agent.config
        import agent.llm_client
        print("✓ Python modules imported")
        checks.append(("✅", "Python modules import successfully"))
    except ImportError as e:
        print(f"✗ Python import error: {e}")
        checks.append(("❌", f"Python import error: {e}"))
        return False

    # Check config
    try:
        from agent.config import config
        print("✓ Configuration loaded successfully")
        checks.append(("✅", f"Configuration loaded (Model: {config.ollama_model})"))
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        checks.append(("❌", f"Configuration error: {e}"))
        return False

    # Check vector store
    try:
        from agent.vector_store import vector_store
        print("✓ Vector store module imported")
        stats = vector_store.get_stats()
        doc_count = stats.get('total_documents', 0)
        print(f"✓ Vector store stats retrieved: {doc_count} documents")
        checks.append(("✅", f"Vector store accessible ({doc_count} documents)"))
    except Exception as e:
        print(f"✗ Vector store error: {e}")
        checks.append(("⚠️", f"Vector store warning: {e}"))

    # Check LLM client
    try:
        from agent.llm_client import llm_client
        print("✓ LLM client module imported")
        # Try a simple test (this might not work with all providers)
        checks.append(("✅", "LLM client initialized"))
    except Exception as e:
        print(f"✗ LLM client error: {e}")
        checks.append(("❌", f"LLM client error: {e}"))
        return False

    # Print results
    for status, message in checks:
        print(f"{status} {message}")

    success_count = sum(1 for s, _ in checks if s == "✅")
    total_checks = len(checks)

    print()
    if success_count == total_checks:
        print("🎉 All checks passed! System is ready for blog generation.")
        return True
    elif success_count >= total_checks - 1:  # Allow one warning
        print("⚠️ System validation completed with minor warnings.")
        return True
    else:
        print("❌ Setup validation failed. Please check your configuration.")
        return False


def main():
    """Main entry point."""
    args = parse_arguments()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🔍 Verbose logging enabled")
    else:
        logging.getLogger().setLevel(logging.INFO)

    print("🚀 Agentic Blog Generation System")
    print("=" * 50)

    # Validate setup if requested
    if args.dry_run:
        print("🧪 DRY RUN MODE: Validating configuration only")
        print()
        success = asyncio.run(validate_setup())
        if success:
            print("\n🎯 Dry run successful! Configuration is valid.")
        else:
            print("\n💥 Dry run failed! Please fix configuration issues.")
        return 0 if success else 1

    # Create generation specification
    spec_data = create_generation_spec(args)

    print(f"🎯 Generating blog post for: '{args.prompt}'")
    print()

    # Execute the workflow
    success = asyncio.run(run_agentic_workflow(spec_data, args.max_iterations))

    print()
    print("=" * 50)
    if success:
        print("🎉 Blog generation completed successfully!")
        return 0
    else:
        print("💥 Blog generation failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
