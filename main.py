import instaloader
import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# -- CONFIGURACIÓN DE RUTAS Y ARCHIVOS ----
def obtener_ruta_base():
    """
    Retorna la ruta del directorio donde está el ejecutable 
    o la ruta del script (si se ejecuta en Python).
    """
    if getattr(sys, 'frozen', False):
        # Si se ejecuta como .exe compilado
        application_path = os.path.dirname(sys.executable)
    else:
        # Si se ejecuta como script .py normal
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    return application_path

# Usar la función para definir tu carpeta de datos
ruta_base = obtener_ruta_base()
data = os.path.join(ruta_base, "data") # Nombre de tu carpeta contenedora

# Crear la carpeta si no existe
if not os.path.exists(data):
    os.makedirs(data)

ruta_db = os.path.join(data, "instagram_tracker.db")
ruta_config = os.path.join(data, "config.json")


# --- 1. CONFIGURACIÓN DE SQLITE ---

DATABASE_NAME = ruta_db
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# --- 2. TABLAS DE LA BASE DE DATOS ---
class Snapshot(Base):
    __tablename__ = 'snapshots'
    id = Column(Integer, primary_key=True)
    target_username = Column(String)
    created_at = Column(DateTime, default=func.now())

class Follower(Base):
    __tablename__ = 'followers'
    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey('snapshots.id'))
    instagram_user_id = Column(BigInteger) # ID único de Instagram
    username = Column(String)              # Nombre de usuario (puede cambiar)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Ayuda a evitar algunos chequeos de seguridad
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ---------------------------------------

def enviar_correo(asunto, cuerpo, email_config, log_callback):
    """Envía un correo electrónico usando Gmail"""
    log_callback("📧 Enviando notificación por correo...")
    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = email_config['sender']
    msg['To'] = email_config['receiver']
    msg.set_content(cuerpo)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_config['sender'], email_config['password'])
            smtp.send_message(msg)
        log_callback("✅ Correo enviado exitosamente.")
    except Exception as e:
        log_callback(f"❌ Error enviando correo: {e}")

def guardar_snapshot(target_user, lista_seguidores):
    """
    Guarda un nuevo snapshot y sus seguidores en la base de datos.
    lista_seguidores debe ser una lista de tuplas: [(username, userid), ...]
    target_user es el nombre del usuario objetivo (string)
    """
    session = Session()
    
    # 1. Crear el Snapshot
    nuevo_snapshot = Snapshot(target_username=target_user)
    session.add(nuevo_snapshot)
    session.commit()

    snapshot_id_guardado = nuevo_snapshot.id

    print(f"💾 Guardando {len(lista_seguidores)} seguidores en la base de datos...")
    
    # 2. Guardar seguidores 
    objetos = [
        Follower(
            snapshot_id=snapshot_id_guardado, 
            instagram_user_id=uid, 
            username=uname
        )
        for uname, uid in lista_seguidores
    ]
    
    session.add_all(objetos)
    session.commit()
    session.close() # Ahora sí cerramos seguros
    
    print(f"✅ Snapshot {snapshot_id_guardado} guardado con {len(lista_seguidores)} seguidores.")
    return snapshot_id_guardado

