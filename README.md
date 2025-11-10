# 📊 Sistema de Análise de Estatística Descritiva

Sistema automatizado para análise estatística descritiva completa com classificação inteligente de variáveis, cálculos estatísticos e geração automática de visualizações e relatórios.

## 🎯 O que este projeto faz?

Este sistema analisa automaticamente qualquer conjunto de dados (CSV ou XLSX) e:

1. **Classifica automaticamente** cada variável em um dos 5 tipos:
   - **Nominal**: Categorias sem ordem (ex: nomes, cores, cidades)
   - **Ordinal**: Categorias com ordem (ex: escolaridade, classificação)
   - **Binária**: Apenas dois valores distintos (ex: sim/não, aprovado/reprovado)
   - **Discreta**: Números inteiros contáveis (ex: número de filhos, idade)
   - **Contínua**: Números reais com medições (ex: altura, peso, temperatura)

2. **Calcula automaticamente** todas as medidas estatísticas apropriadas:
   - Análise de frequência (absoluta, relativa, acumulada)
   - Medidas de tendência central (média, mediana, moda)
   - Separatrizes (quartis, decis, percentis)
   - Medidas de dispersão (amplitude, variância, desvio padrão, IQR, CV)

3. **Gera automaticamente** visualizações profissionais:
   - Gráficos de barras para variáveis nominais
   - Gráficos de pizza para variáveis binárias
   - Histogramas e boxplots para variáveis numéricas
   - Curvas de densidade KDE para variáveis contínuas

4. **Exporta automaticamente** relatórios completos em Markdown com:
   - Tabelas de frequências formatadas
   - Medidas estatísticas organizadas
   - Interpretações automáticas dos resultados
   - Imagens embutidas das visualizações

## 🏗️ Arquitetura

O projeto segue princípios **SOLID** e utiliza **padrões de projeto** profissionais:

### Padrões de Projeto

- **Factory Method**: Para criação de leitores de dados (CSV, XLSX)
- **Strategy Pattern**: Cada tipo de variável implementa sua própria estratégia de análise
- **Interface Segregation**: Interfaces bem definidas (IDataReader, IVariableType)

### Estrutura de Diretórios

```
descriptive-statistics/
├── src/
│   ├── data_loading/          # Leitura de dados (Factory)
│   │   ├── factory.py         # Fábrica de leitores
│   │   ├── idata_reader.py    # Interface
│   │   └── readers/
│   │       ├── csv_reader.py  # Leitor CSV (suporta vírgula decimal)
│   │       └── xlsx_reader.py # Leitor Excel
│   ├── domain/                # Domínio do negócio
│   │   ├── dataset.py         # Conjunto de dados
│   │   ├── variable.py        # Variável individual
│   │   └── variable_types/    # Estratégias por tipo
│   │       ├── ivariable_type.py  # Interface Strategy
│   │       ├── nominal.py
│   │       ├── ordinal.py
│   │       ├── binary.py
│   │       ├── discrete.py
│   │       └── continuous.py
│   ├── analysis/              # Funções estatísticas
│   │   ├── statistical_functions.py
│   │   └── heuristics.py      # Inferência automática de tipo
│   ├── visualization/         # Geração de gráficos
│   │   └── chart_generator.py
│   ├── export/                # Exportação de relatórios
│   │   └── report_generator.py
│   └── main.py                # Ponto de entrada
├── data/                      # Seus arquivos de dados
├── output/                    # Resultados gerados
│   └── <nome_arquivo>/
│       ├── *_histograma.png
│       ├── *_boxplot.png
│       ├── *_relatorio.md
│       └── RELATORIO_GERAL.md
├── pyproject.toml            # Configuração Poetry
└── README.md                 # Este arquivo
```

## 📦 Instalação

### Pré-requisitos

- Python 3.12 ou superior
- Poetry (gerenciador de dependências)

### Passo 1: Instalar Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Passo 2: Clonar e instalar dependências

```bash
cd descriptive-statistics
poetry install
```

### Dependências instaladas automaticamente:

- **pandas** (2.3.3): Manipulação de dados
- **numpy** (2.3.4): Cálculos numéricos
- **matplotlib** (3.10.7): Visualizações
- **seaborn** (0.13.2): Gráficos estatísticos
- **scipy** (1.16.3): Funções estatísticas avançadas

## 🚀 Como Usar

### Uso Básico

```bash
poetry run python src/main.py data/seu_arquivo.csv
```

Ou com Excel:

```bash
poetry run python src/main.py data/seu_arquivo.xlsx
```

