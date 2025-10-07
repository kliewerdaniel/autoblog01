#!/usr/bin/env python3
"""
RSS Feed Fetcher and Blog Topic Generator

Fetches articles from RSS feeds listed in feeds.yaml, summarizes them using Ollama LLM
to create a blog topic prompt, and then passes that prompt to the agent system to generate
a blog post.
"""

import asyncio
import aiohttp
import feedparser
import yaml
import re
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import sys

# Add paths for agent imports
current_dir = Path(__file__).parent
agent_path = current_dir / "agent"
if str(agent_path) not in sys.path:
    sys.path.insert(0, str(agent_path))
if str(current_dir) not in sys.path:  # for run_agentic_blog.py
    sys.path.insert(0, str(current_dir))

from agent.orchestrator import BlogGenerationOrchestrator
from agent.llm_client import OllamaClient
from agent.config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticleData:
    """Simplified Article data class for fetching."""
    def __init__(self, title: str, content: str, url: str, source: str, published: datetime):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published = published


class FeedFetcher:
    def __init__(self, feeds_file: str = "feeds.yaml"):
        self.feeds_file = feeds_file
        self.logger = logger
        self.max_articles_per_feed = 10  # Limit per feed to avoid overload
        self.min_article_length = 100  # Minimum content length

    async def fetch_feeds(self, batch_size: int = 5) -> List[ArticleData]:
        """Fetch articles from all RSS feeds in batch."""
        self.logger.info("Starting to fetch RSS feeds...")

        with open(self.feeds_file, 'r') as f:
            feeds_config = yaml.safe_load(f)

        feeds = feeds_config.get('feeds', [])
        articles = []

        total_feeds = len(feeds)
        self.logger.info(f"Processing {total_feeds} RSS feeds...")

        for i in range(0, len(feeds), batch_size):
            batch = feeds[i:i+batch_size]
            async with aiohttp.ClientSession() as session:
                tasks = [self.fetch_single_feed(session, feed_url.strip()) for feed_url in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                batch_articles = 0
                for result in results:
                    if isinstance(result, list):
                        articles.extend(result)
                        batch_articles += len(result)

            self.logger.info(f"Batch {i//batch_size + 1}: Fetched {batch_articles} articles from {len(batch)} feeds")

            # Small delay between batches
            if i + batch_size < len(feeds):
                await asyncio.sleep(0.5)

        self.logger.info(f"Total articles fetched: {len(articles)}")
        return articles

    async def fetch_single_feed(self, session: aiohttp.ClientSession, feed_url: str) -> List[ArticleData]:
        """Fetch articles from a single RSS feed."""
        try:
            async with session.get(feed_url, timeout=30) as response:
                response.raise_for_status()
                content = await response.text()

            feed = feedparser.parse(content)
            articles = []

            fetched_count = 0
            for entry in feed.entries:
                if fetched_count >= self.max_articles_per_feed:
                    break

                article_content = self.extract_content(entry)
                if len(article_content) < self.min_article_length:
                    continue

                article = ArticleData(
                    title=entry.get('title', 'No Title'),
                    content=article_content,
                    url=entry.get('link', ''),
                    source=feed.feed.get('title', feed_url),
                    published=self.parse_date(entry)
                )

                articles.append(article)
                fetched_count += 1

            self.logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            return articles

        except Exception as e:
            self.logger.warning(f"Error fetching {feed_url}: {e}")
            return []

    def extract_content(self, entry) -> str:
        """Extract and clean content from RSS entry."""
        content = ""
        for field in ['content', 'summary', 'description']:
            if hasattr(entry, field):
                if field == 'content' and entry.content:
                    content = entry.content[0].value if entry.content else ""
                else:
                    content = getattr(entry, field, "")
                break

        # Clean HTML tags
        return re.sub(r'<[^>]+>', '', content).strip()

    def parse_date(self, entry) -> datetime:
        """Parse publication date from RSS entry."""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
        except:
            pass
        return datetime.now()


class BlogTopicGenerator:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.logger = logger

    async def summarize_to_topic(self, articles: List[ArticleData]) -> str:
        """Use Ollama to summarize articles and formulate a blog topic prompt."""
        if not articles:
            return "News Summary and Blog Topic"

        # Prepare articles summary for LLM
        articles_text = []
        for i, article in enumerate(articles[:20]):  # Limit to first 20 to avoid token limits
            articles_text.append(f"Article {i+1}:\nTitle: {article.title}\nContent: {article.content[:500]}...\nSource: {article.source}\n")

        articles_summary = "\n".join(articles_text)

        prompt = f"""
Based on the following collection of recent news articles, please:

1. Summarize the key themes and topics covered in these articles.
2. Identify any connecting patterns or trends across the stories.
3. Suggest a compelling blog post topic that weaves together these themes.
4. Provide a detailed prompt for a blog writer to create an engaging article on this topic.

Articles:
{articles_summary}

Please respond with:
- A brief summary of the articles
- The suggested blog post topic
- A detailed writing prompt suitable for an AI blog generator
"""

        self.logger.info("Sending articles summary to Ollama for topic generation...")

        try:
            result = await self.ollama_client.generate(
                prompt,
                system_prompt="You are a creative blog topic strategist who identifies connections in news and suggests compelling writing prompts.",
                temperature=0.7
            )
            return result if result else "News Summary and Blog Topic"
        except Exception as e:
            self.logger.error(f"Error generating topic with Ollama: {e}")
            return "News Summary and Blog Topic"


class AgentBlogGenerator:
    def __init__(self):
        self.orchestrator = None
        self.logger = logger

    async def generate_blog(self, topic_prompt: str) -> bool:
        """Generate a blog post using the agent system."""
        self.logger.info("Starting blog generation with agent system...")

        try:
            # Initialize orchestrator
            self.orchestrator = BlogGenerationOrchestrator()

            # Default generation specs
            spec_data = {
                'topic': topic_prompt,
                'style': 'technical',
                'length': 'long',  # Changed to long to allow more words
                'tone': 'informative',
                'min_words': 1500,
                'max_words': 2500,
                'categories': ['News', 'Social Impact', 'Technology'],
                'tags': ['news', 'trends', 'analysis']
            }

            self.logger.info(f"Generating blog post for topic: {topic_prompt[:100]}...")

            result = await self.orchestrator.generate_blog_post(topic_prompt, spec_data)

            if result.success:
                self.logger.info(f"Blog post generated successfully: {result.file_path}")
                return True
            else:
                self.logger.error(f"Blog generation failed: {result.error}")
                return False

        except Exception as e:
            self.logger.error(f"Error in agent blog generation: {e}")
            return False


async def main():
    """Main workflow: Fetch feeds -> Generate topic -> Create blog post."""
    logger.info("🚀 Starting RSS Feed Fetcher and Blog Generator")

    # Step 1: Fetch RSS feeds
    fetcher = FeedFetcher("feeds.yaml")
    articles = await fetcher.fetch_feeds(batch_size=5)

    if not articles:
        logger.error("No articles fetched. Cannot proceed.")
        return False

    # Step 2: Generate blog topic from articles
    topic_generator = BlogTopicGenerator()
    blog_topic = await topic_generator.summarize_to_topic(articles)

    logger.info(f"Generated blog topic: {blog_topic[:200]}...")

    # Step 3: Generate blog post using agent
    blog_generator = AgentBlogGenerator()
    success = await blog_generator.generate_blog(blog_topic)

    if success:
        logger.info("🎉 Blog generation workflow completed successfully!")
    else:
        logger.error("❌ Blog generation workflow failed.")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
