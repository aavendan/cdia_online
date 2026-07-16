import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from scipy import stats
from sklearn.cluster import KMeans
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_materias_pendientes

st.set_page_config(page_title="Materias Pendientes - CDIA", page_icon="📚", layout="wide")
st.title("Comparativo de avance en el malla para estudiantes de la cohorte PAO II 2024 - modalidad híbrida y en línea")

df = cargar_materias_pendientes()

COLOR_MAP = {"en línea": "#1565c0", "híbrida": "#ef6c00"}

st.subheader("Número de Estudiantes por Modalidad")
modalidades = sorted(df["modalidad"].unique())
cols = st.columns(len(modalidades))
for col, mod in zip(cols, modalidades):
    estudiantes_mod = df[df["modalidad"] == mod]["nombre"].nunique()
    with col:
        st.metric(mod.capitalize(), estudiantes_mod)

st.markdown("---")
st.subheader("¿Los estudiantes de modalidad híbrida y en línea presentan diferentes niveles de penalidad?")

# --- Estadísticos descriptivos ---
resumen_stats = df.groupby("modalidad")["penalidad"].agg(
    Media="mean", Mediana="median", Desv_Estandar="std",
    Q1=lambda s: s.quantile(0.25), Q3=lambda s: s.quantile(0.75),
).reset_index()
resumen_stats["RIC"] = resumen_stats["Q3"] - resumen_stats["Q1"]
tabla_stats = resumen_stats[["modalidad", "Media", "Mediana", "Desv_Estandar", "RIC"]].copy()
tabla_stats.columns = ["Modalidad", "Media", "Mediana", "Desviación Estándar", "Rango Intercuartílico"]
tabla_stats["Modalidad"] = tabla_stats["Modalidad"].str.capitalize()
tabla_stats = tabla_stats.round(2)
st.dataframe(tabla_stats, width="stretch", hide_index=True)

col_a, col_b = st.columns(2)
with col_a:
    st.caption("Diferencias en la penalidad entre estudiantes de modalidad híbrida y en línea")
    fig_box = px.box(
        df, x="modalidad", y="penalidad", color="modalidad",
        color_discrete_map=COLOR_MAP, points="all",
        labels={"modalidad": "Modalidad", "penalidad": "Penalidad"},
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, width="stretch")
with col_b:
    st.caption("Análisis comparativo de la penalidad académica según la modalidad")
    fig_violin = px.violin(
        df, x="modalidad", y="penalidad", color="modalidad",
        color_discrete_map=COLOR_MAP, box=True, points="all",
        labels={"modalidad": "Modalidad", "penalidad": "Penalidad"},
    )
    fig_violin.update_layout(showlegend=False)
    st.plotly_chart(fig_violin, width="stretch")

col_c, col_d = st.columns(2)
with col_c:
    st.caption("Distribución de frecuencias de la penalidad entre modalidades")
    fig_hist = px.histogram(
        df, x="penalidad", color="modalidad", barmode="overlay", opacity=0.6,
        color_discrete_map=COLOR_MAP, nbins=int(df["penalidad"].max() - df["penalidad"].min()) + 1,
        labels={"penalidad": "Penalidad", "modalidad": "Modalidad"},
    )
    fig_hist.update_layout(legend_title_text="")
    st.plotly_chart(fig_hist, width="stretch")
with col_d:
    st.caption("Curvas de densidad de la penalidad por modalidad")
    grupos = [df[df["modalidad"] == mod]["penalidad"].values for mod in modalidades]
    fig_kde = ff.create_distplot(
        grupos, [mod.capitalize() for mod in modalidades],
        colors=[COLOR_MAP.get(mod, None) for mod in modalidades],
        show_hist=False, show_rug=False,
    )
    fig_kde.update_layout(xaxis_title="Penalidad", yaxis_title="Densidad", legend_title_text="")
    st.plotly_chart(fig_kde, width="stretch")

