import streamlit as st
import pandas as pd
import gspread
from datetime import date

# Configuração da página
st.set_page_config(
    page_title="Mrs. Candy por Letícia Lucas", 
    page_icon="🍬", 
    layout="centered"
)

# Estilo CSS bege/creme claro
st.markdown("""
    <style>
    .stApp {
        background-color: #EADAB9 !important;
        color: #2A1B12 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #DFCDA8 !important;
        border-right: 2px solid #C5A86D !important;
    }
    section[data-testid="stSidebar"] * {
        color: #2A1B12 !important;
        font-weight: 600 !important;
    }
    label, p, span, div, h1, h2, h3, h4 {
        color: #2A1B12 !important;
        font-weight: 600;
    }
    div[data-baseweb="select"] > div, input, select {
        background-color: #F8F3E6 !important;
        color: #2A1B12 !important;
        border: 2px solid #C5A86D !important;
        border-radius: 8px !important;
    }
    ul[data-baseweb="menu"], ul[data-baseweb="menu"] * {
        background-color: #F8F3E6 !important;
        color: #2A1B12 !important;
    }
    li[aria-selected="true"], li:hover {
        background-color: #EADAB9 !important;
    }
    .brand-title {
        color: #2A1B12 !important;
        text-align: center;
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .brand-subtitle {
        color: #5C4328 !important;
        text-align: center;
        font-size: 13px;
        letter-spacing: 2px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #F8F3E6;
        border: 2px solid #C5A86D;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        text-align: center;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    }
    .metric-title {
        color: #5C4328 !important;
        font-size: 14px;
        font-weight: bold;
    }
    .metric-value {
        color: #2A1B12 !important;
        font-size: 26px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Conexão gspread usando os Secrets do Streamlit
SHEET_ID = "1lfxzdhzGCWuzWzJ2BU72bL6CmwLRxfK_dI2zvjFDEXE"

@st.cache_resource
def get_gspread_client():
    creds = dict(st.secrets["gcp_service_account"])
    return gspread.service_account_from_dict(creds)

def get_worksheet(sheet_name):
    client = get_gspread_client()
    sh = client.open_by_key(SHEET_ID)
    try:
        return sh.worksheet(sheet_name)
    except Exception:
        return sh.add_worksheet(title=sheet_name, rows="100", cols="20")

# Carregar dados diretamente do Google Sheets
def load_vendas():
    try:
        ws = get_worksheet("Vendas")
        data = ws.get_all_records()
        return data
    except Exception:
        return []

def load_cardapio():
    try:
        ws = get_worksheet("Cardapio")
        data = ws.get_all_records()
        if data:
            return {row["Doce"]: float(str(row["Preco"]).replace(",", ".")) for row in data if "Doce" in row and "Preco" in row}
    except Exception:
        pass
    return {
        "Bolo de pote": 9.00,
        "Brownie": 8.50,
        "Cone": 8.00,
        "Empadão": 12.00,
        "Morango cravejado": 15.00,
        "Pão de mel": 8.00,
        "Tortinha": 10.00,
        "Tortinha morango": 12.00
    }

def load_clientes():
    try:
        ws = get_worksheet("Clientes")
        records = ws.get_all_records()
        if records:
            return [str(r["Cliente"]).strip() for r in records if "Cliente" in r and r["Cliente"]]
    except Exception:
        pass
    return ["Luanna", "Carlos", "Cliente Avulso"]

MESES_PADRAO = [
    "Todos",
    "10/2026", "11/2026", "12/2026",
    "01/2027", "02/2027", "03/2027", "04/2027", "05/2027", "06/2027",
    "07/2027", "08/2027", "09/2027", "10/2027", "11/2027", "12/2027"
]

if "lista_meses" not in st.session_state:
    st.session_state.lista_meses = MESES_PADRAO

if "vendas" not in st.session_state:
    st.session_state.vendas = load_vendas()

if "cardapio" not in st.session_state:
    st.session_state.cardapio = load_cardapio()

if "clientes" not in st.session_state:
    st.session_state.clientes = load_clientes()

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Cabeçalho da Marca
st.markdown('<div class="brand-title">Mrs. Candy</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">POR LETÍCIA LUCAS</div>', unsafe_allow_html=True)

# Menu Lateral
st.sidebar.title("📌 Menu")
if st.sidebar.button("🔄 Sincronizar / Recarregar"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.vendas = load_vendas()
    st.session_state.cardapio = load_cardapio()
    st.session_state.clientes = load_clientes()
    st.success("Dados sincronizados com a planilha!")
    st.rerun()

pagina = st.sidebar.radio("Navegar", [
    "📊 Visão Geral", 
    "➕ Registrar Venda", 
    "💰 Cobranças (Fiado)", 
    "📈 Resultado Mensal",
    "📅 Resultado Anual",
    "🍬 Gerenciar Cardápio", 
    "👥 Clientes",
    "⚙️ Gerenciar Datas"
])

# 1. VISÃO GERAL
if pagina == "📊 Visão Geral":
    st.subheader("📊 Controle Geral de Vendas")
    
    mes_selecionado = st.selectbox("📅 Selecione o Mês para Filtrar", st.session_state.lista_meses)
    
    if len(st.session_state.vendas) > 0:
        df_v = pd.DataFrame(st.session_state.vendas)
        if "Data" in df_v.columns:
            df_v["Data_DT"] = pd.to_datetime(df_v["Data"], format="%d/%m/%Y", errors="coerce")
            df_v["Ano_Mes"] = df_v["Data_DT"].dt.strftime("%m/%Y")
            
            if mes_selecionado != "Todos":
                df_filtrado = df_v[df_v["Ano_Mes"] == mes_selecionado]
            else:
                df_filtrado = df_v
                
            tot_vendas = df_filtrado["Total"].sum() if not df_filtrado.empty and "Total" in df_filtrado else 0.0
            tot_recebido = df_filtrado["Pago"].sum() if not df_filtrado.empty and "Pago" in df_filtrado else 0.0
            tot_pendente = df_filtrado["Pendente"].sum() if not df_filtrado.empty and "Pendente" in df_filtrado else 0.0
        else:
            df_filtrado = pd.DataFrame()
            tot_vendas = tot_recebido = tot_pendente = 0.0
    else:
        df_filtrado = pd.DataFrame()
        tot_vendas = tot_recebido = tot_pendente = 0.0

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total de Vendas ({mes_selecionado})</div>
            <div class="metric-value">R$ {tot_vendas:,.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Valor Já Recebido</div>
            <div class="metric-value" style="color:#1B5E20 !important;">R$ {tot_recebido:,.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Saldo Pendente (Fiado)</div>
            <div class="metric-value" style="color:#B71C1C !important;">R$ {tot_pendente:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Histórico de Vendas")
    if not df_filtrado.empty:
        colunas_exibir = [c for c in ["ID", "Data", "Cliente", "Doces", "Total", "Pago", "Pendente", "Status"] if c in df_filtrado.columns]
        st.dataframe(df_filtrado[colunas_exibir], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada no período selecionado.")

# 2. REGISTRAR VENDA (Com campo de digitação/pesquisa de cliente)
elif pagina == "➕ Registrar Venda":
    st.subheader("🛍️ Registrar Nova Venda")
    
    c_cli, c_dat = st.columns([2, 1])
    with c_cli:
        cliente_sel = st.selectbox(
            "Selecione ou Digite o Nome do Cliente", 
            st.session_state.clientes,
            index=0 if st.session_state.clientes else None
        )
    with c_dat:
        data_venda = st.date_input("Data", date.today())

    st.markdown("---")
    st.markdown("### Adicionar Doce ao Pedido")
    
    c_doc, c_qtd = st.columns([3, 1])
    with c_doc:
        doces_lista = list(st.session_state.cardapio.keys())
        if len(doces_lista) > 0:
            doce_sel = st.selectbox("Doce", doces_lista)
        else:
            st.warning("Cadastre doces no Cardápio primeiro.")
            doce_sel = None
            
    with c_qtd:
        qtd_input = st.number_input("Qtd.", min_value=1, value=1)

    if doce_sel and st.button("➕ Adicionar Doce ao Pedido", use_container_width=True):
        preco = st.session_state.cardapio[doce_sel]
        st.session_state.carrinho.append({
            "Doce": doce_sel,
            "Qtd": qtd_input,
            "Preço Un.": preco,
            "Subtotal": preco * qtd_input
        })
        st.rerun()

    if len(st.session_state.carrinho) > 0:
        st.markdown("---")
        st.markdown("### 🛒 Itens Selecionados:")
        
        for idx, item in enumerate(st.session_state.carrinho):
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
            col1.write(f"**{item['Doce']}**")
            col2.write(f"x{item['Qtd']}")
            col3.write(f"R$ {item['Subtotal']:.2f}")
            if col4.button("🗑️", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()

        total_pedido = sum(item["Subtotal"] for item in st.session_state.carrinho)
        st.markdown(f"### **Total do Pedido: R$ {total_pedido:.2f}**")

        st.markdown("---")
        v_pago = st.number_input("Valor Recebido (R$)", min_value=0.0, value=float(total_pedido), step=0.50)
        v_pendente = max(0.0, total_pedido - v_pago)

        if v_pendente > 0:
            st.warning(f"⚠️ Saldo que ficará pendente: R$ {v_pendente:.2f}")

        if st.button("✅ Confirmar e Salvar Venda", type="primary", use_container_width=True):
            itens_str = ", ".join([f"{i['Qtd']}x {i['Doce']}" for i in st.session_state.carrinho])
            
            nova_venda = {
                "ID": len(st.session_state.vendas) + 1,
                "Data": data_venda.strftime("%d/%m/%Y"),
                "Cliente": cliente_sel,
                "Doces": itens_str,
                "Total": float(total_pedido),
                "Pago": float(v_pago),
                "Pendente": float(v_pendente),
                "Status": "Pago" if v_pendente == 0 else "Pendente"
            }
            
            # Salvar no Google Sheets em tempo real
            try:
                ws = get_worksheet("Vendas")
                if len(ws.get_all_values()) == 0:
                    ws.append_row(["ID", "Data", "Cliente", "Doces", "Total", "Pago", "Pendente", "Status"])
                ws.append_row(list(nova_venda.values()))
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")

            st.session_state.vendas.append(nova_venda)
            st.session_state.carrinho = []
            st.success("Venda gravada com sucesso na planilha e sincronizada!")
            st.rerun()

# 3. COBRANÇAS / FIADO
elif pagina == "💰 Cobranças (Fiado)":
    st.subheader("💰 Clientes com Fiado Pendente")
    
    pendentes = [v for v in st.session_state.vendas if float(v.get("Pendente", 0)) > 0]
    
    if len(pendentes) == 0:
        st.success("🎉 Nenhum valor pendente de cobrança!")
    else:
        for v in pendentes:
            with st.container():
                st.markdown(f"""
                    <div style="background-color:#F8F3E6; padding:15px; border-radius:8px; border:1px solid #C5A86D; border-left:5px solid #B71C1C; margin-bottom:12px;">
                        <h4 style="margin:0; color:#2A1B12;">👤 {v.get('Cliente', '')}</h4>
                        <p style="margin:4px 0; color:#333;"><b>Data:</b> {v.get('Data', '')} | <b>Itens:</b> {v.get('Doces', '')}</p>
                        <p style="margin:0; color:#333;"><b>Total do Pedido:</b> R$ {float(v.get('Total', 0)):.2f} | <b>Pago:</b> R$ {float(v.get('Pago', 0)):.2f}</p>
                        <h3 style="margin:5px 0; color:#B71C1C !important;">Falta Pagar: R$ {float(v.get('Pendente', 0)):.2f}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                c_baixa1, c_baixa2 = st.columns(2)
                with c_baixa1:
                    if st.button(f"✅ Quitar Tudo", key=f"pago_{v.get('ID')}"):
                        v["Pago"] = float(v.get("Total", 0))
                        v["Pendente"] = 0.0
                        v["Status"] = "Pago"
                        
                        # Atualizar planilha
                        try:
                            ws = get_worksheet("Vendas")
                            records = ws.get_all_records()
                            for idx, row in enumerate(records, start=2):
                                if str(row.get("ID")) == str(v.get("ID")):
                                    ws.update_cell(idx, 6, v["Pago"])
                                    ws.update_cell(idx, 7, 0.0)
                                    ws.update_cell(idx, 8, "Pago")
                                    break
                        except Exception:
                            pass
                        
                        st.success("Dívida quitada e salva na planilha!")
                        st.rerun()

# 4. RESULTADO MENSAL
elif pagina == "📈 Resultado Mensal":
    st.subheader("📈 Fechamento e Resultado Mensal")
    
    meses_sem_todos = [m for m in st.session_state.lista_meses if m != "Todos"]
    mes_foco = st.selectbox("Selecione o Mês para Análise", meses_sem_todos)
    
    if len(st.session_state.vendas) > 0:
        df_
