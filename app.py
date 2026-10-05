import streamlit as st
from supabase import create_client, Client
import qrcode
from io import BytesIO
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Pit Stop: Raio-X do Time", 
    layout="wide", 
    page_icon="🧭"
)

# Chaves de API vindas dos Secrets
# Credenciais diretas
SUPABASE_URL = "https://zjrvyijjsyvziifmnict.supabase.com"
SUPABASE_KEY = "sb_publishable_tadrPK_VZxXET_97WCUTEA_OwBUwCUA"
APP_URL = "https://pitstop-smiles.streamlit.app/"

@st.cache_resource
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Credenciais do Supabase não encontradas nos Secrets.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# Estilo personalizado para os cards
st.markdown("""
<style>
    .card {
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
        background-color: #f9f9f9;
        color: #222;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Pit Stop: Raio-X do Nosso Time")

tab_form, tab_mural, tab_qrcode = st.tabs([
    "📝 Preencher Meu Raio-X (Celular)", 
    "📊 Mural de Apresentação (TV)", 
    "📲 QR Code da Sala"
])

# ==================== ABA 1: FORMULÁRIO ====================
with tab_form:
    st.markdown("Preencha com sinceridade. Vale misturar vivências do **trabalho** e da **vida pessoal**.")
    
    with st.form("form_raio_x", clear_on_submit=True):
        col_nome, col_area = st.columns(2)
        with col_nome:
            nome = st.text_input("Seu Nome:", placeholder="Ex: Grazi")
        with col_area:
            area = st.selectbox("Sua Frente Principal:", ["Dados", "Negócio", "Outra"])

        st.divider()

        brilho_olho = st.text_area(
            "✨ 1. O que me dá brilho no olho / alegria:",
            placeholder="O que te faz terminar o dia com a sensação de 'valeu a pena'? (na rotina ou no trabalho)",
            height=90
        )
        
        drena_bateria = st.text_area(
            "🔋 2. O que drena minha bateria / desanima:",
            placeholder="O que consome sua energia ou te dá aquela sensação pesada de cansaço?",
            height=90
        )
        
        trava_incomoda = st.text_area(
            "🚧 3. O que me trava / incomoda:",
            placeholder="O que tira seu foco, seu ritmo ou seu bom humor na rotina?",
            height=90
        )
        
        como_ajudado = st.text_area(
            "🤝 4. Como eu gosto de ser ajudado(a):",
            placeholder="Qual o seu melhor jeito de interagir ou receber apoio quando a água bate no pescoço?",
            height=90
        )

        enviar = st.form_submit_button("🚀 Enviar Meu Raio-X", use_container_width=True)

        if enviar:
            if not nome or not brilho_olho or not drena_bateria:
                st.warning("Preencha pelo menos seu nome e os primeiros tópicos!")
            else:
                payload = {
                    "nome": nome.strip(),
                    "area": area,
                    "brilho_olho": brilho_olho,
                    "drena_bateria": drena_bateria,
                    "trava_incomoda": trava_incomoda,
                    "como_ajudado": como_ajudado
                }
                supabase.table("team_radar").insert(payload).execute()
                st.success(f"Pronto, {nome}! Suas respostas já estão registradas.")
                st.balloons()

# ==================== ABA 2: MURAL PARA A TV ====================
with tab_mural:
    st.subheader("Mural de Compartilhamento")
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🔄 Atualizar Respostas", use_container_width=True):
            st.rerun()

    res = supabase.table("team_radar").select("*").order("created_at").execute()
    participantes = res.data

    if not participantes:
        st.info("Nenhuma resposta cadastrada ainda. Abra a aba 'QR Code' para o time responder!")
    else:
        st.caption(f"Participantes que responderam: **{len(participantes)}**")
        
        nomes = [p["nome"] for p in participantes]
        selecionado = st.selectbox("👉 Selecione a pessoa da vez para projetar na TV:", nomes)
        
        perfil = next((p for p in participantes if p["nome"] == selecionado), None)
        
        if perfil:
            st.markdown(f"## 👤 {perfil['nome']} <span style='font-size: 1.2rem; color: gray;'>({perfil['area']})</span>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"### ✨ O que dá brilho no olho:\n\n{perfil['brilho_olho']}")
                st.warning(f"### 🚧 O que me trava / incomoda:\n\n{perfil['trava_incomoda']}")
                
            with c2:
                st.error(f"### 🔋 O que drena a bateria:\n\n{perfil['drena_bateria']}")
                st.success(f"### 🤝 Como gosto de ser ajudado(a):\n\n{perfil['como_ajudado']}")

# ==================== ABA 3: QR CODE ====================
with tab_qrcode:
    st.subheader("Aponte a câmera do celular para responder")
    st.caption("Projete esta tela nos primeiros 5 minutos da reunião.")
    
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(APP_URL)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Aponte o celular para abrir o formulário", width=280)
    st.markdown(f"**Link direto:** `{APP_URL}`")
