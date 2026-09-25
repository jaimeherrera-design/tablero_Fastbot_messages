from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_logic import aggregate_with_variation, current_month_comparison, discover_csv_files, load_and_consolidate


DATA_DIR = Path(__file__).resolve().parent
COLORS = {
    "mint": "#50E3C2",
    "cyan": "#44B7F7",
    "amber": "#FFB547",
    "red": "#FF6376",
    "violet": "#C38BFA",
    "grid": "#253047",
}
CHART_SIGNAL_COLORS = {
    "mint": "#00F5A8",
    "amber": "#FFC400",
    "red": "#FF244E",
}
METRIC_LABELS = {
    "mensajes_enviados": "Enviados",
    "mensajes_leidos": "Leídos",
    "mensajes_fallidos": "Fallidos",
    "mensajes_facturables": "Facturables",
}
METRIC_COLORS = {
    "mensajes_enviados": COLORS["cyan"],
    "mensajes_leidos": COLORS["mint"],
    "mensajes_fallidos": COLORS["red"],
    "mensajes_facturables": COLORS["amber"],
}


st.set_page_config(page_title="Fastbot Messages", page_icon="▥", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Material+Symbols+Rounded:FILL@0..1&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { color-scheme: dark; }
    .stApp {
        background:
            radial-gradient(circle at 82% -12%, rgba(0,174,147,.14), transparent 30%),
            #020606;
        color: #edf3fc;
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0 !important; }
    .block-container { padding-top: 1.9rem; }
    [data-testid="stHeader"] { background: #020606; }
    [data-testid="stSidebar"] { background: #070d10; border-right: 1px solid #1b2c31; }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
    }
    [data-testid="stWidgetLabel"] p {
        font-weight: 700 !important;
    }
    [role="radiogroup"][aria-label="Fechas"] [role="radio"][aria-checked="false"] p {
        color: #9aa4ad !important;
    }
    [data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stExpandSidebarButton"] {
        width: 38px;
        height: 38px;
        border: 1px solid #50e3c2 !important;
        border-radius: 8px !important;
        background: #123d2d !important;
        color: #8ff7d5 !important;
        box-shadow: 0 0 0 1px rgba(80,227,194,.12), 0 6px 18px rgba(0,0,0,.28);
        transition: background-color .18s ease, box-shadow .18s ease, transform .18s ease;
    }
    [data-testid="stSidebarCollapseButton"] button:hover,
    button[data-testid="stExpandSidebarButton"]:hover {
        background: #18563f !important;
        box-shadow: 0 0 0 3px rgba(80,227,194,.18), 0 8px 22px rgba(0,0,0,.32);
        transform: translateY(-1px);
    }
    [data-testid="stSidebarCollapseButton"] button:focus-visible,
    button[data-testid="stExpandSidebarButton"]:focus-visible {
        outline: 2px solid #edf3fc !important;
        outline-offset: 2px;
    }
    [data-testid="stSidebarCollapseButton"] button span,
    button[data-testid="stExpandSidebarButton"] span { color: inherit !important; }
    .dashboard-banner {
        position: relative;
        overflow: hidden;
        min-height: 220px;
        margin-bottom: 26px;
        padding: 28px 48px;
        border: 1px solid #183d3a;
        border-radius: 18px;
        background:
            radial-gradient(circle at 89% 30%, rgba(0,194,165,.14), transparent 21%),
            linear-gradient(90deg, #020606 0%, #020707 58%, #071615 100%);
        box-shadow: inset 0 0 0 1px rgba(0,214,177,.03);
    }
    .banner-content { position: relative; z-index: 2; max-width: 76%; }
    .dashboard-banner .eyebrow { color: #21e0bf; font-size: .72rem; font-weight: 700; letter-spacing: .3em; text-transform: uppercase; }
    .dashboard-banner h1 { margin: 28px 0 18px !important; color: #f8fbfa; font-size: clamp(2.65rem, 3.8vw, 3.35rem) !important; font-weight: 700; line-height: 1.02; white-space: nowrap; }
    .dashboard-banner p { max-width: 900px; margin: 0; color: #d3d8dc; font-size: 1.06rem; font-weight: 500; line-height: 1.55; }
    .dashboard-banner strong { color: #50e3c2; }
    .banner-network { position: absolute; z-index: 1; inset: 0 0 0 62%; opacity: .9; }
    .banner-node, .banner-edge { position: absolute; display: block; }
    .banner-node { width: 11px; height: 11px; border-radius: 50%; background: #00b995; box-shadow: 0 0 8px #00b995, 0 0 22px rgba(0,185,149,.78); }
    .banner-node.blue { width: 14px; height: 14px; background: #318cab; box-shadow: 0 0 10px #318cab, 0 0 25px rgba(49,140,171,.7); }
    .banner-edge { height: 1px; background: rgba(0,185,149,.48); transform-origin: left center; }
    .banner-edge.faint { background: rgba(77,135,139,.17); }
    .bn1 { left: 8%; top: 12%; } .bn2 { left: 35%; top: 38%; } .bn3 { left: 68%; top: 8%; }
    .bn4 { left: 89%; top: 43%; } .bn5 { left: 57%; top: 73%; } .bn6 { left: 18%; top: 77%; }
    .be1 { left: 9%; top: 15%; width: 31%; transform: rotate(23deg); }
    .be2 { left: 36%; top: 40%; width: 40%; transform: rotate(-28deg); }
    .be3 { left: 69%; top: 11%; width: 29%; transform: rotate(34deg); }
    .be4 { left: 59%; top: 74%; width: 38%; transform: rotate(-35deg); }
    .be5 { left: 19%; top: 78%; width: 43%; transform: rotate(-11deg); }
    .be6 { left: 36%; top: 42%; width: 37%; transform: rotate(49deg); }
    .be7 { left: 9%; top: 15%; width: 68%; transform: rotate(52deg); }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 14px;
        margin: 14px 0 46px;
    }
    .kpi-card {
        overflow: hidden;
        min-width: 0;
        min-height: 118px;
        padding: 17px 13px 15px;
        border: 1px solid #1b2a32;
        border-radius: 12px;
        background: linear-gradient(180deg, #0b1116 0%, #080d11 100%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
    }
    .kpi-head { display: flex; min-width: 0; align-items: center; justify-content: space-between; gap: 10px; }
    .kpi-label { min-width: 0; overflow: hidden; color: #96a5b7; font-size: .78rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
    .kpi-icon {
        display: block;
        flex: 0 0 auto;
        width: auto;
        height: auto;
        overflow: visible;
        border: 0;
        border-radius: 0;
        background: transparent;
        color: var(--accent);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.7rem;
        font-weight: 700;
        font-style: normal;
        line-height: .9;
        white-space: nowrap;
    }
    .kpi-value {
        margin-top: 18px;
        overflow: hidden;
        color: var(--accent);
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.15rem, 1.35vw, 1.62rem);
        font-weight: 700;
        white-space: nowrap;
    }
    .kpi-subtext { margin-top: 7px; color: #6f8090; font-size: .82rem; font-weight: 700; white-space: nowrap; }
    .section-label { margin: 0 0 20px; color: #7d8b9d; font-size: .78rem; font-weight: 800; letter-spacing: .36em; text-transform: uppercase; }
    .stTabs [data-baseweb="tab-list"],
    [role="tablist"] {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 26px;
        align-items: center;
        min-height: 92px;
        margin: 20px 0 28px;
        padding: 16px 28px;
        border: 1px solid #2a3946;
        border-radius: 18px;
        background: #05090c;
        box-shadow: 0 16px 38px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.025);
    }
    .stTabs [data-baseweb="tab"],
    [role="tab"] {
        justify-content: center;
        height: 58px;
        padding: 0 10px;
        color: #8795aa;
        border-bottom: 0 !important;
        font-size: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] p,
    [role="tab"] p {
        margin: 0;
        color: inherit !important;
        font-size: 1.18rem;
        font-weight: 500;
        letter-spacing: 0;
        white-space: nowrap;
    }
    .stTabs [aria-selected="true"],
    [role="tab"][aria-selected="true"] { position: relative; color: #f5fbff !important; border-bottom: 0 !important; }
    .stTabs [aria-selected="true"] p,
    [role="tab"][aria-selected="true"] p { color: #f3fbff !important; }
    .stTabs [aria-selected="true"]::after,
    [role="tab"][aria-selected="true"]::after {
        content: "✓";
        display: inline-block;
        margin-left: 32px;
        color: #20dfbd;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; background: transparent; }
    [role="tab"] .react-aria-SelectionIndicator { display: none !important; }
    .matrix-shell { overflow: auto; max-height: 430px; border: 1px solid #29364d; border-radius: 8px; }
    table.kpi-matrix { width: 100%; border-collapse: collapse; background: #070b11; font-size: .8rem; }
    table.kpi-matrix th { position: sticky; top: 0; padding: 10px; background: #0d1522 !important; color: #fff !important; text-align: center; }
    table.kpi-matrix td { padding: 9px 10px; border-bottom: 1px solid #1d2939; color: #f4f8ff; text-align: center; }
    .insight-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 28px 14px; }
    .insight { min-height: 178px; padding: 16px; border: 1px solid color-mix(in srgb, var(--signal) 48%, #29364d); border-left: 4px solid var(--signal); border-radius: 8px; background: linear-gradient(145deg, color-mix(in srgb, var(--signal) 8%, #131c2c), #101725); }
    .insight-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .insight-meta { display: flex; align-items: center; gap: 9px; }
    .insight-icon { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid var(--signal); border-radius: 8px; background: color-mix(in srgb, var(--signal) 13%, transparent); color: var(--signal); font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; }
    .insight-label { color: #d6dfec; font-size: .76rem; font-weight: 700; text-transform: uppercase; }
    .insight-status { color: var(--signal); font-size: .68rem; font-weight: 700; text-transform: uppercase; }
    .insight strong { display: block; margin: 13px 0 7px; color: #f4f8ff; font-family: 'Space Grotesk'; }
    .insight p { margin: 0; color: #aab5c7; font-size: .88rem; line-height: 1.45; }
    @media (max-width: 1260px) { .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
    @media (max-width: 1000px) { .insight-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 600px) {
        .kpi-grid, .insight-grid { grid-template-columns: 1fr; }
        .dashboard-banner { min-height: 210px; padding: 24px 20px; border-radius: 12px; }
        .banner-content { max-width: 100%; }
        .dashboard-banner h1 { font-size: 28px !important; white-space: normal; }
        .dashboard-banner p { max-width: 88%; font-size: .84rem; line-height: 1.5; }
        .banner-network { inset: 40% -15% 0 42%; opacity: .32; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_pct(value: float | None, signed: bool = False) -> str:
    if value is None or pd.isna(value):
        return "Sin base"
    pattern = "+.2f" if signed else ".2f"
    return f"{value:{pattern}}%".replace(".", ",")


@st.cache_data(show_spinner="Consolidando archivos CSV...")
def load_data(file_signature: tuple[tuple[str, int, int], ...]) -> pd.DataFrame:
    return load_and_consolidate(DATA_DIR / name for name, _, _ in file_signature)


def style_figure(figure: go.Figure, height: int = 390) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=50, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#dfe7f3"),
        title_font=dict(family="Space Grotesk", size=17, color="#FFFFFF"),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#101725", font_color="#edf3fc"),
    )
    figure.update_xaxes(gridcolor=COLORS["grid"], zeroline=False)
    figure.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return figure


def rate(frame: pd.DataFrame, metric: str) -> float:
    sent = float(frame["mensajes_enviados"].sum())
    return float(frame[metric].sum() / sent * 100) if sent else 0.0


def rate_cell_style(value: float, high_is_good: bool) -> str:
    if pd.isna(value):
        return ""
    favorable = value >= 80 if high_is_good else value <= 5
    adverse = value < 50 if high_is_good else value > 15
    if favorable:
        return "background-color:#123d2d;color:#7ef0b2;font-weight:700"
    if adverse:
        return "background-color:#48202a;color:#ff91a0;font-weight:700"
    return "background-color:#473817;color:#ffd66b;font-weight:700"


def monthly_average_rate(frame: pd.DataFrame, metric: str) -> float:
    monthly = frame.groupby("mes", as_index=False)[["mensajes_enviados", metric]].sum()
    valid = monthly[monthly["mensajes_enviados"].gt(0)]
    if valid.empty:
        return 0.0
    return float((valid[metric] / valid["mensajes_enviados"] * 100).mean())


def build_kpi_matrix(frame: pd.DataFrame, period_label: str) -> tuple[pd.DataFrame, str]:
    period = {"Mes": "mes", "Día": "fecha", "Hora": "hora"}[period_label]
    matrix = frame.groupby(period, as_index=False)[list(METRIC_LABELS)].sum().sort_values(period)
    if period_label == "Mes":
        month_names = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
        }
        matrix["Periodo"] = matrix[period].map(lambda value: month_names[value.month])
    elif period_label == "Día":
        matrix["Periodo"] = matrix[period].dt.strftime("%d/%m/%Y")
    else:
        matrix["Periodo"] = matrix[period].map(lambda value: f"{int(value):02d}:00")
    matrix["% Leídos"] = matrix["mensajes_leidos"].div(matrix["mensajes_enviados"]).mul(100)
    matrix["% Fallidos"] = matrix["mensajes_fallidos"].div(matrix["mensajes_enviados"]).mul(100)
    matrix["% Facturables"] = matrix["mensajes_facturables"].div(matrix["mensajes_enviados"]).mul(100)
    matrix["Variación enviados"] = matrix["mensajes_enviados"].pct_change(fill_method=None).mul(100)
    matrix = matrix.rename(columns=METRIC_LABELS)
    return matrix[["Periodo", "Enviados", "Variación enviados", "Leídos", "% Leídos", "Fallidos", "% Fallidos", "Facturables", "% Facturables"]], period


def build_insights(frame: pd.DataFrame) -> list[tuple[str, str, str, str, str, str]]:
    sent = float(frame["mensajes_enviados"].sum())
    read_rate = rate(frame, "mensajes_leidos")
    failed_rate = rate(frame, "mensajes_fallidos")
    billable_rate = rate(frame, "mensajes_facturables")
    comparison = current_month_comparison(frame)
    daily = frame.groupby("fecha", as_index=False)["mensajes_enviados"].sum()
    hourly = frame.groupby("hora", as_index=False)["mensajes_enviados"].sum()
    peak_day = daily.loc[daily["mensajes_enviados"].idxmax()]
    peak_hour = hourly.loc[hourly["mensajes_enviados"].idxmax()]
    variation = comparison["variation"]
    peak_day_ratio = float(peak_day["mensajes_enviados"] / max(daily["mensajes_enviados"].mean(), 1))
    peak_hour_share = float(peak_hour["mensajes_enviados"] / max(sent, 1) * 100)
    if variation is None:
        trend_status, trend_color = "Sin base", COLORS["amber"]
    elif variation < -10:
        trend_status, trend_color = "Acción prioritaria", COLORS["red"]
    elif variation > 15:
        trend_status, trend_color = "Atención capacidad", COLORS["amber"]
    else:
        trend_status, trend_color = "Estable", COLORS["mint"]
    read_status, read_color = (("Saludable", COLORS["mint"]) if read_rate >= 80 else ("Atención", COLORS["amber"]) if read_rate >= 65 else ("Acción prioritaria", COLORS["red"]))
    failed_status, failed_color = (("Saludable", COLORS["mint"]) if failed_rate <= 5 else ("Atención", COLORS["amber"]) if failed_rate <= 15 else ("Acción prioritaria", COLORS["red"]))
    billed_status, billed_color = (("Saludable", COLORS["mint"]) if billable_rate >= 80 else ("Atención", COLORS["amber"]) if billable_rate >= 60 else ("Acción prioritaria", COLORS["red"]))
    day_status, day_color = (("Distribución estable", COLORS["mint"]) if peak_day_ratio <= 1.25 else ("Atención capacidad", COLORS["amber"]) if peak_day_ratio <= 1.5 else ("Alta concentración", COLORS["red"]))
    hour_status, hour_color = (("Distribución estable", COLORS["mint"]) if peak_hour_share <= 8 else ("Atención capacidad", COLORS["amber"]) if peak_hour_share <= 12 else ("Alta concentración", COLORS["red"]))
    return [
        (
            "↗",
            "Volumen MTD",
            trend_status,
            f"Variación {format_pct(variation, signed=True)}",
            f"Van {format_number(comparison['current'])} envíos frente a {format_number(comparison['previous'])} al mismo corte. Decisión: ajuste capacidad y meta comercial según la tendencia.",
            trend_color,
        ),
        ("✓", "Lectura", read_status, f"{read_rate:.2f}% de lectura", "Objetivo saludable: 80% o más. Decisión: si baja del objetivo, revise contenido, audiencia y horario de envío.", read_color),
        ("!", "Fallos", failed_status, f"{failed_rate:.2f}% de fallos", f"Referencia mensual: {monthly_average_rate(frame, 'mensajes_fallidos'):.2f}%. Decisión: priorice diagnóstico de rutas y franjas con mayor tasa.", failed_color),
        ("$", "Facturación", billed_status, f"{billable_rate:.2f}% facturable", "Objetivo saludable: 80% o más. Decisión: concilie reglas de cobro y mensajes no facturables antes del cierre.", billed_color),
        ("▣", "Pico diario", day_status, f"{peak_day['fecha']:%d/%m/%Y} · {peak_day_ratio:.2f}× el promedio", f"Se enviaron {format_number(float(peak_day['mensajes_enviados']))} mensajes. Decisión: reserve capacidad para días con más de 1,5× el promedio.", day_color),
        ("◷", "Pico horario", hour_status, f"{int(peak_hour['hora']):02d}:00 · {peak_hour_share:.2f}% del tráfico", "Decisión: refuerce monitoreo y capacidad cuando una hora concentre más del 12% de los envíos.", hour_color),
    ]


def build_heatmap(frame: pd.DataFrame, metric: str, title: str, colorscale: list[list[object]]) -> go.Figure:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    values = frame.pivot_table(index="hora", columns="dia_semana", values=metric, aggfunc="sum", fill_value=0)
    values = values.reindex(index=range(24), columns=day_order, fill_value=0)
    labels = values.map(lambda value: f"{value / 1_000_000:.1f}M" if value >= 1_000_000 else f"{value / 1_000:.0f}K" if value >= 1_000 else f"{value:.0f}")
    figure = go.Figure(go.Heatmap(
        z=values.values,
        x=day_labels,
        y=values.index,
        text=labels.values,
        texttemplate="%{text}",
        colorscale=colorscale,
        colorbar=dict(title=METRIC_LABELS[metric], tickformat="~s"),
        xgap=2,
        ygap=2,
        hovertemplate=f"%{{x}} · %{{y}}:00<br>%{{z:,.0f}} {METRIC_LABELS[metric].lower()}<extra></extra>",
    ))
    figure = style_figure(figure, 440)
    figure.update_layout(title=dict(text=title, font=dict(family="Space Grotesk", size=17, color="#FFFFFF")))
    return figure


def build_rate_heatmap(frame: pd.DataFrame, metric: str, colorscale: list[list[object]]) -> go.Figure:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    numerator = frame.pivot_table(
        index="hora", columns="dia_semana", values=metric, aggfunc="sum", fill_value=0
    ).reindex(index=range(24), columns=day_order, fill_value=0)
    sent = frame.pivot_table(
        index="hora", columns="dia_semana", values="mensajes_enviados", aggfunc="sum", fill_value=0
    ).reindex(index=range(24), columns=day_order, fill_value=0)
    rates = numerator.div(sent.where(sent.gt(0))).mul(100).fillna(0)
    labels = rates.map(lambda value: f"{value:.2f}%")
    figure = go.Figure(go.Heatmap(
        z=rates.values,
        x=day_labels,
        y=rates.index,
        text=labels.values,
        texttemplate="%{text}",
        colorscale=colorscale,
        colorbar=dict(title=f"% {METRIC_LABELS[metric]}", ticksuffix="%", tickformat=".1f"),
        xgap=2,
        ygap=2,
        hovertemplate=f"%{{x}} · %{{y}}:00<br>%{{z:.2f}}% {METRIC_LABELS[metric].lower()}<extra></extra>",
    ))
    figure = style_figure(figure, 440)
    figure.update_layout(title=dict(
        text=f"Tasa de {METRIC_LABELS[metric].lower()} por día y hora",
        font=dict(family="Space Grotesk", size=17, color="#FFFFFF"),
    ))
    return figure


files = discover_csv_files(DATA_DIR)
if not files:
    st.error("No se encontraron archivos CSV en la carpeta del proyecto.")
    st.stop()

signature = tuple((path.name, path.stat().st_mtime_ns, path.stat().st_size) for path in files)
try:
    data = load_data(signature)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"No fue posible consolidar los CSV: {error}")
    st.stop()

if data.empty:
    st.warning("Los archivos no contienen registros válidos.")
    st.stop()

with st.sidebar:
    st.markdown("## Filtros")
    min_date = data["fecha"].min().date()
    max_date = data["fecha"].max().date()
    st.markdown("**Periodo de análisis**")
    date_mode = st.segmented_control(
        "Fechas", ["Todas", "Una fecha", "Rango"], default="Todas", key="date_mode"
    ) or "Todas"
    if date_mode == "Una fecha":
        single_date = st.date_input(
            "Fecha", value=max_date, min_value=min_date, max_value=max_date, key="single_date"
        )
        start_date = end_date = pd.Timestamp(single_date)
    elif date_mode == "Rango":
        range_left, range_right = st.columns(2)
        with range_left:
            range_start = st.date_input(
                "Desde", value=min_date, min_value=min_date, max_value=max_date, key="range_start"
            )
        with range_right:
            range_end = st.date_input(
                "Hasta", value=max_date, min_value=min_date, max_value=max_date, key="range_end"
            )
        start_date, end_date = pd.Timestamp(range_start), pd.Timestamp(range_end)
    else:
        start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)
    available_months = sorted(data["fecha"].dt.to_period("M").unique())
    month_names_filter = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }
    month_options: dict[str, pd.Period | None] = {"Todos los meses": None}
    month_options.update(
        {f"{month_names_filter[month.month]} {month.year}": month for month in available_months}
    )
    selected_month_label = st.selectbox("Mes", list(month_options))
    selected_month = month_options[selected_month_label]
    selected_agents = st.multiselect("Agente", sorted(data["agent"].unique()))
    selected_mime = st.multiselect("Tipo MIME", sorted(data["mime_type"].unique()))
    st.divider()
    st.caption(f"{len(files)} archivo(s) consolidado(s)")
    latest_data = data["fecha_hora"].max()
    st.caption(f"Último registro: {latest_data:%d/%m/%Y %H:%M}")

filtered = data.copy()
if selected_agents:
    filtered = filtered[filtered["agent"].isin(selected_agents)]
if selected_mime:
    filtered = filtered[filtered["mime_type"].isin(selected_mime)]
if start_date > end_date:
    st.sidebar.error("La fecha 'Desde' no puede ser posterior a 'Hasta'.")
    st.stop()
filtered = filtered[filtered["fecha"].between(start_date, end_date)]
if selected_month is not None:
    filtered = filtered[filtered["fecha"].dt.to_period("M").eq(selected_month)]

display_start = filtered["fecha"].min() if not filtered.empty else start_date
display_end = filtered["fecha"].max() if not filtered.empty else end_date
latest_filtered = filtered["fecha_hora"].max() if not filtered.empty else None
latest_filtered_text = latest_filtered.strftime("%d/%m/%Y %H:%M") if latest_filtered is not None else "Sin datos"

st.markdown(
    f"""
    <section class="dashboard-banner">
        <div class="banner-content">
            <span class="eyebrow">▥ &nbsp; Analítica de mensajería · IA</span>
            <h1 class="notranslate" translate="no" lang="en">Fastbot Messages</h1>
            <p>Monitoreo consolidado &nbsp;|&nbsp; Periodo analizado: <strong>{display_start:%d/%m/%Y} → {display_end:%d/%m/%Y}</strong> &nbsp;|&nbsp; <strong>{len(files)}</strong> CSV consolidado(s) &nbsp;|&nbsp; Último registro: <strong>{latest_filtered_text}</strong></p>
        </div>
        <div class="banner-network" aria-hidden="true">
            <span class="banner-edge be1"></span><span class="banner-edge be2"></span>
            <span class="banner-edge be3 faint"></span><span class="banner-edge be4"></span>
            <span class="banner-edge be5"></span><span class="banner-edge be6 faint"></span>
            <span class="banner-edge be7 faint"></span>
            <span class="banner-node bn1"></span><span class="banner-node blue bn2"></span>
            <span class="banner-node bn3"></span><span class="banner-node bn4"></span>
            <span class="banner-node blue bn5"></span><span class="banner-node bn6"></span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada.")
    st.stop()

totals = {metric: float(filtered[metric].sum()) for metric in METRIC_LABELS}
rates = {
    "mensajes_leidos": rate(filtered, "mensajes_leidos"),
    "mensajes_fallidos": rate(filtered, "mensajes_fallidos"),
    "mensajes_facturables": rate(filtered, "mensajes_facturables"),
}
cards = [
    ("Mensajes enviados", format_number(totals["mensajes_enviados"]), "➤", COLORS["cyan"]),
    ("Mensajes leídos", format_number(totals["mensajes_leidos"]), "✓", COLORS["mint"]),
    ("Mensajes fallidos", format_number(totals["mensajes_fallidos"]), "×", COLORS["red"]),
    ("Mensajes facturables", format_number(totals["mensajes_facturables"]), "$", COLORS["amber"]),
    ("% de leídos", format_pct(rates["mensajes_leidos"]), "✓", COLORS["mint"]),
    ("% de fallidos", format_pct(rates["mensajes_fallidos"]), "!", COLORS["red"]),
    ("% de facturables", format_pct(rates["mensajes_facturables"]), "$", COLORS["amber"]),
]
card_html = "".join(
    f'<article class="kpi-card" style="--accent:{color}"><div class="kpi-head"><span class="kpi-label">{label}</span><span class="kpi-icon" title="{label}" aria-label="{label}">{icon}</span></div><div class="kpi-value">{value}</div></article>'
    for label, value, icon, color in cards
)
st.markdown('<p class="section-label">Indicadores clave de gestión</p>', unsafe_allow_html=True)
st.markdown(f'<section class="kpi-grid">{card_html}</section>', unsafe_allow_html=True)

timeline_tab, quality_tab, insights_tab = st.tabs(["📊 Evolución y variaciones", "👩‍💼 Calidad y mapas de calor", "💡 Insights"])

with timeline_tab:
    control_left, control_right = st.columns(2)
    with control_left:
        period_label = st.segmented_control("Granularidad", ["Mes", "Día", "Hora"], default="Mes") or "Mes"
    with control_right:
        selected_metric = st.selectbox("Métrica", list(METRIC_LABELS), format_func=METRIC_LABELS.get)
    period = {"Mes": "mes", "Día": "fecha", "Hora": "hora"}[period_label]
    timeline = aggregate_with_variation(filtered, period, selected_metric)
    month_names = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }
    month_ticks = timeline["mes"] if period_label == "Mes" else pd.Series(dtype="datetime64[ns]")
    month_labels = [month_names[value.month] for value in month_ticks]
    day_of_month = pd.DataFrame()
    if period_label == "Día":
        daily_by_date = filtered.groupby("fecha", as_index=False)[selected_metric].sum()
        daily_by_date["dia_mes"] = daily_by_date["fecha"].dt.day
        day_of_month = daily_by_date.groupby("dia_mes", as_index=False)[selected_metric].mean()
        day_of_month["variacion"] = day_of_month[selected_metric].pct_change(fill_method=None) * 100
    chart_left, chart_right = st.columns([1.65, 1])
    with chart_left:
        if period_label == "Mes":
            monthly_average = float(timeline[selected_metric].mean())
            bar_colors = [
                CHART_SIGNAL_COLORS["mint"] if value > monthly_average * 1.05
                else CHART_SIGNAL_COLORS["red"] if value < monthly_average * 0.95
                else CHART_SIGNAL_COLORS["amber"]
                for value in timeline[selected_metric]
            ]
            volume_chart = px.bar(
                timeline,
                x=period,
                y=selected_metric,
                text=[format_number(value) for value in timeline[selected_metric]],
                title=f"{METRIC_LABELS[selected_metric]} por mes",
            )
            volume_chart.update_traces(
                marker_color=bar_colors,
                marker_line_width=0,
                opacity=.98,
                textposition="outside",
                cliponaxis=False,
            )
            volume_chart.add_hline(
                y=monthly_average,
                line_width=2,
                line_dash="dash",
                line_color="#EDF3FC",
                annotation_text=f"Promedio · {format_number(monthly_average)}",
                annotation_position="top right",
                annotation_font_color="#EDF3FC",
            )
            volume_chart.update_layout(margin=dict(l=12, r=12, t=68, b=12))
            volume_chart.update_xaxes(tickmode="array", tickvals=month_ticks, ticktext=month_labels, title_text="Mes")
        elif period_label == "Día":
            daily_average = float(day_of_month[selected_metric].mean())
            day_colors = [
                COLORS["mint"] if value > daily_average * 1.05
                else COLORS["red"] if value < daily_average * 0.95
                else COLORS["amber"]
                for value in day_of_month[selected_metric]
            ]
            volume_chart = px.line(
                day_of_month,
                x="dia_mes",
                y=selected_metric,
                markers=True,
                title=f"{METRIC_LABELS[selected_metric]} por día del mes",
                color_discrete_sequence=[METRIC_COLORS[selected_metric]],
            )
            volume_chart.update_traces(
                line_width=2.5,
                marker=dict(size=9, color=day_colors, line=dict(width=1.5, color="#0C111C")),
            )
            volume_chart.add_hline(
                y=daily_average,
                line_width=2,
                line_dash="dash",
                line_color="#EDF3FC",
                annotation_text=f"Promedio · {format_number(daily_average)}",
                annotation_position="top right",
                annotation_font_color="#EDF3FC",
            )
            volume_chart.update_xaxes(
                tickmode="array",
                tickvals=list(range(1, 32)),
                ticktext=[str(day) for day in range(1, 32)],
                tickfont=dict(size=9),
                title_text="Día del mes",
                range=[0.5, 31.5],
                automargin=True,
            )
        else:
            volume_chart = px.line(
                timeline,
                x=period,
                y=selected_metric,
                markers=True,
                title=f"{METRIC_LABELS[selected_metric]} por {period_label.lower()}",
                color_discrete_sequence=[METRIC_COLORS[selected_metric]],
            )
            volume_chart.update_traces(line_width=2.5, marker_size=7)
        st.plotly_chart(style_figure(volume_chart), use_container_width=True)
    with chart_right:
        variation_data = (
            day_of_month.dropna(subset=["variacion"])
            if period_label == "Día"
            else timeline.dropna(subset=["variacion"])
        )
        variation_period = "dia_mes" if period_label == "Día" else period
        variation_chart = px.bar(
            variation_data,
            x=variation_period,
            y="variacion",
            text=[f"{value:+.2f}%" for value in variation_data["variacion"]],
            title="Variación vs. período anterior (%)",
            color="variacion",
            color_continuous_scale=[
                [0, CHART_SIGNAL_COLORS["red"]],
                [.5, CHART_SIGNAL_COLORS["amber"]],
                [1, CHART_SIGNAL_COLORS["mint"]],
            ],
            color_continuous_midpoint=0,
        )
        variation_chart.update_traces(
            marker_line_width=0,
            opacity=.98,
            textposition="outside",
            cliponaxis=False,
        )
        variation_chart.update_layout(coloraxis_showscale=False)
        variation_chart.update_yaxes(ticksuffix="%")
        if period_label == "Mes":
            variation_chart.update_xaxes(
                tickmode="array", tickvals=month_ticks, ticktext=month_labels, title_text="Mes"
            )
        elif period_label == "Día":
            variation_chart.update_xaxes(
                tickmode="array",
                tickvals=list(range(1, 32)),
                ticktext=[str(day) for day in range(1, 32)],
                tickfont=dict(size=9),
                title_text="Día del mes",
                range=[0.5, 31.5],
                automargin=True,
            )
        st.plotly_chart(style_figure(variation_chart), use_container_width=True)

    st.subheader("Matriz de indicadores")
    matrix_period = st.segmented_control("Detalle", ["Mes", "Día", "Hora"], default="Mes", key="matrix_period") or "Mes"
    matrix, _ = build_kpi_matrix(filtered, matrix_period)
    matrix_style = (
        matrix.style
        .format({
            "Enviados": format_number,
            "Leídos": format_number,
            "Fallidos": format_number,
            "Facturables": format_number,
            "% Leídos": "{:.2f}%",
            "% Fallidos": "{:.2f}%",
            "% Facturables": "{:.2f}%",
            "Variación enviados": lambda value: "—" if pd.isna(value) else f"{value:+.2f}%",
        })
        .map(lambda value: rate_cell_style(value, True), subset=["% Leídos", "% Facturables"])
        .map(lambda value: rate_cell_style(value, False), subset=["% Fallidos"])
        .hide(axis="index")
        .set_table_attributes('class="kpi-matrix"')
    )
    st.markdown(f'<div class="matrix-shell">{matrix_style.to_html()}</div>', unsafe_allow_html=True)

with quality_tab:
    trend = filtered.copy()
    trend["dia_mes"] = trend["fecha"].dt.day
    trend = trend.groupby("dia_mes", as_index=False)[list(METRIC_LABELS)].sum()
    for metric in ["mensajes_leidos", "mensajes_fallidos", "mensajes_facturables"]:
        trend[f"% {METRIC_LABELS[metric]}"] = trend[metric].div(trend["mensajes_enviados"]).mul(100)
    rate_columns = ["% Leídos", "% Fallidos", "% Facturables"]
    rate_chart = px.line(
        trend,
        x="dia_mes",
        y=rate_columns,
        markers=True,
        title="Evolución diaria de tasas",
        color_discrete_map={"% Leídos": COLORS["mint"], "% Fallidos": COLORS["red"], "% Facturables": COLORS["amber"]},
    )
    rate_chart.update_traces(marker=dict(size=7, line=dict(width=1, color="#0C111C")), line_width=2.2)
    rate_chart.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 32)),
        ticktext=[str(day) for day in range(1, 32)],
        tickfont=dict(size=9),
        title_text="Día del mes",
        range=[0.5, 31.5],
        automargin=True,
    )
    rate_chart.update_yaxes(ticksuffix="%")
    rate_chart.update_layout(legend=dict(font=dict(color="#FFFFFF"), title_font=dict(color="#FFFFFF")))
    st.plotly_chart(style_figure(rate_chart, 420), use_container_width=True)

    favorable_heatmap_scale = [[0, "#241322"], [0.45, "#12324f"], [1, "#00a878"]]
    failure_heatmap_scale = [[0, "#063f34"], [0.45, "#6a4a08"], [1, "#b4233f"]]
    st.plotly_chart(
        build_heatmap(
            filtered,
            "mensajes_enviados",
            "Intensidad de envíos por día y hora",
            favorable_heatmap_scale,
        ),
        use_container_width=True,
    )
    heatmap_metric = st.selectbox(
        "Métrica del mapa de calidad",
        ["mensajes_leidos", "mensajes_fallidos", "mensajes_facturables"],
        format_func=METRIC_LABELS.get,
    )
    quality_heatmap_scale = (
        failure_heatmap_scale if heatmap_metric == "mensajes_fallidos" else favorable_heatmap_scale
    )
    st.plotly_chart(
        build_rate_heatmap(
            filtered,
            heatmap_metric,
            quality_heatmap_scale,
        ),
        use_container_width=True,
    )

with insights_tab:
    st.subheader("Señales operativas")
    insight_cards = "".join(
        f'<article class="insight" style="--signal:{color}">'
        f'<div class="insight-head"><div class="insight-meta"><span class="insight-icon">{icon}</span>'
        f'<span class="insight-label">{label}</span></div><span class="insight-status">{status}</span></div>'
        f'<strong>{title}</strong><p>{description}</p></article>'
        for icon, label, status, title, description, color in build_insights(filtered)
    )
    st.markdown(f'<section class="insight-grid">{insight_cards}</section>', unsafe_allow_html=True)

st.caption("Los indicadores se calculan con la suma de cada métrica. Los CSV nuevos se incorporan al recargar la aplicación y los solapamientos se sustituyen con el archivo más reciente.")