# marimo: requirements=["pandas", "duckdb", "scipy", "plotly", "pyarrow"]

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium", css_file="custom.css")


@app.cell
async def _():
    import sys

    # Se estivermos rodando no navegador (WASM/GitHub Pages), forçamos o download
    if "pyodide" in sys.modules:
        import importlib
        _micropip = importlib.import_module("micropip")
        await _micropip.install(["plotly", "scipy", "pyarrow"])

    # Variável de controle para o Marimo saber a ordem correta de execução
    plotly_instalado = True
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import duckdb
    import plotly.express as px
    import json
    import os
    from metodologia_html import METODOLOGIA_HTML
    import numpy as np
    from scipy.stats import gaussian_kde
    import plotly.graph_objects as go

    # Carregar dados
    df_full = duckdb.query("SELECT * FROM 'Municipios_Rpc_previstos_Reais.parquet'").df()
    uf_map = {11:'RO',12:'AC',13:'AM',14:'RR',15:'PA',16:'AP',17:'TO',
              21:'MA',22:'PI',23:'CE',24:'RN',25:'PB',26:'PE',27:'AL',
              28:'SE',29:'BA',31:'MG',32:'ES',33:'RJ',35:'SP',
              41:'PR',42:'SC',43:'RS',50:'MS',51:'MT',52:'GO',53:'DF'}
    df_full['sigla_uf'] = df_full['uf'].map(uf_map)
    if 'Região' not in df_full.columns:
        for _c in df_full.columns:
            if 'Regi' in _c:
                df_full = df_full.rename(columns={_c: 'Região'})
                break
    df_full['cod_ibge_str'] = df_full['codigo_ibge'].astype(str).str.zfill(7)

    # DuckDB
    con = duckdb.connect()
    con.register('dados', df_full)

    lista_anos = sorted(df_full['Ano'].unique())
    lista_regioes = sorted(df_full['Região'].unique())
    lista_ufs = sorted(df_full['sigla_uf'].unique())
    lista_qualidades = sorted(df_full['qualidade_estimativa'].unique())
    map_regiao_uf = df_full.groupby('Região')['sigla_uf'].unique().apply(list).to_dict()
    return (
        METODOLOGIA_HTML,
        con,
        df_full,
        gaussian_kde,
        go,
        json,
        lista_anos,
        lista_regioes,
        lista_ufs,
        map_regiao_uf,
        mo,
        np,
        pd,
        px,
    )


@app.cell
def _(mo):
    header = mo.Html("""
    <div class="gov-header">
        <div class="gov-title">
            <div>
                <h1>📊 Painel de Rendimento Per Capita Municipal</h1>
                <p>Estimativas 2012–2024 | Modelo Híbrido SAE + Machine Learning</p>
            </div>
        </div>
    </div>
    """)
    return (header,)


@app.cell
def _(lista_anos, lista_regioes, mo):
    filtro_ano = mo.ui.slider(
        start=min(lista_anos), stop=max(lista_anos), step=1,
        value=max(lista_anos), label="**Ano**", full_width=False, show_value=True)

    filtro_regiao = mo.ui.dropdown(
        options={"Todas": "Todas", **{r: r for r in lista_regioes}},
        value="Todas", label="**Região**"
    )
    return filtro_ano, filtro_regiao


@app.cell
def _(filtro_regiao, lista_ufs, map_regiao_uf, mo):
    # Lógica de filtro hierárquico para UF
    _ufs_disponiveis = lista_ufs
    if filtro_regiao.value != "Todas":
        _ufs_disponiveis = sorted(map_regiao_uf.get(filtro_regiao.value, []))

    filtro_uf = mo.ui.dropdown(
        options={"Todas": "Todas", **{u: u for u in _ufs_disponiveis}},
        value="Todas", label="**UF**"
    )
    return (filtro_uf,)


@app.cell
def _(con, filtro_ano, filtro_regiao, filtro_uf):
    where_parts = ["Ano = ?"]
    params_list = [filtro_ano.value]
    if filtro_regiao.value != "Todas":
        where_parts.append('"Região" = ?')
        params_list.append(filtro_regiao.value)
    if filtro_uf.value != "Todas":
        where_parts.append("sigla_uf = ?")
        params_list.append(filtro_uf.value)
    sql_query = f"SELECT * FROM dados WHERE {' AND '.join(where_parts)} ORDER BY Rpc_Reais2024 DESC"
    df_filtered = con.execute(sql_query, params_list).df()
    return (df_filtered,)


