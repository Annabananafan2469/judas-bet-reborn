import streamlit as st
import hashlib
from datetime import datetime
import pytz
from supabase import create_client

st.set_page_config(page_title="Judas Bet: Reborn", page_icon="", layout="centered")

URL_SUPABASE = "https://uhuzuxcshqcswpmtmtxf.supabase.co"
CHAVE_SUPABASE = "sb_publishable_waerNnmSoKjcGXU9kenUDA_h7IWZfN8"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

def criptografar_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def obter_horario_servidor():
    fuso = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso)

def checar_manutencao():
    try:
        res = supabase.table("configuracoes").select("manutencao", "mensagem_manutencao").eq("id", 1).execute()
        if res.data:
            return res.data[0]['manutencao'], res.data[0]['mensagem_manutencao']
    except Exception:
        pass
    return False, ""

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "modo_tela" not in st.session_state:
    st.session_state.modo_tela = "login"

st.markdown("""
<style>
    div[data-testid="stForm"] {
        background-color: #1e1e24;
        border-radius: 15px;
        padding: 30px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    input {
        border-radius: 8px !important;
        background-color: #2b2b36 !important;
        color: white !important;
        border: 1px solid #3f3f4e !important;
    }
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        background-color: #3b3b4f;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #50506b;
        color: white;
    }
    .titulo-auth {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
        color: white;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        color: #a0a0a0;
        background-color: transparent;
        text-decoration: underline;
    }
    .stButton > button:hover {
        color: white;
        background-color: #2b2b36;
    }
</style>
""", unsafe_allow_html=True)

em_manutencao, msg_manutencao = checar_manutencao()

if em_manutencao and not st.session_state.is_admin:
    st.error(" Sistema em Manutenção")
    st.subheader(msg_manutencao)
    st.info("O Admin está ajustando os motores. Voltamos já!")
    st.stop()

if not st.session_state.logado:
    st.markdown("<div class='titulo-auth'>Judas Bet</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.modo_tela == "login":
            with st.form("form_login"):
                user_input = st.text_input("Usuário").strip()
                senha_input = st.text_input("Senha", type="password")
                botao_entrar = st.form_submit_button("Entrar")
                
                if botao_entrar:
                    if user_input and senha_input:
                        resposta = supabase.table("usuarios").select("*").ilike("username", user_input).execute()
                        if resposta.data:
                            usuario = resposta.data[0]
                            if usuario['senha'] == criptografar_senha(senha_input):
                                st.session_state.logado = True
                                st.session_state.usuario_id = usuario['id']
                                st.session_state.username = usuario['username']
                                st.session_state.is_admin = usuario['is_admin']
                                st.rerun()
                            else:
                                st.error("Senha incorreta.")
                        else:
                            st.error("Usuário não encontrado.")
                    else:
                        st.warning("Preencha todos os campos.")
            
            if st.button("Esqueceu a Senha ou Usuário?"):
                st.warning("Função de recuperação pendente. Fale com o Admin!")
                
            if st.button("Criar uma Nova Conta"):
                st.session_state.modo_tela = "cadastro"
                st.rerun()

        else:
            with st.form("form_cadastro"):
                novo_user = st.text_input("Escolha um Usuário").strip()
                novo_nome = st.text_input("Seu Nome de Exibição").strip()
                nova_senha = st.text_input("Crie uma Senha", type="password")
                botao_cadastrar = st.form_submit_button("Cadastrar")
                
                if botao_cadastrar:
                    if novo_user and novo_nome and nova_senha:
                        checar_existente = supabase.table("usuarios").select("id").ilike("username", novo_user).execute()
                        if checar_existente.data:
                            st.error("Esse usuário já existe. Escolha outro.")
                        else:
                            dados = {
                                "username": novo_user,
                                "nome": novo_nome,
                                "senha": criptografar_senha(nova_senha)
                            }
                            inserir = supabase.table("usuarios").insert(dados).execute()
                            if inserir.data:
                                st.success("Conta criada! Volte para o login.")
                    else:
                        st.warning("Preencha todos os campos.")
                        
            if st.button("Já tem uma conta? Fazer Login"):
                st.session_state.modo_tela = "login"
                st.rerun()

else:
    st.write(f"Logado como: {st.session_state.username}")
    if st.button("Sair"):
        st.session_state.logado = False
        st.session_state.is_admin = False
        st.rerun()
