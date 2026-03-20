import './globals.css';

export const metadata = {
  title: 'StockPulse AI — Smart Stock Analysis',
  description: 'AI-powered stock analysis dashboard with technical indicators, news sentiment, and ML-driven Buy/Sell signals.',
  keywords: 'stock analysis, AI, machine learning, technical indicators, sentiment analysis',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
