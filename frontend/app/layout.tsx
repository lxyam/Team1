import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '智能简历分析系统',
  description: '技术岗位求职者自测工具，检测简历描述是否经得起深度提问',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <body className={inter.className}>
        <main className="min-h-screen flex flex-col">
          <header className="border-b">
            <div className="container mx-auto px-4 py-4">
              <h1 className="text-2xl font-bold text-primary-600">智能简历分析系统</h1>
            </div>
          </header>
          <div className="flex-1 container mx-auto px-4 py-8">
            {children}
          </div>
          <footer className="border-t py-4">
            <div className="container mx-auto px-4 text-center text-slate-500 text-sm">
              © {new Date().getFullYear()} 智能简历分析系统 - 技术岗位求职者的自测工具
            </div>
          </footer>
        </main>
      </body>
    </html>
  );
} 