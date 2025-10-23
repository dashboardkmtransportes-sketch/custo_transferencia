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
        /* Sombra 1: Brilho azul | Sombra 2: Sombra escura para profundidade */
        box-shadow: 0 0 15px rgba(74, 144, 226, 0.5), 0 8px 25px rgba(0, 0, 0, 0.3);
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
            
    /* ▼▼▼ NOVO ESTILO PARA O TÍTULO DA ABA DE MOTORISTAS ▼▼▼ */
    .title-block-motoristas {
        background: #1C1A29; /* Fundo escuro */
        
        /* Bordas laterais na cor roxa para combinar com a aba */
        border-left: 5px solid #8b5cf6;
        border-right: 5px solid #8b5cf6;
        
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-motoristas h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .title-block-motoristas .fa-bullseye {
        font-size: 2.0rem; /* Tamanho do ícone */
        color: #8b5cf6;   /* Cor do ícone (roxo) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            

    /* ▼▼▼ NOVO ESTILO PARA O TÍTULO DA ABA DE ROTAS ▼▼▼ */
    .title-block-rotas {
        background: #1C1A29; /* Fundo escuro */
        
        /* Bordas laterais na cor vermelha para combinar com a aba */
        border-left: 5px solid #ef4444;
        border-right: 5px solid #ef4444;
        
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-rotas h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .title-block-rotas .fa-route {
        font-size: 2.0rem; /* Tamanho do ícone */
        color: #ef4444;   /* Cor do ícone (vermelho) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            

    /* ▼▼▼ ESTILO CORRIGIDO PARA O TÍTULO DA ABA FINANCEIRA ▼▼▼ */
    .title-block-financeira {
        background: #1C1A29;
        border-left: 5px solid #22c55e; /* Borda verde */
        border-right: 5px solid #22c55e; /* Borda verde */
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-financeira h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Regra genérica para QUALQUER ícone dentro deste bloco de título */
    .title-block-financeira i {
        font-size: 2.0rem;
        color: #22c55e;   /* Cor do ícone (VERDE) */
    }
    /* ▲▲▲ FIM DO ESTILO CORRIGIDO ▲▲▲ */
            
    /* ▼▼▼ ADICIONE ESTE NOVO ESTILO PARA O TÍTULO DE PERFORMANCE ▼▼▼ */
    .title-block-performance {
        background: #1C1A29;
        
        /* Bordas laterais para combinar com a aba de Performance (Laranja) */
        border-left: 5px solid #f97316;
        border-right: 5px solid #f97316;
        
        padding: 5px 30px;
        margin: 20px 0 25px 0; /* Aumenta a margem superior para dar espaço */
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-performance h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Ícone específico para este bloco de título */
    .title-block-performance .fa-chart-line {
        font-size: 2.0rem;
        color: #f97316;   /* Cor do ícone (Laranja) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            
    /* ▼▼▼ ESTILO ATUALIZADO PARA TÍTULOS DE SEÇÃO MODERNOS ▼▼▼ */
    .section-title-modern {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.5rem; /* Aumentei um pouco para mais destaque */
        font-weight: 700;  /* <<< PRINCIPAL MUDANÇA AQUI: de 600 para 700 (bold) */
        color: #FFFFFF;    /* Cor branca pura para mais contraste */
        margin-top: 25px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: 0.5px; /* Adiciona um leve espaçamento entre as letras */
    }
    /* ▲▲▲ FIM DO ESTILO ATUALIZADO ▲▲▲ */

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
            
    # Garante que as colunas de texto sejam do tipo string
    for col_texto in ['LACRES', 'SITUACAO']:
        if col_texto in df.columns:
            df[col_texto] = df[col_texto].astype(str)
            
    return df

@st.cache_data
def carregar_capacidades(caminho_capacidades):
    """Carrega os dados de capacidade, convertendo toneladas para KG."""
    try:
        df_caps = pd.read_excel(caminho_capacidades)
        
        # 1. Limpa os nomes das colunas
        df_caps.columns = df_caps.columns.str.strip().str.upper()
        
        # 2. Encontra a coluna de placa
        coluna_placa_encontrada = None
        nomes_placa_possiveis = ['PLACA_CARRETA', 'PLACA'] 
        for nome in nomes_placa_possiveis:
            if nome in df_caps.columns:
                coluna_placa_encontrada = nome
                break 
        
        if not coluna_placa_encontrada:
            raise KeyError(f"Nenhuma coluna de PLACA encontrada. Colunas disponíveis: {list(df_caps.columns)}")

        # 3. Encontra a coluna de capacidade
        coluna_capacidade_encontrada = None
        nomes_capacidade_possiveis = ['CAPACIDADE_KG', 'CAPACIDADE', 'PESO', 'CAPACIDADE (KG)'] 
        for nome in nomes_capacidade_possiveis:
            if nome in df_caps.columns:
                coluna_capacidade_encontrada = nome
                break

        if not coluna_capacidade_encontrada:
            raise KeyError(f"Nenhuma coluna de CAPACIDADE encontrada. Colunas disponíveis: {list(df_caps.columns)}")

        # --- ▼▼▼ A MÁGICA ACONTECE AQUI ▼▼▼ ---
        # 4. Converte o valor da capacidade de Toneladas para KG
        #    Garante que o valor seja numérico antes de multiplicar
        df_caps[coluna_capacidade_encontrada] = pd.to_numeric(df_caps[coluna_capacidade_encontrada], errors='coerce').fillna(0) * 1000
        # --- ▲▲▲ FIM DA MUDANÇA ▲▲▲ ---

        # 5. Renomeia as colunas para o padrão do script
        df_caps.rename(columns={
            coluna_placa_encontrada: 'PLACA_CARRETA',
            coluna_capacidade_encontrada: 'CAPACIDADE_KG'
        }, inplace=True)

        # Garante que a coluna da placa seja do tipo texto para a junção
        df_caps['PLACA_CARRETA'] = df_caps['PLACA_CARRETA'].astype(str)
        return df_caps

    except FileNotFoundError:
        st.error(f"❌ **Erro: O arquivo de capacidades '{caminho_capacidades}' não foi encontrado.**")
        return pd.DataFrame()
    except KeyError as e: 
        st.error(f"❌ **Erro de Coluna no arquivo 'cadastro_veiculos.xlsx':** {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro inesperado ao ler o arquivo de capacidades: {e}")
        return pd.DataFrame()


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


# ▼▼▼ INÍCIO DA NOVA LÓGICA DE CAPACIDADE ▼▼▼

# 1. Carrega o arquivo com as capacidades dos veículos
caminho_capacidades = os.path.join("data", "cadastro_veiculos.xlsx") 
df_capacidades = carregar_capacidades(caminho_capacidades)

# 2. Junta (merge) o DataFrame de viagens com o de capacidades da CARRETA
if not df_capacidades.empty:
    df_original = pd.merge(
        df_original,
        df_capacidades[['PLACA_CARRETA', 'CAPACIDADE_KG']],
        on='PLACA_CARRETA',
        how='left'
    )
    df_original['CAPACIDADE_KG'].fillna(25000, inplace=True)
else:
    df_original['CAPACIDADE_KG'] = 25000
    st.warning("⚠️ Arquivo de cadastro de veículos não encontrado para CARRETA. Usando capacidade padrão de 25.000 kg.")

# ▲▲▲ FIM DA NOVA LÓGICA DE CAPACIDADE ▲▲▲


# --- ### INÍCIO DA CORREÇÃO DEFINITIVA ### ---
# 3. CRIA A COLUNA 'CAPAC_CAVALO' NO ESCOPO GLOBAL

if not df_capacidades.empty:
    # Prepara o DataFrame de capacidades para a junção com a placa do cavalo
    df_capacidades_cavalo = df_capacidades.rename(columns={'PLACA_CARRETA': 'PLACA_CAVALO', 'CAPACIDADE_KG': 'CAPAC_CAVALO'})
    
    # Junta o df_original com as capacidades do cavalo
    df_original = pd.merge(
        df_original,
        df_capacidades_cavalo[['PLACA_CAVALO', 'CAPAC_CAVALO']],
        on='PLACA_CAVALO',
        how='left'
    )
    # Preenche com 0 ou um valor padrão se o cavalo/truck não for encontrado no cadastro
    df_original['CAPAC_CAVALO'].fillna(0, inplace=True)
else:
    # Se o arquivo de cadastro não existir, cria a coluna com valor 0
    df_original['CAPAC_CAVALO'] = 0
    st.warning("⚠️ Arquivo de cadastro de veículos não encontrado para CAVALO/TRUCK. Capacidade definida como 0.")
# --- ### FIM DA CORREÇÃO DEFINITIVA ### ---


# ▼▼▼ ADICIONE O NOVO CÓDIGO AQUI ▼▼▼
# (O resto do seu código continua a partir daqui)


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

# --- GARANTE A EXISTÊNCIA DA COLUNA DIA_EMISSAO_STR ---
if 'EMIS_MANIF' in df_original.columns:
    df_original['DIA_EMISSAO_STR'] = df_original['EMIS_MANIF'].dt.strftime('%d/%m/%Y')
else:
    df_original['DIA_EMISSAO_STR'] = ''
# --- FIM DO AJUSTE ---

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

# --- INÍCIO DA CORREÇÃO ---
# Adiciona a coluna SOMENTE se o DataFrame não estiver vazio para evitar o ValueError
if not df_filtrado.empty:
    df_filtrado.loc[:, 'DISTANCIA_ESTIMADA_KM'] = distancia_estimada_km
else:
    # Se o DataFrame estiver vazio, mas a coluna for esperada em outras partes do código,
    # é uma boa prática garantir que ela exista, mesmo que vazia.
    df_filtrado['DISTANCIA_ESTIMADA_KM'] = pd.Series(dtype='float64')
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

        valor_mercadoria_total = df_filtrado.get('MERCADORIA-R$', pd.Series(0)).sum()

        # Cálculos operacionais
        peso_total = df_filtrado.get('PESO REAL (KG)', pd.Series(0)).sum()

        # Volume bruto da base
        volume_total = df_filtrado.get('M3', pd.Series(0)).sum()

        # --- Correção: normalização da unidade do volume ---
        if volume_total > 1000:  
            volume_total_m3 = volume_total / 10000
        else:
            volume_total_m3 = volume_total  # já está em m³

        # --- Capacidades e ociosidade (LÓGICA UNIFICADA E CORRIGIDA) ---

        # 1. Define a capacidade de PESO dinamicamente a partir da coluna do arquivo externo.
        #    Usa a média se houver múltiplos veículos ou um padrão de 25000 kg se a coluna não existir.
        capacidade_peso_kg = df_filtrado['CAPACIDADE_KG'].mean() if 'CAPACIDADE_KG' in df_filtrado.columns and not df_filtrado.empty else 25000
        
        # 2. Define a capacidade de VOLUME a partir de um dicionário (pois não vem do arquivo).
        capacidades_volume_por_tipo = {
            'TOCO': 55, 'TRUCK': 75, 'CAVALO': 110, 'PADRAO': 80
        }
        tipo_veiculo_selecionado = df_filtrado['TIPO_CAVALO'].iloc[0] if not df_filtrado.empty and 'TIPO_CAVALO' in df_filtrado.columns else "PADRAO"
        capacidade_volume_m3 = capacidades_volume_por_tipo.get(str(tipo_veiculo_selecionado).upper(), 80)

        # 3. Calcula a ociosidade com base nas capacidades definidas acima.
        ociosidade_peso = (1 - (peso_total / capacidade_peso_kg)) * 100 if capacidade_peso_kg > 0 else 0
        ociosidade_volume = (1 - (volume_total_m3 / capacidade_volume_m3)) * 100 if capacidade_volume_m3 > 0 else 0
        
        # --- FIM DO BLOCO CORRIGIDO ---


        # Infos de identificação (necessárias para os cálculos seguintes)
        nome_completo_motorista = df_filtrado['MOTORISTA'].iloc[0]


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
        # Substitua a linha st.subheader("...") por este bloco:
        st.markdown("""
            <div class="title-block-financeira">
                <i class="fa-solid fa-chart-pie"></i>
                <h2>Painel de Desempenho Geral</h2>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-coins"></i> Análise Financeira</h3>', unsafe_allow_html=True)


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
                return f"{valor:.0f}%"
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
        st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-chart-simple"></i> Indicadores de Performance</h3>', unsafe_allow_html=True)
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
        st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-gears"></i> Detalhes Operacionais</h3>', unsafe_allow_html=True)

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

            /* --- CORREÇÃO DE ALTURA E ANIMAÇÃO DA BARRA --- */
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
                background: linear-gradient(90deg, #7C3AED, #8B5CF6); /* Roxo para Truck (padrão) */
                border-radius: 8px;

                /* ▼▼▼ ANIMAÇÃO DE CRESCIMENTO ADICIONADA AQUI ▼▼▼ */
                transition: width 1.2s ease-in-out; 
                /* ▲▲▲ FIM DA ANIMAÇÃO ▲▲▲ */
            }

            /* Este seletor já existe e aplica a cor para a carreta */
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
                border-left: 5px solid #facc15; /* Amarelo/Dourado */
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

        # --- NOVO SELECTOR DE FROTA (Glass Style com Animação Suave) ---
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
                    # ▼▼▼ TRANSIÇÃO ADICIONADA AQUI ▼▼▼
                    "transition": "all 0.4s ease-in-out", 
                },
                # 🔹 Efeito hover
                "nav-link:hover": {
                    "background-color": "rgba(255, 255, 255, 0.12)",
                    "color": "#fff",
                    "transform": "translateY(-2px)",
                },
                # 🔹 Botão selecionado — Estilo refinado
                "nav-link-selected": {
                    "background-color": "#222433", # Fundo azul escuro
                    "color": "#FFFFFF",           # Texto branco
                    "border": "1.5px solid #5D9CEC", # Borda azul clara
                    "box-shadow": "0 0 15px rgba(93, 156, 236, 0.6)", # Brilho (glow) azul
                    "transform": "translateY(-2px)",
                },
            },
        )

        # ===============================================
        # LÓGICA DE OCUPAÇÃO (MODO VISÃO GERAL)
        # ===============================================
        if rota_sel_visivel == "(Todos)":

            # --- 1. FUNÇÕES DE LÓGICA DE COR (COM AJUSTE) ---
            def obter_cor_ocupacao(percentual):
                """Retorna gradiente para a barra de OCUPAÇÃO (verde = alto)."""
                if percentual < 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"  # Vermelho
                elif percentual < 80: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)" # Amarelo
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)" # Verde

            def obter_cor_ociosidade(percentual):
                """Retorna SEMPRE um gradiente amarelo para a barra de OCIOSIDADE."""
                # A lógica condicional foi removida. Agora a cor é fixa.
                return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)" # Amarelo Fixo

            # --- 2. CÁLCULO DOS DADOS AGREGADOS POR TIPO DE FROTA ---
            capacidades_por_tipo = {
                'TRUCK':  {'peso_kg': 16000, 'volume_m3': 75},
                'CAVALO': {'peso_kg': 25000, 'volume_m3': 110},
                'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
            }

            # --- 2. CÁLCULO DOS DADOS AGREGADOS POR TIPO DE FROTA (VERSÃO FINAL CORRIGIDA) ---
            def calcular_dados_ocupacao(tipo_veiculo, df_dados):
                df_tipo = df_dados[df_dados['TIPO_CAVALO'].fillna('').astype(str).str.upper() == tipo_veiculo]
                if df_tipo.empty:
                    return None

                dados = {}
                viagens_unicas = df_tipo.drop_duplicates(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR'])

                # --- ### INÍCIO DA LÓGICA CONDICIONAL DE CAPACIDADE ### ---

                # Define qual coluna de capacidade usar com base no tipo de veículo
                if tipo_veiculo == 'CAVALO':
                    coluna_capacidade = 'CAPACIDADE_KG' # Para carretas, a capacidade está na carreta
                else: # Para 'TRUCK' ou qualquer outro
                    coluna_capacidade = 'CAPAC_CAVALO'  # Para trucks, a capacidade é do próprio veículo

                # Verifica se a coluna de capacidade correta existe
                if coluna_capacidade not in viagens_unicas.columns:
                    st.error(f"Erro Crítico: A coluna de capacidade '{coluna_capacidade}' não foi encontrada para a frota {tipo_veiculo}.")
                    return None

                # Soma a capacidade da coluna correta para cada viagem única
                dados['cap_total_peso'] = viagens_unicas[coluna_capacidade].sum()
                
                # --- ### FIM DA LÓGICA CONDICIONAL DE CAPACIDADE ### ---

                # O resto da função continua o mesmo, agora usando a capacidade correta
                dados['total_peso'] = df_tipo['PESO REAL (KG)'].sum()
                dados['ocup_peso_perc'] = (dados['total_peso'] / dados['cap_total_peso'] * 100) if dados['cap_total_peso'] > 0 else 0
                dados['ociosidade_peso_perc'] = 100 - dados['ocup_peso_perc']
                dados['potencial_nao_utilizado_kg'] = dados['cap_total_peso'] - dados['total_peso']

                # --- CÁLCULO DE VOLUME (sem alteração na lógica) ---
                capacidades_volume_por_tipo = { 'TRUCK': 75, 'CAVALO': 110, 'PADRAO': 80 }
                capacidade_unitaria_volume = capacidades_volume_por_tipo.get(tipo_veiculo, 80)
                num_viagens_volume = len(viagens_unicas)
                
                dados['cap_total_volume'] = num_viagens_volume * capacidade_unitaria_volume
                dados['total_volume'] = df_tipo['M3'].sum()
                
                if dados['total_volume'] > 1000:
                    dados['total_volume'] /= 10000

                dados['ocup_volume_perc'] = (dados['total_volume'] / dados['cap_total_volume'] * 100) if dados['cap_total_volume'] > 0 else 0
                dados['ociosidade_volume_perc'] = 100 - dados['ocup_volume_perc']
                dados['potencial_nao_utilizado_m3'] = dados['cap_total_volume'] - dados['total_volume']
                
                return dados

            dados_truck = calcular_dados_ocupacao('TRUCK', df_filtrado)
            dados_carreta = calcular_dados_ocupacao('CAVALO', df_filtrado)

            # --- ▼▼▼ INÍCIO DA NOVA LÓGICA DE UNIFICAÇÃO ▼▼▼ ---
            dados_ambas = None
            # Só calcula se ambos os conjuntos de dados existirem
            if dados_truck and dados_carreta:
                dados_ambas = {
                    # Soma os valores absolutos (peso, capacidade, etc.)
                    'total_peso': dados_truck['total_peso'] + dados_carreta['total_peso'],
                    'cap_total_peso': dados_truck['cap_total_peso'] + dados_carreta['cap_total_peso'],
                    'potencial_nao_utilizado_kg': dados_truck['potencial_nao_utilizado_kg'] + dados_carreta['potencial_nao_utilizado_kg'],
                    
                    'total_volume': dados_truck['total_volume'] + dados_carreta['total_volume'],
                    'cap_total_volume': dados_truck['cap_total_volume'] + dados_carreta['cap_total_volume'],
                    'potencial_nao_utilizado_m3': dados_truck['potencial_nao_utilizado_m3'] + dados_carreta['potencial_nao_utilizado_m3'],
                }
                # Recalcula os percentuais com base nos totais somados
                dados_ambas['ocup_peso_perc'] = (dados_ambas['total_peso'] / dados_ambas['cap_total_peso'] * 100) if dados_ambas['cap_total_peso'] > 0 else 0
                dados_ambas['ociosidade_peso_perc'] = 100 - dados_ambas['ocup_peso_perc']
                
                dados_ambas['ocup_volume_perc'] = (dados_ambas['total_volume'] / dados_ambas['cap_total_volume'] * 100) if dados_ambas['cap_total_volume'] > 0 else 0
                dados_ambas['ociosidade_volume_perc'] = 100 - dados_ambas['ocup_volume_perc']

            # Caso apenas uma das frotas tenha dados no período
            elif dados_truck:
                dados_ambas = dados_truck
            elif dados_carreta:
                dados_ambas = dados_carreta
            # --- ▲▲▲ FIM DA NOVA LÓGICA DE UNIFICAÇÃO ▲▲▲ ---

            # --- 3. FUNÇÃO PARA RENDERIZAR OS CARDS (MODIFICADA) ---
            def renderizar_card_ocupacao(dados, tipo_metrica, container):
                if not dados:
                    return

                if tipo_metrica == 'peso':
                    titulo = "⚖️ Ocupação de Peso (KG)"
                    ocup_perc = dados['ocup_peso_perc']
                    total_valor = dados['total_peso']
                    cap_total = dados['cap_total_peso']
                    unidade = "KG"
                    ociosidade_perc = dados['ociosidade_peso_perc']
                    potencial_nao_utilizado = dados['potencial_nao_utilizado_kg']
                    icone_ociosidade = "fa-solid fa-scale-unbalanced-flip"
                    titulo_ociosidade = "Ociosidade de Peso"
                else: # volume
                    titulo = "📦 Ocupação de Cubagem (M³)"
                    ocup_perc = dados['ocup_volume_perc']
                    total_valor = dados['total_volume']
                    cap_total = dados['cap_total_volume']
                    unidade = "M³"
                    ociosidade_perc = dados['ociosidade_volume_perc']
                    potencial_nao_utilizado = dados['potencial_nao_utilizado_m3']
                    icone_ociosidade = "fa-solid fa-box-open"
                    titulo_ociosidade = "Ociosidade de Cubagem (M³)"

                cor_ocup = obter_cor_ocupacao(ocup_perc)
                cor_ocios = obter_cor_ociosidade(ociosidade_perc)
                borda_ocios = cor_ocios.split(',')[1].strip()

                with container:
                    st.markdown(f"""
                    <div class="ocupacao-card-custom"> 
                        <div class="progress-card-header">
                            <div class="progress-card-title">{titulo}</div>
                            <div class="progress-card-value">{ocup_perc:.0f}%</div>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width: {min(ocup_perc, 100)}%; background: {cor_ocup};"></div>
                        </div>
                        <div class="progress-card-footer">
                            <span>Total: {formatar_numero(total_valor, 3 if unidade == 'M³' else 0)} {unidade}</span>
                            <span>Capacidade: {formatar_numero(cap_total)} {unidade}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {borda_ocios}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                        <span><i class="{icone_ociosidade}"></i> <b>{titulo_ociosidade}:</b> {ociosidade_perc:.0f}%</span>
                        <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                            <div style="width: {min(ociosidade_perc, 100)}%; height: 100%; background: {cor_ocios};"></div>
                        </div>
                        <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(potencial_nao_utilizado, 2 if unidade == 'M³' else 0)} {unidade}</span>
                    </div>""", unsafe_allow_html=True)



            # --- 4. RENDERIZAÇÃO CONDICIONAL (CORREÇÃO FINAL) ---
            if selecionar_frota == "FROTA TRUCK":
                st.markdown("<div class='frota-title' style='width: 100%; text-align: center;'><i class='fa-solid fa-truck-moving'></i> FROTA TRUCK</div>", unsafe_allow_html=True)
                col1, col2 = st.columns(2, gap="large")
                renderizar_card_ocupacao(dados_truck, 'peso', col1)
                renderizar_card_ocupacao(dados_truck, 'volume', col2)

            elif selecionar_frota == "FROTA CARRETA":
                st.markdown("<div class='frota-title' style='width: 100%; text-align: center;'><i class='fa-solid fa-trailer'></i> FROTA CARRETA</div>", unsafe_allow_html=True)
                col1, col2 = st.columns(2, gap="large")
                renderizar_card_ocupacao(dados_carreta, 'peso', col1)
                renderizar_card_ocupacao(dados_carreta, 'volume', col2)

            elif selecionar_frota == "AMBAS":
                # --- MODO AMBAS (UNIFICADO) ---
                st.markdown("<div class='frota-title' style='width: 100%; text-align: center;'><i class='fa-solid fa-layer-group'></i> FROTA COMPLETA (TRUCK + CARRETA)</div>", unsafe_allow_html=True)
                
                # Define as colunas 'col1' e 'col2' que serão usadas pela função
                col1, col2 = st.columns(2, gap="large")
                
                # Chama a função de renderização passando os dados unificados ('dados_ambas')
                renderizar_card_ocupacao(dados_ambas, 'peso', col1)
                renderizar_card_ocupacao(dados_ambas, 'volume', col2)

            # Adicione uma verificação final para o caso de nenhuma das condições ser atendida
            # (Isso é uma boa prática para evitar erros caso 'selecionar_frota' fique com um valor inesperado)
            else:
                st.warning("Selecione um tipo de frota para visualizar os dados.")



                # 🔹 FROTA TRUCK
                with col_truck_container:
                    st.markdown("<div class='frota-title' style='text-align:center; margin-bottom:10px;'><i class='fa-solid fa-truck-moving'></i> FROTA TRUCK</div>", unsafe_allow_html=True)

                    container_truck_peso = st.container()
                    renderizar_card_ocupacao(dados_truck, 'peso', container_truck_peso)

                    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)  # espaço entre cards

                    container_truck_volume = st.container()
                    renderizar_card_ocupacao(dados_truck, 'volume', container_truck_volume)

                # 🔹 FROTA CARRETA
                with col_carreta_container:
                    st.markdown("<div class='frota-title' style='text-align:center; margin-bottom:10px;'><i class='fa-solid fa-trailer'></i> FROTA CARRETA</div>", unsafe_allow_html=True)

                    container_carreta_peso = st.container()
                    renderizar_card_ocupacao(dados_carreta, 'peso', container_carreta_peso)

                    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)  # espaço entre cards

                    container_carreta_volume = st.container()
                    renderizar_card_ocupacao(dados_carreta, 'volume', container_carreta_volume)

        # Substitua o bloco "else:" do modo de viagem única por este:
        else:
            # --- MODO VIAGEM ÚNICA (COM ÍCONES ESPECÍFICOS PARA CADA OCIOSIDADE) ---
            ocupacao_peso_perc = (peso_total / capacidade_peso_kg) * 100 if capacidade_peso_kg > 0 else 0
            ociosidade_peso = 100 - ocupacao_peso_perc
            ocupacao_volume_perc = (volume_total_m3 / capacidade_volume_m3) * 100 if capacidade_volume_m3 > 0 else 0
            ociosidade_volume = 100 - ocupacao_volume_perc

            potencial_nao_utilizado_kg = capacidade_peso_kg - peso_total
            potencial_nao_utilizado_m3 = capacidade_volume_m3 - volume_total_m3

            # --- FUNÇÕES DE LÓGICA DE COR (sem alteração) ---
            def obter_cor_ocupacao(percentual):
                if percentual < 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
                elif percentual < 80: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)"

            def obter_cor_ociosidade(percentual):
                if percentual > 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
                elif percentual > 20: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)"

            # --- CÁLCULOS PARA RENDERIZAÇÃO (sem alteração) ---
            barra_peso = min(ocupacao_peso_perc, 100)
            barra_volume = min(ocupacao_volume_perc, 100)
            barra_ociosidade_peso = min(ociosidade_peso, 100)
            barra_ociosidade_volume = min(ociosidade_volume, 100)

            cor_ocupacao_peso = obter_cor_ocupacao(ocupacao_peso_perc)
            cor_ocupacao_volume = obter_cor_ocupacao(ocupacao_volume_perc)
            cor_ociosidade_peso = obter_cor_ociosidade(ociosidade_peso)
            cor_ociosidade_volume = obter_cor_ociosidade(ociosidade_volume)
            
            cor_borda_ociosidade_peso = cor_ociosidade_peso.split(',')[1].strip()
            cor_borda_ociosidade_volume = cor_ociosidade_volume.split(',')[1].strip()

            col1, col2 = st.columns(2)

            with col1:
                # Card de Ocupação de Peso
                st.markdown(f"""
                <div class="ocupacao-card-custom"> 
                    <div class="progress-card-header">
                        <div class="progress-card-title">⚖️ Peso KG</div>
                        <div class="progress-card-value">{ocupacao_peso_perc:.0f}%</div>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {barra_peso}%; background: {cor_ocupacao_peso};"></div>
                    </div>
                    <div class="progress-card-footer">
                        <span>{formatar_numero(peso_total)} KG</span>
                        <span>Capacidade: {formatar_numero(capacidade_peso_kg)} KG</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # AVISO DE OCIOSIDADE DE PESO (com ícone de balança)
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {cor_borda_ociosidade_peso}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                    <span><i class="fa-solid fa-scale-unbalanced-flip"></i> <b>Ociosidade de Peso:</b> {ociosidade_peso:.0f}%</span>
                    <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                        <div style="width: {barra_ociosidade_peso}%; height: 100%; background: {cor_ociosidade_peso};"></div>
                    </div>
                    <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(potencial_nao_utilizado_kg)} KG</span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Card de Ocupação de Cubagem
                st.markdown(f"""
                <div class="ocupacao-card-custom">
                    <div class="progress-card-header">
                        <div class="progress-card-title">📦 Cubagem M³</div>
                        <div class="progress-card-value">{ocupacao_volume_perc:.1f}%</div>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {barra_volume}%; background: {cor_ocupacao_volume};"></div>
                    </div>
                    <div class="progress-card-footer">
                        <span>{formatar_numero(volume_total_m3, 3)} M³</span>
                        <span>Capacidade: {formatar_numero(capacidade_volume_m3)} M³</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # AVISO DE OCIOSIDADE DE CUBAGEM (com ícone de caixa)
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {cor_borda_ociosidade_volume}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                    <span><i class="fa-solid fa-box-open"></i> <b>Ociosidade de Cubagem (M³):</b> {ociosidade_volume:.1f}%</span>
                    <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                        <div style="width: {barra_ociosidade_volume}%; height: 100%; background: {cor_ociosidade_volume};"></div>
                    </div>
                    <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(potencial_nao_utilizado_m3, 2)} M³</span>
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
                return ', '.join(series.dropna().astype(str).unique())


            # Agrupamento para criar a tabela unificada
            resumo_viagens = df_viagens.groupby('VIAGEM_ID').agg(
                EMISSÃO=('EMIS_MANIF', 'first'),
                NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                SITUACAO=('SITUACAO', 'first'),
                MOTORISTA=('MOTORISTA', 'first'),
                PLACA_CAVALO=('PLACA_CAVALO', 'first'),
                CAPAC_CAVALO=('CAPAC_CAVALO', 'first'), # <<< NOVA COLUNA AGREGADA
                PLACA_CARRETA=('PLACA_CARRETA', 'first'),
                CAP_CARRETA=('CAPACIDADE_KG', 'first'), 
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

            # Renomeia colunas para processamento (sem alteração aqui)
            resumo_viagens.rename(columns={
                'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 
                'TIPO_VEICULO': 'TIPO_CAVALO', 'DESTINOS': 'DEST_MANIF',
                'PROPRIETARIO': 'PROPRIETARIO_CAVALO', 'CUSTO_OS_TOTAL': 'OS-R$',
                'CUSTO_CTRB_TOTAL': 'CTRB-R$', 'FRETE_TOTAL': 'FRETE-R$',
                'NUM_OS_LISTA': 'NUM_OS', 'NUM_CTRB_LISTA': 'NUM_CTRB',
                'ICMS': 'ICMS-R$', 'PESO_KG': 'PESO REAL (KG)',
                'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
            }, inplace=True)

            # Funções de cálculo para as colunas finais (sem alteração aqui)
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
            
            # Formata as colunas de capacidade
            resumo_viagens['CAP_CARRETA'] = resumo_viagens['CAP_CARRETA'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg')
            resumo_viagens['CAPAC_CAVALO'] = resumo_viagens['CAPAC_CAVALO'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg') # <<< FORMATAÇÃO DA NOVA COLUNA

            resumo_viagens.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto',
                'TIPO_CAVALO': 'TIPO', 'DEST_MANIF': 'DESTINOS', 'Nº Documento Custo': 'Nº CTRB/OS',
                'QTDE_CTRC': 'Qtd. CTRCs',
                'SITUACAO': 'SITUAÇÃO'
            }, inplace=True)

            # Define a ordem final, com a nova coluna no lugar certo
            ordem_final = [
                'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUAÇÃO', 'MOTORISTA', 'DESTINOS', 'ENTREGAS',
                'TIPO', # <<< MOVIDO PARA CÁ
                'PLACA_CAVALO', 'CAPAC_CAVALO', 'PLACA_CARRETA', 'CAP_CARRETA', 'Nº CTRB/OS', 'Custo (CTRB/OS)', 
                'CTRB/Frete (%)', 'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)', 'M3', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
            ]
            colunas_para_exibir = [col for col in ordem_final if col in resumo_viagens.columns]

            df_para_exibir = resumo_viagens[colunas_para_exibir].copy()
            
            # Aplica o gradiente de cor (pode precisar ajustar o subset se o nome da coluna mudou no rename)
            # A coluna para o gradiente ainda é 'CTRB/Frete (%)_valor', então não precisa mudar.
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

            # O df_filtrado já contém os dados corretos para a rota selecionada.
            # Vamos criar uma cópia para trabalhar.
            df_detalhado_base = df_filtrado.copy()

            # 1. FUNÇÕES PARA UNIFICAR AS COLUNAS DE CUSTO
            #    (Essas funções decidem qual valor/número usar baseado no proprietário)
            def calcular_custo_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)

            def obter_numero_documento_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('NUM_OS', '')
                return row.get('NUM_CTRB', '')

            # 2. APLICA AS FUNÇÕES PARA CRIAR AS NOVAS COLUNAS UNIFICADAS
            df_detalhado_base['Custo (CTRB/OS)'] = df_detalhado_base.apply(calcular_custo_unificado, axis=1)
            df_detalhado_base['Nº CTRB/OS'] = df_detalhado_base.apply(obter_numero_documento_unificado, axis=1)

            # 3. DEFINE A LISTA FINAL DE COLUNAS PARA EXIBIR
            #    (Note que as colunas antigas de custo foram removidas e as novas, adicionadas)
            colunas_para_exibir = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS',          # <-- COLUNA UNIFICADA
                'Custo (CTRB/OS)',     # <-- COLUNA UNIFICADA
                'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            
            # 4. Garante que apenas colunas existentes sejam usadas para evitar erros
            colunas_existentes = [col for col in colunas_para_exibir if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes].copy()

            # 5. Renomeia as colunas para uma apresentação mais limpa
            df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 
                'NUM_MANIF': 'Nº Manifesto',
                'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino',
                'PLACA_CAVALO': 'PLACA', 
                'TIPO_CAVALO': 'TIPO', 
                'QTDE_CTRC': 'Qtd. CTRCs'
                # Não precisa mais renomear as colunas de custo aqui
            }, inplace=True)

            # 6. Formata as colunas para exibição
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')
            
            # Formata as colunas de moeda, incluindo a nova coluna unificada
            colunas_moeda_det = ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)
            
            if 'PESO REAL (KG)' in df_detalhado_final.columns:
                df_detalhado_final['PESO REAL (KG)'] = df_detalhado_final['PESO REAL (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))

            # 7. Exibe a tabela final, já corrigida
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)
            
            # 8. Botão de download para os dados detalhados (agora com as colunas corretas)
            try:
                excel_bytes_detalhado = to_excel(df_detalhado_final)
                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=f"detalhes_viagem_{rota_sel_visivel.split(' ')[1]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado_tab1_final" # Chave única para evitar conflitos
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel detalhado: {e}")

                # ▼▼▼ INSIRA ESTE BLOCO DE CÓDIGO COMPLETO AQUI ▼▼▼

# ==================================================================
# ABA 2 (ANÁLISE FINANCEIRA)
# ==================================================================
with tab2:
    # Título estilizado para a aba
    st.markdown("""
        <div class="title-block-financeira">
            <i class="fa-solid fa-coins"></i>
            <h2>Análise Financeira Avançada</h2>
        </div>
    """, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # KPIs financeiros que foram movidos da primeira aba
        kpi_f1, kpi_f2, kpi_f3, kpi_f4, kpi_f5, kpi_f6 = st.columns(6)

        # Lógica para determinar o título do KPI de Custo
        titulo_kpi_custo = "📄 Custo CTRB / OS" # Título padrão
        if not df_filtrado.empty:
            if df_filtrado['PROPRIETARIO_CAVALO'].nunique() > 1:
                titulo_kpi_custo = "📄 Custo CTRB / OS"
            elif df_filtrado['PROPRIETARIO_CAVALO'].iloc[0] == 'KM TRANSPORTES ROD. DE CARGAS LTDA':
                titulo_kpi_custo = "📄 Custo CTRB"
            elif df_filtrado['PROPRIETARIO_CAVALO'].iloc[0] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                titulo_kpi_custo = "📋 Custo OS"

        # Dicionário com os KPIs financeiros
        kpis_financeiros = {
            kpi_f1: {"titulo": "💵 Receita Total", "valor": formatar_moeda(receita_total), "classe": "receita"},
            kpi_f2: {"titulo": titulo_kpi_custo, "valor": formatar_moeda(custo_ctrb_os), "classe": "custo"},
            kpi_f3: {"titulo": "💸 ICMS", "valor": formatar_moeda(custo_icms), "classe": "custo"},
            kpi_f4: {"titulo": "📊 Custo Total", "valor": formatar_moeda(custo_total), "classe": "custo"},
            kpi_f5: {"titulo": "💰 Lucro Líquido", "valor": formatar_moeda(lucro_estimado), "classe": "lucro"},
            kpi_f6: {"titulo": "📈 Margem de Lucro", "valor": formatar_percentual(margem_lucro), "classe": "lucro"}
        }

        # Itera e exibe cada KPI
        for coluna, info in kpis_financeiros.items():
            with coluna:
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: center;'>
                        <div class='kpi-title'>{info['titulo']}</div>
                        <div class='kpi-value {info['classe']}'>{info['valor']}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Futuramente, você pode adicionar gráficos e outras análises aqui.
        # st.info("Área reservada para gráficos de análise financeira.")

# ▲▲▲ FIM DO BLOCO A SER INSERIDO ▲▲▲



# ==================================================================
# ABA 3 (PERFORMANCE DA FROTA) - COM ESTILO E COR ATUALIZADOS
# ==================================================================
with tab3:
    # --- CSS E HTML PARA O TÍTULO PERSONALIZADO ---
    st.markdown("""
    <style>
        .title-block-performance {
            /* ▼▼▼ COR DE FUNDO ATUALIZADA AQUI ▼▼▼ */
            background: #1C1A29; /* Azul/Roxo bem escuro, como na imagem */
            
            /* Bordas laterais na cor laranja para combinar com o tema */
            border-left: 5px solid #f97316;
            border-right: 5px solid #f97316;
            
            padding: 5px 30px; /* Espaçamento interno */
            margin: 10px 0 25px 0; /* Margem para separar do conteúdo */
            border-radius: 12px; /* Bordas arredondadas */
            width: 100%;
            box-sizing: border-box;
            
            /* Centraliza o ícone e o texto */
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px; /* Espaço entre o ícone e o texto */
            
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); /* Sombra suave */
        }

        .title-block-performance h2 {
            font-family: "Poppins", "Segoe UI", sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff; /* Cor do texto */
            margin: 0;
            letter-spacing: 0.5px;
        }

        .title-block-performance .fa-bolt-lightning {
            font-size: 2.0rem; /* Tamanho do ícone */
            color: #f97316; /* Cor do ícone (laranja) */
        }
    </style>
    
    <div class="title-block-performance">
        <i class="fa-solid fa-bolt-lightning"></i>
        <h2>Performance da Frota: Frota vs. Terceiros</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # --- PREPARAÇÃO DOS DADOS (sem alterações) ---
        df_aux_frota = df_filtrado.copy()
        df_aux_frota["DATA_EMISSAO"] = df_aux_frota["EMIS_MANIF"].dt.date
        
        # Garante que a coluna de ID da viagem exista para ambos os dataframes
        df_aux_frota["VIAGEM_ID"] = df_aux_frota.groupby(["MOTORISTA", "PLACA_CAVALO", "DATA_EMISSAO"], sort=False).ngroup() + 1
        
        # ... (o resto da sua preparação de dados continua igual)
        capacidades = {
            'TOCO': {'peso_kg': 10000, 'volume_m3': 55}, 'TRUCK': {'peso_kg': 16000, 'volume_m3': 75},
            'CAVALO': {'peso_kg': 25000, 'volume_m3': 110}, 'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
        }
        df_aux_frota['CAPACIDADE_PESO'] = df_aux_frota['TIPO_CAVALO'].map(lambda x: capacidades.get(str(x).upper(), capacidades['PADRAO'])['peso_kg'])
        df_aux_frota["CUSTO_POR_LINHA"] = df_aux_frota.apply(lambda r: r["CTRB-R$"] if r.get("PROPRIETARIO_CAVALO") == "KM TRANSPORTES ROD. DE CARGAS LTDA" else r.get("OS-R$"), axis=1)

        # --- SELETOR DE PROPRIETÁRIO (sem alterações) ---
        selecao_proprietario = option_menu(
            menu_title=None,
            options=["TODOS", "FROTA KM", "TERCEIROS"],
            icons=["collection-fill", "building", "person-badge"],
            menu_icon="cast", default_index=0, orientation="horizontal",
            styles={
                "container": {"padding": "6px", "background-color": "rgba(30, 30, 40, 0.4)", "border-radius": "16px", "justify-content": "center"},
                # ▼▼▼ ALTERAÇÃO APLICADA AQUI ▼▼▼
                "icon": {"color": "#FFFFFF", "font-size": "18px"}, # Cor alterada para branco
                "nav-link": {"font-size": "14px", "font-weight": "600", "color": "#E5E7EB", "padding": "10px 26px", "border-radius": "12px", "margin": "0px 6px", "background-color": "rgba(255, 255, 255, 0.05)"},
                "nav-link:hover": {"background-color": "rgba(255,255,255,0.12)", "color": "#fff"},
                "nav-link-selected": {"background": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)", "color": "white"},
            }
        )

        # --- FILTRAGEM DOS DADOS (sem alterações) ---
        df_viagens = df_aux_frota.copy()
        if selecao_proprietario == "FROTA KM":
            df_viagens = df_viagens[df_viagens['PROPRIETARIO_CAVALO'] == 'KM TRANSPORTES ROD. DE CARGAS LTDA']
        elif selecao_proprietario == "TERCEIROS":
            df_viagens = df_viagens[df_viagens['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME']

        # --- 4. CÁLCULO E EXIBIÇÃO DOS KPIs ---
        # Este bloco agora vem logo após a filtragem dos dados.
        if not df_viagens.empty:
            # Agrega os dados por viagem para calcular as métricas (código existente, sem alterações)
            resumo_por_viagem = df_viagens.groupby('VIAGEM_ID').agg(
                FRETE_VIAGEM=('FRETE-R$', 'sum'),
                CUSTO_UNICO_VIAGEM=('CUSTO_POR_LINHA', 'max'),
                PESO_VIAGEM=('PESO REAL (KG)', 'sum'),
                ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'),
                DISTANCIA_ESTIMADA=('DISTANCIA_ESTIMADA_KM', 'first')
            ).reset_index()

            # --- CÁLCULO DOS KPIs TOTAIS E MÉDIOS (código existente, sem alterações) ---
            total_viagens = resumo_por_viagem['VIAGEM_ID'].nunique()
            distancia_total = resumo_por_viagem['DISTANCIA_ESTIMADA'].sum()
            distancia_media = distancia_total / total_viagens if total_viagens > 0 else 0
            total_entregas = resumo_por_viagem['ENTREGAS_VIAGEM'].sum()
            peso_total = resumo_por_viagem['PESO_VIAGEM'].sum()
            peso_medio_viagem = peso_total / total_viagens if total_viagens > 0 else 0
            
            capacidade_total = df_viagens.drop_duplicates(subset=['VIAGEM_ID'])['CAPACIDADE_PESO'].sum()
            ocupacao_media = (peso_total / capacidade_total * 100) if capacidade_total > 0 else 0
            
            custo_total_kpi = resumo_por_viagem['CUSTO_UNICO_VIAGEM'].sum()
            frete_total_kpi = resumo_por_viagem['FRETE_VIAGEM'].sum()
            perc_custo_frete = (custo_total_kpi / frete_total_kpi * 100) if frete_total_kpi > 0 else 0

            # Funções de formatação (código existente, sem alterações)
            def fmt_num_kpi(v, suf=""): return f"{v:,.0f}{suf}".replace(",", ".")
            def fmt_perc_kpi(v): return f"{v:.0f}%"

            # --- Seletor de menu de opções (código existente, sem alterações) ---
            kpi_view = option_menu(
                menu_title=None,
                options=["Médias e Índices", "Valores Totais"],
                icons=["graph-up-arrow", "calculator"],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#0e1117", "justify-content": "center", "margin-bottom": "25px"},
                    "icon": {"color": "#E5E7EB", "font-size": "16px"},
                    "nav-link": {"font-size": "14px", "font-weight": "600", "color": "#bdc3c7", "background-color": "#2c3e50", "border-radius": "10px", "padding": "10px 25px", "margin": "0px 8px", "text-align": "center"},
                    "nav-link:hover": {"background-color": "#34495e", "color": "#ffffff"},
                    "nav-link-selected": {"background": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)", "color": "white", "box-shadow": "0 4px 15px rgba(249, 115, 22, 0.4)"},
                }
            )

            # --- Lógica para exibir os KPIs corretos ---
            kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

            if kpi_view == 'Médias e Índices':
                kpis_data = {
                    kpi1: {"titulo": "🗺️ TOTAL DE VIAGENS", "valor": fmt_num_kpi(total_viagens)},
                    kpi2: {"titulo": "🚛 DISTÂNCIA MÉDIA", "valor": fmt_num_kpi(distancia_media, " km")},
                    kpi3: {"titulo": "📦 TOTAL DE ENTREGAS", "valor": fmt_num_kpi(total_entregas)},
                    kpi4: {"titulo": "⚖️ PESO MÉDIO / VIAGEM", "valor": fmt_num_kpi(peso_medio_viagem, " kg")},
                    kpi5: {"titulo": "📈 OCUPAÇÃO MÉDIA", "valor": fmt_perc_kpi(ocupacao_media)},
                    kpi6: {"titulo": "📊 % CUSTO / FRETE", "valor": fmt_perc_kpi(perc_custo_frete)},
                }
            else: # kpi_view == 'Valores Totais'
                # --- ▼▼▼ A MUDANÇA FOI FEITA AQUI ▼▼▼ ---
                kpis_data = {
                    kpi1: {"titulo": "🗺️ TOTAL DE VIAGENS", "valor": fmt_num_kpi(total_viagens)},
                    kpi2: {"titulo": "🚛 DISTÂNCIA TOTAL", "valor": fmt_num_kpi(distancia_total, " km")},
                    kpi3: {"titulo": "📦 TOTAL DE ENTREGAS", "valor": fmt_num_kpi(total_entregas)},
                    kpi4: {"titulo": "⚖️ PESO TOTAL", "valor": fmt_num_kpi(peso_total, " kg")},
                    # KPI de Custo Total foi substituído pelo de % Custo / Frete
                    kpi5: {"titulo": "📊 % CUSTO / FRETE", "valor": fmt_perc_kpi(perc_custo_frete)},
                    kpi6: {"titulo": "💵 FRETE TOTAL", "valor": f"R$ {fmt_num_kpi(frete_total_kpi)}"},
                }
                # --- ▲▲▲ FIM DA MUDANÇA ▲▲▲ ---
            
            # Renderiza os KPIs
            for coluna, info in kpis_data.items():
                with coluna:
                    st.markdown(f"""
                        <div class='kpi-container' style='text-align: center;'>
                            <div class='kpi-title'>{info['titulo']}</div>
                            <div class='kpi-value'>{info['valor']}</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.divider()

        # ... (o resto do seu código da aba continua aqui)



        # --- TABELA DE RESUMO DAS VIAGENS ---
        titulo_tabela_resumo = f"### 📋 Resumo das Viagens ({selecao_proprietario})"
        st.markdown(titulo_tabela_resumo)

        if not df_viagens.empty:

            def juntar_unicos(series): return ', '.join(series.dropna().astype(str).unique())
            resumo_viagens = df_viagens.groupby('VIAGEM_ID').agg(
                EMISSÃO=('EMIS_MANIF', 'first'),
                NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                SITUACAO=('SITUACAO', 'first'), MOTORISTA=('MOTORISTA', 'first'),
                PLACA_CAVALO=('PLACA_CAVALO', 'first'), PLACA_CARRETA=('PLACA_CARRETA', 'first'),
                TIPO_VEICULO=('TIPO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
                PROPRIETARIO_CAVALO=('PROPRIETARIO_CAVALO', 'first'), # <-- MUDANÇA: Nome da coluna original
                CUSTO_OS_TOTAL=('OS-R$', 'max'),
                CUSTO_CTRB_TOTAL=('CTRB-R$', 'max'), FRETE_TOTAL=('FRETE-R$', 'sum'),
                ICMS=('ICMS-R$', 'sum'), PESO_KG=('PESO REAL (KG)', 'sum'), M3=('M3', 'sum'),
                VOLUMES=('VOLUMES', 'sum'), VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                ENTREGAS=('DEST_MANIF', 'nunique'), QTDE_CTRC=('QTDE_CTRC', 'sum')
            ).reset_index()

            # Renomeia colunas para processamento
            resumo_viagens.rename(columns={
                'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 'TIPO_VEICULO': 'TIPO_CAVALO', 
                'DESTINOS': 'DEST_MANIF', 'CUSTO_OS_TOTAL': 'OS-R$', 'CUSTO_CTRB_TOTAL': 'CTRB-R$', 
                'FRETE_TOTAL': 'FRETE-R$', 'ICMS': 'ICMS-R$', 'PESO_KG': 'PESO REAL (KG)', 
                'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
            }, inplace=True)

            # Funções de cálculo
            def calcular_custo_final(row):
                custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                destinos_str = str(row.get('DEST_MANIF', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str: return custo_base / 2
                return custo_base
            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_final, axis=1)

            def calcular_ctrb_frete_numerico(row):
                try:
                    custo = float(row['Custo (CTRB/OS)'])
                    frete = float(row['FRETE-R$'])
                    return (custo / frete) * 100 if frete > 0 else 0.0
                except (ValueError, TypeError): return 0.0
            resumo_viagens['CTRB/Frete (%)_valor'] = resumo_viagens.apply(calcular_ctrb_frete_numerico, axis=1)
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.0f}%")

            # Formatação para exibição
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
            
            # Renomeia colunas para exibição final
            resumo_viagens.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'TIPO_CAVALO': 'TIPO', 
                'DEST_MANIF': 'DESTINOS', 'QTDE_CTRC': 'Qtd. CTRCs', 'SITUACAO': 'SITUAÇÃO',
                'PROPRIETARIO_CAVALO': 'PROPRIETÁRIO' # <-- MUDANÇA 1: Renomeia a coluna para exibição
            }, inplace=True)

            # ▼▼▼ MUDANÇA 2: Adiciona 'PROPRIETÁRIO' na ordem de exibição ▼▼▼
            ordem_final = [
                'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUACAO', 'MOTORISTA', 'DESTINOS', 
                'ENTREGAS', 'TIPO', 
                'PROPRIETÁRIO', # <-- COLUNA ADICIONADA AQUI
                'PLACA_CAVALO', 'PLACA_CARRETA', 'Custo (CTRB/OS)', 'CTRB/Frete (%)', 
                'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)', 'M3', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
            ]
            # ▲▲▲ FIM DA MUDANÇA 2 ▲▲▲

            colunas_para_exibir = [col for col in ordem_final if col in resumo_viagens.columns]
            df_para_exibir = resumo_viagens[colunas_para_exibir].copy()

            # ▼▼▼ INÍCIO DA MUDANÇA: APLICA A FUNÇÃO PARA ENCURTAR O NOME ▼▼▼
            def encurtar_proprietario(nome):
                if 'MARCELO H LEMOS' in nome:
                    return 'MARCELO LEMOS BERALDO'
                if 'KM TRANSPORTES' in nome:
                    return 'KM TRANSPORTES'
                return nome # Retorna o nome original se não for nenhum dos dois

            df_para_exibir['PROPRIETÁRIO'] = df_para_exibir['PROPRIETÁRIO'].apply(encurtar_proprietario)
            # ▲▲▲ FIM DA MUDANÇA ▲▲▲

            styled_df = df_para_exibir.style.background_gradient(cmap='Reds', subset=['CTRB/Frete (%)'], gmap=resumo_viagens['CTRB/Frete (%)_valor'])
            
            # Exibição da tabela de resumo
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Botão de download do resumo
            excel_bytes_resumo = to_excel(df_para_exibir)
            st.download_button(
                label=f"📤 Exportar Resumo ({selecao_proprietario})", data=excel_bytes_resumo,
                file_name=f"resumo_performance_{selecao_proprietario}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_tab3_resumo_{selecao_proprietario}"
            )

            # --- ▼▼▼ BLOCO ATUALIZADO: TABELA DE DADOS DETALHADOS ▼▼▼ ---
            st.divider()
            titulo_tabela_detalhada = f"### 📄 Dados Detalhados das Viagens ({selecao_proprietario})"
            st.markdown(titulo_tabela_detalhada)

            # Usamos o DataFrame 'df_viagens', que já está filtrado por Frota ou Terceiros
            df_detalhado_base = df_viagens.copy()

            # 1. Funções para unificar as colunas de custo
            def calcular_custo_unificado(row):
                """Retorna o valor de OS-R$ para TERCEIROS e CTRB-R$ para os demais."""
                if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)

            def obter_numero_documento_unificado(row):
                """Retorna o NUM_OS para TERCEIROS e NUM_CTRB para os demais."""
                if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('NUM_OS', '')
                return row.get('NUM_CTRB', '')

            # 2. Aplica as funções para criar as novas colunas unificadas
            df_detalhado_base['Custo CTRB/OS'] = df_detalhado_base.apply(calcular_custo_unificado, axis=1)
            df_detalhado_base['Nº CTRB/OS'] = df_detalhado_base.apply(obter_numero_documento_unificado, axis=1)

            # 3. Define a lista de colunas que você quer exibir, incluindo as novas
            colunas_para_exibir = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS',          # <-- Coluna unificada
                'Custo CTRB/OS',       # <-- Coluna unificada
                'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]

            # 4. Garante que apenas colunas existentes sejam usadas para evitar erros
            colunas_existentes = [col for col in colunas_para_exibir if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes].copy()

            # 5. Renomeia as colunas para uma apresentação mais limpa
            df_detalhado_final = df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO',
                'NUM_MANIF': 'Nº Manifesto',
                'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino',
                'PLACA_CAVALO': 'PLACA',
                'TIPO_CAVALO': 'TIPO',
                'QTDE_CTRC': 'Qtd. CTRCs'
            })

            # 6. Formata os valores (data, moeda, peso, etc.)
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')

            # Formata todas as colunas de moeda, incluindo a nova coluna de custo
            colunas_moeda = ['Custo CTRB/OS', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)

            # Formata peso e M3
            if 'PESO REAL (KG)' in df_detalhado_final.columns:
                df_detalhado_final['PESO REAL (KG)'] = df_detalhado_final['PESO REAL (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))

            # 7. Exibe a tabela detalhada final com as colunas corretas
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)

            # 8. Botão de download para os dados detalhados (agora com as colunas unificadas)
            excel_bytes_detalhado = to_excel(df_detalhado_final)
            st.download_button(
                label=f"📤 Exportar Detalhes ({selecao_proprietario})",
                data=excel_bytes_detalhado,
                file_name=f"detalhes_viagens_{selecao_proprietario}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_tab3_detalhes_{selecao_proprietario}"
            )
            # --- ▲▲▲ FIM DO BLOCO ATUALIZADO ▲▲▲ ---



        else:
            st.info(f"Nenhuma viagem encontrada para o grupo '{selecao_proprietario}' no período selecionado.")


with tab4:
    # Adicione a importação do Altair no início do seu script
    import altair as alt

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
                
                # Busca a capacidade correspondente ao tipo de veículo
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
            
            # ▼▼▼ KPI CORRIGIDO PARA FICAR EM UMA ÚNICA LINHA ▼▼▼
            with id3:
                # Formata a capacidade para exibição
                capacidade_formatada = f"Cap. {formatar_numero(capacidade_kg_frequente)} kg"
                
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: center;'>
                        <div class='kpi-title'><i class='fa-solid fa-gear'></i> Tipo / Capacidade</div>
                        <div class='kpi-value'>
                            {tipo_veiculo_frequente} - <span style='font-size: 1rem; color: #d1d5db; font-weight: 500;'>{capacidade_formatada}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with id4:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-map-location-dot'></i> Destino Frequente</div><div class='kpi-value'>{destino_frequente}</div></div>", unsafe_allow_html=True)
            
            with id5:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-calendar-days'></i> Última Viagem</div><div class='kpi-value'>{ultima_viagem_data}</div></div>", unsafe_allow_html=True)
            
            st.divider()

        # Título e KPIs (sem alterações)
        st.markdown("""
            <div class="title-block-motoristas">
                <i class="fa-solid fa-bullseye"></i>
                <h2>Painel de Eficiência Operacional</h2>
            </div>
        """, unsafe_allow_html=True)

        def fmt_num(v, suf=""): return f"{v:,.0f}{suf}".replace(",", ".")
        def fmt_perc(v): return f"{v:.0f}%".replace(".", ",")
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

        # --- ▼▼▼ NOVO BLOCO: RANKING DE MOTORISTAS (COM FILTRO INDIVIDUAL) ▼▼▼

        # Só exibe o ranking se houver dados para comparar
        if not resumo_motorista.empty:
            st.markdown("### 🏆 Ranking de Motoristas no Período")

            # --- 1. PREPARAÇÃO DOS DADOS E NOMES ---
            def formatar_nome_curto(nome_completo):
                partes = str(nome_completo).strip().split()
                if not partes: return ""
                preposicoes = ['DA', 'DE', 'DO', 'DOS']
                if len(partes) >= 3 and partes[1].upper() in preposicoes:
                    return f"{partes[0]} {partes[1]} {partes[2]}"
                elif len(partes) >= 2:
                    return f"{partes[0]} {partes[1]}"
                else:
                    return partes[0]

            resumo_motorista['NOME_CURTO'] = resumo_motorista['MOTORISTA'].apply(formatar_nome_curto)

            # --- 2. CRIAÇÃO DO NOVO SELETOR DE MOTORISTA ---
            # Gera a lista de motoristas para o seletor, já com o nome curto
            lista_motoristas_ranking = ["(Todos)"] + sorted(resumo_motorista['NOME_CURTO'].unique())
            
            motorista_ranking_sel = st.selectbox(
                'Selecione um motorista para análise individual:',
                options=lista_motoristas_ranking,
                key="filtro_motorista_ranking" # Chave única para este seletor
            )

            # --- 3. FILTRAGEM DOS DADOS PARA OS GRÁFICOS ---
            # Filtra o dataframe do ranking com base na seleção. Se "(Todos)" for escolhido, usa o df completo.
            if motorista_ranking_sel != "(Todos)":
                df_para_graficos = resumo_motorista[resumo_motorista['NOME_CURTO'] == motorista_ranking_sel]
            else:
                df_para_graficos = resumo_motorista

            # --- 4. CRIAÇÃO DAS COLUNAS E GRÁFICOS (LÓGICA EXISTENTE ADAPTADA) ---
            col_rank1, col_rank2 = st.columns(2)

            with col_rank1:
                # O dicionário de opções permanece o mesmo
                opcoes_ranking = {
                    'Performance das Viagens - CTRB/Frete (%)': {
                        'coluna_valor': 'PERC_CUSTO_FRETE', 'coluna_ordem': 'PERC_CUSTO_FRETE',
                        'titulo_eixo': '% Custo / Frete', 'ordem': 'ascending',
                        'formato_label': "format(datum.PERC_CUSTO_FRETE, '.0f') + '%'"
                    },
                    'Produtividade - Nº de Viagens': {
                        'coluna_valor': 'TOTAL_VIAGENS', 'coluna_ordem': 'TOTAL_VIAGENS',
                        'titulo_eixo': 'Nº de Viagens', 'ordem': 'descending',
                        'formato_label': "format(datum.TOTAL_VIAGENS, '.0f')"
                    },
                    'Performance Operacional - Peso Médio KG': {
                        'coluna_valor': 'PESO_MEDIO_VIAGEM', 'coluna_ordem': 'PESO_MEDIO_VIAGEM',
                        'titulo_eixo': 'Peso Médio por Viagem (kg)', 'ordem': 'descending',
                        'formato_label': "format(datum.PESO_MEDIO_VIAGEM, ',.0f') + ' kg'"
                    },
                    'Ordem Alfabética - Motorista': {
                        'coluna_valor': 'PERC_CUSTO_FRETE', 'coluna_ordem': 'NOME_CURTO',
                        'titulo_eixo': '% Custo / Frete', 'ordem': 'ascending',
                        'formato_label': "format(datum.PERC_CUSTO_FRETE, '.0f') + '%'"
                    }
                }
                selecao_ranking = st.selectbox(
                    'Selecione a métrica para o ranking:',
                    options=list(opcoes_ranking.keys())
                )
                
                # Prepara as variáveis dinâmicas
                config_selecionada = opcoes_ranking[selecao_ranking]
                coluna_valor_selecionada = config_selecionada['coluna_valor']
                coluna_ordem_selecionada = config_selecionada['coluna_ordem']
                titulo_eixo_selecionado = config_selecionada['titulo_eixo']
                ordem_selecionada = config_selecionada['ordem']
                formato_label_selecionado = config_selecionada['formato_label']

                # Ordena o DataFrame (df_para_graficos já está filtrado)
                ranking_dinamico_df = df_para_graficos.sort_values(
                    by=coluna_ordem_selecionada, 
                    ascending=(ordem_selecionada == 'ascending')
                )

                # Criação do gráfico (aqui usamos o 'ranking_dinamico_df' que já pode estar filtrado)
                barras_dinamicas = alt.Chart(ranking_dinamico_df).mark_bar(
                    cornerRadius=5,
                    height=25
                ).encode(
                    x=alt.X(f'{coluna_valor_selecionada}:Q', title=titulo_eixo_selecionado, axis=alt.Axis(format='.0f')),
                    y=alt.Y('NOME_CURTO:N', 
                            title=None, 
                            sort=alt.EncodingSortField(field=coluna_ordem_selecionada, op="min", order=ordem_selecionada),
                            axis=alt.Axis(labelFontSize=14, labelLimit=0)
                        ),
                    color=alt.Color(f'{coluna_valor_selecionada}:Q',
                                    scale=alt.Scale(scheme='reds', reverse=(ordem_selecionada == 'ascending')),
                                    legend=None),
                    tooltip=[
                        alt.Tooltip('NOME_CURTO', title='Motorista'),
                        alt.Tooltip('PERC_CUSTO_FRETE', title='% Custo/Frete', format='.1f'),
                        alt.Tooltip('TOTAL_VIAGENS', title='Nº de Viagens'),
                        alt.Tooltip('PESO_MEDIO_VIAGEM', title='Peso Médio', format=',.0f')
                    ]
                )
                
                # O resto da lógica do gráfico continua igual...
                texto_dinamico = barras_dinamicas.transform_calculate(
                    text_label=formato_label_selecionado.replace('datum.PESO_MEDIO_VIAGEM', f'datum.{coluna_valor_selecionada}').replace('datum.PERC_CUSTO_FRETE', f'datum.{coluna_valor_selecionada}').replace('datum.TOTAL_VIAGENS', f'datum.{coluna_valor_selecionada}')
                ).mark_text(
                    align='left', baseline='middle', dx=5, fontSize=14
                ).encode(
                    text=alt.Text('text_label:N'), color=alt.value('white')
                )

                chart_dinamico = (barras_dinamicas + texto_dinamico).properties(
                    title={"text": selecao_ranking, "anchor": "start", "fontSize": 16, "fontWeight": "bold"},
                    height=alt.Step(35)
                ).configure_view(stroke=None).configure_axis(grid=False).configure_title(color='white')
                
                st.altair_chart(chart_dinamico, use_container_width=True)

            with col_rank2:
                # A lógica para o segundo gráfico é a mesma, apenas adaptada
                opcoes_ranking_op = {
                    'Eficiência Operacional (Ocupação Média)': {
                        'coluna_valor': 'OCUPACAO_MEDIA_CARGA', 'coluna_ordem': 'OCUPACAO_MEDIA_CARGA',
                        'titulo_eixo': 'Ocupação Média (%)', 'ordem': 'descending', 'cor_esquema': 'greens',
                        'formato_label': "format(datum.OCUPACAO_MEDIA_CARGA, '.0f') + '%'"
                    },
                    'Performance de Entrega (Média de Entregas)': {
                        'coluna_valor': 'MEDIA_ENTREGAS_VIAGEM', 'coluna_ordem': 'MEDIA_ENTREGAS_VIAGEM',
                        'titulo_eixo': 'Média de Entregas por Viagem', 'ordem': 'descending', 'cor_esquema': 'bluepurple',
                        'formato_label': "format(datum.MEDIA_ENTREGAS_VIAGEM, '.1f')"
                    },
                    'Performance de Distância (Distância Média)': {
                        'coluna_valor': 'DISTANCIA_MEDIA_VIAGEM', 'coluna_ordem': 'DISTANCIA_MEDIA_VIAGEM',
                        'titulo_eixo': 'Distância Média por Viagem (km)', 'ordem': 'descending', 'cor_esquema': 'teals',
                        'formato_label': "format(datum.DISTANCIA_MEDIA_VIAGEM, ',.0f') + ' km'"
                    },
                    'Ordem Alfabética (Motorista)': {
                        'coluna_valor': 'OCUPACAO_MEDIA_CARGA', 'coluna_ordem': 'NOME_CURTO',
                        'titulo_eixo': 'Ocupação Média (%)', 'ordem': 'ascending', 'cor_esquema': 'greens',
                        'formato_label': "format(datum.OCUPACAO_MEDIA_CARGA, '.0f') + '%'"
                    }
                }
                selecao_ranking_op = st.selectbox(
                    'Selecione a métrica para o ranking operacional:',
                    options=list(opcoes_ranking_op.keys())
                )

                config_selecionada_op = opcoes_ranking_op[selecao_ranking_op]
                coluna_valor_op = config_selecionada_op['coluna_valor']
                coluna_ordem_op = config_selecionada_op['coluna_ordem']
                titulo_eixo_op = config_selecionada_op['titulo_eixo']
                ordem_op = config_selecionada_op['ordem']
                cor_esquema_op = config_selecionada_op['cor_esquema']
                formato_label_op = config_selecionada_op['formato_label']

                # Usa o mesmo dataframe filtrado 'df_para_graficos'
                ranking_dinamico_op_df = df_para_graficos.sort_values(
                    by=coluna_ordem_op, ascending=(ordem_op == 'ascending')
                )

                barras_dinamicas_op = alt.Chart(ranking_dinamico_op_df).mark_bar(
                    cornerRadius=5, height=25
                ).encode(
                    x=alt.X(f'{coluna_valor_op}:Q', title=titulo_eixo_op, axis=alt.Axis(format='.0f')),
                    y=alt.Y('NOME_CURTO:N', title=None, 
                            sort=alt.EncodingSortField(field=coluna_ordem_op, op="min", order=ordem_op),
                            axis=alt.Axis(labelFontSize=14, labelLimit=0)),
                    color=alt.Color(f'{coluna_valor_op}:Q', scale=alt.Scale(scheme=cor_esquema_op, reverse=(ordem_op == 'ascending')), legend=None),
                    tooltip=[
                        alt.Tooltip('NOME_CURTO', title='Motorista'),
                        alt.Tooltip('OCUPACAO_MEDIA_CARGA', title='Ocupação Média', format='.1f'),
                        alt.Tooltip('MEDIA_ENTREGAS_VIAGEM', title='Média de Entregas', format='.1f'),
                        alt.Tooltip('DISTANCIA_MEDIA_VIAGEM', title='Distância Média', format=',.0f')
                    ]
                )
                
                # O resto da lógica do gráfico continua igual...
                texto_dinamico_op = barras_dinamicas_op.transform_calculate(
                    text_label=formato_label_op.replace(f'datum.{coluna_valor_op}', f'datum.{coluna_valor_op}')
                ).mark_text(
                    align='left', baseline='middle', dx=5, fontSize=14
                ).encode(
                    text=alt.Text('text_label:N'), color=alt.value('white')
                )

                chart_dinamico_op = (barras_dinamicas_op + texto_dinamico_op).properties(
                    title={"text": selecao_ranking_op, "anchor": "start", "fontSize": 16, "fontWeight": "bold"},
                    height=alt.Step(35)
                ).configure_view(stroke=None).configure_axis(grid=False).configure_title(color='white')
                
                st.altair_chart(chart_dinamico_op, use_container_width=True)
            
            st.divider()

        # --- ▲▲▲ FIM DO BLOCO ATUALIZADO ▲▲▲



                # Tabela de Resumo das Viagens
        if motorista_sel != "(Todos)":
            st.markdown(f"### 📋 Resumo das Viagens 👨‍✈️{motorista_sel}")
        else:
            st.markdown("### 📋 Resumo de Todas as Viagens no Período")

        df_agrupado = df_motorista.copy()
        
        # Agrupa os dados por viagem para criar o resumo
        resumo_viagens = df_agrupado.groupby('VIAGEM_ID').agg(
            EMISSÃO=('EMIS_MANIF', 'first'), PLACA=('PLACA_CAVALO', 'first'), TIPO=('TIPO_CAVALO', 'first'),
            MOTORISTA=('MOTORISTA', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
            FRETE=('FRETE-R$', 'sum'), CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
            PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), ICMS=('ICMS-R$', 'sum'), PESO_KG=('PESO REAL (KG)', 'sum'),
            M3=('M3', 'sum'), VOLUMES=('VOLUMES', 'sum'), VALOR_MERC=('MERCADORIA-R$', 'sum'),
            ENTREGAS=('DEST_MANIF', 'nunique'), QTDE_CTRC=('QTDE_CTRC', 'sum')
        ).reset_index()

        # Calcula colunas adicionais
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

        # Renomeia as colunas para exibição
        resumo_viagens.rename(columns={
            'VIAGEM_ID': '🧭 Viagem', 'TIPO': 'Tipo Veículo', 'DESTINOS': 'Destinos da Rota', 
            'PESO_KG': 'Peso Total', 'M3_corrigido': 'Volume Total (M³)', 'VOLUMES': 'Volumes Totais', 
            'VALOR_MERC': 'Valor Mercadoria', 'QTDE_CTRC': 'Qtd. CTRCs',
        }, inplace=True)

        # --- INÍCIO DO CÓDIGO ATUALIZADO ---

        # 1. Define a ordem das colunas e cria a lista ANTES de usá-la
        ordem_final_renomeada = [
            '🧭 Viagem', 'EMISSÃO', 'PLACA', 'Tipo Veículo', 'Destinos da Rota', 'MOTORISTA', 'Distância (KM)',
            'ENTREGAS', 'Custo (CTRB/OS)', 'CTRB/Frete (%)', 'FRETE', 'ICMS', 'Peso Total',
            'Volume Total (M³)', 'Qtd. CTRCs', 'Volumes Totais', 'Valor Mercadoria'
        ]
        colunas_para_exibir_e_exportar = [col for col in ordem_final_renomeada if col in resumo_viagens.columns]

        # 2. Cria o DataFrame para exportação com os dados brutos (antes da formatação)
        df_para_exportar = resumo_viagens[colunas_para_exibir_e_exportar].copy()

        # 3. Funções de formatação reutilizáveis
        def formatar_moeda_br(valor):
            try: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError): return "R$ 0,00"

        def formatar_peso_br(valor):
            try: return f"{valor:,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError): return "0,00 kg"

        # 4. Aplica a formatação em cada coluna do DataFrame que será exibido
        if 'EMISSÃO' in resumo_viagens.columns:
            resumo_viagens['EMISSÃO'] = pd.to_datetime(resumo_viagens['EMISSÃO']).dt.strftime('%d/%m/%Y')
        
        colunas_moeda = ['Custo (CTRB/OS)', 'FRETE', 'Valor Mercadoria', 'ICMS']
        for col in colunas_moeda:
            if col in resumo_viagens.columns:
                resumo_viagens[col] = resumo_viagens[col].apply(formatar_moeda_br)

        if 'Peso Total' in resumo_viagens.columns:
            resumo_viagens['Peso Total'] = resumo_viagens['Peso Total'].apply(formatar_peso_br)
        
        if 'Distância (KM)' in resumo_viagens.columns:
            resumo_viagens['Distância (KM)'] = resumo_viagens['Distância (KM)'].apply(lambda x: f"{int(x)} km")
        
        if 'Volume Total (M³)' in resumo_viagens.columns:
            resumo_viagens['Volume Total (M³)'] = resumo_viagens['Volume Total (M³)' ].apply(lambda x: f"{x:,.3f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # 5. Lógica de estilização para a coluna de percentual
        resumo_viagens['CTRB/Frete (%)_valor_numerico'] = resumo_viagens['CTRB/Frete (%)']

        if 'CTRB/Frete (%)' in resumo_viagens.columns:
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)'].apply(lambda x: f"{x:,.0f}%".replace(",", "."))

        # 6. Seleciona as colunas para exibição ANTES de aplicar o estilo
        df_para_exibir_formatado = resumo_viagens[colunas_para_exibir_e_exportar]

        # 7. Aplica o estilo ao DataFrame já fatiado
        styled_df = df_para_exibir_formatado.style.background_gradient(
            cmap='Reds', 
            subset=['CTRB/Frete (%)'], 
            gmap=resumo_viagens['CTRB/Frete (%)_valor_numerico'] # gmap ainda usa o df original com dados numéricos
        )

        # 8. Exibe o DataFrame ESTILIZADO
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # --- FIM DO CÓDIGO ATUALIZADO ---

        # O botão de download continua usando o df_para_exportar (não formatado)
        excel_bytes = to_excel(df_para_exportar)
        st.download_button(
            label="📤 Exportar Resumo para Excel", data=excel_bytes,
            file_name=f"resumo_viagens_{motorista_sel.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        
        # ▼▼▼ SUBSTITUA O BLOCO DA TABELA "DETALHES" POR ESTE ▼▼▼

        # A tabela detalhada só aparece se um motorista específico for selecionado.
        if motorista_sel != "(Todos)":
            st.divider() 
            st.subheader("📄 Detalhes dos Documentos da Viagem")

            df_detalhado_base = df_motorista.copy()

            # 1. Funções para unificar as colunas de custo
            def calcular_custo_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)

            def obter_numero_documento_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('NUM_OS', '')
                return row.get('NUM_CTRB', '')

            # 2. Aplica as funções para criar as novas colunas
            df_detalhado_base['Custo (CTRB/OS)'] = df_detalhado_base.apply(calcular_custo_unificado, axis=1)
            df_detalhado_base['Nº CTRB/OS'] = df_detalhado_base.apply(obter_numero_documento_unificado, axis=1)

            # 3. Define a lista de colunas a serem exibidas
            colunas_para_exibir = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS',          # <-- Coluna unificada
                'Custo (CTRB/OS)',     # <-- Coluna unificada
                'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            
            colunas_existentes = [col for col in colunas_para_exibir if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes].copy()

            # 4. Renomeia as colunas para a exibição
            df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino', 'PLACA_CAVALO': 'PLACA', 'TIPO_CAVALO': 'TIPO',
                'QTDE_CTRC': 'Qtd. CTRCs'
            }, inplace=True)

            # 5. Formata os valores
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')
            
            colunas_moeda_det = ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)
                    
            if 'PESO REAL (KG)' in df_detalhado_final.columns:
                df_detalhado_final['PESO REAL (KG)'] = df_detalhado_final['PESO REAL (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
                
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].apply(corrigir_volume_numerico).apply(lambda x: formatar_numero(x, 3))

            # 6. Exibe a tabela final
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)
            
            # 7. Botão de download
            try:
                excel_bytes_detalhado = to_excel(df_detalhado_final)
                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=f"detalhes_motorista_{motorista_sel.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado_motorista"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel detalhado: {e}")

        # ▲▲▲ FIM DO BLOCO SUBSTITUÍDO ▲▲▲


with tab5:
    # ▼▼▼ AQUI ESTÁ A MUDANÇA ▼▼▼
    # Substitua a linha st.header("📋 Análise de Rotas") por este bloco:
    st.markdown("""
        <div class="title-block-rotas">
            <i class="fa-solid fa-route"></i>
            <h2>Desempenho de Análise de Rotas</h2>
        </div>
    """, unsafe_allow_html=True)
    # ▲▲▲ FIM DA MUDANÇA ▲▲▲

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # ✅ Proteção para evitar travamento quando há múltiplas rotas do mesmo motorista
        if df_filtrado['MOTORISTA'].nunique() == 1 and df_filtrado['PLACA_CAVALO'].nunique() > 1:
            st.info("🔎 Foram encontradas várias viagens para o mesmo motorista. "
                    "Selecione também uma rota específica no filtro 🗺️ para visualizar o mapa e os detalhes da rota.")
            st.stop()
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
    
        # --- Inicializa estado de sessão com segurança ---
    st.session_state.setdefault('rota_clicada_id', None)

    # --- Variáveis possivelmente definidas fora deste escopo ---
    rota_sel_visivel = globals().get('rota_sel_visivel', "(Todos)")
    rotas_df = globals().get('rotas_df', pd.DataFrame())
    df_filtrado = globals().get('df_filtrado', pd.DataFrame())
    df_original = globals().get('df_original', df_filtrado.copy())

    # Se um filtro de rota for selecionado na sidebar, ele tem prioridade
    if rota_sel_visivel != "(Todos)":
        try:
            viagem_selecionada = rotas_df[rotas_df['NOME_ROTA'] == rota_sel_visivel]
            if not viagem_selecionada.empty:
                placa = viagem_selecionada['PLACA_CAVALO'].iloc[0]
                data = viagem_selecionada['DIA_EMISSAO_STR'].iloc[0]
                st.session_state['rota_clicada_id'] = (placa, data)
        except Exception:
            st.session_state['rota_clicada_id'] = None  # limpa se algo falhar

    # --- Funções ---
    def obter_geometria_rota(pontos_da_rota):
        if not pontos_da_rota or len(pontos_da_rota) < 2:
            return None, 0
        coordenadas_str = ";".join([f"{lon},{lat}" for lat, lon in pontos_da_rota])
        url = f"http://router.project-osrm.org/route/v1/driving/{coordenadas_str}?overview=full&geometries=polyline"
        try:
            resposta = requests.get(url, timeout=15)
            resposta.raise_for_status()
            dados_rota = resposta.json()
            geometria_codificada = dados_rota['routes'][0]['geometry']
            distancia_metros = dados_rota['routes'][0].get('distance', 0)
            tracado_rota = polyline.decode(geometria_codificada)
            distancia_km = round(distancia_metros / 1000)
            return tracado_rota, distancia_km
        except Exception:
            return None, 0

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

    # --- Lógica de exibição: visão geral vs detalhe ---
    if st.session_state.get('rota_clicada_id') is None:
        # ----------------------------------------
        # MODO 1: VISÃO GERAL (NENHUMA ROTA CLICADA)
        # ----------------------------------------
        # Visão geral com todos os marcadores
        st.markdown("### 🗺️ Trajeto da Viagem")
        st.info("Clique em um marcador de destino 🚚 no mapa para ver os detalhes da rota específica.")

        m = folium.Map(
            location=[-19.5, -54.5],
            zoom_start=7,
            tiles='https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps - Satélite'
        )
        folium.TileLayer(
            'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps - Ruas'
        ).add_to(m)
        folium.LayerControl().add_to(m)

        # Previna erro se df_filtrado vazio ou sem colunas esperadas
        if df_filtrado is None or df_filtrado.empty or 'PLACA_CAVALO' not in df_filtrado.columns:
            st.warning("Nenhuma viagem disponível para plotar.")
            # ▼▼▼ ADICIONE ESTA LINHA ▼▼▼
            
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            for (placa, dia_emissao), df_viagem in df_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR']):
                origem_viagem = df_viagem['CIDADE_UF_ORIGEM'].iloc[0]
                if origem_viagem in locais:
                    folium.Marker(
                        locais[origem_viagem],
                        popup=f"Origem: {origem_viagem}",
                        # Adicionando tooltip para a origem também
                        tooltip=f"Partida: {origem_viagem}",
                        icon=folium.Icon(color='blue', icon='home', prefix='fa')
                    ).add_to(m)

                for _, row in df_viagem.iterrows():
                    dest = row.get('CIDADE_UF_DEST')
                    if dest in locais:
                        popup_html = f"<strong>Destino: {dest}</strong><br>Veículo: {placa}<br>Data: {dia_emissao}"
                        folium.Marker(
                            locais[dest],
                            popup=popup_html,
                            tooltip=f"Destino: {dest}", 
                            icon=folium.Icon(color='red', icon='truck', prefix='fa')
                        ).add_to(m)

            map_data = st_folium(m, use_container_width=True, height=800)

            # st_folium pode retornar chaves diferentes dependendo da versão; checamos várias
            popup_text = None
            if map_data:
                popup_text = map_data.get("last_object_clicked_popup") or map_data.get("last_object_clicked") or map_data.get("last_clicked")
            if popup_text:
                try:
                    # tolera <br> ou quebras de linha simples
                    if "<br>" in popup_text:
                        placa_clicada = popup_text.split("Veículo: ")[1].split("<br>")[0].strip()
                        data_clicada = popup_text.split("Data: ")[1].strip()
                    else:
                        placa_clicada = popup_text.split("Veículo: ")[1].splitlines()[0].strip()
                        data_clicada = popup_text.split("Data: ")[1].splitlines()[0].strip()

                    st.session_state['rota_clicada_id'] = (placa_clicada, data_clicada)
                    st.rerun()

                except Exception:
                    # se não for possível extrair, ignora (provavelmente clicou na origem)
                    pass

            st.divider()
            st.markdown("### 📊 Dados das Viagens (Visão Geral)")
            st.dataframe(df_filtrado, use_container_width=True)

    else:
        # -------------------------------------------------
        # MODO 2: DETALHE DA ROTA (APÓS CLICAR NO MAPA)
        # -------------------------------------------------
        # Visão de detalhe para a rota selecionada
        placa_selecionada, data_selecionada = st.session_state['rota_clicada_id']
        df_detalhe = df_original[
            (df_original['PLACA_CAVALO'] == placa_selecionada) &
            (df_original['DIA_EMISSAO_STR'] == data_selecionada)
        ].copy()

        # --- CABEÇALHO ---
        st.markdown(f"### 🏙️ Detalhes da Rota: {placa_selecionada} em {data_selecionada}")

        # --- CSS dos cards ---
        st.markdown("""
        <style>
        .detail-section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .detail-card {
            background-color: #1F2937;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #374151;
            height: 100%;
            margin-bottom: 1rem;
        }
        .detail-card-title {
            font-size: 1rem;
            font-weight: 600;
            color: #E5E7EB;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .detail-card-title .fa-map-pin { color: #EF4444; }
        .detail-grid {  
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .metric-item {
            background-color: #111827;
            padding: 12px;
            border-radius: 8px;
        }
        .metric-label {
            font-size: 0.8rem;
            color: #9CA3AF;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .metric-value {
            font-size: 1rem;
            font-weight: 600;
            color: #FFFFFF;
        }
        .metric-label .fa-weight-hanging { color: #F59E0B; }
        .metric-label .fa-cube { color: #3B82F6; }
        .metric-label .fa-hand-holding-dollar { color: #22C55E; }
        .metric-label .fa-truck-ramp-box { color: #22C55E; }
        .metric-label .fa-file-invoice { color: #8B5CF6; }
        .metric-label .fa-boxes-stacked { color: #F97316; }
        </style>
        """, unsafe_allow_html=True)

        # --- AGREGA OS DADOS ---
        carga_por_cidade = df_detalhe.groupby('CIDADE_UF_DEST').agg(
            PESO_TOTAL=('PESO REAL (KG)', 'sum'),
            VOLUME_TOTAL=('M3', 'sum'),
            FRETE_TOTAL=('FRETE-R$', 'sum'),
            VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
            QTDE_CTRC=('QTDE_CTRC', 'sum'),
            QTDE_VOLUME=('VOLUMES', 'sum')
        ).reset_index()

        # --- FUNÇÕES DE FORMATAÇÃO ---
        def fmt_moeda(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        def fmt_num(v): return f"{v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        def fmt_m3(v): return f"{v:,.1f}".replace(".", ",")

        # --- BLOCO DE KPIs POR CIDADE (AGORA DIVIDIDO EM SEÇÕES) ---
        num_cidades = len(carga_por_cidade)
        cols = st.columns(num_cidades if num_cidades > 0 else 1)

        for i, row in carga_por_cidade.iterrows():
            with cols[i]:
                html = f"""
        <div class="detail-card">
        <div class="detail-card-title">
            <i class="fa-solid fa-map-pin"></i> {row['CIDADE_UF_DEST']}
        </div>

        <div class="detail-section-title"><i class="fa-solid fa-chart-line"></i> Indicadores de Performance</div>
        <div class="detail-grid">
            <div class="metric-item">
            <div class="metric-label"><i class="fa-solid fa-hand-holding-dollar"></i> Frete Total</div>
            <div class="metric-value">{fmt_moeda(row['FRETE_TOTAL'])}</div>
            </div>
            <div class="metric-item">
            <div class="metric-label"><i class="fa-solid fa-truck-ramp-box"></i> Mercadoria</div>
            <div class="metric-value">{fmt_moeda(row['VALOR_MERCADORIA'])}</div>
            </div>
            <div class="metric-item">
            <div class="metric-label"><i class="fa-solid fa-weight-hanging"></i> Peso</div>
            <div class="metric-value">{fmt_num(row['PESO_TOTAL'])} kg</div>
            </div>
            <div class="metric-item">
            <div class="metric-label"><i class="fa-solid fa-cube"></i> Cubagem</div>
            <div class="metric-value">{fmt_m3(row['VOLUME_TOTAL'])} m³</div>
            </div>
        </div>

        <div class="detail-section-title"><i class="fa-solid fa-gears"></i> Indicadores Operacionais</div>
        <div class="detail-grid">
            <div class="metric-item">
            <div class="metric-label"><i class="fa-solid fa-file-invoice"></i> CTRCs</div>
            <div class="metric-value">{fmt_num(row['QTDE_CTRC'])}</div>
            </div>
            <div class="metric-item">
            <div class="metric-label"><i class="fa-solid fa-boxes-stacked"></i> Qtd. Volumes</div>
            <div class="metric-value">{fmt_num(row['QTDE_VOLUME'])}</div>
            </div>
        </div>
        </div>
        """
                st.markdown(html, unsafe_allow_html=True)

        # Dentro de "with tab5:", na seção "else" onde st.session_state['rota_clicada_id'] não é None

        # --- 📊 NOVO BLOCO: INDICADORES CONSOLIDADOS DA ROTA (DINÂMICO) ---
        st.markdown("""
        <hr style="border: 1px solid #333; margin: 30px 0;">
        <h3 style="color:#fff; margin-bottom:10px;">
            📈 Indicadores Consolidados da Rota
        </h3>
        """, unsafe_allow_html=True)

        # --- 1. PREPARAÇÃO DOS PONTOS PARA O CÁLCULO DA DISTÂNCIA ---
        pontos_para_distancia = []
        if not df_detalhe.empty:
            origem_nome = df_detalhe['CIDADE_UF_ORIGEM'].iloc[0]
            if origem_nome in locais:
                pontos_para_distancia.append(locais[origem_nome])

            destinos_ordenados_dist = df_detalhe.sort_values(by='EMIS_MANIF')['CIDADE_UF_DEST'].unique()
            for dest in destinos_ordenados_dist:
                if dest in locais and locais[dest] not in pontos_para_distancia:
                    pontos_para_distancia.append(locais[dest])

        # --- 2. CÁLCULO DE TODOS OS KPIs DINÂMICOS ---
        distancia_total_rota, _ = obter_geometria_rota(pontos_para_distancia)
        distancia_total_rota = _ # A função retorna a distância como segundo argumento

        # Garante que a coluna de custo unificada exista
        if 'Custo (CTRB/OS)' not in df_detalhe.columns:
            def calcular_custo_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)
            df_detalhe['Custo (CTRB/OS)'] = df_detalhe.apply(calcular_custo_unificado, axis=1)

        # Cálculos principais
        peso_total_rota = df_detalhe['PESO REAL (KG)'].sum()
        entregas_rota = df_detalhe['DEST_MANIF'].nunique()
        custo_total_rota = df_detalhe['Custo (CTRB/OS)'].sum()
        frete_total_rota = df_detalhe['FRETE-R$'].sum()

        # Cálculos derivados (com proteção contra divisão por zero)
        perc_custo_frete = (custo_total_rota / frete_total_rota * 100) if frete_total_rota > 0 else 0
        custo_por_km = (custo_total_rota / distancia_total_rota) if distancia_total_rota > 0 else 0
        frete_por_km = (frete_total_rota / distancia_total_rota) if distancia_total_rota > 0 else 0

        # --- 3. FORMATAÇÃO DOS VALORES PARA EXIBIÇÃO ---
        distancia_formatada = f"{distancia_total_rota:,.0f} km".replace(",", ".")
        peso_formatado = f"{peso_total_rota:,.0f} kg".replace(",", ".")
        entregas_formatadas = str(entregas_rota)
        perc_custo_frete_formatado = f"{perc_custo_frete:.1f}%".replace(".", ",")
        custo_por_km_formatado = formatar_moeda(custo_por_km) # Reutiliza sua função de formatação
        frete_por_km_formatado = formatar_moeda(frete_por_km) # Reutiliza sua função de formatação

        # --- 4. EXIBIÇÃO DOS KPIs EM COLUNAS ---
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        kpi_cards = {
            col1: {"icon": "fa-route", "title": "Viagens", "value": "1"},
            col2: {"icon": "fa-road", "title": "Distância Total", "value": distancia_formatada},
            col3: {"icon": "fa-weight-hanging", "title": "Peso Total", "value": peso_formatado},
            col4: {"icon": "fa-boxes-stacked", "title": "Entregas", "value": entregas_formatadas},
            col5: {"icon": "fa-gas-pump", "title": "Custo / Frete", "value": perc_custo_frete_formatado},
            col6: {"icon": "fa-leaf", "title": "Custo / Km", "value": custo_por_km_formatado},
            col7: {"icon": "fa-truck", "title": "Frete / Km", "value": frete_por_km_formatado}
        }

        for col, data in kpi_cards.items():
            with col:
                st.markdown(f"""
                <div class="detail-card">
                    <div class="detail-card-title"><i class="fa-solid {data['icon']}"></i> {data['title']}</div>
                    <div class="metric-value" style="font-size: 1.2rem;">{data['value']}</div>
                </div>
                """, unsafe_allow_html=True)

                # COLE TODO ESTE BLOCO AQUI

        st.markdown("""
        <hr style="border: 1px solid #333; margin: 20px 0;">
        <h3 style="color:#fff; margin-bottom:10px;">
            ⚖️ Análise de Ocupação de Carga na Rota
        </h3>
        """, unsafe_allow_html=True)

        # --- 1. CÁLCULO DOS DADOS DE OCUPAÇÃO E CAPACIDADE ---
        if not df_detalhe.empty:
            # Pega o peso e volume totais da viagem selecionada
            peso_total_viagem = df_detalhe['PESO REAL (KG)'].sum()
            volume_total_viagem = df_detalhe['M3'].sum()

            # Corrige o volume se necessário
            if volume_total_viagem > 1000:
                volume_total_viagem /= 10000

            # Determina o tipo do veículo da viagem
            tipo_veiculo_viagem = df_detalhe['TIPO_CAVALO'].iloc[0]

            # --- LÓGICA DE CAPACIDADE DINÂMICA ---
            if tipo_veiculo_viagem == 'CAVALO':
                capacidade_peso_kg = df_detalhe['CAPACIDADE_KG'].iloc[0]
            else:
                capacidade_peso_kg = df_detalhe['CAPAC_CAVALO'].iloc[0]

            capacidades_volume_por_tipo = {'TOCO': 55, 'TRUCK': 75, 'CAVALO': 110, 'PADRAO': 80}
            capacidade_volume_m3 = capacidades_volume_por_tipo.get(str(tipo_veiculo_viagem).upper(), 80)

            # --- 2. CÁLCULO DE OCUPAÇÃO E OCIOSIDADE ---
            ocupacao_peso_perc = (peso_total_viagem / capacidade_peso_kg * 100) if capacidade_peso_kg > 0 else 0
            ociosidade_peso_perc = 100 - ocupacao_peso_perc
            potencial_nao_utilizado_kg = max(0, capacidade_peso_kg - peso_total_viagem)

            ocupacao_volume_perc = (volume_total_viagem / capacidade_volume_m3 * 100) if capacidade_volume_m3 > 0 else 0
            ociosidade_volume_perc = 100 - ocupacao_volume_perc
            potencial_nao_utilizado_m3 = max(0, capacidade_volume_m3 - volume_total_viagem)

            # --- 3. LÓGICA DE CORES PARA AS BARRAS ---
            def obter_cor_ocupacao(percentual):
                if percentual < 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
                elif percentual < 80: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)"

            def obter_cor_ociosidade(percentual):
                if percentual > 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
                elif percentual > 20: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)"

            # --- 4. RENDERIZAÇÃO DOS CARDS VISUAIS ---
            col_ocup_1, col_ocup_2 = st.columns(2, gap="large")

            with col_ocup_1:
                # Card de Ocupação de Peso
                st.markdown(f"""
                <div class="ocupacao-card-custom">
                    <div class="progress-card-header">
                        <div class="progress-card-title">⚖️ Ocupação de Peso (KG)</div>
                        <div class="progress-card-value">{ocupacao_peso_perc:.0f}%</div>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {min(ocupacao_peso_perc, 100)}%; background: {obter_cor_ocupacao(ocupacao_peso_perc)};"></div>
                    </div>
                    <div class="progress-card-footer">
                        <span>Total: {formatar_numero(peso_total_viagem)} KG</span>
                        <span>Capacidade: {formatar_numero(capacidade_peso_kg)} KG</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Card de Ociosidade de Peso
                cor_ocios_peso = obter_cor_ociosidade(ociosidade_peso_perc)
                borda_ocios_peso = cor_ocios_peso.split(',')[1].strip()
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {borda_ocios_peso}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                    <span><i class="fa-solid fa-scale-unbalanced-flip"></i> <b>Ociosidade de Peso:</b> {ociosidade_peso_perc:.0f}%</span>
                    <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                        <div style="width: {min(ociosidade_peso_perc, 100)}%; height: 100%; background: {cor_ocios_peso};"></div>
                    </div>
                    <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(potencial_nao_utilizado_kg)} KG</span>
                </div>
                """, unsafe_allow_html=True)

            with col_ocup_2:
                # Card de Ocupação de Cubagem
                st.markdown(f"""
                <div class="ocupacao-card-custom">
                    <div class="progress-card-header">
                        <div class="progress-card-title">📦 Ocupação de Cubagem (M³)</div>
                        <div class="progress-card-value">{ocupacao_volume_perc:.0f}%</div>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {min(ocupacao_volume_perc, 100)}%; background: {obter_cor_ocupacao(ocupacao_volume_perc)};"></div>
                    </div>
                    <div class="progress-card-footer">
                        <span>Total: {formatar_numero(volume_total_viagem, 3)} M³</span>
                        <span>Capacidade: {formatar_numero(capacidade_volume_m3)} M³</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Card de Ociosidade de Cubagem
                cor_ocios_vol = obter_cor_ociosidade(ociosidade_volume_perc)
                borda_ocios_vol = cor_ocios_vol.split(',')[1].strip()
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {borda_ocios_vol}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                    <span><i class="fa-solid fa-box-open"></i> <b>Ociosidade de Cubagem (M³):</b> {ociosidade_volume_perc:.0f}%</span>
                    <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                        <div style="width: {min(ociosidade_volume_perc, 100)}%; height: 100%; background: {cor_ocios_vol};"></div>
                    </div>
                    <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(potencial_nao_utilizado_m3, 2)} M³</span>
                </div>
                """, unsafe_allow_html=True)

        # FIM DO BLOCO PARA COLAR


        # --- MAPA ABAIXO DOS INDICADORES ---
        st.markdown("### 🗺️ Trajeto da Viagem")

        mapa_detalhe = folium.Map(
            location=[-19.5, -54.5],
            zoom_start=5,
            tiles='https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps - Satélite'
        )
        folium.TileLayer(
            'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps - Ruas'
        ).add_to(mapa_detalhe)

        pontos_marcadores = []
        if not df_detalhe.empty:
            origem_nome = df_detalhe['CIDADE_UF_ORIGEM'].iloc[0]
            if origem_nome in locais:
                pontos_marcadores.append(locais[origem_nome])
                folium.Marker(locais[origem_nome], popup=f"Origem: {origem_nome}",
                            icon=folium.Icon(color='blue', icon='home', prefix='fa')).add_to(mapa_detalhe)

            destinos_ordenados = df_detalhe.sort_values(by='EMIS_MANIF')['CIDADE_UF_DEST'].unique()
            for dest in destinos_ordenados:
                if dest in locais:
                    if locais[dest] not in pontos_marcadores:
                        pontos_marcadores.append(locais[dest])
                    popup_html = f"<strong>Destino: {dest}</strong><br>Veículo: {placa_selecionada}<br>Data: {data_selecionada}"
                    folium.Marker(locais[dest], popup=popup_html,
                                icon=folium.Icon(color='red', icon='truck', prefix='fa')).add_to(mapa_detalhe)

        tracado, dist = obter_geometria_rota(pontos_marcadores)
        if tracado:
            folium.PolyLine(tracado, weight=5, opacity=0.8, tooltip=f"Distância: {dist} km").add_to(mapa_detalhe)
            lats = [p[0] for p in tracado]
            lons = [p[1] for p in tracado]
            mapa_detalhe.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

        folium.LayerControl().add_to(mapa_detalhe)
        st_folium(mapa_detalhe, use_container_width=True, height=700)

                # --- INÍCIO DO BLOCO DA TABELA DE DADOS (ATUALIZADO) ---
        st.divider()
        st.markdown("### 📊 Dados das Viagens")

        # 1. Cria uma cópia do DataFrame de detalhes para trabalhar
        df_tabela_detalhada = df_detalhe.copy()

        # 2. Lógica de Custo Unificado (essencial para as colunas de custo)
        def calcular_custo_final(row):
            if 'PROPRIETARIO_CAVALO' in row and row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                return row.get('OS-R$', 0)
            return row.get('CTRB-R$', 0)

        def obter_numero_documento(row):
            if 'PROPRIETARIO_CAVALO' in row and row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                return row.get('NUM_OS', '')
            return row.get('NUM_CTRB', '')

        df_tabela_detalhada['Custo (CTRB/OS)'] = df_tabela_detalhada.apply(calcular_custo_final, axis=1)
        df_tabela_detalhada['Nº CTRB/OS'] = df_tabela_detalhada.apply(obter_numero_documento, axis=1)

        # 3. Define a lista de colunas que você quer exibir, na ordem correta
        colunas_para_mostrar = [
            'NUM_MANIF', 'DEST_MANIF', 'PLACA_CAVALO', 'MOTORISTA', 'FRETE-R$',
            'Nº CTRB/OS', 'Custo (CTRB/OS)', 'M3', 'PESO REAL (KG)', 'MERCADORIA-R$',
            'VOLUMES', 'QTDE_CTRC'
        ]
        
        # Garante que só colunas existentes sejam selecionadas
        colunas_existentes = [col for col in colunas_para_mostrar if col in df_tabela_detalhada.columns]
        df_tabela_final = df_tabela_detalhada[colunas_existentes]

        # 4. Cria uma cópia para exportação ANTES de formatar os valores
        df_para_exportar = df_tabela_final.copy()

        # 5. Formata as colunas para exibição
        # Funções de formatação
        def formatar_moeda_br(valor):
            try: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError): return "R$ 0,00"

        def formatar_peso_br(valor):
            try: return f"{valor:,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError): return "0,00 kg"

        # Aplica a formatação
        colunas_moeda = ['FRETE-R$', 'Custo (CTRB/OS)', 'MERCADORIA-R$']
        for col in colunas_moeda:
            if col in df_tabela_final.columns:
                df_tabela_final[col] = df_tabela_final[col].apply(formatar_moeda_br)

        if 'PESO REAL (KG)' in df_tabela_final.columns:
            df_tabela_final['PESO REAL (KG)'] = df_tabela_final['PESO REAL (KG)'].apply(formatar_peso_br)

        # 6. Exibe a tabela final, já formatada
        st.dataframe(df_tabela_final, use_container_width=True, hide_index=True)

        # 7. Botão de Download (usando o df_para_exportar com dados não formatados)
        try:
            excel_bytes_rota = to_excel(df_para_exportar)
            st.download_button(
                label="📥 Download Dados da Rota (Excel)",
                data=excel_bytes_rota,
                file_name=f"dados_detalhados_{placa_selecionada}_{data_selecionada}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_detalhes_rota"
            )
        except Exception as e:
            st.error(f"❌ Erro ao gerar o arquivo Excel: {e}")

        # 8. Botão para voltar à visão geral
        if st.button("⬅️ Voltar para a Visão Geral"):
            st.session_state['rota_clicada_id'] = None
            st.rerun()

        # --- FIM DO BLOCO ATUALIZADO ---


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