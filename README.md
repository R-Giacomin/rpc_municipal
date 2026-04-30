# Painel para visualização, análise e acesso às estimativas de **Rendimento Per Capita dos Municípios do Brasil**

Os dados foram estimados por meio de um preditor sintético baseado em algoritmos de *Machine Learning* (ML), treinado no nível dos estratos de municípios da PNAD Contínua para capturar padrões complexos em registros administrativos, e aplica uma calibração espacial rigorosa para ancorar as predições municipais às estimativas diretas da PNAD Contínua.

# 🏗 Estimador Sintético de Aprendizado de Máquina com Calibração Espacial

### **Produção de Estimativas Municipais (A Abordagem Top-Down)**

#### **Passo 1: Predição Sintética (ML)**

#### **Passo 2: Benchmarking Espacial por Estrato**
Ancora hierarquicamente as predições sintéticas para que a média ponderada do estrato coincida exatamente com a **estimativa direta** da PNAD Contínua:

#### **Passo 3: Cálculo de Incerteza (Erro Quadrático Médio - MSE)**
A variância total de um município (não autorrepresentativo) é a soma de 2 componentes:
1. **Incerteza Herdada da PNAD**: A variância direta do IBGE para o estrato desce para o município proporcionalmente ao quadrado da relação (peso relativo) entre a renda do município e a renda do estrato.
2. **Incerteza Sintética do ML**: O erro empírico do modelo (*Out-of-Fold*), originalmente no espaço logarítmico, é projetado para a escala de Reais de forma individualizada para cada município utilizando o **Método Delta**.

#### **Passo 4: Regra de Exceção (Áreas Autorrepresentativas)**
- Municípios que compreendem integralmente um estrato (ex: Capitais) sofrem um *bypass* do modelo.
- **Predição final:** Recebem exatamente a estimativa direta da PNAD.
- **Incerteza:** O MSE é exatamente a variância oficial da PNAD, garantindo que áreas com amostra plena não sejam penalizadas por incertezas de modelos sintéticos.

#### **Passo 5: Coeficiente de Variação (CV)**
- Avaliação final da qualidade: `CV = sqrt(MSE_rpc) / y_bench`.

### **Inovações Implementadas:**
1. **Estimador Sintético Calibrado**: Substitui a modelagem mista clássica após diagnóstico empírico, adotando uma arquitetura *Top-Down* ancorada nos agregados oficiais.
2. **Decomposição Híbrida de Incerteza**: Formulação matemática rigorosa que soma a imprecisão do desenho amostral (herdada) com o erro do algoritmo de *Machine Learning* (Método Delta).
3. **Imunidade à Extrapolação**: O uso de algoritmos baseados em árvores previne predições espúrias (comuns em regressões lineares) nos limites extremos de riqueza e pobreza.
4. **Preservação de Áreas Autorrepresentativas**: Respeito integral às diretrizes de amostragem clássica (*design-based*).

### **Vantagens:**
- **Credibilidade Institucional**: O *benchmarking* nas estimativas diretas garante que os dados finais não entrem em conflito com os totais divulgados pelo IBGE.
- **Estabilização de Variância**: Elimina a explosão de erros em pequenas áreas e cimenta tetos e pisos lógicos para a distribuição de renda.

## **Fluxo de Dados**
```text
Dados PNAD (Estratos) → Treino Modelos ML → Seleção do Melhor Algoritmo
         ↓
Dados Municipais (Reg. Admin.) → Predição Sintética Pura (ML)
         ↓
Benchmarking Espacial (Calibração pela PNAD Direta) → Estimativa Pontual Final
         ↓
Propagação de Variância (Herdada + Delta) & Regra de Bypass (Capitais)
         ↓
Cálculo do Erro Quadrático Médio (MSE) e Coeficiente de Variação (CV)
```

## **Saídas Produzidas**
Para cada município brasileiro na série histórica:
- `Rpc_pred_benchmarked`: Renda per capita municipal final calibrada em Reais.
- `CV_rpc`: Coeficiente de Variação (Métrica definidora da qualidade e confiabilidade do dado).

## **Aplicações Práticas**
Este sistema permite:
- **Democratização de Dados**: Geração de estimativas municipais em anos intercensitários com precisão auditável.
- **Focalização de Políticas Públicas**: Identificação precisa de bolsões de pobreza intraestaduais.
- **Rateio Justo de Recursos**: Distribuição de fundos governamentais baseada em estratificação de renda (quintis) geograficamente consistente.

## **Limitações e Pressupostos**
1. **Premissa Sintética**: Assume-se que o modelo de *Machine Learning* treinado no nível agregado (estrato) captura as verdadeiras relações estruturais que regem as diferenças de renda no nível desagregado (município).
2. **Qualidade dos Registros Administrativos**: A acurácia da distribuição interna da renda no estrato é estritamente dependente da completude, tempestividade e qualidade dos dados administrativos utilizados como covariáveis (CadÚnico, RAIS, etc.).
3. **Dependência da Âncora**: Qualquer viés não amostral presente nas estimativas diretas da PNAD Contínua será, por definição do *benchmarking*, propagado para as estimativas municipais.

*(Obs: Os modelos são estimados e calibrados de forma independente para cada ano da análise, visando capturar a estabilidade e as mudanças estruturais temporais da economia brasileira).*

Painel para visualização, análise e acesso aos dados disponível em: [Painel de Rendimento Per Capita Municipal](https://r-giacomin.github.io/rpc_municipal/)
