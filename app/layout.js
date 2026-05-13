import './globals.css';
export const metadata = { title: '아침 브리핑', description: '시사 라디오 AI 큐레이션 브리핑' };
export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&family=Noto+Serif+KR:wght@400;700&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
