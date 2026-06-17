import streamlit as st
import hashlib
from datetime import datetime
import pytz
from supabase import create_client

# Configuração da página mantendo a identidade visual escura
st.set_page_config(page_title="Judas Bet: Reborn", page_icon="", layout="wide")

# Suas credenciais oficiais do Supabase
URL_SUPABASE = "https://uhuzuxcshqcswpmtmtxf.supabase.co"
CHAVE_SUPABASE = "sb_publishable_waerNnmSoKjcGXU9kenUDA_h7IWZfN8"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- FUNÇÕES DE SEGURANÇA E AUXILIARES ---
def criptografar_senha(senha: str) -> str:
    """Criptografa a senha em SHA-256 para checar com segurança."""
    return hashlib.sha256(senha.encode()).hexdigest()

def obter_horario_servidor():
    """Retorna o horário oficial de Brasília (base do Relógio Mestre)."""
    fuso = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso)

def checar_manutencao():
    """Busca o status da manutenção na tabela configuracoes."""
    try:
        res = supabase.table("configuracoes").select("manutencao", "mensagem_manutencao").eq("id", 1).execute()
        if res.data:
            return res.data[0]['manutencao'], res.data[0]['mensagem_manutencao']
    except Exception:
        pass
    return False, ""

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- TRAVA DO MODO MANUTENÇÃO ---
em_manutencao, msg_manutencao = checar_manutencao()

if em_manutencao and not st.session_state.is_admin:
    st.error(" Sistema em Manutenção")
    st.subheader(msg_manutencao)
    st.info("O Admin está ajustando os motores. Voltamos já!")
    st.stop()

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title(" Judas Bet: Reborn")
    st.subheader("Acesse com seu usuário e senha")
    
    with st.form("form_login"):
        user_input = st.text_input("Usuário").strip()
        senha_input = st.text_input("Senha", type="password")
        botao_entrar = st.form_submit_button("Entrar")
        
        if botao_entrar:
            if user_input and senha_input:
                # Busca o usuário ignorando maiúsculas/minúsculas no username
                resposta = supabase.table("usuarios").select("*").ilike("username", user_input).execute()
                
                if resposta.data:
                    usuario = resposta.data[0]
                    if usuario['senha'] == criptografar_senha(senha_input):
                        st.session_state.logado = True
                        st.session_state.usuario_id = usuario['id']
                        st.session_state.username = usuario['username']
                        st.session_state.is_admin = usuario['is_admin']
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
                else:
                    st.error("Usuário não encontrado.")
            else:
                st.warning("Por favor, preencha todos os campos.")

# --- ÁREA LOGADA DO APLICATIVO ---
else:
    col_user, col_clock, col_logout = st.columns([2, 2, 1])
    with col_user:
        st.write(f" Usuário: **{st.session_state.username}** {'(ADMIN)' if st.session_state.is_admin else ''}")
    with col_clock:
        hora_mestre = obter_horario_servidor().strftime("%d/%m/%Y %H:%M:%S")
        st.write(f" Relógio Mestre: `{hora_mestre}`")
    with col_logout:
        if st.button("Sair / Logoff"):
            st.session_state.logado = False
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("---")
    
    if st.session_state.is_admin:
        menu = ["Jogos", "Mural", "Ranking", "Perfil", "Painel Admin"]
    else:
        menu = ["Jogos", "Mural", "Ranking", "Perfil"]
        
    aba_atual = st.sidebar.radio("Navegação", menu)
    
    if aba_atual == "Jogos":
        st.title(" Mural de Jogos & Apostas")
        st.write("Aqui vai entrar a listagem por grupos e o sistema de travar palpite por horário.")
        
    elif aba_atual == "Mural":
        st.title(" Mural da Comunidade")
        st.write("Aqui vai entrar o feed de posts com upload direto de fotos/áudios e reações.")
        
    elif aba_atual == "Ranking":
        st.title(" Classificação Geral")
        st.write("Tabela de liderança atualizada em tempo real.")
        
    elif aba_atual == "Perfil":
        st.title(" Meu Perfil")
        st.write("Estatísticas e escolha do Campeão da Copa.")
        
    elif aba_atual == "Painel Admin" and st.session_state.is_admin:
        st.title(" Painel de Controle Administrativo")
        st.write("Gerenciamento de manutenção, usuários e inserção de resultados.")
