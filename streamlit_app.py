import streamlit as st
import pandas as pd
import os
import locale
import folium
from streamlit_folium import st_folium
from datetime import date
from io import BytesIO
import requests
import polyline # Biblioteca para decodificar a geometria da rota
from streamlit_option_menu import option_menu
import base64 # <<< LINHA ADICIONADA PARA CORRIGIR O ERRO



# --- 1. CONFIGURAÇÕES DA PÁGINA E ESTILO ---
st.set_page_config(
    page_title="📊 Dashboard de Viagens",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para customizar a aparência do título baseado na imagem de referência
st.markdown("""
    <style>
            
    /* --- IMPORTANDO FONTES E ÍCONES --- */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&display=swap' );
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css' ); /* <<< ADICIONE ESTA LINHA */
            
    /* ▼▼▼ ADICIONE ESTE NOVO ESTILO PARA O BOTÃO DE DOWNLOAD ▼▼▼ */
    .custom-download-button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px; /* Espaço entre o ícone e o texto */
        background-color: #2c3e50; /* Cor de fundo do botão */
        color: #ffffff; /* Cor do texto */
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #34495e;
        text-decoration: none; /* Remove o sublinhado do link */
        font-weight: bold;
        transition: background-color 0.3s ease, border-color 0.3s ease;
        width: 100%; /* Faz o botão ocupar a largura total do contêiner */
        box-sizing: border-box; /* Garante que padding e border não aumentem a largura */
    }
    .custom-download-button:hover {
        background-color: #34495e; /* Cor ao passar o mouse */
        border-color: #4a90e2;
        color: #ffffff; /* Mantém a cor do texto no hover */
    }
    .custom-download-button i {
        font-size: 1.2em; /* Tamanho do ícone */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            

    /* --- GERAL --- */
    body {
        font-family: "Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif;
        background-color: #0e1117; /* Cor de fundo mais escura */
    }

    /* --- TÍTULO PRINCIPAL --- */
    .main-title {
        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%); /* Gradiente azul claro */
        border-radius: 15px; /* Bordas arredondadas */
        padding: px; /* Espaçamento interno */
        margin: 20px 0; /* Margem superior e inferior */
        text-align: center; /* Centraliza o texto */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); /* Sombra suave */
        border: 1px solid #b3d9ff; /* Borda sutil */
    }
    
    .main-title h1 {
        color: #2c3e50; /* Wet Asphalt */
        font-size: 2.0rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-family: "Poppins", "Montserrat", sans-serif; /* 🔹 usando Google Fonts */
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    /* --- ABAS ESTILO DASHBOARD PREMIUM --- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1A1D29; 
        padding: 8px;
        border-radius: 14px;
        border: 1px solid #2C2F3A;
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-family: "Poppins", "Montserrat", sans-serif;
        padding: 20px 0;
        border-radius: 12px;
        background: #222433;
        color: #ffffff;
        border: 1px solid #2C2F3A;
        transition: all 0.3s ease;
        flex-grow: 1;
        flex-basis: 0;
        text-align: center;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #2A2D3D;
        color: #ffffff;
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59,130,246,0.2);
    }

    /* CÓDIGO NOVO - COM CORES DIFERENTES POR ABA */

/* Estilo base para a aba INATIVA (como já estava) */
.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: "Poppins", "Montserrat", sans-serif;
    padding: 20px 0;
    border-radius: 12px;
    background: #222433; /* Cor cinza escuro para inativas */
    color: #a0a0a0;      /* Cor do texto cinza claro para inativas */
    border: 1px solid #2C2F3A;
    transition: all 0.3s ease;
    flex-grow: 1;
    flex-basis: 0;
    text-align: center;
}

/* Efeito HOVER (passar o mouse) para todas as abas */
.stTabs [data-baseweb="tab"]:hover {
    background: #2A2D3D;
    color: #ffffff;
    border-color: #4a90e2; /* Borda azul ao passar o mouse */
}

/* --- A MÁGICA ACONTECE AQUI: CORES PARA CADA ABA ATIVA --- */

/* Aba 1 (Visão Geral) - Azul */
.stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: #ffffff;
    border-color: #2563eb;
}

/* Aba 2 (Análise Financeira) - Verde */
.stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: #ffffff;
    border-color: #16a34a;
}

/* Aba 3 (Performance) - Laranja */
.stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    color: #ffffff;
    border-color: #ea580c;
}

/* Aba 4 (Motoristas) - Roxo */
.stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    color: #ffffff;
    border-color: #7c3aed;
}

/* Aba 5 (Análise de Rotas) - Vermelho */
.stTabs [data-baseweb="tab"]:nth-child(5)[aria-selected="true"] {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: #ffffff;
    border-color: #dc2626;
}


    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent !important;
    }

    /* === ÍCONES FONT AWESOME NAS ABAS === */
.stTabs [data-baseweb="tab"]::before {
    font-family: "Font Awesome 6 Free"; /* Usa a fonte dos ícones */
    font-weight: 900; /* Necessário para ícones sólidos */
    margin-right: 10px;
    display: inline-block;
    vertical-align: middle;
}

/* Mapeia cada aba para um ícone específico */
.stTabs [data-baseweb="tab"]:nth-child(1)::before { content: "\\f080"; } /* fa-chart-bar (Visão Geral) */
.stTabs [data-baseweb="tab"]:nth-child(2)::before { content: "\\f201"; } /* fa-chart-pie (Análise Financeira) */
.stTabs [data-baseweb="tab"]:nth-child(3)::before { content: "\\f0e7"; } /* fa-bolt (Performance) */
.stTabs [data-baseweb="tab"]:nth-child(4)::before { content: "\\f2c2"; } /* fa-id-card (Motoristas) */
.stTabs [data-baseweb="tab"]:nth-child(5)::before { content: "\\f542"; } /* fa-route (Análise de Rotas) */

    /* --- MÉTRICAS MELHORADAS --- */
    .stMetric {
        background: linear-gradient(135deg, #1e2139 0%, #262a47 100%) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        border: 1px solid #3a4063 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        border-color: #4a90e2 !important;
    }
    
    .stMetric > div:nth-child(1) {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #9ca3af !important;
        margin-bottom: 8px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stMetric > div:nth-child(2) {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
    }

    .kpi-container {
        background: linear-gradient(135deg, #1a1d35 0%, #2d3348 100%);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #3a4063;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .kpi-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
        border-color: #4a90e2;
    }
    
    /* DEPOIS */
    .kpi-title {
        font-size: 14px;
        font-weight: 500;
        color: #FFFFFF; /* BRANCO */
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
        /* ... */
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF; /* Cor padrão para Performance & Operacional (Branco) */
        line-height: 1.1;
    }
    
    /* Cor para métricas POSITIVAS (Financeiro Positivo) */
    .kpi-value.receita,
    .kpi-value.lucro { 
        color: #22c55e; /* Verde */
    }

    /* Cor para CUSTOS (Financeiro Negativo) */
    .kpi-value.custo { 
        color: #f59e0b; /* Laranja/Amarelo */
    }
    /* ... */


    /* --- SIDEBAR --- */
    .css-1d391kg {
        background-color: #1E1E1E;
    }
    .css-1d391kg .stSelectbox [data-baseweb="select"] > div {
        background-color: #333333;
    }
    .css-1d391kg .stDateInput input {
        background-color: #333333;
    }

    /* === AJUSTES PARA O MAPA (Folium/Leaflet) === */
    .leaflet-tile {
        border: none !important;
        box-shadow: none !important;
        image-rendering: optimizeSpeed !important;
        transform: translateZ(0);
    }
    .leaflet-container {
        background: #000;
    }
            
    /* --- NOVO ESTILO PARA O ÍCONE DE AJUDA (TOOLTIP) --- */
    .help-icon {
        position: relative; /* Necessário para o posicionamento do tooltip */
        display: inline-block;
        margin-left: 8px; /* Espaço entre o título e o ícone */
        cursor: help; /* Muda o cursor para indicar que é um item de ajuda */
    }

    .help-icon .tooltip-text {
        visibility: hidden; /* Oculta o balão de dica por padrão */
        width: 250px; /* Largura do balão */
        background-color: #2c3e50; /* Cor de fundo escura */
        color: #fff; /* Cor do texto */
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        border: 1px solid #3498db; /* Borda azul */
        
        /* Posicionamento do balão */
        position: absolute;
        z-index: 1;
        bottom: 125%; /* Posiciona acima do ícone */
        left: 50%;
        margin-left: -125px; /* Metade da largura para centralizar */
        
        /* Efeito de fade */
        opacity: 0;
        transition: opacity 0.3s;
    }

    /* Mostra o balão de dica ao passar o mouse sobre o ícone */
    .help-icon:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    </style>
            
""", unsafe_allow_html=True)

# Configura o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    st.warning("Locale 'pt_BR.UTF-8' não encontrado.")

# --- 2. FUNÇÕES DE APOIO ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e pré-processa os dados do arquivo Excel."""
    df = pd.read_excel(caminho, sheet_name=0)
    for col in ['EMIS_MANIF', 'DIA_SAIDA_MANIF', 'DIA_CHEGADA_MANIF', 'DATA PREV CHEGADA']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    # --- ALTERAÇÃO AQUI ---
    # Garante que as colunas de texto sejam do tipo string
    for col_texto in ['LACRES', 'SITUACAO']:
        if col_texto in df.columns:
            df[col_texto] = df[col_texto].astype(str)
            
    return df

def to_excel(df):
    """
    Converte um DataFrame do Pandas para um arquivo Excel em memória,
    com auto-ajuste da largura das colunas.
    """
    output = BytesIO()
    # Cria um ExcelWriter usando o engine 'xlsxwriter' para ter mais controle
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DadosFiltrados')
        
        # Acessa o workbook e a worksheet para customização
        workbook = writer.book
        worksheet = writer.sheets['DadosFiltrados']
        
        # Itera sobre as colunas do DataFrame para ajustar a largura
        for i, col in enumerate(df.columns):
            # Encontra o comprimento máximo do conteúdo na coluna (incluindo o cabeçalho)
            column_len = max(df[col].astype(str).map(len).max(), len(col))
            # Adiciona um pouco de espaço extra (padding)
            worksheet.set_column(i, i, column_len + 2)
            
    # Pega os dados binários do arquivo Excel gerado na memória
    processed_data = output.getvalue()
    return processed_data

def obter_info_periodo(df, data_inicio=None, data_fim=None):
    """Retorna informações sobre o período selecionado com base na EMISSÃO."""
    # (Esta função sua permanece inalterada)
    if data_inicio and data_fim:
        df_periodo = df[(df['EMIS_MANIF'].dt.date >= data_inicio) & \
                       (df['EMIS_MANIF'].dt.date <= data_fim)]
    elif data_inicio:
        df_periodo = df[df['EMIS_MANIF'].dt.date == data_inicio]
    else:
        df_periodo = df
    
    num_registros = len(df_periodo)
    num_veiculos = df_periodo['PLACA_CAVALO'].nunique()
    num_motoristas = df_periodo['MOTORISTA'].nunique()
    
    return num_registros, num_veiculos, num_motoristas


# --- 3. CARREGAMENTO DOS DADOS ---
caminho_do_arquivo = os.path.join("data", "viagens_outubro.xlsx")
try:
    df_bruto = carregar_dados(caminho_do_arquivo)
except FileNotFoundError:
    st.error(f"❌ **Erro: O arquivo '{caminho_do_arquivo}' não foi encontrado.**")
    st.stop()

# --- INÍCIO DA MUDANÇA ---
# 1. Define a lista de proprietários que você quer manter
proprietarios_desejados = [
    'KM TRANSPORTES ROD. DE CARGAS LTDA',
    'MARCELO H LEMOS BERALDO E CIA LTDA ME'
]

# 2. Filtra o DataFrame para conter apenas os proprietários da lista
#    O .copy() é importante para evitar avisos de "SettingWithCopyWarning" mais tarde
df_original = df_bruto[df_bruto['PROPRIETARIO_CAVALO'].isin(proprietarios_desejados)].copy()

# 3. (Opcional, mas recomendado) Adiciona um aviso se nenhum dado for encontrado após o filtro
if df_original.empty:
    st.warning("⚠️ Nenhum dado encontrado para os proprietários 'KM TRANSPORTES' ou 'MARCELO H LEMOS'. Verifique o arquivo de origem.")
    st.stop()
# --- FIM DA MUDANÇA ---


# ▼▼▼ ADICIONE O NOVO CÓDIGO AQUI ▼▼▼

# --- NOVO FILTRO PARA REMOVER DADOS INDESEJADOS ---
# 1. Define os valores que queremos excluir
motoristas_para_excluir = ['RETIRA']
placas_para_excluir = ['TROCAUN']

# 2. Aplica os filtros para remover as linhas correspondentes
#    O símbolo '~' significa 'NÃO', então estamos mantendo as linhas que NÃO estão na lista.
df_original = df_original[~df_original['MOTORISTA'].isin(motoristas_para_excluir)]
df_original = df_original[~df_original['PLACA_CAVALO'].isin(placas_para_excluir)]
# --- FIM DO NOVO FILTRO ---


# ✅ Conversão automática para colunas numéricas (corrige formatos BR e EUA)
colunas_numericas = ['FRETE-R$', 'CTRB-R$', 'OS-R$', 'ICMS-R$', 'PESO REAL (KG)', 'M3', 'MERCADORIA-R$', 'VOLUMES']



# ✅ Conversão automática para colunas numéricas (corrige formatos BR e EUA)
colunas_numericas = ['FRETE-R$', 'CTRB-R$', 'OS-R$', 'ICMS-R$', 'PESO REAL (KG)', 'M3', 'MERCADORIA-R$', 'VOLUMES']

for col in colunas_numericas:
    if col in df_original.columns:
        # Limpa a coluna, mantendo apenas dígitos, ponto, vírgula e sinal de menos
        df_original[col] = (
            df_original[col]
            .astype(str)
            .str.replace(r'[^\d.,-]', '', regex=True)
            .str.strip()
        )

        # --- NOVA FUNÇÃO DE CONVERSÃO (MAIS SEGURA) ---
        def converter_numero_robusto(valor_str):
            if pd.isna(valor_str) or valor_str == '':
                return 0.0
            
            # Conta a ocorrência de pontos e vírgulas
            num_pontos = valor_str.count('.')
            num_virgulas = valor_str.count(',')

            # Caso 1: Formato brasileiro (ex: "1.234,56" ou "1234,56")
            # A vírgula é o separador decimal.
            if num_virgulas == 1 and (num_pontos == 0 or valor_str.rfind('.') < valor_str.rfind(',')):
                return float(valor_str.replace('.', '').replace(',', '.'))
            
            # Caso 2: Formato americano (ex: "1,234.56" ou "1234.56")
            # O ponto é o separador decimal.
            elif num_pontos == 1 and (num_virgulas == 0 or valor_str.rfind(',') < valor_str.rfind('.')):
                 return float(valor_str.replace(',', ''))

            # Caso 3: Formato com múltiplos separadores de milhar (ex: "1.234.567,89" ou "1,234,567.89")
            # Remove todos os separadores de milhar e converte o decimal
            if num_virgulas > 0 and num_pontos > 0:
                if valor_str.rfind(',') > valor_str.rfind('.'): # Decimal é vírgula
                    return float(valor_str.replace('.', '').replace(',', '.'))
                else: # Decimal é ponto
                    return float(valor_str.replace(',', ''))
            
            # Caso 4: Número sem separador decimal claro (trata como inteiro ou float simples)
            try:
                # Tenta converter diretamente (pode funcionar para "123" ou "123.45")
                return float(valor_str)
            except ValueError:
                # Se falhar, tenta o formato com vírgula decimal
                try:
                    return float(valor_str.replace(',', '.'))
                except ValueError:
                    return 0.0 # Retorna 0 se todas as tentativas falharem

        # Aplica a nova função
        df_original[col] = df_original[col].apply(converter_numero_robusto)


# ========================================
# 🔹 SIDEBAR DE FILTROS
# ========================================

# --- FILTRO DE PERÍODO MELHORADO ---
st.sidebar.subheader("📅 Período de Emissão") # ALTERAÇÃO: Texto do título

# Calcula informações sobre os dados disponíveis
# ALTERAÇÃO: Usar 'EMIS_MANIF' para calcular min/max
df_sem_na_emissao = df_original.dropna(subset=['EMIS_MANIF'])
min_data_emissao = df_sem_na_emissao['EMIS_MANIF'].min().date()
max_data_emissao = df_sem_na_emissao['EMIS_MANIF'].max().date()
total_registros = len(df_sem_na_emissao)

periodo_tipo = st.sidebar.radio(
    "Filtrar por data de EMISSÃO:", # ALTERAÇÃO: Texto do radio button
    ["Dia Específico", "Mês Completo", "Período Personalizado"],
    key="periodo_tipo",
    horizontal=True
)

# Data padrão inteligente: usa a data mais recente disponível
data_padrao_inteligente = max_data_emissao

df_periodo_filtrado = df_original.copy()

if periodo_tipo == "Dia Específico":
    # CSS para estilizar a caixa do dia da semana
    st.sidebar.markdown("""
        <style>
        .dia-semana-box {
            background-color: #2C2F38; /* Cor de fundo similar ao input */
            color: #E0E0E0;             /* Cor do texto */
            padding: 8px 12px;          /* Espaçamento interno */
            border-radius: 6px;         /* Bordas arredondadas */
            text-align: center;         /* Centraliza o texto */
            font-weight: bold;          /* Texto em negrito */
            border: 1px solid #444;     /* Borda sutil */
            margin-top: 28px;           /* Alinha verticalmente com o date_input */
        }
        </style>
    """, unsafe_allow_html=True)

    # Cria as colunas para o layout lado a lado
    col_data, col_dia = st.sidebar.columns([3, 1])

    with col_data:
        # ALTERAÇÃO: Usar as novas variáveis de min/max data
        data_emissao_especifica = st.date_input(
            "📜 Selecione o Dia:", # ALTERAÇÃO: Texto do input
            value=data_padrao_inteligente,
            min_value=min_data_emissao,
            max_value=max_data_emissao,
            format="DD/MM/YYYY"
        )

    with col_dia:
        # Obtém o nome do dia da semana, pega as 3 primeiras letras e capitaliza
        dia_semana_abbr = data_emissao_especifica.strftime('%A')[:3].capitalize()
        # Usa o CSS customizado para criar a caixa
        st.markdown(f'<div class="dia-semana-box">{dia_semana_abbr}</div>', unsafe_allow_html=True)

    # ALTERAÇÃO: Lógica de filtro agora usa 'EMIS_MANIF'
    df_periodo_filtrado = df_original[df_original['EMIS_MANIF'].dt.date == data_emissao_especifica]

    # ALTERAÇÃO: Feedback usa a nova data e textos
    num_reg, num_veic, num_mot = obter_info_periodo(df_original, data_emissao_especifica)
    if num_reg > 0:
        st.sidebar.info(f"📜 {num_reg} Manifestos • 🚚 {num_veic} Veículos")
    else:
        st.sidebar.warning(f"⚠️ Nenhum registro encontrado para {data_emissao_especifica.strftime('%d/%m/%Y')}")

elif periodo_tipo == "Mês Completo":
    # ALTERAÇÃO: Usar 'EMIS_MANIF' para agrupar por mês
    meses = df_sem_na_emissao['EMIS_MANIF'].dt.to_period("M").unique().astype(str)
    meses_formatados = {m: pd.Period(m).strftime("%B/%Y").capitalize() for m in sorted(meses, reverse=True)}
    mes_formatado_sel = st.sidebar.selectbox("🗓️ Selecione o Mês:", list(meses_formatados.values()))
    mes_emissao_completo = [k for k, v in meses_formatados.items() if v == mes_formatado_sel][0]
    
    # ALTERAÇÃO: Filtrar por mês de emissão
    df_periodo_filtrado = df_original[df_original['EMIS_MANIF'].dt.to_period("M").astype(str) == mes_emissao_completo]
    
    num_reg = len(df_periodo_filtrado)
    if num_reg > 0:
        st.sidebar.success(f"✅ {num_reg} registros encontrados para {mes_formatado_sel}")
        datas_mes = sorted(df_periodo_filtrado['EMIS_MANIF'].dt.date.unique())
        st.sidebar.info(f"📅 {len(datas_mes)} dias com emissões no mês")

elif periodo_tipo == "Período Personalizado":
    # ALTERAÇÃO: Usar as novas variáveis de min/max data
    periodo_emissao_sel = st.sidebar.date_input(
        "🗓️ Selecione o intervalo:", 
        [min_data_emissao, max_data_emissao], 
        format="DD/MM/YYYY"
    )
    if len(periodo_emissao_sel) == 2:
        # ALTERAÇÃO: Filtrar pelo intervalo de emissão
        df_periodo_filtrado = df_original[
            (df_original['EMIS_MANIF'].dt.date >= periodo_emissao_sel[0]) & \
            (df_original['EMIS_MANIF'].dt.date <= periodo_emissao_sel[1])
        ]
        
        num_reg, num_veic, num_mot = obter_info_periodo(df_original, periodo_emissao_sel[0], periodo_emissao_sel[1])
        if num_reg > 0:
            dias_periodo = (periodo_emissao_sel[1] - periodo_emissao_sel[0]).days + 1
            st.sidebar.success(f"✅ {num_reg} registros encontrados")
            st.sidebar.info(f"📅 {dias_periodo} dias • 🚚 {num_veic} veículos • 👨‍✈️ {num_mot} motoristas")
        else:
            st.sidebar.warning("⚠️ Nenhum registro encontrado no período selecionado")

# --- FILTROS DE VIAGEM ---
with st.sidebar.expander("👨‍✈️ Filtros de Viagem", expanded=True):
    motorista_sel = st.selectbox("👤 Motorista", ["(Todos)"] + sorted(df_periodo_filtrado["MOTORISTA"].dropna().unique()))
    destino_sel = st.selectbox("📍 Destino Final", ["(Todos)"] + sorted(df_periodo_filtrado["CIDADE_UF_DEST"].dropna().unique()))

    # --- LÓGICA DE ROTA DINÂMICA (AGRUPANDO POR ORDEM GEOGRÁFICA) ---
    # ALTERAÇÃO: Usar 'EMIS_MANIF' para criar o identificador da viagem
    df_periodo_filtrado['DIA_EMISSAO_STR'] = df_periodo_filtrado['EMIS_MANIF'].dt.strftime('%d/%m/%Y')
    rotas_df = df_periodo_filtrado.dropna(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA', 'DEST_MANIF']).copy()

    if not rotas_df.empty:
        # 1. DEFINIR A ORDEM GEOGRÁFICA DAS ENTREGAS
        # Mapeia a sigla do destino para uma ordem numérica.
        # Quanto menor o número, mais cedo na rota.
        ordem_geografica = {
            # 📍 Sequência inicial (SP)
            'CSL': 1,   # Cassilândia
            'PBA': 2,   # Paranaíba
            'ATB': 3,   # Aparecida do Taboado
            'SPO': 4,   # São Paulo

            # 📍 Ribas e Água Clara
            'RRP': 5,   # Ribas do Rio Pardo
            'ACL': 6,   # Água Clara

            # 📍 Miranda e Bodoquena
            'MDA': 7,   # Miranda
            'BDQ': 8,   # Bodoquena

            # 📍 Camapuã e Costa Rica
            'CMP': 9,   # Camapuã
            'CRC': 10,  # Costa Rica

            # 📍 Região Sul
            'NSU': 11,  # Nova Alvorada do Sul
            'RBT': 12,  # Rio Brilhante
            'DOU': 13,  # Dourados
            'IVM': 14,  # Ivinhema

            # 📍 Região Sudoeste
            'NQU': 15,  # Nioaque
            'JDM': 16,  # Jardim
            'SDL': 17,  # Sidrolândia
            'MJU': 18,  # Maracaju

            # 📍 Região Norte
            'SGO': 19,  # São Gabriel do Oeste
            'RVM': 20,  # Rio Verde de Mato Grosso
            'COX': 21,  # Coxim
            'PGO': 22,  # Pedro Gomes
            'SNR': 23,  # Sonora

            # 📍 Já existentes
            'PDA': 24,  # Paraíso das Águas
            'CDS': 25,  # Chapadão do Sul
            'GYN': 26,  # Goiânia
        }


        # 2. FUNÇÃO PARA ORDENAR OS DESTINOS
        def ordenar_destinos(destinos_unicos):
            """
            Ordena uma lista de siglas de destino com base no dicionário 'ordem_geografica'.
            Destinos não mapeados são colocados no final, em ordem alfabética.
            """
            return sorted(destinos_unicos, key=lambda d: ordem_geografica.get(d, 99))

        # 3. AGRUPAR E APLICAR A ORDENAÇÃO
        rotas_df = rotas_df.groupby(
            ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']
        ).agg(
            Destinos=('DEST_MANIF', lambda x: ' - '.join(ordenar_destinos(x.unique())))
        ).reset_index()


        # --- VERSÃO FINAL (Lida com nomes compostos como "dos Santos") ---
        def formatar_nome_motorista(nome_completo):
            """Formata o nome do motorista para ser mais legível."""
            partes = str(nome_completo).strip().split()
            
            # Se não houver nome, retorna vazio
            if not partes:
                return ""
                
            # Se o nome tiver 3 ou mais partes e a segunda for uma preposição curta
            preposicoes_curtas = ['DA', 'DE', 'DO', 'DOS']
            if len(partes) >= 3 and partes[1].upper() in preposicoes_curtas:
                # Pega as três primeiras partes (ex: MARCIANO DOS SANTOS)
                return f"{partes[0]} {partes[1]} {partes[2]}"
                
            # Se tiver 2 ou mais partes (e a segunda não for preposição), pega as duas primeiras
            elif len(partes) >= 2:
                # Pega as duas primeiras partes (ex: RAUL SANTOS)
                return f"{partes[0]} {partes[1]}"
                
            # Se tiver apenas uma palavra, retorna essa palavra
            else:
                return partes[0]

        # Aplica a função para criar uma coluna com o nome curto
        rotas_df['NOME_CURTO_MOTORISTA'] = rotas_df['MOTORISTA'].apply(formatar_nome_motorista)

        # Agora, cria o NOME_ROTA usando o nome curto
        rotas_df['NOME_ROTA'] = (
            "📍 " + rotas_df['Destinos'] + 
            " 👨‍✈️ " + rotas_df['NOME_CURTO_MOTORISTA']
        )

        lista_rotas_visiveis = ["(Todos)"] + sorted(rotas_df['NOME_ROTA'].unique())

    else:
        lista_rotas_visiveis = ["(Todos)"]
        
    rota_sel_visivel = st.selectbox("🗺️ Selecione a Rota", lista_rotas_visiveis)


# --- FILTROS DE VEÍCULOS ---
with st.sidebar.expander("🚛 Filtros de Veículos", expanded=True):
    placa_sel = st.selectbox("🚚 Placa do Cavalo", ["(Todos)"] + sorted(df_periodo_filtrado["PLACA_CAVALO"].dropna().unique()))
    tipo_sel = st.selectbox("⚙️ Tipo do Veículo", ["(Todos)"] + sorted(df_periodo_filtrado["TIPO_CAVALO"].dropna().unique()))
    proprietario_sel = st.selectbox("🏢 Proprietário", ["(Todos)"] + sorted(df_periodo_filtrado["PROPRIETARIO_CAVALO"].dropna().unique()))

# --- BUSCA RÁPIDA ---
with st.sidebar.expander("🔎 Busca Rápida", expanded=False):
    busca_placa = st.text_input("Buscar por Placa", placeholder="Digite a placa...")
    busca_lacre = st.text_input("Buscar por Lacres", placeholder="Digite o lacre...")

# ========================================
# 🔹 APLICAÇÃO FINAL DOS FILTROS
# ========================================
df_filtrado = df_original.copy()

# A busca rápida tem prioridade sobre os outros filtros
if busca_placa:
    df_filtrado = df_original[df_original['PLACA_CAVALO'].str.contains(busca_placa.strip(), case=False, na=False)]
elif busca_lacre:
    if 'LACRES' in df_original.columns:
        df_filtrado = df_original[df_original['LACRES'].str.contains(busca_lacre.strip(), case=False, na=False)]
    else:
        st.sidebar.error("A coluna 'LACRES' não foi encontrada no arquivo.")
else:
    df_filtrado = df_periodo_filtrado.copy()

    if rota_sel_visivel != "(Todos)":
        try:
            viagens_possiveis = rotas_df[rotas_df['NOME_ROTA'] == rota_sel_visivel]
            if not viagens_possiveis.empty:
                placa_rota = viagens_possiveis['PLACA_CAVALO'].iloc[0]
                # ALTERAÇÃO: Usar as colunas corretas do 'rotas_df'
                data_emissao_rota = viagens_possiveis['DIA_EMISSAO_STR'].iloc[0]
                motorista_rota = viagens_possiveis['MOTORISTA'].iloc[0]
                
                df_filtrado = df_periodo_filtrado[
                # ALTERAÇÃO: Filtrar usando 'DIA_EMISSAO_STR'
                    (df_periodo_filtrado['PLACA_CAVALO'] == placa_rota) &
                    (df_periodo_filtrado['DIA_EMISSAO_STR'] == data_emissao_rota) &
                    (df_periodo_filtrado['MOTORISTA'] == motorista_rota)
                ]
        except (IndexError, KeyError):
            st.warning("Não foi possível aplicar o filtro de rota.")
            pass
    else:
        if motorista_sel != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["MOTORISTA"] == motorista_sel]
        if placa_sel != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["PLACA_CAVALO"] == placa_sel]
        if tipo_sel != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["TIPO_CAVALO"] == tipo_sel]
        if proprietario_sel != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["PROPRIETARIO_CAVALO"] == proprietario_sel]
        if destino_sel != "(Todos)":
           df_filtrado = df_filtrado[df_filtrado["CIDADE_UF_DEST"] == destino_sel]

