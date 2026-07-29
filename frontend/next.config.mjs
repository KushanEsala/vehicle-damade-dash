/** @type {import('next').NextConfig} */
const nextConfig = {
  // Development and production builds must never share generated files.
  // This prevents missing chunk/CSS errors when a validation build runs while
  // the local development server is open.
  distDir: process.env.NODE_ENV === "development" ? ".next-dev" : ".next",
  async headers() {
    const contentSecurityPolicy = [
      "default-src 'self'",
      "base-uri 'self'",
      "frame-ancestors 'self'",
      "form-action 'self'",
      "object-src 'none'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' data: https://fonts.gstatic.com",
      "img-src 'self' data: blob: http://localhost:8000 http://127.0.0.1:8000",
      "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 ws://localhost:3000 ws://127.0.0.1:3000",
    ].join("; ");
    return [{
      source: "/(.*)",
      headers: [{key: "Content-Security-Policy", value: contentSecurityPolicy}],
    }];
  },
};

export default nextConfig;