st.markdown("---")
st.subheader("¿En qué niveles existen mayores diferencias entre modalidades?")
st.caption(
    "La Penalidad depende únicamente del Nivel de la malla, por lo que no varía entre modalidades dentro de "
    "un mismo nivel. La comparación se realiza sobre el número de materias pendientes por estudiante en cada "
    "nivel, que sí refleja diferencias reales de avance entre modalidades."
)

NIVELES_ORDEN = ["100-I", "100-II", "200-I", "200-II", "300-I"]
niveles_disp = [n for n in NIVELES_ORDEN if n in df["nivel"].unique()]

pendientes_est = (
    df.groupby(["matricula", "nombre", "modalidad", "nivel"])
    .size()
    .reset_index(name="materias_pendientes")
)
resumen_nivel_mod = (
    pendientes_est.groupby(["nivel", "modalidad"])["materias_pendientes"]
    .mean()
    .reset_index(name="promedio_pendientes")
)

# --- Insight: nivel con mayor diferencia entre modalidades ---
pivot_diff = resumen_nivel_mod.pivot(index="nivel", columns="modalidad", values="promedio_pendientes")
pivot_diff = pivot_diff.reindex(niveles_disp)
pivot_diff["diferencia"] = (pivot_diff[modalidades[0]] - pivot_diff[modalidades[1]]).abs()
nivel_max_diff = pivot_diff["diferencia"].idxmax()
st.info(
    f"El nivel con mayor diferencia entre modalidades es **{nivel_max_diff}**, con una brecha de "
    f"**{pivot_diff.loc[nivel_max_diff, 'diferencia']:.2f}** materias pendientes en promedio por estudiante."
)

st.caption("Promedio de Materias Pendientes por Estudiante, según Nivel y Modalidad")
fig_bar = px.bar(
    resumen_nivel_mod, x="nivel", y="promedio_pendientes", color="modalidad", barmode="group",
    color_discrete_map=COLOR_MAP, text_auto=".2f",
    category_orders={"nivel": niveles_disp},
    labels={"nivel": "Nivel", "promedio_pendientes": "Promedio de Materias Pendientes", "modalidad": "Modalidad"},
    title="Promedio de Materias Pendientes por Estudiante según Nivel y Modalidad",
)
fig_bar.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
st.plotly_chart(fig_bar, width="stretch")

col_e, col_f = st.columns(2)
with col_e:
    pivot_heat = resumen_nivel_mod.pivot(index="modalidad", columns="nivel", values="promedio_pendientes")
    pivot_heat = pivot_heat.reindex(columns=niveles_disp)
    pivot_heat.index = [m.capitalize() for m in pivot_heat.index]
    fig_heat = px.imshow(
        pivot_heat, text_auto=".2f", color_continuous_scale="Oranges", aspect="auto",
        labels=dict(x="Nivel", y="Modalidad", color="Promedio de<br>Materias Pendientes"),
        title="Mapa de Calor: Promedio de Materias Pendientes por Modalidad y Nivel",
    )
    st.plotly_chart(fig_heat, width="stretch")
with col_f:
    fig_box_nivel = px.box(
        pendientes_est, x="nivel", y="materias_pendientes", color="modalidad",
        color_discrete_map=COLOR_MAP, points="all",
        category_orders={"nivel": niveles_disp},
        labels={"nivel": "Nivel", "materias_pendientes": "Materias Pendientes", "modalidad": "Modalidad"},
        title="Distribución de Materias Pendientes por Estudiante según Nivel y Modalidad",
    )
    fig_box_nivel.update_layout(legend_title_text="", yaxis=dict(rangemode="tozero"))
    st.plotly_chart(fig_box_nivel, width="stretch")

