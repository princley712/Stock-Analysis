/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    // Try to get the API URL from multiple sources
    // BACKEND_URL is often used in Docker internal networks
    // NEXT_PUBLIC_API_URL is the standard for client-side matching
    const apiUrl = process.env.BACKEND_URL || 
                   process.env.NEXT_PUBLIC_API_URL || 
                   'http://localhost:8000';
    
    console.log(`[NextConfig] Rewriting /api/* to ${apiUrl}/api/*`);
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
