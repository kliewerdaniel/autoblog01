import { promises as fs } from 'fs';
import path from 'path';
import matter from 'gray-matter';
import Link from 'next/link';
import TableOfContents from '../../components/TableOfContents';
import Callout from '../../components/Callout';
import MarkdownRenderer from '../../components/MarkdownRenderer';

interface BlogPost {
  slug: string;
  title: string;
  date: string;
  description: string;
  tags: string[];
  content: string;
}

async function getBlogPost(slug: string): Promise<BlogPost | null> {
  try {
    const filePath = path.join(process.cwd(), 'content', 'blog', `${slug}.md`);

    try {
      const fileContent = await fs.readFile(filePath, 'utf8');
      const { data, content } = matter(fileContent);

      return {
        slug,
        title: data.title || 'Untitled',
        date: data.date || 'No date',
        description: data.description || '',
        tags: data.tags || [],
        content,
      };
    } catch {
      // Blog post not found
      return null;
    }
  } catch (error) {
    console.error('Error loading blog post:', error);
    return null;
  }
}

async function getAllBlogPosts(): Promise<BlogPost[]> {
  try {
    const blogDir = path.join(process.cwd(), 'content', 'blog');
    const files = await fs.readdir(blogDir);
    const mdFiles = files.filter(file => file.endsWith('.md'));

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
          content,
        };
      })
    );

    return posts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  } catch (error) {
    console.error('Error loading blog posts:', error);
    return [];
  }
}

export async function generateStaticParams() {
  const posts = await getAllBlogPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const slug = (await params).slug;
  const post = await getBlogPost(slug);

  if (!post) {
    return {
      title: 'Post Not Found',
    };
  }

  return {
    title: `${post.title} | Blog`,
    description: post.description,
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const slug = (await params).slug;
  const post = await getBlogPost(slug);

  if (!post) {
    return (
      <div>
        <div className="mx-auto max-w-4xl px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Post Not Found
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              The blog post you're looking for doesn't exist.
            </p>
         
          </div>
        </div>
      </div>
    );
  }


  return (
    <div className="relative">
      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Back to Blog */}
        <div className="mb-8">
          <Link
            href="/blog"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
          >
            <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Blog
          </Link>
        </div>

        {/* Article Header */}
        <article>
          <header className="mb-16">
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-4">
              <time dateTime={post.date}>
                {new Date(post.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </time>
            </div>

            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
              {post.title}
            </h1>

            {post.description && (
              <p className="text-xl text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                {post.description}
              </p>
            )}

            {/* Tags */}
            {post.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </header>

          {/* Article Content */}
          <div className="prose prose-lg dark:prose-invert max-w-none">
            <MarkdownRenderer content={post.content} />
          </div>
        </article>

        {/* Navigation */}
        <nav className="mt-16 pt-8 border-t border-gray-200 dark:border-gray-800">
          <div className="flex justify-between">
            <div>
              <Link
                href="/blog"
                className="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium"
              >
                ← All Posts
              </Link>
            </div>
           
          </div>
        </nav>
      </div>

      {/* Table of Contents */}
      <TableOfContents content={post.content} />
    </div>
  );
}