@app.cell
def _(df_filtered, mo):
    n_mun = len(df_filtered)
    media_rpc = df_filtered['Rpc_Reais2024'].mean() if n_mun > 0 else 0
    mediana_cv = (df_filtered['CV_rpc'].median() * 100) if n_mun > 0 else 0
    pop_total = df_filtered['Populacao'].sum() if n_mun > 0 else 0

    def kpi(title, value, sub=""):
        return f'<div class="kpi-card"><h3>{title}</h3><div class="value">{value}</div><div class="sub">{sub}</div></div>'

    kpi_html = mo.Html(f"""<div class="kpi-row">
        {kpi("Municípios", f"{n_mun:,}".replace(",","."), "no filtro selecionado")}
        {kpi("RPC Média", f"R$ {media_rpc:,.0f}".replace(",","."), "Reais de 2024")}
        {kpi("Mediana CV", f"{mediana_cv:.1f}%", "coeficiente de variação")}
        {kpi("Pop. Total", f"{pop_total:,.0f}".replace(",","."), "habitantes")}
    </div>""")
    return (kpi_html,)


@app.cell
def _(df_filtered, json, mo, px):
    # Carregar e processar o GeoJSON removendo o último dígito do codarea
    geojson_path = "./assets/municipios_br_simpl.geojson"

    # Carregar GeoJSON
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    # Função para normalizar códigos para 6 dígitos
    def normalize_6_digits(val):
        s = str(int(float(val)))
        return s[:6] if len(s) == 7 else s

    # Processar GeoJSON: Garantir que cada feature tenha um 'id' de 6 dígitos
    for feature in geojson_data['features']:
        if 'codarea' in feature['properties']:
            cod_6 = normalize_6_digits(feature['properties']['codarea'])
            feature['id'] = cod_6
            feature['properties']['codarea'] = cod_6

    # Preparar dados: Garantir que a coluna 'id' tenha os mesmos 6 dígitos
    map_data = df_filtered[['codigo_ibge', 'Rpc_Reais2024', 'municipio', 'sigla_uf']].copy()
    map_data['id'] = map_data['codigo_ibge'].apply(normalize_6_digits)

    if map_data.empty:
        fig_map = mo.md("Sem dados para exibir no mapa.")
    else:
        # Criar mapa com Plotly
        fig = px.choropleth_mapbox(
            map_data,
            geojson=geojson_data,
            locations='id',
            # Ao omitir featureidkey, o Plotly usa o campo 'id' que definimos no loop acima
            color='Rpc_Reais2024',
            color_continuous_scale='Teal',
            range_color=(map_data['Rpc_Reais2024'].min(), map_data['Rpc_Reais2024'].max()),
            mapbox_style='carto-positron',
            zoom=3.5,
            center={"lat": -14.235, "lon": -51.925},
            opacity=0.8,
            labels={'Rpc_Reais2024': 'RPC (R$ 2024)'},
            hover_name='municipio',
            hover_data={'Rpc_Reais2024': ':,.2f', 'sigla_uf': True, 'id': True}
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=600,
            dragmode=False
        )

        fig_map = mo.ui.plotly(fig)
    return (fig_map,)


