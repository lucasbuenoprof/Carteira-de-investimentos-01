import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Carteira de Investimentos", layout="wide")

st.title("📊 Dashboard de Investimentos")

# -----------------------------
# carregar carteira
# -----------------------------

def carregar_carteira():
    try:
        df = pd.read_csv("carteira.csv")
        df["ticker"] = df["ticker"].str.upper()
        return df
    except:
        return pd.DataFrame(columns=["ticker","quantidade","preco_medio"])

def salvar_carteira(df):
    df.to_csv("carteira.csv", index=False)

carteira = carregar_carteira()

# -----------------------------
# adicionar ativo
# -----------------------------

st.sidebar.header("Adicionar ativo")

ticker = st.sidebar.text_input("Ticker (ex: PETR4.SA)")
quantidade = st.sidebar.number_input("Quantidade", min_value=1)
preco = st.sidebar.number_input("Preço médio", min_value=0.0)

if st.sidebar.button("Adicionar"):

    if ticker != "":

        novo = pd.DataFrame({
            "ticker":[ticker.upper()],
            "quantidade":[quantidade],
            "preco_medio":[preco]
        })

        carteira = pd.concat([carteira, novo], ignore_index=True)

        salvar_carteira(carteira)

        st.sidebar.success("Ativo adicionado!")

# -----------------------------
# buscar preços
# -----------------------------

if not carteira.empty:

    tickers = carteira["ticker"].tolist()

    precos = {}

    for t in tickers:

        try:

            ativo = yf.Ticker(t)

            hist = ativo.history(period="1d")

            if not hist.empty:
                precos[t] = float(hist["Close"].iloc[-1])
            else:
                precos[t] = 0

        except:
            precos[t] = 0

    carteira["preco_atual"] = carteira["ticker"].map(precos)

# -----------------------------
# garantir números
# -----------------------------

    carteira["quantidade"] = pd.to_numeric(carteira["quantidade"], errors="coerce").fillna(0)
    carteira["preco_medio"] = pd.to_numeric(carteira["preco_medio"], errors="coerce").fillna(0)
    carteira["preco_atual"] = pd.to_numeric(carteira["preco_atual"], errors="coerce").fillna(0)

# -----------------------------
# cálculos
# -----------------------------

    carteira["valor_investido"] = carteira["quantidade"] * carteira["preco_medio"]

    carteira["valor_atual"] = carteira["quantidade"] * carteira["preco_atual"]

    carteira["lucro"] = carteira["valor_atual"] - carteira["valor_investido"]

# rentabilidade %

    carteira["rentabilidade_%"] = 0

    carteira.loc[carteira["valor_investido"] > 0, "rentabilidade_%"] = (
        carteira["lucro"] / carteira["valor_investido"]
    ) * 100

    carteira["rentabilidade_%"] = carteira["rentabilidade_%"].round(1).astype(str) + " %"

# % na carteira

    total_investido = carteira["valor_investido"].sum()

    carteira["% na carteira"] = 0

    if total_investido > 0:

        carteira["% na carteira"] = (
            carteira["valor_investido"] / total_investido
        ) * 100

    carteira["% na carteira"] = carteira["% na carteira"].round(1).astype(str) + " %"

# -----------------------------
# métricas
# -----------------------------

    total_atual = carteira["valor_atual"].sum()

    lucro_total = total_atual - total_investido

    col1,col2,col3 = st.columns(3)

    col1.metric("💰 Valor investido", f"R$ {total_investido:,.2f}")

    col2.metric("📈 Valor atual", f"R$ {total_atual:,.2f}")

    col3.metric("📊 Lucro / Prejuízo", f"R$ {lucro_total:,.2f}")

# -----------------------------
# tabela
# -----------------------------

    st.subheader("Carteira")

    st.dataframe(carteira, use_container_width=True)

# -----------------------------
# remover ativo
# -----------------------------

    st.subheader("Remover ativo")

    ativo_remover = st.selectbox(
        "Escolha o ativo",
        carteira["ticker"]
    )

    if st.button("Remover ativo"):

        carteira = carteira[carteira["ticker"] != ativo_remover]

        salvar_carteira(carteira)

        st.success("Ativo removido!")

        st.rerun()

# -----------------------------
# gráfico do ativo
# -----------------------------

    st.subheader("Gráfico")

    ativo = st.selectbox("Escolha um ativo", tickers)

    try:

        hist = yf.Ticker(ativo).history(period="6mo")

        if not hist.empty:
            st.line_chart(hist["Close"])

    except:
        st.warning("Não foi possível carregar o gráfico.")

else:

    st.info("Adicione ativos na barra lateral.")

# -----------------------------
# atualização automática
# -----------------------------

st.caption("Atualização automática a cada 10 segundos")

time.sleep(10)

st.rerun()
