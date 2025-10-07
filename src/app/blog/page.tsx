import { promises as fs } from 'fs';
import path from 'path';
import Link from 'next/link';
import matter from 'gray-matter';
import BlogFilter from './BlogFilter';

interface BlogPost {
  slug: string;
  title: string;
  date: string;
  description: string;
  tags: string[];
  categories: string[];
}

async function getBlogPosts(): Promise<BlogPost[]> {
  try {
    // Read blog posts from content/blog directory
    const blogDir = path.join(process.cwd(), 'content', 'blog');
    const files = await fs.readdir(blogDir);

    // Filter for markdown files
    const mdFiles = files.filter(file => file.endsWith('.md'));

    // Parse frontmatter from each file
    const posts = await Promise.all(
      mdFiles.map(async (file) => {
        const filePath = path.join(blogDir, file);
        const fileContent = await fs.readFile(filePath, 'utf8');
        const { data, content } = matter(fileContent);

        const slug = file.replace(/\.md$/, '');

        return {
          slug,
          title: data.title || 'Untitled',
          date: data.date || 'No date',
          description: data.description || content.slice(0, 150) + '...',
          tags: data.tags || [],
          categories: data.categories || [],
        };
      })
    );

    // Sort posts by date (newest first)
    return posts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  } catch (error) {
    console.error('Error loading blog posts:', error);
    // Return fallback posts
    return [
      {
        slug: 'getting-started-with-ai-development',
        title: 'Getting Started with AI Development',
        date: '2025-01-15',
        description: 'A comprehensive guide to beginning your journey in AI development, covering essential concepts and practical steps.',
        tags: ['ai', 'development', 'tutorial', 'beginners'],
        categories: ['AI Integration & Development', 'Technical Tutorials'],
      },
      {
        slug: 'building-local-first-ai-systems',
        title: 'Building Local-First AI Systems',
        date: '2025-02-20',
        description: 'Exploring the benefits and challenges of developing AI systems that run locally on user devices rather than in the cloud.',
        tags: ['ai', 'local-first', 'privacy', 'offline', 'development'],
        categories: ['AI Integration & Development', 'Technical Tutorials'],
      },
    ];
  }
}

export default async function BlogPage() {
  const posts = await getBlogPosts();

  return (
    <div>
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-white sm:text-5xl">
            Blog
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-400">
            I write about AI engineering, practical tooling, and experiments in local-first model deployment.
            Posts are Markdown and can embed code & demos.
          </p>
        </div>

        {/* Blog Filter and Posts */}
        <BlogFilter posts={posts} />

        {/* RSS Feed Link */}
        <div className="mt-16 text-center">
          <a
            href="/rss.xml"
            className="inline-flex items-center text-sm text-gray-400 hover:text-gray-300 transition-colors"
          >
            <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a1 1 0 000 2c5.523 0 10 4.477 10 10a1 1 0 102 0C17 8.373 11.627 3 5 3z" />
              <path d="M4 9a1 1 0 011-1 7 7 0 017 7 1 1 0 11-2 0 5 5 0 00-5-5 1 1 0 01-1-1zM3 15a2 2 0 114 0 2 2 0 01-4 0z" />
            </svg>
            Subscribe to RSS feed
          </a>
        </div>
      </div>
    </div>
  );
}
