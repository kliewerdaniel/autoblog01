'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Resume', href: '/about' },
    { name: 'Projects', href: '/projects' },
    { name: 'Art', href: '/art' },
    { name: 'Blog', href: '/' },
    { name: 'Contact', href: '/contact' },
  ];

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'glass border-b neon-border shadow-lg'
          : 'bg-transparent'
      }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Top">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <motion.div
            className="flex items-center"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link href="/" className="group">
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <div className="w-8 h-8 bg-gradient-to-br from-accent to-secondary rounded-lg flex items-center justify-center glitch-hover">
                    <span className="text-black font-bold text-sm font-mono">DK</span>
                  </div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-accent to-secondary rounded-lg blur opacity-30 group-hover:opacity-60 transition-opacity"></div>
                </div>
                <span className="glitch-text text-xl font-bold text-foreground group-hover:text-accent transition-colors" data-text="Daniel Kliewer">
                  Daniel Kliewer
                </span>
              </div>
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {navigation.map((item, index) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 + 0.3 }}
              >
                <Link
                  href={item.href}
                  className="glitch-hover relative px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors group"
                >
                  <span className="relative z-10">{item.name}</span>
                  <span className="absolute inset-x-0 bottom-0 h-0.5 bg-gradient-to-r from-accent to-secondary transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></span>
                </Link>
              </motion.div>
            ))}
          </div>

          {/* Mobile menu button */}
          <motion.div
            className="md:hidden"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <button
              type="button"
              className="glitch-hover relative p-2 text-muted-foreground hover:text-foreground focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 rounded-lg"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              <div className="w-6 h-6 flex flex-col justify-center items-center">
                <motion.span
                  className="w-5 h-0.5 bg-current block transition-all duration-300"
                  animate={{
                    rotate: isMenuOpen ? 45 : 0,
                    y: isMenuOpen ? 0 : -8
                  }}
                />
                <motion.span
                  className="w-5 h-0.5 bg-current block transition-all duration-300 mt-1"
                  animate={{
                    opacity: isMenuOpen ? 0 : 1
                  }}
                />
                <motion.span
                  className="w-5 h-0.5 bg-current block transition-all duration-300 mt-1"
                  animate={{
                    rotate: isMenuOpen ? -45 : 0,
                    y: isMenuOpen ? 0 : 8
                  }}
                />
              </div>
            </button>
          </motion.div>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              className="md:hidden border-t neon-border"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
              <div className="px-2 pt-2 pb-3 space-y-1 glitch-card">
                {navigation.map((item, index) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Link
                      href={item.href}
                      className="glitch-hover block px-3 py-3 text-base font-medium text-muted-foreground hover:text-foreground hover:bg-accent/10 rounded-lg transition-all"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </motion.header>
  );
}
