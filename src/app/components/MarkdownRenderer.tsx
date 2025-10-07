'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import rehypePrism from 'rehype-prism-plus';
import 'prismjs/themes/prism-tomorrow.css';

interface CodeBlockProps {
  children: React.ReactNode;
  className?: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ children, className }) => {
  const [isCopied, setIsCopied] = useState(false);
  const textInput = useRef<HTMLDivElement>(null);

  const handleCopy = () => {
    if (textInput.current) {
      const code = textInput.current.innerText;
      navigator.clipboard.writeText(code);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const language = className?.replace(/language-/, '') || 'javascript';

  return (
    <div className="relative group">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 bg-gray-700 text-white px-2 py-1 rounded text-sm opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {isCopied ? 'Copied!' : 'Copy'}
      </button>
      <div ref={textInput}>
        <pre className={`language-${language}`}>
          <code>{children}</code>
        </pre>
      </div>
    </div>
  );
};

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <ReactMarkdown
      rehypePlugins={[rehypeRaw, rehypePrism]}
      components={{
        pre: ({ children, ...props }) => {
          const codeChild = React.Children.toArray(children).find(
            (child): child is React.ReactElement<{ className?: string; children?: React.ReactNode }> =>
              React.isValidElement(child) && child.type === 'code'
          );

          if (codeChild) {
            return (
              <CodeBlock className={codeChild.props.className}>
                {codeChild.props.children}
              </CodeBlock>
            );
          }
          return <pre {...props}>{children}</pre>;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;
