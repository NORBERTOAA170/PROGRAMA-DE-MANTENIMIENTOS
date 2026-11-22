import calendar
from datetime import datetime, date, timedelta
import html
import os
from zoneinfo import ZoneInfo
from PIL import Image
import streamlit as st

EMPRESA = "NAUPAGAS"
PERMISO_DISTRIBUCION = "LP/20474/DIST/PLA/2017"
HOY_MX = datetime.now(ZoneInfo("America/Mexico_City")).date()

st.set_page_config(
    page_title="Mantenimiento y Bitácora - NAUPAGAS",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def cargar_logo():
    candidatos = [
        "logo.jpg",
        "logo.jpg.jpg",
        "logo.jpeg",
        "logo.png",
        "logo.png.png",
        "LOGO.JPG",
        "LOGO.PNG",
    ]
    for nombre in candidatos:
        ruta = os.path.join(BASE_DIR, nombre)
        if os.path.isfile(ruta):
            try:
                return Image.open(ruta).copy()
            except Exception:
                pass
    try:
        for archivo in os.listdir(BASE_DIR):
            if archivo.lower().startswith("logo") and archivo.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                ruta = os.path.join(BASE_DIR, archivo)
                try:
                    return Image.open(ruta).copy()
                except Exception:
                    pass
    except Exception:
        pass
    return None

LOGO_IMG = cargar_logo()

PIPAS_BASE = [
    {
        "id_unidad": "005",
        "marca_modelo": "CHRYSLER",
        "numero_motor": "90291900821315",
        "serie_vin": "",
        "anio": "2010",
        "chofer": "MARTIN GONZALEZ LEON",
        "placas": "XV0965A",
    },
    {
        "id_unidad": "AT 20",
        "marca_modelo": "FREIGHTLINER M2 106 35K",
        "numero_motor": "90291900926231",
        "serie_vin": "3ALACYCS6CDBS9001",
        "anio": "2012",
        "chofer": "MARCO ANTONIO ALVARADO DURAN",
        "placas": "XX2879A",
    },
]

FRECUENCIAS_ORDEN = [
    "Todas",
    "Semanal",
    "Mensual",
    "Bimestral",
    "Trimestral",
    "Semestral",
    "Anual",
    "Evento / Correctivo",
]

MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

def _sumar_dias_habiles_sin_domingo(fecha_base, dias_desfase):
    d = fecha_base
    while d.weekday() == 6:
        d += timedelta(days=1)
    restantes = dias_desfase
    while restantes > 0:
        d += timedelta(days=1)
        if d.weekday() != 6:
            restantes -= 1
    return d

def _ultimo_sabado_del_mes(anio, mes):
    if mes == 12:
        siguiente = date(anio + 1, 1, 1)
    else:
        siguiente = date(anio, mes + 1, 1)
    d = siguiente - timedelta(days=1)
    while d.weekday() != 5:
        d -= timedelta(days=1)
    return d

def _crear_entrada(fecha_base, desfase_unidad, tipo_mant, frecuencia, actividad, criterios, personal, responsable="Por asignar"):
    fecha_obj = _sumar_dias_habiles_sin_domingo(fecha_base, desfase_unidad)
    cumplido = fecha_obj <= HOY_MX
    return {
        "_fecha_dt": fecha_obj,
        "TIPO DE MANTENIMIENTO": tipo_mant,
        "FRECUENCIA": frecuencia,
        "FECHA PROGRAMADA": fecha_obj.strftime("%d/%m/%Y"),
        "ACTIVIDAD A REALIZAR": actividad,
        "CUMPLIO": "Sí" if cumplido else "Pendiente",
        "ESTADO": "Cerrado" if cumplido else "Abierto",
        "ACCIONES TOMADAS": (
            f"Mantenimiento {frecuencia.lower()} ejecutado conforme al programa"
            if cumplido
            else "Pendiente por fecha programada"
        ),
        "RESPONSABLE": responsable,
        "CRITERIOS DE ACEPTACIÓN O RECHAZO": criterios,
        "PERSONAL COMPETENTE": personal,
    }

def generar_programa_anual_2026(desfase_unidad=0):
    registros = []

    d_sem = date(2026, 1, 3)
    while d_sem <= date(2026, 12, 31):
        registros.append(_crear_entrada(
            d_sem,
            desfase_unidad,
            "Preventivo",
            "Semanal",
            "Inspección visual y limpieza de válvulas de desconexión seca y acoplamiento de llenado, revisión de presión/estado de llantas, torque de birlos, bornes de batería e instrumentos.",
            "Aceptación: Sin fugas, sin grietas ni corrosión severa; acople sella y libera sin atoramiento; llantas y birlos firmes. Rechazo: Cualquier fuga/goteo de Gas LP, traba dañada, llanta dañada/ponchada o birlo flojo/barrido.",
            "Operador capacitado / Técnico de mantenimiento de unidad",
        ))
        d_sem += timedelta(days=7)

    for mes in range(1, 13):
        d_mes = _ultimo_sabado_del_mes(2026, mes)
        registros.append(_crear_entrada(
            d_mes,
            desfase_unidad,
            "Preventivo",
            "Mensual",
            "Verificación operativa de válvulas de desconexión seca y acoplamiento de llenado, prueba de paro de emergencia, cableado eléctrico y rótulos/señalización.",
            "Aceptación: Cierre hermético al desconectar, paro de emergencia inmediato y rótulos legibles. Rechazo: Fuga al desacoplar, retardo/falla en paro de emergencia, cableado dañado o rótulos faltantes.",
            "Técnico de mantenimiento mecánico-eléctrico / Responsable de seguridad",
        ))

    for mes in (2, 4, 6, 8, 10, 12):
        d_bim = _ultimo_sabado_del_mes(2026, mes)
        registros.append(_crear_entrada(
            d_bim,
            desfase_unidad,
            "Preventivo",
            "Bimestral",
            "Revisión de juego en dirección, suspensión/muelles/amortiguadores y revisión/purga de filtro o trampa de agua de combustible.",
            "Aceptación: Holgura de dirección dentro de tolerancia, suspensión sin golpes/fugas y combustible limpio. Rechazo: Juego excesivo en dirección, amortiguador/muelle roto o con fuga, o combustible contaminado.",
            "Mecánico automotriz competente",
        ))

    for mes in (3, 6, 9, 12):
        d_trim = _ultimo_sabado_del_mes(2026, mes)
        registros.append(_crear_entrada(
            d_trim,
            desfase_unidad,
            "Preventivo",
            "Trimestral",
            "Inspección trimestral de sistema de medición/transferencia, frenos, suspensión, mangueras/acoples y pruebas funcionales de dispositivos de emergencia.",
            "Aceptación: Transferencia estable, frenos y suspensión sin anomalías y paro de emergencia operativo. Rechazo: Fugas, descalibración o falla en transferencia, frenos, suspensión o emergencia.",
            "Técnico mecánico-eléctrico / Especialista de mantenimiento",
        ))

    for mes in (6, 12):
        d_semestral = _ultimo_sabado_del_mes(2026, mes)
        registros.append(_crear_entrada(
            d_semestral,
            desfase_unidad,
            "Preventivo",
            "Semestral",
            "Revisión integral semestral de válvulas de relevo de presión, sistema de contención, tuberías, conexiones, hermeticidad general, frenos y dispositivos de seguridad.",
            "Aceptación: Sin fugas, sin grietas ni corrosión severa; válvulas, tuberías y seguridad íntegros. Rechazo: Cualquier fuga de Gas LP, daño estructural/en válvulas/tuberías o falla de seguridad.",
            "Especialista en sistemas LP / Técnico de mantenimiento certificado",
        ))

    registros.append(_crear_entrada(
        date(2026, 12, 26),
        desfase_unidad,
        "Preventivo",
        "Anual",
        "Evaluación anual consolidada de cumplimiento del programa preventivo de la unidad, revisión general de componentes críticos, dispositivos de seguridad, hermeticidad y control documental.",
        "Aceptación: Programa anual cumplido, componentes íntegros, sin fugas ni fallas críticas y condiciones seguras. Rechazo: Fugas, fallas críticas no atendidas, deficiencias en seguridad o incumplimiento normativo.",
        "Responsable de mantenimiento / Especialista técnico certificado",
    ))

    orden_frec = {
        "Semanal": 1,
        "Mensual": 2,
        "Bimestral": 3,
        "Trimestral": 4,
        "Semestral": 5,
        "Anual": 6,
        "Evento / Correctivo": 7,
    }
    registros.sort(key=lambda r: (r["_fecha_dt"], orden_frec.get(r["FRECUENCIA"], 99)))

    filas_finales = []
    for idx, r in enumerate(registros, start=1):
        limpia = {k: v for k, v in r.items() if k != "_fecha_dt"}
        fila = {"FOLIO": f"PRV-{idx:03d}"}
        fila.update(limpia)
        filas_finales.append(fila)

    return filas_finales

def _normalizar_cumplio(val):
    if val is True or val in ("Sí", "Si", "SÍ", "SI"):
        return "Sí"
    return "Pendiente"

def _normalizar_estado(val):
    if val in ("Cerrado", "CERRADO"):
        return "Cerrado"
    return "Abierto"

def normalizar_filas(filas):
    limpias = []
    for r in filas:
        item = dict(r)
        for k, v in item.items():
            if v is None:
                item[k] = ""
        item["CUMPLIO"] = _normalizar_cumplio(item.get("CUMPLIO"))
        item["ESTADO"] = _normalizar_estado(item.get("ESTADO"))
        limpias.append(item)
    return limpias

def obtener_desfase_unidad(unidad_obj):
    lista = st.session_state.get("unidades_naupagas", PIPAS_BASE)
    for idx, u in enumerate(lista):
        if u["id_unidad"] == unidad_obj["id_unidad"]:
            return idx
    return 0

def obtener_filas_unidad(unidad_obj):
    clave = f"prog_2026_{unidad_obj['id_unidad']}"
    if clave not in st.session_state:
        desfase = obtener_desfase_unidad(unidad_obj)
        st.session_state[clave] = normalizar_filas(generar_programa_anual_2026(desfase_unidad=desfase))
    else:
        st.session_state[clave] = normalizar_filas(st.session_state[clave])
    return st.session_state[clave], clave

def filtrar_por_frecuencia(filas, frecuencia_sel):
    if not frecuencia_sel or frecuencia_sel == "Todas":
        return filas
    return [f for f in filas if f.get("FRECUENCIA") == frecuencia_sel]

def _resumen_corto_actividad(texto):
    t = (texto or "").strip()
    if "," in t:
        t = t.split(",", 1)[0]
    if len(t) > 54:
        return t[:51].rstrip() + "..."
    return t

def construir_html_calendario(anio, mes, eventos_por_dia):
    cal = calendar.Calendar(firstweekday=0)
    semanas = cal.monthdayscalendar(anio, mes)
    encabezados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo (No laborable)"]

    css = """
    <style>
        .cal-wrap {
            width: 100%;
            overflow-x: auto;
            margin-top: 8px;
            margin-bottom: 16px;
        }
        table.cal-grid {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            font-family: sans-serif;
            background: #ffffff;
        }
        table.cal-grid th {
            background: #0f294a;
            color: #ffffff;
            padding: 10px 8px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid #cbd5e1;
            text-align: center;
        }
        table.cal-grid th.th-domingo {
            background: #475569;
        }
        table.cal-grid td {
            border: 1px solid #cbd5e1;
            vertical-align: top;
            height: 122px;
            padding: 6px;
            background: #ffffff;
        }
        table.cal-grid td.celda-vacia {
            background: #f8fafc;
        }
        table.cal-grid td.celda-domingo {
            background: #f1f5f9;
        }
        table.cal-grid td.celda-hoy {
            background: #eff6ff;
            outline: 2px solid #2563eb;
            outline-offset: -2px;
        }
        .dia-num {
            font-size: 13px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .tag-domingo {
            font-size: 10px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
        }
        .ev-card {
            border-radius: 5px;
            padding: 4px 6px;
            margin-bottom: 4px;
            font-size: 11px;
            line-height: 1.28;
            word-wrap: break-word;
        }
        .ev-u0 {
            background: #e0f2fe;
            border-left: 3px solid #0284c7;
            color: #0c4a6e;
        }
        .ev-u1 {
            background: #fef3c7;
            border-left: 3px solid #d97706;
            color: #78350f;
        }
        .ev-u2 {
            background: #dcfce7;
            border-left: 3px solid #16a34a;
            color: #14532d;
        }
        .ev-title {
            font-weight: 700;
        }
        .ev-sub {
            font-size: 10.5px;
            margin-top: 1px;
        }
    </style>
    """

    partes = [css, '<div class="cal-wrap"><table class="cal-grid"><thead><tr>']
    for idx_h, nombre_dia in enumerate(encabezados):
        clase_th = ' class="th-domingo"' if idx_h == 6 else ""
        partes.append(f"<th{clase_th}>{html.escape(nombre_dia)}</th>")
    partes.append("</tr></thead><tbody>")

    for semana in semanas:
        partes.append("<tr>")
        for idx_dia, dia_num in enumerate(semana):
            if dia_num == 0:
                partes.append('<td class="celda-vacia"></td>')
                continue

            fecha_celda = date(anio, mes, dia_num)
            es_domingo = (idx_dia == 6)
            es_hoy = (fecha_celda == HOY_MX)

            clases = []
            if es_domingo:
                clases.append("celda-domingo")
            if es_hoy:
                clases.append("celda-hoy")
            clase_td = f' class="{" ".join(clases)}"' if clases else ""

            etiqueta_dom = '<span class="tag-domingo">No laborable</span>' if es_domingo else ""
            partes.append(f'<td{clase_td}><div class="dia-num"><span>{dia_num}</span>{etiqueta_dom}</div>')

            for ev in eventos_por_dia.get(dia_num, []):
                clase_color = f"ev-u{ev['color_idx'] % 3}"
                folio_txt = html.escape(ev["folio"])
                pipa_txt = html.escape(ev["id_unidad"])
                act_txt = html.escape(ev["resumen"])
                frec_txt = html.escape(ev["frecuencia"])
                est_txt = html.escape(ev["estado"])
                partes.append(
                    f'<div class="ev-card {clase_color}">'
                    f'<div class="ev-title">{folio_txt} - {act_txt}</div>'
                    f'<div class="ev-sub">Pipa ID {pipa_txt} | {frec_txt} | {est_txt}</div>'
                    f"</div>"
                )

            partes.append("</td>")
        partes.append("</tr>")

    partes.append("</tbody></table></div>")
    return "".join(partes)

USUARIOS = {
    "NAUPAGAS":    {"pass": "NAUPAGAS2026",  "nombre": "Operación y Mantenimiento NAUPAGAS"},
    "admin_naupa": {"pass": "NaupaMant2026!", "nombre": "Responsable Mantenimiento NAUPAGAS"},
    "op_taller1":  {"pass": "Taller2026!",     "nombre": "Técnico de Mantenimiento 1"},
}

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "unidades_naupagas" not in st.session_state:
    st.session_state.unidades_naupagas = list(PIPAS_BASE)

# ================= PORTADA Y LOGIN =================
if st.session_state.usuario_actual is None:
    st.markdown(
        """
        <style>
            .portada-badge {
                display: inline-block;
                background: rgba(56, 189, 248, 0.14);
                color: #0369a1;
                border: 1px solid rgba(56, 189, 248, 0.4);
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 0.82rem;
                font-weight: 600;
                margin-bottom: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    _, col_centro, _ = st.columns([1, 2.2, 1])
    with col_centro:
        c_logo, c_titulo = st.columns([1, 2.4], vertical_alignment="center")
        with c_logo:
            if LOGO_IMG is not None:
                st.image(LOGO_IMG, use_container_width=True)
            else:
                st.markdown("### **NAUPAGAS**")
                st.caption(f"No se encontró logo en: `{BASE_DIR}`")
        with c_titulo:
            st.markdown('<div class="portada-badge">NAUPAGAS • PROGRAMA ANUAL DE MANTENIMIENTO</div>', unsafe_allow_html=True)
            st.markdown("## Programa de Mantenimiento y Bitácora Electrónica")
            st.caption("Sistema exclusivo de NAUPAGAS para unidades de distribución de Gas LP.")
            st.caption(f"**No. de permiso de distribución:** {PERMISO_DISTRIBUCION}")

        st.markdown("---")

        with st.form("form_login"):
            st.markdown("### Iniciar sesión")
            user_in = st.text_input("Usuario", placeholder="Ej. NAUPAGAS").strip()
            pass_in = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submit_login = st.form_submit_button("Entrar al sistema", type="primary", use_container_width=True)

        if submit_login:
            info = USUARIOS.get(user_in) or USUARIOS.get(user_in.upper())
            if info and info["pass"] == pass_in:
                st.session_state.usuario_actual = {
                    "username": user_in,
                    "nombre": info["nombre"],
                    "empresa": EMPRESA
                }
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    st.stop()

usuario = st.session_state.usuario_actual

# ================= SIDEBAR =================
with st.sidebar:
    if LOGO_IMG is not None:
        st.image(LOGO_IMG, use_container_width=True)
    else:
        st.warning("Logo no cargado en carpeta del proyecto.")
    st.markdown(f"**Usuario:** {usuario['nombre']}")
    st.caption(f"ID: `{usuario['username']}` | **{EMPRESA}**")
    modulo = st.radio(
        "Módulos",
        [
            "Programa de Mantenimiento Anual",
            "Calendario Anual 2026",
            "GENERAR NUEVO MANTENIMIENTO",
            "Cerrar Mantenimientos",
            "Agregar Unidad"
        ]
    )
    st.markdown("---")
    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state.usuario_actual = None
        st.rerun()

unidades = st.session_state.unidades_naupagas
mapa_unidades = {
    f"ID {u['id_unidad']} — {u['marca_modelo']} ({u['anio']}) | Chofer: {u['chofer']}": u
    for u in unidades
}

# ================= 1. PROGRAMA DE MANTENIMIENTO ANUAL =================
if modulo == "Programa de Mantenimiento Anual":
    st.title(f"Programa de Mantenimiento Anual 2026 — {EMPRESA}")

    f_col1, f_col2 = st.columns([2.2, 1.2])
    unidad_label = f_col1.selectbox("Selecciona unidad / chofer", list(mapa_unidades.keys()))
    frecuencia_filtro = f_col2.selectbox("Filtrar por FRECUENCIA", FRECUENCIAS_ORDEN)

    u_sel = mapa_unidades[unidad_label]
    st.caption(
        f"**ID Unidad:** {u_sel['id_unidad']} | **Marca / Modelo:** {u_sel['marca_modelo']} | "
        f"**Año:** {u_sel['anio']} | **Número de motor:** {u_sel['numero_motor'] or 'N/A'} | "
        f"**Serie:** {u_sel['serie_vin'] or 'N/A'} | **Chofer:** {u_sel['chofer']}"
    )

    filas_actuales, _ = obtener_filas_unidad(u_sel)
    filas_filtradas = filtrar_por_frecuencia(filas_actuales, frecuencia_filtro)

    st.dataframe(
        filas_filtradas,
        use_container_width=True,
        hide_index=True,
        height=540,
    )

# ================= 2. CALENDARIO ANUAL 2026 =================
elif modulo == "Calendario Anual 2026":
    st.title(f"Calendario Anual de Mantenimiento 2026 — {EMPRESA}")
    st.caption("Las unidades están escalonadas por días hábiles (Lunes a Sábado) para evitar empalmes y respetar domingos no laborables.")

    c_cal1, c_cal2, c_cal3 = st.columns([1.2, 1.8, 1.2])
    mes_sel = c_cal1.selectbox(
        "Mes",
        list(MESES_ES.keys()),
        index=HOY_MX.month - 1 if HOY_MX.year == 2026 else 0,
        format_func=lambda m: f"{MESES_ES[m]} 2026"
    )
    opciones_pipa_cal = ["Todas las unidades"] + list(mapa_unidades.keys())
    pipa_cal_sel = c_cal2.selectbox("Unidad / pipa", opciones_pipa_cal)
    frec_cal_sel = c_cal3.selectbox("Frecuencia", FRECUENCIAS_ORDEN, key="frec_cal")

    unidades_a_mostrar = (
        list(enumerate(unidades))
        if pipa_cal_sel == "Todas las unidades"
        else [(obtener_desfase_unidad(mapa_unidades[pipa_cal_sel]), mapa_unidades[pipa_cal_sel])]
    )

    eventos_por_dia = {}
    detalle_mes = []

    for color_idx, u_obj in unidades_a_mostrar:
        filas_u, _ = obtener_filas_unidad(u_obj)
        filas_u = filtrar_por_frecuencia(filas_u, frec_cal_sel)
        for f in filas_u:
            try:
                f_dt = datetime.strptime(f["FECHA PROGRAMADA"], "%d/%m/%Y").date()
            except Exception:
                continue
            if f_dt.year == 2026 and f_dt.month == mes_sel:
                eventos_por_dia.setdefault(f_dt.day, []).append({
                    "color_idx": color_idx,
                    "folio": f["FOLIO"],
                    "id_unidad": u_obj["id_unidad"],
                    "resumen": _resumen_corto_actividad(f["ACTIVIDAD A REALIZAR"]),
                    "frecuencia": f["FRECUENCIA"],
                    "estado": f["ESTADO"],
                })
                detalle_mes.append({
                    "FECHA": f["FECHA PROGRAMADA"],
                    "DÍA": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][f_dt.weekday()],
                    "PIPA": f"ID {u_obj['id_unidad']} ({u_obj['marca_modelo']})",
                    "CHOFER": u_obj["chofer"],
                    "FOLIO": f["FOLIO"],
                    "TIPO": f["TIPO DE MANTENIMIENTO"],
                    "FRECUENCIA": f["FRECUENCIA"],
                    "ACTIVIDAD A REALIZAR": f["ACTIVIDAD A REALIZAR"],
                    "ESTADO": f["ESTADO"],
                    "RESPONSABLE": f["RESPONSABLE"],
                })

    st.markdown(
        "**Referencia de unidades:** "
        + " | ".join([f"Pipa ID {u['id_unidad']} ({u['marca_modelo']} - {u['chofer']})" for u in unidades])
    )

    html_cal = construir_html_calendario(2026, mes_sel, eventos_por_dia)
    st.markdown(html_cal, unsafe_allow_html=True)

    st.subheader(f"Detalle de actividades programadas — {MESES_ES[mes_sel]} 2026")
    if detalle_mes:
        detalle_mes.sort(key=lambda x: (datetime.strptime(x["FECHA"], "%d/%m/%Y").date(), x["PIPA"], x["FOLIO"]))
        st.dataframe(detalle_mes, use_container_width=True, hide_index=True)
    else:
        st.info("No hay actividades programadas con los filtros seleccionados en este mes.")

# ================= 3. GENERAR NUEVO MANTENIMIENTO =================
elif modulo == "GENERAR NUEVO MANTENIMIENTO":
    st.title(f"GENERAR NUEVO MANTENIMIENTO — {EMPRESA}")

    unidad_label = st.selectbox("Selecciona unidad / chofer", list(mapa_unidades.keys()), key="sel_unidad_nuevo")
    u_sel = mapa_unidades[unidad_label]
    filas_actuales, clave_tabla = obtener_filas_unidad(u_sel)

    with st.container(border=True):
        with st.form("form_nuevo_mant"):
            c1, c2, c3 = st.columns(3)
            tipo_mant = c1.selectbox("Tipo de mantenimiento", ["Preventivo", "Correctivo"])
            frecuencia_nuevo = c2.selectbox(
                "Frecuencia",
                ["Evento / Correctivo", "Semanal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual"]
            )
            fecha_nuevo = c3.date_input("Fecha programada", value=HOY_MX)

            c4, c5 = st.columns(2)
            asignado_a = c4.text_input("Asignado a (Responsable)", placeholder="Ej. Mecánico de turno / Chofer / Técnico LP")
            personal_nuevo = c5.text_input(
                "Personal competente necesario",
                value="Operador capacitado / Técnico de mantenimiento de unidad"
            )

            descripcion_nuevo = st.text_area(
                "Descripción / Actividad a realizar",
                placeholder="Describe el mantenimiento preventivo o correctivo a ejecutar..."
            )
            criterios_nuevo = st.text_area(
                "Criterios de aceptación o rechazo",
                value=(
                    "Aceptación: Sin fugas, componente operativo y seguro. "
                    "Rechazo: Fugas, falla operativa o condición insegura."
                )
            )

            crear_btn = st.form_submit_button("Generar mantenimiento", type="primary")

        if crear_btn:
            if not descripcion_nuevo.strip() or not asignado_a.strip():
                st.error("Completa la descripción de la actividad y a quién se asigna.")
            elif fecha_nuevo.weekday() == 6:
                st.error("No se programan mantenimientos en domingo porque es día no laborable.")
            else:
                siguiente_num = len(filas_actuales) + 1
                nuevo_folio = f"PRV-{siguiente_num:03d}" if tipo_mant == "Preventivo" else f"COR-{siguiente_num:03d}"
                cumplido_flag = fecha_nuevo <= HOY_MX

                nueva_fila = {
                    "FOLIO": nuevo_folio,
                    "TIPO DE MANTENIMIENTO": tipo_mant,
                    "FRECUENCIA": frecuencia_nuevo,
                    "FECHA PROGRAMADA": fecha_nuevo.strftime("%d/%m/%Y"),
                    "ACTIVIDAD A REALIZAR": descripcion_nuevo.strip(),
                    "CUMPLIO": "Sí" if cumplido_flag else "Pendiente",
                    "ESTADO": "Cerrado" if cumplido_flag else "Abierto",
                    "ACCIONES TOMADAS": "Asignado para ejecución" if not cumplido_flag else "Ejecutado conforme a fecha",
                    "RESPONSABLE": asignado_a.strip(),
                    "CRITERIOS DE ACEPTACIÓN O RECHAZO": criterios_nuevo.strip(),
                    "PERSONAL COMPETENTE": personal_nuevo.strip() or "Personal técnico competente",
                }
                filas_actuales.append(nueva_fila)
                st.session_state[clave_tabla] = normalizar_filas(filas_actuales)
                st.success(f"Mantenimiento {nuevo_folio} ({tipo_mant}) generado y asignado a {asignado_a.strip()}.")
                st.rerun()

    st.subheader(f"Mantenimientos registrados — ID {u_sel['id_unidad']}")
    st.dataframe(st.session_state[clave_tabla], use_container_width=True, hide_index=True, height=400)

# ================= 4. CERRAR MANTENIMIENTOS =================
elif modulo == "Cerrar Mantenimientos":
    st.title(f"Cerrar Mantenimientos — {EMPRESA}")

    c_top1, c_top2 = st.columns([2.2, 1.2])
    unidad_label = c_top1.selectbox("Selecciona unidad / chofer", list(mapa_unidades.keys()), key="sel_unidad_cierre")
    frecuencia_filtro_cierre = c_top2.selectbox("Filtrar por FRECUENCIA", FRECUENCIAS_ORDEN, key="filtro_freq_cierre")

    u_sel = mapa_unidades[unidad_label]
    filas_actuales, clave_tabla = obtener_filas_unidad(u_sel)

    pendientes = [f for f in filas_actuales if f.get("ESTADO") != "Cerrado"]
    pendientes_filtrados = filtrar_por_frecuencia(pendientes, frecuencia_filtro_cierre)

    if not pendientes:
        st.success("Todos los mantenimientos de esta unidad ya están cerrados.")
    elif not pendientes_filtrados:
        st.info("No hay mantenimientos abiertos para la frecuencia seleccionada.")
    else:
        folios_abiertos = [f["FOLIO"] for f in pendientes_filtrados]
        with st.container(border=True):
            with st.form("form_cerrar_mant"):
                c1, c2 = st.columns([1.5, 2.5])
                folio_sel = c1.selectbox("Folio abierto a cerrar", folios_abiertos)
                fila_actual = next((f for f in pendientes_filtrados if f["FOLIO"] == folio_sel), pendientes_filtrados[0])
                responsable_cierre = c2.text_input(
                    "RESPONSABLE",
                    value=fila_actual.get("RESPONSABLE", "Por asignar")
                )

                acciones_cierre = st.text_input(
                    "ACCIONES TOMADAS",
                    placeholder="Ej. Se revisó, ajustó y verificó sin fugas..."
                )

                cerrar_btn = st.form_submit_button("Cerrar mantenimiento", type="primary")

            if cerrar_btn:
                for f in filas_actuales:
                    if f["FOLIO"] == folio_sel:
                        f["ESTADO"] = "Cerrado"
                        f["CUMPLIO"] = "Sí"
                        f["RESPONSABLE"] = responsable_cierre.strip() or usuario["nombre"]
                        f["ACCIONES TOMADAS"] = acciones_cierre.strip() or "Mantenimiento cerrado"
                        break
                st.session_state[clave_tabla] = normalizar_filas(filas_actuales)
                st.success(f"Folio {folio_sel} cerrado. Ya no aparecerá en pendientes.")
                st.rerun()

        st.subheader("Mantenimientos abiertos pendientes de cierre")
        st.dataframe(pendientes_filtrados, use_container_width=True, hide_index=True, height=400)

# ================= 5. AGREGAR UNIDAD =================
elif modulo == "Agregar Unidad":
    st.title(f"Agregar Unidad — {EMPRESA}")

    with st.container(border=True):
        with st.form("form_agregar_unidad"):
            c1, c2, c3 = st.columns(3)
            id_u = c1.text_input("ID de unidad", placeholder="Ej. 006 o AT 21").strip().upper()
            marca_u = c2.text_input("Marca / Modelo", placeholder="Ej. FREIGHTLINER M2").strip().upper()
            anio_u = c3.text_input("Año", placeholder="Ej. 2015").strip()

            c4, c5, c6, c7 = st.columns(4)
            motor_u = c4.text_input("Número de motor", placeholder="Ej. 90291900...").strip().upper()
            serie_u = c5.text_input("Serie / VIN", placeholder="Ej. 3ALACY...").strip().upper()
            chofer_u = c6.text_input("Chofer", placeholder="Ej. JUAN PEREZ LOPEZ").strip().upper()
            placas_u = c7.text_input("Placas", placeholder="Ej. XY1234A").strip().upper()

            guardar_u = st.form_submit_button("Guardar unidad", type="primary")

        if guardar_u:
            if not id_u or not marca_u or not chofer_u:
                st.error("Completa al menos ID de unidad, Marca/Modelo y Chofer.")
            else:
                st.session_state.unidades_naupagas.append({
                    "id_unidad": id_u,
                    "marca_modelo": marca_u,
                    "numero_motor": motor_u,
                    "serie_vin": serie_u,
                    "anio": anio_u,
                    "chofer": chofer_u,
                    "placas": placas_u,
                })
                st.success(f"Unidad ID {id_u} agregada correctamente.")
                st.rerun()

    st.subheader("Unidades registradas")
    vista_unidades = [
        {
            "MARCA / MODELO": u["marca_modelo"],
            "NÚMERO DE MOTOR": u["numero_motor"],
            "SERIE / VIN": u["serie_vin"],
            "AÑO": u["anio"],
            "ID UNIDAD": u["id_unidad"],
            "CHOFER": u["chofer"],
            "PLACAS": u["placas"],
        }
        for u in unidades
    ]
    st.dataframe(vista_unidades, use_container_width=True, hide_index=True)