# ========================================
# 🔹 CORPO PRINCIPAL DO DASHBOARD
# ========================================

# --- INÍCIO DA CORREÇÃO ---

# 1. Mover o cálculo de custo e distância para o escopo global, após os filtros.
#    Isso garante que as variáveis estarão disponíveis para todas as abas.

# Dicionário de custo por KM, baseado no tipo do veículo.
custo_km_por_tipo = {
    'TOCO': 3.50,
    'TRUCK': 4.50,
    'CAVALO': 6.75,
    'CARRETA': 6.75
}

# Inicializa as variáveis para evitar erros caso o DataFrame esteja vazio.
valor_por_km = 0
custo_ctrb_os = 0
distancia_estimada_km = 0

# Garante que há dados filtrados para evitar erros de índice.
if not df_filtrado.empty:
    # Determina o tipo de veículo (usando o mais frequente se houver vários).
    tipo_veiculo = df_filtrado['TIPO_CAVALO'].mode()[0] if 'TIPO_CAVALO' in df_filtrado.columns and not df_filtrado['TIPO_CAVALO'].dropna().empty else "PADRAO"
    
    # Busca o valor do custo por KM no dicionário.
    valor_por_km = custo_km_por_tipo.get(str(tipo_veiculo).upper(), 0)

    # --- Lógica de Custo Centralizada (reutilizada da sua tab1) ---
    # Esta lógica calcula o custo total de CTRB/OS corretamente, considerando as regras de negócio.
    df_custo = df_filtrado.copy()
    if 'VIAGEM_ID' not in df_custo.columns:
        df_custo['VIAGEM_ID'] = df_custo.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

    resumo_viagens_custo = df_custo.groupby('VIAGEM_ID').agg(
        PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
        CUSTO_OS=('OS-R$', 'max'),
        CUSTO_CTRB=('CTRB-R$', 'max'),
        DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique()))
    ).reset_index()

    def calcular_custo_viagem_com_regra(row):
        custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
        destinos_str = str(row.get('DESTINOS', '')).upper()
        if 'GYN' in destinos_str or 'SPO' in destinos_str:
            return custo_base / 2
        return custo_base

    if not resumo_viagens_custo.empty:
        resumo_viagens_custo['CUSTO_FINAL_VIAGEM'] = resumo_viagens_custo.apply(calcular_custo_viagem_com_regra, axis=1)
        custo_ctrb_os = resumo_viagens_custo['CUSTO_FINAL_VIAGEM'].sum()

    # Agora, calcula a distância estimada com as variáveis já definidas.
    if valor_por_km > 0 and custo_ctrb_os > 0:
        distancia_estimada_km = custo_ctrb_os / valor_por_km

