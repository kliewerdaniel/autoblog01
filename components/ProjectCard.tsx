import Image from 'next/image';
import Link from 'next/link';

interface ProjectCardProps {
  name: string;
  description: string;
  html_url: string;
  homepage?: string;
  language?: string;
  stargazers_count: number;
  topics?: string[];
  hasImage?: boolean;
}

export default function ProjectCard({
  name,
  description,
  html_url,
  homepage,
  language,
  stargazers_count,
  topics = [],
  hasImage = false,
}: ProjectCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      {/* Project Image/Screenshot */}
      <div className="relative h-48 bg-gray-100 dark:bg-gray-700">
        {hasImage ? (
          <Image
            src={`/api/screenshot/${name}`}
            alt={`${name} screenshot`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <p className="mt-2 text-sm">{name}</p>
            </div>
          </div>
        )}
      </div>

      {/* Project Content */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              <Link
                href={`/projects/${name}`}
                className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                {name}
              </Link>
            </h3>
            {description && (
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                {description}
              </p>
            )}
          </div>
        </div>

        {/* Language and Topics */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {language && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
              {language}
            </span>
          )}
          {topics.slice(0, 3).map((topic) => (
            <span
              key={topic}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200"
            >
              {topic}
            </span>
          ))}
        </div>

        {/* Stars and Links */}
        <div className="flex items-center justify-between">
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10.293 15.707a1 1 0 010-1.414L14.586 10l-4.293-4.293a1 1 0 111.414-1.414l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
            {stargazers_count} stars
          </div>

          <div className="flex space-x-2">
            <a
              href={html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
            >
              Code
            </a>
            {homepage && (
              <a
                href={homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
              >
                Demo
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
