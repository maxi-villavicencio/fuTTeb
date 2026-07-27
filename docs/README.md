# Docs — Bet Analyzer AI

Documentación del proyecto: arquitectura, decisiones de diseño, especificación
del "Índice de Apuesta", contrato de los mercados (plugins) y guías de
contribución.

Documentos previstos:

- `arquitectura.md`   → capas (Frontend → API → DB) y engine independiente.
- `indice-apuesta.md` → definición y componentes del Índice de Apuesta.
- `mercados.md`       → contrato de un mercado y cómo añadir uno nuevo.
- `backtesting.md`    → metodología de validación histórica.

> La regla de oro del proyecto: **la web y la API nunca calculan**. Toda la
> inteligencia vive en `engine/`.
