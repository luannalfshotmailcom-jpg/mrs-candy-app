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
        # Tentar buscar sem ou com acento
        worksheets = [ws.title for ws in sh.worksheets()]
        for title in worksheets:
            if title.lower() == sheet_name.lower():
                return sh.worksheet(title)
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
        ws = get_worksheet("Cardápio")
        data = ws.get_all_records()
        if data:
            cardapio_dict = {}
            for row in data:
                doc_nome = str(row.get("Doces", row.get("Doce", ""))).strip()
                preco_val = row.get("Preços", row.get("Preco", row.get("Preço", 0)))
                if doc_nome:
                    preco_float = float(str(preco_val).replace("R$", "").replace(",", ".").strip())
                    cardapio_dict[doc_nome] = preco_float
            if cardapio_dict:
                return cardapio_dict
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
            res = []
            for r in records:
                cli = r.get("Clientes", r.get("Cliente", ""))
                if cli:
                    res.append(str(cli).strip())
            if res:
                return res
    except Exception:
        pass
    return ["Luanna", "Carlos", "Cliente Avulço"]

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
            tot_pendente = df_filtrado["Pendente"].sum() if not df_filtrado.empty and "Pendente" in df_filtrado else 0.0
            tot_recebido = tot_vendas - tot_pendente
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
        colunas_exibir = [c for c in ["ID", "Data", "Cliente", "Doces", "Total", "Pendente", "Status"] if c in df_filtrado.columns]
        st.dataframe(df_filtrado[colunas_exibir], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda registrada no período selecionado.")

# 2. REGISTRAR VENDA
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
            
            nova_venda_dict = {
                "ID": len(st.session_state.vendas) + 1,
                "Data": data_venda.strftime("%d/%m/%Y"),
                "Cliente": cliente_sel,
                "Doces": itens_str,
                "Total": float(total_pedido),
                "Pendente": float(v_pendente),
                "Status": "Pago" if v_pendente == 0 else "Pendente"
            }
            
            # Salvar no Google Sheets
            try:
                ws = get_worksheet("Vendas")
                ws.append_row([
                    nova_venda_dict["ID"],
                    nova_venda_dict["Data"],
                    nova_venda_dict["Cliente"],
                    nova_venda_dict["Doces"],
                    nova_venda_dict["Total"],
                    nova_venda_dict["Pendente"],
                    nova_venda_dict["Status"]
                ])
                st.success("Venda gravada com sucesso na planilha!")
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")

            st.session_state.vendas.append(nova_venda_dict)
            st.session_state.carrinho = []
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
                        <p style="margin:0; color:#333;"><b>Total do Pedido:</b> R$ {float(v.get('Total', 0)):.2f}</p>
                        <h3 style="margin:5px 0; color:#B71C1C !important;">Falta Pagar: R$ {float(v.get('Pendente', 0)):.2f}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✅ Quitar Tudo", key=f"pago_{v.get('ID')}"):
                    v["Pendente"] = 0.0
                    v["Status"] = "Pago"
                    
                    try:
                        ws = get_worksheet("Vendas")
                        records = ws.get_all_records()
                        for idx, row in enumerate(records, start=2):
                            if str(row.get("ID")) == str(v.get("ID")):
                                ws.update_cell(idx, 6, 0.0) # Coluna Pendente
                                ws.update_cell(idx, 7, "Pago") # Coluna Status
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
        df_v = pd.DataFrame(st.session_state.vendas)
        if "Data" in df_v.columns:
            df_v["Data_DT"] = pd.to_datetime(df_v["Data"], format="%d/%m/%Y", errors="coerce")
            df_v["Ano_Mes"] = df_v["Data_DT"].dt.strftime("%m/%Y")
            
            df_mes = df_v[df_v["Ano_Mes"] == mes_foco]
            
            if not df_mes.empty:
                tot_faturamento = df_mes["Total"].sum()
                tot_fiado = df_mes["Pendente"].sum()
                tot_pago = tot_faturamento - tot_fiado
                qtd_pedidos = len(df_mes)
                
                c1, c2 = st.columns(2)
                c1.markdown(f'<div class="metric-card"><div class="metric-title">Faturamento Total</div><div class="metric-value">R$ {tot_faturamento:,.2f}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="metric-card"><div class="metric-title">Nº de Pedidos</div><div class="metric-value">{qtd_pedidos}</div></div>', unsafe_allow_html=True)
                
                c3, c4 = st.columns(2)
                c3.markdown(f'<div class="metric-card"><div class="metric-title">Valor Recebido</div><div class="metric-value" style="color:#1B5E20 !important;">R$ {tot_pago:,.2f}</div></div>', unsafe_allow_html=True)
                c4.markdown(f'<div class="metric-card"><div class="metric-title">Fiado Pendente</div><div class="metric-value" style="color:#B71C1C !important;">R$ {tot_fiado:,.2f}</div></div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.write(f"### Pedidos do Mês de {mes_foco}")
                cols = [c for c in ["ID", "Data", "Cliente", "Doces", "Total", "Status"] if c in df_mes.columns]
                st.dataframe(df_mes[cols], use_container_width=True, hide_index=True)
            else:
                st.info(f"Nenhuma venda registrada no mês de {mes_foco}.")

# 5. RESULTADO ANUAL
elif pagina == "📅 Resultado Anual":
    st.subheader("📅 Fechamento e Balanço Anual")
    
    anos_disponiveis = ["2026", "2027", "2028"]
    ano_foco = st.selectbox("Selecione o Ano para Análise", anos_disponiveis)
    
    if len(st.session_state.vendas) > 0:
        df_v = pd.DataFrame(st.session_state.vendas)
        if "Data" in df_v.columns:
            df_v["Data_DT"] = pd.to_datetime(df_v["Data"], format="%d/%m/%Y", errors="coerce")
            df_v["Ano"] = df_v["Data_DT"].dt.strftime("%Y")
            
            df_ano = df_v[df_v["Ano"] == ano_foco]
            
            if not df_ano.empty:
                tot_ano_vendas = df_ano["Total"].sum()
                tot_ano_fiado = df_ano["Pendente"].sum()
                tot_ano_pago = tot_ano_vendas - tot_ano_fiado
                
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Faturamento Anual ({ano_foco})</div>
                        <div class="metric-value">R$ {tot_ano_vendas:,.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Total Recebido no Ano</div>
                        <div class="metric-value" style="color:#1B5E20 !important;">R$ {tot_ano_pago:,.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Total em Fiado no Ano</div>
                        <div class="metric-value" style="color:#B71C1C !important;">R$ {tot_ano_fiado:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"Nenhuma venda registrada no ano de {ano_foco}.")

# 6. GERENCIAR CARDÁPIO E PREÇOS
elif pagina == "🍬 Gerenciar Cardápio":
    st.subheader("🍬 Cardápio e Preços Cadastrados")
    
    df_c = pd.DataFrame([{"Doce": k, "Preço Unitário (R$)": f"{v:.2f}"} for k, v in st.session_state.cardapio.items()])
    st.dataframe(df_c, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("✏️ Cadastrar ou Atualizar Doce")
    
    c_nome, c_pr = st.columns([2, 1])
    with c_nome:
        nome_doce_input = st.text_input("Nome do Doce (Novo ou Existente)")
    with c_pr:
        preco_doce_input = st.number_input("Novo Preço (R$)", min_value=0.0, value=10.0, step=0.50)

    if st.button("💾 Salvar Doce / Atualizar Preço", use_container_width=True):
        if nome_doce_input.strip():
            doce_limpo = nome_doce_input.strip()
            st.session_state.cardapio[doce_limpo] = preco_doce_input
            
            try:
                ws = get_worksheet("Cardápio")
                records = ws.get_all_records()
                encontrado = False
                for idx, row in enumerate(records, start=2):
                    doc_atual = str(row.get("Doces", row.get("Doce", ""))).strip()
                    if doc_atual == doce_limpo:
                        ws.update_cell(idx, 2, preco_doce_input)
                        encontrado = True
                        break
                if not encontrado:
                    ws.append_row([doce_limpo, preco_doce_input])
            except Exception:
                pass

            st.success(f"Doce '{doce_limpo}' salvo com sucesso!")
            st.rerun()

# 7. CLIENTES
elif pagina == "👥 Clientes":
    st.subheader("👥 Lista de Clientes")
    
    novo_c = st.text_input("Nome do Novo Cliente")
    if st.button("➕ Adicionar Cliente") and novo_c:
        c_nome = novo_c.strip()
        if c_nome not in st.session_state.clientes:
            st.session_state.clientes.append(c_nome)
            try:
                ws = get_worksheet("Clientes")
                ws.append_row([c_nome])
            except Exception:
                pass
            st.success(f"Cliente '{c_nome}' cadastrado!")
            st.rerun()
            
    st.markdown("---")
    for c in st.session_state.clientes:
        st.write(f"• {c}")

# 8. GERENCIAR MESES / DATAS
elif pagina == "⚙️ Gerenciar Datas":
    st.subheader("⚙️ Gerenciar Lista de Meses para Filtro")
    
    novo_mes = st.text_input("Adicionar novo mês (Ex: 01/2028)")
    if st.button("➕ Adicionar Mês") and novo_mes:
        m_limpo = novo_mes.strip()
        if m_limpo not in st.session_state.lista_meses:
            st.session_state.lista_meses.append(m_limpo)
            st.success(f"Mês '{m_limpo}' adicionado ao filtro!")
            st.rerun()
            
    st.markdown("---")
    st.write("### Meses Atualmente Disponíveis no Filtro:")
    st.write(", ".join(st.session_state.lista_meses))
