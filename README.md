# 🔐 Password Generator GUI

Aplicación gráfica minimalista en **Python 3.9+** que genera contraseñas criptográficamente seguras usando [CustomTkinter].  
Incluye selector de longitud, opciones de caracteres (mayúsculas, minúsculas, dígitos, símbolos), barra de fuerza por entropía y copia rápida al portapapeles.

---

## ✨ Características principales

- **Longitud ajustable** (4 – 64 caracteres)  
- Interruptores para incluir/excluir letras, números, símbolos y caracteres ambiguos  
- **Medidor de fuerza** con código de color y bits de entropía estimados  
- **Atajos de teclado:**  
  - `Ctrl/⌘ + R`  ►  Generar nueva contraseña  
  - `Ctrl/⌘ + C`  ►  Copiar al portapapeles  
- Avisos tipo *toast* y tooltips explicativos  
- Sin dependencias externas pesadas: solo `customtkinter` además de bibliotecas estándar

---

## 🚀 Instalación rápida

A continuación tienes un paso a paso detallado. Copia y pega en tu terminal (ajusta las rutas según tu sistema):

```bash
# 1. Clona este repositorio en tu máquina
git clone https://github.com/student-forever-01/password-generator-.git
cd password-generator-

# 2. (Opcional pero recomendado) Crea y activa un entorno virtual
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate

# 3. Instala las dependencias del proyecto
pip install customtkinter

# 4. Ejecuta la aplicación
python app.py
