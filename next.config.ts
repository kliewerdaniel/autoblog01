import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    domains: ['raw.githubusercontent.com', 'github.com', 'avatars.githubusercontent.com'],
    unoptimized: true, // For Netlify compatibility
  },
  distDir: 'dist',
};

export default nextConfig;
