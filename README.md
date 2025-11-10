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

4. **Exporta automaticamente** relatórios em **PDF profissional**:
   - Apenas PDFs no output (sem poluir com .png, .md, etc.)
   - Todas as imagens embutidas diretamente no PDF
   - Tabelas de frequências formatadas
   - Medidas estatísticas organizadas
   - Interpretações automáticas dos resultados
   - Pronto para compartilhar com pessoas não-técnicas

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
│   │   ├── report_generator.py    # Gerador de Markdown
│   │   └── pdf_generator.py       # Gerador de PDFs
│   └── main.py                # Ponto de entrada
├── data/                      # Seus arquivos de dados
├── output/                    # Resultados (APENAS PDFs)
│   └── <nome_arquivo>/
│       ├── *_relatorio.pdf      # Relatórios por variável
│       └── RELATORIO_GERAL.pdf  # Resumo geral
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
- **weasyprint** (66.0): Geração de PDFs
- **markdown** (3.10): Conversão MD → HTML
- **beautifulsoup4** (4.14.2): Processamento HTML

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
5. ✅ Gera gráficos profissionais (300 DPI) temporariamente
6. ✅ Cria relatórios em Markdown temporariamente
7. ✅ Converte tudo para PDFs com imagens embutidas
8. ✅ Salva **APENAS PDFs** em `output/<nome_arquivo>/`
9. ✅ Remove arquivos temporários automaticamente

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

📄 **Apenas PDFs** (com todas as imagens embutidas):
- `nome_relatorio.pdf` - Relatório da variável nome
- `idade_relatorio.pdf` - Relatório da variável idade (com histograma + boxplot)
- `altura_relatorio.pdf` - Relatório da variável altura (com histograma + boxplot)
- `cidade_relatorio.pdf` - Relatório da variável cidade
- `aprovado_relatorio.pdf` - Relatório da variável aprovado (com gráficos)
- `RELATORIO_GERAL.pdf` - **Resumo completo do dataset** ⭐

💡 **Sem poluição**: Não há arquivos .png ou .md soltos! Tudo está embutido nos PDFs.

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

## 📄 Relatórios PDF Profissionais

Os PDFs gerados são **prontos para compartilhar com pessoas não-técnicas** e incluem:

✅ **Formatação Profissional**:
- Fonte legível e organizada
- Cabeçalhos coloridos e hierarquizados
- Tabelas com cores alternadas para facilitar leitura
- Imagens centralizadas e em alta qualidade

✅ **Imagens Embutidas**:
- Todas as visualizações (gráficos, histogramas, boxplots) são **embutidas diretamente no PDF**
- Não é necessário enviar imagens separadamente
- Gráficos em alta resolução (300 DPI)

✅ **Conteúdo Completo**:
- **Relatórios Individuais**: Um PDF por variável com análise completa
- **Relatório Geral**: PDF resumo com todas as variáveis do dataset

✅ **Pronto para Apresentação**:
- Layout profissional estilo A4
- Numeração de páginas automática
- Quebras de página inteligentes (evita tabelas cortadas)

### Como usar apenas PDFs:

Os PDFs são gerados **automaticamente** junto com os relatórios Markdown. Para compartilhar com outras pessoas:

1. Execute a análise normalmente: `poetry run python src/main.py data/seu_arquivo.csv`
2. Vá para `output/<nome_arquivo>/`
3. Compartilhe os arquivos `.pdf` diretamente!

**Exemplo**: Para o arquivo `pessoas.csv`, você pode enviar:
- `RELATORIO_GERAL.pdf` - Para visão geral
- `idade_relatorio.pdf` - Para análise detalhada da idade
- `altura_relatorio.pdf` - Para análise detalhada da altura

💡 **Dica**: Os PDFs contêm todas as imagens embutidas, então você pode enviá-los por email, WhatsApp, ou incluir em apresentações sem se preocupar com arquivos soltos!

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

## ❓ Perguntas Frequentes (FAQ)

### Por que apenas PDFs no output?

O sistema gera **apenas PDFs** na pasta `output/` para manter tudo limpo e organizado:

✅ **Vantagens**:
- Nenhum arquivo solto (.png, .md) poluindo a pasta
- Tudo que você precisa está dentro dos PDFs
- Fácil de compartilhar (um ou poucos arquivos)
- Imagens embutidas em alta qualidade
- Profissional e pronto para apresentação

🔧 **Como funciona**:
1. Sistema gera gráficos e relatórios em pasta temporária
2. Converte tudo para PDF com imagens embutidas (base64)
3. Salva PDFs em `output/`
4. Remove arquivos temporários automaticamente

💡 **Resultado**: Pasta `output/` limpa com apenas PDFs prontos para compartilhar!

### Posso desabilitar a geração de PDFs?

Sim! No arquivo `src/main.py`, altere:

```python
output_dir = dataset.export_all(generate_charts=True, generate_pdfs=False)
```

### Os PDFs ficam grandes demais?

Os PDFs são otimizados mas podem ficar entre 150-300 KB dependendo do número de gráficos. Isso é normal para PDFs com imagens de alta qualidade embutidas. São perfeitamente compartilháveis por email.

### Posso customizar o estilo dos PDFs?

Sim! Edite o CSS em `src/export/pdf_generator.py` na variável `REPORT_CSS`. Você pode alterar cores, fontes, tamanhos, etc.

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais.

## 👥 Contribuindo

Sugestões e melhorias são bem-vindas! Este é um projeto educacional em constante evolução.

---

**Desenvolvido com Python 3.12 + Poetry**

*Sistema genérico e reutilizável para análise estatística descritiva automatizada*