# Adiciona a coluna de distância ao DataFrame principal para uso global (ex: na tab4).
# Usar .loc para evitar o SettingWithCopyWarning.
df_filtrado.loc[:, 'DISTANCIA_ESTIMADA_KM'] = distancia_estimada_km

# --- FIM DA CORREÇÃO ---


# TÍTULO PRINCIPAL COM ESTILO DAS IMAGENS DE REFERÊNCIA
st.markdown("""
    <div class="main-title">
        <h1><i class="fa-solid fa-truck-front"></i> Gestão de Frota: Análise de Viagens</h1>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Visão Geral", 
    "Análise Financeira", 
    "Performance da Frota", 
    "Análise de Motoristas", 
    "Análise de Rotas"
])

# --- ABA 1: VISÃO GERAL (PROFISSIONALIZADA) ---
with tab1:
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
               # ==============================
        # 1. CÁLCULOS PRINCIPAIS (COM LÓGICA DE CUSTO DINÂMICO E DISTÂNCIA)
        # ==============================
        receita_total = df_filtrado.get('FRETE-R$', pd.Series(0)).sum()

        # --- ### INÍCIO DA NOVA LÓGICA DE CUSTO CENTRALIZADA ### ---
        custo_ctrb_os = 0
        if not df_filtrado.empty:
            # 1. Cria uma cópia para trabalhar
            df_custo = df_filtrado.copy()

            # 2. Identifica cada viagem única para o agrupamento
            if 'VIAGEM_ID' not in df_custo.columns:
                df_custo['VIAGEM_ID'] = df_custo.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

            # 3. Agrupa por viagem para obter os valores corretos
            resumo_viagens_custo = df_custo.groupby('VIAGEM_ID').agg(
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique()))
            ).reset_index()

            # 4. Função para calcular o custo final por viagem (com a regra de divisão)
            def calcular_custo_viagem_com_regra(row):
                custo_base = 0
                if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    custo_base = row['CUSTO_OS']
                else:
                    custo_base = row['CUSTO_CTRB']

                # Aplica a regra de divisão
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                
                return custo_base

            # 5. Aplica a função para cada viagem e soma os resultados
            if not resumo_viagens_custo.empty:
                resumo_viagens_custo['CUSTO_FINAL_VIAGEM'] = resumo_viagens_custo.apply(calcular_custo_viagem_com_regra, axis=1)
                
                # 6. O custo total agora é a soma dos custos já processados
                custo_ctrb_os = resumo_viagens_custo['CUSTO_FINAL_VIAGEM'].sum()
        # --- ### FIM DA NOVA LÓGICA DE CUSTO CENTRALIZADA ### ---
                    
        # Cálculos financeiros usando a nova variável 'custo_ctrb_os'
        custo_icms = df_filtrado.get('ICMS-R$', pd.Series(0)).sum()
        custo_total = custo_ctrb_os + custo_icms # <<< USA O CUSTO JÁ CORRIGIDO
        lucro_estimado = receita_total - custo_total
        margem_lucro = (lucro_estimado / receita_total * 100) if receita_total > 0 else 0

        # ▼▼▼ ADICIONE ESTA LINHA ▼▼▼
        valor_mercadoria_total = df_filtrado.get('MERCADORIA-R$', pd.Series(0)).sum()

        # Cálculos operacionais
        peso_total = df_filtrado.get('PESO REAL (KG)', pd.Series(0)).sum()

        # Cálculos operacionais
        peso_total = df_filtrado.get('PESO REAL (KG)', pd.Series(0)).sum()

        # Volume bruto da base
        volume_total = df_filtrado.get('M3', pd.Series(0)).sum()

        # --- Correção: normalização da unidade do volume ---
        # Se o valor total for muito grande, assume que está em litros e converte para m³
        if volume_total > 1000:  
            volume_total_m3 = volume_total / 10000
        else:
            volume_total_m3 = volume_total  # já está em m³

        # --- Capacidades e ociosidade (LÓGICA DINÂMICA) ---


        # 1. Dicionário com as capacidades por tipo de veículo
        capacidades_por_tipo = {
            'TOCO':    {'peso_kg': 10000, 'volume_m3': 55},
            'TRUCK':   {'peso_kg': 16000, 'volume_m3': 75},
            'CAVALO':  {'peso_kg': 25000, 'volume_m3': 110},
            'PADRAO':  {'peso_kg': 25000, 'volume_m3': 80} # Valor padrão de segurança
        }

        # 2. Identifica o tipo do veículo a partir dos dados filtrados
        tipo_veiculo_selecionado = "PADRAO" # Padrão inicial
        if not df_filtrado.empty and 'TIPO_CAVALO' in df_filtrado.columns:
            tipo_veiculo_selecionado = df_filtrado['TIPO_CAVALO'].iloc[0]

        # 3. Busca a capacidade correta no dicionário
        capacidade_veiculo = capacidades_por_tipo.get(str(tipo_veiculo_selecionado).upper(), capacidades_por_tipo['PADRAO'])

        # 4. Define as variáveis de capacidade que o resto do código utiliza
        capacidade_peso_kg = capacidade_veiculo['peso_kg']
        capacidade_volume_m3 = capacidade_veiculo['volume_m3']

        # O cálculo de ociosidade agora usa os valores corretos e dinâmicos
        ociosidade_peso = (1 - (peso_total / capacidade_peso_kg)) * 100 if capacidade_peso_kg > 0 else 0
        ociosidade_volume = (1 - (volume_total_m3 / capacidade_volume_m3)) * 100 if capacidade_volume_m3 > 0 else 0

        # Infos de identificação (necessárias para os cálculos seguintes)
        nome_completo_motorista = df_filtrado['MOTORISTA'].iloc[0]

        # --- LÓGICA PARA PEGAR O PRIMEIRO E ÚLTIMO NOME ---
        partes_nome = nome_completo_motorista.split()
        if len(partes_nome) > 1:
            # Junta o primeiro nome (partes_nome[0]) com o último (partes_nome[-1])
            motorista_principal = f"{partes_nome[0]} {partes_nome[-1]}"
        else:
            # Caso o nome tenha apenas uma palavra, usa o nome completo
            motorista_principal = nome_completo_motorista
        # --- FIM DA LÓGICA ---

        placa_cavalo = df_filtrado['PLACA_CAVALO'].iloc[0]
        placa_carreta = df_filtrado['PLACA_CARRETA'].iloc[0] if 'PLACA_CARRETA' in df_filtrado.columns else "N/A"
        tipo_veiculo = df_filtrado['TIPO_CAVALO'].iloc[0] if 'TIPO_CAVALO' in df_filtrado.columns else "N/A"
        proprietario_veiculo = df_filtrado['PROPRIETARIO_CAVALO'].iloc[0] if 'PROPRIETARIO_CAVALO' in df_filtrado.columns else "N/A"

        
        # --- CÁLCULO DE DISTÂNCIA ESTIMADA (POSICIONADO CORRETAMENTE) ---
        custo_km_por_tipo = {
            'TOCO': 3.50,
            'TRUCK': 4.50,
            'CAVALO': 6.75,
            'CARRETA': 6.75
        }
        # Usa str(tipo_veiculo) para mais segurança caso o valor seja nulo
        valor_por_km = custo_km_por_tipo.get(str(tipo_veiculo).upper(), 0)
        
        # Usa a variável de custo dinâmico 'custo_ctrb_os' para o cálculo
        if valor_por_km > 0 and custo_ctrb_os > 0:
            distancia_estimada_km = custo_ctrb_os / valor_por_km
        else:
            distancia_estimada_km = 0

        # --- IDENTIFICAÇÃO DO DESTINO E OUTROS DETALHES ---
        ordem_geografica_cidades = {
            'PARAISO DAS AGUAS/MS': 1,
            'CHAPADAO DO SUL/MS': 2,
            'GOIANIA/GO': 3,
        }

        destinos_da_viagem = df_filtrado['CIDADE_UF_DEST'].dropna().unique()
        if len(destinos_da_viagem) > 0:
            destino_principal = sorted(destinos_da_viagem, key=lambda d: ordem_geografica_cidades.get(d, 99))[-1]
        else:
            destino_principal = "N/A"

        data_emissao = df_filtrado['EMIS_MANIF'].min()
        num_manifestos = df_filtrado['NUM_MANIF'].nunique()
        num_lacres = df_filtrado['LACRES'].nunique()


        # ==============================
        # 2. CABEÇALHO EXECUTIVO COM ÍCONES (7 KPIs)
        # ==============================
        if rota_sel_visivel != "(Todos)":
            st.markdown("""
            <style>
            .card-info {
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                border-radius: 14px;
                padding: 20px;
                border: 1px solid #374151;
                box-shadow: 0 6px 16px rgba(0,0,0,0.3);
                text-align: center;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 110px;
            }
            .card-info:hover {
                transform: translateY(-3px);
                border-color: #3b82f6;
                box-shadow: 0 10px 24px rgba(59,130,246,0.4);
            }
            .card-title {
                font-size: 14px;
                font-weight: 600;
                color: #9ca3af;
                text-transform: uppercase;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .card-value {
                font-size: 22px;
                font-weight: 700;
                color: #fff;
                line-height: 1.3;
            }
            </style>
            """, unsafe_allow_html=True)

            kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7 = st.columns(7)

            with kpi1:
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-user-tie"></i> Motorista</div>
                    <div class="card-value">{motorista_principal}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi2:
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-truck-front"></i> Placa Cavalo</div>
                    <div class="card-value">{placa_cavalo}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi3:
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-trailer"></i> Placa Carreta</div>
                    <div class="card-value">{placa_carreta}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi4:
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-gear"></i> Tipo Veículo</div>
                    <div class="card-value">{tipo_veiculo}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi5:
                proprietario_curto = 'KM TRANSPORTES' if proprietario_veiculo == 'KM TRANSPORTES ROD. DE CARGAS LTDA' else proprietario_veiculo
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-building-user"></i> Proprietário</div>
                    <div class="card-value">{proprietario_curto}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi6:
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-map-location-dot"></i> Destino</div>
                    <div class="card-value">{destino_principal}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi7:
                st.markdown(f"""
                <div class="card-info">
                    <div class="card-title"><i class="fa-solid fa-calendar-day"></i> Emissão</div>
                    <div class="card-value">{data_emissao.strftime('%d/%m/%Y')}</div>
                </div>
                """, unsafe_allow_html=True)


        # ==============================
        # 3. KPIs FINANCEIROS COM ÍCONES (COM TÍTULO DINÂMICO)
        # ==============================
        st.subheader("💰 Análise Financeira")
        kpi_f1, kpi_f2, kpi_f3, kpi_f4, kpi_f5, kpi_f6 = st.columns(6)


        # Garante que o locale está configurado para formatação correta
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except locale.Error:
            # Se o locale pt_BR não estiver disponível, podemos criar uma formatação manual
            # para evitar que o app quebre.
            pass

        def formatar_moeda(valor):
            """Formata um número como moeda brasileira (R$ 1.234,56)."""
            try:
                # Tenta usar o locale, que é a forma mais correta.
                return locale.currency(valor, grouping=True)
            except (NameError, TypeError, ValueError):
                # Se falhar, usa uma formatação manual robusta.
                try:
                    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except (ValueError, TypeError):
                    return "R$ 0,00"

        def formatar_percentual(valor):
            """Formata um número como percentual com vírgula (ex: 82,1%)."""
            try:
                return f"{valor:.1f}%".replace('.', ',')
            except (ValueError, TypeError):
                return "0,0%"

        def formatar_numero(valor, casas_decimais=0):
            """Formata um número com separador de milhar e vírgula decimal (padrão BR)."""
            try:
                return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                return "0"


        # ===============================================
        # Função para calcular distância real com OSRM
        # ===============================================
        import requests

        def calcular_distancia_osrm(lat_origem, lon_origem, lat_dest, lon_dest):
            """
            Calcula a distância real (dirigindo) entre origem e destino usando OSRM.
            Retorna em KM arredondado.
            """
            try:
                url = f"http://router.project-osrm.org/route/v1/driving/{lon_origem},{lat_origem};{lon_dest},{lat_dest}?overview=false"
                resposta = requests.get(url ).json()
                distancia_metros = resposta["routes"][0]["distance"]
                return round(distancia_metros / 1000, 1)  # distância em KM
            except Exception:
                return None

        # --- Lógica para determinar o título e o ícone do KPI de Custo ---
        titulo_kpi_custo = "📄 Custo CTRB / OS" # Título padrão
        if not df_filtrado.empty:
            # Pega o primeiro proprietário dos dados filtrados para decidir o título
            proprietario_principal = df_filtrado['PROPRIETARIO_CAVALO'].iloc[0]
            
            # Se houver mais de um proprietário nos dados (visão geral), mantém o título genérico
            if df_filtrado['PROPRIETARIO_CAVALO'].nunique() > 1:
                titulo_kpi_custo = "📄 Custo CTRB / OS"
            elif proprietario_principal == 'KM TRANSPORTES ROD. DE CARGAS LTDA':
                titulo_kpi_custo = "📄 Custo CTRB"
            elif proprietario_principal == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                titulo_kpi_custo = "📋 Custo OS" # Ícone diferente para OS

        # Ajuste no dicionário de KPIs financeiros para usar o título dinâmico
        kpis_financeiros = {
            kpi_f1: {
                "titulo": "💵 Receita Total",
                "valor": formatar_moeda(receita_total),
                "classe": "receita"
            },
            kpi_f2: {
                "titulo": titulo_kpi_custo,
                "valor": formatar_moeda(custo_ctrb_os),
                "classe": "custo"
            },
            kpi_f3: {
                "titulo": "💸 ICMS",
                "valor": formatar_moeda(custo_icms),
                "classe": "custo"
            },
            kpi_f4: {
                "titulo": """📊 Custo Total
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Soma de CTRB + ICMS.<br>
                            Representa o custo total da viagem.
                        </span>
                    </span>""",
                "valor": formatar_moeda(custo_total),
                "classe": "custo"
            },
            kpi_f5: {
                "titulo": """💰 Lucro Líquido
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Receita − (CTRB + ICMS).<br>
                            Lucro final após custos.
                        </span>
                    </span>""",
                "valor": formatar_moeda(lucro_estimado),
                "classe": "lucro"
            },
            kpi_f6: {
                "titulo": """📈 Margem de Lucro
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            (Lucro ÷ Receita) × 100.<br>
                            Percentual de ganho líquido.
                        </span>
                    </span>""",
                "valor": formatar_percentual(margem_lucro),
                "classe": "lucro"
            }
        }

        # Itera sobre o dicionário para criar cada KPI
        for coluna, info in kpis_financeiros.items():
            with coluna:
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: center;'>
                        <div class='kpi-title'>{info['titulo']}</div>
                        <div class='kpi-value {info['classe']}'>{info['valor']}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()


        # ==============================
        # 4. INDICADORES DE PERFORMANCE
        # ==============================
        st.subheader("📊 Indicadores de Performance")
        perf1, perf2, perf3 = st.columns(3)

        # CORREÇÃO: Usando a variável 'custo_ctrb_os' que foi definida na seção de cálculos
        custo_transferencia = (custo_ctrb_os / receita_total * 100) if receita_total > 0 else 0
        custo_faturamento = (custo_total / receita_total * 100) if receita_total > 0 else 0

        with perf1:
            st.markdown(f"""
                <div class='kpi-container' style='text-align: center;'>
                    <div class='kpi-title'>
                        🔄 Custo de Transferência
                        <span class="help-icon">ℹ️
                            <span class="tooltip-text">
                                Indica quanto do valor do frete foi gasto em custos de transporte entre filiais.
                            </span>
                        </span>
                    </div>
                    <div class='kpi-value'>{formatar_percentual(custo_transferencia)}</div>
                </div>
            """, unsafe_allow_html=True)


        with perf2:
            st.markdown(f"""
                <div class='kpi-container' style='text-align: center;'>
                    <div class='kpi-title'>
                        📊 Custo Total
                        <span class="help-icon">ℹ️
                            <span class="tooltip-text">
                                Soma de CTRB + ICMS. Porcentagem do faturamento usada para cobrir os custos totais da viagem.
                            </span>
                        </span>
                    </div>
                    <div class='kpi-value'>{formatar_moeda(custo_total)}</div>
                </div>
            """, unsafe_allow_html=True)


        with perf3:
            st.markdown(f"""
                <div class='kpi-container' style='text-align: center;'>
                    <div class='kpi-title'>
                        📈 Lucro Líquido (%)
                        <span class="help-icon">ℹ️
                            <span class="tooltip-text">
                                Percentual que mostra quanto da receita permaneceu como lucro após todos os custos.
                            </span>
                        </span>
                    </div>
                    <div class='kpi-value'>{formatar_percentual(margem_lucro)}</div>
                </div>
            """, unsafe_allow_html=True)


        st.divider()

        # ==============================
        # 5. DETALHES OPERACIONAIS (COM NOVOS KPIS)
        # ==============================
        st.subheader("⚙️ Detalhes Operacionais")

        # --- LÓGICA PARA KPIs DINÂMICOS ---
        if rota_sel_visivel != "(Todos)":
            # --- MODO VIAGEM ÚNICA: Exibe detalhes específicos da viagem selecionada ---
            
            # 1. CALCULAR OS NOVOS VALORES
            qtd_ctrc_total = df_filtrado.get('QTDE_CTRC', pd.Series(0)).sum()
            volumes_total = df_filtrado.get('VOLUMES', pd.Series(0)).sum()
            
            custo_por_km = valor_por_km 
            
            # 2. AJUSTAR O NÚMERO DE COLUNAS PARA 7
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            # Card 1: Custo por KM
            with col1:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">💸 Custo por KM</div>
                        <div class="kpi-value">{formatar_moeda(custo_por_km)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Card 2: Valor da Mercadoria
            with col2:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">💰 Valor da Mercadoria</div>
                        <div class="kpi-value">{formatar_moeda(valor_mercadoria_total)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Card 3: Peso Total
            with col3:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">⚖️ Peso Total (KG)</div>
                        <div class="kpi-value">{formatar_numero(peso_total)} KG</div>
                    </div>
                """, unsafe_allow_html=True)

            # Card 4: QTD CTRC (NOVO)
            with col4:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">📄 Qtd. CTRCs</div>
                        <div class="kpi-value">{formatar_numero(qtd_ctrc_total)}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Card 5: VOLUMES (NOVO)
            with col5:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">📦 Volumes</div>
                        <div class="kpi-value">{formatar_numero(volumes_total)}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Card 6: Volume M³
            with col6:
                volume_exibicao = volume_total
                try:
                    if volume_exibicao > 100:
                        volume_exibicao = volume_exibicao / 10000
                except:
                    volume_exibicao = 0
                volume_formatado_correto = f"{volume_exibicao:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">🧊 Volume (M³)</div>
                        <div class="kpi-value">{volume_formatado_correto}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Card 7: Distância
            with col7:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">🗺️ Distância (KM)</div>
                        <div class="kpi-value">{formatar_numero(distancia_estimada_km, casas_decimais=0)} KM</div>
                    </div>
                """, unsafe_allow_html=True)

        else:
            # --- MODO VISÃO GERAL: Exibe KPIs agregados de todas as viagens no período ---
            
            # 1. Calcula os novos KPIs agregados
            total_viagens = df_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroups if not df_filtrado.empty else 0
            
            if not df_filtrado.empty:
                entregas_por_viagem = df_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR'])['DEST_MANIF'].nunique()
                total_entregas = entregas_por_viagem.sum()
            else:
                total_entregas = 0
            
            cidades_atendidas = df_filtrado['CIDADE_UF_DEST'].nunique()
            
            # 2. Cria o layout com 5 colunas para os novos KPIs
            col1, col2, col3, col4, col5 = st.columns(5)

            # Card 1: Total de Viagens
            with col1:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-route"></i> Total de Viagens</div>
                        <div class="kpi-value">{total_viagens}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Card 2: Total de Entregas
            with col2:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-dolly"></i> Total de Entregas</div>
                        <div class="kpi-value">{formatar_numero(total_entregas)}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Card 3: Peso Total Agregado
            with col3:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">⚖️ Peso Total (KG)</div>
                        <div class="kpi-value">{formatar_numero(peso_total)} KG</div>
                    </div>
                """, unsafe_allow_html=True)

            # Card 4: Cidades Atendidas
            with col4:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-city"></i> Cidades Atendidas</div>
                        <div class="kpi-value">{cidades_atendidas}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Card 5: Distância Total Estimada
            with col5:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">🗺️ Distância Total (KM)</div>
                        <div class="kpi-value">{formatar_numero(distancia_estimada_km, casas_decimais=0)} KM</div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()

                # 🌟 CSS PROFISSIONAL PARA OS CARDS E O NOVO TÍTULO
        st.markdown("""
        <style>
            /* ▼▼▼ SUBSTITUA O ESTILO DO TÍTULO ANTERIOR POR ESTE ▼▼▼ */
            .title-block-modern {
                background: linear-gradient(90deg, rgba(30, 41, 59, 0.8) 0%, rgba(30, 41, 59, 0.2) 100%);
                border-left: 5px solid #22c55e;
                border-right: 5px solid #22c55e;
                padding: 5px 30px;
                margin: 20px 0;
                border-radius: 12px;
                width: 100%;
                box-sizing: border-box;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }

            .title-block-modern h2 {
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 1.8rem;
                font-weight: 700;
                color: #ffffff;
                margin: 0;
                letter-spacing: 0.5px;
            }

            .title-block-modern .fa-scale-balanced {
                font-size: 2.2rem;
                color: #22c55e;
            }
            /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */

            .frota-title {
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            /* --- CORREÇÃO APLICADA AQUI --- */
            .ocupacao-card-custom {
                background-color: #1E1E2E;
                border-radius: 14px;
                padding: 18px;
                /* margin-bottom: 16px; */ /* Removido para controlar o espaço com o aviso */
                box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
                transition: transform 0.2s ease;
                min-height: 120px; /* Garante altura mínima para o card */
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .ocupacao-card-custom:hover {
                transform: scale(1.01);
            }

            .progress-card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .progress-card-title {
                font-size: 1rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .progress-card-value {
                font-size: 1.4rem;
                font-weight: 700;
            }

            /* --- CORREÇÃO DE ALTURA DA BARRA --- */
            .progress-bar-container {
                width: 100%;
                height: 18px; /* <<< ALTURA AUMENTADA */
                background-color: #3A3A4A;
                border-radius: 8px;
                overflow: hidden;
                margin-bottom: 10px;
            }
            .ocupacao-card-custom .progress-bar-fill {
                height: 18px; /* <<< ALTURA CORRIGIDA (igual ao container) */
                background: linear-gradient(90deg, #7C3AED, #8B5CF6); /* Roxo para Truck */
                border-radius: 8px;
            }
            .ocupacao-card-cavalo .progress-bar-fill {
                height: 18px; /* <<< ALTURA CORRIGIDA (igual ao container) */
                background: linear-gradient(90deg, #F97316, #FB923C); /* Laranja para Carreta */
                border-radius: 8px;
            }

            .progress-card-footer {
                display: flex;
                justify-content: space-between;
                font-size: 0.9rem;
                color: #d1d1d1;
            }

            /* --- NOVO ESTILO PARA O AVISO DE OCIOSIDADE --- */
            .aviso-ociosidade {
                background-color:#1E1E2E;
                border-left: 5px solid #facc15;
                padding: 12px 20px;
                border-radius: 8px;
                margin-top: 10px;
                margin-bottom: 20px;
                color:#e4e4e7;
                font-size: 0.95rem;
            }
        </style>
        """, unsafe_allow_html=True)



        # --- TÍTULO MODERNIZADO ---
        st.markdown("""
            <div class="title-block-modern">
                <i class="fa-solid fa-scale-balanced"></i>
                <h2>Análise de Ocupação de Carga por Tipo de Veículo</h2>
            </div>
        """, unsafe_allow_html=True)


        # ===============================================
        # 🧭 OPTION MENU DE SELEÇÃO DE FROTA (LÓGICA ATUALIZADA)
        # ===============================================

        # Define um valor padrão inicial
        frota_default = "AMBAS"

        # --- INÍCIO DA NOVA LÓGICA ---
        # 1. VERIFICA SE UMA PLACA ESPECÍFICA FOI SELECIONADA NA SIDEBAR
        if placa_sel != "(Todos)":
            # Encontra o tipo de veículo para a placa selecionada
            tipo_veiculo_da_placa = df_original[df_original['PLACA_CAVALO'] == placa_sel]['TIPO_CAVALO'].iloc[0]
            
            if tipo_veiculo_da_placa == 'TRUCK':
                frota_default = "FROTA TRUCK"
            elif tipo_veiculo_da_placa == 'CAVALO':
                frota_default = "FROTA CARRETA"

        # 2. SE NENHUMA PLACA FOI SELECIONADA, USA A LÓGICA DA ROTA (como antes)
        elif rota_sel_visivel != "(Todos)":
            tipos_encontrados = df_filtrado['TIPO_CAVALO'].dropna().unique()
            tipos_upper = [t.upper() for t in tipos_encontrados]

            if "TRUCK" in tipos_upper and "CAVALO" in tipos_upper:
                frota_default = "AMBAS"
            elif "TRUCK" in tipos_upper:
                frota_default = "FROTA TRUCK"
            elif "CAVALO" in tipos_upper:
                frota_default = "FROTA CARRETA"

        # --- NOVO SELECTOR DE FROTA (Glass Style Modernizado) ---
        selecionar_frota = option_menu(
            menu_title=None,
            options=["FROTA TRUCK", "FROTA CARRETA", "AMBAS"],
            icons=["truck-moving", "trailer", "layer-group"],
            menu_icon="cast",
            default_index=["FROTA TRUCK", "FROTA CARRETA", "AMBAS"].index(frota_default),
            orientation="horizontal",
            styles={
                # 🔹 Container principal (fundo translúcido com leve blur)
                "container": {
                    "padding": "6px",
                    "background-color": "rgba(30, 30, 40, 0.4)",
                    "border-radius": "16px",
                    "backdrop-filter": "blur(10px)",
                    "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.3)",
                    "justify-content": "center",
                },
                # 🔹 Ícones
                "icon": {
                    "color": "#A3A3A3",
                    "font-size": "18px",
                },
                # 🔹 Botões inativos
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "600",
                    "color": "#E5E7EB",
                    "padding": "10px 26px",
                    "border-radius": "12px",
                    "margin": "0px 6px",
                    "background-color": "rgba(255, 255, 255, 0.05)",
                    "transition": "all 0.3s ease-in-out",
                },
                # 🔹 Efeito hover
                "nav-link:hover": {
                    "background-color": "rgba(255,255,255,0.12)",
                    "color": "#fff",
                    "transform": "translateY(-2px)",
                },
                # 🔹 Botão selecionado — gradiente verde + brilho
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                    "color": "white",
                    "box-shadow": "0 0 10px rgba(34,197,94,0.5)",
                    "transform": "translateY(-2px)",
                },
            },
        )

        # ===============================================
        # LÓGICA ORIGINAL (reutilizada)
        # ===============================================
        if rota_sel_visivel == "(Todos)":

            capacidades_por_tipo = {
                'TRUCK':  {'peso_kg': 16000, 'volume_m3': 75},
                'CAVALO': {'peso_kg': 25000, 'volume_m3': 110},
                'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
            }

            def calcular_dados_ocupacao(tipo_veiculo, df_dados):
                df_tipo = df_dados[df_dados['TIPO_CAVALO'].fillna('').astype(str).str.upper() == tipo_veiculo]
                if df_tipo.empty:
                    return None

                capacidade = capacidades_por_tipo.get(tipo_veiculo, capacidades_por_tipo['PADRAO'])
                num_viagens = df_tipo.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroups
                if num_viagens == 0:
                    return None

                dados = {}
                dados['cap_total_peso'] = num_viagens * capacidade['peso_kg']
                dados['total_peso'] = df_tipo['PESO REAL (KG)'].sum()
                dados['ocup_peso_perc'] = (dados['total_peso'] / dados['cap_total_peso'] * 100) if dados['cap_total_peso'] > 0 else 0

                dados['cap_total_volume'] = num_viagens * capacidade['volume_m3']
                dados['total_volume'] = df_tipo['M3'].sum() if 'M3' in df_tipo.columns else 0
                if dados['total_volume'] > 1000:
                    dados['total_volume'] /= 10000
                dados['ocup_volume_perc'] = (dados['total_volume'] / dados['cap_total_volume'] * 100) if dados['cap_total_volume'] > 0 else 0

                return dados

            dados_truck = calcular_dados_ocupacao('TRUCK', df_filtrado)
            dados_carreta = calcular_dados_ocupacao('CAVALO', df_filtrado)

            if selecionar_frota == "FROTA TRUCK":
                if dados_truck:
                    
                    col1, col2 = st.columns([1, 1], gap="large")

                    # --- Card e Aviso de Ociosidade de PESO ---
                    with col1:
                        # Card de Ocupação de Peso
                        st.markdown(f"""
                        <div class="ocupacao-card-custom"> 
                            <div class="progress-card-header">
                                <div class="progress-card-title">⚖️ Ocupação de Peso (KG)</div>
                                <div class="progress-card-value">{dados_truck['ocup_peso_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {min(dados_truck['ocup_peso_perc'], 100)}%;"></div>
                            </div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_truck['total_peso'])} KG</span>
                                <span>Capacidade: {formatar_numero(dados_truck['cap_total_peso'])} KG</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Aviso de Ociosidade de Peso (com mais margem superior)
                        ociosidade_peso = 100 - dados_truck['ocup_peso_perc']
                        st.markdown(f"""
                        <div style="
                            background-color:#1E1E2E;
                            border-left: 5px solid #facc15;
                            padding: 12px 20px;
                            border-radius: 8px;
                            margin-top: 5px; /* <<< ALTERADO AQUI */
                            color:#e4e4e7;
                            font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Peso:</b> <b>{ociosidade_peso:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

                    # --- Card e Aviso de Ociosidade de CUBAGEM ---
                    with col2:
                        # Card de Ocupação de Cubagem
                        st.markdown(f"""
                        <div class="ocupacao-card-custom">
                            <div class="progress-card-header">
                                <div class="progress-card-title">📦 Ocupação de Cubagem (M³)</div>
                                <div class="progress-card-value">{dados_truck['ocup_volume_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {min(dados_truck['ocup_volume_perc'], 100)}%;"></div>
                            </div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_truck['total_volume'], 3)} M³</span>
                                <span>Capacidade: {formatar_numero(dados_truck['cap_total_volume'])} M³</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Aviso de Ociosidade de Cubagem (com mais margem superior)
                        ociosidade_volume = 100 - dados_truck['ocup_volume_perc']
                        st.markdown(f"""
                        <div style="
                            background-color:#1E1E2E;
                            border-left: 5px solid #facc15;
                            padding: 12px 20px;
                            border-radius: 8px;
                            margin-top: 5px; /* <<< ALTERADO AQUI */
                            color:#e4e4e7;
                            font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Cubagem (M³):</b> <b>{ociosidade_volume:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

            elif selecionar_frota == "FROTA CARRETA":
                if dados_carreta:
                    
                    col1, col2 = st.columns([1, 1], gap="large")

                    with col1:
                        st.markdown(f"""
                        <div class="ocupacao-card-custom ocupacao-card-cavalo"> 
                            <div class="progress-card-header">
                                <div class="progress-card-title">⚖️ Ocupação de Peso (KG)</div>
                                <div class="progress-card-value">{dados_carreta['ocup_peso_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {min(dados_carreta['ocup_peso_perc'], 100)}%;"></div></div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_carreta['total_peso'])} KG</span>
                                <span>Capacidade: {formatar_numero(dados_carreta['cap_total_peso'])} KG</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        ociosidade_peso_carreta = 100 - dados_carreta['ocup_peso_perc']
                        st.markdown(f"""
                        <div style="
                            background-color:#1E1E2E;
                            border-left: 5px solid #facc15;
                            padding: 12px 20px;
                            border-radius: 8px;
                            margin-top: 5px; /* <<< AJUSTADO PARA 5PX */
                            color:#e4e4e7;
                            font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Peso:</b> <b>{ociosidade_peso_carreta:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="ocupacao-card-custom ocupacao-card-cavalo">
                            <div class="progress-card-header">
                                <div class="progress-card-title">📦 Ocupação de Cubagem (M³)</div>
                                <div class="progress-card-value">{dados_carreta['ocup_volume_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {min(dados_carreta['ocup_volume_perc'], 100)}%;"></div></div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_carreta['total_volume'], 3)} M³</span>
                                <span>Capacidade: {formatar_numero(dados_carreta['cap_total_volume'])} M³</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        ociosidade_volume_carreta = 100 - dados_carreta['ocup_volume_perc']
                        st.markdown(f"""
                        <div style="
                            background-color:#1E1E2E;
                            border-left: 5px solid #facc15;
                            padding: 12px 20px;
                            border-radius: 8px;
                            margin-top: 5px; /* <<< AJUSTADO PARA 5PX */
                            color:#e4e4e7;
                            font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Cubagem (M³):</b> <b>{ociosidade_volume_carreta:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

            elif selecionar_frota == "AMBAS":
                # --- Cria duas colunas principais para dividir as frotas ---
                col_truck, col_carreta = st.columns(2, gap="large")

                # --- COLUNA DA ESQUERDA: FROTA TRUCK ---
                with col_truck:
                    if dados_truck:
                        st.markdown("<div class='frota-title'><i class='fa-solid fa-truck-moving'></i> FROTA TRUCK</div>", unsafe_allow_html=True)
                        
                        # Card de Peso (Truck)
                        st.markdown(f"""
                        <div class="ocupacao-card-custom"> 
                            <div class="progress-card-header">
                                <div class="progress-card-title">⚖️ Ocupação de Peso (KG)</div>
                                <div class="progress-card-value">{dados_truck['ocup_peso_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {min(dados_truck['ocup_peso_perc'], 100)}%;"></div>
                            </div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_truck['total_peso'])} KG</span>
                                <span>Capacidade: {formatar_numero(dados_truck['cap_total_peso'])} KG</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Aviso de Ociosidade de Peso (Truck)
                        ociosidade_peso = 100 - dados_truck['ocup_peso_perc']
                        st.markdown(f"""
                        <div style="background-color:#1E1E2E; border-left: 5px solid #facc15; padding: 12px 20px; border-radius: 8px; margin-top: 5px; color:#e4e4e7; font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Peso:</b> <b>{ociosidade_peso:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

                        # Espaçamento vertical entre as seções
                        st.markdown("<br>", unsafe_allow_html=True)

                        # Card de Cubagem (Truck)
                        st.markdown(f"""
                        <div class="ocupacao-card-custom">
                            <div class="progress-card-header">
                                <div class="progress-card-title">📦 Ocupação de Cubagem (M³)</div>
                                <div class="progress-card-value">{dados_truck['ocup_volume_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {min(dados_truck['ocup_volume_perc'], 100)}%;"></div>
                            </div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_truck['total_volume'], 3)} M³</span>
                                <span>Capacidade: {formatar_numero(dados_truck['cap_total_volume'])} M³</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Aviso de Ociosidade de Cubagem (Truck)
                        ociosidade_volume = 100 - dados_truck['ocup_volume_perc']
                        st.markdown(f"""
                        <div style="background-color:#1E1E2E; border-left: 5px solid #facc15; padding: 12px 20px; border-radius: 8px; margin-top: 5px; color:#e4e4e7; font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Cubagem (M³):</b> <b>{ociosidade_volume:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='frota-title'><i class='fa-solid fa-truck-moving'></i> FROTA TRUCK</div>", unsafe_allow_html=True)
                        st.info("Nenhum dado de Truck encontrado para o período.")

                # --- COLUNA DA DIREITA: FROTA CARRETA ---
                with col_carreta:
                    if dados_carreta:
                        st.markdown("<div class='frota-title'><i class='fa-solid fa-trailer'></i> FROTA CARRETA</div>", unsafe_allow_html=True)
                        
                        # Card de Peso (Carreta)
                        st.markdown(f"""
                        <div class="ocupacao-card-custom ocupacao-card-cavalo"> 
                            <div class="progress-card-header">
                                <div class="progress-card-title">⚖️ Ocupação de Peso (KG)</div>
                                <div class="progress-card-value">{dados_carreta['ocup_peso_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {min(dados_carreta['ocup_peso_perc'], 100)}%;"></div></div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_carreta['total_peso'])} KG</span>
                                <span>Capacidade: {formatar_numero(dados_carreta['cap_total_peso'])} KG</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Aviso de Ociosidade de Peso (Carreta)
                        ociosidade_peso_carreta = 100 - dados_carreta['ocup_peso_perc']
                        st.markdown(f"""
                        <div style="background-color:#1E1E2E; border-left: 5px solid #facc15; padding: 12px 20px; border-radius: 8px; margin-top: 5px; color:#e4e4e7; font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Peso:</b> <b>{ociosidade_peso_carreta:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

                        # Espaçamento vertical entre as seções
                        st.markdown("<br>", unsafe_allow_html=True)

                        # Card de Cubagem (Carreta)
                        st.markdown(f"""
                        <div class="ocupacao-card-custom ocupacao-card-cavalo">
                            <div class="progress-card-header">
                                <div class="progress-card-title">📦 Ocupação de Cubagem (M³)</div>
                                <div class="progress-card-value">{dados_carreta['ocup_volume_perc']:.1f}%</div>
                            </div>
                            <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {min(dados_carreta['ocup_volume_perc'], 100)}%;"></div></div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_carreta['total_volume'], 3)} M³</span>
                                <span>Capacidade: {formatar_numero(dados_carreta['cap_total_volume'])} M³</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Aviso de Ociosidade de Cubagem (Carreta)
                        ociosidade_volume_carreta = 100 - dados_carreta['ocup_volume_perc']
                        st.markdown(f"""
                        <div style="background-color:#1E1E2E; border-left: 5px solid #facc15; padding: 12px 20px; border-radius: 8px; margin-top: 5px; color:#e4e4e7; font-size: 0.95rem;">
                            ⚠️ <b>Ociosidade de Cubagem (M³):</b> <b>{ociosidade_volume_carreta:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='frota-title'><i class='fa-solid fa-trailer'></i> FROTA CARRETA</div>", unsafe_allow_html=True)
                        st.info("Nenhum dado de Carreta encontrado para o período.")

        # Substitua o bloco "else:" do modo de viagem única por este:
        else:
            # --- MODO VIAGEM ÚNICA (lógica existente com novo visual) ---
            ocupacao_peso_perc = (peso_total / capacidade_peso_kg) * 100 if capacidade_peso_kg > 0 else 0
            ociosidade_peso = 100 - ocupacao_peso_perc
            ocupacao_volume_perc = (volume_total_m3 / capacidade_volume_m3) * 100 if capacidade_volume_m3 > 0 else 0
            ociosidade_volume = 100 - ocupacao_volume_perc

            barra_peso = min(ocupacao_peso_perc, 100)
            barra_volume = min(ocupacao_volume_perc, 100)

            col1, col2 = st.columns(2)
            with col1:
                # Card de Ocupação de Peso (sem alterações)
                st.markdown(f"""
                <div class="ocupacao-card-custom"> 
                    <div class="progress-card-header">
                        <div class="progress-card-title">⚖️ Peso KG</div>
                        <div class="progress-card-value">{ocupacao_peso_perc:.1f}%</div>
                    </div>
                    <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {barra_peso}%;"></div></div>
                    <div class="progress-card-footer">
                        <span>{formatar_numero(peso_total)} KG</span>
                        <span>Capacidade: {formatar_numero(capacidade_peso_kg)} KG</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                # ▼▼▼ NOVO AVISO DE OCIOSIDADE DE PESO ▼▼▼
                st.markdown(f"""
                <div style="
                    background-color:#1E1E2E;
                    border-left: 5px solid #facc15; /* Borda amarela à esquerda */
                    padding: 12px 20px;
                    border-radius: 8px;
                    margin-top: 10px; /* Espaço acima do aviso */
                    color:#e4e4e7;
                    font-size: 0.95rem;">
                    ⚠️ <b>Ociosidade de Peso:</b> {ociosidade_peso:.1f}%
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Card de Ocupação de Cubagem (sem alterações)
                st.markdown(f"""
                <div class="ocupacao-card-custom">
                    <div class="progress-card-header">
                        <div class="progress-card-title">📦 Cubagem M³</div>
                        <div class="progress-card-value">{ocupacao_volume_perc:.1f}%</div>
                    </div>
                    <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {barra_volume}%;"></div></div>
                    <div class="progress-card-footer">
                        <span>{formatar_numero(volume_total_m3, 3)} M³</span>
                        <span>Capacidade: {formatar_numero(capacidade_volume_m3)} M³</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                # ▼▼▼ NOVO AVISO DE OCIOSIDADE DE CUBAGEM ▼▼▼
                st.markdown(f"""
                <div style="
                    background-color:#1E1E2E;
                    border-left: 5px solid #facc15; /* Borda amarela à esquerda */
                    padding: 12px 20px;
                    border-radius: 8px;
                    margin-top: 10px; /* Espaço acima do aviso */
                    color:#e4e4e7;
                    font-size: 0.95rem;">
                    ⚠️ <b>Ociosidade de Cubagem (M³):</b> {ociosidade_volume:.1f}%
                </div>
                """, unsafe_allow_html=True)         

        st.divider()


        # ==============================
        # 8. TABELA RESUMIDA E DETALHES DA VIAGEM
        # ==============================
        st.subheader("📋 Resumo das Viagens no Período")

        # --- LÓGICA DE FILTRO DA FROTA (igual à anterior) ---
        df_para_tabela = df_filtrado.copy()
        if rota_sel_visivel == "(Todos)":
            if selecionar_frota == "FROTA TRUCK":
                df_para_tabela = df_para_tabela[df_para_tabela['TIPO_CAVALO'].str.upper() == 'TRUCK']
            elif selecionar_frota == "FROTA CARRETA":
                df_para_tabela = df_para_tabela[df_para_tabela['TIPO_CAVALO'].str.upper() == 'CAVALO']
        
        df_viagens = df_para_tabela.copy()

        # --- INÍCIO DO BLOCO PRINCIPAL (TABELA UNIFICADA) ---
        if not df_viagens.empty:
            # Garante que a coluna de identificação da viagem exista
            if 'VIAGEM_ID' not in df_viagens.columns:
                df_viagens['VIAGEM_ID'] = df_viagens.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup() + 1
            
            def juntar_unicos(series):
                # Junta os valores únicos da série, removendo NAs e convertendo para string
                return ', '.join(series.dropna().astype(str).unique())

            # Corrige o valor de M3 antes de agrupar
            if "M3" in df_viagens.columns:
                # Cria uma cópia para evitar SettingWithCopyWarning
                df_viagens = df_viagens.copy()
                df_viagens["M3"] = df_viagens["M3"].astype(float) / 10000

            # Agrupamento para criar a tabela unificada
            resumo_viagens = df_viagens.groupby('VIAGEM_ID').agg(
                EMISSÃO=('EMIS_MANIF', 'first'),
                NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                SITUACAO=('SITUACAO', 'first'), # <<< ADICIONADO AQUI PARA PEGAR A SITUAÇÃO
                MOTORISTA=('MOTORISTA', 'first'),
                PLACA=('PLACA_CAVALO', 'first'),
                TIPO_VEICULO=('TIPO_CAVALO', 'first'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS_TOTAL=('OS-R$', 'max'),
                CUSTO_CTRB_TOTAL=('CTRB-R$', 'max'),
                FRETE_TOTAL=('FRETE-R$', 'sum'),
                NUM_OS_LISTA=('NUM_OS', juntar_unicos),
                NUM_CTRB_LISTA=('NUM_CTRB', juntar_unicos),
                ICMS=('ICMS-R$', 'sum'),
                PESO_KG=('PESO REAL (KG)', 'sum'),
                M3=('M3', 'sum'),
                VOLUMES=('VOLUMES', 'sum'),
                VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                ENTREGAS=('DEST_MANIF', 'nunique'),
                QTDE_CTRC=('QTDE_CTRC', 'sum')
            ).reset_index()

            # Renomeia colunas para processamento
            resumo_viagens.rename(columns={
                'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 'PLACA': 'PLACA_CAVALO',
                'TIPO_VEICULO': 'TIPO_CAVALO', 'DESTINOS': 'DEST_MANIF',
                'PROPRIETARIO': 'PROPRIETARIO_CAVALO', 'CUSTO_OS_TOTAL': 'OS-R$',
                'CUSTO_CTRB_TOTAL': 'CTRB-R$', 'FRETE_TOTAL': 'FRETE-R$',
                'NUM_OS_LISTA': 'NUM_OS', 'NUM_CTRB_LISTA': 'NUM_CTRB',
                'ICMS': 'ICMS-R$', 'PESO_KG': 'PESO REAL (KG)',
                'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
            }, inplace=True)

            # Funções de cálculo para as colunas finais
            def calcular_custo_final(row):
                custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                destinos_str = str(row.get('DEST_MANIF', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base

            def obter_numero_documento(row):
                return row['NUM_OS'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['NUM_CTRB']

            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_final, axis=1)
            resumo_viagens['Nº Documento Custo'] = resumo_viagens.apply(obter_numero_documento, axis=1)

            def calcular_ctrb_frete_numerico(row):
                try:
                    custo = float(row['Custo (CTRB/OS)'])
                    frete = float(row['FRETE-R$'])
                    return (custo / frete) * 100 if frete > 0 else 0.0
                except (ValueError, TypeError):
                    return 0.0

            resumo_viagens['CTRB/Frete (%)_valor'] = resumo_viagens.apply(calcular_ctrb_frete_numerico, axis=1)
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.1f}%".replace(".", ","))

            # Formatação final para exibição
            resumo_viagens['EMIS_MANIF'] = pd.to_datetime(resumo_viagens['EMIS_MANIF']).dt.strftime('%d/%m/%Y')
            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens['Custo (CTRB/OS)'].astype(float).apply(formatar_moeda)
            resumo_viagens['FRETE-R$'] = resumo_viagens['FRETE-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['ICMS-R$'] = resumo_viagens['ICMS-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['MERCADORIA-R$'] = resumo_viagens['MERCADORIA-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['PESO REAL (KG)'] = resumo_viagens['PESO REAL (KG)'].astype(float).apply(lambda x: formatar_numero(x, 2) + ' kg')
            resumo_viagens['M3'] = resumo_viagens['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))
            resumo_viagens['VOLUMES'] = resumo_viagens['VOLUMES'].astype(int)
            resumo_viagens['ENTREGAS'] = resumo_viagens['ENTREGAS'].astype(int)
            resumo_viagens['QTDE_CTRC'] = resumo_viagens['QTDE_CTRC'].astype(int)

            resumo_viagens.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'PLACA_CAVALO': 'PLACA',
                'TIPO_CAVALO': 'TIPO', 'DEST_MANIF': 'DESTINOS', 'Nº Documento Custo': 'Nº CTRB/OS',
                'QTDE_CTRC': 'Qtd. CTRCs',
                'SITUACAO': 'SITUAÇÃO' # <<< RENOMEADO AQUI
            }, inplace=True)

            # Define a ordem final, com a SITUAÇÃO após o Manifesto
            ordem_final = [
                'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUAÇÃO', 'MOTORISTA', 'DESTINOS', 'ENTREGAS', # <<< ORDEM AJUSTADA AQUI
                'PLACA', 'TIPO', 'Nº CTRB/OS', 'Custo (CTRB/OS)', 'CTRB/Frete (%)', 'FRETE-R$',
                'ICMS-R$', 'PESO REAL (KG)', 'M3', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
            ]
            colunas_para_exibir = [col for col in ordem_final if col in resumo_viagens.columns]

            df_para_exibir = resumo_viagens[colunas_para_exibir].copy()
            styled_df = df_para_exibir.style.background_gradient(cmap='Reds', subset=['CTRB/Frete (%)'], gmap=resumo_viagens['CTRB/Frete (%)_valor'])
            
            # --- EXIBIÇÃO DA TABELA UNIFICADA ---
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # --- BOTÃO DE DOWNLOAD DA TABELA UNIFICADA (ESTILO ATUALIZADO) ---
            try:
                excel_bytes_resumo = to_excel(resumo_viagens)
                st.download_button(
                    label="📥 Download Resumo (Excel)", # Ícone e texto atualizados
                    data=excel_bytes_resumo,
                    file_name="resumo_viagens_filtradas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_resumo" # Chave única para este botão
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel para o resumo: {e}")

        
        # A tabela detalhada só aparece se uma rota específica for selecionada.
        if rota_sel_visivel != "(Todos)":
            st.divider() 
            st.subheader("📄 Detalhes dos Documentos da Viagem")

            # 1. Define as colunas desejadas, incluindo a nova coluna 'SITUACAO'
            colunas_detalhadas = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'NUM_CTRB', 'CTRB-R$', 'NUM_OS', 'OS-R$', 'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            
            # 2. Filtra o df_filtrado para as colunas existentes
            colunas_existentes_det = [col for col in colunas_detalhadas if col in df_filtrado.columns]
            df_detalhado = df_filtrado[colunas_existentes_det].copy()

            # 3. Renomeia as colunas para exibição
            df_detalhado.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 
                'NUM_MANIF': 'Nº Manifesto',
                'SITUACAO': 'SITUAÇÃO', # <<< COLUNA ADICIONADA AQUI
                'DEST_MANIF': 'Destino',
                'PLACA_CAVALO': 'PLACA', 
                'TIPO_CAVALO': 'TIPO', 
                'NUM_CTRB': 'Nº CTRB',
                'NUM_OS': 'Nº OS', 
                'CTRB-R$': 'Custo CTRB', 
                'OS-R$': 'Custo OS', 
                'QTDE_CTRC': 'Qtd. CTRCs'
            }, inplace=True)

            # 4. Formata as colunas para exibição (nenhuma mudança aqui)
            df_detalhado['EMISSÃO'] = pd.to_datetime(df_detalhado['EMISSÃO']).dt.strftime('%d/%m/%Y')
            
            colunas_moeda_det = ['Custo CTRB', 'Custo OS', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado.columns:
                    df_detalhado[col] = df_detalhado[col].apply(formatar_moeda)
            
            if 'PESO REAL (KG)' in df_detalhado.columns:
                df_detalhado['PESO REAL (KG)'] = df_detalhado['PESO REAL (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            
            if 'M3' in df_detalhado.columns:
                 df_detalhado['M3'] = (df_detalhado['M3'].astype(float) / 10000).apply(lambda x: formatar_numero(x, 3))

            # 5. Exibe a tabela detalhada
            st.dataframe(df_detalhado, use_container_width=True, hide_index=True)
            
            # 6. Botão de download para os dados detalhados
            try:
                excel_bytes_detalhado = to_excel(df_detalhado)
                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=f"detalhes_viagem_{rota_sel_visivel.split(' ')[1]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel detalhado: {e}")
        # --- ▲▲▲ FIM DO BLOCO ATUALIZADO ▲▲▲ ---

# --- ABA 2: ANÁLISE FINANCEIRA ---
with tab2:
    st.header("📈 Análise Financeira")
    st.info("Conteúdo da análise financeira será implementado aqui.")

# --- ABA 3: PERFORMANCE DA FROTA ---
with tab3:
    st.header("⚡ Performance da Frota")
    st.info("Conteúdo da análise de performance será implementado aqui.")


# Substitua a seção "with tab4:" inteira pelo código abaixo

with tab4:

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # -----------------------------
        # 1️⃣ PREPARAÇÃO DE DADOS E KPIs (sem alterações)
        # -----------------------------
        df_aux = df_filtrado.copy()
        df_aux["DATA_EMISSAO"] = df_aux["EMIS_MANIF"].dt.date
        df_aux["VIAGEM_ID"] = df_aux.groupby(["MOTORISTA", "PLACA_CAVALO", "DATA_EMISSAO"], sort=False).ngroup() + 1

        capacidades = {
            'TOCO': {'peso_kg': 10000, 'volume_m3': 55}, 'TRUCK': {'peso_kg': 16000, 'volume_m3': 75},
            'CAVALO': {'peso_kg': 25000, 'volume_m3': 110}, 'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
        }
        df_aux['CAPACIDADE_PESO'] = df_aux['TIPO_CAVALO'].map(lambda x: capacidades.get(str(x).upper(), capacidades['PADRAO'])['peso_kg'])
        df_aux["CUSTO_POR_LINHA"] = df_aux.apply(lambda r: r["CTRB-R$"] if r.get("PROPRIETARIO_CAVALO") == "KM TRANSPORTES ROD. DE CARGAS LTDA" else r.get("OS-R$"), axis=1)
        
        resumo_por_viagem = df_aux.groupby('VIAGEM_ID').agg(
            MOTORISTA=('MOTORISTA', 'first'), FRETE_VIAGEM=('FRETE-R$', 'sum'),
            CUSTO_UNICO_VIAGEM=('CUSTO_POR_LINHA', 'max'), PESO_VIAGEM=('PESO REAL (KG)', 'sum'),
            ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'), CAPACIDADE_PESO_VIAGEM=('CAPACIDADE_PESO', 'first'),
            DISTANCIA_ESTIMADA=('DISTANCIA_ESTIMADA_KM', 'first')
        ).reset_index()

        resumo_motorista = resumo_por_viagem.groupby('MOTORISTA').agg(
            TOTAL_VIAGENS=('VIAGEM_ID', 'nunique'), FRETE_TOTAL=('FRETE_VIAGEM', 'sum'),
            CUSTO_OS_CTRB_TOTAL=('CUSTO_UNICO_VIAGEM', 'sum'), PESO_TOTAL=('PESO_VIAGEM', 'sum'),
            TOTAL_ENTREGAS=('ENTREGAS_VIAGEM', 'sum'), CAPACIDADE_TOTAL_PESO=('CAPACIDADE_PESO_VIAGEM', 'sum'),
            DISTANCIA_TOTAL=('DISTANCIA_ESTIMADA', 'sum')
        ).reset_index()

        resumo_motorista["DISTANCIA_MEDIA_VIAGEM"] = (resumo_motorista["DISTANCIA_TOTAL"] / resumo_motorista["TOTAL_VIAGENS"]).fillna(0)
        resumo_motorista["MEDIA_ENTREGAS_VIAGEM"] = (resumo_motorista["TOTAL_ENTREGAS"] / resumo_motorista["TOTAL_VIAGENS"]).fillna(0)
        resumo_motorista["PESO_MEDIO_VIAGEM"] = (resumo_motorista["PESO_TOTAL"] / resumo_motorista["TOTAL_VIAGENS"]).fillna(0)
        resumo_motorista["OCUPACAO_MEDIA_CARGA"] = (resumo_motorista["PESO_TOTAL"] / resumo_motorista["CAPACIDADE_TOTAL_PESO"] * 100).fillna(0)
        resumo_motorista["PERC_CUSTO_FRETE"] = (resumo_motorista["CUSTO_OS_CTRB_TOTAL"] / resumo_motorista["FRETE_TOTAL"] * 100).fillna(0)

        if motorista_sel != "(Todos)" and motorista_sel in resumo_motorista["MOTORISTA"].values:
            df_motorista = df_aux[df_aux["MOTORISTA"] == motorista_sel]
            dados_m = resumo_motorista[resumo_motorista["MOTORISTA"] == motorista_sel].iloc[0]
        else:
            df_motorista = df_aux.copy()
            dados_m = pd.Series({
                "TOTAL_VIAGENS": resumo_motorista["TOTAL_VIAGENS"].sum(), "TOTAL_ENTREGAS": resumo_motorista["TOTAL_ENTREGAS"].sum(),
                "DISTANCIA_MEDIA_VIAGEM": resumo_motorista["DISTANCIA_TOTAL"].sum() / resumo_motorista["TOTAL_VIAGENS"].sum() if resumo_motorista["TOTAL_VIAGENS"].sum() > 0 else 0,
                "MEDIA_ENTREGAS_VIAGEM": resumo_motorista["TOTAL_ENTREGAS"].sum() / resumo_motorista["TOTAL_VIAGENS"].sum() if resumo_motorista["TOTAL_VIAGENS"].sum() > 0 else 0,
                "PESO_MEDIO_VIAGEM": resumo_motorista["PESO_TOTAL"].sum() / resumo_motorista["TOTAL_VIAGENS"].sum() if resumo_motorista["TOTAL_VIAGENS"].sum() > 0 else 0,
                "OCUPACAO_MEDIA_CARGA": resumo_motorista["PESO_TOTAL"].sum() / resumo_motorista["CAPACIDADE_TOTAL_PESO"].sum() * 100 if resumo_motorista["CAPACIDADE_TOTAL_PESO"].sum() > 0 else 0,
                "PERC_CUSTO_FRETE": resumo_motorista["CUSTO_OS_CTRB_TOTAL"].sum() / resumo_motorista["FRETE_TOTAL"].sum() * 100 if resumo_motorista["FRETE_TOTAL"].sum() > 0 else 0,
            })

        # --- BLOCO DE IDENTIFICAÇÃO DO MOTORISTA (ATUALIZADO) ---
        if motorista_sel != "(Todos)":
            st.markdown("### <i class='fa-solid fa-id-card-clip'></i> Identificação do Motorista", unsafe_allow_html=True)
            
            # Inicializa as variáveis para o caso de o dataframe estar vazio
            placa_frequente, tipo_veiculo_frequente, destino_frequente, ultima_viagem_data = "N/A", "N/A", "N/A", "N/A"
            capacidade_kg_frequente = 0

            if not df_motorista.empty:
                placa_frequente = df_motorista['PLACA_CAVALO'].mode()[0]
                tipo_veiculo_frequente = df_motorista['TIPO_CAVALO'].mode()[0]
                destino_frequente = df_motorista['CIDADE_UF_DEST'].mode()[0]
                ultima_viagem_data = df_motorista['EMIS_MANIF'].max().strftime('%d/%m/%Y')
                
                # ▼▼▼ BUSCA A CAPACIDADE CORRESPONDENTE AO TIPO DE VEÍCULO ▼▼▼
                capacidade_info = capacidades.get(str(tipo_veiculo_frequente).upper(), capacidades['PADRAO'])
                capacidade_kg_frequente = capacidade_info['peso_kg']

            # Layout com 5 colunas
            id1, id2, id3, id4, id5 = st.columns(5)
            
            with id1:
                partes_nome = motorista_sel.split()
                nome_formatado = f"{partes_nome[0]} {partes_nome[1]}" if len(partes_nome) > 1 else motorista_sel
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-user-tie'></i> Motorista</div><div class='kpi-value'>{nome_formatado}</div></div>", unsafe_allow_html=True)
            
            with id2:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-truck'></i> Veículo Frequente</div><div class='kpi-value'>{placa_frequente}</div></div>", unsafe_allow_html=True)
            
                        # ▼▼▼ KPI CORRIGIDO PARA FICAR NA MESMA LINHA ▼▼▼
            with id3:
                # Formata a capacidade para exibição (ex: "Cap. 16.000 kg")
                capacidade_formatada = f"Cap. {formatar_numero(capacidade_kg_frequente)} kg"
                
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: center;'>
                        <div class='kpi-title'><i class='fa-solid fa-gear'></i> Tipo / Capacidade</div>
                        <div class='kpi-value'>
                            {tipo_veiculo_frequente}<br>
                            <span style='font-size: 16px; color: #d1d5db; font-weight: 500;'>{capacidade_formatada}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


            with id4:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-map-location-dot'></i> Destino Frequente</div><div class='kpi-value'>{destino_frequente}</div></div>", unsafe_allow_html=True)
            
            with id5:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-calendar-days'></i> Última Viagem</div><div class='kpi-value'>{ultima_viagem_data}</div></div>", unsafe_allow_html=True)
            
            st.divider()

        # ... (Restante do código da tab4 permanece o mesmo) ...
        st.markdown("### 🎯 Indicadores de Desempenho Operacional")
        def fmt_num(v, suf=""): return f"{v:,.0f}{suf}".replace(",", ".")
        def fmt_perc(v): return f"{v:.1f}%".replace(".", ",")
        kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
        kpis_operacionais = {
            kpi1: {"titulo": "🚛 Total de Viagens", "valor": fmt_num(dados_m["TOTAL_VIAGENS"])},
            kpi2: {"titulo": "🗺️ Distância Média", "valor": fmt_num(dados_m["DISTANCIA_MEDIA_VIAGEM"], " km")},
            kpi3: {"titulo": "<i class='fa-solid fa-dolly'></i> Total de Entregas", "valor": fmt_num(dados_m["TOTAL_ENTREGAS"])},
            kpi4: {"titulo": "⚖️ Peso Médio / Viagem", "valor": fmt_num(dados_m["PESO_MEDIO_VIAGEM"], " kg")},
            kpi5: {"titulo": "📈 Ocupação Média", "valor": fmt_perc(dados_m["OCUPACAO_MEDIA_CARGA"])},
            kpi6: {"titulo": "📊 % Custo / Frete", "valor": fmt_perc(dados_m["PERC_CUSTO_FRETE"])},
        }
        for coluna, info in kpis_operacionais.items():
            with coluna: st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'>{info['titulo']}</div><div class='kpi-value'>{info['valor']}</div></div>", unsafe_allow_html=True)
        st.divider()

        if motorista_sel != "(Todos)":
            st.markdown(f"### 📋 Resumo das Viagens 👨‍✈️{motorista_sel}")
        else:
            st.markdown("### 📋 Resumo de Todas as Viagens no Período")

        df_agrupado = df_motorista.copy()
        resumo_viagens = df_agrupado.groupby('VIAGEM_ID').agg(
            EMISSÃO=('EMIS_MANIF', 'first'), PLACA=('PLACA_CAVALO', 'first'), TIPO=('TIPO_CAVALO', 'first'),
            MOTORISTA=('MOTORISTA', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
            FRETE=('FRETE-R$', 'sum'), CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
            PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), ICMS=('ICMS-R$', 'sum'), PESO_KG=('PESO REAL (KG)', 'sum'),
            M3=('M3', 'sum'), VOLUMES=('VOLUMES', 'sum'), VALOR_MERC=('MERCADORIA-R$', 'sum'),
            ENTREGAS=('DEST_MANIF', 'nunique'), QTDE_CTRC=('QTDE_CTRC', 'sum')
        ).reset_index()

        def calcular_custo_viagem(row):
            return row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']

        resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_viagem, axis=1)
        resumo_viagens['CTRB/Frete (%)'] = ((resumo_viagens['Custo (CTRB/OS)'] / resumo_viagens['FRETE']) * 100).fillna(0)
        
        def calcular_distancia_por_viagem(row):
            tipo_veiculo = str(row.get('TIPO', 'PADRAO')).upper()
            valor_por_km = custo_km_por_tipo.get(tipo_veiculo, 0)
            custo_da_viagem = row['Custo (CTRB/OS)']
            return (custo_da_viagem / valor_por_km) if valor_por_km > 0 and custo_da_viagem > 0 else 0

        resumo_viagens['Distância (KM)'] = resumo_viagens.apply(calcular_distancia_por_viagem, axis=1)
        def corrigir_volume_numerico(valor):
            try:
                valor_float = float(valor)
                return valor_float / 10000 if valor_float > 1000 else valor_float
            except (ValueError, TypeError): return 0.0
        resumo_viagens['M3_corrigido'] = resumo_viagens['M3'].apply(corrigir_volume_numerico)

        resumo_viagens.rename(columns={
            'VIAGEM_ID': '🧭 Viagem', 'TIPO': 'Tipo Veículo', 'DESTINOS': 'Destinos da Rota', 'PESO_KG': 'Peso Total',
            'M3_corrigido': 'Volume Total (M³)', 'VOLUMES': 'Volumes Totais', 'VALOR_MERC': 'Valor Mercadoria', 'QTDE_CTRC': 'Qtd. CTRCs'
        }, inplace=True)

        ordem_final_renomeada = [
            '🧭 Viagem', 'EMISSÃO', 'PLACA', 'Tipo Veículo', 'Destinos da Rota', 'MOTORISTA', 'Distância (KM)',
            'ENTREGAS', 'Custo (CTRB/OS)', 'CTRB/Frete (%)', 'FRETE', 'ICMS', 'Peso Total',
            'Volume Total (M³)', 'Qtd. CTRCs', 'Volumes Totais', 'Valor Mercadoria'
        ]
        colunas_para_exibir_e_exportar = [col for col in ordem_final_renomeada if col in resumo_viagens.columns]
        df_para_exportar = resumo_viagens[colunas_para_exibir_e_exportar].copy()

        if 'EMISSÃO' in resumo_viagens.columns: resumo_viagens['EMISSÃO'] = resumo_viagens['EMISSÃO'].dt.strftime('%d/%m/%Y')
        resumo_viagens['Distância (KM)'] = resumo_viagens['Distância (KM)'].apply(lambda x: f"{int(x)} km")
        if 'Volume Total (M³)' in resumo_viagens.columns:
            resumo_viagens['Volume Total (M³)'] = resumo_viagens['Volume Total (M³)'].apply(lambda x: f"{x:,.3f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(resumo_viagens[colunas_para_exibir_e_exportar], use_container_width=True, hide_index=True)
        
        excel_bytes = to_excel(df_para_exportar)
        st.download_button(
            label="📤 Exportar Resumo para Excel", data=excel_bytes,
            file_name=f"resumo_viagens_{motorista_sel.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if motorista_sel != "(Todos)":
            st.divider() 
            st.subheader("📄 Detalhes dos Documentos da Viagem")

            df_detalhado = df_motorista.copy()
            colunas_detalhadas = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'NUM_CTRB', 'CTRB-R$', 'NUM_OS', 'OS-R$', 'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            colunas_existentes_det = [col for col in colunas_detalhadas if col in df_detalhado.columns]
            df_detalhado = df_detalhado[colunas_existentes_det]

            df_detalhado.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino', 'PLACA_CAVALO': 'PLACA', 'TIPO_CAVALO': 'TIPO',
                'NUM_CTRB': 'Nº CTRB', 'NUM_OS': 'Nº OS', 'CTRB-R$': 'Custo CTRB',
                'OS-R$': 'Custo OS', 'QTDE_CTRC': 'Qtd. CTRCs'
            }, inplace=True)

            df_detalhado['EMISSÃO'] = pd.to_datetime(df_detalhado['EMISSÃO']).dt.strftime('%d/%m/%Y')
            colunas_moeda_det = ['Custo CTRB', 'Custo OS', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado.columns: df_detalhado[col] = df_detalhado[col].apply(formatar_moeda)
            if 'PESO REAL (KG)' in df_detalhado.columns:
                df_detalhado['PESO REAL (KG)'] = df_detalhado['PESO REAL (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            if 'M3' in df_detalhado.columns:
                df_detalhado['M3'] = (df_detalhado['M3'].astype(float) / 10000).apply(lambda x: formatar_numero(x, 3))

            st.dataframe(df_detalhado, use_container_width=True, hide_index=True)
            
            try:
                excel_bytes_detalhado = to_excel(df_detalhado)
                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=f"detalhes_motorista_{motorista_sel.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado_motorista"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel detalhado: {e}")




    # --- ABA 5: ANÁLISE DE ROTAS ---
with tab5:
    st.header("📋 Análise de Rotas")

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # ------------------------------------
        # 1. ANÁLISE DAS PARADAS POR CIDADE (FORMATO KPI)
        # ------------------------------------
        df_paradas = df_filtrado.copy()

        # ✅ Mostra detalhes apenas se uma rota específica for selecionada
        if rota_sel_visivel == "(Todos)":
            st.markdown("### 🏙️ Detalhes das Paradas")
            st.info("🗺️ Selecione uma rota específica para visualizar as cidades e seus indicadores.")
        else:
            if not df_paradas.empty:
                # Título da seção
                st.markdown(f"### 🏙️ Detalhes das Paradas")

                # --- CSS (sem alterações, pode manter o seu) ---
                st.markdown("""
                <style>
                /* ... seu CSS existente para os cards ... */
                .stop-card-v2 {
                    background: linear-gradient(145deg, #23273c, #1a1d2e);
                    border-radius: 16px;
                    padding: 24px;
                    border: 1px solid #3a4063;
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                    margin-bottom: 1rem;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    transition: all 0.3s ease;
                }
                .stop-card-v2:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 12px 35px rgba(59, 130, 246, 0.2);
                    border-color: #3b82f6;
                }
                .stop-card-v2-title {
                    font-size: 1.2rem;
                    font-weight: 700;
                    color: #ffffff;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .stop-card-v2-title .fa-map-pin { color: #ef4444; }
                .stop-card-v2-metrics {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                    flex-grow: 1;
                }
                .stop-card-v2-metric {
                    background-color: rgba(17, 24, 39, 0.5);
                    padding: 12px;
                    border-radius: 10px;
                    border: 1px solid #374151;
                }
                .stop-card-v2-metric-label {
                    font-size: 0.8rem;
                    color: #9ca3af;
                    margin-bottom: 4px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                .stop-card-v2-metric-value {
                    font-size: 1.1rem;
                    font-weight: 600;
                    color: #ffffff;
                }
                /* Ícones */
                .fa-weight-hanging { color: #f97316; }
                .fa-boxes-stacked { color: #3b82f6; }
                .fa-cube { color: #14b8a6; }
                .fa-file-invoice { color: #8b5cf6; }
                .fa-box-open { color: #f59e0b; }
                .fa-hand-holding-dollar { color: #22c55e; }
                </style>
                """, unsafe_allow_html=True)

                # Agrega os dados por cidade
                carga_por_cidade = df_paradas.groupby('CIDADE_UF_DEST').agg(
                    PESO_TOTAL=('PESO REAL (KG)', 'sum'),
                    VOLUME_TOTAL=('M3', 'sum'),
                    VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                    QTDE_CTRC=('QTDE_CTRC', 'sum'),
                    VOLUMES_TOTAL=('VOLUMES', 'sum'),
                    FRETE_TOTAL=('FRETE-R$', 'sum')
                ).reset_index()

                # Lógica de ordenação (mantida)
                if 'Destinos' in rotas_df.columns:
                    try:
                        destinos_str = rotas_df.loc[rotas_df['NOME_ROTA'] == rota_sel_visivel, 'Destinos'].iloc[0]
                        destinos_ordenados_siglas = destinos_str.split(' - ')
                        mapa_ordem_siglas = {sigla: i for i, sigla in enumerate(destinos_ordenados_siglas)}
                        mapa_cidade_para_sigla = (
                            df_paradas.drop_duplicates(subset=['CIDADE_UF_DEST'])
                            [['CIDADE_UF_DEST', 'DEST_MANIF']]
                            .set_index('CIDADE_UF_DEST')['DEST_MANIF']
                        )
                        carga_por_cidade['sigla'] = carga_por_cidade['CIDADE_UF_DEST'].map(mapa_cidade_para_sigla)
                        carga_por_cidade['ordem'] = carga_por_cidade['sigla'].map(mapa_ordem_siglas)
                        carga_por_cidade = carga_por_cidade.sort_values('ordem', ascending=True).reset_index(drop=True)
                    except Exception as e:
                        st.warning(f"⚠️ Não foi possível aplicar a ordem da rota. Erro: {e}")

                if not carga_por_cidade.empty:
                    # Funções de formatação
                    def fmt_moeda(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    def fmt_num(v): return f"{v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    def fmt_m3(v): return f"{v:,.1f}".replace(".", ",")

                    # --- INÍCIO DA LÓGICA DE LAYOUT MODIFICADA ---
                    num_cidades = len(carga_por_cidade)
                    
                    # Define o número de colunas por linha (máximo de 3, ou 2 se houver 4 cidades)
                    cols_per_row = 2 if num_cidades == 4 else min(3, num_cidades)

                    # Itera sobre as cidades em "pedaços" (chunks) do tamanho de cols_per_row
                    for i in range(0, num_cidades, cols_per_row):
                        # Cria uma nova linha de colunas para cada "pedaço"
                        cols = st.columns(cols_per_row)
                        
                        # Pega o subconjunto de cidades para esta linha
                        cidades_na_linha = carga_por_cidade.iloc[i : i + cols_per_row]

                        # Itera sobre as cidades e colunas desta linha
                        for col_index, row in enumerate(cidades_na_linha.itertuples()):
                            with cols[col_index]:
                                st.markdown(f"""
                                <div class="stop-card-v2">
                                    <div class="stop-card-v2-title">
                                        <i class="fa-solid fa-map-pin"></i> {row.CIDADE_UF_DEST}
                                    </div>
                                    <div class="stop-card-v2-metrics">
                                        <div class="stop-card-v2-metric">
                                            <div class="stop-card-v2-metric-label"><i class="fa-solid fa-weight-hanging"></i> Peso</div>
                                            <div class="stop-card-v2-metric-value">{fmt_num(row.PESO_TOTAL)} kg</div>
                                        </div>
                                        <div class="stop-card-v2-metric">
                                            <div class="stop-card-v2-metric-label"><i class="fa-solid fa-cube"></i> Volume</div>
                                            <div class="stop-card-v2-metric-value">{fmt_m3(row.VOLUME_TOTAL)} M³</div>
                                        </div>
                                        <div class="stop-card-v2-metric">
                                            <div class="stop-card-v2-metric-label"><i class="fa-solid fa-boxes-stacked"></i> Volumes</div>
                                            <div class="stop-card-v2-metric-value">{fmt_num(row.VOLUMES_TOTAL)}</div>
                                        </div>
                                        <div class="stop-card-v2-metric">
                                            <div class="stop-card-v2-metric-label"><i class="fa-solid fa-file-invoice"></i> CTRCs</div>
                                            <div class="stop-card-v2-metric-value">{fmt_num(row.QTDE_CTRC)}</div>
                                        </div>
                                        <div class="stop-card-v2-metric">
                                            <div class="stop-card-v2-metric-label"><i class="fa-solid fa-box-open"></i> Mercadoria</div>
                                            <div class="stop-card-v2-metric-value">{fmt_moeda(row.VALOR_MERCADORIA)}</div>
                                        </div>
                                        <div class="stop-card-v2-metric">
                                            <div class="stop-card-v2-metric-label"><i class="fa-solid fa-hand-holding-dollar"></i> Frete</div>
                                            <div class="stop-card-v2-metric-value">{fmt_moeda(row.FRETE_TOTAL)}</div>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    # --- FIM DA LÓGICA DE LAYOUT MODIFICADA ---
                else:
                    st.info("Nenhuma parada registrada para os filtros selecionados.")

                st.divider()

            # ------------------------------------
            # 8️⃣ ANÁLISE DE OCUPAÇÃO DA ROTA (NOVO FORMATO VISUAL)
            # ------------------------------------
            st.markdown("##### ⚖️ Ocupação da Carga na Rota")

            # --- CSS para os cards e o novo texto de ociosidade ---
            st.markdown("""
            <style>
            .occupancy-card {
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #374151;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                margin-bottom: 0.5rem;
                transition: all 0.3s ease;

                /* ▼▼▼ CONTROLE DE ALTURA E ALINHAMENTO ADICIONADO AQUI ▼▼▼ */
                min-height: 150px;      /* <--- AJUSTE ESTE VALOR PARA CONTROLAR A ALTURA */
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .occupancy-card:hover {
                transform: translateY(-2px);
                border-color: #4f46e5;
            }
            .occupancy-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }
            .occupancy-title {
                font-size: 1rem;
                font-weight: 600;
                color: #d1d5db;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .occupancy-percentage {
                font-size: 1.5rem;
                font-weight: 700;
                color: #a78bfa;
            }
            .occupancy-progress-bar-container {
                width: 100%;
                background-color: #374151;
                border-radius: 8px;
                height: 10px;
                overflow: hidden;
            }
            .occupancy-progress-bar-fill {
                height: 100%;
                border-radius: 8px;
                background: linear-gradient(90deg, #4f46e5 0%, #a78bfa 100%);
                transition: width 0.5s ease-in-out;
            }
            .occupancy-footer {
                display: flex;
                justify-content: space-between;
                margin-top: 8px;
                font-size: 0.8rem;
                color: #FFFFFF;
            }
            .ociosidade-text {
                font-size: 0.9rem;
                color: #FFFFFF;
                padding: 0 10px;
            }
            </style>
            """, unsafe_allow_html=True)

            # 1. Lógica de cálculo (sem alterações)
            peso_total_motorista = df_motorista['PESO REAL (KG)'].sum()
            volume_total_motorista = df_motorista['M3'].sum()

            if not df_motorista['TIPO_CAVALO'].empty and df_motorista['TIPO_CAVALO'].mode().any():
                tipo_veiculo_frequente = df_motorista['TIPO_CAVALO'].mode()[0]
            else:
                tipo_veiculo_frequente = 'PADRAO'

            capacidades = {
                'TOCO': {'peso_kg': 10000, 'volume_m3': 55},
                'TRUCK': {'peso_kg': 16000, 'volume_m3': 75},
                'CAVALO': {'peso_kg': 45000, 'volume_m3': 110},
                'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
            }
            capacidade_veiculo = capacidades.get(str(tipo_veiculo_frequente).upper(), capacidades['PADRAO'])
            capacidade_peso_kg = capacidade_veiculo['peso_kg']
            capacidade_volume_m3 = capacidade_veiculo['volume_m3']

            ocupacao_peso_perc = (peso_total_motorista / capacidade_peso_kg * 100) if capacidade_peso_kg > 0 else 0
            ociosidade_peso_perc = 100 - ocupacao_peso_perc
            peso_livre = capacidade_peso_kg - peso_total_motorista

            volume_corrigido = volume_total_motorista / 1000 if volume_total_motorista > 1000 else volume_total_motorista
            ocupacao_volume_perc = (volume_corrigido / capacidade_volume_m3 * 100) if capacidade_volume_m3 > 0 else 0
            ociosidade_volume_perc = 100 - ocupacao_volume_perc
            volume_livre = capacidade_volume_m3 - volume_corrigido

            ocupacao_peso_barra = min(ocupacao_peso_perc, 100)
            ocupacao_volume_barra = min(ocupacao_volume_perc, 100)

            # 2. Layout com colunas para os cards
            col_card1, col_card2 = st.columns(2)

            with col_card1:
                if peso_total_motorista > 0:
                    st.markdown(f"""
                    <div class="occupancy-card">
                        <div class="occupancy-header">
                            <div class="occupancy-title">⚖️ Peso KG</div>
                            <div class="occupancy-percentage">{ocupacao_peso_perc:.1f}%</div>
                        </div>
                        <div class="occupancy-progress-bar-container">
                            <div class="occupancy-progress-bar-fill" style="width: {ocupacao_peso_barra}%;"></div>
                        </div>
                        <div class="occupancy-footer">
                            <span>{fmt_num(peso_total_motorista)} KG</span>
                            <span>Capacidade: {fmt_num(capacidade_peso_kg)} KG</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_card2:
                if volume_corrigido > 0:
                    st.markdown(f"""
                    <div class="occupancy-card">
                        <div class="occupancy-header">
                            <div class="occupancy-title">📦 Cubagem M³</div>
                            <div class="occupancy-percentage">{ocupacao_volume_perc:.1f}%</div>
                        </div>
                        <div class="occupancy-progress-bar-container">
                            <div class="occupancy-progress-bar-fill" style="width: {ocupacao_volume_barra}%;"></div>
                        </div>
                        <div class="occupancy-footer">
                            <span>{fmt_m3(volume_corrigido)} M³</span>
                            <span>Capacidade: {fmt_num(capacidade_volume_m3)} M³</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 3. Layout com colunas para os textos de ociosidade
            col_ocio1, col_ocio2 = st.columns(2)

            with col_ocio1:
                if peso_total_motorista > 0:
                    st.markdown(f"""
                    <div class="ociosidade-text">
                        ⚖️ Ociosidade de Peso: {ociosidade_peso_perc:.1f}% ({fmt_num(peso_livre)} KG livres)
                    </div>
                    """, unsafe_allow_html=True)

            with col_ocio2:
                if volume_corrigido > 0:
                    st.markdown(f"""
                    <div class="ociosidade-text">
                        📦 Ociosidade de Volume: {ociosidade_volume_perc:.1f}% ({fmt_m3(volume_livre)} M³ livres)
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
    
        if df_filtrado.empty:
            st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
        else:
            # ==============================
            # MAPA DA ROTA (COM TRAÇADO CONDICIONAL E MARCADORES OTIMIZADOS)
            # ==============================
            st.subheader("🗺️ Trajeto da Viagem")

            # Função para obter a geometria da rota (o traçado) do serviço OSRM
            def obter_geometria_rota(pontos_da_rota):
                """
                Busca o traçado da rota entre uma lista de coordenadas usando o serviço OSRM.
                Retorna uma lista de coordenadas [lat, lon] para a PolyLine e a distância em km.
                """
                if len(pontos_da_rota) < 2:
                    return None, 0
                
                coordenadas_str = ";".join([f"{lon},{lat}" for lat, lon in pontos_da_rota])
                url = f"http://router.project-osrm.org/route/v1/driving/{coordenadas_str}?overview=full&geometries=polyline"
                
                try:
                    resposta = requests.get(url, timeout=15 )
                    resposta.raise_for_status()
                    dados_rota = resposta.json()
                    geometria_codificada = dados_rota['routes'][0]['geometry']
                    distancia_metros = dados_rota['routes'][0]['distance']
                    tracado_rota = polyline.decode(geometria_codificada)
                    distancia_km = round(distancia_metros / 1000)
                    return tracado_rota, distancia_km
                except (requests.exceptions.RequestException, KeyError, IndexError) as e:
                    st.warning(f"Não foi possível obter o traçado da rota. Erro: {e}")
                    return None, 0

            # Dicionário de locais com coordenadas
            locais = {
                "KM Transportes - Campo Grande": [-20.50461, -54.56829], "CAMPO GRANDE/MS": [-20.50461, -54.56829],
                "AGUA CLARA/MS": [-20.4486, -52.8783], "ANASTACIO/MS": [-20.4953, -55.8089], "COXIM/MS": [-18.5134, -54.7406],
                "APARECIDA DO TABOADO/MS": [-20.0867, -51.0933], "BATAGUASSU/MS": [-21.715, -52.4225],
                "BODOQUENA/MS": [-20.5507, -56.67928], "BONITO/MS": [-21.1236, -56.4934], "CAMAPUA/MS": [-19.5349, -54.0432],
                "CASSILANDIA/MS": [-19.1133, -51.7339], "CHAPADAO DO SUL/MS": [-18.7955, -52.6012],
                "CORUMBA/MS": [-19.0205, -57.6578], "COSTA RICA/MS": [-18.5432, -53.1292], "DOURADOS/MS": [-22.2204, -54.7360],
                "GOIANIA/GO": [-16.6869, -49.2648], "IVINHEMA/MS": [-22.3067, -53.8153], "JARDIM/MS": [-21.4803, -56.1381],
                "MARACAJU/MS": [-21.6147, -55.1683], "MIRANDA/MS": [-20.2363, -56.3812], "NIOAQUE/MS": [-21.1576, -55.8446],
                "NOVA ALVORADA DO SUL/MS": [-21.4631, -54.3844], "NOVA ANDRADINA/MS": [-22.235, -53.3433],
                "PARANAIBA/MS": [-19.6834, -51.1968], "PARAISO DAS AGUAS/MS": [-19.0202, -53.0094],
                "PEDRO GOMES/MS": [-18.1011, -54.5525], "PONTA PORA/MS": [-22.5609, -55.6945],
                "RIBAS DO RIO PARDO/MS": [-20.4433, -53.7592], "RIO BRILHANTE/MS": [-21.8036, -54.5456],
                "RIO VERDE DE MATO GROSSO/MS": [-18.9181, -54.8453], "SAO GABRIEL DO OESTE/MS": [-19.395, -54.56],
                "SAO PAULO/SP": [-23.5183, -46.5729], "SIDROLANDIA/MS": [-20.9319, -54.9603], "SONORA/MS": [-17.5736, -54.7558],
                "TERENOS/MS": [-20.4428, -55.7597], "TRES LAGOAS/MS": [-20.7519, -51.6783],
            }
            
            # Pega a origem e os destinos únicos do DataFrame já filtrado
            origem_nome = df_filtrado['CIDADE_UF_ORIGEM'].iloc[0] if not df_filtrado.empty else None
            destinos_unicos = df_filtrado['CIDADE_UF_DEST'].dropna().unique()

            # Monta a lista de coordenadas para os marcadores
            pontos_marcadores = []
            if origem_nome and origem_nome in locais:
                pontos_marcadores.append(locais[origem_nome])
            
            # Usa a ordem geográfica definida anteriormente
            ordem_geografica_cidades = {
                'PARAISO DAS AGUAS/MS': 1, 'CHAPADAO DO SUL/MS': 2, 'GOIANIA/GO': 3,
            }
            destinos_ordenados = sorted(destinos_unicos, key=lambda d: ordem_geografica_cidades.get(d, 99))

            for dest in destinos_ordenados:
                if dest in locais and locais[dest] not in pontos_marcadores:
                    pontos_marcadores.append(locais[dest])

            # Define um ponto inicial para o mapa (será sobreposto pelo fit_bounds)
            ponto_inicial_mapa = [-15.78, -47.88] # Brasília

            # Cria o mapa base
            m = folium.Map(location=ponto_inicial_mapa, zoom_start=4, tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google', name='Google Maps - Ruas'  )
            
            # --- MELHORIA ADICIONADA AQUI ---
            # Garante que o mapa sempre comece focado no Brasil
            m.fit_bounds([[-33.75, -73.99], [5.27, -32.39]])

            folium.TileLayer('https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', attr='Google', name='Google Maps - Satélite'  ).add_to(m)
            folium.TileLayer('openstreetmap', name="OpenStreetMap").add_to(m)

            # Verifica se os dados filtrados se referem a uma única viagem
            e_viagem_unica = df_filtrado['PLACA_CAVALO'].nunique() == 1 and df_filtrado['DIA_EMISSAO_STR'].nunique() == 1

            if e_viagem_unica:
                tracado_da_rota, distancia_total_km = obter_geometria_rota(pontos_marcadores)
                if tracado_da_rota:
                    folium.PolyLine(
                        locations=tracado_da_rota,
                        color='#3b82f6', weight=5, opacity=0.8,
                        tooltip=f"Distância da Rota: {distancia_total_km} km"
                    ).add_to(m)
                    # Ajusta o zoom para a rota específica, sobrepondo o zoom geral do Brasil
                    m.fit_bounds(folium.PolyLine(locations=tracado_da_rota).get_bounds())
            elif pontos_marcadores:
                # Se houver múltiplos pontos (mas não uma rota única), ajusta o zoom para eles
                if len(pontos_marcadores) > 1:
                    m.fit_bounds(pontos_marcadores)

            # Adiciona marcador para a ORIGEM
            if origem_nome and origem_nome in locais:
                folium.Marker(
                    location=locais[origem_nome],
                    popup=f"<strong>Origem: {origem_nome}</strong>",
                    tooltip="Ponto de Partida",
                    icon=folium.Icon(color='blue', icon='home', prefix='fa')
                ).add_to(m)

            # Adiciona marcadores para cada DESTINO
            for dest in destinos_unicos:
                if dest in locais and dest != origem_nome:
                    folium.Marker(
                        location=locais[dest],
                        popup=f"<strong>Destino: {dest}</strong>",
                        tooltip=dest,
                        icon=folium.Icon(color='red', icon='truck', prefix='fa')
                    ).add_to(m)

            folium.LayerControl().add_to(m)
            st_folium(m, use_container_width=True, height=700)


        st.divider()

        # ==============================
        # TABELA DE DADOS FILTRADOS (COM LÓGICA DE CUSTO DINÂMICO)
        # ==============================
        st.subheader("📊 Dados das Viagens")

        # 1. Define a lista de colunas desejadas, incluindo as necessárias para a lógica
        colunas_desejadas = [
            'NUM_MANIF', 'DEST_MANIF', 'PLACA_CAVALO', 'MOTORISTA', 'FRETE-R$', 'M3',
            'PESO REAL (KG)', 'MERCADORIA-R$', 'VOLUMES', 'QTDE_CTRC',
            # Colunas necessárias para a lógica de custo:
            'PROPRIETARIO_CAVALO', 'NUM_CTRB', 'CTRB-R$', 'NUM_OS', 'OS-R$'
        ]

        # 2. Filtra o DataFrame para conter apenas as colunas existentes
        colunas_para_exibir = [col for col in colunas_desejadas if col in df_filtrado.columns]
        df_tabela_selecionada = df_filtrado[colunas_para_exibir]

        # 3. Cria uma cópia do DataFrame para aplicar a formatação e novas colunas
        df_formatado = df_tabela_selecionada.copy()

        # --- INÍCIO DA NOVA LÓGICA DE CUSTO ---
        # 4. Funções para determinar o custo e o número do documento
        def calcular_custo_final(row):
            # Verifica se a coluna 'PROPRIETARIO_CAVALO' existe
            if 'PROPRIETARIO_CAVALO' in row and row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                return row.get('OS-R$', 0) # Usa .get() para segurança
            return row.get('CTRB-R$', 0)

        def obter_numero_documento(row):
            if 'PROPRIETARIO_CAVALO' in row and row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                return row.get('NUM_OS', '')
            return row.get('NUM_CTRB', '')

        # 5. Aplica as funções para criar as novas colunas unificadas
        df_formatado['Custo (CTRB/OS)'] = df_formatado.apply(calcular_custo_final, axis=1)
        df_formatado['Nº CTRB/OS'] = df_formatado.apply(obter_numero_documento, axis=1)
        # --- FIM DA NOVA LÓGICA DE CUSTO ---

        # 6. Define as funções de formatação no padrão brasileiro
        def formatar_moeda_br(valor):
            try:
                return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                return "R$ 0,00"

        def formatar_peso_br(valor):
            try:
                return f"{valor:,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                return "0,00 kg"

        # 7. Aplica a formatação nas colunas específicas
        colunas_moeda = ['FRETE-R$', 'MERCADORIA-R$', 'Custo (CTRB/OS)'] # Adicionada a nova coluna de custo
        for col in colunas_moeda:
            if col in df_formatado.columns:
                df_formatado[col] = df_formatado[col].apply(formatar_moeda_br)

        if 'PESO REAL (KG)' in df_formatado.columns:
            df_formatado['PESO REAL (KG)'] = df_formatado['PESO REAL (KG)'].apply(formatar_peso_br)

        # 8. Define a ordem final das colunas para exibição
        ordem_final_tabela = [
            'NUM_MANIF', 'DEST_MANIF', 'PLACA_CAVALO', 'MOTORISTA', 'FRETE-R$',
            'Nº CTRB/OS', 'Custo (CTRB/OS)', # Novas colunas unificadas
            'M3', 'PESO REAL (KG)', 'MERCADORIA-R$', 'VOLUMES', 'QTDE_CTRC'
        ]

        # Filtra a ordem final para garantir que todas as colunas existem no df_formatado
        colunas_finais_para_exibir = [col for col in ordem_final_tabela if col in df_formatado.columns]

        # 9. Exibe a tabela com os dados formatados e as colunas corretas
        st.dataframe(df_formatado[colunas_finais_para_exibir], use_container_width=True, hide_index=True)

        # --- BOTÃO PARA DOWNLOAD DOS DADOS FILTRADOS (ESTILO PADRÃO) ---
        try:
            # O DataFrame a ser exportado aqui é o 'df_formatado'
            excel_bytes_rotas = to_excel(df_formatado)
            
            st.download_button(
                label="📥 Download Dados da Rota (Excel)",
                data=excel_bytes_rotas,
                file_name="dados_rota_detalhada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_rota" # Chave única para este botão
            )

        except Exception as e:
            st.error(f"❌ Erro ao gerar o arquivo Excel: {e}")
