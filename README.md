# 🚀 Auto-Blog: Automated AI-Powered Blogging Platform

A professional Next.js blogging platform with advanced AI-driven content generation. Auto-Blog leverages RSS feed analysis and Retrieval-Augmented Generation (RAG) to create high-quality, SEO-optimized blog content automatically. Built for content creators, marketers, and businesses who want to scale their blogging efforts with AI assistance.

[![Next.js](https://img.shields.io/badge/Next.js-14.0+-000000?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-007ACC?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange?style=for-the-badge)](https://ollama.ai/)

![alt text](<Screenshot 2025-10-08 at 02.24.33.png>)


## ✨ Features

- 🎨 **Modern Next.js Boilerplate**: Production-ready blog site with TypeScript, Tailwind CSS
- 🤖 **Automated Content Generation**: `automated_blog_generator.py` - RSS-driven AI blog posts
- 📡 **RSS Feed Integration**: Automatic article fetching from configurable RSS sources
- 🔍 **Semantic Search**: ChromaDB-powered knowledge base for consistent content
- 🎯 **SEO Optimized**: Built-in meta tags, sitemaps, and search engine optimization
- 📱 **Responsive Design**: Mobile-first, SEO-friendly blog layout
- ⚡ **Static Generation**: Fast loading with modern web performance practices
- 🎭 **Agent Architecture**: Specialized AI agents for research, writing, and editing

## 🏗️ Architecture Overview

```
RSS Feeds → Fetcher → Knowledge Base → AI Agents → Generated Posts → Next.js Site
     ↓         ↓           ↓           ↓           ↓             ↓
   News     Ingest     ChromaDB     Research    SEO-Optimized  Static Blog
  Articles  Vector     Optimized    →Write→     Rich Content   Posts
             Store     Retrieval    →Edit→     →Publish
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+**
- **Python 3.8+**
- **Ollama** running with compatible LLM

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 2. Set Up Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a compatible model (recommended: 14B+ parameters)
ollama pull llama2:13b-chat
# or
ollama pull mistral:7b-instruct
```

### 3. Configure RSS Feeds

Edit `feeds.yaml` to add your preferred RSS sources:

```yaml
feeds:
  - https://example.com/rss.xml
  - https://techcrunch.com/rss/
  - https://dev.to/rss
```

### 4. Generate Your First Blog Post

```bash
python automated_blog_generator.py
```

This command will:
- Fetch articles from your RSS feeds
- Build a comprehensive knowledge base
- Generate SEO-optimized blog content
- Save posts to `content/blog/`
- Update the knowledge base for future generations

The generated posts are automatically compatible with your Next.js site!

### 5. Run the Blog Site

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your blog.

## 📝 Automated Blog Generation

### How It Works

The `automated_blog_generator.py` script is the core content creation engine:

1. **Feed Aggregation**: Fetches and processes RSS articles
2. **Knowledge Building**: Vectorizes content for semantic search
3. **Context Synthesis**: Uses RAG to find patterns and themes
4. **AI Generation**: Multi-agent pipeline creates polished content
5. **SEO Optimization**: Built-in keyword research and meta generation
6. **Content Integration**: Seamlessly integrates with Next.js structure

### Generation Options

Run the generator with custom parameters:

```bash
# Basic generation
python automated_blog_generator.py

# Force refresh knowledge base
export FORCE_REFRESH=true
python automated_blog_generator.py

# Check logs
tail -f automated_blog_generator.log
```

### Blog Post Format

Generated posts include proper Next.js frontmatter:

```markdown
---
title: "Generated Post Title"
date: "2025-01-07"
excerpt: "SEO-optimized description..."
categories: ["Tech", "AI"]
tags: ["automation", "blogs"]
image: "/images/posts/generated-post.jpg"
---

# Content here...
```

## 🛠️ Development

### Project Structure

```
auto-blog/
├── automated_blog_generator.py    # 🏆 Primary content generator
├── agent/                        # AI agent system
│   ├── agents/                  # Specialized agents
│   ├── prompts/                 # LLM prompt templates
│   ├── llm_client.py           # Ollama integration
│   └── vector_store.py         # ChromaDB operations
├── content/                     # Generated blog content
├── src/app/                     # Next.js application
│   ├── blog/                   # Blog pages & components
│   ├── components/             # Reusable UI components
│   └── globals.css             # Global styles
├── feeds.yaml                  # RSS feed configuration
├── package.json                # Node.js dependencies
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Available Scripts

**Next.js Commands:**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

**Content Generation:**
```bash
# All-in-one generation
python automated_blog_generator.py

# Run individual components
python fetcher.py    # Only fetch RSS feeds
python run_agentic_blog.py  # Use existing knowledge base
```

**Agent CLI (Advanced):**
```bash
# Ingest existing content
python agent/cli.py ingest

# Generate with specific parameters
python agent/cli.py generate "Your Topic" --style technical --length long
```

### Customization

#### Modify Agent Behavior

Edit `agent/prompts/system_prompts.py` to customize AI behavior:

```python
WRITER_AGENT_PROMPT = """
You are a technical blogger who writes in a conversational tone...
"""
```

#### Add RSS Feeds

Add sources to `feeds.yaml` for different content domains:

```yaml
feeds:
  - https://techcrunch.com/rss/
  - https://dev.to/rss
  - https://news.ycombinator.com/rss
  - https://github.blog/rss/
```

## 🎨 Blog Features

- **Static Generation**: Fast loading, great SEO
- **Markdown Support**: Full CommonMark compliance
- **Syntax Highlighting**: Code blocks with Prism.js
- **Table of Contents**: Auto-generated post navigation
- **Search Functionality**: Client-side content search
- **Categories & Tags**: Content organization
- **Responsive Images**: Optimized lazy loading
- **Dark Mode**: System-aware theme switching

## 🔧 Configuration

### Environment Variables

Create `.env.local` for custom settings:

```env
# Ollama Configuration
OLLAMA_MODEL=llama2:13b-chat
OLLAMA_BASE_URL=http://localhost:11434

# Content Settings
MAX_POSTS_PER_GENERATION=5
TARGET_WORD_COUNT_MIN=1200
TARGET_WORD_COUNT_MAX=2500
```

### Netlify Deployment

The project includes `netlify.toml` with optimized settings:

```toml
[build]
  command = "npm run build"
  publish = "out"

[build.environment]
  NODE_VERSION = "18"
```

## 📊 Performance

### Generation Benchmarks
- **RSS Fetching**: ~50-100 articles/minute
- **Content Vectorization**: ~100 posts/minute
- **Blog Generation**: 2-5 minutes per post
- **Knowledge Base**: ~1GB per 1000 processed articles

### Site Performance
- **Lighthouse Score**: 95+ on all metrics
- **First Contentful Paint**: <1.2s
- **Time to Interactive**: <2.5s
- **Static Asset Optimization**: 90%+ compression

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Next.js** - The React framework for production
- **Ollama** - Local LLM execution
- **ChromaDB** - Vector database for semantic search
- **SentenceTransformers** - Text embedding models
- **Feedparser** - RSS/Atom feed parsing

## 🚦 Roadmap

- [ ] Multi-language content generation
- [ ] Advanced SEO analytics dashboard
- [ ] Automated image generation for posts
- [ ] Social media integration
- [ ] Newsletter automation
- [ ] Content calendar management
- [ ] Performance optimization suite

---

**Auto-Blog: Scale Your Content, Multiply Your Impact.**

Built with ❤️ for content creators who want to leverage AI for automated, professional blogging.

