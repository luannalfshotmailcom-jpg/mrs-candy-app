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

# Estilo CSS bege/creme claro e responsivo
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
    .card-venda {
        background-color: #F8F3E6;
        border: 1px solid #C5A86D;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

SHEET_ID = "1lfxzdhzGCWuzWzJ2BU72bL6CmwLRxfK_dI2zvjFDEXE"

def get_worksheet(sheet_name):
    try:
        creds = dict(st.secrets["gcp_service_account"])
        client = gspread.service_account_from_dict(creds)
        sh = client.open_by_key(SHEET_ID)
        for ws in sh.worksheets():
            if ws.title.lower() == sheet_name.lower():
                return ws
        return sh.worksheet(sheet_name)
    except Exception as e:
        st.warning(f"Aviso de Conexão com Planilha: {e}")
        return None

def load_vendas():
    ws = get_worksheet("Vendas")
    if ws:
        try:
            return ws.get_all_records()
        except Exception:
            pass
    return []

def load_cardapio():
    ws = get_worksheet("Cardápio")
    if ws:
        try:
            data = ws.get_all_records()
            c_dict = {}
            for row in data:
                d = str(row.get("Doces", row.get("Doce", ""))).strip()
                p = row.get("Preços", row.get("Preco", row.get("Preço", 0)))
                if d:
                    c_dict[d] = float(str(p).replace("R$", "").replace(",", ".").strip())
            if c_dict:
                return c_dict
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
    ws = get_worksheet("Clientes")
    if ws:
        try:
            data = ws.get_all_records()
            cli_list = []
            for r in data:
                c = r.get("Clientes", r.get("Cliente", ""))
                if c:
                    cli_list.append(str(c).strip())
            if cli_list:
                return sorted(list(set(cli_list)))
        except Exception:
            pass
    return ["Luanna", "Carlos", "Cliente Avulso"]

MESES_PADRAO = [
    "Todos", "10/2026", "11/2026", "12/2026",
    "01/2027", "02/2027", "03/2027", "04/2027", "05/2027", "06/2027"
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

# Menu
st.sidebar.title("📌 Menu")
if st.sidebar.button("🔄 Sincronizar / Recarregar"):
    st.session_state.vendas = load_vendas()
    st.session_state.cardapio = load_cardapio()
    st.session_state.clientes = load_clientes()
    st.success("Sincronizado!")
    st.rerun()

pagina = st.sidebar.radio("Navegar", [
    "📊 Visão Geral", 
    "➕ Registrar Venda", 
    "💰 Cobranças (Fiado)", 
    "📈 Resultado Mensal",
    "📅 Resultado Anual",
    "🍬 Gerenciar Cardápio", 
    "👥 Clientes"
])

# 1. VISÃO GERAL
if pagina == "📊 Visão Geral":
    st.subheader("📊 Controle Geral de Vendas")
    mes_sel = st.selectbox("📅 Selecione o Mês", st.session_state.lista_meses)
    
    ws_vendas = get_worksheet("Vendas")

    if len(st.session_state.vendas) > 0:
        vendas_filtradas = []
        for idx_v, v in enumerate(st.session_state.vendas):
            data_str = str(v.get("Data", ""))
            try:
                dt_obj = pd.to_datetime(data_str, format="%d/%m/%Y", errors="coerce")
                ano_mes = dt_obj.strftime("%m/%Y") if pd.notnull(dt_obj) else "Outros"
            except Exception:
                ano_mes = "Outros"
                
            if mes_sel == "Todos" or ano_mes == mes_sel:
                v_copia = dict(v)
                v_copia["_idx_orig"] = idx_v
                vendas_filtradas.append(v_copia)

        tot = sum(float(v.get("Total", 0)) for v in vendas_filtradas)
        pend = sum(float(v.get("Pendente", 0)) for v in vendas_filtradas)
        rec = tot - pend
    else:
        vendas_filtradas = []
        tot = rec = pend = 0.0

    st.markdown(f"""
        <div class="metric-card"><div class="metric-title">Total Vendas</div><div class="metric-value">R$ {tot:,.2f}</div></div>
        <div class="metric-card"><div class="metric-title">Recebido</div><div class="metric-value" style="color:#1B5E20 !important;">R$ {rec:,.2f}</div></div>
        <div class="metric-card"><div class="metric-title">Pendente (Fiado)</div><div class="metric-value" style="color:#B71C1C !important;">R$ {pend:,.2f}</div></div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Histórico de Vendas Registradas")

    if vendas_filtradas:
        for item in vendas_filtradas:
            v_id = item.get("ID")
            idx_o = item.get("_idx_orig")
            v_data = str(item.get("Data", ""))
            v_cli = str(item.get("Cliente", ""))
            v_doces = str(item.get("Doces", ""))
            v_tot = float(item.get("Total", 0))
            v_pend = float(item.get("Pendente", 0))
            v_status = str(item.get("Status", "Pago"))

            with st.container():
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                        <div class="card-venda">
                            <span style="font-size:12px; color:#5C4328;">📅 {v_data}</span><br>
                            <b>👤 {v_cli}</b><br>
                            <small>🍬 {v_doces}</small><br>
                            <b>Total: R$ {v_tot:.2f}</b> | <span style="color:{'#1B5E20' if v_pend == 0 else '#B71C1C'};">{v_status} (Pend: R$ {v_pend:.2f})</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    if st.button("🗑️", key=f"btn_del_v_{v_id}_{idx_o}"):
                        st.session_state.vendas.pop(idx_o)
                        if ws_vendas:
                            try:
                                records = ws_vendas.get_all_records()
                                for idx, row in enumerate(records, start=2):
                                    if str(row.get("ID")) == str(v_id):
                                        ws_vendas.delete_rows(idx)
                                        break
                            except Exception:
                                pass
                        st.success("Venda excluída!")
                        st.rerun()
    else:
        st.info("Nenhuma venda registrada no período selecionado.")

# 2. REGISTRAR VENDA
elif pagina == "➕ Registrar Venda":
    st.subheader("🛍️ Registrar Nova Venda")
    
    c_cli, c_dat = st.columns([2, 1])
    with c_cli:
        cliente_input = st.selectbox(
            "Cliente (Escolha da lista ou digite para filtrar/criar)", 
            options=[""] + st.session_state.clientes,
            accept_new_options=True
        )
    with c_dat:
        data_venda = st.date_input("Data", date.today())

    st.markdown("---")
    c_doc, c_qtd = st.columns([3, 1])
    with c_doc:
        doces_lista = list(st.session_state.cardapio.keys())
        doce_sel = st.selectbox("Doce", doces_lista) if doces_lista else None
    with c_qtd:
        qtd_input = st.number_input("Qtd.", min_value=1, value=1)

    if doce_sel and st.button("➕ Adicionar Doce", use_container_width=True):
        p = st.session_state.cardapio[doce_sel]
        st.session_state.carrinho.append({"Doce": doce_sel, "Qtd": qtd_input, "Subtotal": p * qtd_input})
        st.rerun()

    if st.session_state.carrinho:
        st.markdown("### 🛒 Pedido:")
        for idx, item in enumerate(st.session_state.carrinho):
            c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
            c1.write(f"**{item['Doce']}**")
            c2.write(f"x{item['Qtd']}")
            c3.write(f"R$ {item['Subtotal']:.2f}")
            if c4.button("🗑️", key=f"del_cart_item_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()

        tot_ped = sum(i["Subtotal"] for i in st.session_state.carrinho)
        st.markdown(f"### **Total: R$ {tot_ped:.2f}**")
        
        v_pago = st.number_input("Valor Recebido (R$)", min_value=0.0, value=float(tot_ped), step=0.50)
        v_pend = max(0.0, tot_ped - v_pago)

        if st.button("✅ Confirmar e Salvar Venda", type="primary", use_container_width=True):
            if not cliente_input or not str(cliente_input).strip():
                st.error("Por favor, informe o nome do cliente.")
            else:
                cli_final = str(cliente_input).strip()
                
                if cli_final not in st.session_state.clientes:
                    st.session_state.clientes.append(cli_final)
                    ws_c = get_worksheet("Clientes")
                    if ws_c:
                        try:
                            ws_c.append_row([cli_final])
                        except Exception:
                            pass

                itens_str = ", ".join([f"{i['Qtd']}x {i['Doce']}" for i in st.session_state.carrinho])
                nova_venda = {
                    "ID": len(st.session_state.vendas) + 1,
                    "Data": data_venda.strftime("%d/%m/%Y"),
                    "Cliente": cli_final,
                    "Doces": itens_str,
                    "Total": float(tot_ped),
                    "Pendente": float(v_pend),
                    "Status": "Pago" if v_pend == 0 else "Pendente"
                }
                
                ws = get_worksheet("Vendas")
                if ws:
                    try:
                        ws.append_row([
                            nova_venda["ID"], nova_venda["Data"], nova_venda["Cliente"],
                            nova_venda["Doces"], nova_venda["Total"], nova_venda["Pendente"], nova_venda["Status"]
                        ])
                        st.success("Salvo na Planilha!")
                    except Exception as e:
                        st.error(f"Erro na gravação: {e}")

                st.session_state.vendas.append(nova_venda)
                st.session_state.carrinho = []
                st.rerun()

# 3. COBRANÇAS / FIADO
elif pagina == "💰 Cobranças (Fiado)":
    st.subheader("💰 Clientes com Fiado Pendente")
    
    pendentes = [v for v in st.session_state.vendas if float(v.get("Pendente", 0)) > 0]
    
    if len(pendentes) == 0:
        st.success("🎉 Nenhum valor pendente de cobrança!")
    else:
        ws_vendas = get_worksheet("Vendas")
        for v in pendentes:
            v_id = v.get("ID")
            v_cli = v.get("Cliente", "")
            v_dat = v.get("Data", "")
            v_doc = v.get("Doces", "")
            v_tot = float(v.get("Total", 0))
            v_pend = float(v.get("Pendente", 0))
            
            st.markdown(f"""
                <div class="card-venda" style="border-left: 5px solid #B71C1C;">
                    <b>👤 {v_cli}</b><br>
                    <small>📅 {v_dat} | 🍬 {v_doc}</small><br>
                    <b>Total Pedido: R$ {v_tot:.2f}</b><br>
                    <h4 style="color:#B71C1C !important; margin: 4px 0;">Falta Pagar: R$ {v_pend:.2f}</h4>
                </div>
            """, unsafe_allow
