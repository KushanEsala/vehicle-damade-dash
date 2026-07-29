/** @type {import('next').NextConfig} */
const nextConfig = {
  // Development and production builds must never share generated files.
  // This prevents missing chunk/CSS errors when a validation build runs while
  // the local development server is open.
  distDir: process.env.NODE_ENV === "development" ? ".next-dev" : ".next",
};

export default nextConfig;
