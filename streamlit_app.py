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
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, BoundaryNorm
import altair as alt
import numpy as np # Adicione esta linha no topo do seu arquivo se ainda não tiver
import folium
from streamlit_folium import st_folium
import requests
import polyline # Biblioteca para decodificar a geometria da rota
from folium import plugins # <<< ADICIONE ESTA LINHA
from folium.plugins import Fullscreen


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
            
/* ▼▼▼ NOVO ESTILO PARA O SELETOR DE ROTA ▼▼▼ */

/* Container que envolve o rótulo e o seletor */
.custom-selectbox-container {
    margin-top: 15px; /* Espaço acima */
    margin-bottom: 25px; /* Espaço abaixo */
}

/* Estilo para o rótulo (label) "SELECIONE A ROTA..." */
.custom-selectbox-label {
    font-family: "Poppins", "Segoe UI", sans-serif;
    font-size: 0.9rem; /* Tamanho da fonte */
    font-weight: 600; /* Negrito */
    color: #A0AEC0; /* Cinza claro, menos chamativo */
    text-transform: uppercase; /* Caixa alta */
    letter-spacing: 0.8px; /* Espaçamento entre letras */
    margin-bottom: 8px; /* Espaço entre o rótulo e a caixa */
    display: flex;
    align-items: center;
    gap: 8px; /* Espaço entre o ícone e o texto */
}

/* Estilo para o próprio seletor (a caixa de seleção) */
.stSelectbox > div {
    background-color: #1A202C; /* Fundo escuro (azul-acinzentado) */
    border: 1px solid #2D3748; /* Borda sutil */
    border-radius: 10px; /* Bordas arredondadas */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* Sombra interna suave */
    transition: border-color 0.3s ease, box-shadow 0.3s ease; /* Animação suave */
}

/* Efeito ao passar o mouse (hover) */
.stSelectbox > div:hover {
    border-color: #4A90E2; /* Borda azul ao passar o mouse */
    box-shadow: 0 0 10px rgba(74, 144, 226, 0.3); /* Brilho azul */
}

/* Cor do texto dentro do seletor */
.stSelectbox div[data-baseweb="select"] > div {
    color: #E2E8F0;
}

/* Cor da setinha (dropdown arrow) */
.stSelectbox svg {
    color: #A0AEC0;
}

/* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */

            
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
            
/* Aba 6 (Análise Temporal) - Ciano/Azul-Petróleo */
.stTabs [data-baseweb="tab"]:nth-child(6)[aria-selected="true"] {
    background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); /* Gradiente Ciano */
    color: #ffffff;
    border-color: #0d9488;
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
.stTabs [data-baseweb="tab"]:nth-child(6)::before { content: "\\f133"; } /* fa-calendar-days (Análise Temporal) */

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
            
    /* ▼▼▼ NOVO ESTILO PARA O TÍTULO DA ABA TEMPORAL ▼▼▼ */
    .title-block-temporal {
        background: #1C1A29; /* Fundo escuro padrão */
        
        /* Bordas laterais na cor CIANO para combinar com a aba */
        border-left: 5px solid #14b8a6;
        border-right: 5px solid #14b8a6;
        
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

    .title-block-temporal h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Ícone específico para este bloco de título */
    .title-block-temporal .fa-chart-simple {
        font-size: 2.0rem; /* Tamanho do ícone */
        color: #14b8a6;   /* Cor do ícone (Ciano) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */

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

# =================================================
# 🔹 CONFIGURAÇÕES GLOBAIS E REGRAS DE NEGÓCIO
# =================================================

# --- DICIONÁRIO DE ROTAS COMPOSTAS ---
# A ordem é importante: rotas mais abrangentes (com mais siglas) devem vir primeiro.
ROTAS_COMPOSTAS = {
    # Rotas com múltiplos destinos
    "ROTA SÃO PAULO": {"CSL", "PBA", "ATB", "SPO"},
    "ROTA GOIÂNIA": {"PDA", "CDS", "GYN"},
    "ROTA COXIM": {"SNR", "PGO", "COX"},
    "ROTA BATAGUASSU": {"SRP", "BLD", "BAT"},
    "ROTA RIO BRILHANTE": {"RBT", "DOU"}, # Nome padronizado
    "ROTA SÃO GABRIEL": {"RVM", "SGO"},
    "ROTA MARACAJU": {"SDL", "MJU"},
    "ROTA JARDIM": {"NQU", "JDM"},
    "ROTA BODOQUENA": {"MDA", "BDQ"},
    "ROTA COSTA RICA": {"CMP", "CRC"},
    "ROTA IVINHEMA": {"NSU", "IVM"},
    "ROTA RIBAS": {"ACL", "RRP"},

    # Rotas com um único destino principal
    "ROTA DOURADOS": {"DOU"},
    "ROTA NOVA ANDRADINA": {"NAD"},
    "ROTA BONITO": {"BTO"},
    "ROTA AQUIDAUANA": {"AQU"},
    "ROTA PONTA PORÃ": {"PPR"},
    "ROTA TRÊS LAGOAS": {"TLG"},
    "ROTA CORUMBÁ": {"COR"},
}

# --- DICIONÁRIO PARA ORDENAÇÃO GEOGRÁFICA ---
# Define a sequência exata em que os destinos devem aparecer.
ORDEM_DAS_ROTAS = {
    # Rotas Compostas (na ordem de entrega desejada)
    "ROTA GOIÂNIA": ["PDA", "CDS", "GYN"],
    "ROTA COXIM": ["SNR", "PGO", "COX"],
    "ROTA SÃO PAULO": ["CSL", "PBA", "ATB", "SPO"],
    "ROTA BATAGUASSU": ["SRP", "BLD", "BAT"],
    "ROTA RIO BRILHANTE": ["RBT", "DOU"], # Nome padronizado
    "ROTA SÃO GABRIEL": ["RVM", "SGO"],
    "ROTA MARACAJU": ["SDL", "MJU"],
    "ROTA JARDIM": ["NQU", "JDM"],
    "ROTA BODOQUENA": ["MDA", "BDQ"],
    "ROTA COSTA RICA": ["CMP", "CRC"],
    "ROTA IVINHEMA": ["NSU", "IVM"],
    "ROTA RIBAS": ["ACL", "RRP"],

    # Rotas de destino único
    "ROTA DOURADOS": ["DOU"],
    "ROTA NOVA ANDRADINA": ["NAD"],
    "ROTA BONITO": ["BTO"],
    "ROTA AQUIDAUANA": ["AQU"],
    "ROTA PONTA PORÃ": ["PPR"],
    "ROTA TRÊS LAGOAS": ["TLG"],
    "ROTA CORUMBÁ": ["COR"],
}

# --- DICIONÁRIO PARA MAPEAMENTO DE SIGLA PARA NOME COMPLETO ---
# "Traduz" as siglas para os nomes completos que serão exibidos nos cards.
MAPA_SIGLA_NOME_COMPLETO = {
    # Rota Goiânia
    "PDA": "PARAISO DAS AGUAS/MS",
    "CDS": "CHAPADAO DO SUL/MS",
    "GYN": "GOIANIA/GO",

    # Rota Coxim
    "SNR": "SONORA/MS",
    "PGO": "PEDRO GOMES/MS",
    "COX": "COXIM/MS",

    # Rota São Paulo
    "CSL": "CASSILANDIA/MS",
    "PBA": "PARANAIBA/MS",
    "ATB": "APARECIDA DO TABOADO/MS",
    "SPO": "SAO PAULO/SP",

    # Rota Bataguassu
    "SRP": "SANTA RITA DO PARDO/MS",
    "BLD": "BRASILANDIA/MS",
    "BAT": "BATAGUASSU/MS",

    # Rota Rio Brilhante
    "RBT": "RIO BRILHANTE/MS",
    "DOU": "DOURADOS/MS",

    # Rota São Gabriel
    "RVM": "RIO VERDE DE MATO GROSSO/MS",
    "SGO": "SAO GABRIEL DO OESTE/MS",

    # Rota Maracaju
    "SDL": "SIDROLANDIA/MS",
    "MJU": "MARACAJU/MS",

    # Rota Jardim
    "NQU": "NIOAQUE/MS",
    "JDM": "JARDIM/MS",

    # Rota Bodoquena
    "MDA": "MIRANDA/MS",
    "BDQ": "BODOQUENA/MS",

    # Rota Costa Rica
    "CMP": "CAMAPUA/MS",
    "CRC": "COSTA RICA/MS",

    # Rota Ivinhema
    "NSU": "NOVA ALVORADA DO SUL/MS",
    "IVM": "IVINHEMA/MS",

    # Rota Ribas
    "ACL": "AGUA CLARA/MS",
    "RRP": "RIBAS DO RIO PARDO/MS",

    # Rotas de Destino Único
    "NAD": "NOVA ANDRADINA/MS",
    "BTO": "BONITO/MS",
    "AQU": "AQUIDAUANA/MS",
    "PPR": "PONTA PORA/MS",
    "TLG": "TRES LAGOAS/MS",
    "COR": "CORUMBA/MS"
}

# =================================================
# 🔹 MAPA PARA COORDENADAS DO MAPA
# =================================================
MAPA_ROTA_CIDADE = {
    # Rotas Compostas (Múltiplos Destinos)
    "ROTA COXIM": "Coxim, MS",
    "ROTA SÃO PAULO": "São Paulo, SP",
    "ROTA GOIÂNIA": "Goiânia, GO",
    "ROTA BATAGUASSU": "Bataguassu, MS",
    "ROTA RIO BRILHANTE": "Rio Brilhante, MS", # Nome padronizado
    "ROTA SÃO GABRIEL": "São Gabriel do Oeste, MS",
    "ROTA MARACAJU": "Maracaju, MS",
    "ROTA JARDIM": "Jardim, MS",
    "ROTA BODOQUENA": "Bodoquena, MS",
    "ROTA COSTA RICA": "Costa Rica, MS",
    "ROTA IVINHEMA": "Ivinhema, MS",
    "ROTA RIBAS": "Ribas do Rio Pardo, MS",

    # Rotas de Destino Único
    "ROTA DOURADOS": "Dourados, MS",
    "ROTA NOVA ANDRADINA": "Nova Andradina, MS",
    "ROTA BONITO": "Bonito, MS",
    "ROTA AQUIDAUANA": "Aquidauana, MS",
    "ROTA PONTA PORÃ": "Ponta Porã, MS",
    "ROTA TRÊS LAGOAS": "Três Lagoas, MS",
    "ROTA CORUMBÁ": "Corumbá, MS",
}


def classificar_viagens_do_dia(df):
    """
    Classifica as viagens com base na coluna 'CONFERENTE CARGA'.
    - Se 'CONFERENTE CARGA' começar com o código "253", a viagem é 'Viagem Extra'.
    - Caso contrário, é 'Rota Completa'.
    """
    # 1. Define o nome da coluna que será usada para a verificação.
    coluna_verificacao = 'CONFERENTE CARGA'

    # 2. Verifica se a coluna de verificação existe no DataFrame.
    if coluna_verificacao not in df.columns:
        # Se não existir, assume que todas são 'Rota Completa' e exibe um aviso.
        df['TIPO_VIAGEM_CALCULADO'] = 'Rota Completa'
        st.warning(f"Aviso: Coluna '{coluna_verificacao}' não encontrada. Não foi possível classificar 'Viagens Extras'.")
        return df

    # 3. Aplica a lógica de classificação.
    #    - Garante que a coluna seja do tipo string para usar funções de texto.
    #    - Usa .str.startswith("253") para verificar se o texto começa com o código.
    #    - 'na=False' trata valores nulos (NaN) como se não correspondessem.
    df['TIPO_VIAGEM_CALCULADO'] = np.where(
        df[coluna_verificacao].astype(str).str.strip().str.startswith("253", na=False),
        'Viagem Extra',      # Valor se a condição for verdadeira
        'Rota Completa'      # Valor se a condição for falsa
    )

    return df

# --- 2. FUNÇÕES DE APOIO ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e pré-processa os dados do arquivo Excel."""
    df = pd.read_excel(caminho, sheet_name=0)

    # Converte colunas de data
    for col in ['EMIS_MANIF', 'DIA_SAIDA_MANIF', 'DIA_CHEGADA_MANIF', 'DATA PREV CHEGADA']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # =========================================================
    # 🕔 CRIA DATA OPERACIONAL (VIRADA DE DIA)
    # =========================================================

    # Cria datetime real de saída (data + hora)
    df['DT_SAIDA_MANIF'] = pd.to_datetime(
        df['DIA_SAIDA_MANIF'].astype(str) + ' ' +
        df['HORA_SAIDA_MANIF'].astype(str),
        errors='coerce'
    )

    # Regra de virada de dia (05:00)
    HORA_CORTE_OPERACIONAL = 5

    df['DATA_OPERACIONAL'] = (
        df['DT_SAIDA_MANIF'] - pd.Timedelta(hours=HORA_CORTE_OPERACIONAL)
    ).dt.date

    # ▼▼▼ LINHA ADICIONADA PARA GARANTIR COMPATIBILIDADE ▼▼▼
    # Converte a coluna para o tipo datetime completo, necessário para os filtros.
    df['DATA_OPERACIONAL'] = pd.to_datetime(df['DATA_OPERACIONAL'])
    # ▲▲▲ FIM DA ADIÇÃO ▲▲▲

    # Garante que as colunas de texto sejam string
    for col_texto in ['LACRES', 'SITUACAO', 'OBSERVAÇÕES']:
        if col_texto in df.columns:
            df[col_texto] = df[col_texto].astype(str)

    return df


    # =========================================================

    # Garante que as colunas de texto sejam string
    for col_texto in ['LACRES', 'SITUACAO', 'OBSERVAÇÕES']:
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

# ▼▼▼ COLE AS FUNÇÕES DE FORMATAÇÃO AQUI ▼▼▼

def formatar_moeda(valor):
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    try:
        return locale.currency(valor, grouping=True)
    except (NameError, TypeError, ValueError):
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
    
    # ▼▼▼ COLE AS NOVAS FUNÇÕES DO MAPA AQUI ▼▼▼

@st.cache_data
def get_coords(cidade_nome):
    """Busca as coordenadas (latitude, longitude) de uma cidade usando a API Nominatim."""
    try:
        # Usamos um user_agent para identificar nossa aplicação, uma boa prática para APIs públicas
        headers = {'User-Agent': 'MeuDashboardStreamlit/1.0'}
        url = f"https://nominatim.openstreetmap.org/search?q={cidade_nome}&format=json&limit=1"
        response = requests.get(url, headers=headers, timeout=10 ) # Adicionado timeout
        response.raise_for_status() # Lança um erro para respostas ruins (4xx ou 5xx)
        data = response.json()
        if data:
            # Retorna as coordenadas como uma tupla de floats
            return (float(data[0]['lat']), float(data[0]['lon']))
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar coordenadas para {cidade_nome}: {e}")
    except (KeyError, IndexError):
        st.warning(f"Não foi possível encontrar coordenadas para '{cidade_nome}'.")
    return None

@st.cache_data
def get_route(coord_origem, coord_destino):
    """Obtém a rota (geometria polyline) entre duas coordenadas usando a API do OSRM."""
    if not coord_origem or not coord_destino:
        return None
    
    # Formata as coordenadas para a URL da API
    lon_orig, lat_orig = coord_origem[1], coord_origem[0]
    lon_dest, lat_dest = coord_destino[1], coord_destino[0]
    
    url = f"http://router.project-osrm.org/route/v1/driving/{lon_orig},{lat_orig};{lon_dest},{lat_dest}?overview=full&geometries=polyline"
    
    try:
        response = requests.get(url, timeout=10 ) # Adicionado timeout
        response.raise_for_status()
        data = response.json()
        if data['routes']:
            # Decodifica a geometria polyline para uma lista de coordenadas (lat, lon)
            route_polyline = data['routes'][0]['geometry']
            return polyline.decode(route_polyline)
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar a rota: {e}")
    except (KeyError, IndexError):
        st.warning("Não foi possível obter a geometria da rota.")
    return None

def criar_mapa_folium(coord_origem, coord_destino, nome_cidade_destino, rota_coords):
    """
    Cria e configura o mapa Folium com múltiplas camadas, marcadores,
    a linha da rota e um controle para alternar as camadas.
    """
    if not coord_origem or not coord_destino:
        return None

    # Calcula o ponto central do mapa
    map_center = [
        (coord_origem[0] + coord_destino[0]) / 2,
        (coord_origem[1] + coord_destino[1]) / 2
    ]

    # Cria o mapa base (a primeira camada será a padrão)
    m = folium.Map(location=map_center, zoom_start=7, tiles=None)

    # --- CAMADAS DE FUNDO ---

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr='Google',
        name='🌄 Terreno (Google Maps)'
    ).add_to(m)

    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='🌃 Modo Escuro (CartoDB)'
    ).add_to(m)

    folium.TileLayer(
        'OpenStreetMap',
        name='🗺️ Ruas (OpenStreetMap)'
    ).add_to(m)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr='Google',
        name='🛰️ Satélite (Google Maps)'
    ).add_to(m)

    # --- GRUPO DE ELEMENTOS (rota + marcadores) ---
    feature_group = folium.FeatureGroup(name="🚚 Trajeto da Viagem").add_to(m)

    # Marcador de Origem
    folium.Marker(
        location=coord_origem,
        popup="<b>Origem:</b><br>Campo Grande, MS",
        tooltip="Origem",
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    ).add_to(feature_group)

    # Marcador de Destino
    folium.Marker(
        location=coord_destino,
        popup=f"<b>Destino:</b><br>{nome_cidade_destino}",
        tooltip="Destino",
        icon=folium.Icon(color='red', icon='truck', prefix='fa')
    ).add_to(feature_group)

    # Linha da rota (se existir)
    if rota_coords:
        folium.PolyLine(
            locations=rota_coords,
            color='#1E90FF',
            weight=5,
            opacity=0.9
        ).add_to(feature_group)

    # --- CONTROLE DE CAMADAS ---
    folium.LayerControl(collapsed=False).add_to(m)
    
    Fullscreen(position='topright', title='Tela cheia', title_cancel='Sair').add_to(m)

    return m

# ▼▼▼ COLE A NOVA FUNÇÃO AQUI ▼▼▼
def ordenar_destinos_geograficamente(destinos_da_viagem, rotas_completas, ordem_das_rotas):
    """
    Ordena uma lista de siglas de destino com base na ordem geográfica pré-definida
    para a rota correspondente. Funciona para todas as rotas.
    """
    # 1. Converte as siglas da viagem para um conjunto (set) para facilitar a comparação
    destinos_set = set(destinos_da_viagem)
    
    # 2. Identifica a qual rota principal esta viagem pertence
    nome_rota_identificada = None
    # Itera sobre o dicionário de rotas compostas para encontrar a correspondência
    for nome_rota, siglas_rota in rotas_completas.items():
        if siglas_rota.issubset(destinos_set):
            nome_rota_identificada = nome_rota
            break # Para na primeira correspondência encontrada (importante pela ordem do dicionário)

    # 3. Se uma rota foi identificada, busca sua ordem específica
    if nome_rota_identificada:
        # Pega a lista de ordem para a rota encontrada (ex: ["SRP", "BLD", "BAT"])
        ordem_especifica = ordem_das_rotas.get(nome_rota_identificada, [])
        
        # Cria um mapa de posição para a ordenação (ex: {'SRP': 0, 'BLD': 1, 'BAT': 2})
        mapa_de_ordem = {sigla: pos for pos, sigla in enumerate(ordem_especifica)}
        
        # Ordena os destinos da viagem usando o mapa
        destinos_ordenados = sorted(destinos_da_viagem, key=lambda d: mapa_de_ordem.get(d, 99))
        
        return ' / '.join(destinos_ordenados)
    
    # 4. Fallback: Se nenhuma rota composta for encontrada, ordena alfabeticamente
    # Isso lida com rotas de destino único ou combinações não previstas.
    return ' / '.join(sorted(destinos_da_viagem))
# ▲▲▲ FIM DA NOVA FUNÇÃO ▲▲▲

