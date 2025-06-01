import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mindful - AI Mental Health Coach",
  description: "A calm and supportive AI mental health coaching platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body style={{
        minHeight: "100vh",
        background: "linear-gradient(to bottom right, var(--color-cream-50), var(--color-cream-100))"
      }}>
        {/* Grainy overlay is handled by body::before in CSS */}
        
        {/* Soft floating shapes */}
        <div style={{
          position: "fixed",
          inset: 0,
          zIndex: 0,
          overflow: "hidden",
          opacity: 0.2,
          pointerEvents: "none"
        }}>
          {/* Floating blob 1 */}
          <div className="floating" style={{
            position: "absolute",
            width: "30vw",
            height: "30vw",
            borderRadius: "60% 40% 50% 50% / 40% 50% 50% 60%",
            background: "radial-gradient(circle at 30% 40%, var(--color-sage-300), transparent 70%)",
            top: "10%",
            left: "5%",
            filter: "blur(60px)"
          }}></div>
          
          {/* Floating blob 2 */}
          <div className="floating-delayed" style={{
            position: "absolute",
            width: "25vw",
            height: "25vw",
            borderRadius: "50% 60% 40% 50% / 50% 40% 60% 50%",
            background: "radial-gradient(circle at 70% 60%, var(--color-cream-400), transparent 70%)",
            bottom: "15%",
            right: "10%",
            filter: "blur(50px)"
          }}></div>
          
          {/* Floating blob 3 */}
          <div className="floating" style={{
            position: "absolute",
            width: "20vw",
            height: "20vw",
            borderRadius: "40% 60% 50% 50% / 60% 40% 50% 40%",
            background: "radial-gradient(circle at 40% 30%, var(--color-mist-300), transparent 70%)",
            top: "50%",
            right: "25%",
            filter: "blur(40px)"
          }}></div>
        </div>
        
        <main style={{
          position: "relative",
          zIndex: 10
        }}>
          {children}
        </main>
      </body>
    </html>
  );
}
