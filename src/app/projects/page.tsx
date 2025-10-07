// Featured Projects with Detailed Write-ups
const featuredProjects = [
  {
    title: 'Workflow Automation Framework',
    description: 'A comprehensive development workflow system that streamlines complex development processes through intelligent task orchestration and automated code management.',
    features: [
      'Automated task sequencing and dependency management',
      'Multi-language support for modern development stacks',
      'Integration with popular CI/CD pipelines',
      'Custom workflow templates for common development patterns'
    ],
    technologies: ['JavaScript', 'Node.js', 'Workflow Engine', 'CI/CD'],
    stars: 26,
    githubUrl: 'https://github.com/example-user/workflow',
    projectType: 'Development Tools'
  },
  {
    title: 'OpenAI Agents SDK + Ollama Integration',
    description: 'A powerful integration framework that combines OpenAI\'s advanced agent capabilities with local Ollama models, enabling sophisticated AI-driven applications that run entirely on your own infrastructure.',
    features: [
      'Seamless integration between OpenAI agents and local LLMs',
      'Support for complex multi-agent conversations',
      'Privacy-preserving AI workflows',
      'Extensible SDK for custom agent development'
    ],
    technologies: ['Python', 'OpenAI API', 'Ollama', 'AI/ML'],
    stars: 10,
    githubUrl: 'https://github.com/example-user/openai-agents-ollama',
    projectType: 'AI/ML'
  },
  {
    title: 'Interactive News Broadcast Generator',
    description: 'An innovative content generation system that creates dynamic news broadcasts using AI-driven storytelling and multi-modal content synthesis.',
    features: [
      'AI-powered news story generation and summarization',
      'Multi-modal content creation (audio/video/text)',
      'Real-time news aggregation and processing',
      'Interactive broadcast compilation tools'
    ],
    technologies: ['Python', 'AI/ML', 'Content Generation', 'Media Processing'],
    stars: 7,
    githubUrl: 'https://github.com/example-user/news-generator',
    projectType: 'Content Generation'
  },
  {
    title: 'Reddit AI Analysis Platform',
    description: 'A sophisticated data analysis tool that leverages AI to extract insights from Reddit discussions, providing deep behavioral analysis and trend forecasting.',
    features: [
      'Advanced sentiment analysis and opinion mining',
      'Community behavior pattern recognition',
      'Automated trend identification and reporting',
      'Real-time discussion monitoring and alerts'
    ],
    technologies: ['Python', 'Reddit API', 'NLP', 'Data Analysis'],
    stars: 2,
    githubUrl: 'https://github.com/example-user/reddit-analysis',
    projectType: 'Data Science'
  },
  {
    title: 'PersonaGen AI',
    description: 'A cutting-edge AI system for generating realistic digital personas, complete with psychological profiling, behavioral patterns, and contextual relationships.',
    features: [
      'Multi-dimensional persona creation with deep psychological modeling',
      'Cross-platform persona consistency and adaptation',
      'Behavioral simulation and interaction modeling',
      'Ethical AI guidelines and bias mitigation'
    ],
    technologies: ['Python', 'AI/ML', 'NLP', 'Psychology'],
    stars: 2,
    githubUrl: 'https://github.com/example-user/personagen',
    projectType: 'AI/ML'
  }
];

export default async function ProjectsPage() {
  return (
    <div>
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-white sm:text-5xl">
            Featured Projects
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-400">
            A showcase of my best open-source work, selected for their impact, innovation, and community value.
            These projects demonstrate advanced AI/ML implementations, development tools, and creative solutions.
          </p>
        </div>

        {/* Featured Projects */}
        <div className="space-y-16">
          {featuredProjects.map((project, index) => (
            <article key={index} className="bg-gray-900 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
              <div className="p-8">
                {/* Project Header */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        {project.projectType}
                      </span>
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                        ★ {project.stars.toLocaleString()} stars
                      </span>
                    </div>
                    <h2 className="text-3xl font-bold text-white mb-3">
                      {project.title}
                    </h2>
                  </div>

                  {/* GitHub Link */}
                  <a
                    href={project.githubUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
                    </svg>
                    View on GitHub
                  </a>
                </div>

                {/* Project Description */}
                <p className="text-lg text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                  {project.description}
                </p>

                {/* Features */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wide mb-3">
                    Key Features
                  </h3>
                  <ul className="grid gap-2">
                    {project.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start">
                        <svg className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Technologies */}
                <div>
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wide mb-3">
                    Technologies
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {project.technologies.map((tech, techIndex) => (
                      <span
                        key={techIndex}
                        className="px-3 py-1 text-sm font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>

        {/* More Projects CTA */}
        <div className="mt-20 text-center">
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-4">
              More Projects
            </h2>
            <p className="text-gray-300 mb-6">
              These are just a few highlights from my portfolio. Check out my full collection of projects on GitHub.
            </p>
            <a
              href="https://github.com/example-user"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
              </svg>
              View All Projects on GitHub
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