# --- 3. CARREGAMENTO DOS DADOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_do_arquivo = os.path.join(BASE_DIR, "Arquivos", "Relatorio_de_Viagens.xlsx")
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
df_original = df_bruto[df_bruto['PROPRIETARIO_CAVALO'].isin(proprietarios_desejados)].copy()

### FILTRO 1: REMOVER MANIFESTOS CANCELADOS ###
if 'SITUACAO' in df_original.columns:
    df_original['SITUACAO'] = df_original['SITUACAO'].astype(str)
    df_original = df_original[df_original['SITUACAO'].str.upper().str.strip() != 'CANCELADO']
else:
    st.warning("⚠️ A coluna 'SITUACAO' não foi encontrada. Não foi possível filtrar manifestos cancelados.")
### FIM DO FILTRO 1 ###

### FILTRO 2: REMOVER RETIRADAS DE TERENOS (CONFERENTE 224) ###
if 'CONFERENTE CARGA' in df_original.columns:
    df_original['CONFERENTE CARGA'] = df_original['CONFERENTE CARGA'].astype(str)
    padrao_terenos_conf = "224 - ERISSCGR"
    df_original = df_original[~df_original['CONFERENTE CARGA'].str.contains(padrao_terenos_conf, case=False, na=False)]
else:
    st.warning("⚠️ A coluna 'CONFERENTE CARGA' não foi encontrada. Não foi possível filtrar as retiradas de Terenos.")
### FIM DO FILTRO 2 ###


# ▼▼▼ NOVO FILTRO ADICIONADO AQUI ▼▼▼
### FILTRO 3: REMOVER VIAGENS COM DESTINO TERENOS (TRN) ###
if 'DEST_MANIF' in df_original.columns:
    # Garante que a coluna seja do tipo string para a comparação
    df_original['DEST_MANIF'] = df_original['DEST_MANIF'].astype(str)
    
    # Remove todas as linhas onde a sigla do destino é exatamente 'TRN'
    # .str.strip() remove espaços em branco antes e depois da sigla
    df_original = df_original[df_original['DEST_MANIF'].str.strip().str.upper() != 'TRN']
else:
    st.warning("⚠️ A coluna 'DEST_MANIF' não foi encontrada. Não foi possível filtrar viagens para Terenos.")
### ▲▲▲ FIM DO NOVO FILTRO ▲▲▲


# 3. (Opcional) Adiciona um aviso se nenhum dado for encontrado após os filtros
if df_original.empty:
    st.warning("⚠️ Nenhum dado encontrado para os proprietários e filtros aplicados. Verifique o arquivo de origem.")
    st.stop()
# --- FIM DA MUDANÇA ---

# ▼▼▼ NOVA LÓGICA FIXA DE CAPACIDADE BASEADA EM PLACA + TIPO ▼▼▼

# Dicionário fixo de capacidades por tipo
CAPACIDADES_FIXAS = {
    "TRUCK": 15000,
    "BI-TRUCK": 19000,
    "CARRETA": 25000,
    "TOCO": 10000
}

# Lista de placas BI-TRUCK informadas
PLACAS_BITRUCK = [
    "REW6J23",
    "GBQ0I23",
    "RWG9G33",
    "SFH1C15"
]

def identificar_tipo(row):

    # tenta detectar automaticamente o nome da coluna de placa
    possiveis_colunas_placa = ['PLACA', 'PLACA_CAVALO', 'PLACA_CARRETA',
                               'Veículo (Placa)', 'VEÍCULO (PLACA)', 'VEICULO', 'VEÍCULO']

    placa = None
    for col in possiveis_colunas_placa:
        if col in row.index:
            placa = str(row[col]).strip().upper()
            break

    # se não encontrou placa
    if placa is None:
        tipo_bruto = str(row.get("TIPO_CAVALO", "")).upper().strip()
    else:
        tipo_bruto = str(row.get("TIPO_CAVALO", "")).upper().strip()

    # Normalizações
    if placa in PLACAS_BITRUCK:
        return "BI-TRUCK"

    # Aqui está a correção principal:
    if tipo_bruto in ["CAVALO", "CAV", "CAVALINHO"]:
        return "CARRETA"

    if tipo_bruto in ["CARRETA"]:
        return "CARRETA"

    if tipo_bruto in ["TRUCK"]:
        return "TRUCK"

    if tipo_bruto in ["TOCO"]:
        return "TOCO"

    return "TRUCK"  # fallback seguro


# Gera a nova coluna TIPO_CORRIGIDO
df_original['TIPO_CORRIGIDO'] = df_original.apply(identificar_tipo, axis=1)

# Função de capacidade
def obter_capacidade(tipo):
    return CAPACIDADES_FIXAS.get(tipo.upper(), 0)

# Capacidade final usada nos cálculos
df_original['CAPACIDADE_KG'] = df_original['TIPO_CORRIGIDO'].apply(obter_capacidade)

# (Opcional) capacidade do cavalo (se quiser manter)
df_original['CAPAC_CAVALO'] = df_original['CAPACIDADE_KG']

# ▲▲▲ FIM DA NOVA LÓGICA FIXA DE CAPACIDADE ▲▲▲


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

st.sidebar.subheader("📅 Período de Emissão")

# 🔴 TROCA 1 — BASE DE DATA (AGORA USANDO DATA_OPERACIONAL)
df_sem_na_emissao = df_original.dropna(subset=['DATA_OPERACIONAL'])
min_data_emissao = df_sem_na_emissao['DATA_OPERACIONAL'].min().date()
max_data_emissao = df_sem_na_emissao['DATA_OPERACIONAL'].max().date()
total_registros = len(df_sem_na_emissao)

# 🛡️ flag global de controle
dados_periodo_validos = True

# Define o valor padrão somente na primeira carga da sessão
if "periodo_tipo" not in st.session_state:
    st.session_state["periodo_tipo"] = "Mês Completo"

periodo_tipo = st.sidebar.radio(
    "Filtrar por data OPERACIONAL:", # <-- Texto atualizado para clareza
    ["Dia Específico", "Mês Completo", "Período Personalizado"],
    key="periodo_tipo"
)

data_padrao_inteligente = max_data_emissao
df_periodo_filtrado = df_original.copy()

# =========================================================
# 📅 DIA ESPECÍFICO
# =========================================================
if periodo_tipo == "Dia Específico":

    st.sidebar.markdown("""
        <style>
        .dia-semana-box {
            background-color: #2C2F38;
            color: #E0E0E0;
            padding: 8px 12px;
            border-radius: 6px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #444;
            margin-top: 28px;
        }
        </style>
    """, unsafe_allow_html=True)

    col_data, col_dia = st.sidebar.columns([3, 1])

    with col_data:
        data_emissao_especifica = st.date_input(
            "📜 Selecione o Dia:",
            value=data_padrao_inteligente,
            min_value=min_data_emissao,
            max_value=max_data_emissao,
            format="DD/MM/YYYY"
        )

    with col_dia:
        dia_semana_abbr = data_emissao_especifica.strftime('%A')[:3].capitalize()
        st.markdown(
            f'<div class="dia-semana-box">{dia_semana_abbr}</div>',
            unsafe_allow_html=True
        )

    # 🔴 TROCA 2 — FILTRO DIA ESPECÍFICO PELA DATA OPERACIONAL
    df_periodo_filtrado = df_original[
        df_original['DATA_OPERACIONAL'].dt.date == data_emissao_especifica
    ]

    # A função obter_info_periodo ainda usa EMIS_MANIF, vamos mantê-la por enquanto
    # para não quebrar outras partes, mas o filtro principal está correto.
    num_reg, num_veic, num_mot = obter_info_periodo(
        df_original, data_emissao_especifica
    )

    if len(df_periodo_filtrado) > 0:
        st.sidebar.info(f"📜 {len(df_periodo_filtrado)} Manifestos • 🚚 {df_periodo_filtrado['PLACA_CAVALO'].nunique()} Veículos")
    else:
        st.sidebar.warning(
            f"⚠️ Nenhum registro encontrado para "
            f"{data_emissao_especifica.strftime('%d/%m/%Y')}"
        )

    if df_periodo_filtrado.empty:
        st.warning("📭 Não há manifestos para a data operacional selecionada.")
        dados_periodo_validos = False


# =========================================================
# 🗓️ MÊS COMPLETO
# =========================================================
elif periodo_tipo == "Mês Completo":

    # 🔴 TROCA 3 — MÊS BASEADO NA DATA OPERACIONAL
    meses = df_sem_na_emissao['DATA_OPERACIONAL'].dt.to_period("M").unique().astype(str)
    meses_ordenados = sorted(meses, reverse=True)

    meses_formatados = {
        m: pd.Period(m).strftime("%B/%Y").capitalize()
        for m in meses_ordenados
    }

    lista_meses = list(meses_formatados.values())

    mes_formatado_sel = st.sidebar.selectbox(
        "🗓️ Selecione o Mês:",
        lista_meses,
        index=0,
        key="mes_completo_padrao"
    )

    mes_emissao_completo = [
        k for k, v in meses_formatados.items()
        if v == mes_formatado_sel
    ][0]

    # 🔴 TROCA 4 — FILTRO MÊS PELA DATA OPERACIONAL
    df_periodo_filtrado = df_original[
        df_original['DATA_OPERACIONAL']
        .dt.to_period("M")
        .astype(str) == mes_emissao_completo
    ]

    if df_periodo_filtrado.empty:
        st.warning("📭 Não há manifestos no mês selecionado.")
        dados_periodo_validos = False
    else:
        st.sidebar.success(
            f"✅ {len(df_periodo_filtrado)} registros para {mes_formatado_sel}"
        )


# =========================================================
# 📆 PERÍODO PERSONALIZADO
# =========================================================
elif periodo_tipo == "Período Personalizado":

    periodo_emissao_sel = st.sidebar.date_input(
        "🗓️ Selecione o intervalo:",
        [min_data_emissao, max_data_emissao],
        format="DD/MM/YYYY"
    )

    if len(periodo_emissao_sel) == 2:
        # 🔴 TROCA 5 — INTERVALO PELA DATA OPERACIONAL
        df_periodo_filtrado = df_original[
            (df_original['DATA_OPERACIONAL'].dt.date >= periodo_emissao_sel[0]) &
            (df_original['DATA_OPERACIONAL'].dt.date <= periodo_emissao_sel[1])
        ]

        num_reg = len(df_periodo_filtrado)
        num_veic = df_periodo_filtrado['PLACA_CAVALO'].nunique()
        num_mot = df_periodo_filtrado['MOTORISTA'].nunique()

        if num_reg > 0:
            dias_periodo = (periodo_emissao_sel[1] - periodo_emissao_sel[0]).days + 1
            st.sidebar.success(f"✅ {num_reg} registros encontrados")
            st.sidebar.info(
                f"📅 {dias_periodo} dias • 🚚 {num_veic} veículos • 👨‍✈️ {num_mot} motoristas"
            )
        else:
            st.sidebar.warning("⚠️ Nenhum registro encontrado no período selecionado")


