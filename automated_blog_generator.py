#!/usr/bin/env python3
"""
Automated RSS Feed Fetcher and Blog Generator

Fetches articles from RSS feeds, ingests them into the knowledge base,
generates rich context from the ENTIRE database of previously ingested files,
and creates blog posts colored by this completely interconnected information base.

This script automates the complete pipeline:
1. Fetch RSS feeds and articles
2. Ingest articles into vector database
3. Retrieve enhanced context from FULL knowledge base (all blog posts + all RSS articles)
4. Generate blog posts with richer context and connections
5. Save and ingest the final blog post back into knowledge base

Usage:
    python3 automated_blog_generator.py
"""

import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import aiohttp
import feedparser
import yaml
import re
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
from agent.vector_store import vector_store
from agent.models import DocumentChunk
from agent.utils.parser import chunk_content, clean_markdown
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_blog_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ArticleData:
    """Data class for fetched RSS articles."""
    def __init__(self, title: str, content: str, url: str, source: str, published: datetime):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published = published


class RSSIngestor:
    """Handles ingestion of RSS articles into the vector database."""

    def __init__(self):
        self.logger = logger
        self.embed_model = SentenceTransformer(config.embedding_model)

    async def ingest_articles(self, articles: List[ArticleData]) -> Dict[str, Any]:
        """Ingest RSS articles into the vector database for retrieval."""
        self.logger.info(f"Ingesting {len(articles)} RSS articles into knowledge base...")

        if not articles:
            return {"error": "No articles to ingest"}

        processed_texts = []
        processed_metadata = []
        processed_ids = []
        total_chunks = 0

        for i, article in enumerate(articles):
            try:
                # Clean content for better embeddings
                clean_content = clean_markdown(article.content)

                # Chunk the content
                chunks = chunk_content(
                    clean_content,
                    chunk_size=config.chunk_size,
                    overlap=config.chunk_overlap
                )

                if not chunks:
                    self.logger.warning(f"No chunks generated for article: {article.title}")
                    continue

                # Generate embeddings for this article's chunks
                embeddings = self.embed_model.encode(chunks, show_progress_bar=False)

                # Process each chunk
                for j, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    metadata = {
                        "source_type": "rss_feed",
                        "source_file": f"rss_{i}_{article.source.replace(' ', '_')}",
                        "title": article.title,
                        "url": article.url,
                        "source": article.source,
                        "date": article.published.isoformat() if article.published else None,
                        "categories": "News, Current Events",
                        "tags": f"rss, {article.source.replace(' ', '').lower()}, news",
                        "chunk_index": j,
                        "total_chunks": len(chunks),
                        "excerpt": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                        "word_count": len(article.content.split()),
                    }

                    processed_texts.append(chunk)
                    processed_metadata.append(metadata)
                    processed_ids.append(f"rss_{i}_chunk_{j}")

                total_chunks += len(chunks)
                self.logger.info(f"Processed article {i+1}/{len(articles)}: {article.title} ({len(chunks)} chunks)")

            except Exception as e:
                self.logger.error(f"Failed to process article {article.title}: {e}")
                continue

        # Store all chunks in vector database if there are any
        if processed_texts:
            try:
                self.logger.info(f"Storing {len(processed_texts)} chunks in vector database...")

                # Generate embeddings for all texts at once
                batch_embeddings = self.embed_model.encode(processed_texts, show_progress_bar=False)

                vector_store.add_documents(
                    texts=processed_texts,
                    embeddings=batch_embeddings,
                    metadata=processed_metadata,
                    ids=processed_ids
                )

                self.logger.info(f"Successfully ingested {total_chunks} chunks from {len(articles)} RSS articles")

                return {
                    "success": True,
                    "articles_ingested": len(articles),
                    "chunks_created": total_chunks,
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                self.logger.error(f"Failed to store RSS articles: {e}")
                return {"error": f"Storage failed: {e}"}
        else:
            return {"error": "No chunks were processed"}


class FeedFetcher:
    """Fetches articles from RSS feeds."""

    def __init__(self, feeds_file: str = "feeds.yaml"):
        self.feeds_file = feeds_file
        self.logger = logger
        self.max_articles_per_feed = 10
        self.min_article_length = 100

    async def fetch_feeds(self, batch_size: int = 5) -> List[ArticleData]:
        """Fetch articles from all RSS feeds in batch."""
        self.logger.info("Starting to fetch RSS feeds...")

        with open(self.feeds_file, 'r') as f:
            feeds_config = yaml.safe_load(f)

        feeds = feeds_config.get('feeds', [])
        articles = []

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
    """Generates initial blog topics from RSS content."""

    def __init__(self):
        self.ollama_client = OllamaClient()
        self.logger = logger

    async def summarize_to_topic(self, articles: List[ArticleData]) -> str:
        """Create a blog topic prompt from RSS articles."""
        if not articles:
            return "News Summary and Current Events Analysis"

        articles_text = []
        for i, article in enumerate(articles[:20]):
            articles_text.append(f"Article {i+1}:\nTitle: {article.title}\nContent: {article.content[:500]}...\nSource: {article.source}\n")

        articles_summary = "\n".join(articles_text)

        prompt = f"""
Based on the following collection of recent news articles, please:

1. Summarize the key themes and topics covered
2. Identify any connecting patterns or trends across the stories
3. Suggest a compelling blog post topic that weaves together these themes
4. Create a detailed writing prompt for an AI blog generator

Articles:
{articles_summary}

Please respond with:
- A brief summary of the articles
- The suggested blog post topic
- A detailed writing prompt suitable for an AI blog generator
"""

        self.logger.info("Generating initial blog topic from RSS content...")

        try:
            result = await self.ollama_client.generate(
                prompt,
                system_prompt="You are a creative blog topic strategist who finds connections in news and creates compelling writing prompts.",
                temperature=0.7
            )
            return result if result else "News Summary and Blog Topic"
        except Exception as e:
            self.logger.error(f"Error generating topic: {e}")
            return "News Summary and Blog Topic"


class AutomatedBlogGenerator:
    """Main orchestrator for the complete automated pipeline."""

    def __init__(self):
        self.logger = logger
        self.feed_fetcher = FeedFetcher()
        self.rss_ingestor = RSSIngestor()
        self.topic_generator = BlogTopicGenerator()
        self.orchestrator = BlogGenerationOrchestrator()

    async def run_automated_pipeline(self) -> bool:
        """
        Execute the complete automated pipeline:
        1. Fetch RSS feeds
        2. Ingest articles into knowledge base
        3. Generate blog topic
        4. Use expanded knowledge base for context-rich blog generation
        """
        logger.info("🚀 Starting Automated Blog Generation Pipeline")
        print("🚀 Starting Automated RSS Feed and Blog Generation Pipeline")
        print("=" * 60)

        try:
            # Step 1: Fetch RSS feeds
            print("📡 Step 1: Fetching RSS feeds...")
            articles = await self.feed_fetcher.fetch_feeds()

            if not articles:
                print("❌ No articles fetched. Cannot proceed.")
                return False

            print(f"✅ Fetched {len(articles)} articles from RSS feeds")

            # Step 2: Ingest RSS articles into knowledge base
            print("\n💾 Step 2: Ingesting RSS articles into knowledge base...")
            ingestion_result = await self.rss_ingestor.ingest_articles(articles)

            if 'error' in ingestion_result:
                print(f"❌ Ingestion failed: {ingestion_result['error']}")
                return False

            print(f"✅ Ingested {ingestion_result['articles_ingested']} articles ({ingestion_result['chunks_created']} chunks)")

            # Step 3: Generate initial blog topic
            print("\n🎯 Step 3: Generating blog topic from RSS content...")
            blog_topic_prompt = await self.topic_generator.summarize_to_topic(articles)
            print(f"✅ Generated topic: {blog_topic_prompt[:100]}...")

            # Step 4: Generate blog post using expanded knowledge base
            print("\n🤖 Step 4: Generating blog post with context from ingested articles...")

            spec_data = {
                'topic': blog_topic_prompt,
                'style': 'technical',
                'length': 'long',
                'tone': 'informative',
                'min_words': 1500,
                'max_words': 5000,  # Increased maximum word count for unlimited generation
                'categories': ['News', 'Analysis', 'Current Events'],
                'tags': ['news', 'trends', 'analysis', 'rss', 'synthesis']
            }

            print(f"📝 Generating blog post on: {blog_topic_prompt[:80]}...")

            # The orchestrator will now use the retriever agent, which searches the ENTIRE vector store
            # containing ALL previous blog posts, previously ingested RSS articles, AND the newly ingested RSS articles
            result = await self.orchestrator.generate_blog_post(blog_topic_prompt, spec_data)

            if result.success:
                print("🎉 SUCCESS: Blog post generated and saved!")
                print(f"� File: {result.file_path}")
                print(f"�🔄 Iterations: {result.iterations}")

                # The ingestor agent automatically adds the new blog post back to the knowledge base
                print("♻️  Final blog post ingested back into knowledge base for future reference")

                print("\n" + "=" * 60)
                print("🎯 Pipeline completed successfully!")
                print("📊 Knowledge base now includes:")
                print(f"   • Previous blog posts")
                print(f"   • {ingestion_result['articles_ingested']} current RSS articles")
                print(f"   • This newly generated blog post")
                print("   → Future generations can reference all this enriched context!")

                return True
            else:
                print(f"❌ Blog generation failed: {result.error}")
                return False

        except Exception as e:
            self.logger.error(f"Pipeline failed with error: {e}")
            print(f"💥 Critical error: {e}")
            return False


async def main():
    """Main entry point."""
    print("🤖 Automated RSS Feed Blog Generator")
    print("Creates blogs from RSS feeds with rich contextual awareness")
    print()

    generator = AutomatedBlogGenerator()

    success = await generator.run_automated_pipeline()

    if success:
        print("\n🎉 Automation pipeline completed successfully!")
        return 0
    else:
        print("\n💥 Automation pipeline failed.")
        return 1


if __name__ == "__main__":
    success_code = asyncio.run(main())
    sys.exit(success_code)
