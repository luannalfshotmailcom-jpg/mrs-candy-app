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
                return cli_list
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
    "🍬 Gerenciar Cardápio", 
    "👥 Clientes"
])

# 1. VISÃO GERAL
if pagina == "📊 Visão Geral":
    st.subheader("📊 Controle Geral de Vendas")
    mes_sel = st.selectbox("📅 Selecione o Mês", st.session_state.lista_meses)
    
    if len(st.session_state.vendas) > 0:
        df_v = pd.DataFrame(st.session_state.vendas)
        if "Data" in df_v.columns:
            df_v["Data_DT"] = pd.to_datetime(df_v["Data"], format="%d/%m/%Y", errors="coerce")
            df_v["Ano_Mes"] = df_v["Data_DT"].dt.strftime("%m/%Y")
            df_f = df_v[df_v["Ano_Mes"] == mes_sel] if mes_sel != "Todos" else df_v
            
            tot = df_f["Total"].sum() if "Total" in df_f else 0.0
            pend = df_f["Pendente"].sum() if "Pendente" in df_f else 0.0
            rec = tot - pend
        else:
            df_f = pd.DataFrame()
            tot = rec = pend = 0.0
    else:
        df_f = pd.DataFrame()
        tot = rec = pend = 0.0

    st.markdown(f"""
        <div class="metric-card"><div class="metric-title">Total Vendas</div><div class="metric-value">R$ {tot:,.2f}</div></div>
        <div class="metric-card"><div class="metric-title">Recebido</div><div class="metric-value" style="color:#1B5E20 !important;">R$ {rec:,.2f}</div></div>
        <div class="metric-card"><div class="metric-title">Pendente (Fiado)</div><div class="metric-value" style="color:#B71C1C !important;">R$ {pend:,.2f}</div></div>
    """, unsafe_allow_html=True)

    if not df_f.empty:
        cols = [c for c in ["ID", "Data", "Cliente", "Doces", "Total", "Pendente", "Status"] if c in df_f.columns]
        st.dataframe(df_f[cols], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda no período.")

# 2. REGISTRAR VENDA
elif pagina == "➕ Registrar Venda":
    st.subheader("🛍️ Registrar Nova Venda")
    
    c_cli, c_dat = st.columns([2, 1])
    with c_cli:
        cliente_sel = st.selectbox("Cliente (Selecione ou Digite)", st.session_state.clientes)
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
            if c4.button("🗑️", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()

        tot_ped = sum(i["Subtotal"] for i in st.session_state.carrinho)
        st.markdown(f"### **Total: R$ {tot_ped:.2f}**")
        
        v_pago = st.number_input("Valor Recebido (R$)", min_value=0.0, value=float(tot_ped), step=0.50)
        v_pend = max(0.0, tot_ped - v_pago)

        if st.button("✅ Confirmar e Salvar Venda", type="primary", use_container_width=True):
            itens_str = ", ".join([f"{i['Qtd']}x {i['Doce']}" for i in st.session_state.carrinho])
            nova_venda = {
                "ID": len(st.session_state.vendas) + 1,
                "Data": data_venda.strftime("%d/%m/%Y"),
                "Cliente": cliente_sel,
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

# 3. CLIENTES
elif pagina == "👥 Clientes":
    st.subheader("👥 Clientes")
    novo_c = st.text_input("Novo Cliente")
    if st.button("Adicionar") and novo_c:
        st.session_state.clientes.append(novo_c.strip())
        ws = get_worksheet("Clientes")
        if ws:
            ws.append_row([novo_c.strip()])
        st.success("Cliente adicionado!")
        st.rerun()
    for c in st.session_state.clientes:
        st.write(f"• {c}")

# 4. GERENCIAR CARDÁPIO (EDIÇÃO E EXCLUSÃO FÁCIL)
elif pagina == "🍬 Gerenciar Cardápio":
    st.subheader("🍬 Cardápio e Preços Cadastrados")
    st.write("Altere os preços diretamente ou clique na lixeira 🗑️ para remover um doce.")

    ws_cardapio = get_worksheet("Cardápio")

    doces_para_remover = []
    
    for doce, preco_atual in list(st.session_state.cardapio.items()):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        with c1:
            st.markdown(f"**{doce}**")
        with c2:
            novo_p = st.number_input(
                f"Preço (R$)", 
                min_value=0.0, 
                value=float(preco_atual), 
                step=0.50, 
                key=f"p_{doce}"
            )
        with c3:
            if st.button("💾 Salvar", key=f"save_{doce}"):
                st.session_state.cardapio[doce] = novo_p
                if ws_cardapio:
                    try:
                        records = ws_cardapio.get_all_records()
                        for idx, row in enumerate(records, start=2):
                            d_row = str(row.get("Doces", row.get("Doce", ""))).strip()
                            if d_row == doce:
                                ws_cardapio.update_cell(idx, 2, novo_p)
                                break
                    except Exception:
                        pass
                st.success(f"Preço do {doce} atualizado!")
                st.rerun()
        with c4:
            if st.button("🗑️", key=f"del_cardapio_{doce}"):
                doces_para_remover.append(doce)

    if doces_para_remover:
        for d in doces_para_remover:
            del st.session_state.cardapio[d]
            if ws_cardapio:
                try:
                    records = ws_cardapio.get_all_records()
                    for idx, row in enumerate(records, start=2):
                        d_row = str(row.get("Doces", row.get("Doce", ""))).strip()
                        if d_row == d:
                            ws_cardapio.delete_rows(idx)
                            break
                except Exception:
                    pass
        st.success("Doce removido!")
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Cadastrar Novo Doce")
    c_nome, c_pr = st.columns([2, 1])
    with c_nome:
        nome_novo = st.text_input("Nome do Doce")
    with c_pr:
        preco_novo = st.number_input("Preço Inicial (R$)", min_value=0.0, value=10.0, step=0.50)

    if st.button("✨ Adicionar ao Cardápio", use_container_width=True):
        if nome_novo.strip():
            d_limpo = nome_novo.strip()
            st.session_state.cardapio[d_limpo] = preco_novo
            if ws_cardapio:
                try:
                    ws_cardapio.append_row([d_limpo, preco_novo])
                except Exception:
                    pass
            st.success(f"'{d_limpo}' cadastrado com sucesso!")
            st.rerun()