def generar_reporte(target_user, log_callback):
    """
    Compara los dos últimos snapshots del usuario objetivo y genera un reporte de cambios.
    target_user es el nombre del usuario objetivo (string)
    """
    session = Session()
    
    # 1. Obtener los dos últimos snapshots para ese usuario
    snapshots = session.query(Snapshot)\
        .filter_by(target_username=target_user)\
        .order_by(Snapshot.created_at.desc())\
        .limit(2)\
        .all()

    if len(snapshots) < 2:
        log_callback("⚠️ No hay suficiente historial para comparar (se necesitan al menos 2 escaneos).")
        session.close()
        return

    snapshot_actual = snapshots[0]
    snapshot_anterior = snapshots[1]
    
    log_callback(f"\n--- REPORTE DE CAMBIOS ---")
    log_callback(f"Comparando: {snapshot_anterior.created_at} vs {snapshot_actual.created_at}")

    # 2. Cargar datos en diccionarios para comparación rápida {user_id: username}
    def get_followers_dict(snapshot_id):
        query = session.query(Follower.instagram_user_id, Follower.username)\
                       .filter_by(snapshot_id=snapshot_id).all()
        return {uid: uname for uid, uname in query}

    dict_actual = get_followers_dict(snapshot_actual.id)     # Datos de HOY
    dict_anterior = get_followers_dict(snapshot_anterior.id) # Datos de AYER

    # Sets de IDs para operaciones de conjuntos
    ids_actuales = set(dict_actual.keys())
    ids_anteriores = set(dict_anterior.keys())


    # A. Dejaron de seguir (Estaban antes, no están hoy)
    unfollowers_ids = ids_anteriores - ids_actuales
    
    # B. Nuevos seguidores (Están hoy, no estaban antes)
    new_followers_ids = ids_actuales - ids_anteriores
    
    # C. Se quedaron, pero cambiaron de nombre
    common_ids = ids_actuales & ids_anteriores
    renamed_users = []
    for uid in common_ids:
        if dict_anterior[uid] != dict_actual[uid]:
            renamed_users.append({
                'id': uid,
                'old': dict_anterior[uid],
                'new': dict_actual[uid]
            })

    # --- RESULTADOS ---
    
    # Si NO hay cambios, retornamos None
    if not unfollowers_ids and not new_followers_ids and not renamed_users:
        return None

    # Si HAY cambios, construimos el mensaje del correo
    reporte = f"Reporte de cambios para @{target_user}\n"
    reporte += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    if new_followers_ids:
        reporte += f"✨ NUEVOS SEGUIDORES ({len(new_followers_ids)}):\n"
        for uid in new_followers_ids:
            reporte += f" - {dict_actual[uid]}\n"
        reporte += "\n"

    if unfollowers_ids:
        reporte += f"🚫 DEJARON DE SEGUIRTE ({len(unfollowers_ids)}):\n"
        for uid in unfollowers_ids:
            reporte += f" - {dict_anterior[uid]}\n"
        reporte += "\n"

    if renamed_users:
        reporte += f"🔄 CAMBIOS DE NOMBRE ({len(renamed_users)}):\n"
        for cambio in renamed_users:
            reporte += f" - {cambio}\n"

    return reporte

    session.close()

def iniciar_analisis(usuario, session_id, targets, email_config, log_callback):
    L = instaloader.Instaloader(user_agent=USER_AGENT)

    log_callback("🔧 Inyectando cookies de Chrome...")

    try:
        L.context._session.cookies.set('sessionid', session_id)
        
        # setear el usuario manualmente en la sesión
        L.context.username = usuario
        
        # Verificamos si funcionó pidiendo nuestro propio perfil
        log_callback(f"🔄 Verificando acceso como {usuario}...")
        me = instaloader.Profile.from_username(L.context, usuario)
        log_callback(f"✅ ¡Éxito! Logueado como: {me.username} (ID: {me.userid})")

    except instaloader.ConnectionException as e:
        log_callback(f"❌ Error de conexión: La cookie (contraseña) podría estar vencida o mal copiada.\nError: {e}")
        sys.exit()
    except Exception as e:
        log_callback(f"❌ Error inesperado: {e}")
        sys.exit()

    # 3. bucle con objetivos
    for target_username in targets:
        log_callback(f"\n🔍 Analizando seguidores de '{target_username}'...")

        try:
            profile = instaloader.Profile.from_username(L.context, target_username)
            if(profile.is_private and not profile.followed_by_viewer):
                log_callback(f"❌ La cuenta '{target_username}' es privada y no la sigues. Saltando...")
                continue

            log_callback(f"📊 Cantidad de seguidores detectados: {profile.followers}")
            
            log_callback("📥 Descargando lista (Paciencia, esto puede tardar un rato)...")
            
            followers_list = [] # Lista para almacenar los seguidores nombre y id
            
            # Usamos el iterador. Instaloader maneja la paginación interna.
            # NOTA: Para cuentas grandes, esto puede tomar mucho tiempo.
            for follower in profile.get_followers():
                followers_list.append((follower.username, follower.userid))

            log_callback(f"\n✅ Terminado. Se extrajeron {len(followers_list)} cuentas.")
            
            guardar_snapshot(target_username, followers_list) # Guardar en DB

            # Analizar y notificar
            cuerpo_correo = generar_reporte(target_username, log_callback)
            
            if cuerpo_correo:
                log_callback("⚠️ ¡Cambios detectados!")
                log_callback(cuerpo_correo) # Imprimir en consola también
                enviar_correo(f"🔔 Alerta Instagram: {target_username}", cuerpo_correo, email_config, log_callback)
            else:
                log_callback("💤 Sin cambios relevantes.")

            log_callback(f"--- Análisis de '{target_username}' completado ---")
        
        except instaloader.ProfileNotExistsException:
            log_callback(f"❌ La cuenta '{target_username}' no existe. Saltando...")
        except instaloader.PrivateProfileNotFollowedException:
            log_callback(f"❌ La cuenta '{target_username}' es privada y no la sigues. Saltando...")
        except instaloader.QueryReturnedNotFoundException:
            log_callback(f"❌ El usuario '{target_username}' no existe.")
        except Exception as e:
            log_callback(f"❌ Ocurrió un error durante la extracción: {e}")
if __name__ == "__main__":
    iniciar_analisis()