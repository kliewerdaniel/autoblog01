#!/usr/bin/env python3
"""
CLI interface for the Agentic Blog Post Generation System.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

# Handle both module and direct execution
current_dir = Path(__file__).parent
if current_dir not in sys.path:
    sys.path.insert(0, str(current_dir))

from config import config
from ingest import ingest_knowledge_base, get_knowledge_base_stats, search_knowledge_base
from agents.researcher import ResearcherAgent
from orchestrator import BlogGenerationOrchestrator
from models import GenerationSpec
from utils.validator import validate_generation_spec

# Ensure data directories exist
config.logs_dir.mkdir(parents=True, exist_ok=True)
config.vector_db_dir.mkdir(parents=True, exist_ok=True)
config.cache_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logs_dir / config.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config-file', type=click.Path(exists=True), help='Path to custom config file')
def cli(verbose, config_file):
    """Agentic Blog Post Generation System CLI"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if config_file:
        # Load custom config if provided
        pass  # TODO: Implement custom config loading


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force re-ingestion of all posts')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def ingest(force, verbose):
    """Ingest blog posts into the knowledge base."""
    with console.status("[bold green]Ingesting knowledge base...", spinner="dots"):
        try:
            result = ingest_knowledge_base(force=force, verbose=verbose)

            if "error" in result:
                console.print(f"[red]Error:[/red] {result['error']}")
                return

            # Display results
            table = Table(title="Ingestion Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Total Posts", str(result.get("total_posts", 0)))
            table.add_row("Processed Posts", str(result.get("processed_posts", 0)))
            table.add_row("Total Chunks", str(result.get("total_chunks", 0)))
            table.add_row("Vector Store Documents", str(result.get("vector_store_stats", {}).get("total_documents", 0)))

            console.print(table)
            console.print("[green]✓ Knowledge base ingestion complete![/green]")

        except Exception as e:
            console.print(f"[red]Error during ingestion:[/red] {e}")
            logger.exception("Ingestion failed")


@cli.command()
@click.argument('topic', required=True)
@click.option('--style', '-s', default='technical',
              type=click.Choice(['technical', 'casual', 'professional']),
              help='Writing style')
@click.option('--length', '-l', default='medium',
              type=click.Choice(['short', 'medium', 'long']),
              help='Content length')
@click.option('--categories', '-c', help='Comma-separated categories')
@click.option('--tags', '-t', help='Comma-separated tags')
@click.option('--keywords', '-k', help='Comma-separated keywords')
@click.option('--tone', default='informative',
              type=click.Choice(['informative', 'persuasive', 'educational']),
              help='Content tone')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--dry-run', is_flag=True, help='Dry run (no actual generation)')
def generate(topic, style, length, categories, tags, keywords, tone, interactive, output, dry_run):
    """Generate a blog post based on topic and specifications."""
    console.print(f"[bold blue]Generating blog post: {topic}[/bold blue]")

    # Parse parameters
    word_counts = {'short': (600, 1000), 'medium': (1000, 1500), 'long': (1500, 2500)}

    spec_data = {
        'topic': topic,
        'style': style,
        'length': length,
        'tone': tone,
        'min_words': word_counts[length][0],
        'max_words': word_counts[length][1]
    }

    if categories:
        spec_data['categories'] = [cat.strip() for cat in categories.split(',')]
    if tags:
        spec_data['tags'] = [tag.strip() for tag in tags.split(',')]
    if keywords:
        spec_data['keywords'] = [kw.strip() for kw in keywords.split(',')]

    # Validate spec
    spec_validation = validate_generation_spec(spec_data)
    if not spec_validation.is_valid:
        console.print("[red]Invalid generation spec:[/red]")
        for error in spec_validation.errors:
            console.print(f"  - {error}")
        return

    console.print(f"[green]✓ Specification validated[/green]")

    if dry_run:
        console.print("[yellow]Dry run mode - no generation performed[/yellow]")
        console.print(f"Topic: {topic}")
        console.print(f"Word range: {spec_data['min_words']}-{spec_data['max_words']}")
        return

    # Generate content using agentic workflow
    with console.status("[bold green]Generating content...", spinner="dots"):
        try:
            # Run the agentic workflow
            orchestrator = BlogGenerationOrchestrator()
            workflow_result = asyncio.run(orchestrator.generate_blog_post(spec_data['topic'], spec_data))

            if not workflow_result.success:
                console.print(f"[red]Generation failed:[/red] {workflow_result.error}")
                return

            # Display results
            console.print("[green]✓ Blog post generated successfully![/green]")
            console.print(f"[green]✓ Completed in {workflow_result.iterations} iterations[/green]")

            if output:
                # User specified output path - still save there for compatibility
                from utils.file_utils import write_blog_post
                from utils.file_utils import generate_frontmatter
                from models import GeneratedContent, GenerationSpec

                # Create content objects
                spec_obj = GenerationSpec(**spec_data)
                gen_content = GeneratedContent(
                    title=spec_data['topic'],
                    content=workflow_result.final_content['content'],
                    frontmatter={
                        'title': spec_data['topic'],
                        'date': None,
                        'categories': spec_data.get('categories', []),
                        'tags': spec_data.get('tags', [])
                    }
                )

                frontmatter = generate_frontmatter(spec_obj, gen_content)
                saved_path = write_blog_post(Path(output).name, frontmatter, workflow_result.final_content['content'])
                console.print(f"[green]✓ Saved blog post to: {saved_path}[/green]")
            else:
                # Orchestrator already saved to ./content/posts/
                console.print(f"[green]✓ Auto-saved blog post to: {workflow_result.file_path}[/green]")
                console.print(f"[green]✓ Ingested into knowledge base for future retrieval[/green]")

            # Preview (first 500 chars)
            content = workflow_result.final_content['content']
            preview = content[:500] + "..." if len(content) > 500 else content
            console.print("\n[bold]Preview:[/bold]")
            console.print(Panel(preview))

        except Exception as e:
            console.print(f"[red]Error during generation:[/red] {e}")
            logger.exception("Generation failed")