st.markdown("---")
st.subheader("¿La diferencia en penalidad corresponde a un retraso académico real?")
st.caption(
    "Se compara el número total de materias pendientes por estudiante entre modalidades, y se contrasta "
    "contra la penalidad total acumulada, para validar si la penalidad refleja el retraso académico real "
    "o si oculta diferencias en el volumen de materias pendientes."
)

resumen_est = df.groupby(["matricula", "nombre", "modalidad"]).agg(
    materias_pendientes=("materia", "count"), penalidad_total=("penalidad", "sum")
).reset_index()

# --- Estadísticos descriptivos de materias pendientes por estudiante ---
stats_mp = resumen_est.groupby("modalidad")["materias_pendientes"].agg(
    Media="mean", Mediana="median", Desv_Estandar="std",
    Q1=lambda s: s.quantile(0.25), Q3=lambda s: s.quantile(0.75),
).reset_index()
stats_mp["RIC"] = stats_mp["Q3"] - stats_mp["Q1"]
tabla_mp = stats_mp[["modalidad", "Media", "Mediana", "Desv_Estandar", "RIC"]].copy()
tabla_mp.columns = ["Modalidad", "Media", "Mediana", "Desviación Estándar", "Rango Intercuartílico"]
tabla_mp["Modalidad"] = tabla_mp["Modalidad"].str.capitalize()
tabla_mp = tabla_mp.round(2)
st.dataframe(tabla_mp, width="stretch", hide_index=True)

# --- Prueba estadística: ¿difiere el número de materias pendientes entre modalidades? ---
g1 = resumen_est[resumen_est["modalidad"] == modalidades[0]]["materias_pendientes"]
g2 = resumen_est[resumen_est["modalidad"] == modalidades[1]]["materias_pendientes"]
u_stat, p_value = stats.mannwhitneyu(g1, g2, alternative="two-sided")
corr, _ = stats.pearsonr(resumen_est["penalidad_total"], resumen_est["materias_pendientes"])

es_significativo = p_value < 0.05
mod_mayor = modalidades[0] if g1.mean() > g2.mean() else modalidades[1]
diferencia_txt = "una diferencia estadísticamente significativa" if es_significativo else "una diferencia que no es estadísticamente significativa"
st.info(
    f"Prueba de Mann-Whitney U: **p = {p_value:.3f}**, lo que indica {diferencia_txt} (α = 0.05) en el número "
    f"de materias pendientes entre modalidades. En promedio, la modalidad **{mod_mayor.capitalize()}** presenta "
    f"más materias pendientes por estudiante ({g1.mean():.2f} en línea vs {g2.mean():.2f} híbrida). La correlación "
    f"entre penalidad total y número de materias pendientes es **{corr:.2f}**: la penalidad sí refleja el retraso "
    f"académico acumulado, pero {'la diferencia en volumen de materias pendientes confirma' if es_significativo else 'no hay evidencia suficiente para confirmar'} "
    f"que ese retraso varía realmente entre modalidades."
)

col_g, col_h = st.columns(2)
with col_g:
    fig_box_mp = px.box(
        resumen_est, x="modalidad", y="materias_pendientes", color="modalidad",
        color_discrete_map=COLOR_MAP, points="all",
        labels={"modalidad": "Modalidad", "materias_pendientes": "Materias Pendientes"},
        title="Materias Pendientes por Estudiante según Modalidad",
    )
    fig_box_mp.update_layout(showlegend=False)
    st.plotly_chart(fig_box_mp, width="stretch")
with col_h:
    fig_scatter = px.scatter(
        resumen_est, x="materias_pendientes", y="penalidad_total", color="modalidad",
        color_discrete_map=COLOR_MAP, trendline="ols",
        labels={"materias_pendientes": "Materias Pendientes", "penalidad_total": "Penalidad Total", "modalidad": "Modalidad"},
        title="Penalidad Total vs. Materias Pendientes por Estudiante",
    )
    fig_scatter.update_layout(legend_title_text="")
    st.plotly_chart(fig_scatter, width="stretch")

