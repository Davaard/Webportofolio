import streamlit as st

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Metal+Mania&family=Bungee+Hairline&family=Rajdhani:wght@300&family=Jura:wght@300&family=Syncopate:wght@400&display=swap');

/* =========================================
   1. KILL COUNT (Metal Mania - Sudah Fiks)
========================================= */
.kill-metal-bold {
    font-family: 'Metal Mania', system-ui;
    font-size: 55px;
    color: transparent;
    -webkit-text-stroke: 2.5px #ff4b4b; 
    margin-bottom: -10px;
    letter-spacing: 3px;
}

/* =========================================
   2. MATCH ID (SATU GARIS / MONOLINE)
========================================= */

/* Opsi 1: Bungee Hairline (Benar-benar murni 1 garis kawat/neon) */
.match-id-bungee {
    font-family: 'Bungee Hairline', display;
    font-size: 40px;
    color: #ffc107; /* Warna emas solid, TANPA text-stroke */
    font-weight: 900;
    letter-spacing: 2px;
}

/* Opsi 2: Rajdhani Light (Garis tipis, kotak tegas, sangat Esports) */
.match-id-rajdhani {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 300;
    font-size: 40px;
    color: #ffc107;
    letter-spacing: 4px;
}

/* Opsi 3: Jura Light (Elegan, melengkung ala mecha/robot) */
.match-id-jura {
    font-family: 'Jura', sans-serif;
    font-weight: 300;
    font-size: 40px;
    color: #ffc107;
    letter-spacing: 3px;
}

/* Opsi 4: Syncopate (Melebar, tipis, sangat futuristik) */
.match-id-syncopate {
    font-family: 'Syncopate', sans-serif;
    font-weight: 400;
    font-size: 30px;
    color: #ffc107;
    letter-spacing: 3px;
}
</style>
""", unsafe_allow_html=True)

html_content = """
<div style="background-color: #121212; padding: 30px; border-radius: 10px; width: 400px; border: 1px solid #333;">

<p style="color: gray; font-size: 12px; margin-bottom: 0;">Kill Count (Metal Mania):</p>
<div class="kill-metal-bold">43 KILL</div>
<br><br>
<hr style="border-color: #333;">

<p style="color: gray; font-size: 12px; margin-bottom: 0;">Match ID 1 (Bungee Hairline - Murni 1 Garis):</p>
<div class="match-id-bungee">W2D1G4</div>
<br>

<p style="color: gray; font-size: 12px; margin-bottom: 0;">Match ID 2 (Rajdhani Light - Kotak Sci-Fi):</p>
<div class="match-id-rajdhani">W2D1G4</div>
<br>

<p style="color: gray; font-size: 12px; margin-bottom: 0;">Match ID 3 (Jura Light - Mecha Elegance):</p>
<div class="match-id-jura">W2D1G4</div>
<br>

<p style="color: gray; font-size: 12px; margin-bottom: 0;">Match ID 4 (Syncopate - Wide Future):</p>
<div class="match-id-syncopate">W2D1G4</div>

</div>
"""

st.markdown(html_content, unsafe_allow_html=True)