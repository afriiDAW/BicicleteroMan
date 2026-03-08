# 🚴‍♂️ BICICLETERO MAN - Juego Completo

## 📁 Estructura del Proyecto
```
BicicleteroMan/
├── main.py                 # 🎯 MENÚ PRINCIPAL (EJECUTAR ESTE ARCHIVO)
├── assets/                 # 🖼️ Recursos compartidos
│   ├── PANTALLA-PRINCIPAL.png
│   ├── fondo-menu.png
│   └── [botones del menú]
├── nivel-1/               # 🟢 Primer nivel 
│   ├── main.py
│   └── [archivos del nivel 1]
├── nivel-2/               # 🟡 Segundo nivel
│   ├── LVL2_1.py
│   └── [archivos del nivel 2]
└── nivel-3/               # 🔴 Tercer nivel
    ├── main.py
    └── [archivos del nivel 3]
```

## 🎮 Cómo Jugar

### ▶️ Iniciar el Juego
1. Ejecuta `main.py` desde la carpeta raíz del proyecto
2. Aparecerá la pantalla de inicio durante 3 segundos
3. Se hará un fundido al menú principal

### 🎯 Menú Principal
- **↑↓** - Navegar entre opciones
- **ENTER/ESPACIO** - Seleccionar opción
- **ESC** - Salir del juego
- **Cualquier tecla** - Saltar pantalla de inicio

### 🕹️ Opciones del Menú
- **NIVEL 1** - Primer nivel del juego
- **NIVEL 2** - Segundo nivel del juego  
- **NIVEL 3** - Tercer nivel del juego
- **SALIR** - Cerrar el juego

## 🔧 Características Técnicas

### ✨ Sistema de Menú
- **Pantalla completa automática** - Se adapta a tu resolución
- **Pantalla de inicio** con temporizador de 3 segundos
- **Efecto de fundido** suave entre pantallas
- **Menú interactivo** con navegación por teclado
- **Escalado automático** para diferentes resoluciones

### 🎯 Integración de Niveles
- **Lanzamiento automático** de cada nivel
- **Retorno al menú** cuando termina un nivel
- **Manejo de errores** si un nivel no se encuentra
- **Compatibilidad** con cada estructura de nivel

## 🎨 Recursos Visuales

### 📱 Pantalla de Inicio
- Imagen: `assets/PANTALLA-PRINCIPAL.png`
- Duración: 3 segundos
- Salto manual: Presionar cualquier tecla

### 🎭 Menú Principal  
- Fondo: `assets/fondo-menu.png`
- Título: "BICICLETERO MAN"
- Efectos: Sombras y escalado en selección

## 🚀 Ejecución

```bash
# Desde la carpeta raíz del proyecto
python main.py
```

## 🎯 Flujo del Juego
1. **Pantalla de Inicio** (3 segundos)
2. **Fundido a Menú Principal**
3. **Selección de Nivel** (1, 2 o 3)
4. **Ejecución del Nivel**
5. **Regreso al Menú** (al terminar nivel)

## 🔄 Sistema de Navegación
- El sistema maneja automáticamente el cambio entre niveles
- Cuando termina un nivel, regresa al menú principal
- Los niveles mantienen su funcionalidad original
- Compatible con pantalla completa en todos los niveles

## ⚙️ Requisitos
- Python 3.x
- Pygame
- Todos los archivos de nivel en sus respectivas carpetas
- Imágenes del menú en la carpeta `assets/`

¡Disfruta jugando BICICLETERO MAN! 🚴‍♂️🎮