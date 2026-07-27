# Bet Analyzer AI

Motor de **análisis estadístico** de partidos de fútbol que calcula un
**"Índice de Apuesta"** por mercado (goles, tarjetas, córners, remates, BTTS).

> **No predice resultados.** Evalúa la **calidad de una apuesta** usando datos
> históricos, contexto y estadísticas, y devuelve: índice + explicación +
> probabilidades.

---

## 🥇 Regla de oro: la web no calcula

La inteligencia vive **exclusivamente** en el módulo `engine/`.

```
Frontend (Next.js)  ──►  API (FastAPI)  ──►  Base de datos (SQL Server)
        │                     │
        │                     └──►  engine/  (TODA la inteligencia)
        └──────────────  solo muestran; NUNCA calculan  ──────────────┘
```

- El **frontend** solo muestra lo que recibe.
- La **API** solo recibe la petición, se la pasa al **engine** y devuelve el
  resultado. **No calcula nada.**
- El **engine** lee los datos, calcula el índice y devuelve el resultado con su
  explicación. Es **independiente**: no importa nada de FastAPI ni del
  frontend, y se puede ejecutar solo.

---

## 📁 Estructura del proyecto

```
fuTTeb/
├── backend/                # API (FastAPI). Solo expone endpoints; no calcula.
│   ├── app/
│   │   ├── main.py         # Crea la app y registra routers
│   │   ├── config.py       # Configuración por variables de entorno
│   │   ├── database.py     # Conexión SQLAlchemy + pyodbc (sin modelos aún)
│   │   └── routers/
│   │       ├── health.py   # GET /health
│   │       └── analyze.py  # POST /analyze (mock; delegará en el engine)
│   ├── requirements.txt    # Dependencias de backend + engine
│   └── .env.example        # Plantilla de variables de entorno (sin secretos)
│
├── engine/                 # ⭐ TODA la inteligencia. Módulo independiente.
│   ├── core/               # Tipos, protocolo del mercado y registro
│   │   ├── types.py        # Tipos compartidos (contexto, resultado...)
│   │   ├── protocol.py     # Contrato que TODO mercado debe cumplir
│   │   └── registry.py     # Descubrimiento de mercados disponibles
│   ├── data/               # Repositorios que LEEN de SQL Server
│   │   ├── connection.py   # Conexión propia del engine a la BD
│   │   └── repositories.py # Consultas de solo lectura
│   ├── backtesting/        # Framework de validación histórica
│   │   └── framework.py
│   ├── markets/            # Mercados como PLUGINS (misma estructura c/u)
│   │   ├── goals/          # Goles
│   │   ├── corners/        # Córners
│   │   ├── cards/          # Tarjetas
│   │   ├── shots/          # Remates
│   │   └── btts/           # Ambos equipos marcan (BTTS)
│   └── requirements.txt    # Dependencias del engine (ejecutable solo)
│
├── frontend/               # Interfaz web (Next.js). Solo muestra.
│   └── package.json
│
├── database/               # Scripts SQL, migraciones y seeds (SQL Server)
│
├── docs/                   # Documentación del proyecto
│
├── .gitignore
└── README.md
```

### Anatomía de un mercado (plugin)

Cada carpeta dentro de `engine/markets/` tiene **exactamente** la misma
estructura interna:

| Archivo           | Responsabilidad                                                  |
|-------------------|------------------------------------------------------------------|
| `calculator.py`   | Punto de entrada; implementa el protocolo y orquesta el cálculo. |
| `weights.py`      | Pesos/configuración de cada factor del mercado.                  |
| `rules.py`        | Reglas y validaciones específicas del mercado.                   |
| `simulator.py`    | Estimación de probabilidades (Poisson, Montecarlo, etc.).        |
| `explanation.py`  | Genera la explicación legible del índice.                        |
| `__init__.py`     | Expone el plugin.                                                 |

---

## 🚀 Puesta en marcha

Se asume un entorno virtual `.venv` ya creado en la raíz.

### 1. Activar el entorno virtual

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```bash
pip install -r backend/requirements.txt
```

> `backend/requirements.txt` incluye lo necesario para la API **y** el engine.
> Si quieres instalar solo el engine (para ejecutarlo aislado):
> `pip install -r engine/requirements.txt`.

### 3. Configurar variables de entorno

```bash
# Copiar la plantilla y rellenar con valores reales (no se sube al repo)
copy backend\.env.example backend\.env
```

### 4. Levantar la API

```bash
uvicorn backend.app.main:app --reload
```

- Salud:  <http://127.0.0.1:8000/health>
- Docs:   <http://127.0.0.1:8000/docs>

### 5. Comprobar que el engine importa (aislado)

```bash
python -c "import engine; import engine.core; import engine.markets; print('engine OK')"
```

> **Nota (SQL Server):** para conectar de verdad necesitas el
> *ODBC Driver for SQL Server* instalado en el sistema. La API puede arrancar y
> responder `/health` sin base de datos, porque la conexión se crea de forma
> perezosa (solo al usarla).

---

## ➕ Cómo agregar un mercado nuevo (paso a paso)

Ejemplo: añadir el mercado **`offsides`** (fueras de juego).

1. **Crear la carpeta** del mercado dentro de `engine/markets/`:

   ```
   engine/markets/offsides/
   ```

2. **Crear los 6 archivos** con la estructura estándar (puedes copiarlos de un
   mercado existente como plantilla):

   ```
   engine/markets/offsides/__init__.py
   engine/markets/offsides/calculator.py
   engine/markets/offsides/weights.py
   engine/markets/offsides/rules.py
   engine/markets/offsides/simulator.py
   engine/markets/offsides/explanation.py
   ```

3. **Implementar el contrato**: en `calculator.py`, crear la calculadora que
   cumpla el protocolo de [`engine/core/protocol.py`](engine/core/protocol.py)
   (método `calculate(context) -> MarketResult`).

4. **Definir los factores**: pesos en `weights.py`, validaciones en `rules.py`,
   probabilidades en `simulator.py` y el texto en `explanation.py`.

5. **Registrar el mercado** en [`engine/core/registry.py`](engine/core/registry.py)
   para que el engine lo descubra por su nombre (`"offsides"`).

6. **(Opcional) Validar** con el framework de `engine/backtesting/` sobre datos
   históricos.

7. **Listo.** La API y el frontend **no cambian**: piden el mercado por su
   nombre y muestran el resultado. Ninguno de los dos calcula.
