import Link from 'next/link';

export default function AboutPage() {
  const technicalExpertise = [
    { category: 'AI & Machine Learning', items: ['Local LLMs (Ollama)', 'LangChain', 'SmolAgents', 'ChromaDB', 'OpenAI API', 'Agentic Frameworks', 'RAG Systems'] },
    { category: 'Programming Languages', items: ['Python', 'TypeScript', 'JavaScript', 'SQL'] },
    { category: 'Web Development', items: ['React', 'Next.js', 'Django', 'FastAPI', 'HTML5', 'CSS3', 'Tailwind CSS'] },
    { category: 'Databases', items: ['SQLite', 'PostgreSQL', 'Vector Databases'] },
    { category: 'Data Annotation', items: ['Custom labeling systems', 'JSON/JSONL pipelines', 'Universal Data Tool (UDT)'] },
    { category: 'DevOps & Tools', items: ['Git', 'Docker', 'Netlify', 'VSCode', 'Cline', 'Markdown workflows'] },
    { category: 'Creative Tools', items: ['Photoshop', 'Wacom tablet integration', 'CRT modulation', 'video production'] },
  ];

  const keyProjects = [
    {
      name: 'Sample Project 1',
      type: 'Personal Project',
      year: '2024',
      description: 'A placeholder project description. Replace with your own project details.',
      details: [
        'Describe the technologies used and challenges overcome',
        'Highlight key features and functionalities',
        'Mention any notable achievements or impact'
      ]
    },
    {
      name: 'Sample Project 2',
      type: 'Open-Source Project',
      year: '2023',
      description: 'Another placeholder project. Customize this with your actual work.',
      details: [
        'Add your own project details here',
        'Include technologies, outcomes, and learnings'
      ]
    }
  ];

  const experiences = [
    {
      title: 'Independent AI Developer & Consultant',
      location: 'Austin, TX',
      period: '2022 – Present',
      description: 'Design and develop full-stack AI applications with emphasis on local-first architecture. Create custom data annotation workflows for machine learning model training. Build privacy-focused AI tools leveraging local inference capabilities.',
      achievements: [
        'Built production-ready AI applications serving real user needs with privacy-first approach',
        'Created comprehensive persona modeling framework adopted by other developers',
        'Successfully organized community hackathons fostering local AI development',
        'Developed innovative data annotation tools improving ML model training efficiency'
      ]
    },
    {
      title: 'Map Quality Analyst',
      location: 'Lionbridge (Remote)',
      period: 'August 2020 – 2024',
      description: 'Performed large-scale geospatial data annotation and quality assurance for global mapping services. Utilized proprietary annotation tools to improve location-based service accuracy.',
      achievements: [
        'Maintained high accuracy standards across diverse geographic regions and data types',
        'Collaborated with international teams on data quality improvement initiatives',
        'Processed thousands of map data points with consistent quality metrics'
      ]
    },
    {
      title: 'Freelance Creative Technology Specialist',
      location: 'Austin, TX',
      period: '2010 – Present',
      description: 'Developed multiple full-stack web applications and created experimental digital art installations combining traditional media with modern technology.',
      achievements: [
        'Created multiple full-stack web applications for diverse clients',
        'Produced award-recognized experimental film screened at Austin Film Society Avant Cinema (2012)',
        'Integrated CRT modulation and custom electronics into fine art installations',
        'Maintained 4+ years of consistent freelance client relationships and project delivery'
      ]
    },
    {
      title: 'Inventory Management Specialist',
      location: 'HEB, Austin, TX',
      period: '2024 – 2025',
      description: 'Managed high-volume retail operations while developing AI tools and applications. Demonstrated strong multitasking abilities balancing customer service with technical project development.',
      achievements: [
        'Successfully transitioned to full-time development focus upon project success',
        'Maintained operational efficiency in fast-paced retail environment'
      ]
    }
  ];

  const education = {
    degree: 'Bachelor of Arts in History',
    school: 'University of Mary Hardin-Baylor, Belton, TX',
    period: '2003 – 2007',
    continuing: [
      'Advanced AI/ML coursework and certification programs',
      'Open-source contribution and community leadership',
      'Local-first AI development methodologies'
    ]
  };

  return (
    <div>
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white sm:text-5xl">
            About
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
            A placeholder about page that you can customize with your own information.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Professional Summary */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Professional Summary</h2>
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  This is a placeholder professional summary. Replace this text with your own professional background,
                  skills, and experience. This section should highlight what makes you unique as a developer or creator.
                </p>
              </div>
            </section>

            {/* Key Projects */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Key Projects</h2>
              <div className="space-y-8">
                {keyProjects.map((project, index) => (
                  <div key={index} className="border-l-4 border-indigo-600 pl-6">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {project.name}
                      </h3>
                      <span className="text-sm text-gray-500 dark:text-gray-400 mt-1 sm:mt-0">
                        {project.year}
                      </span>
                    </div>
                    <p className="text-sm text-indigo-600 dark:text-indigo-400 mb-2 font-medium">
                      {project.type}
                    </p>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {project.description}
                    </p>
                    <ul className="space-y-2">
                      {project.details.map((detail, i) => (
                        <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                          <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                          {detail}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            {/* Bio */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Biography</h2>
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
                  This is a placeholder biography. Replace this text with your own personal story, background, and what drives you as a developer or creator.
                </p>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
                  Tell visitors about your journey, your interests outside of work, and what makes you unique in your field.
                </p>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  Use this space to connect with potential collaborators, employers, or anyone interested in your work.
                </p>
              </div>
            </section>

            {/* Experience */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Experience</h2>
              <div className="space-y-8">
                {experiences.map((exp, index) => (
                  <div key={index} className="border-l-4 border-indigo-600 pl-6">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {exp.title}
                      </h3>
                      <span className="text-sm text-gray-500 dark:text-gray-400 mt-1 sm:mt-0">
                        {exp.period}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {exp.description}
                    </p>
                    <ul className="space-y-2">
                      {exp.achievements.map((achievement, i) => (
                        <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                          <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                          {achievement}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            {/* Resume Download */}
            <section>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Download Resume
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Get a detailed PDF version of my professional experience and qualifications.
                </p>
                <a
                  href="/resume.pdf"
                  download
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
                >
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l4-4m-4 4l-4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Download PDF Resume
                </a>
              </div>
            </section>
          </div>

          {/* Sidebar */}
          <div>
            {/* Technical Expertise */}
            <section className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Technical Expertise</h2>
              <div className="space-y-4">
                {technicalExpertise.map((skillGroup) => (
                  <div key={skillGroup.category}>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-2">
                      {skillGroup.category}
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {skillGroup.items.map((skill) => (
                        <span
                          key={skill}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Education */}
            <section className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Education</h2>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                  {education.degree}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  {education.school}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mb-3">
                  {education.period}
                </p>
                <div>
                  <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Continuing Education:</p>
                  <ul className="space-y-1">
                    {education.continuing.map((item, index) => (
                      <li key={index} className="text-xs text-gray-600 dark:text-gray-400">
                        • {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>

            {/* Community Leadership */}
            <section className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Community Leadership</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                    Founder & Moderator
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    r/locollm subreddit - Growing community focused on local-first AI tools and development
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                    Open Source Contributor
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Active GitHub profile with multiple public repositories
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                    Hackathon Organizer
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    LoCo Hackathon series promoting local AI development
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                    Technical Writer
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Regular blog posts on AI development, system design, and privacy-focused technology
                  </p>
                </div>
              </div>
            </section>

            {/* Notable Achievements */}
            <section className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Notable Achievements</h2>
              <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li className="flex items-start">
                    <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                    Built production-ready AI applications serving real user needs with privacy-first approach
                  </li>
                  <li className="flex items-start">
                    <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                    Created comprehensive persona modeling framework adopted by other developers
                  </li>
                  <li className="flex items-start">
                    <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                    Successfully organized community hackathons fostering local AI development
                  </li>
                  <li className="flex items-start">
                    <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                    Developed innovative data annotation tools improving ML model training efficiency
                  </li>
                  <li className="flex items-start">
                    <span className="text-indigo-600 dark:text-indigo-400 mr-2">•</span>
                    Maintained 4+ years of consistent freelance client relationships and project delivery
                  </li>
                </ul>
              </div>
            </section>

            {/* Availability */}
            <section className="mb-8">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Availability</h2>
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Immediately available for full-time positions, consulting engagements, or collaborative projects
                  in AI development, data annotation, or system architecture roles.
                </p>
              </div>
            </section>

            {/* Quick Links */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Connect</h2>
              <div className="space-y-3">
                <a
                  href="https://github.com/example-user"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                >
                  <svg className="h-5 w-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
                  </svg>
                  GitHub Profile
                </a>
                <a
                  href="https://example.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                >
                  <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9h.01M12 12v0a9 9 0 01-9 9m9-9a9 9 0 00-9-9" />
                  </svg>
                  Personal Website
                </a>
                <Link
                  href="/contact"
                  className="flex items-center text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                >
                  <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Get in Touch
                </Link>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
