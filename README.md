# Sistema de ventas para kiosco con Tkinter

Proyecto educativo inicial escrito en Python. Permite administrar productos,
controlar el stock y registrar ventas desde una caja sencilla. Los datos se
guardan localmente en SQLite.

## Funciones incluidas

- Dashboard con productos activos, stock bajo, ventas y recaudación del día.
- Alta y edición de productos.
- Activación y desactivación de productos sin borrar su historial.
- Buscador por nombre o código.
- Caja con carrito y control de disponibilidad.
- Descuento automático de stock al confirmar una venta.
- Historial y detalle de las últimas ventas.
- Base SQLite creada automáticamente al iniciar.
- Pruebas automáticas de las reglas principales.

> Esta primera versión no tiene usuarios ni contraseñas. La pestaña **Productos**
> funciona como panel administrativo. El inicio de sesión queda propuesto como
> una mejora para los estudiantes.

## Requisitos

- Python 3.10 o superior.
- Tkinter, normalmente incluido con Python en Windows.
- No requiere instalar paquetes con `pip`.

## Cómo ejecutar en Windows

1. Descargar o clonar el proyecto.
2. Abrir una terminal dentro de la carpeta `kiosco_tkinter`.
3. Ejecutar:

```bash
python main.py
```

La base de datos se creará en `data/kiosco.db`. Desde el menú **Datos** se
pueden cargar cinco productos de ejemplo.

## Ejecutar las pruebas

Desde la carpeta principal:

```bash
python -m unittest discover -v
```

Las pruebas usan una base temporal y no modifican los datos reales.

## Organización del código

```text
kiosco_tkinter/
├── main.py                    # Punto de entrada
├── app/
│   ├── config.py              # Configuración general
│   ├── database.py            # Conexión y tablas SQLite
│   ├── repositories.py        # Productos, ventas y reglas de stock
│   ├── utils.py               # Precio y formato de moneda
│   └── ui/
│       ├── dashboard_view.py  # Resumen del negocio
│       ├── products_view.py   # Panel administrativo
│       ├── pos_view.py        # Caja y carrito
│       ├── sales_view.py      # Historial
│       └── styles.py          # Estilos visuales
└── tests/
    └── test_system.py
```

## Propuestas de ramas para el trabajo en grupo

| Rama | Mejora sugerida |
| --- | --- |
| `feature/login` | Usuarios, contraseña y roles administrador/cajero |
| `feature/reportes` | Informe diario, semanal y exportación CSV |
| `feature/tickets` | Ticket imprimible de cada venta |
| `feature/codigo-barras` | Entrada rápida con lector de códigos |
| `feature/clientes` | Registro opcional de clientes |
| `feature/backup` | Copia y restauración de la base de datos |
| `feature/ui` | Mejoras visuales, iconos y accesibilidad |

## Flujo Git recomendado para estudiantes

```bash
git clone URL_DEL_REPOSITORIO
cd kiosco_tkinter
git switch -c feature/nombre-de-la-mejora
# trabajar y probar
git add .
git commit -m "feat: describir la mejora"
git push -u origin feature/nombre-de-la-mejora
```

Luego cada grupo crea un *Pull Request*. Antes de integrar una rama, debe
ejecutar las pruebas y revisar que la caja siga descontando correctamente el
stock.

## Posibles objetivos didácticos

- Comprender módulos, clases y separación de responsabilidades.
- Practicar eventos y componentes de Tkinter.
- Trabajar con SQL y transacciones.
- Usar ramas, commits y Pull Requests.
- Escribir pruebas antes de integrar cambios.

