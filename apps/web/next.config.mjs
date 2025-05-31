/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@ai-mental-health-coach/core"],
  async redirects() {
    return [
      {
        source: '/',
        destination: '/conversations',
        permanent: false,
      },
    ];
  },
}

export default nextConfig; 