### O que acontece automaticamente:

1. ✅ Lê o arquivo (detecta automaticamente CSV ou XLSX)
2. ✅ Converte números com vírgula decimal (formato brasileiro)
3. ✅ Classifica cada coluna no tipo apropriado
4. ✅ Calcula todas as estatísticas relevantes
5. ✅ Gera gráficos profissionais (300 DPI)
6. ✅ Exporta relatórios em Markdown
7. ✅ Salva tudo em `output/<nome_arquivo>/`

## 📋 Exemplos

### Exemplo 1: Dados de Pessoas

**Arquivo**: `data/pessoas.csv`
```csv
nome,idade,altura,cidade,aprovado
João,25,1.75,São Paulo,sim
Maria,30,1.68,Rio de Janeiro,sim
Pedro,25,1.82,Belo Horizonte,não
```

**Comando**:
```bash
poetry run python src/main.py data/pessoas.csv
```

**Resultado**:
```
Analisando dataset: pessoas.csv
Total de variáveis: 5

Variável: nome (Nominal)
  - Total de valores: 3
  - Valores únicos: 3

Variável: idade (Discreta)
  - Média: 26.67
  - Mediana: 25.0
  - Desvio Padrão: 2.89

Variável: altura (Contínua)
  - Média: 1.75
  - Mediana: 1.75
  - Coeficiente de Variação: 4.02%

Variável: cidade (Nominal)
  - Total de valores: 3
  - Valores únicos: 3

Variável: aprovado (Binária)
  - sim: 66.67%
  - não: 33.33%

✨ Visualizações e relatórios salvos em: output/pessoas_csv/
```

**Arquivos gerados** em `output/pessoas_csv/`:
- `nome_barras.png` - Gráfico de barras
- `nome_relatorio.md` - Relatório da variável
- `idade_histograma.png` - Histograma
- `idade_boxplot.png` - Boxplot
- `idade_relatorio.md` - Relatório com todas as medidas
- `altura_histograma.png` - Histograma com curva KDE
- `altura_boxplot.png` - Boxplot
- `altura_relatorio.md` - Relatório completo
- `cidade_barras.png` - Gráfico de barras
- `cidade_relatorio.md` - Relatório
- `aprovado_pizza.png` - Gráfico de pizza
- `aprovado_barras.png` - Gráfico de barras
- `aprovado_relatorio.md` - Relatório
- `_resumo_dataset.png` - Visão geral do dataset
- `RELATORIO_GERAL.md` - Resumo completo de todas as variáveis

### Exemplo 2: Dados com Decimais Brasileiros

**Arquivo**: `data/medidas.csv`
```csv
produto,peso,altura
A,1,75,2,3
B,2,30,1,8
C,0,95,3,1
```

**Comando**:
```bash
poetry run python src/main.py data/medidas.csv
```

✅ O sistema **detecta automaticamente** que `1,75` é um número decimal e converte para `1.75`

### Exemplo 3: Excel com Múltiplas Colunas

**Arquivo**: `data/vendas.xlsx`

| Vendedor | Região | Vendas | Comissão | Meta_Atingida |
|----------|--------|--------|----------|---------------|
| João | Norte | 150 | 15,5 | Sim |
| Maria | Sul | 230 | 23,0 | Sim |
| Pedro | Leste | 120 | 12,0 | Não |

**Comando**:
```bash
poetry run python src/main.py data/vendas.xlsx
```

**Classificação automática**:
- `Vendedor` → Nominal
- `Região` → Nominal
- `Vendas` → Discreta
- `Comissão` → Contínua (converte vírgula automaticamente)
- `Meta_Atingida` → Binária

## 🧠 Recursos Inteligentes

### 1. Detecção Automática de Formato Numérico

O sistema detecta e converte automaticamente:
- `1,75` → `1.75`
- `2,30` → `2.30`
- `1.000,50` → `1000.50`

### 2. Inferência Inteligente de Tipo

O sistema analisa os dados e decide automaticamente:

| Característica | Tipo Inferido |
|----------------|---------------|
| Apenas 2 valores únicos | Binária |
| Texto sem ordem | Nominal |
| Números inteiros pequenos (<30 únicos) | Discreta |
| Números reais ou inteiros grandes | Contínua |

### 3. Análises Específicas por Tipo

Cada tipo de variável recebe análises apropriadas:

**Variáveis Nominais/Ordinais**:
- Frequências (absoluta, relativa, acumulada)
- Moda
- Gráfico de barras

