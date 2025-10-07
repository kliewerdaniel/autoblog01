'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function Footer() {
  const [currentYear, setCurrentYear] = useState(2024);

  useEffect(() => {
    setCurrentYear(new Date().getFullYear());
  }, []);

  const footerLinks = {
    navigation: [
      { name: 'Resume', href: '/about' },
      { name: 'Projects', href: '/projects' },
      { name: 'Art Gallery', href: '/art' },
      { name: 'Blog', href: '/blog' },
    ],
    connect: [
      {
        name: 'GitHub',
        href: 'https://github.com/kliewerdaniel',
        external: true
      },
      {
        name: 'Personal Site',
        href: 'https://danielkliewer.com',
        external: true
      },
      { name: 'Contact', href: '/contact', external: false },
    ]
  };

  return (
    <footer className="relative border-t neon-border bg-background/50 backdrop-blur-sm glitch-card">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />

      <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand */}
          <motion.div
            className="col-span-1 md:col-span-2"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-accent to-secondary rounded-lg flex items-center justify-center glitch-hover">
                <span className="text-black font-bold text-sm font-mono">DK</span>
              </div>
              <h3 className="glitch-text text-xl font-bold text-foreground" data-text="Daniel Kliewer">
                Daniel Kliewer
              </h3>
            </div>
            <p className="text-muted-foreground leading-relaxed max-w-md">
              AI Developer, Full-Stack Technologist, and System Designer.
              Building intelligent systems with an emphasis on{' '}
              <span className="neon-text text-accent font-semibold">local-first AI</span>,{' '}
              <span className="neon-text text-secondary font-semibold">agentic reasoning</span>, and{' '}
              <span className="neon-text text-accent font-semibold">resilient open-source infrastructure</span>.
            </p>
          </motion.div>

          {/* Quick Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h4 className="glitch-text text-sm font-semibold text-foreground uppercase tracking-wider mb-6" data-text="Navigation">
              Navigation
            </h4>
            <ul className="space-y-3">
              {footerLinks.navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="glitch-hover text-muted-foreground hover:text-accent transition-colors duration-200 flex items-center group"
                  >
                    <span className="w-1.5 h-1.5 bg-accent rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Connect */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h4 className="glitch-text text-sm font-semibold text-foreground uppercase tracking-wider mb-6" data-text="Connect">
              Connect
            </h4>
            <ul className="space-y-3">
              {footerLinks.connect.map((item) => (
                <li key={item.name}>
                  {item.external ? (
                    <a
                      href={item.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="glitch-hover text-muted-foreground hover:text-secondary transition-colors duration-200 flex items-center group"
                    >
                      <span className="w-1.5 h-1.5 bg-secondary rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                      {item.name}
                      <svg className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  ) : (
                    <Link
                      href={item.href}
                      className="glitch-hover text-muted-foreground hover:text-secondary transition-colors duration-200 flex items-center group"
                    >
                      <span className="w-1.5 h-1.5 bg-secondary rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                      {item.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Bottom */}
        <motion.div
          className="mt-12 pt-8 border-t neon-border"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
            <p className="text-sm text-muted-foreground">
              © {currentYear} Daniel Kliewer. All rights reserved.
            </p>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>Built with</span>
              <div className="flex items-center space-x-2">
                <span className="neon-text text-accent font-semibold">Next.js</span>
                <span>•</span>
                <span className="neon-text text-secondary font-semibold">TypeScript</span>
                <span>•</span>
                <span className="neon-text text-accent font-semibold">Tailwind</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </footer>
  );
}
