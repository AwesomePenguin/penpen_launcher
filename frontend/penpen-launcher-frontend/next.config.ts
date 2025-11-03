import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  
  // 图片配置 - 允许任意外部主机名
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**', // 允许任意 HTTPS 主机名
      },
      {
        protocol: 'http',
        hostname: '**', // 允许任意 HTTP 主机名 (开发环境)
      }
    ],
    // 备用配置：如果 remotePatterns 不生效，使用 domains
    domains: ['*'], // 已废弃但作为后备
  },
};

export default nextConfig;
