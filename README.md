# 🕵️‍♂️ Instagram Follower Tracker 

![Logo App](icon.ico)

Esta es una aplicación de escritorio para monitorear seguidores en Instagram. Detecta quién te dejó de seguir, nuevos seguidores y cambios de nombre de seguidores, enviando notificaciones automáticas por correo electrónico.
---

## ⚠️ ADVERTENCIAS (Leer antes de usar)

El uso de herramientas de scraping automatizado conlleva riesgos. Por favor, ten en cuenta lo siguiente:

1.  **Riesgo de Bloqueo:** Instagram tiene límites estrictos. Si ejecutas este escáner demasiadas veces en poco tiempo (ej: cada 5 minutos), tu cuenta o tu IP podrían ser bloqueadas temporalmente (Soft Ban).
    * *Mi recomendación:* No hagas escaneos frecuentes. Con que lo hagas 2 veces ya esta bien
2.  **Tamaño de la Cuenta:** Esta aplicación está optimizada para **cuentas medianas o chicas** (hasta ~5k - 10k seguidores).
    * *Por qué:* Para cuentas masivas (100k+), la descarga de la lista de seguidores puede tardar demasiado, consumir mucha RAM o activar los sistemas anti-bot de Instagram antes de terminar.
3.  **Seguridad de la Cuenta:** Recomiendo usar una **cuenta secundaria** para realizar el scraping y espiar. Aun asi con cuenta principal funciona

---

## ✨ Características

* **GUI Moderna:** Interfaz gráfica fácil de usar con modo oscuro/claro.
* **Persistencia de Datos:** Base de datos SQLite local para guardar el historial.
* **Detección Inteligente:** Identifica:
    * 🚫 Unfollowers (Gente que te dejó de seguir).
    * ✨ Nuevos seguidores.
    * 🔄 Usuarios que cambiaron su nombre (evita falsos positivos).
* **Notificaciones por Email:** Recibe un reporte diario en tu bandeja de entrada solo si hubo cambios.
  
---

## 🔧 Instalación y Ejecución

### Opción A: Ejecutable (.exe)
Si descargaste la versión compilada desde "Releases":
1.  Descomprime el archivo.
2.  Ejecuta `InstaTrackerBot.exe`.
3.  *(Nota: La primera vez puede que Windows Defender te pregunte, permite la ejecución).*
4.  *(Nota: si el icono de la app no te aparece, solo arrastra el .ico a la misma carpeta donde esta ubicado el .exe)*

### Opción B: Desde el Código Fuente (Python)
Requisitos previos: tener Python 3.10+ instalado.

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/instagram-tracker.git
    cd instagram-tracker
    ```
2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecuta la aplicación:
    ```bash
    python gui.py
    ```

---

## ⚙️ Guía de Configuración (Campos de la GUI)

Al abrir la aplicación, verás los siguientes campos que debes llenar:

### 1. Usuario Objetivo (Target)
* Es el nombre de usuario (sin @) de la cuenta que quieres analizar.
* *(Nota: se debe ingresar uno por linea apretando la tecla enter)*
* *(Nota: En caso de que la cuenta a trackear sea privada, la "cuenta tracker" debe seguir a la cuenta a trackear, de otra forma dara error)*

### 2. Session ID (Cookie de Sesión)
**IMPORTANTE:** No usamos contraseña de Instagram por seguridad. Usamos la cookie de una sesión activa de Chrome.

**¿Cómo obtener el Session ID?**
Es muy sencillo:
1.  Abre [Instagram.com](https://www.instagram.com) en Google Chrome y loguéate (Con la cuenta que vas a usar para trackear).
2.  Presiona **F12** para abrir las Herramientas de Desarrollador.
3.  Ve a la pestaña **Application** (en el menú superior del panel derecho).
4.  En la columna izquierda, despliega **Cookies** y haz clic en `https://www.instagram.com`.
5.  En la lista del centro, busca la fila llamada `sessionid`.
6.  Copia todo el contenido de la columna "Value" (es una cadena larga de letras y números).
7.  Pega eso en la aplicación.
* *(Nota: Si en algun momento cerras sesión, vas a tener que volver a copiar el Session ID)*
* *(Recomendación: Si usas una cuenta secundaria, podes abrirla en algun otro navegador que no uses y la cookie seguira siendo válida)*

### 3. Email para Notificaciones
* Es el correo donde quieres enviar/recibir los reportes.
* *(Nota: Podes poner como Email remitente la misma cuenta que Email destino)*

### 4. Contraseña de Aplicación de Google
Si estás configurando para que envíe correos desde tu Gmail, no puedes usar tu contraseña normal. Necesitas una **Contraseña de Aplicación**:

1.  Ve a tu cuenta de Google > **Seguridad**.
2.  Asegúrate de tener la **Verificación en 2 pasos** activada.
3.  Busca la opción **"Contraseñas de aplicaciones"** (al final).
4.  Crea una nueva (Cualquier nombre).
5.  Google te dará una contraseña de 16 caracteres. Es la que tenes que poner en el campo de *contraseña de aplicación*

---

## 🚀 Tecnologías y Librerias Usadas

* **Python 3.10**
* **CustomTkinter:** Para la interfaz gráfica moderna.
* **Instaloader:** Para la extracción de datos de Instagram.
* **SQLAlchemy + SQLite:** Para el almacenamiento eficiente de datos y comparación de snapshots.

---

## 📄 Licencia

Este proyecto es para fines educativos. El uso de la información extraída es responsabilidad del usuario.