**Variáveis Binárias**:
- Frequências
- Proporções
- Gráfico de pizza + barras

**Variáveis Discretas**:
- Frequências
- Média, Mediana, Moda
- Quartis
- Variância, Desvio Padrão, CV
- Histograma + Boxplot

**Variáveis Contínuas**:
- Classes (Sturges)
- Média, Mediana, Moda (de King)
- Quartis, Decis, Percentis
- Amplitude, Variância, DP, IQR, CV
- Histograma com KDE + Boxplot

## 📊 Interpretações Automáticas

O sistema gera interpretações automáticas, por exemplo:

**Para Dispersão**:
- CV < 15%: "Os dados são muito homogêneos"
- 15% ≤ CV < 30%: "Os dados têm dispersão moderada"
- CV ≥ 30%: "Os dados são muito heterogêneos"

**Para Distribuição**:
- Média ≈ Mediana: "Distribuição simétrica"
- Média > Mediana: "Assimetria positiva (cauda à direita)"
- Média < Mediana: "Assimetria negativa (cauda à esquerda)"

## 🎨 Visualizações Geradas

Todas as visualizações são geradas em **alta qualidade (300 DPI)** e incluem:

### Para Variáveis Nominais:
- Gráfico de barras horizontal
- Anotações com frequências

### Para Variáveis Binárias:
- Gráfico de pizza
- Gráfico de barras

### Para Variáveis Discretas:
- Histograma com grid
- Boxplot com outliers destacados

### Para Variáveis Contínuas:
- Histograma com curva de densidade KDE
- Boxplot com estatísticas anotadas

### Resumo Geral:
- Painel com visão geral de todas as variáveis

## 🔧 Personalização

### Adicionar novo tipo de leitor

```python
# src/data_loading/readers/json_reader.py
from data_loading.idata_reader import IDataReader
from data_loading.factory import register
import pandas as pd

@register('json')
class JSONReader(IDataReader):
    def read(self) -> pd.DataFrame:
        return pd.read_json(self.file_path)
```

### Adicionar novo tipo de variável

```python
# src/domain/variable_types/temporal.py
from domain.variable_types.ivariable_type import IVariableType

class Temporal(IVariableType):
    @property
    def name(self) -> str:
        return "Temporal"

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        # Sua análise personalizada
        pass
```

## 📚 Conceitos Estatísticos

### Tipos de Variáveis

**Qualitativas**:
- **Nominal**: Sem ordem natural (cores, nomes, categorias)
- **Ordinal**: Com ordem natural (grau de escolaridade, ranking)
- **Binária**: Apenas dois valores (sim/não, verdadeiro/falso)

**Quantitativas**:
- **Discreta**: Valores inteiros contáveis (número de filhos, carros)
- **Contínua**: Valores reais mensuráveis (altura, peso, temperatura)

### Medidas Calculadas

**Tendência Central**:
- **Média**: Soma dividida pela quantidade
- **Mediana**: Valor central quando ordenado
- **Moda**: Valor mais frequente

**Separatrizes**:
- **Quartis**: Dividem dados em 4 partes (Q1, Q2, Q3)
- **Decis**: Dividem dados em 10 partes (D1...D9)
- **Percentis**: Dividem dados em 100 partes (P1...P99)

**Dispersão**:
- **Amplitude**: Máximo - Mínimo
- **Variância**: Média dos quadrados dos desvios
- **Desvio Padrão**: Raiz quadrada da variância
- **IQR**: Amplitude interquartílica (Q3 - Q1)
- **CV**: Coeficiente de variação (DP/Média × 100%)

## 🧪 Testado Com

- ✅ Datasets com 1 coluna
- ✅ Datasets com múltiplas colunas (6+)
- ✅ Números com vírgula decimal (formato brasileiro)
- ✅ Números com ponto decimal (formato internacional)
- ✅ Arquivos CSV com diferentes delimitadores (`,` `;` `\t`)
- ✅ Arquivos Excel (.xlsx)
- ✅ Dados mistos (texto + números)
- ✅ Valores faltantes (NaN)

## 🐛 Tratamento de Erros

O sistema trata automaticamente:
- Arquivos não encontrados
- Formatos não suportados
- Dados ausentes/nulos
- Colunas vazias
- Tipos incompatíveis

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais.

## 👥 Contribuindo

Sugestões e melhorias são bem-vindas! Este é um projeto educacional em constante evolução.

---

**Desenvolvido com Python 3.12 + Poetry**

*Sistema genérico e reutilizável para análise estatística descritiva automatizada*
