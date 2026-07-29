import "./globals.css";

// Metadatos de la página (pestaña del navegador).
export const metadata = {
  title: "Bet Analyzer AI",
  description: "Análisis estadístico de partidos por mercado. La web solo muestra; no calcula.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
