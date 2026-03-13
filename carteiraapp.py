import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(
    page_title="Minha Carteira",
    layout="wide"
)

st.title("📈 Dashboard de Investimentos")

# -------------------------
# carregar carteira
# -------------------------

def carregar_carteira():
    try:
        return pd.read_csv("carteira.csv")
    except:
        return pd.DataFrame(columns=["ticker","quantidade","preco_medio"])

def salvar_carteira(df):
    df.to_csv("carteira.csv", index=False)

carteira = carregar_carteira()

# -------------------------
# adicionar ativo
# -------------------------

st.sidebar.header("Adicionar ativo")

ticker = st.sidebar.text_input("Ticker (ex: PETR4.SA)")
quantidade = st.sidebar.number_input("Quantidade", min_value=1)
preco = st.sidebar.number_input("Preço médio", min_value=0.0)

if st.sidebar.button("Adicionar"):

    if ticker != "":

        novo = pd.DataFrame({
            "ticker":[ticker],
            "quantidade":[quantidade],
            "preco_medio":[preco]
        })

        carteira = pd.concat([carteira, novo], ignore_index=True)
        salvar_carteira(carteira)

        st.sidebar.success("Ativo adicionado!")

# -------------------------
# buscar preços
# -------------------------

if not carteira.empty:

    tickers = carteira["ticker"].tolist()

    dados = yf.download(
        tickers,
        period="5d",
        progress=False
    )

    if dados.empty:
        st.error("Não foi possível carregar os preços. Verifique os tickers.")
        st.stop()

    precos = dados["Close"].iloc[-1]

    carteira["preco_atual"] = carteira["ticker"].map(precos)

    carteira["valor_investido"] = carteira["quantidade"] * carteira["preco_medio"]
    carteira["valor_atual"] = carteira["quantidade"] * carteira["preco_atual"]

    carteira["lucro"] = carteira["valor_atual"] - carteira["valor_investido"]

    carteira["rentabilidade_%"] = (
        carteira["lucro"] / carteira["valor_investido"]
    ) * 100

# -------------------------
# métricas da carteira
# -------------------------

    total_investido = carteira["valor_investido"].sum()
    total_atual = carteira["valor_atual"].sum()
    lucro_total = total_atual - total_investido

    col1,col2,col3 = st.columns(3)

    col1.metric(
        "💰 Valor investido",
        f"R$ {total_investido:,.2f}"
    )

    col2.metric(
        "📊 Valor atual",
        f"R$ {total_atual:,.2f}"
    )

    col3.metric(
        "📈 Lucro / Prejuízo",
        f"R$ {lucro_total:,.2f}"
    )

# -------------------------
# tabela carteira
# -------------------------
    
    st.dataframe(
    carteira,
    use_container_width=True
)
    st.subheader("Carteira")

    st.subheader("Remover ativo")

    ativo_remover = st.selectbox(
    "Escolha o ativo para remover",
    carteira["ticker"]
)

if st.button("Remover ativo"):

    carteira = carteira[carteira["ticker"] != ativo_remover]

    carteira.to_csv("carteira.csv", index=False)

    st.success("Ativo removido!")

    st.experimental_rerun()

# -------------------------
# gráfico ativo
# -------------------------

    st.subheader("Gráfico do ativo")

    ativo = st.selectbox(
        "Escolha um ativo",
        tickers
    )

    hist = yf.download(
        ativo,
        period="6mo",
        progress=False
    )

    if not hist.empty:
        st.line_chart(hist["Close"])
    else:
        st.warning("Não foi possível carregar o gráfico.")

else:

    st.info("Adicione ativos na barra lateral.")

# -------------------------
# atualização automática
# -------------------------

st.caption("Atualiza automaticamente a cada 60 segundos")

time.sleep(60)
st.experimental_rerun()
