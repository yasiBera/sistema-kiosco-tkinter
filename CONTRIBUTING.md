# Guía para colaborar

## Regla principal

Nadie trabaja directamente sobre `main`. Cada mejora se desarrolla en una rama
y se integra mediante un Pull Request revisado por otro estudiante.

## Antes de empezar

```bash
git switch main
git pull
git switch -c feature/descripcion-corta
```

## Antes de subir los cambios

1. Ejecutar `python -m unittest discover -v`.
2. Abrir la aplicación y probar manualmente la parte modificada.
3. Revisar que no se haya agregado `data/kiosco.db` al commit.
4. Usar mensajes claros: `feat:`, `fix:`, `docs:` o `test:`.

## Pull Request

El texto debe indicar qué problema resuelve, qué archivos modifica y cómo se
probó. Se recomienda que cada Pull Request tenga una sola mejora principal.

