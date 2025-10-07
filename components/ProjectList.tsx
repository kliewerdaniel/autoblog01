import ProjectCard from './ProjectCard';

interface Project {
  name: string;
  description: string;
  html_url: string;
  homepage?: string;
  language?: string;
  stargazers_count: number;
  topics?: string[];
  hasImage?: boolean;
}

interface ProjectListProps {
  projects: Project[];
  loading?: boolean;
}

export default function ProjectList({ projects, loading = false }: ProjectListProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden animate-pulse">
            <div className="h-48 bg-gray-200 dark:bg-gray-700"></div>
            <div className="p-6">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
              <div className="flex space-x-2">
                <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No projects found</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Get started by creating a new project.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <ProjectCard
          key={project.name}
          name={project.name}
          description={project.description}
          html_url={project.html_url}
          homepage={project.homepage}
          language={project.language}
          stargazers_count={project.stargazers_count}
          topics={project.topics}
          hasImage={project.hasImage}
        />
      ))}
    </div>
  );
}