@cli.command()
@click.argument('query', required=True)
@click.option('--top-k', '-k', default=5, help='Number of results to return')
def search(query, top_k):
    """Search the knowledge base for relevant content."""
    with console.status(f"[bold green]Searching for '{query}'...", spinner="dots"):
        try:
            results = search_knowledge_base(query, top_k=top_k)

            if not results:
                console.print("[yellow]No results found.[/yellow]")
                return

            # Display results
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Title", style="cyan", no_wrap=True)
            table.add_column("Content Preview", style="white")
            table.add_column("Relevance", style="magenta", justify="right")

            for result in results:
                title = result.get('title', 'Unknown')[:50]
                content = result.get('content', '')[:100] + "..."
                relevance = ".3f"

                table.add_row(title, content, relevance)

            console.print(table)

        except Exception as e:
            console.print(f"[red]Search failed:[/red] {e}")


@cli.command()
def stats():
    """Display knowledge base statistics."""
    try:
        stats = get_knowledge_base_stats()

        if "error" in stats:
            console.print(f"[red]Error getting stats:[/red] {stats['error']}")
            return

        console.print("[bold blue]Knowledge Base Statistics[/bold blue]")

        # Vector store stats
        vs_stats = stats.get("vector_database", {})
        console.print(f"Vector Store: {vs_stats.get('provider', 'Unknown')}")
        console.print(f"Total Documents: {vs_stats.get('total_documents', 0)}")

        # Manifest stats
        manifest = stats.get("manifest", {})
        console.print(f"Total Blog Posts: {manifest.get('total_posts', 0)}")
        console.print(f"Last Updated: {manifest.get('last_updated', 'Never')}")

    except Exception as e:
        console.print(f"[red]Error getting stats:[/red] {e}")


async def generate_blog_post(spec_data: Dict[str, Any]) -> str:
    """Main agentic blog post generation workflow."""
    # Initialize the orchestrator
    orchestrator = BlogGenerationOrchestrator()

    # Execute the agentic workflow
    result = await orchestrator.generate_blog_post(
        spec_data['topic'],
        spec_data
    )

    if not result.success:
        raise Exception(f"Generation failed: {result.error}")

    # Return the final content
    return result.final_content['content'] if result.final_content else ""


def facts_to_markdown(facts: list) -> str:
    """Convert list of facts to markdown bullets."""
    if not facts:
        return "• No specific facts available from knowledge base\n"
    return "\n".join(f"• {fact}" for fact in facts[:5]) + "\n"


def topics_to_markdown(topics: list) -> str:
    """Convert list of topics to markdown bullets."""
    if not topics:
        return "• No related topics found\n"
    return "\n".join(f"• {topic}" for topic in topics[:5]) + "\n"


if __name__ == '__main__':
    cli()