# --- FILTROS DE VIAGEM (COM AMBOS OS SELETORES) ---
with st.sidebar.expander("👨‍✈️ Filtros de Viagem", expanded=True):

    # ▼▼▼ NOVO FILTRO DE TIPO DE VIAGEM ▼▼▼
  
    tipo_viagem_sel = st.radio(
        "⚙️ Tipo de Viagem",
        ["Todas", "Viagem Extra"], 
        horizontal=True,
        key="tipo_viagem_sel"
    )
    # ▲▲▲ FIM DO NOVO FILTRO ▲▲▲
    
    # --- NOVO FILTRO DE DESEMPENHO DE CTRB/FRETE (%) ---
    opcoes_desempenho = ["(Todos)", "Bom (Até 25%)", "Regular (Entre 26 a 45%)", "Péssimo (Acima de 45%)"]
    desempenho_ctrb_sel = st.selectbox(
        "📊 Desempenho CTRB/Frete",
        options=opcoes_desempenho,
        key="filtro_desempenho_sidebar"
    )
    # --- FIM DO NOVO FILTRO ---



    motorista_sel = st.selectbox("👤 Motorista", ["(Todos)"] + sorted(df_periodo_filtrado["MOTORISTA"].dropna().unique()))
    # --- FILTRO DE DESTINO MÚLTIPLO ---
    # Gera a lista de opções de destino, removendo valores nulos e ordenando
    lista_destinos = sorted(df_periodo_filtrado["CIDADE_UF_DEST"].dropna().unique())
    
    # Usa st.multiselect para permitir a seleção de múltiplas cidades
    destinos_sel = st.multiselect(
        "📍 Destino(s) Final(is)", 
        options=lista_destinos,
        placeholder="Selecione uma ou mais cidades" # Texto que aparece quando nada está selecionado
    )


    # Garante que a coluna de data formatada existe para ambos os filtros
    if 'EMIS_MANIF' in df_periodo_filtrado.columns:
        df_periodo_filtrado['DIA_EMISSAO_STR'] = df_periodo_filtrado['EMIS_MANIF'].dt.strftime('%d/%m/%Y')
    else:
        df_periodo_filtrado['DIA_EMISSAO_STR'] = ''


    # --- INÍCIO: LÓGICA DO FILTRO DE VIAGEM ESPECÍFICA (O ANTIGO) ---
    rotas_df_antigo = df_periodo_filtrado.dropna(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA', 'DEST_MANIF']).copy()

    if not rotas_df_antigo.empty:
        # Agrupa por viagem e cria a lista de destinos
        rotas_df_antigo = rotas_df_antigo.groupby(
            ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']
        ).agg(
            Destinos=('DEST_MANIF', lambda x: ' - '.join(sorted(x.unique())))
        ).reset_index()

        # Formata o nome do motorista
        def formatar_nome_motorista(nome_completo):
            partes = str(nome_completo).strip().split()
            if not partes: return ""
            preposicoes = ['DA', 'DE', 'DO', 'DOS']
            if len(partes) >= 3 and partes[1].upper() in preposicoes:
                return f"{partes[0]} {partes[1]} {partes[2]}"
            elif len(partes) >= 2:
                return f"{partes[0]} {partes[1]}"
            else:
                return partes[0]

        rotas_df_antigo['NOME_CURTO_MOTORISTA'] = rotas_df_antigo['MOTORISTA'].apply(formatar_nome_motorista)
        
        # Cria o rótulo para o selectbox
        rotas_df_antigo['NOME_ROTA_ANTIGO'] = (
            "📍 " + rotas_df_antigo['Destinos'] + 
            " 👨‍✈️ " + rotas_df_antigo['NOME_CURTO_MOTORISTA']
        )
        lista_rotas_antigas = ["(Todos)"] + sorted(rotas_df_antigo['NOME_ROTA_ANTIGO'].unique())
    else:
        lista_rotas_antigas = ["(Todos)"]
        rotas_df_antigo = pd.DataFrame()

    # Cria o selectbox para a VIAGEM ESPECÍFICA
    viagem_especifica_sel = st.selectbox("🗺️ Selecione a Viagem (Específica)", lista_rotas_antigas)

    # 🔹 Guarda a viagem selecionada na sessão (com o nome correto)
    st.session_state["viagem_especifica"] = viagem_especifica_sel



    # --- INÍCIO: LÓGICA DO FILTRO DE GRUPO DE ROTAS (ATUALIZADO) ---

    # Dicionário que define as rotas completas e suas siglas.
    # A ORDEM É IMPORTANTE: As rotas mais abrangentes (com mais destinos) devem vir primeiro.
    ROTAS_COMPLETAS = {
        # Rotas compostas (mais destinos primeiro)
        "ROTA COXIM": {"COX", "PGO", "SNR"},
        "ROTA SÃO PAULO": {"CSL", "PBA", "ATB", "SPO"},
        "ROTA GOIÂNIA": {"PDA", "CDS", "GYN"},
        "ROTA BATAGUASSU": {"BAT", "BLD", "SRP"},
        "ROTA RIO BRILHANTE/DOURADOS": {"RBT", "DOU"},
        "ROTA SÃO GABRIEL": {"SGO", "RVM"},
        "ROTA MARACAJU": {"MJU", "SDL"},
        "ROTA JARDIM": {"JDM", "NQU"},
        "ROTA BODOQUENA": {"BDQ", "MDA"},
        "ROTA COSTA RICA": {"CRC", "CMP"},
        "ROTA IVINHEMA": {"IVM", "NSU"},
        "ROTA RIBAS": {"ACL", "RRP"},

        # Rotas com um único destino principal (ou que podem aparecer sozinhas)
        "ROTA DOURADOS": {"DOU"},
        "ROTA RIO BRILHANTE": {"RBT"},
        "ROTA NOVA ANDRADINA": {"NAD"},
        "ROTA BONITO": {"BTO"},
        "ROTA AQUIDAUANA": {"AQU"},
        "ROTA PONTA PORÃ": {"PPR"},
        "ROTA TRÊS LAGOAS": {"TLG"},
        "ROTA CORUMBÁ": {"COR"},
    }

    # Dicionário reverso para mapear uma sigla individual ao nome completo da sua rota principal.
    # Isso garante que "BAT" sozinho seja mapeado para "ROTA BATAGUASSU".
    MAPA_SIGLA_PARA_ROTA = {
        sigla: nome_rota
        for nome_rota, siglas in ROTAS_COMPLETAS.items()
        for sigla in siglas
    }


    if not df_periodo_filtrado.empty and all(col in df_periodo_filtrado.columns for col in ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA', 'DEST_MANIF']):
        # Agrupa as viagens para obter uma lista única de destinos para cada uma
        viagens_agrupadas = df_periodo_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA'])['DEST_MANIF'].unique().reset_index()

        def obter_nome_rota_padronizado(lista_destinos_da_viagem):
            """
            Identifica a rota correta para um conjunto de destinos, dando prioridade
            às rotas compostas e tratando corretamente as rotas individuais.
            """
            destinos_set = {str(d).upper() for d in lista_destinos_da_viagem}

            # 1. VERIFICA AS ROTAS COMPLETAS (DA MAIS ABRANGENTE PARA A MENOS)
            for nome_rota, destinos_rota in ROTAS_COMPLETAS.items():
                if destinos_rota.issubset(destinos_set):
                    return nome_rota

            # 2. SE NENHUMA ROTA COMPLETA CORRESPONDER, USA O MAPEAMENTO INDIVIDUAL
            nomes_de_rota_encontrados = set()
            for sigla in destinos_set:
                # Busca o nome da rota para a sigla no mapa reverso.
                # Se não encontrar, cria um nome genérico "ROTA [SIGLA]".
                nome_encontrado = MAPA_SIGLA_PARA_ROTA.get(sigla, f"ROTA {sigla}")
                nomes_de_rota_encontrados.add(nome_encontrado)
            
            if nomes_de_rota_encontrados:
                # Junta os nomes únicos, ordenados alfabeticamente.
                return ' / '.join(sorted(list(nomes_de_rota_encontrados)))

            return "ROTA INDEFINIDA"

        # Aplica a função para criar a coluna com o nome padronizado da rota
        viagens_agrupadas['NOME_ROTA_PADRAO'] = viagens_agrupadas['DEST_MANIF'].apply(obter_nome_rota_padronizado)
        
        # Gera a lista de opções para o selectbox
        lista_rotas_padronizadas = ["(Todos)"] + sorted(viagens_agrupadas['NOME_ROTA_PADRAO'].unique())
    else:
        lista_rotas_padronizadas = ["(Todos)"]
        viagens_agrupadas = pd.DataFrame()

    # Cria o selectbox para o GRUPO DE ROTAS
    grupo_rota_sel = st.selectbox("🗺️ Filtro de Rotas (Grupo)", lista_rotas_padronizadas)
    # --- FIM: LÓGICA DO FILTRO DE GRUPO DE ROTAS ---


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
# 🔹 APLICAÇÃO FINAL DOS FILTROS (LÓGICA CORRIGIDA E FINAL)
# ========================================

# Começa com os dados já filtrados pelo período (Dia, Mês, etc.)
df_filtrado = df_periodo_filtrado.copy()

# --- ETAPA FUNDAMENTAL: GARANTIR A EXISTÊNCIA DO VIAGEM_ID ---
# Cria a coluna VIAGEM_ID no DataFrame principal ANTES de qualquer outro filtro de viagem.
# Isso garante que a coluna estará sempre disponível para as lógicas subsequentes.
if not df_filtrado.empty:
    if 'VIAGEM_ID' not in df_filtrado.columns:
        df_filtrado['VIAGEM_ID'] = df_filtrado.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()
else:
    # Se o dataframe estiver vazio, garante que a coluna exista para evitar erros posteriores
    df_filtrado['VIAGEM_ID'] = pd.Series(dtype='int')
# --- FIM DA ETAPA FUNDAMENTAL ---


# --- PASSO 1: APLICA O FILTRO DE TIPO DE VIAGEM (EXTRA vs COMPLETA) PRIMEIRO ---
# Este filtro é o mais complexo e precisa ser aplicado antes dos outros.
if tipo_viagem_sel != "Todas":
    if not df_filtrado.empty:
        # A função de classificação precisa do contexto do dia inteiro para funcionar.
        # Portanto, ela é aplicada ANTES de outros filtros de viagem.
        df_classificado = classificar_viagens_do_dia(df_filtrado)
        
        # Agora, filtramos o resultado com base na seleção do usuário
        df_filtrado = df_classificado[df_classificado['TIPO_VIAGEM_CALCULADO'] == tipo_viagem_sel].copy()

# --- PASSO 2: APLICA OS OUTROS FILTROS EM CASCATA ---
# A variável 'rota_sel_visivel' é usada para controlar a exibição de detalhes posteriormente.
rota_sel_visivel = "(Todos)"

# Prioridade máxima: Busca Rápida
if busca_placa:
    df_filtrado = df_original[df_original['PLACA_CAVALO'].str.contains(busca_placa.strip(), case=False, na=False)]
elif busca_lacre:
    df_filtrado = df_original[df_original['LACRES'].str.contains(busca_lacre.strip(), case=False, na=False)]

# Filtros de Viagem (só são aplicados se a busca rápida não foi usada)
else:
    if viagem_especifica_sel != "(Todos)":
        viagem_selecionada = rotas_df_antigo[rotas_df_antigo['NOME_ROTA_ANTIGO'] == viagem_especifica_sel]
        if not viagem_selecionada.empty:
            placa_rota = viagem_selecionada['PLACA_CAVALO'].iloc[0]
            data_emissao_rota = viagem_selecionada['DIA_EMISSAO_STR'].iloc[0]
            motorista_rota = viagem_selecionada['MOTORISTA'].iloc[0]
            df_filtrado = df_filtrado[
                (df_filtrado['PLACA_CAVALO'] == placa_rota) &
                (df_filtrado['DIA_EMISSAO_STR'] == data_emissao_rota) &
                (df_filtrado['MOTORISTA'] == motorista_rota)
            ]
        rota_sel_visivel = viagem_especifica_sel

    elif grupo_rota_sel != "(Todos)":
        if not viagens_agrupadas.empty:
            viagens_do_grupo = viagens_agrupadas[viagens_agrupadas['NOME_ROTA_PADRAO'] == grupo_rota_sel]
            chaves_viagens = list(zip(viagens_do_grupo['PLACA_CAVALO'], viagens_do_grupo['DIA_EMISSAO_STR'], viagens_do_grupo['MOTORISTA']))
            if chaves_viagens:
                df_filtrado = df_filtrado[pd.MultiIndex.from_frame(df_filtrado[['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']]).isin(chaves_viagens)]
            else:
                df_filtrado = pd.DataFrame(columns=df_filtrado.columns)
        rota_sel_visivel = "(Todos)"

    else:  # Filtros individuais
        if motorista_sel != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["MOTORISTA"] == motorista_sel]

        # --- NOVO: APLICA O FILTRO DE DESEMPENHO DE CTRB/FRETE ---
        if desempenho_ctrb_sel != "(Todos)":
            # 1. Precisamos calcular o CTRB/Frete (%) para cada viagem antes de filtrar.
            # Agrupa por viagem para obter os valores corretos.
            df_temp_desempenho = df_filtrado.copy()
            if 'VIAGEM_ID' not in df_temp_desempenho.columns:
                df_temp_desempenho['VIAGEM_ID'] = df_temp_desempenho.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

            resumo_viagens_desempenho = df_temp_desempenho.groupby('VIAGEM_ID').agg(
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'),
                FRETE_TOTAL=('FRETE-R$', 'sum'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique()))
            ).reset_index()

            # 2. Calcula o custo e o percentual
            def calcular_custo_viagem_temp(row):
                custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base
            
            resumo_viagens_desempenho['CUSTO_FINAL'] = resumo_viagens_desempenho.apply(calcular_custo_viagem_temp, axis=1)
            resumo_viagens_desempenho['CTRB_FRETE_PERC'] = (resumo_viagens_desempenho['CUSTO_FINAL'] / resumo_viagens_desempenho['FRETE_TOTAL'] * 100).fillna(0)

            # --- INÍCIO DA CORREÇÃO ---

            # 3. Inicializa a variável para garantir que ela sempre exista, evitando o NameError.
            viagens_filtradas_ids = []

            # 4. Filtra as viagens com base na faixa de desempenho selecionada (COM OS TEXTOS ATUALIZADOS)
            if desempenho_ctrb_sel == "Bom (Até 25%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[resumo_viagens_desempenho['CTRB_FRETE_PERC'] <= 25]['VIAGEM_ID']
            elif desempenho_ctrb_sel == "Regular (Entre 26 a 45%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[(resumo_viagens_desempenho['CTRB_FRETE_PERC'] > 25) & (resumo_viagens_desempenho['CTRB_FRETE_PERC'] <= 45)]['VIAGEM_ID']
            elif desempenho_ctrb_sel == "Péssimo (Acima de 45%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[resumo_viagens_desempenho['CTRB_FRETE_PERC'] > 45]['VIAGEM_ID']
            
            # 5. Aplica o filtro final no DataFrame principal.
            #    Se 'viagens_filtradas_ids' estiver vazia, o dataframe resultante também ficará vazio.
            df_filtrado = df_filtrado[df_filtrado['VIAGEM_ID'].isin(viagens_filtradas_ids)]
            
            # --- FIM DA CORREÇÃO ---
        # --- FIM DO FILTRO DE DESEMPENHO ---


        
        # --- INÍCIO DA NOVA LÓGICA DE FILTRO DE DESTINO ---
        if destinos_sel:
            # 1. Converte as cidades selecionadas para um conjunto para performance
            destinos_selecionados_set = set(destinos_sel)
            
            # 2. Identifica todas as viagens (pela chave única) no dataframe atual
            viagens_candidatas = df_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA'])
            
            viagens_para_manter = []

            # 3. Itera sobre cada viagem para aplicar a lógica correta
            for chave_viagem, grupo_viagem in viagens_candidatas:
                # Pega o conjunto de destinos únicos da viagem atual
                destinos_da_viagem_set = set(grupo_viagem['CIDADE_UF_DEST'].unique())

                # ▼▼▼ AQUI ESTÁ A EXCEÇÃO QUE VOCÊ PEDIU ▼▼▼
                # Se exatamente 3 cidades foram selecionadas no filtro...
                if len(destinos_selecionados_set) == 3:
                    # LÓGICA "OU": Mantém a viagem se HOUVER QUALQUER INTERSEÇÃO
                    # entre os destinos selecionados e os destinos da viagem.
                    if not destinos_selecionados_set.isdisjoint(destinos_da_viagem_set):
                        viagens_para_manter.append(chave_viagem)
                
                # ▼▼▼ LÓGICA PADRÃO (PARA 1, 2, 4+ cidades) ▼▼▼
                else:
                    # LÓGICA "E": Mantém a viagem somente se os destinos da viagem
                    # FOREM EXATAMENTE IGUAIS aos destinos selecionados.
                    if destinos_da_viagem_set == destinos_selecionados_set:
                        viagens_para_manter.append(chave_viagem)

            # 4. Aplica o filtro final com base nas viagens que passaram na lógica
            if viagens_para_manter:
                multi_index = pd.MultiIndex.from_tuples(viagens_para_manter, names=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA'])
                # Filtra o dataframe mantendo apenas as linhas cujas chaves de viagem estão na lista 'viagens_para_manter'
                df_filtrado = df_filtrado[pd.MultiIndex.from_frame(df_filtrado[['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']]).isin(multi_index)]
            else:
                # Se nenhuma viagem corresponder, retorna um DataFrame vazio
                df_filtrado = pd.DataFrame(columns=df_filtrado.columns)
        
        # A variável abaixo não muda, continua como está
        rota_sel_visivel = "(Todos)"
        # --- FIM DA NOVA LÓGICA DE FILTRO DE DESTINO ---

# Filtros finais de veículo (aplicados sobre qualquer resultado anterior)
if placa_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["PLACA_CAVALO"] == placa_sel]
if tipo_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["TIPO_CAVALO"] == tipo_sel]
if proprietario_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["PROPRIETARIO_CAVALO"] == proprietario_sel]

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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Visão Geral", 
    "Análise Financeira", 
    "Performance da Frota", 
    "Desempenho de Motoristas", 
    "Gestão de Rotas",
    "Análise Temporal" 
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

        # Corrige M3 nulo ou texto inválido antes do somatório
        if 'M3' in df_filtrado.columns:
            df_filtrado['M3'] = pd.to_numeric(df_filtrado['M3'], errors='coerce').fillna(0)


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

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

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

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # ==============================
        # 5. DETALHES OPERACIONAIS (TOTAIS)
        # ==============================
        st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-gears"></i> Detalhes Operacionais</h3>', unsafe_allow_html=True)

        # --- LÓGICA CORRIGIDA PARA KPIs DINÂMICOS ---
        # Verifica se o DataFrame filtrado representa uma única viagem.
        # Isso funciona tanto para a seleção de "Viagem Específica" quanto para um "Grupo de Rota" que resulta em uma única viagem.
        is_single_trip = df_filtrado['VIAGEM_ID'].nunique() == 1 if 'VIAGEM_ID' in df_filtrado.columns and not df_filtrado.empty else False

        if is_single_trip:
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
                distancia_formatada = f"{int(distancia_estimada_km):,} KM".replace(",", ".")
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">🗺️ Distância (KM)</div>
                        <div class="kpi-value">{distancia_formatada}</div>
                    </div>
                """, unsafe_allow_html=True)

        else:
            # --- MODO VISÃO GERAL: Exibe KPIs agregados de todas as viagens no período ---
            
            # 1. Calcula os KPIs agregados (TOTAIS)
            total_viagens = df_filtrado.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroups if not df_filtrado.empty else 0
            
            if not df_filtrado.empty:
                entregas_por_viagem = df_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR'])['DEST_MANIF'].nunique()
                total_entregas = entregas_por_viagem.sum()
            else:
                total_entregas = 0
            
            cidades_atendidas = df_filtrado['CIDADE_UF_DEST'].nunique()

            distancia_total_agregada = 0
            if not df_filtrado.empty:
                df_temp = df_filtrado.copy()
                df_temp['VIAGEM_ID'] = df_temp.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()
                resumo_temp = df_temp.groupby('VIAGEM_ID').agg(
                    PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), CUSTO_OS=('OS-R$', 'max'),
                    CUSTO_CTRB=('CTRB-R$', 'max'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
                    TIPO_VEICULO=('TIPO_CAVALO', 'first')
                ).reset_index()
                def calcular_custo_viagem_temp(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    destinos_str = str(row.get('DESTINOS', '')).upper()
                    if 'GYN' in destinos_str or 'SPO' in destinos_str: return custo_base / 2
                    return custo_base
                resumo_temp['CUSTO_FINAL'] = resumo_temp.apply(calcular_custo_viagem_temp, axis=1)
                def calcular_distancia_viagem_temp(row):
                    custo_km_por_tipo = {'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75}
                    tipo_veiculo = str(row.get('TIPO_VEICULO', 'PADRAO')).upper()
                    valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                    if valor_km > 0: return row['CUSTO_FINAL'] / valor_km
                    return 0
                resumo_temp['DISTANCIA_VIAGEM'] = resumo_temp.apply(calcular_distancia_viagem_temp, axis=1)
                distancia_total_agregada = resumo_temp['DISTANCIA_VIAGEM'].sum()

            # 2. Cria o layout com 5 colunas para os KPIs de TOTAIS
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-route"></i> Total de Viagens</div>
                        <div class="kpi-value">{total_viagens}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-dolly"></i> Total de Entregas</div>
                        <div class="kpi-value">{formatar_numero(total_entregas)}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">⚖️ Peso Total (KG)</div>
                        <div class="kpi-value">{formatar_numero(peso_total)} KG</div>
                    </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-city"></i> Cidades Atendidas</div>
                        <div class="kpi-value">{cidades_atendidas}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col5:
                distancia_formatada_kpi = f"{int(distancia_total_agregada):,} KM".replace(",", ".")
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">🗺️ Distância Total (KM)</div>
                        <div class="kpi-value">{distancia_formatada_kpi}</div>
                    </div>
                """, unsafe_allow_html=True)


        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        ### INÍCIO DO NOVO BLOCO DE CÓDIGO ###
        # ==================================================
        # 6. MÉDIAS OPERACIONAIS POR VIAGEM (NOVA SEÇÃO)
        # ==================================================
        if rota_sel_visivel == "(Todos)": # Só exibe esta seção na visão geral
            st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-chart-line"></i> Médias Operacionais por Viagem</h3>', unsafe_allow_html=True)
            
            # 1. Calcula os totais necessários para as médias
            # Reutiliza os totais já calculados
            # total_viagens, total_entregas, peso_total, custo_ctrb_os, distancia_total_agregada

            ### MUDANÇA 1: CÁLCULO DA CAPACIDADE TOTAL E OCUPAÇÃO MÉDIA ###
            capacidade_total_agregada = 0
            if not df_filtrado.empty:
                # Usamos o resumo_temp que já agrupa por viagem
                capacidades_veiculos = {'TOCO': 10000, 'TRUCK': 16000, 'CAVALO': 25000, 'CARRETA': 25000, 'PADRAO': 25000}
                
                # Para capacidade do cavalo/truck, usamos 'CAPAC_CAVALO'
                # Para capacidade da carreta, usamos 'CAPACIDADE_KG'
                # Vamos simplificar pegando a capacidade do TIPO de veículo para o cálculo da média
                resumo_temp['CAPACIDADE_VIAGEM'] = resumo_temp['TIPO_VEICULO'].apply(lambda x: capacidades_veiculos.get(str(x).upper(), 25000))
                capacidade_total_agregada = resumo_temp['CAPACIDADE_VIAGEM'].sum()

            # 2. Calcula as médias (com proteção contra divisão por zero)
            distancia_media = distancia_total_agregada / total_viagens if total_viagens > 0 else 0
            entregas_media = total_entregas / total_viagens if total_viagens > 0 else 0
            peso_medio = peso_total / total_viagens if total_viagens > 0 else 0
            custo_medio = custo_ctrb_os / total_viagens if total_viagens > 0 else 0
            ocupacao_media = (peso_total / capacidade_total_agregada * 100) if capacidade_total_agregada > 0 else 0


            # 3. Cria o layout com 5 colunas para os KPIs de médias
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

            with m_col1:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-road"></i> Distância Média</div>
                        <div class="kpi-value">{int(distancia_media):,} km</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)

            with m_col2:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-dolly"></i> Entregas / Viagem</div>
                        <div class="kpi-value">{entregas_media:.0f}</div>
                    </div>
                """.replace(".", ","), unsafe_allow_html=True)

            with m_col3:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title">⚖️ Peso Médio</div>
                        <div class="kpi-value">{formatar_numero(peso_medio)} kg</div>
                    </div>
                """, unsafe_allow_html=True)

            ### MUDANÇA 2: SUBSTITUIÇÃO DO CARD DE RECEITA MÉDIA POR OCUPAÇÃO MÉDIA ###
            with m_col4:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-percent"></i> Ocupação Média</div>
                        <div class="kpi-value">{ocupacao_media:.0f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with m_col5:
                st.markdown(f"""
                    <div class="kpi-container" style="text-align:center;">
                        <div class="kpi-title"><i class="fa-solid fa-tags"></i> Custo Médio CTRB</div>
                        <div class="kpi-value">{formatar_moeda(custo_medio)}</div>
                    </div>
                """, unsafe_allow_html=True)
        ### FIM DO BLOCO DE CÓDIGO ###

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

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
                font-size: 1.2rem;
                font-weight: 700;
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
                font-size: 1.1rem;  /* <<< TAMANHO AUMENTADO (era 1rem) */
                font-weight: 500;   /* <<< ADICIONADO: Deixa a fonte um pouco mais encorpada */
                color: #e0e0e0;     /* <<< ADICIONADO: Cor um pouco mais clara para melhor leitura */
                margin-top: 5px;    /* <<< ADICIONADO: Pequeno espaço acima do rodapé */
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
                    
            /* ▼▼▼ ADICIONE ESTA NOVA CLASSE CSS AQUI ▼▼▼ */
            .aviso-ociosidade-texto {
                font-size: 1.1rem;    /* <<< TAMANHO AUMENTADO */
                font-weight: 600;     /* <<< PESO DA FONTE (SEMI-NEGRITO) */
                display: flex;
                align-items: center;
                gap: 8px;             /* Espaço entre o ícone e o texto */
            }
            /* ▲▲▲ FIM DA NOVA CLASSE ▲▲▲ */
                    
            /* ▼▼▼ ADICIONE ESTA NOVA CLASSE CSS AQUI ▼▼▼ */
            .ociosidade-valor-final {
                font-size: 1.1rem;    /* Tamanho da fonte aumentado (mesmo do título) */
                font-weight: 700;     /* Peso da fonte (negrito) */
                white-space: nowrap;  /* Evita que o número quebre a linha */
                color: #E0E0E0;       /* Cor do texto (um branco suave) */
            }
            /* ▲▲▲ FIM DA NOVA CLASSE ▲▲▲ */
                    
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
        # 🧭 OPTION MENU DINÂMICO E ANÁLISE DE OCUPAÇÃO (VERSÃO FINAL COM IDENTIFICAÇÃO POR PLACA)
        # ===============================================

        # --- INÍCIO DA LÓGICA DA CATEGORIA DE VIAGEM ---

        df_com_categoria = df_filtrado.copy()

        # ▼▼▼ INÍCIO DA CORREÇÃO ▼▼▼
        def definir_categoria_viagem(row):
            """
            Define a categoria da viagem com uma lógica aprimorada:
            1. Verifica se a placa do cavalo pertence à lista de BI-TRUCKs.
            2. Se não, verifica se é uma CARRETA.
            3. Se não, usa o TIPO_CAVALO como fallback.
            """
            # 1. Lista de placas que são BI-TRUCKs
            placas_bitruck = {"REW6J23", "RWG9G33", "GBQ0I23", "SFH1C15"}
            
            placa_cavalo_atual = row.get('PLACA_CAVALO')

            # 2. Lógica de identificação prioritária
            if placa_cavalo_atual in placas_bitruck:
                return 'BI-TRUCK'

            # 3. Lógica para CARRETA (permanece a mesma)
            placa_carreta = row.get('PLACA_CARRETA')
            if pd.notna(placa_carreta) and placa_carreta != 'nan' and placa_carreta != placa_cavalo_atual:
                return 'CARRETA' 
            
            # 4. Fallback: Se não for BI-TRUCK nem CARRETA, usa o tipo da coluna
            return str(row.get('TIPO_CAVALO', 'INDEFINIDO')).upper()
        # ▲▲▲ FIM DA CORREÇÃO ▲▲▲

        if not df_com_categoria.empty:
            df_com_categoria['CATEGORIA_VIAGEM'] = df_com_categoria.apply(definir_categoria_viagem, axis=1)
        else:
            df_com_categoria['CATEGORIA_VIAGEM'] = pd.Series(dtype='str')


        # --- LÓGICA DO SELETOR DINÂMICO (COM ORDEM FIXA) ---

        # 1. Define a ordem EXATA que você quer para os botões
        ordem_personalizada = ["TRUCK", "BI-TRUCK", "CARRETA", "TOCO"]

        # 2. Pega as categorias que REALMENTE existem nos seus dados filtrados
        categorias_de_viagem_nos_dados = df_com_categoria['CATEGORIA_VIAGEM'].dropna().unique()

        # 3. Cria a lista de opções para o seletor, respeitando a ordem
        opcoes_ordenadas = [tipo for tipo in ordem_personalizada if tipo in categorias_de_viagem_nos_dados]
        
        # 4. Adiciona "TODOS" no início da lista final
        opcoes_seletor = ["TODOS"] + opcoes_ordenadas

        # 5. Remove ícones completamente
        icones_seletor = [""] * len(opcoes_seletor)

        # 6. Cria o seletor dinâmico
        selecionar_veiculo = option_menu(
            menu_title=None,
            options=opcoes_seletor,
            icons=icones_seletor,
            menu_icon=None,
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "6px", "background-color": "rgba(30, 30, 40, 0.4)", "border-radius": "16px", "justify-content": "center"},
                "nav-link": {"font-size": "14px", "font-weight": "600", "color": "#E5E7EB", "padding": "10px 26px", "border-radius": "12px", "margin": "0px 6px", "background-color": "rgba(255, 255, 255, 0.05)"},
                "nav-link:hover": {"background-color": "rgba(255,255,255,0.12)", "color": "#fff"},
                "nav-link-selected": {"background-color": "rgba(34, 36, 51, 0.8)", "color": "#FFFFFF", "border": "1.5px solid #5D9CEC", "box-shadow": "0 0 15px rgba(93, 156, 236, 0.6)"},
            },
        )


        # 7. Cria o DataFrame final para análise ('df_para_analise')
        df_para_analise = df_com_categoria.copy()
        if selecionar_veiculo != "TODOS":
            df_para_analise = df_para_analise[df_para_analise['CATEGORIA_VIAGEM'] == selecionar_veiculo]


        # ===============================================
        # LÓGICA DE OCUPAÇÃO (MODO VISÃO GERAL)
        # ===============================================
        if rota_sel_visivel == "(Todos)":

            # --- 1. FUNÇÕES DE LÓGICA DE COR (COM AJUSTE) ---
            def obter_cor_ocupacao(percentual):
                if percentual < 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
                elif percentual < 80: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)"

            def obter_cor_ociosidade(percentual):
                return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"

            # CÓDIGO FINAL E CORRIGIDO (VERSÃO 5)

            def calcular_dados_ocupacao_geral(df_dados):
                if df_dados.empty:
                    return None

                dados = {}
                if 'VIAGEM_UNICA_ID' not in df_dados.columns:
                    df_dados['VIAGEM_UNICA_ID'] = df_dados.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).ngroup()
                
                # Garante que as colunas são numéricas
                df_dados['M3'] = pd.to_numeric(df_dados['M3'], errors='coerce').fillna(0)
                df_dados['PESO REAL (KG)'] = pd.to_numeric(df_dados['PESO REAL (KG)'], errors='coerce').fillna(0)

                # DataFrame com cada viagem única no período
                viagens_unicas = df_dados.drop_duplicates(subset=['VIAGEM_UNICA_ID']).copy()

                # --- LÓGICA DE CAPACIDADE DE PESO ---
                capacidades_padrao_veiculo_sozinho = {'TRUCK': 16000, 'TOCO': 10000, '3/4 - CAMINHAO PEQUE': 4500}
                def get_capacidade_viagem_peso(row):
                    if pd.notna(row['PLACA_CARRETA']) and row['PLACA_CARRETA'] != '' and row['CAPACIDADE_KG'] > 0:
                        return row['CAPACIDADE_KG']
                    if row['CAPAC_CAVALO'] > 0:
                        return row['CAPAC_CAVALO']
                    tipo_veiculo = str(row['TIPO_CAVALO']).upper()
                    return capacidades_padrao_veiculo_sozinho.get(tipo_veiculo, 0)
                
                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)
                
                # Soma a capacidade de peso de cada viagem
                dados['cap_total_peso'] = viagens_unicas['CAPACIDADE_PESO_VIAGEM'].sum()
                # Soma o peso total transportado em todas as viagens
                dados['total_peso'] = df_dados['PESO REAL (KG)'].sum()
                
                # --- LÓGICA DE CAPACIDADE DE VOLUME ---
                capacidades_volume_por_tipo = {'TRUCK': 75, 'CAVALO': 110, 'TOCO': 55, '3/4 - CAMINHAO PEQUE': 40, 'PADRAO': 80}
                viagens_unicas['CAP_VOL_VIAGEM'] = viagens_unicas['TIPO_CAVALO'].map(capacidades_volume_por_tipo).fillna(80)
                
                # Soma a capacidade de volume de cada viagem
                dados['cap_total_volume'] = viagens_unicas['CAP_VOL_VIAGEM'].sum()
                # Soma o volume total transportado em todas as viagens
                dados['total_volume'] = df_dados['M3'].sum()

                # --- CÁLCULO DOS PERCENTUAIS DE OCUPAÇÃO (MÉDIA DO PERÍODO) ---
                # Agora, o percentual é a divisão do total transportado pela capacidade total ofertada no período.
                # Isso representa a OCUPAÇÃO MÉDIA de todas as viagens.
                dados['ocup_peso_perc'] = (dados['total_peso'] / dados['cap_total_peso'] * 100) if dados['cap_total_peso'] > 0 else 0
                dados['ociosidade_peso_perc'] = 100 - dados['ocup_peso_perc']
                dados['potencial_nao_utilizado_kg'] = max(0, dados['cap_total_peso'] - dados['total_peso'])
                
                dados['ocup_volume_perc'] = (dados['total_volume'] / dados['cap_total_volume'] * 100) if dados['cap_total_volume'] > 0 else 0
                dados['ociosidade_volume_perc'] = 100 - dados['ocup_volume_perc']
                dados['potencial_nao_utilizado_m3'] = max(0, dados['cap_total_volume'] - dados['total_volume'])
                
                return dados


            # --- 3. FUNÇÃO PARA RENDERIZAR OS CARDS ---
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
                else: # tipo_metrica == 'volume'
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
                
                # --- LINHA CORRIGIDA/ADICIONADA AQUI ---
                # Extrai a cor secundária do gradiente para usar na borda
                borda_ocios = cor_ocios.split(',')[1].strip() if ',' in cor_ocios else cor_ocios

                with container:
                    # Card de Ocupação (sem alterações)
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
                            <span>Capacidade: {formatar_numero(cap_total, 0 if unidade == 'KG' else 2)} {unidade}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    # Card de Ociosidade (HTML corrigido para usar a variável 'borda_ocios')
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {borda_ocios}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7;">
                        <span class="aviso-ociosidade-texto"><i class="{icone_ociosidade}"></i> {titulo_ociosidade}: {ociosidade_perc:.0f}%</span>
                        <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                            <div style="width: {min(ociosidade_perc, 100)}%; height: 100%; background: {cor_ocios};"></div>
                        </div>
                        <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(potencial_nao_utilizado, 2 if unidade == 'M³' else 0)} {unidade}</span>
                    </div>""", unsafe_allow_html=True)

            # --- 4. RENDERIZAÇÃO FINAL ---
            dados_agregados = calcular_dados_ocupacao_geral(df_para_analise)
            
            if dados_agregados:
                col1, col2 = st.columns(2, gap="large")
                renderizar_card_ocupacao(dados_agregados, 'peso', col1)
                renderizar_card_ocupacao(dados_agregados, 'volume', col2)
            else:
                st.info(f"Nenhum dado de ocupação encontrado para '{selecionar_veiculo}' no período selecionado.")

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

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # CÓDIGO NOVO E CORRIGIDO

        # ==============================
        # 8. TABELA RESUMIDA E DETALHES DA VIAGEM (VERSÃO FINAL COM AGRUPAMENTO CORRIGIDO)
        # ==============================
        st.subheader("📋 Resumo das Viagens no Período")

        df_viagens = df_para_analise.copy()

        if not df_viagens.empty:
            if 'VIAGEM_ID' not in df_viagens.columns:
                df_viagens['VIAGEM_ID'] = df_viagens.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup() + 1
            
            def juntar_unicos(series):
                return ', '.join(series.dropna().astype(str).unique())

            # --- INÍCIO DA CORREÇÃO NO AGRUPAMENTO ---
            def obter_primeiro_valido(series):
                """
                Dentro de um grupo, encontra e retorna o primeiro valor que não é nulo/vazio.
                Isso garante que a placa da carreta seja capturada mesmo que não esteja na primeira linha.
                """
                for valor in series:
                    if pd.notna(valor) and str(valor).strip() != '' and str(valor).lower() != 'nan':
                        return valor
                return None # Retorna None se nenhum valor válido for encontrado

            # O agrupamento agora usa a nova função 'obter_primeiro_valido' para as placas
            resumo_viagens = df_viagens.groupby('VIAGEM_ID').agg(
                EMISSÃO=('EMIS_MANIF', 'first'),
                NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                SITUACAO=('SITUACAO', 'first'),
                CONFERENTE_CARGA=('CONFERENTE CARGA', 'first'), # <<< ADICIONE ESTA LINHA
                MOTORISTA=('MOTORISTA', 'first'),
                PLACA_CAVALO=('PLACA_CAVALO', 'first'),
                PLACA_CARRETA=('PLACA_CARRETA', obter_primeiro_valido), # <-- LÓGICA CORRIGIDA AQUI
                CAPAC_CAVALO=('CAPAC_CAVALO', 'first'),
                CAP_CARRETA=('CAPACIDADE_KG', 'first'), 
                TIPO_VEICULO=('TIPO_CAVALO', 'first'),
                DESTINOS=('DEST_MANIF', lambda x: ordenar_destinos_geograficamente(x.unique(), ROTAS_COMPOSTAS, ORDEM_DAS_ROTAS)),
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
            # --- FIM DA CORREÇÃO NO AGRUPAMENTO ---

            resumo_viagens.rename(columns={
                'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 
                'TIPO_VEICULO': 'TIPO_CAVALO', 'DESTINOS': 'DEST_MANIF',
                'PROPRIETARIO': 'PROPRIETARIO_CAVALO', 'CUSTO_OS_TOTAL': 'OS-R$',
                'CUSTO_CTRB_TOTAL': 'CTRB-R$', 'FRETE_TOTAL': 'FRETE-R$',
                'NUM_OS_LISTA': 'NUM_OS', 'NUM_CTRB_LISTA': 'NUM_CTRB',
                'ICMS': 'ICMS-R$', 'PESO_KG': 'PESO REAL (KG)',
                'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
            }, inplace=True)

            def obter_capacidade_real_viagem(row):
                capacidade_carreta = row.get('CAP_CARRETA', 0)
                if pd.notna(capacidade_carreta) and capacidade_carreta > 0:
                    return capacidade_carreta
                else:
                    return row.get('CAPAC_CAVALO', 0)
            
            def obter_placa_veiculo_formatada(row):
                placa_cavalo = row.get('PLACA_CAVALO', 'N/A')
                placa_carreta = row.get('PLACA_CARRETA', 'N/A')
                
                if pd.notna(placa_carreta) and placa_carreta != 'nan' and placa_carreta != placa_cavalo:
                    return f"{placa_cavalo} / {placa_carreta}"
                else:
                    return placa_cavalo

            resumo_viagens['Capacidade (KG)'] = resumo_viagens.apply(obter_capacidade_real_viagem, axis=1)
            resumo_viagens['Veículo (Placa)'] = resumo_viagens.apply(obter_placa_veiculo_formatada, axis=1)

            # ✅ Ajusta VIAGEM para começar em 1 (como COLUNA, não índice)
            resumo_viagens = resumo_viagens.reset_index(drop=True)
            resumo_viagens['VIAGEM'] = range(1, len(resumo_viagens) + 1)

            def calcular_custo_final(row):
                custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                destinos_str = str(row.get('DEST_MANIF', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base

            def obter_numero_documento(row):
                return row['NUM_OS'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['NUM_CTRB']

            def calcular_distancia_viagem(row):
                custo_km_por_tipo = {'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75}
                tipo_veiculo = str(row.get('TIPO_CAVALO', 'PADRAO')).upper()
                valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                custo_viagem = row['Custo (CTRB/OS)']
                if valor_km > 0 and custo_viagem > 0:
                    return custo_viagem / valor_km
                return 0.0

            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_final, axis=1)
            resumo_viagens['Nº Documento Custo'] = resumo_viagens.apply(obter_numero_documento, axis=1)
            resumo_viagens['DISTANCIA'] = resumo_viagens.apply(calcular_distancia_viagem, axis=1)

            def calcular_ctrb_frete_numerico(row):
                try:
                    custo = float(row['Custo (CTRB/OS)'])
                    frete = float(row['FRETE-R$'])
                    return (custo / frete) * 100 if frete > 0 else 0.0
                except (ValueError, TypeError):
                    return 0.0

            resumo_viagens['CTRB/Frete (%)_valor'] = resumo_viagens.apply(calcular_ctrb_frete_numerico, axis=1)
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.0f}%")

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
            resumo_viagens['Capacidade (KG)'] = resumo_viagens['Capacidade (KG)'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg')
            resumo_viagens['DISTANCIA'] = resumo_viagens['DISTANCIA'].astype(float).apply(lambda x: f"{int(x):,} km".replace(",", "."))

            resumo_viagens.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto',
                'TIPO_CAVALO': 'TIPO', 'DEST_MANIF': 'DESTINOS', 'Nº Documento Custo': 'Nº CTRB/OS',
                'QTDE_CTRC': 'Qtd. CTRCs',
                'SITUACAO': 'SITUAÇÃO',
                'CONFERENTE_CARGA': 'CONFERENTE' # <<< ADICIONE ESTA LINHA
            }, inplace=True)

            # --- ORDEM FINAL DAS COLUNAS ATUALIZADA (MAIS LIMPA) ---
            ordem_final = [
                'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUAÇÃO',
                'CONFERENTE', # <<< ADICIONE A NOVA COLUNA AQUI
                'MOTORISTA',
                'CTRB/Frete (%)',
                'DESTINOS',
                'DISTANCIA',
                'ENTREGAS', 'TIPO',
                'Veículo (Placa)', # <-- NOVA COLUNA DE PLACA UNIFICADA
                'PESO REAL (KG)',
                'Capacidade (KG)', # <-- COLUNA DE CAPACIDADE UNIFICADA
                'M3',
                'Nº CTRB/OS', 'Custo (CTRB/OS)',
                'FRETE-R$', 'ICMS-R$', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
            ]

            colunas_para_exibir = [col for col in ordem_final if col in resumo_viagens.columns]
            df_para_exibir = resumo_viagens[colunas_para_exibir].copy()

            df_para_exibir_ordenado = df_para_exibir.sort_values(by='VIAGEM', ascending=True)

            # 2. Define a função de cores que recebe o valor diretamente
            def colorir_celula_ctrb(valor_texto):
                """
                Recebe o valor da célula como texto (ex: "26%"), converte para número e retorna o estilo.
                - BOM (0 a 25%): Verde
                - REGULAR (26 a 45%): Amarelo
                - PÉSSIMO (>= 46%): Vermelho
                """
                try:
                    # Remove o '%' e converte para número
                    v = float(valor_texto.strip('%'))
                except (ValueError, TypeError):
                    return '' # Sem estilo se a célula estiver vazia ou não for um número

                if 0 <= v <= 25:
                    return 'background-color: #2E7D32; color: white;'
                elif 26 <= v <= 45:
                    return 'background-color: #FF8F00; color: white;'
                elif v >= 46:
                    return 'background-color: #C62828; color: white;'
                
                return '' # Cor padrão

            # 3. Aplica a função de estilo diretamente na coluna desejada
            #    O método .style.applymap() passa o valor de cada célula para a função.
            styled_df = df_para_exibir_ordenado.style.applymap(
                colorir_celula_ctrb,
                subset=['CTRB/Frete (%)']
            )

            # 4. Exibe o DataFrame estilizado
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # 5. Adiciona a legenda visual de cores logo abaixo da tabela
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 20px; font-size: 14px;">
                <b style="color: #E0E0E0;">Legenda de Desempenho:</b>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                    <span style="color: #E0E0E0;">Bom </span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                    <span style="color: #E0E0E0;">Regular </span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                    <span style="color: #E0E0E0;">Péssimo </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")     

            try:
                excel_bytes_resumo = to_excel(resumo_viagens)
                st.download_button(
                    label="📥 Download Resumo (Excel)",
                    data=excel_bytes_resumo,
                    file_name="resumo_viagens_filtradas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_resumo"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel para o resumo: {e}")


        # =========================================================
        # 🔹 TABELA DE DETALHES (DOCUMENTOS)
        # =========================================================
        # A tabela detalhada aparecerá se uma VIAGEM ESPECÍFICA ou um GRUPO DE ROTAS for selecionado.
        if rota_sel_visivel != "(Todos)" or grupo_rota_sel != "(Todos)":
        
            # Adiciona um separador visual e um título para a nova seção
            st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)
            
            # Título dinâmico: muda conforme o filtro usado
            if rota_sel_visivel != "(Todos)":
                st.subheader("📄 Detalhes dos Documentos da Viagem")
            else: # Se chegou aqui, é porque o grupo_rota_sel foi usado
                st.subheader(f"📄 Detalhes dos Documentos do Grupo: {grupo_rota_sel}")

            # O 'df_filtrado' já contém os dados corretos para a viagem ou grupo de rotas selecionado.
            # Vamos criar uma cópia para trabalhar com segurança.
            df_detalhado_base = df_filtrado.copy()

            # 1. FUNÇÕES PARA UNIFICAR AS COLUNAS DE CUSTO
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
            colunas_para_exibir_detalhe = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS', 'Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'PESO REAL (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            
            # 4. Garante que apenas colunas existentes sejam usadas
            colunas_existentes_detalhe = [col for col in colunas_para_exibir_detalhe if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes_detalhe].copy()

            # 5. Renomeia as colunas para uma apresentação mais limpa
            df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino', 'PLACA_CAVALO': 'PLACA', 'TIPO_CAVALO': 'TIPO', 
                'QTDE_CTRC': 'Qtd. CTRCs'
            }, inplace=True)

            # 6. Formata as colunas para exibição
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')
            
            colunas_moeda_det = ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)
            
            if 'PESO REAL (KG)' in df_detalhado_final.columns:
                df_detalhado_final['PESO REAL (KG)'] = df_detalhado_final['PESO REAL (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].apply(lambda x: x / 10000 if x > 1000 else x).apply(lambda x: formatar_numero(x, 3))

            # 7. Exibe a tabela final
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)
            
            # 8. Adiciona o botão de download
            try:
                excel_bytes_detalhado = to_excel(df_detalhado_base[colunas_existentes_detalhe])
                nome_arquivo = f"detalhes_{grupo_rota_sel.replace('/', '_') if grupo_rota_sel != '(Todos)' else 'viagem_especifica'}.xlsx"

                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado_tab1"
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
        
        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
        
        # Futuramente, você pode adicionar gráficos e outras análises aqui.
        # st.info("Área reservada para gráficos de análise financeira.")

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
        # --- SELETOR DE PROPRIETÁRIO ---
        selecao_proprietario = option_menu(
            menu_title=None,
            options=["TODOS", "FROTA KM", "TERCEIROS"],
            icons=["collection-fill", "building", "person-badge"],
            menu_icon="cast", default_index=0, orientation="horizontal",
            key="select_proprietario_tab3", # Chave única para evitar erro de ID duplicado
            styles={
                "container": {"padding": "6px", "background-color": "rgba(30, 30, 40, 0.4)", "border-radius": "16px", "justify-content": "center"},
                "icon": {"color": "#FFFFFF", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "font-weight": "600", "color": "#E5E7EB", "padding": "10px 26px", "border-radius": "12px", "margin": "0px 6px", "background-color": "rgba(255, 255, 255, 0.05)"},
                "nav-link:hover": {"background-color": "rgba(255,255,255,0.12)", "color": "#fff"},
                "nav-link-selected": {"background": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)", "color": "white"},
            }
        )

        # --- ▼▼▼ LÓGICA DE FILTRAGEM CORRIGIDA E CENTRALIZADA ▼▼▼ ---
        # Começa com o df_filtrado (que já vem da sidebar) e aplica o filtro desta aba
        df_viagens = df_filtrado.copy()
        if selecao_proprietario == "FROTA KM":
            df_viagens = df_viagens[df_viagens['PROPRIETARIO_CAVALO'] == 'KM TRANSPORTES ROD. DE CARGAS LTDA']
        elif selecao_proprietario == "TERCEIROS":
            df_viagens = df_viagens[df_viagens['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME']
        # Se 'TODOS' estiver selecionado, df_viagens permanece como uma cópia completa de df_filtrado.

        # --- 4. CÁLCULO E EXIBIÇÃO DOS KPIs ---
        if not df_viagens.empty:
            # Adiciona VIAGEM_ID ao df_viagens JÁ FILTRADO
            df_viagens["VIAGEM_ID"] = df_viagens.groupby(["MOTORISTA", "PLACA_CAVALO", "DIA_EMISSAO_STR"], sort=False).ngroup() + 1
            
            # Define capacidades
            capacidades = {
                'TOCO': {'peso_kg': 10000, 'volume_m3': 55}, 'TRUCK': {'peso_kg': 16000, 'volume_m3': 75},
                'CAVALO': {'peso_kg': 25000, 'volume_m3': 110}, 'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
            }
            df_viagens['CAPACIDADE_PESO'] = df_viagens['TIPO_CAVALO'].map(lambda x: capacidades.get(str(x).upper(), capacidades['PADRAO'])['peso_kg'])

            # Agrupa por viagem para obter os valores corretos para os cálculos
            resumo_por_viagem = df_viagens.groupby('VIAGEM_ID').agg(
                FRETE_VIAGEM=('FRETE-R$', 'sum'), CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'), PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                TIPO_VEICULO=('TIPO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
                PESO_VIAGEM=('PESO REAL (KG)', 'sum'), ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'),
                CAPACIDADE_PESO_VIAGEM=('CAPACIDADE_PESO', 'first')
            ).reset_index()

            # Função para calcular o custo ajustado por viagem
            def calcular_custo_ajustado_viagem(row):
                custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base
            resumo_por_viagem['CUSTO_AJUSTADO'] = resumo_por_viagem.apply(calcular_custo_ajustado_viagem, axis=1)

            # --- DISTÂNCIA TOTAL UNIFICADA (SOMA DAS VIAGENS INDIVIDUAIS) ---
            custo_km_por_tipo = {
                'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75, 'PADRAO': 0
            }

            # Função para calcular a distância de uma única viagem
            def calcular_distancia_individual(row):
                tipo_veiculo = str(row.get('TIPO_VEICULO', 'PADRAO')).upper()
                valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                custo_viagem = row['CUSTO_AJUSTADO']
                
                if valor_km > 0 and custo_viagem > 0:
                    return custo_viagem / valor_km
                return 0.0

            # Aplica a função para criar uma nova coluna de distância em cada viagem
            resumo_por_viagem['DISTANCIA_VIAGEM'] = resumo_por_viagem.apply(calcular_distancia_individual, axis=1)

            # A distância total agora é a SOMA das distâncias de cada viagem
            distancia_total = resumo_por_viagem['DISTANCIA_VIAGEM'].sum()


            # --- CÁLCULOS COMPLEMENTARES ---
            total_viagens = resumo_por_viagem['VIAGEM_ID'].nunique()
            distancia_media = distancia_total / total_viagens if total_viagens > 0 else 0

            # Conta uma entrega para cada destino em cada viagem
            # --- Contagem de entregas idêntica à aba "Visão Geral" ---
            if not df_viagens.empty:
                entregas_por_viagem = df_viagens.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR'])['DEST_MANIF'].nunique()
                total_entregas = entregas_por_viagem.sum()
            else:
                total_entregas = 0

            peso_total = resumo_por_viagem['PESO_VIAGEM'].sum()
            peso_medio_viagem = peso_total / total_viagens if total_viagens > 0 else 0
            
            capacidade_total = resumo_por_viagem['CAPACIDADE_PESO_VIAGEM'].sum()
            ocupacao_media = (peso_total / capacidade_total * 100) if capacidade_total > 0 else 0
            
            custo_total_kpi = custo_ctrb_os
            frete_total_kpi = resumo_por_viagem['FRETE_VIAGEM'].sum()
            perc_custo_frete = (custo_total_kpi / frete_total_kpi * 100) if frete_total_kpi > 0 else 0

            # Funções de formatação e exibição dos KPIs
            def fmt_num_kpi(v, suf=""): return f"{v:,.0f}{suf}".replace(",", ".")
            def fmt_perc_kpi(v): return f"{v:.0f}%"

            # ▼▼▼ CÓDIGO ATUALIZADO ▼▼▼
            kpi_view = option_menu(
                menu_title=None,
                options=["Médias e Índices", "Valores Totais"],
                icons=["graph-up-arrow", "calculator"],
                menu_icon="cast", 
                default_index=0, 
                orientation="horizontal",
                key="kpi_view_selector_tab3", # Chave única
                styles={
                    # 🔹 Container principal (fundo translúcido com leve blur)
                    "container": {
                        "padding": "6px",
                        "background-color": "rgba(30, 30, 40, 0.4)", # Fundo semi-transparente
                        "border-radius": "16px",
                        "backdrop-filter": "blur(10px)", # Efeito de vidro
                        "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.3)",
                        "justify-content": "center",
                        "margin-bottom": "25px", # Mantém a margem inferior
                    },
                    # 🔹 Ícones
                    "icon": {
                        "color": "#A3A3A3",
                        "font-size": "16px", # Ajustado para consistência
                    },
                    # 🔹 Botões inativos
                    "nav-link": {
                        "font-size": "14px",
                        "font-weight": "600",
                        "color": "#E5E7EB",
                        "padding": "10px 26px",
                        "border-radius": "12px",
                        "margin": "0px 6px",
                        "background-color": "rgba(255, 255, 255, 0.05)", # Fundo sutil
                        "transition": "all 0.4s ease-in-out", # Animação suave
                    },
                    # 🔹 Efeito hover (passar o mouse)
                    "nav-link:hover": {
                        "background-color": "rgba(255, 255, 255, 0.12)",
                        "color": "#fff",
                        "transform": "translateY(-2px)",
                    },
                    # 🔹 Botão selecionado — Estilo refinado com brilho
                    "nav-link-selected": {
                        "background-color": "#222433", # Fundo escuro
                        "color": "#FFFFFF",           # Texto branco
                        "border": "1.5px solid #f97316", # Borda laranja (cor da aba)
                        "box-shadow": "0 0 15px rgba(249, 115, 22, 0.6)", # Brilho (glow) laranja
                        "transform": "translateY(-2px)",
                    },
                }
            )
            # ▲▲▲ FIM DO CÓDIGO ATUALIZADO ▲▲▲


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
            else:  # kpi_view == 'Valores Totais'
                kpis_data = {
                    kpi1: {"titulo": "🗺️ TOTAL DE VIAGENS", "valor": fmt_num_kpi(total_viagens)},
                    kpi2: {"titulo": "🚛 DISTÂNCIA TOTAL", "valor": f"{int(distancia_total):,} km".replace(",", ".")},
                    kpi3: {"titulo": "📦 TOTAL DE ENTREGAS", "valor": fmt_num_kpi(total_entregas)},
                    kpi4: {"titulo": "⚖️ PESO TOTAL", "valor": fmt_num_kpi(peso_total, " kg")},
                    kpi5: {"titulo": "💰 CUSTO TOTAL (CTRB/OS)", "valor": formatar_moeda(custo_total_kpi)},
                    kpi6: {"titulo": "💵 FRETE TOTAL", "valor": formatar_moeda(frete_total_kpi)},
                }
            
            for coluna, info in kpis_data.items():
                with coluna:
                    st.markdown(f"""
                        <div class='kpi-container' style='text-align: center;'>
                            <div class='kpi-title'>{info['titulo']}</div>
                            <div class='kpi-value'>{info['valor']}</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

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
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
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
            
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

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
        
        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # --- ▼▼▼ BLOCO ATUALIZADO: RANKING DE MOTORISTAS (COM FILTROS LADO A LADO) ▼▼▼

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

            # --- 2. CRIAÇÃO DOS SELETORES LADO A LADO ---
            col_filtro1, col_filtro2 = st.columns(2)

            with col_filtro1:
                # Gera a lista de motoristas para o seletor
                lista_motoristas_ranking = ["(Todos)"] + sorted(resumo_motorista['NOME_CURTO'].unique())
                motorista_ranking_sel = st.selectbox(
                    'Selecione um motorista para análise individual:',
                    options=lista_motoristas_ranking,
                    key="filtro_motorista_ranking"
                )

            with col_filtro2:
                # Opções para o novo seletor de desempenho
                opcoes_desempenho = ["(Todos)", "Bom (0-25%)", "Regular (26-45%)", "Péssimo (>45%)"]
                desempenho_sel = st.selectbox(
                    'Filtre por Desempenho de CTRB/Frete (%):',
                    options=opcoes_desempenho,
                    key="filtro_desempenho_ctrb"
                )

            # --- 3. FILTRAGEM DOS DADOS PARA OS GRÁFICOS ---
            # Começa com o dataframe completo do resumo
            df_para_graficos = resumo_motorista.copy()

            # Filtro 1: Aplica o filtro de desempenho CTRB/Frete
            if desempenho_sel == "Bom (0-25%)":
                df_para_graficos = df_para_graficos[df_para_graficos['PERC_CUSTO_FRETE'] <= 25]
            elif desempenho_sel == "Regular (26-45%)":
                df_para_graficos = df_para_graficos[(df_para_graficos['PERC_CUSTO_FRETE'] > 25) & (df_para_graficos['PERC_CUSTO_FRETE'] <= 45)]
            elif desempenho_sel == "Péssimo (>45%)":
                df_para_graficos = df_para_graficos[df_para_graficos['PERC_CUSTO_FRETE'] > 45]
            
            # Filtro 2: Aplica o filtro de motorista sobre o resultado do primeiro filtro
            if motorista_ranking_sel != "(Todos)":
                df_para_graficos = df_para_graficos[df_para_graficos['NOME_CURTO'] == motorista_ranking_sel]

            # --- 4. CRIAÇÃO DAS COLUNAS E GRÁFICOS ---
            # (O restante do código dos gráficos permanece o mesmo)
            col_rank1, col_rank2 = st.columns(2)

            with col_rank1:
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
                
                config_selecionada = opcoes_ranking[selecao_ranking]
                coluna_valor_selecionada = config_selecionada['coluna_valor']
                coluna_ordem_selecionada = config_selecionada['coluna_ordem']
                titulo_eixo_selecionado = config_selecionada['titulo_eixo']
                ordem_selecionada = config_selecionada['ordem']
                formato_label_selecionado = config_selecionada['formato_label']

                # Verifica se há dados para plotar após a filtragem
                if not df_para_graficos.empty:
                    ranking_dinamico_df = df_para_graficos.sort_values(
                        by=coluna_ordem_selecionada, 
                        ascending=(ordem_selecionada == 'ascending')
                    )

                    if periodo_tipo in ["Mês Completo", "Período Personalizado"]:
                        ranking_dinamico_df = ranking_dinamico_df.head(15)

                    if selecao_ranking == 'Performance das Viagens - CTRB/Frete (%)':
                        ranking_dinamico_df['cor_barra'] = ranking_dinamico_df[coluna_valor_selecionada].apply(
                            lambda x: '#2E7D32' if x <= 25 else ('#FF8F00' if x <= 45 else '#C62828')
                        )
                        color_condition = alt.Color('cor_barra:N', scale=None)
                    else:
                        color_condition = alt.Color(f'{coluna_valor_selecionada}:Q',
                                        scale=alt.Scale(scheme='reds', reverse=(ordem_selecionada == 'ascending')),
                                        legend=None)

                    barras_dinamicas = alt.Chart(ranking_dinamico_df).mark_bar(
                        cornerRadius=5, height=25
                    ).encode(
                        x=alt.X(f'{coluna_valor_selecionada}:Q', title=titulo_eixo_selecionado, axis=alt.Axis(format='.0f')),
                        y=alt.Y('NOME_CURTO:N', 
                                title=None, 
                                sort=alt.EncodingSortField(field=coluna_ordem_selecionada, op="min", order=ordem_selecionada),
                                axis=alt.Axis(labelFontSize=14, labelLimit=0)
                            ),
                        color=color_condition,
                        tooltip=[
                            alt.Tooltip('NOME_CURTO', title='Motorista'),
                            alt.Tooltip('PERC_CUSTO_FRETE', title='% Custo/Frete', format='.1f'),
                            alt.Tooltip('TOTAL_VIAGENS', title='Nº de Viagens'),
                            alt.Tooltip('PESO_MEDIO_VIAGEM', title='Peso Médio', format=',.0f')
                        ]
                    )
                    
                    texto_dinamico = barras_dinamicas.transform_calculate(
                        text_label=formato_label_selecionado
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

                    if selecao_ranking == 'Performance das Viagens - CTRB/Frete (%)':
                        st.markdown("""
                        <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 15px; font-size: 14px;">
                            <b style="color: #E0E0E0;">CTRB/Frete (%):</b>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px; border: 1px solid #4A4A4A;"></div>
                                <span style="color: #E0E0E0;">Bom</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px; border: 1px solid #4A4A4A;"></div>
                                <span style="color: #E0E0E0;">Regular</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px; border: 1px solid #4A4A4A;"></div>
                                <span style="color: #E0E0E0;">Péssimo</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhum motorista encontrado para os filtros selecionados.")


            with col_rank2:
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

                if not df_para_graficos.empty:
                    ranking_dinamico_op_df = df_para_graficos.sort_values(
                        by=coluna_ordem_op, ascending=(ordem_op == 'ascending')
                    )

                    if periodo_tipo in ["Mês Completo", "Período Personalizado"]:
                        ranking_dinamico_op_df = ranking_dinamico_op_df.head(15)

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
                    
                    texto_dinamico_op = barras_dinamicas_op.transform_calculate(
                        text_label=formato_label_op
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
                else:
                    # Esta mensagem já existe na coluna da esquerda, não precisa repetir.
                    pass
            
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # --- ▲▲▲ FIM DO BLOCO ATUALIZADO ▲▲▲


            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

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
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
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

# ==================================================================
# ABA 5: GESTÃO DE ROTAS (VERSÃO SIMPLIFICADA)
# ==================================================================
with tab5:

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:

        # --- TÍTULO DA SEÇÃO DE OCUPAÇÃO ---
        st.markdown("""
            <div class="title-block-modern" style="border-left-color: #ef4444; border-right-color: #ef4444;">
                <i class="fa-solid fa-map-signs" style="color: #ef4444;"></i>
                <h2>Análise de Ocupação de Carga por Rota</h2>
            </div>
        """, unsafe_allow_html=True)

        # --- FILTROS DE TIPO DE VIAGEM E ROTA (COM A OPÇÃO "TODAS") ---
        tipo_viagem_ocupacao_sel = option_menu(
            menu_title=None,
            # 1. Adiciona a nova opção "TODAS AS ROTAS" no início
            options=["TODAS AS ROTAS", "ROTA COMPLETA", "VIAGEM EXTRA"],
            # 2. Adiciona o ícone correspondente para a nova opção
            icons=["collection-fill", "arrow-repeat", "exclamation-octagon-fill"],
            menu_icon="filter-circle",
            default_index=0, # Começa com "TODAS AS ROTAS" selecionado
            orientation="horizontal",
            key="option_menu_tipo_viagem_tab5",
            styles={
                "container": {
                    "padding": "5px",
                    "background-color": "#1F2937",
                    "border-radius": "999px",
                    "margin-bottom": "25px",
                    "display": "flex",
                    "justify-content": "center"
                },
                "icon": {
                    "color": "#9CA3AF",
                    "font-size": "16px"
                },
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "600",
                    "color": "#D1D5DB",
                    "text-transform": "uppercase",
                    "padding": "10px 25px",
                    "border-radius": "999px",
                    "margin": "0px",
                    "transition": "all 0.3s ease"
                },
                "nav-link:hover": {
                    "background-color": "rgba(255, 255, 255, 0.05)",
                    "color": "#FFFFFF"
                },
                "nav-link-selected": {
                    "background-color": "#ef4444",
                    "color": "#FFFFFF",
                    "box-shadow": "0 2px 10px rgba(0, 0, 0, 0.3)"
                },
            }
        )
        
        # --- SINCRONIZAÇÃO DO FILTRO DE VIAGEM COM A SELEÇÃO DO MENU ---
        df_filtrado_por_tipo = df_filtrado.copy()
        if not df_filtrado_por_tipo.empty:
            # A função de classificação é chamada para garantir que a coluna exista
            df_classificado_completo = classificar_viagens_do_dia(df_filtrado)

            # Filtra APENAS se a opção não for "TODAS AS ROTAS"
            if tipo_viagem_ocupacao_sel == "ROTA COMPLETA":
                df_filtrado_por_tipo = df_classificado_completo[
                    df_classificado_completo['TIPO_VIAGEM_CALCULADO'] == "Rota Completa"
                ].copy()
            elif tipo_viagem_ocupacao_sel == "VIAGEM EXTRA":
                df_filtrado_por_tipo = df_classificado_completo[
                    df_classificado_completo['TIPO_VIAGEM_CALCULADO'] == "Viagem Extra"
                ].copy()
            # Se for "TODAS AS ROTAS", df_filtrado_por_tipo já é a cópia completa e não fazemos nada
            
            # Garante que, em qualquer caso, o dataframe final seja o classificado
            # para que a lógica subsequente funcione.
            else: # tipo_viagem_ocupacao_sel == "TODAS AS ROTAS"
                df_filtrado_por_tipo = df_classificado_completo.copy()


        # --- SE EXISTIR DADOS APÓS O FILTRO ---
        if not df_filtrado_por_tipo.empty:
            viagens_agrupadas_rotas = df_filtrado_por_tipo.groupby(
                ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']
            )['DEST_MANIF'].unique().reset_index()

            viagens_agrupadas_rotas['NOME_ROTA_PADRAO'] = viagens_agrupadas_rotas['DEST_MANIF'].apply(obter_nome_rota_padronizado)
            lista_opcoes_rotas = ["(Todas as Rotas)"] + sorted(viagens_agrupadas_rotas['NOME_ROTA_PADRAO'].unique())

            # --- INÍCIO DA MODERNIZAÇÃO DO SELETOR ---
            # Envolve o seletor em uma div para aplicar o CSS customizado
            st.markdown("""
                <div class="custom-selectbox-container">
                    <div class="custom-selectbox-label">
                        <i class="fa-solid fa-map-signs"></i>
                        Selecione a Rota para Análise
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # O label é removido do selectbox e colocado no markdown acima
            rota_selecionada_ocupacao = st.selectbox(
                label="selectbox_ocupacao_por_rota_label", # Label interno para o Streamlit
                label_visibility="collapsed", # Esconde o label padrão
                options=lista_opcoes_rotas,
                key="selectbox_ocupacao_por_rota"
            )
           
            df_para_ocupacao = pd.DataFrame()
            if rota_selecionada_ocupacao == "(Todas as Rotas)":
                df_para_ocupacao = df_filtrado_por_tipo.copy()
            else:
                viagens_da_rota_selecionada = viagens_agrupadas_rotas[
                    viagens_agrupadas_rotas['NOME_ROTA_PADRAO'] == rota_selecionada_ocupacao
                ]
                chaves_viagens_rota = list(zip(
                    viagens_da_rota_selecionada['PLACA_CAVALO'],
                    viagens_da_rota_selecionada['DIA_EMISSAO_STR'],
                    viagens_da_rota_selecionada['MOTORISTA']
                ))
                if chaves_viagens_rota:
                    df_para_ocupacao = df_filtrado_por_tipo[
                        pd.MultiIndex.from_frame(df_filtrado_por_tipo[['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']]).isin(chaves_viagens_rota)
                    ]

            # --- CÁLCULO E EXIBIÇÃO DOS CARDS DE OCUPAÇÃO ---
            def calcular_dados_ocupacao(df_dados):
                if df_dados.empty:
                    return None

                dados = {}

                # 1. Identifica cada viagem única para evitar contagem duplicada de capacidade
                viagens_unicas = df_dados.drop_duplicates(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).copy()

                # 2. Lógica de capacidade de PESO robusta
                def get_capacidade_viagem_peso(row):
                    # Se for um CAVALO, a capacidade vem da coluna da carreta ('CAPACIDADE_KG')
                    if row.get('TIPO_CAVALO') == 'CAVALO':
                        return row.get('CAPACIDADE_KG', 0)
                    # Para outros tipos (TRUCK, TOCO), a capacidade vem da coluna do cavalo ('CAPAC_CAVALO')
                    return row.get('CAPAC_CAVALO', 0)

                # Aplica a função para obter a capacidade correta para CADA viagem
                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)

                # A capacidade total é a soma das capacidades individuais de cada viagem
                dados['cap_total_peso'] = viagens_unicas['CAPACIDADE_PESO_VIAGEM'].sum()
                dados['total_peso'] = df_dados['PESO REAL (KG)'].sum()

                # 3. Lógica de capacidade de VOLUME (M³)
                capacidades_volume_por_tipo = {'TRUCK': 75, 'CAVALO': 110, 'TOCO': 55, 'PADRAO': 80}
                viagens_unicas['CAP_VOL_VIAGEM'] = viagens_unicas['TIPO_CAVALO'].map(capacidades_volume_por_tipo).fillna(capacidades_volume_por_tipo['PADRAO'])

                dados['cap_total_volume'] = viagens_unicas['CAP_VOL_VIAGEM'].sum()

                            # --- CÁLCULO E EXIBIÇÃO DOS CARDS DE OCUPAÇÃO ---
            def calcular_dados_ocupacao(df_dados):
                """
                VERSÃO CORRIGIDA: Remove a divisão por 10.000 da cubagem,
                assumindo que os dados do Excel já estão em M³.
                """
                if df_dados.empty:
                    return None

                dados = {}

                # 1. Identifica cada viagem única para evitar contagem duplicada de capacidade
                viagens_unicas = df_dados.drop_duplicates(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).copy()

                # 2. Lógica de capacidade de PESO (sem alterações)
                def get_capacidade_viagem_peso(row):
                    if row.get('TIPO_CAVALO') == 'CAVALO':
                        return row.get('CAPACIDADE_KG', 0)
                    return row.get('CAPAC_CAVALO', 0)

                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)
                dados['cap_total_peso'] = viagens_unicas['CAPACIDADE_PESO_VIAGEM'].sum()
                dados['total_peso'] = df_dados['PESO REAL (KG)'].sum()

                # 3. Lógica de capacidade de VOLUME (M³) (sem alterações)
                capacidades_volume_por_tipo = {'TRUCK': 75, 'CAVALO': 110, 'TOCO': 55, 'PADRAO': 80}
                viagens_unicas['CAP_VOL_VIAGEM'] = viagens_unicas['TIPO_CAVALO'].map(capacidades_volume_por_tipo).fillna(capacidades_volume_por_tipo['PADRAO'])
                dados['cap_total_volume'] = viagens_unicas['CAP_VOL_VIAGEM'].sum()

                # --- ▼▼▼ AQUI ESTÁ A CORREÇÃO PRINCIPAL ▼▼▼ ---
                # A linha que dividia por 10.000 foi removida.
                # Agora, simplesmente somamos os valores da coluna 'M3'.
                dados['total_volume'] = df_dados['M3'].sum()
                # --- ▲▲▲ FIM DA CORREÇÃO ▲▲▲ ---

                # 4. Calcula os percentuais de ocupação e ociosidade (agora com o valor correto)
                dados['ocup_peso_perc'] = (dados['total_peso'] / dados['cap_total_peso'] * 100) if dados['cap_total_peso'] > 0 else 0
                dados['ociosidade_peso_perc'] = 100 - dados['ocup_peso_perc']
                dados['potencial_nao_utilizado_kg'] = max(0, dados['cap_total_peso'] - dados['total_peso'])

                dados['ocup_volume_perc'] = (dados['total_volume'] / dados['cap_total_volume'] * 100) if dados['cap_total_volume'] > 0 else 0
                dados['ociosidade_volume_perc'] = 100 - dados['ocup_volume_perc']
                dados['potencial_nao_utilizado_m3'] = max(0, dados['cap_total_volume'] - dados['total_volume'])

                return dados


            dados_agregados = calcular_dados_ocupacao(df_para_ocupacao)

            if dados_agregados:
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    st.markdown(f"""
                        <div class="ocupacao-card-custom">
                            <div class="progress-card-header">
                                <div class="progress-card-title">⚖️ Ocupação de Peso (KG)</div>
                                <div class="progress-card-value">{dados_agregados['ocup_peso_perc']:.0f}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {min(dados_agregados['ocup_peso_perc'], 100)}%; background: {obter_cor_ocupacao(dados_agregados['ocup_peso_perc'])};"></div>
                            </div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_agregados['total_peso'])} KG</span>
                                <span>Capacidade: {formatar_numero(dados_agregados['cap_total_peso'])} KG</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    cor_ocios_peso = obter_cor_ociosidade(dados_agregados['ociosidade_peso_perc'])
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {cor_ocios_peso.split(',')[1].strip()}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                            <span class="aviso-ociosidade-texto"><i class="fa-solid fa-scale-unbalanced-flip"></i> Ociosidade de Peso: {dados_agregados['ociosidade_peso_perc']:.0f}%</span>
                            <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                                <div style="width: {min(dados_agregados['ociosidade_peso_perc'], 100)}%; height: 100%; background: {cor_ocios_peso};"></div>
                            </div>
                            <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(dados_agregados['potencial_nao_utilizado_kg'])} KG</span>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                        <div class="ocupacao-card-custom">
                            <div class="progress-card-header">
                                <div class="progress-card-title">📦 Ocupação de Cubagem (M³)</div>
                                <div class="progress-card-value">{dados_agregados['ocup_volume_perc']:.0f}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {min(dados_agregados['ocup_volume_perc'], 100)}%; background: {obter_cor_ocupacao(dados_agregados['ocup_volume_perc'])};"></div>
                            </div>
                            <div class="progress-card-footer">
                                <span>Total: {formatar_numero(dados_agregados['total_volume'], 3)} M³</span>
                                <span>Capacidade: {formatar_numero(dados_agregados['cap_total_volume'], 2)} M³</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    cor_ocios_vol = obter_cor_ociosidade(dados_agregados['ociosidade_volume_perc'])
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1E1E2E; border-left: 5px solid {cor_ocios_vol.split(',')[1].strip()}; padding: 10px 16px; border-radius: 8px; margin-top: 10px; color: #e4e4e7; font-size: 0.95rem;">
                            <span class="aviso-ociosidade-texto"><i class="fa-solid fa-box-open"></i> Ociosidade de Cubagem (M³): {dados_agregados['ociosidade_volume_perc']:.0f}%</span>
                            <div style="flex: 1; height: 10px; margin: 0 15px; background-color: #2a2a3a; border-radius: 5px; overflow: hidden;">
                                <div style="width: {min(dados_agregados['ociosidade_volume_perc'], 100)}%; height: 100%; background: {cor_ocios_vol};"></div>
                            </div>
                            <span style="font-weight: bold; white-space: nowrap;">{formatar_numero(dados_agregados['potencial_nao_utilizado_m3'], 2)} M³</span>
                        </div>
                    """, unsafe_allow_html=True)

            else:
                st.info(f"Nenhum dado de ocupação para calcular para a rota '{rota_selecionada_ocupacao}' no período e tipo de viagem selecionados.")

            # =================================================================
            # 🔹 DETALHES POR DESTINO DENTRO DA ROTA (VERSÃO FINAL CORRIGIDA)
            # =================================================================

            def fmt_moeda(valor):
                """Formata número como moeda brasileira: R$ 1.234,56"""
                if pd.isna(valor):
                    return "R$ 0,00"
                return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            def fmt_num(valor):
                """Formata número inteiro com separador de milhar"""
                if pd.isna(valor):
                    return "0"
                return f"{int(valor):,}".replace(",", ".")

            # =================================================================
            # 🔹 DETALHES POR DESTINO DENTRO DA ROTA (VERSÃO FINAL CORRIGIDA)
            # =================================================================

            # Esta condição verifica se uma rota específica ou uma viagem específica foi selecionada.
            if rota_selecionada_ocupacao != "(Todas as Rotas)" or viagem_especifica_sel != "(Todos)":

                # --- 1. Adiciona um separador e o CSS específico para os novos cards ---
                st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

                # --- INÍCIO DA NOVA LÓGICA PARA O TÍTULO ---
                titulo_analise = ""

                # Se uma VIAGEM ESPECÍFICA for selecionada, monta o título detalhado
                if viagem_especifica_sel != "(Todos)":
                    # Busca os detalhes da viagem selecionada no dataframe 'rotas_df_antigo'
                    viagem_selecionada_info = rotas_df_antigo[rotas_df_antigo['NOME_ROTA_ANTIGO'] == viagem_especifica_sel]
                    
                    if not viagem_selecionada_info.empty:
                        # Pega a primeira (e única) linha de resultado
                        info = viagem_selecionada_info.iloc[0]
                        
                        # Extrai os dados para o título
                        destinos = info['Destinos'] # Já vem formatado como 'DOU - RBT'
                        motorista = info['NOME_CURTO_MOTORISTA']
                        
                        # Monta o título no formato desejado
                        titulo_analise = f"{destinos}  | 👨‍✈️ {motorista}"
                    else:
                        # Fallback caso não encontre a informação
                        titulo_analise = "Viagem Específica"

                # Se um GRUPO DE ROTAS for selecionado, usa o nome do grupo
                elif rota_selecionada_ocupacao != "(Todas as Rotas)":
                    titulo_analise = rota_selecionada_ocupacao
                # --- FIM DA NOVA LÓGICA PARA O TÍTULO ---


                # ✅ TÍTULO ATUALIZADO COM OS DETALHES DA VIAGEM
                st.markdown(
                    f'<h3 class="section-title-modern">'
                    f'<i class="fa-solid fa-chart-line"></i> '
                    f'Análise Operacional – <span style="color:#3B82F6;">{titulo_analise}</span>'
                    f'</h3>',
                    unsafe_allow_html=True
                )

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
                    font-size: 1.2rem;          /* <<< TAMANHO DA FONTE AUMENTADO */
                    font-weight: 700;           /* <<< PESO DA FONTE AUMENTADO (BOLD) */
                    color: #FFFFFF;             /* Cor mais branca para destaque */
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start; /* <<< ALTERADO DE 'center' PARA 'flex-start' */
                    gap: 10px;                  /* Espaço entre o ícone e o texto */
                    text-transform: uppercase;  /* Garante que o texto fique em maiúsculas */
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
                    font-size: 0.9rem;      /* <<< TAMANHO DA FONTE AUMENTADO */
                    color: #B0B8C4;         /* Cor um pouco mais clara para legibilidade */
                    margin-bottom: 8px;     /* Aumenta o espaço entre o rótulo e o valor */
                    display: flex;
                    align-items: center;
                    gap: 8px;               /* Aumenta o espaço entre o ícone e o texto */
                    font-weight: 500;       /* Deixa a fonte um pouco mais encorpada */
}
                .metric-value {
                    font-size: 1.3rem;
                    font-weight: 700;
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

                # --- 2. AGREGA OS DADOS por cidade, usando o DataFrame da rota selecionada ---
                carga_por_cidade = df_para_ocupacao.groupby('CIDADE_UF_DEST').agg(
                    PESO_TOTAL=('PESO REAL (KG)', 'sum'),
                    VOLUME_TOTAL=('M3', 'sum'),
                    FRETE_TOTAL=('FRETE-R$', 'sum'),
                    VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                    QTDE_CTRC=('QTDE_CTRC', 'sum'),
                    QTDE_VOLUME=('VOLUMES', 'sum')
                ).reset_index()

                # ▼▼▼ INÍCIO DA CORREÇÃO FINAL E MAIS ROBUSTA ▼▼▼

                # 1. Cria um dicionário reverso para "traduzir" NOME COMPLETO -> SIGLA
                mapa_nome_para_sigla = {nome.upper(): sigla for sigla, nome in MAPA_SIGLA_NOME_COMPLETO.items()}

                # 2. Adiciona uma coluna temporária 'SIGLA' ao DataFrame 'carga_por_cidade'
                carga_por_cidade['SIGLA'] = carga_por_cidade['CIDADE_UF_DEST'].str.upper().map(mapa_nome_para_sigla)

                # 3. Busca a ordem correta das SIGLAS para a rota selecionada
                rota_selecionada = rota_selecionada_ocupacao
                ordem_siglas_correta = ORDEM_DAS_ROTAS.get(rota_selecionada, [])

                # 4. Se uma ordem foi encontrada, usa-a para ordenar o DataFrame pelas SIGLAS
                if ordem_siglas_correta:
                    # Converte a coluna 'SIGLA' para uma categoria ordenada
                    carga_por_cidade['SIGLA'] = pd.Categorical(
                        carga_por_cidade['SIGLA'],
                        categories=ordem_siglas_correta,
                        ordered=True
                    )
                    # Ordena o DataFrame com base na ordem das siglas e remove a coluna temporária
                    carga_por_cidade = carga_por_cidade.sort_values('SIGLA').drop(columns=['SIGLA'])

                # ▲▲▲ FIM DA CORREÇÃO FINAL ▲▲▲


                # --- BLOCO DE KPIs POR CIDADE ---
                num_cidades = len(carga_por_cidade)
                cols = st.columns(num_cidades if num_cidades > 0 else 1)

                def fmt_m3(valor):
                    """Formata volume em m³ com 3 casas decimais e separador brasileiro"""
                    if pd.isna(valor):
                        return "0,000"
                    return f"{round(valor, 3):,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


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
                    <div class="metric-value">{fmt_m3(row['VOLUME_TOTAL'])} M³</div>
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
       
            st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

            # --- SEÇÃO DE INDICADORES DE PERFORMANCE ---
            kpi_view_rotas = option_menu(
                menu_title=None,
                options=["MÉDIAS E ÍNDICES", "VALORES TOTAIS"],  # 🔠 Maiúsculo
                icons=["graph-up-arrow", "calculator"],
                menu_icon=None,  # 🔇 remove ícone global
                default_index=0,
                orientation="horizontal",
                key="kpi_view_selector_tab5",
                styles={
                    "container": {
                        "padding": "6px",
                        "background-color": "rgba(30, 30, 40, 0.4)",
                        "border-radius": "16px",
                        "justify-content": "center",
                        "margin-bottom": "25px"
                    },
                    "icon": {
                        "color": "#A3A3A3",
                        "font-size": "16px"
                    },
                    "nav-link": {
                        "font-size": "14px",
                        "font-weight": "700",              # negrito mais forte
                        "color": "#E5E7EB",
                        "text-transform": "uppercase",     # 🔠 força maiúsculo
                        "padding": "10px 26px",
                        "border-radius": "12px",
                        "margin": "0px 6px",
                        "background-color": "rgba(255, 255, 255, 0.05)",
                        "transition": "all 0.3s ease"
                    },
                    "nav-link:hover": {
                        "background-color": "rgba(255,255,255,0.12)",
                        "color": "#FFFFFF"
                    },
                    "nav-link-selected": {
                        "background-color": "#222433",
                        "color": "#FFFFFF",
                        "border": "1.5px solid #ef4444",
                        "box-shadow": "0 0 15px rgba(239, 68, 68, 0.6)"
                    },
                }
            )

            if not df_para_ocupacao.empty:
                resumo_viagens_kpi = df_para_ocupacao.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).agg(CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'), PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), TIPO_VEICULO=('TIPO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())), PESO_VIAGEM=('PESO REAL (KG)', 'sum'), ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'), FRETE_VIAGEM=('FRETE-R$', 'sum'), CAPACIDADE_PESO=('CAPACIDADE_KG', 'first'), CAPACIDADE_PESO_CAVALO=('CAPAC_CAVALO', 'first')).reset_index()
                def calcular_custo_ajustado(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    if 'GYN' in str(row['DESTINOS']) or 'SPO' in str(row['DESTINOS']): return custo_base / 2
                    return custo_base
                resumo_viagens_kpi['CUSTO_AJUSTADO'] = resumo_viagens_kpi.apply(calcular_custo_ajustado, axis=1)
                custo_km_por_tipo = {'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75}
                def calcular_distancia_viagem(row):
                    valor_km = custo_km_por_tipo.get(str(row['TIPO_VEICULO']).upper(), 0)
                    if valor_km > 0: return row['CUSTO_AJUSTADO'] / valor_km
                    return 0
                resumo_viagens_kpi['DISTANCIA_VIAGEM'] = resumo_viagens_kpi.apply(calcular_distancia_viagem, axis=1)
                def get_capacidade_correta(row):
                    if row['TIPO_VEICULO'] == 'CAVALO': return row['CAPACIDADE_PESO']
                    return row['CAPACIDADE_PESO_CAVALO']
                resumo_viagens_kpi['CAPACIDADE_VIAGEM'] = resumo_viagens_kpi.apply(get_capacidade_correta, axis=1)
                total_viagens = len(resumo_viagens_kpi)
                distancia_total = resumo_viagens_kpi['DISTANCIA_VIAGEM'].sum()
                total_entregas = resumo_viagens_kpi['ENTREGAS_VIAGEM'].sum()
                peso_total = resumo_viagens_kpi['PESO_VIAGEM'].sum()
                custo_total_kpi = resumo_viagens_kpi['CUSTO_AJUSTADO'].sum()
                frete_total_kpi = resumo_viagens_kpi['FRETE_VIAGEM'].sum()
                capacidade_total_kpi = resumo_viagens_kpi['CAPACIDADE_VIAGEM'].sum()
                distancia_media = distancia_total / total_viagens if total_viagens > 0 else 0
                peso_medio_viagem = peso_total / total_viagens if total_viagens > 0 else 0
                ocupacao_media = (peso_total / capacidade_total_kpi * 100) if capacidade_total_kpi > 0 else 0
                perc_custo_frete = (custo_total_kpi / frete_total_kpi * 100) if frete_total_kpi > 0 else 0
                kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
                if kpi_view_rotas.upper() == "MÉDIAS E ÍNDICES":
                    kpis_data = [{'titulo': "🗺️ TOTAL DE VIAGENS", "valor": f"{total_viagens}"}, {'titulo': "🚛 DISTÂNCIA MÉDIA", "valor": f"{int(distancia_media):,} km".replace(",", ".")}, {'titulo': "📦 TOTAL DE ENTREGAS", "valor": f"{total_entregas}"}, {'titulo': "⚖️ PESO MÉDIO / VIAGEM", "valor": f"{int(peso_medio_viagem):,} kg".replace(",", ".")}, {'titulo': "📈 OCUPAÇÃO MÉDIA", "valor": f"{ocupacao_media:.0f}%"}, {'titulo': "📊 % CUSTO / FRETE", "valor": f"{perc_custo_frete:.0f}%"}]
                else:
                    kpis_data = [{'titulo': "🗺️ TOTAL DE VIAGENS", "valor": f"{total_viagens}"}, {'titulo': "🚛 DISTÂNCIA TOTAL", "valor": f"{int(distancia_total):,} km".replace(",", ".")}, {'titulo': "📦 TOTAL DE ENTREGAS", "valor": f"{total_entregas}"}, {'titulo': "⚖️ PESO TOTAL", "valor": f"{int(peso_total):,} kg".replace(",", ".")}, {'titulo': "💰 CUSTO TOTAL (CTRB/OS)", "valor": formatar_moeda(custo_total_kpi)}, {'titulo': "💵 FRETE TOTAL", "valor": formatar_moeda(frete_total_kpi)}]
                colunas_kpi = [kpi1, kpi2, kpi3, kpi4, kpi5, kpi6]
                for i, info in enumerate(kpis_data):
                    with colunas_kpi[i]:
                        st.markdown(f"""<div class='kpi-container' style='text-align: center;'><div class='kpi-title'>{info['titulo']}</div><div class='kpi-value'>{info['valor']}</div></div>""", unsafe_allow_html=True)
            else:
                st.info("Não há dados de performance para exibir para a seleção atual.")

            # --- ▼▼▼ INÍCIO DO BLOCO DE GRÁFICOS DE BARRAS (COM LÓGICA ATUALIZADA) ▼▼▼

            # A exibição dos gráficos agora depende apenas de haver dados
            if not df_para_ocupacao.empty:
                st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

                # 1. PREPARAÇÃO DOS DADOS (AGORA COM LÓGICA CONDICIONAL)
                resumo_viagens_base = df_para_ocupacao.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).agg(
                    CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
                    PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', 'unique'),
                    PESO_VIAGEM=('PESO REAL (KG)', 'sum'), FRETE_VIAGEM=('FRETE-R$', 'sum'),
                    TIPO_VEICULO=('TIPO_CAVALO', 'first'), CAPACIDADE_PESO_CARRETA=('CAPACIDADE_KG', 'first'),
                    CAPACIDADE_PESO_CAVALO=('CAPAC_CAVALO', 'first')
                ).reset_index()

                def get_capacidade_correta(row):
                    if row['TIPO_VEICULO'] == 'CAVALO': return row['CAPACIDADE_PESO_CARRETA']
                    return row['CAPACIDADE_PESO_CAVALO']
                resumo_viagens_base['CAPACIDADE_VIAGEM'] = resumo_viagens_base.apply(get_capacidade_correta, axis=1)

                def calcular_custo_ajustado(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    if any(dest in str(row['DESTINOS']) for dest in ['GYN', 'SPO']): return custo_base / 2
                    return custo_base
                resumo_viagens_base['CUSTO_AJUSTADO'] = resumo_viagens_base.apply(calcular_custo_ajustado, axis=1)
                
                resumo_viagens_base['NOME_ROTA'] = resumo_viagens_base['DESTINOS'].apply(obter_nome_rota_padronizado)

                # --- LÓGICA PRINCIPAL CORRIGIDA: Agrupa os dados para o gráfico ---
                df_grafico = resumo_viagens_base.groupby('NOME_ROTA').agg(
                    CTRB_FRETE_PERC=('FRETE_VIAGEM', lambda x: (resumo_viagens_base.loc[x.index, 'CUSTO_AJUSTADO'].sum() / x.sum() * 100) if x.sum() > 0 else 0),
                    OCUPACAO_KG_PERC=('PESO_VIAGEM', lambda x: (x.sum() / resumo_viagens_base.loc[x.index, 'CAPACIDADE_VIAGEM'].sum() * 100) if resumo_viagens_base.loc[x.index, 'CAPACIDADE_VIAGEM'].sum() > 0 else 0),
                    TOTAL_VIAGENS=('NOME_ROTA', 'size')
                ).reset_index()

                # As variáveis para o Altair agora são sempre as mesmas
                tooltip_label = 'NOME_ROTA'
                titulo_tooltip = 'Rota'
                eixo_y_ordenacao = 'NOME_ROTA'

                # Cria a nova coluna 'LABEL_EIXO_Y' substituindo 'ROTA ' pelo ícone
                coluna_fonte = 'NOME_ROTA' if 'NOME_ROTA' in df_grafico.columns else 'VIAGEM_LABEL'
                if coluna_fonte in df_grafico.columns:
                    df_grafico['LABEL_EIXO_Y'] = df_grafico[coluna_fonte].str.replace('ROTA ', 'ROTA 📍 ', regex=False)
                else:
                    df_grafico['LABEL_EIXO_Y'] = ''

                # --- 2. CRIAÇÃO DOS GRÁFICOS LADO A LADO ---
                col_graf1, col_graf2 = st.columns(2, gap="large")

                # ===============================================
                # 🔴 GRÁFICO 1 - Performance das Viagens
                # ===============================================
                with col_graf1:
                    opcoes_ranking_ctrb = {
                        'Performance das Viagens - CTRB/Frete (%)': 'CTRB_FRETE_PERC',
                        'Ordem Alfabética': eixo_y_ordenacao
                    }
                    selecao_ranking_ctrb = st.selectbox(
                        'Selecione a métrica para o ranking:',
                        options=list(opcoes_ranking_ctrb.keys()),
                        key='ranking_ctrb_selector'
                    )

                    # --- INÍCIO DA LÓGICA DE CORES ATUALIZADA ---
                    # 1. Pré-calcula a cor para cada rota com base nas faixas de desempenho
                    df_grafico['cor_barra'] = df_grafico['CTRB_FRETE_PERC'].apply(
                        # Se <= 25, é Verde (Bom). Se <= 45, é Laranja (Regular). Senão, é Vermelho (Péssimo).
                        lambda x: '#2E7D32' if x <= 25 else ('#FF8F00' if x <= 45 else '#C62828')
                    )
                    
                    # 2. Define a cor no Altair para usar a coluna pré-calculada
                    color_condition = alt.Color(
                        'cor_barra:N', # Usa a coluna 'cor_barra' como uma categoria de cor
                        scale=None     # Diz ao Altair para usar os valores hexadecimais diretamente
                    )
                    # --- FIM DA LÓGICA DE CORES ATUALIZADA ---

                    ordenacao_ctrb = alt.EncodingSortField(
                        field=opcoes_ranking_ctrb[selecao_ranking_ctrb],
                        op="min",
                        order='ascending' # 'ascending' para mostrar os melhores (menores %) no topo
                    )

                    st.markdown("##### Performance das Viagens")

                    barras_ctrb = alt.Chart(df_grafico).mark_bar(cornerRadius=5).encode(
                        x=alt.X('CTRB_FRETE_PERC:Q', title='CTRB/Frete (%)', axis=alt.Axis(format='.0f', titleFontSize=14, labelFontSize=12)),
                        y=alt.Y('LABEL_EIXO_Y:N', title=None, sort=ordenacao_ctrb, 
                                axis=alt.Axis(labelFontSize=14, labelLimit=0)
                            ),
                        color=color_condition, # Aplica a cor condicional
                        tooltip=[
                            alt.Tooltip(tooltip_label, title=titulo_tooltip),
                            alt.Tooltip('CTRB_FRETE_PERC', title='CTRB/Frete', format='.1f'),
                            alt.Tooltip('TOTAL_VIAGENS:Q', title='Total de Viagens') if 'TOTAL_VIAGENS' in df_grafico.columns else alt.Tooltip('MOTORISTA', title='Motorista')
                        ]
                    )

                    texto_ctrb = alt.Chart(df_grafico).mark_text(
                        align='left', baseline='middle', dx=5, fontSize=14, color='white'
                    ).transform_calculate(
                        label_text="format(datum.CTRB_FRETE_PERC, '.0f') + '%'"
                    ).encode(
                        y=alt.Y('LABEL_EIXO_Y:N', sort=ordenacao_ctrb),
                        x='CTRB_FRETE_PERC:Q',
                        text='label_text:N'
                    )

                    chart_final_ctrb = (barras_ctrb + texto_ctrb).properties(
                        height=alt.Step(40)
                    ).configure_view(stroke=None).configure_axis(grid=False)

                    st.altair_chart(chart_final_ctrb, use_container_width=True)

                    # --- ▼▼▼ NOVO BLOCO: LEGENDA DE DESEMPENHO ▼▼▼ ---
                    st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 15px; font-size: 14px;">
                        <b style="color: #E0E0E0;">CTRB/Frete (%):</b>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                            <span style="color: #E0E0E0;">Bom</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                            <span style="color: #E0E0E0;">Regular</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                            <span style="color: #E0E0E0;">Péssimo</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # --- ▲▲▲ FIM DO NOVO BLOCO ▲▲▲ ---

                # ===============================================
                # 🟢 GRÁFICO 2 - Eficiência Operacional
                # ===============================================
                with col_graf2:
                    opcoes_ranking_ocupacao = {
                        'Eficiência Operacional - Ocupação Média (KG)': 'OCUPACAO_KG_PERC',
                        'Ordem Alfabética': eixo_y_ordenacao
                    }
                    selecao_ranking_ocupacao = st.selectbox(
                        'Selecione a métrica para o ranking:',
                        options=list(opcoes_ranking_ocupacao.keys()),
                        key='ranking_ocupacao_selector'
                    )

                    ordenacao_ocupacao = alt.EncodingSortField(
                        field=opcoes_ranking_ocupacao[selecao_ranking_ocupacao],
                        op="min",
                        order='ascending' if selecao_ranking_ocupacao == 'Ordem Alfabética' else 'descending'
                    )

                    st.markdown("##### Eficiência Operacional")

                    barras_ocupacao = alt.Chart(df_grafico).mark_bar(cornerRadius=5).encode(
                        x=alt.X('OCUPACAO_KG_PERC:Q', title='Ocupação Média (KG)', 
                            axis=alt.Axis(format='.0f', titleFontSize=14, labelFontSize=12)),
                        
                        y=alt.Y('LABEL_EIXO_Y:N', title=None, sort=ordenacao_ocupacao,
                            axis=alt.Axis(labelFontSize=14, labelLimit=0)),
                        
                        color=alt.Color('OCUPACAO_KG_PERC:Q', scale=alt.Scale(scheme='greens'), legend=None),
                        
                        tooltip=[
                            alt.Tooltip(tooltip_label, title=titulo_tooltip),
                            alt.Tooltip('OCUPACAO_KG_PERC', title='Ocupação KG', format='.1f'),
                            alt.Tooltip('TOTAL_VIAGENS:Q', title='Total de Viagens') if 'TOTAL_VIAGENS' in df_grafico.columns else alt.Tooltip('PESO_VIAGEM', title='Peso Total', format=',.0f')
                        ]
                    )

                    texto_ocupacao = alt.Chart(df_grafico).mark_text(
                        align='left', baseline='middle', dx=5, fontSize=14, color='white'
                    ).transform_calculate(
                        label_text="format(datum.OCUPACAO_KG_PERC, '.0f') + '%'"
                    ).encode(
                        y=alt.Y('LABEL_EIXO_Y:N', sort=ordenacao_ocupacao),
                        x='OCUPACAO_KG_PERC:Q',
                        text='label_text:N'
                    )

                    chart_final_ocupacao = (barras_ocupacao + texto_ocupacao).properties(
                        height=alt.Step(40)
                    ).configure_view(stroke=None).configure_axis(grid=False)

                    st.altair_chart(chart_final_ocupacao, use_container_width=True)

                # ▼▼▼ INÍCIO DO NOVO BLOCO: TABELA DE RESUMO DAS VIAGENS NA ABA DE ROTAS ▼▼▼

                st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

                # --- Título dinâmico para a tabela ---
                if rota_selecionada_ocupacao == "(Todas as Rotas)":
                    st.subheader("📋 Resumo de Todas as Viagens no Período")
                else:
                    # Formata o nome da rota para ficar mais limpo no título
                    nome_rota_titulo = rota_selecionada_ocupacao.replace("ROTA ", "")
                    st.subheader(f"📋 Resumo das Viagens: {nome_rota_titulo}")

                # ▼▼▼ INÍCIO DO BLOCO DO MAPA DINÂMICO ▼▼▼
                # Condição 1: O filtro de período na sidebar deve ser "Dia Específico"
                # Condição 2: Uma rota específica (qualquer uma, exceto "Todas") deve ser selecionada nesta aba
                if periodo_tipo == "Dia Específico" and rota_selecionada_ocupacao != "(Todas as Rotas)":
                    
                    # Busca o nome da cidade correspondente à rota selecionada no dicionário que você adicionou
                    nome_cidade_destino = MAPA_ROTA_CIDADE.get(rota_selecionada_ocupacao)
                    
                    # Se encontrou uma cidade correspondente no dicionário...
                    if nome_cidade_destino:
                        st.markdown("#### 🗺️ Trajeto da Viagem")

                        # Busca as coordenadas da origem (fixa) e do destino (dinâmico)
                        coord_origem = get_coords("Campo Grande, MS")
                        coord_destino = get_coords(nome_cidade_destino)

                        # Se ambas as coordenadas foram encontradas com sucesso...
                        if coord_origem and coord_destino:
                            # Busca a rota entre os dois pontos
                            rota_desenhada = get_route(coord_origem, coord_destino)
                            
                            # Cria o mapa passando o nome da cidade de destino para o popup
                            mapa_viagem = criar_mapa_folium(coord_origem, coord_destino, nome_cidade_destino, rota_desenhada)
                            
                            # Exibe o mapa no Streamlit
                            if mapa_viagem:
                                st_folium(mapa_viagem, width=None, height=450, use_container_width=True)
                            else:
                                st.error("Não foi possível gerar o mapa da viagem.")
                        else:
                            st.warning(f"Coordenadas para '{nome_cidade_destino}' não encontradas. O mapa não pode ser exibido.")
                    else:
                        # Opcional: Informa ao usuário que a rota selecionada não tem um mapa configurado
                        st.info(f"A rota '{rota_selecionada_ocupacao}' não possui um trajeto de mapa pré-configurado.")
                # ▲▲▲ FIM DO BLOCO DO MAPA DINÂMICO ▲▲▲

                st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

                # O DataFrame 'df_para_ocupacao' já contém os dados filtrados pela rota selecionada
                df_viagens_tabela = df_para_ocupacao.copy()

                if not df_viagens_tabela.empty:
                    # 1. Agrupamento dos dados por viagem
                    if 'VIAGEM_ID' not in df_viagens_tabela.columns:
                        df_viagens_tabela['VIAGEM_ID'] = df_viagens_tabela.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup() + 1
                    
                    def obter_primeiro_valido(series):
                        for valor in series:
                            if pd.notna(valor) and str(valor).strip() != '' and str(valor).lower() != 'nan':
                                return valor
                        return None

                    resumo_viagens_tabela = df_viagens_tabela.groupby('VIAGEM_ID').agg(
                        EMISSÃO=('EMIS_MANIF', 'first'),
                        NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                        SITUACAO=('SITUACAO', 'first'),
                        MOTORISTA=('MOTORISTA', 'first'),
                        PLACA_CAVALO=('PLACA_CAVALO', 'first'),
                        PLACA_CARRETA=('PLACA_CARRETA', obter_primeiro_valido),
                        CAPAC_CAVALO=('CAPAC_CAVALO', 'first'),
                        CAP_CARRETA=('CAPACIDADE_KG', 'first'), 
                        TIPO_VEICULO=('TIPO_CAVALO', 'first'),
                        DESTINOS=('DEST_MANIF', lambda x: ordenar_destinos_geograficamente(x.unique(), ROTAS_COMPOSTAS, ORDEM_DAS_ROTAS)),
                        PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                        CUSTO_OS_TOTAL=('OS-R$', 'max'),
                        CUSTO_CTRB_TOTAL=('CTRB-R$', 'max'),
                        FRETE_TOTAL=('FRETE-R$', 'sum'),
                        ICMS=('ICMS-R$', 'sum'),
                        PESO_KG=('PESO REAL (KG)', 'sum'),
                        M3=('M3', 'sum'),
                        VOLUMES=('VOLUMES', 'sum'),
                        VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                        ENTREGAS=('DEST_MANIF', 'nunique'),
                        QTDE_CTRC=('QTDE_CTRC', 'sum')
                    ).reset_index()

                    resumo_viagens_tabela.rename(columns={
                        'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 'TIPO_VEICULO': 'TIPO_CAVALO', 'DESTINOS': 'DEST_MANIF',
                        'PROPRIETARIO': 'PROPRIETARIO_CAVALO', 'CUSTO_OS_TOTAL': 'OS-R$', 'CUSTO_CTRB_TOTAL': 'CTRB-R$',
                        'FRETE_TOTAL': 'FRETE-R$', 'ICMS': 'ICMS-R$', 'PESO_KG': 'PESO REAL (KG)',
                        'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
                    }, inplace=True)

                    # ✅ Ajusta VIAGEM para começar em 1 (como coluna, não índice)
                    resumo_viagens_tabela['VIAGEM'] = range(1, len(resumo_viagens_tabela) + 1)


                    # 2. Funções de cálculo e formatação
                    def obter_capacidade_real_viagem(row):
                        capacidade_carreta = row.get('CAP_CARRETA', 0)
                        return capacidade_carreta if pd.notna(capacidade_carreta) and capacidade_carreta > 0 else row.get('CAPAC_CAVALO', 0)
                    
                    def obter_placa_veiculo_formatada(row):
                        placa_cavalo, placa_carreta = row.get('PLACA_CAVALO', 'N/A'), row.get('PLACA_CARRETA', 'N/A')
                        return f"{placa_cavalo} / {placa_carreta}" if pd.notna(placa_carreta) and placa_carreta != 'nan' and placa_carreta != placa_cavalo else placa_cavalo

                    resumo_viagens_tabela['Capacidade (KG)'] = resumo_viagens_tabela.apply(obter_capacidade_real_viagem, axis=1)
                    resumo_viagens_tabela['Veículo (Placa)'] = resumo_viagens_tabela.apply(obter_placa_veiculo_formatada, axis=1)

                    def calcular_custo_final(row):
                        custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                        return custo_base / 2 if any(dest in str(row.get('DEST_MANIF', '')).upper() for dest in ['GYN', 'SPO']) else custo_base

                    def calcular_distancia_viagem(row):
                        tipo_veiculo = str(row.get('TIPO_CAVALO', 'PADRAO')).upper()
                        valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                        custo_viagem = row['Custo (CTRB/OS)']
                        return custo_viagem / valor_km if valor_km > 0 and custo_viagem > 0 else 0.0

                    resumo_viagens_tabela['Custo (CTRB/OS)'] = resumo_viagens_tabela.apply(calcular_custo_final, axis=1)
                    resumo_viagens_tabela['DISTANCIA'] = resumo_viagens_tabela.apply(calcular_distancia_viagem, axis=1)
                    resumo_viagens_tabela['CTRB/Frete (%)_valor'] = (resumo_viagens_tabela['Custo (CTRB/OS)'] / resumo_viagens_tabela['FRETE-R$'] * 100).fillna(0)
                    resumo_viagens_tabela['CTRB/Frete (%)'] = resumo_viagens_tabela['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.0f}%")

                    # 3. Formatação para exibição
                    resumo_viagens_tabela['EMIS_MANIF'] = pd.to_datetime(resumo_viagens_tabela['EMIS_MANIF']).dt.strftime('%d/%m/%Y')
                    for col_moeda in ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']:
                        resumo_viagens_tabela[col_moeda] = resumo_viagens_tabela[col_moeda].astype(float).apply(formatar_moeda)
                    resumo_viagens_tabela['PESO REAL (KG)'] = resumo_viagens_tabela['PESO REAL (KG)'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg')
                    resumo_viagens_tabela['M3'] = resumo_viagens_tabela['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))
                    resumo_viagens_tabela['Capacidade (KG)'] = resumo_viagens_tabela['Capacidade (KG)'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg')
                    resumo_viagens_tabela['DISTANCIA'] = resumo_viagens_tabela['DISTANCIA'].astype(float).apply(lambda x: f"{int(x):,} km".replace(",", "."))
                    resumo_viagens_tabela['VOLUMES'] = resumo_viagens_tabela['VOLUMES'].astype(int)


                    resumo_viagens_tabela.rename(columns={
                        'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'TIPO_CAVALO': 'TIPO', 'DEST_MANIF': 'DESTINOS',
                        'QTDE_CTRC': 'Qtd. CTRCs', 'SITUACAO': 'SITUAÇÃO'
                    }, inplace=True)

                    # 4. Definição da ordem final e exibição
                    ordem_final_tabela = [
                        'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUAÇÃO', 'MOTORISTA', 'CTRB/Frete (%)', 'DESTINOS',
                        'DISTANCIA', 'ENTREGAS', 'TIPO', 'Veículo (Placa)', 'PESO REAL (KG)', 'Capacidade (KG)',
                        'M3', 'Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
                    ]
                    colunas_para_exibir_tabela = [col for col in ordem_final_tabela if col in resumo_viagens_tabela.columns]
                    df_para_exibir_tabela = resumo_viagens_tabela[colunas_para_exibir_tabela].sort_values(by='VIAGEM', ascending=True)

                    def colorir_celula_ctrb(valor_texto):
                        try:
                            v = float(valor_texto.strip('%'))
                            if 0 <= v <= 25: return 'background-color: #2E7D32; color: white;'
                            elif 26 <= v <= 45: return 'background-color: #FF8F00; color: white;'
                            elif v >= 46: return 'background-color: #C62828; color: white;'
                        except (ValueError, TypeError): pass
                        return ''

                    styled_df_tabela = df_para_exibir_tabela.style.applymap(colorir_celula_ctrb, subset=['CTRB/Frete (%)'])
                    
                    st.dataframe(styled_df_tabela, use_container_width=True, hide_index=True)

                    # 5. Legenda e botão de download
                    st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 20px; font-size: 14px;">
                        <b style="color: #E0E0E0;">Legenda de Desempenho:</b>
                        <div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px;"></div><span style="color: #E0E0E0;">Bom</span></div>
                        <div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px;"></div><span style="color: #E0E0E0;">Regular</span></div>
                        <div style="display: flex; align-items: center; gap: 8px;"><div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px;"></div><span style="color: #E0E0E0;">Péssimo</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("")

                    try:
                        excel_bytes_tabela = to_excel(df_para_exibir_tabela)
                        st.download_button(
                            label="📥 Download Resumo da Rota (Excel)",
                            data=excel_bytes_tabela,
                            file_name=f"resumo_rota_{rota_selecionada_ocupacao.replace(' / ', '_')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_resumo_rota_tab5"
                        )
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar o arquivo Excel para o resumo da rota: {e}")

            # --- ▲▲▲ FIM DO BLOCO DE GRÁFICOS DE BARRAS ---

        else:
            st.info(f"Não há viagens do tipo '{tipo_viagem_ocupacao_sel}' para analisar no período selecionado.")

# ==================================================================
# ABA 6: ANÁLISE TEMPORAL DE ROTAS
# ==================================================================
with tab6:
    # Título estilizado para a nova aba
    st.markdown("""
        <div class="title-block-temporal">
            <i class="fa-solid fa-chart-simple"></i>
            <h2>Painel de Performance por Rota</h2>
        </div>
    """, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # --- 1. PREPARAÇÃO AVANÇADA DOS DADOS ---
        df_temporal = df_filtrado.copy()
        
        # Garante que a data de emissão e o dia da semana existem
        df_temporal['EMISSAO_DATE'] = pd.to_datetime(df_temporal['EMIS_MANIF']).dt.date
        df_temporal['DIA_SEMANA_NUM'] = pd.to_datetime(df_temporal['EMIS_MANIF']).dt.dayofweek
        dias_semana_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        df_temporal['DIA_SEMANA'] = df_temporal['DIA_SEMANA_NUM'].map(dias_semana_map)

        # Identifica cada viagem única
        df_temporal['VIAGEM_ID'] = df_temporal.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

        # Agrega os dados por VIAGEM para cálculos corretos
        resumo_viagens_temporal = df_temporal.groupby('VIAGEM_ID').agg(
            FRETE_VIAGEM=('FRETE-R$', 'sum'),
            CUSTO_OS=('OS-R$', 'max'),
            CUSTO_CTRB=('CTRB-R$', 'max'),
            ICMS_VIAGEM=('ICMS-R$', 'sum'),
            PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
            DESTINOS=('DEST_MANIF', 'unique'),
            PESO_VIAGEM=('PESO REAL (KG)', 'sum'),
            TIPO_VEICULO=('TIPO_CAVALO', 'first'),
            CAPACIDADE_CARRETA=('CAPACIDADE_KG', 'first'),
            CAPACIDADE_CAVALO=('CAPAC_CAVALO', 'first'),
            DIA_SEMANA=('DIA_SEMANA', 'first'),
            DIA_SEMANA_NUM=('DIA_SEMANA_NUM', 'first')
        ).reset_index()

        # Calcula métricas de performance por VIAGEM
        def get_capacidade_viagem(row):
            return row['CAPACIDADE_CARRETA'] if row['TIPO_VEICULO'] == 'CAVALO' else row['CAPACIDADE_CAVALO']
        
        def calcular_custo_viagem(row):
            custo = row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']
            return custo / 2 if any(d in str(row['DESTINOS']) for d in ['GYN', 'SPO']) else custo

        resumo_viagens_temporal['CAPACIDADE_VIAGEM'] = resumo_viagens_temporal.apply(get_capacidade_viagem, axis=1)
        resumo_viagens_temporal['CUSTO_VIAGEM'] = resumo_viagens_temporal.apply(calcular_custo_viagem, axis=1)
        resumo_viagens_temporal['LUCRO_VIAGEM'] = resumo_viagens_temporal['FRETE_VIAGEM'] - (resumo_viagens_temporal['CUSTO_VIAGEM'] + resumo_viagens_temporal['ICMS_VIAGEM'])
        resumo_viagens_temporal['OCUPACAO_PERC'] = (resumo_viagens_temporal['PESO_VIAGEM'] / resumo_viagens_temporal['CAPACIDADE_VIAGEM'] * 100).fillna(0)
        resumo_viagens_temporal['CUSTO_FRETE_PERC'] = (resumo_viagens_temporal['CUSTO_VIAGEM'] / resumo_viagens_temporal['FRETE_VIAGEM'] * 100).fillna(0)
        resumo_viagens_temporal['NOME_ROTA'] = resumo_viagens_temporal['DESTINOS'].apply(obter_nome_rota_padronizado)

        # --- 2. CRIAÇÃO DAS ABAS INTERNAS (IDEIA 1) ---
        aba_totais, aba_medias, aba_ranking = st.tabs(["📈 Totais por Dia", "📊 Médias & Performance", "🏁 Ranking de Rotas"])

        # --- ABA 1: TOTAIS POR DIA ---
        with aba_totais:
            st.markdown("#### Análise de Volume Total por Dia da Semana")
            
            # Agrupa os dados por dia da semana para os totais
            totais_dia_semana = resumo_viagens_temporal.groupby(['DIA_SEMANA_NUM', 'DIA_SEMANA']).agg(
                TOTAL_VIAGENS=('VIAGEM_ID', 'nunique'),
                FRETE_TOTAL=('FRETE_VIAGEM', 'sum'),
                CUSTO_TOTAL=('CUSTO_VIAGEM', 'sum'),
                LUCRO_TOTAL=('LUCRO_VIAGEM', 'sum')
            ).reset_index().sort_values('DIA_SEMANA_NUM')

            # Gráfico de totais
            base_totais = alt.Chart(totais_dia_semana).encode(x=alt.X('DIA_SEMANA:N', sort=None, title="Dia da Semana"))

            barras_frete = base_totais.mark_bar(opacity=0.8, color="#22c55e").encode(
                y=alt.Y('FRETE_TOTAL:Q', title='Valor Total (R$)'),
                tooltip=[alt.Tooltip('DIA_SEMANA', title='Dia'), alt.Tooltip('FRETE_TOTAL', title='Frete Total', format='$,.2f')]
            )
            
            linha_lucro = base_totais.mark_line(point=True, color="#3b82f6", strokeWidth=3).encode(
                y=alt.Y('LUCRO_TOTAL:Q', title='Lucro Total (R$)'),
                tooltip=[alt.Tooltip('LUCRO_TOTAL', title='Lucro Total', format='$,.2f')]
            )

            chart_totais = alt.layer(barras_frete, linha_lucro).resolve_scale(y='independent').properties(
                title="Frete Total (Barras) vs. Lucro Total (Linha) por Dia da Semana",
                height=400
            ).configure_axis(labelFontSize=12, titleFontSize=14).configure_title(fontSize=16)
            
            st.altair_chart(chart_totais, use_container_width=True)

        # --- ABA 2: MÉDIAS & PERFORMANCE (COM GRÁFICO HÍBRIDO - IDEIA 2 e 4) ---
        with aba_medias:
            st.markdown("#### Performance Média das Rotas")
            
            metrica_selecionada = st.radio(
                "Selecione a métrica principal para análise:",
                options=['Custo/Frete (%)', 'Ocupação Média (KG)', 'Lucro Médio (R$)'],
                horizontal=True,
                key="metrica_media_selector"
            )

            medias_por_rota = resumo_viagens_temporal.groupby('NOME_ROTA').agg(
                CUSTO_FRETE_MEDIO=('CUSTO_FRETE_PERC', 'mean'),
                OCUPACAO_MEDIA=('OCUPACAO_PERC', 'mean'),
                LUCRO_MEDIO=('LUCRO_VIAGEM', 'mean'),
                TOTAL_VIAGENS=('VIAGEM_ID', 'nunique')
            ).reset_index()

            if metrica_selecionada == 'Custo/Frete (%)':
                col_barra, col_linha, titulo_barra = 'CUSTO_FRETE_MEDIO', 'OCUPACAO_MEDIA', 'Custo/Frete Médio (%)'
                color_scale = alt.Scale(scheme='redyellowgreen', reverse=True)
            elif metrica_selecionada == 'Ocupação Média (KG)':
                col_barra, col_linha, titulo_barra = 'OCUPACAO_MEDIA', 'CUSTO_FRETE_MEDIO', 'Ocupação Média (%)'
                color_scale = alt.Scale(scheme='redyellowgreen', reverse=False)
            else: # Lucro Médio
                col_barra, col_linha, titulo_barra = 'LUCRO_MEDIO', 'OCUPACAO_MEDIA', 'Lucro Médio por Viagem (R$)'
                color_scale = alt.Scale(scheme='redyellowgreen', reverse=False)

            # =============================================================
            # ▼▼▼ LINHA CORRIGIDA/ADICIONADA AQUI ▼▼▼
            # Define o gráfico base ANTES de usá-lo
            base_medias = alt.Chart(medias_por_rota).encode(
                x=alt.X('NOME_ROTA:N', sort='-y', title=None, axis=alt.Axis(labelAngle=-45))
            )
            # ▲▲▲ FIM DA CORREÇÃO ▲▲▲
            # =============================================================

            # Barras verticais com gradiente de cor
            barras_medias = base_medias.mark_bar().encode(
                y=alt.Y(f'{col_barra}:Q', title=titulo_barra),
                color=alt.Color(f'{col_barra}:Q',
                                scale=color_scale,
                                legend=None),
                tooltip=[
                    alt.Tooltip('NOME_ROTA', title='Rota'),
                    alt.Tooltip('CUSTO_FRETE_MEDIO', title='Custo/Frete Médio', format='.1f'),
                    alt.Tooltip('OCUPACAO_MEDIA', title='Ocupação Média', format='.1f'),
                    alt.Tooltip('LUCRO_MEDIO', title='Lucro Médio', format='$,.2f'),
                    alt.Tooltip('TOTAL_VIAGENS', title='Nº de Viagens')
                ]
            )

            # Linha sobreposta
            linha_medias = base_medias.mark_line(point=alt.OverlayMarkDef(color="#FFFFFF", size=60), color="#FFFFFF", strokeWidth=2).encode(
                y=alt.Y(f'{col_linha}:Q', title=f"{col_linha.replace('_', ' ').title()} (%)")
            )
            
            chart_hibrido = alt.layer(barras_medias, linha_medias).resolve_scale(y='independent').properties(
                title=f"Análise Híbrida: {titulo_barra} (Barras) vs. {col_linha.replace('_', ' ').title()} (Linha)",
                height=450
            )
            
            st.altair_chart(chart_hibrido, use_container_width=True)

            # ... (resto do código com o scatter plot) ...


            # --- SEÇÃO DE CORRELAÇÃO (IDEIA 6) ---
            st.markdown("---")
            st.markdown("#### Análise de Correlação: Eficiência vs. Rentabilidade")
            
            scatter_plot = alt.Chart(medias_por_rota).mark_circle(size=100, opacity=0.8).encode(
                x=alt.X('OCUPACAO_MEDIA:Q', title='Eficiência de Ocupação (%)', scale=alt.Scale(zero=False)),
                y=alt.Y('CUSTO_FRETE_MEDIO:Q', title='Performance de Custo/Frete (%)', scale=alt.Scale(zero=False)),
                color=alt.Color('LUCRO_MEDIO:Q', scale=alt.Scale(scheme='viridis'), title='Lucro Médio (R$)'),
                size=alt.Size('TOTAL_VIAGENS:Q', title='Nº de Viagens'),
                tooltip=[
                    alt.Tooltip('NOME_ROTA', title='Rota'),
                    alt.Tooltip('OCUPACAO_MEDIA', title='Ocupação Média', format='.1f'),
                    alt.Tooltip('CUSTO_FRETE_MEDIO', title='Custo/Frete Médio', format='.1f'),
                    alt.Tooltip('LUCRO_MEDIO', title='Lucro Médio', format='$,.2f')
                ]
            ).properties(
                title="Correlação entre Ocupação, Custo/Frete e Lucro",
                height=400
            ).interactive()

            st.altair_chart(scatter_plot, use_container_width=True)

        # --- ABA 3: RANKING & DESTAQUES (CORREÇÃO FINAL E DEFINITIVA) ---
with aba_ranking:
    st.markdown("#### Destaques de Performance das Rotas no Período")

    # Garante que há dados para processar
    if not df_filtrado.empty:
        # 1. REPROCESSA os dados a partir do df_filtrado (original da sidebar)
        #    para garantir que TODAS as viagens (completas e extras) sejam incluídas.
        df_ranking_base = df_filtrado.copy()
        df_ranking_base['VIAGEM_ID'] = df_ranking_base.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

        # 2. Agrega por viagem para obter os valores corretos
        resumo_viagens_ranking = df_ranking_base.groupby('VIAGEM_ID').agg(
            FRETE_VIAGEM=('FRETE-R$', 'sum'),
            CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
            ICMS_VIAGEM=('ICMS-R$', 'sum'), PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
            DESTINOS=('DEST_MANIF', 'unique'), PESO_VIAGEM=('PESO REAL (KG)', 'sum'),
            TIPO_VEICULO=('TIPO_CAVALO', 'first'),
            # Captura as capacidades de forma separada para a lógica correta
            CAPACIDADE_CARRETA=('CAPACIDADE_KG', 'first'),
            CAPACIDADE_CAVALO=('CAPAC_CAVALO', 'first')
        ).reset_index()

        # 3. Aplica as mesmas funções de cálculo robustas usadas na Aba 5
        def get_capacidade_correta_viagem(row):
            # Se for um CAVALO, a capacidade é a da CARRETA. Senão, é a do próprio veículo (TRUCK/TOCO).
            if row['TIPO_VEICULO'] == 'CAVALO':
                return row['CAPACIDADE_CARRETA']
            return row['CAPACIDADE_CAVALO']

        def calcular_custo_correto_viagem(row):
            custo = row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']
            # Regra de divisão para rotas longas
            return custo / 2 if any(d in str(row['DESTINOS']) for d in ['GYN', 'SPO']) else custo

        resumo_viagens_ranking['CAPACIDADE_VIAGEM'] = resumo_viagens_ranking.apply(get_capacidade_correta_viagem, axis=1)
        resumo_viagens_ranking['CUSTO_VIAGEM'] = resumo_viagens_ranking.apply(calcular_custo_correto_viagem, axis=1)
        resumo_viagens_ranking['LUCRO_VIAGEM'] = resumo_viagens_ranking['FRETE_VIAGEM'] - (resumo_viagens_ranking['CUSTO_VIAGEM'] + resumo_viagens_ranking['ICMS_VIAGEM'])
        resumo_viagens_ranking['CUSTO_FRETE_PERC'] = (resumo_viagens_ranking['CUSTO_VIAGEM'] / resumo_viagens_ranking['FRETE_VIAGEM'] * 100).fillna(0)
        resumo_viagens_ranking['NOME_ROTA'] = resumo_viagens_ranking['DESTINOS'].apply(obter_nome_rota_padronizado)

        # 4. Agrupa por ROTA para obter os valores finais para os destaques e ranking
        dados_agregados_rota = resumo_viagens_ranking.groupby('NOME_ROTA').agg(
            CUSTO_FRETE_MEDIO=('CUSTO_FRETE_PERC', 'mean'),
            LUCRO_MEDIO=('LUCRO_VIAGEM', 'mean'),
            TOTAL_VIAGENS=('VIAGEM_ID', 'nunique'),
            # A OCUPAÇÃO CORRETA: SOMA DOS PESOS / SOMA DAS CAPACIDADES
            PESO_TOTAL_ROTA=('PESO_VIAGEM', 'sum'),
            CAPACIDADE_TOTAL_ROTA=('CAPACIDADE_VIAGEM', 'sum')
        ).reset_index()

        # Calcula a ocupação média da forma correta
        dados_agregados_rota['OCUPACAO_MEDIA'] = (
            dados_agregados_rota['PESO_TOTAL_ROTA'] / dados_agregados_rota['CAPACIDADE_TOTAL_ROTA'] * 100
        ).fillna(0)

        # O restante do código para exibir os cards e a tabela permanece o mesmo
        if not dados_agregados_rota.empty:
            # ... (código dos 4 cards de destaque, sem alterações) ...
            rota_destaque = dados_agregados_rota.loc[dados_agregados_rota['CUSTO_FRETE_MEDIO'].idxmin()]
            rota_baixa_eficiencia = dados_agregados_rota.loc[dados_agregados_rota['OCUPACAO_MEDIA'].idxmin()]
            rota_mais_rentavel = dados_agregados_rota.loc[dados_agregados_rota['LUCRO_MEDIO'].idxmax()]
            ponto_atencao = dados_agregados_rota[
                (dados_agregados_rota['CUSTO_FRETE_MEDIO'] > dados_agregados_rota['CUSTO_FRETE_MEDIO'].quantile(0.75)) &
                (dados_agregados_rota['OCUPACAO_MEDIA'] < dados_agregados_rota['OCUPACAO_MEDIA'].quantile(0.25))
            ]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: left; border-left: 5px solid #22c55e;'>
                        <div class='kpi-title'>🥇 Rota Destaque (Custo/Frete %)</div>
                        <div class='kpi-value' style='color: #22c55e;'>{rota_destaque['NOME_ROTA']}</div>
                        <p style='color: #d1d5db; font-size: 1rem;'>{rota_destaque['CUSTO_FRETE_MEDIO']:.0f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: left; border-left: 5px solid #f59e0b;'>
                        <div class='kpi-title'>🐢 Rota com Menor Eficiência</div>
                        <div class='kpi-value' style='color: #f59e0b;'>{rota_baixa_eficiencia['NOME_ROTA']}</div>
                        <p style='color: #d1d5db; font-size: 1rem;'>{rota_baixa_eficiencia['OCUPACAO_MEDIA']:.0f}% Ocupação</p>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: left; border-left: 5px solid #3b82f6;'>
                        <div class='kpi-title'>💰 Rota Mais Rentável</div>
                        <div class='kpi-value' style='color: #3b82f6;'>{rota_mais_rentavel['NOME_ROTA']}</div>
                        <p style='color: #d1d5db; font-size: 1rem;'>R$ {rota_mais_rentavel['LUCRO_MEDIO']:,.2f} / viagem</p>
                    </div>
                """, unsafe_allow_html=True)

            with col4:
                nome_atencao = ponto_atencao['NOME_ROTA'].iloc[0] if not ponto_atencao.empty else "N/A"
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: left; border-left: 5px solid #ef4444;'>
                        <div class='kpi-title'>⚙️ Ponto de Atenção</div>
                        <div class='kpi-value' style='color: #ef4444;'>{nome_atencao}</div>
                        <p style='color: #d1d5db; font-size: 1rem;'>Alto Custo & Baixa Ocupação</p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Ranking Completo das Rotas")

        df_ranking = dados_agregados_rota.sort_values('LUCRO_MEDIO', ascending=False).reset_index(drop=True)
        df_ranking.index += 1

        df_ranking['CUSTO_FRETE_MEDIO'] = df_ranking['CUSTO_FRETE_MEDIO'].apply(lambda x: f"{x:.1f}%")
        df_ranking['OCUPACAO_MEDIA'] = df_ranking['OCUPACAO_MEDIA'].apply(lambda x: f"{x:.1f}%")
        df_ranking['LUCRO_MEDIO'] = df_ranking['LUCRO_MEDIO'].apply(lambda x: f"R$ {x:,.2f}")
        df_ranking.rename(columns={'TOTAL_VIAGENS': 'Nº de Viagens'}, inplace=True)

        st.dataframe(df_ranking[['NOME_ROTA', 'LUCRO_MEDIO', 'CUSTO_FRETE_MEDIO', 'OCUPACAO_MEDIA', 'Nº de Viagens']], use_container_width=True)

    else:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
