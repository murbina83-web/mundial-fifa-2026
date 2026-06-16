# 🏆 Copa Mundial FIFA 2026 — Calendario y Resultados

Aplicación web que muestra el calendario completo y resultados en tiempo real
del Mundial de Fútbol 2026, extrayendo los datos directamente de **fifa.com**.

## Requisito único: Python 3

Descárgalo desde https://www.python.org/downloads/  
Al instalar, marca **"Add Python to PATH"**.

---

## Instalación (solo la primera vez)

### Windows
Doble clic en **`instalar.bat`**

### Mac / Linux
```bash
chmod +x instalar.sh
./instalar.sh
```

---

## Iniciar la aplicación

### Windows
Doble clic en **`iniciar.bat`**

### Mac / Linux
```bash
python3 app.py
```
Luego abre tu navegador en **http://localhost:5000**

---

## Funcionalidades

| Pestaña | Descripción |
|---------|-------------|
| 📅 Calendario | Todos los partidos ordenados por fecha |
| 👥 Por Grupo | Filtrar por Grupo A hasta L |
| ⚡ Fase Final | Octavos, Cuartos, Semis, Final |
| ✅ Resultados | Partidos jugados (más recientes primero) |

- 🔍 Búsqueda por equipo, estadio o grupo
- 🔗 Clic en un partido → página oficial en FIFA
- 🔄 Botón **Actualizar** → descarga datos frescos de fifa.com

> El archivo `matches.json` ya viene incluido con los datos del torneo,
> por lo que la app funciona aunque no se instale Playwright.
> Playwright solo es necesario para el botón **Actualizar**.

---

## Estructura del proyecto

```
mundial2026/
├── app.py            ← Servidor web (Flask)
├── scraper.py        ← Extractor de datos de fifa.com (Playwright)
├── matches.json      ← Datos del torneo (104 partidos)
├── requirements.txt  ← Dependencias Python
├── instalar.bat      ← Instalador para Windows
├── iniciar.bat       ← Iniciador para Windows
├── instalar.sh       ← Instalador para Mac/Linux
└── templates/
    └── index.html    ← Interfaz web
```
