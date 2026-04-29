METODOLOGIA_HTML = """
<div class="metodo-section">
<h2>Modelo Híbrido: Estimação para Pequenas Áreas + Aprendizado de Máquina</h2>
<p>As estimativas de rendimento per capita municipal foram geradas por um <strong>modelo híbrido</strong> que integra técnicas de <em>Estimação para Pequenas Áreas (SAE – Small Area Estimation)</em> com algoritmos de <em>Aprendizado de Máquina</em> (ensembles e boosting). Essa combinação permite:</p>
<ul>
<li>Contornar a <strong>restrição amostral da PNAD Contínua</strong>, que não possui representatividade municipal;</li>
<li>Capturar <strong>não linearidades</strong> nos dados que modelos lineares tradicionais não conseguem modelar;</li>
<li>Incorporar a <strong>capilaridade dos registros administrativos federais</strong> como variáveis auxiliares.</li>
</ul>

<h3>Visão Geral do Processo</h3>
<div style="text-align: center; margin: 20px 0; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    {{FLUXOGRAMA_IMG}}
    <p style="font-size: 12px; color: #666; margin-top: 10px;">Fluxograma da metodologia aplicada para a estimativa do rendimento per capita municipal.</p>
</div>
<p>No desenho metodológico adotado, a estimação do rendimento per capita dos municípios foi realizada por meio de um preditor sintético baseado em algoritmo de Machine Learning (ML), treinado exclusivamente no nível dos estratos de municípiosda PNAD Contínua.</p>
<p>A etapa subsequente de benchmarking fez com que a média ponderada das estimativas municipais correspondesse exatamente à estimativa direta do estrato em questão. Assim, o papel do preditor sintético transcende a simples geração de valores preliminares: ele atuou como um mecanismo de alocação interna da informação, definindo o perfil relativo dos municípios dentro de cada área.</p>
<h3>Fontes de Dados e Variáveis Auxiliares</h3>
<p>O modelo sintético foi calibrado utilizando a combinação de dados amostrais e registros administrativos:</p>
<table>
<tr><th>Fonte</th><th>Variáveis</th><th>Contribuição</th></tr>
<tr><td>PNAD Contínua (IBGE)</td><td>Rendimento domiciliar per capita</td><td>Variável resposta (benchmark)</td></tr>
<tr><td>Cadastro Único (MDS)</td><td>part_pes_cadunico, part_fam_cadunico</td><td>Proxy de vulnerabilidade social</td></tr>
<tr><td>DIRPF (Receita Federal)</td><td>part_pes_IRPF, IRPF_pc</td><td>Proxy de renda alta e massa salarial formal</td></tr>
<tr><td>RAIS (MTE)</td><td>Ren_Formal_pc, part_emp_formal</td><td>Renda do trabalho formal</td></tr>
<tr><td>Previdência Social</td><td>Prev_pc, part_aposentados</td><td>Transferências previdenciárias</td></tr>
<tr><td>Bolsa Família / Auxílio Brasil</td><td>Bolsa_Familia_pc</td><td>Transferências de renda</td></tr>
<tr><td>BPC/LOAS</td><td>Ben_Assist_pc</td><td>Benefícios assistenciais</td></tr>
</table>

<h3>Qualidade das Estimativas</h3>
<p>A confiabilidade de cada estimativa municipal é avaliada pelo <strong> Coeficiente de Variação (CV)</strong>:</p>
<table>
<tr><th>Faixa</th><th>CV (%)</th><th>Interpretação</th></tr>
<tr><td><span class="badge badge-otima">Ótima precisão</span></td><td>≤ 5%</td><td>Alta confiabilidade</td></tr>
<tr><td><span class="badge badge-boa">Boa</span></td><td>5% – 15%</td><td>Confiável para análises</td></tr>
<tr><td><span class="badge badge-razoavel">Razoável</span></td><td>15% – 25%</td><td>Usar com cautela</td></tr>
<tr><td><span class="badge badge-pouco">Pouco precisa</span></td><td>&gt; 25%</td><td>Indicativo, não conclusivo</td></tr>
</table>

<h3>Valores em Reais de 2024</h3>
<p>Todas as estimativas são disponibilizadas tanto em valores correntes (<code>Rpc</code>) quanto deflacionadas para <strong>Reais de 2024</strong> (<code>Rpc_Reais2024</code>).</p>

<h3>Referência</h3>
<p>GIACOMIN, R. <em>Estimação do Rendimento Per Capita Municipal no Brasil (2012–2024): Uma Abordagem Híbrida com SAE e Machine Learning</em>. Artigo submetido para publicação.</p>
</div>
"""
