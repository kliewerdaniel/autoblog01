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
  

        {/* Blog Filter and Posts */}
        <BlogFilter posts={posts} />

       
      </div>
    </div>
  );
}
