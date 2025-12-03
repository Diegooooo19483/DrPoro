#  DrPoro — FastAPI

Sistema web para administrar **Campeones**, **Ítems** y estadísticas de League of Legends, construido con **FastAPI**, **SQLAlchemy**, **Jinja2** y soporte para PostgreSQL o SQLite.



# 📦 Características principales

### ✔ Gestión de Campeones
- Crear, editar, listar y desactivar campeones  
- Filtrar por rol (Top, JG, Mid, Adc, Sup)  
- Ver detalles con items asignados  
- Asignar items con porcentaje de uso  

### ✔ Gestión de Ítems
- Crear, editar, listar y eliminar ítems  
- Asociación automática con campeones  

### ✔ Relación Champions ↔ Items
Se maneja a través del modelo intermedio **ChampionItem**, que además almacena:

- `porcentaje_uso`: cuán popular es el ítem en ese campeón.

---

# 🧩 Modelos y Relaciones

## **Champion**
Representa un campeón jugable.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | Primary Key |
| nombre | str | Nombre del campeón |
| rol | str | Top/JG/Mid/Adc/Sup |
| tasa_victoria | float | Winrate (%) |
| tasa_seleccion | float | Pick rate (%) |
| tasa_baneo | float | Ban rate (%) |
| activo | bool | Soft delete |

---

## **Item**
Representa un ítem del juego.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | Primary Key |
| nombre | str | Nombre |
| tipo | str | Tipo (Ofensivo / Defensivo / etc.) |
| porcentaje_uso | float | Uso global |
| activo | bool | Soft delete |

---



---

# 🌐 Mapa de Endpoints

## 🧩 1. Champions

### 🔵 HTML (Frontend)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/champions/list` | Lista HTML de campeones (filtro por rol) |
| GET | `/champions/new` | Form para crear campeón |
| POST | `/champions/new` | Crear campeón desde form |
| GET | `/champions/{id}/view` | Detalle del campeón + ítems |
| POST | `/champions/{id}/add-item` | Asociar ítem al campeón |
| GET | `/champions/{id}/edit` | Form para editar |
| POST | `/champions/{id}/edit` | Guardar cambios |

---

### 🟢 API JSON

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/champions/` | Listado JSON |
| GET | `/champions/{id}` | Obtener campeón |
| GET | `/champions/by-name/{name}` | Buscar por nombre |
| POST | `/champions/` | Crear campeón |
| PUT | `/champions/{id}` | Editar campeón |
| DELETE | `/champions/{id}` | Desactivar campeón |

---

## 🧩 2. Items

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/items` | Listado JSON |
| GET | `/items/{id}` | Obtener ítem |
| POST | `/items` | Crear ítem |
| PUT | `/items/{id}` | Editar ítem |
| DELETE | `/items/{id}` | Eliminar ítem |

---

## 🧩 3. Champion Items (relación many-to-many)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/champion-items/{champion_id}` | Ver ítems del campeón |
| GET | `/champion-items/{champion_id}/add` | Form para agregar ítem |
| POST | `/champion-items/{champion_id}/add` | Asociar ítem al campeón |