@app.cell
def _(
    con,
    df_filtered,
    filtro_ano,
    filtro_regiao,
    filtro_uf,
    gaussian_kde,
    go,
    mo,
    np,
    pd,
    px,
):

    # Gráfico de Rank (Top 10 / Bot 10)
    top10 = df_filtered.nlargest(10, 'Rpc_Reais2024')
    bot10 = df_filtered.nsmallest(10, 'Rpc_Reais2024')
    rank_df = pd.concat([top10, bot10]).sort_values('Rpc_Reais2024', ascending=True)

    fig_rank = px.bar(
        rank_df, y='municipio', x='Rpc_Reais2024', orientation='h',
        color_discrete_sequence=['#1351B4'],
        labels={'Rpc_Reais2024': 'RPC (R$ 2024)', 'municipio': ''},
        title='Top 10 e Bottom 10 Municípios por RPC'
    )
    fig_rank.update_layout(height=450, margin=dict(l=0, r=20, t=40, b=0), showlegend=False)

    # Função auxiliar para gerar curvas KDE com preenchimento (estilo Seaborn)
    def create_kde_plotly(df, x_col, hue_col=None, title=""):
        fig = go.Figure()
        colors = px.colors.qualitative.Plotly

        if hue_col and hue_col in df.columns:
            categories = sorted(df[hue_col].unique())
            for i, cat in enumerate(categories):
                subset = df[df[hue_col] == cat][x_col].dropna()
                if len(subset) < 3: continue

                kde = gaussian_kde(subset)
                x_range = np.linspace(df[x_col].min(), df[x_col].max(), 200)
                y_vals = kde(x_range)

                fig.add_trace(go.Scatter(
                    x=x_range, y=y_vals, mode='lines',
                    line=dict(width=2, color=colors[i % len(colors)]),
                    fill='tozeroy', name=str(cat), opacity=0.4
                ))
        else:
            data = df[x_col].dropna()
            if len(data) > 2:
                kde = gaussian_kde(data)
                x_range = np.linspace(data.min(), data.max(), 200)
                y_vals = kde(x_range)
                fig.add_trace(go.Scatter(
                    x=x_range, y=y_vals, mode='lines',
                    line=dict(width=3, color='#1351B4'),
                    fill='tozeroy', name='Geral', opacity=0.5
                ))

        fig.update_layout(
            title=title, xaxis_title='RPC (R$ 2024)', yaxis_title='Densidade',
            height=450, margin=dict(l=0, r=20, t=40, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template='plotly_white'
        )
        return fig

    # NOVO: Gráfico de Densidade Geral (KDE)
    fig_dist_total = create_kde_plotly(df_filtered, 'Rpc_Reais2024', title='Densidade Geral da RPC dos Municípios(R$ 2024)')

    # NOVO: Gráfico de Densidade com Hue (Região ou UF)
    _hue_col = 'Região' if filtro_regiao.value == "Todas" else 'sigla_uf'
    fig_dist_hue = create_kde_plotly(df_filtered, 'Rpc_Reais2024', hue_col=_hue_col, title=f'Densidade da RPC dos Municípios por {_hue_col}')

    # Gráfico de Trajetória Temporal Responsivo
    _where_ts = []
    _params_ts = []
    if filtro_regiao.value != "Todas":
        _where_ts.append('"Região" = ?')
        _params_ts.append(filtro_regiao.value)
    if filtro_uf.value != "Todas":
        _where_ts.append("sigla_uf = ?")
        _params_ts.append(filtro_uf.value)

    _where_clause = f"WHERE {' AND '.join(_where_ts)}" if _where_ts else ""

    # Determina o que mostrar na legenda (Região ou UF)
    _group_col = 'sigla_uf' if (filtro_regiao.value != "Todas" or filtro_uf.value != "Todas") else 'Região'

    _ts_query = f"""
        SELECT Ano, {_group_col}, AVG(Rpc_Reais2024) as media_rpc 
        FROM dados {_where_clause} 
        GROUP BY Ano, {_group_col} 
        ORDER BY Ano
    """
    ts_df = con.execute(_ts_query, _params_ts).df()

    fig_ts = px.line(
        ts_df, x='Ano', y='media_rpc', color=_group_col,
        labels={'media_rpc': 'RPC Média (R$ 2024)', 'Ano': 'Ano', _group_col: _group_col},
        title=f'Trajetória Temporal da Renda Média dos Municípios por {_group_col}'
    )
    fig_ts.add_vline(x=filtro_ano.value, line_dash="dash", line_color="gray", 
                     annotation_text=f"Ano: {filtro_ano.value}", annotation_position="top left")
    fig_ts.update_layout(height=450, margin=dict(l=0, r=20, t=40, b=0))
    mo.output.replace(None)
    return fig_dist_hue, fig_dist_total, fig_rank, fig_ts


@app.cell
def _(df_filtered, mo):
    cols = ['Ano', 'codigo_ibge', 'municipio', 'sigla_uf', 'Região',
            'Populacao', 'Rpc_predita', 'Rpc_Reais2024', 'CV_rpc', 'qualidade_estimativa',
            'part_pes_cadunico', 'part_pes_IRPF', 'IRPF_pc',
            'Ren_Formal_pc', 'Prev_pc', 'Bolsa_Familia_pc', 'Ben_Assist_pc']
    existing_cols = [_c for _c in cols if _c in df_filtered.columns]
    tdf = df_filtered[existing_cols].copy().sort_values('Rpc_Reais2024', ascending=False)

    # Formatação de colunas
    tdf['codigo_ibge'] = tdf['codigo_ibge'].astype(str)
    tdf['CV_rpc'] = (tdf['CV_rpc'] * 100).round(2)
    tdf['Rpc_Reais2024'] = tdf['Rpc_Reais2024'].round(2)
    tdf['Populacao'] = tdf['Populacao'].round(0).astype(int)

    # Arredondar variáveis econômicas e sociais para 2 casas decimais
    float_cols = ['part_pes_cadunico', 'part_pes_IRPF', 'IRPF_pc', 'Ren_Formal_pc', 
                  'Prev_pc', 'Bolsa_Familia_pc', 'Ben_Assist_pc', 'Rpc_predita']
    for _c in float_cols:
        if _c in tdf.columns:
            tdf[_c] = tdf[_c].round(2)

    tdf = tdf.rename(columns={
        'codigo_ibge': 'Cód. IBGE', 'municipio': 'Município', 'sigla_uf': 'UF',
        'Populacao': 'Pop.', 'Rpc_Reais2024': 'RPC (R$2024)', 'Rpc_predita': 'RPC Predita',
        'CV_rpc': 'CV(%)', 'qualidade_estimativa': 'Qualidade',
        'part_pes_cadunico': '%CadÚnico', 'part_pes_IRPF': '%IRPF',
        'IRPF_pc': 'IRPF pc', 'Ren_Formal_pc': 'Renda Formal pc',
        'Prev_pc': 'Prev pc', 'Bolsa_Familia_pc': 'BF pc', 'Ben_Assist_pc': 'BPC pc'
    })
    data_table = mo.ui.table(tdf, selection=None, page_size=20, label="")
    mo.output.replace(None)
    return (data_table,)


@app.cell
def _(df_full, mo):
    # Usamos uma função lambda para que o processamento só ocorra no clique.
    # Isso é muito mais estável para bases de dados maiores.
    download_csv = mo.download(
        data=lambda: df_full.to_csv(index=False).encode('utf-8-sig'),
        filename="rpc_municipal_completo.csv",
        label="⬇️ Baixar Tabela Completa (CSV)"
    )
    mo.output.replace(None)
    return (download_csv,)


@app.cell
def _(METODOLOGIA_HTML, mo):
    # Usamos mo.image para garantir que marimo gerencie o caminho da imagem corretamente,
    # inclusive embutindo-a se o dashboard for exportado para WASM.
    fluxograma = mo.image(
        src="assets/fluxograma.png",
        alt="Fluxograma da Metodologia",
        style={"max-width": "100%", "height": "auto", "border": "1px solid #eee"}
    )

    # Substituímos o placeholder na string HTML pelo componente de imagem do marimo
    html_com_imagem = METODOLOGIA_HTML.replace("{{FLUXOGRAMA_IMG}}", fluxograma._repr_html_())

    metodologia_content = mo.Html(html_com_imagem + """
    <div class="metodo-section" style="text-align:center; margin-top:20px;">
        <h3>📄 Artigo Completo</h3>
        <p>O relatório de pesquisa detalhado estará disponível para download em breve.</p>
        <button class="download-btn" disabled style="opacity:0.5; cursor:not-allowed;">
            ⬇️ Download do Artigo (PDF) — Em breve
        </button>
    </div>
    """)
    mo.output.replace(None)
    return (metodologia_content,)


@app.cell
def _(
    data_table,
    download_csv,
    fig_dist_hue,
    fig_dist_total,
    fig_map,
    fig_rank,
    fig_ts,
    filtro_ano,
    filtro_regiao,
    filtro_uf,
    header,
    kpi_html,
    metodologia_content,
    mo,
):
    # Top bar fixa (Header + Filtros)
    sticky_top = mo.vstack([
            header,
            mo.hstack([filtro_ano, filtro_regiao, filtro_uf], widths=[2, 1, 1], gap=1).style({"padding": "10px 0"})
    ]).style({
            "position": "sticky",
            "top": "0",
            "z-index": "1000",
            "background": "white",
            "padding": "10px 20px",
            "box-shadow": "0 2px 10px rgba(0,0,0,0.1)",
            "width": "100%",
            "margin": "0"
    })

    visao_tab = mo.vstack([
            mo.Html('<div class="section-title">Indicadores Resumo</div>'),
            kpi_html,
            mo.Html('<div class="section-title">Mapa Coroplético</div>'),
            fig_map,
            mo.Html('<div class="section-title">Análise Comparativa</div>'),
            mo.vstack([fig_rank, fig_dist_total]),
            mo.vstack([fig_dist_hue, fig_ts])
    ])

    explorador_tab = mo.vstack([
            mo.Html('<div class="section-title">Tabela Analítica</div>'),
            mo.Html('<p style="color:#666;font-size:13px;">Ordenado por RPC (decrescente).</p>'),
            data_table,
            mo.Html('<div class="section-title">Baixar os dados brutos com todos os anos da série histórica</div>'),
            mo.hstack([download_csv], justify="start")
    ])

    tab_content = {
            "📊 Visao Geral": visao_tab,
            "🕵️ Explorador de Dados": explorador_tab,
            "📄 Metodologia": metodologia_content
    }

    layout = mo.vstack([
            sticky_top,
            mo.ui.tabs(tab_content)
    ])
    return (layout,)


@app.cell
def _(layout):
    layout
    return


if __name__ == "__main__":
    app.run()
