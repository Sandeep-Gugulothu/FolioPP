const path = require('path');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/** @type {import('next').NextConfig} */
const nextConfig = {
    turbopack: {
        root: path.resolve(__dirname, '..'),
    },
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: `${BACKEND_URL}/api/:path*`,
        },
        {
          source: '/intelligence/:path*',
          destination: `${BACKEND_URL}/intelligence/:path*`,
        },
        {
          source: '/equity/:path*',
          destination: `${BACKEND_URL}/equity/:path*`,
        },
        {
          source: '/nse/:path*',
          destination: `${BACKEND_URL}/nse/:path*`,
        },
        {
          source: '/market/:path*',
          destination: `${BACKEND_URL}/market/:path*`,
        },
      ];
    },
};

module.exports = nextConfig;
