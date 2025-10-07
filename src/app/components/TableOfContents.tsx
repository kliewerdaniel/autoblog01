'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TableOfContentsProps {
  content: string;
  className?: string;
}

interface Heading {
  id: string;
  text: string;
  level: number;
}

export default function TableOfContents({ content, className = '' }: TableOfContentsProps) {
  const [headings, setHeadings] = useState<Heading[]>([]);
  const [activeId, setActiveId] = useState<string>('');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Extract headings from markdown content
    const headingRegex = /^(#{1,6})\s+(.+)$/gm;
    const extractedHeadings: Heading[] = [];
    let match;

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length;
      const text = match[2].trim();
      const id = text
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();

      extractedHeadings.push({ id, text, level });
    }

    setHeadings(extractedHeadings);
  }, [content]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: '-20% 0px -35% 0px' }
    );

    // Observe all headings
    headings.forEach(({ id }) => {
      const element = document.getElementById(id);
      if (element) {
        observer.observe(element);
      }
    });

    return () => observer.disconnect();
  }, [headings]);

  if (headings.length === 0) {
    return null;
  }

  return (
    <div className={`fixed right-4 top-1/2 transform -translate-y-1/2 z-40 ${className}`}>
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Toggle Button */}
          <motion.button
            onClick={() => setIsOpen(!isOpen)}
            className="mb-4 p-3 bg-card/80 backdrop-blur-sm border border-border rounded-lg shadow-lg hover:bg-card transition-colors group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg
              className={`w-5 h-5 text-muted-foreground group-hover:text-foreground transition-transform duration-200 ${
                isOpen ? 'rotate-90' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </motion.button>

          {/* Table of Contents */}
          <AnimatePresence>
            {isOpen && (
              <motion.div
                initial={{ opacity: 0, x: 20, width: 0 }}
                animate={{ opacity: 1, x: 0, width: 'auto' }}
                exit={{ opacity: 0, x: 20, width: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-card/90 backdrop-blur-sm border border-border rounded-lg shadow-xl overflow-hidden"
              >
                <div className="p-4 min-w-[250px] max-w-[300px]">
                  <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center">
                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                    </svg>
                    Table of Contents
                  </h3>

                  <nav className="space-y-1 max-h-[60vh] overflow-y-auto">
                    {headings.map((heading, index) => (
                      <motion.a
                        key={heading.id}
                        href={`#${heading.id}`}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`block py-2 px-3 text-sm transition-colors rounded-md hover:bg-accent/10 ${
                          activeId === heading.id
                            ? 'bg-accent/20 text-accent font-medium'
                            : 'text-muted-foreground hover:text-foreground'
                        }`}
                        style={{
                          paddingLeft: `${(heading.level - 1) * 16 + 12}px`,
                        }}
                        onClick={(e) => {
                          e.preventDefault();
                          const element = document.getElementById(heading.id);
                          if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            setIsOpen(false);
                          }
                        }}
                      >
                        {heading.text}
                      </motion.a>
                    ))}
                  </nav>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
