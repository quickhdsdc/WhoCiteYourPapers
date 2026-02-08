import click
from .step1_fetch_citations import main as fetch_citations
from .step2_fetch_author_details import main as fetch_details
from .step3_analyze_results import main as analyze
from .step4_filter_authors import main as filter_authors
from .step5_research_authors import main as research
from .step6_merge_results import main as merge

@click.group()
def cli():
    """WhoCiteYourPapers CLI"""
    pass

@cli.command(name="fetch-citations")
def cmd_fetch_citations():
    """Fetch citations for papers in my.bib"""
    fetch_citations()

@cli.command(name="fetch-authors")
def cmd_fetch_authors():
    """Fetch author details from Semantic Scholar"""
    fetch_details()

@cli.command(name="analyze")
def cmd_analyze():
    """Analyze results and generate CSV"""
    analyze()

@cli.command(name="filter")
def cmd_filter():
    """Filter high-impact authors"""
    filter_authors()

@cli.command(name="research")
@click.option("--limit", default=None, type=int, help="Limit number of authors to research")
def cmd_research(limit):
    """Research authors using Google GenAI"""
    research(limit=limit)

@cli.command(name="merge")
def cmd_merge():
    """Merge research results into main CSV"""
    merge()

@cli.command(name="run-all")
@click.option("--limit-research", default=None, type=int, help="Limit for research step")
def cmd_run_all(limit_research):
    """Run the entire pipeline"""
    click.echo("Step 1: Fetching Citations...")
    fetch_citations()
    click.echo("\nStep 2: Fetching Author Details...")
    fetch_details()
    click.echo("\nStep 3: Analyzing Results...")
    analyze()
    click.echo("\nStep 4: Filtering Authors...")
    filter_authors()
    click.echo("\nStep 5: Researching Authors...")
    research(limit=limit_research)
    click.echo("\nStep 6: Merging Results...")
    merge()
    click.echo("\nPipeline Complete!")

if __name__ == "__main__":
    cli()
