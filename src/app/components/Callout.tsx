'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface CalloutProps {
  children: ReactNode;
  type?: 'info' | 'warning' | 'error' | 'success' | 'tip';
  title?: string;
  className?: string;
}

export default function Callout({
  children,
  type = 'info',
  title,
  className = ''
}: CalloutProps) {
  const typeStyles = {
    info: {
      container: 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800',
      icon: 'text-blue-600 dark:text-blue-400',
      title: 'text-blue-800 dark:text-blue-200',
      content: 'text-blue-700 dark:text-blue-300'
    },
    warning: {
      container: 'bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800',
      icon: 'text-yellow-600 dark:text-yellow-400',
      title: 'text-yellow-800 dark:text-yellow-200',
      content: 'text-yellow-700 dark:text-yellow-300'
    },
    error: {
      container: 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800',
      icon: 'text-red-600 dark:text-red-400',
      title: 'text-red-800 dark:text-red-200',
      content: 'text-red-700 dark:text-red-300'
    },
    success: {
      container: 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800',
      icon: 'text-green-600 dark:text-green-400',
      title: 'text-green-800 dark:text-green-200',
      content: 'text-green-700 dark:text-green-300'
    },
    tip: {
      container: 'bg-purple-50 dark:bg-purple-950/20 border-purple-200 dark:border-purple-800',
      icon: 'text-purple-600 dark:text-purple-400',
      title: 'text-purple-800 dark:text-purple-200',
      content: 'text-purple-700 dark:text-purple-300'
    }
  };

  const styles = typeStyles[type];

  const getIcon = () => {
    switch (type) {
      case 'info':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'success':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'tip':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`border-l-4 p-4 rounded-r-lg ${styles.container} ${className}`}
    >
      <div className="flex items-start">
        <div className={`flex-shrink-0 mr-3 ${styles.icon}`}>
          {getIcon()}
        </div>
        <div className="flex-1">
          {title && (
            <h4 className={`text-sm font-semibold mb-1 ${styles.title}`}>
              {title}
            </h4>
          )}
          <div className={`text-sm ${styles.content}`}>
            {children}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