st.markdown("---")
st.subheader("¿Qué materias generan la mayor penalidad en cada modalidad?")
st.caption(
    "Para cada modalidad se identifican las materias que más contribuyen a la penalidad acumulada, "
    "mediante el top de materias por penalidad total y un análisis de Pareto que evidencia si un grupo "
    "reducido de materias concentra la mayor parte del retraso académico."
)

TOP_N = 10


def _penalidad_por_materia(mod):
    tot = (
        df[df["modalidad"] == mod]
        .groupby("materia")["penalidad"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    tot["porcentaje"] = tot["penalidad"] / tot["penalidad"].sum() * 100
    tot["acumulado_pct"] = tot["porcentaje"].cumsum()
    return tot


cols_bar = st.columns(len(modalidades))
for col, mod in zip(cols_bar, modalidades):
    tabla_mod = _penalidad_por_materia(mod)
    top_mod = tabla_mod.head(TOP_N).sort_values("penalidad")
    with col:
        fig_top = px.bar(
            top_mod, x="penalidad", y="materia", orientation="h",
            color_discrete_sequence=[COLOR_MAP.get(mod, None)],
            text="penalidad",
            labels={"penalidad": "Penalidad Total", "materia": "Materia"},
            title=f"Top {TOP_N} Materias con Mayor Penalidad Total en Modalidad {mod.capitalize()}",
        )
        fig_top.update_layout(height=450)
        st.plotly_chart(fig_top, width="stretch")

cols_pareto = st.columns(len(modalidades))
for col, mod in zip(cols_pareto, modalidades):
    tabla_mod = _penalidad_por_materia(mod)
    with col:
        fig_pareto = go.Figure()
        fig_pareto.add_bar(
            x=tabla_mod["materia"], y=tabla_mod["penalidad"], name="Penalidad Total",
            marker_color=COLOR_MAP.get(mod, None),
        )
        fig_pareto.add_trace(go.Scatter(
            x=tabla_mod["materia"], y=tabla_mod["acumulado_pct"], name="% Acumulado",
            yaxis="y2", mode="lines+markers", marker_color="#c62828",
        ))
        fig_pareto.add_hline(y=80, line_dash="dash", line_color="gray", yref="y2")
        fig_pareto.update_layout(
            title=f"Análisis de Pareto de la Penalidad por Materia en Modalidad {mod.capitalize()}",
            xaxis=dict(title="Materia", tickangle=-45),
            yaxis=dict(title="Penalidad Total"),
            yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=550,
        )
        st.plotly_chart(fig_pareto, width="stretch")

st.markdown("---")
st.subheader("Riesgo de Retraso Académico")
st.caption(
    "Cada estudiante se clasifica en un nivel de riesgo según su penalidad total acumulada (suma de la "
    "penalidad de todas sus materias pendientes), usando los terciles de la distribución general como "
    "puntos de corte."
)

RIESGO_ORDEN = ["Bajo riesgo", "Riesgo medio", "Riesgo alto"]
RIESGO_COLOR = {"Bajo riesgo": "#2e7d32", "Riesgo medio": "#f9a825", "Riesgo alto": "#c62828"}

t1_riesgo = resumen_est["penalidad_total"].quantile(1 / 3)
t2_riesgo = resumen_est["penalidad_total"].quantile(2 / 3)


def _clasificar_riesgo(p):
    if p <= t1_riesgo:
        return "Bajo riesgo"
    if p <= t2_riesgo:
        return "Riesgo medio"
    return "Riesgo alto"


resumen_est["riesgo"] = resumen_est["penalidad_total"].apply(_clasificar_riesgo)
st.caption(f"Puntos de corte: Bajo riesgo ≤ {t1_riesgo:.1f} · Riesgo medio ≤ {t2_riesgo:.1f} · Riesgo alto > {t2_riesgo:.1f} (penalidad total)")

cols_riesgo = st.columns(3)
for col, r in zip(cols_riesgo, RIESGO_ORDEN):
    with col:
        st.metric(r, int((resumen_est["riesgo"] == r).sum()))

col_k, col_l = st.columns(2)
with col_k:
    conteo_riesgo_mod = resumen_est.groupby(["riesgo", "modalidad"]).size().reset_index(name="estudiantes")
    fig_riesgo_bar = px.bar(
        conteo_riesgo_mod, x="riesgo", y="estudiantes", color="modalidad", barmode="group",
        category_orders={"riesgo": RIESGO_ORDEN}, color_discrete_map=COLOR_MAP, text="estudiantes",
        labels={"riesgo": "Nivel de Riesgo", "estudiantes": "Estudiantes", "modalidad": "Modalidad"},
        title="Número de Estudiantes por Nivel de Riesgo Académico según Modalidad",
    )
    fig_riesgo_bar.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
    st.plotly_chart(fig_riesgo_bar, width="stretch")
with col_l:
    fig_riesgo_pie = px.pie(
        resumen_est, names="riesgo", color="riesgo", color_discrete_map=RIESGO_COLOR,
        category_orders={"riesgo": RIESGO_ORDEN},
        title="Distribución General de Estudiantes según Nivel de Riesgo Académico",
    )
    fig_riesgo_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_riesgo_pie, width="stretch")

st.caption("Detalle de Estudiantes por Nivel de Riesgo Académico")
tabla_riesgo = resumen_est[["matricula", "nombre", "modalidad", "materias_pendientes", "penalidad_total", "riesgo"]].copy()
tabla_riesgo.columns = ["Matrícula", "Nombre", "Modalidad", "Materias Pendientes", "Penalidad Total", "Riesgo"]
tabla_riesgo["Modalidad"] = tabla_riesgo["Modalidad"].str.capitalize()
tabla_riesgo["Riesgo"] = pd.Categorical(tabla_riesgo["Riesgo"], categories=RIESGO_ORDEN, ordered=True)
st.dataframe(
    tabla_riesgo.sort_values(["Riesgo", "Penalidad Total"], ascending=[False, False]),
    width="stretch", hide_index=True,
)

st.markdown("---")
st.subheader("Perfil de Materias Pendientes")

# --- Tabla de contingencia: materia x modalidad ---
st.caption("Tabla de Contingencia: Número de Estudiantes con cada Materia Pendiente según Modalidad")
contingencia = df.groupby(["materia", "modalidad"])["matricula"].nunique().unstack(fill_value=0)
contingencia = contingencia.reindex(columns=modalidades, fill_value=0)
contingencia["Total"] = contingencia.sum(axis=1)
contingencia = contingencia.sort_values("Total", ascending=False)

tabla_contingencia = contingencia.reset_index()
tabla_contingencia.columns = ["Materia"] + [m.capitalize() for m in modalidades] + ["Total"]
st.dataframe(tabla_contingencia, width="stretch", hide_index=True)

fig_heat_cont = px.imshow(
    contingencia[modalidades].rename(columns=lambda m: m.capitalize()),
    text_auto=True, color_continuous_scale="Blues", aspect="auto",
    labels=dict(x="Modalidad", y="Materia", color="Estudiantes"),
    title="Mapa de Calor: Estudiantes con Materia Pendiente según Modalidad",
)
fig_heat_cont.update_layout(height=600)
st.plotly_chart(fig_heat_cont, width="stretch")

# --- Clustering de perfiles de retraso ---
st.markdown("#### Clustering de Perfiles de Retraso Académico")
st.caption(
    "Se agrupa a los estudiantes con K-Means según el patrón de materias que tienen pendientes "
    "(presencia/ausencia de cada materia), para identificar perfiles característicos de retraso académico."
)

pivot_bin = df.pivot_table(
    index=["matricula", "nombre", "modalidad"], columns="materia", values="penalidad",
    aggfunc="size", fill_value=0,
)
pivot_bin = (pivot_bin > 0).astype(int)
materias_cols = pivot_bin.columns.tolist()

N_CLUSTERS = 3
km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
etiquetas_cluster = km.fit_predict(pivot_bin.values)

perfil_est = pivot_bin.reset_index()
perfil_est["cluster"] = etiquetas_cluster
perfil_est["total_pendientes"] = pivot_bin.sum(axis=1).values

PERFIL_ORDEN = ["Perfil Leve", "Perfil Moderado", "Perfil Crítico"][:N_CLUSTERS]
PERFIL_COLOR = {"Perfil Leve": "#2e7d32", "Perfil Moderado": "#f9a825", "Perfil Crítico": "#c62828"}
orden_por_promedio = perfil_est.groupby("cluster")["total_pendientes"].mean().sort_values().index.tolist()
mapa_perfil = {c: PERFIL_ORDEN[i] for i, c in enumerate(orden_por_promedio)}
perfil_est["perfil"] = perfil_est["cluster"].map(mapa_perfil)

cols_perfil = st.columns(N_CLUSTERS)
for col, p in zip(cols_perfil, PERFIL_ORDEN):
    with col:
        st.metric(p, int((perfil_est["perfil"] == p).sum()))

col_m, col_n = st.columns(2)
with col_m:
    comp_mod = perfil_est.groupby(["perfil", "modalidad"]).size().reset_index(name="estudiantes")
    fig_comp = px.bar(
        comp_mod, x="perfil", y="estudiantes", color="modalidad", barmode="group",
        category_orders={"perfil": PERFIL_ORDEN}, color_discrete_map=COLOR_MAP, text="estudiantes",
        labels={"perfil": "Perfil de Retraso", "estudiantes": "Estudiantes", "modalidad": "Modalidad"},
        title="Composición de los Perfiles de Retraso Académico según Modalidad",
    )
    fig_comp.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
    st.plotly_chart(fig_comp, width="stretch")
with col_n:
    fig_box_perfil = px.box(
        perfil_est, x="perfil", y="total_pendientes", color="perfil",
        category_orders={"perfil": PERFIL_ORDEN}, color_discrete_map=PERFIL_COLOR, points="all",
        labels={"perfil": "Perfil de Retraso", "total_pendientes": "Materias Pendientes"},
        title="Materias Pendientes por Estudiante según Perfil de Retraso",
    )
    fig_box_perfil.update_layout(showlegend=False)
    st.plotly_chart(fig_box_perfil, width="stretch")

centroides = perfil_est.groupby("perfil")[materias_cols].mean() * 100
centroides = centroides.reindex(PERFIL_ORDEN)
orden_materias = centroides.mean(axis=0).sort_values(ascending=False).index.tolist()
centroides = centroides[orden_materias]

fig_heat_cluster = px.imshow(
    centroides, text_auto=".0f", color_continuous_scale="Reds", aspect="auto",
    labels=dict(x="Materia", y="Perfil de Retraso", color="% Estudiantes<br>con Pendiente"),
    title="Mapa de Calor: Patrón de Materias Pendientes por Perfil de Retraso Académico",
)
fig_heat_cluster.update_xaxes(tickangle=-45)
fig_heat_cluster.update_layout(height=450)
st.plotly_chart(fig_heat_cluster, width="stretch")

insights = []
for p in PERFIL_ORDEN:
    sub_p = perfil_est[perfil_est["perfil"] == p]
    top3 = centroides.loc[p].sort_values(ascending=False).head(3)
    materias_top = ", ".join([f"{m} ({v:.0f}%)" for m, v in top3.items()])
    insights.append(
        f"- **{p}** ({len(sub_p)} estudiantes, {sub_p['total_pendientes'].mean():.1f} materias pendientes en "
        f"promedio): predominan {materias_top}."
    )
st.markdown("\n".join(insights))
