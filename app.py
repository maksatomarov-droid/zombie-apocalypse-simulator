import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from model import run_sir_model, get_summary_stats
from rules import get_survival_rules
from translations import t
import os
import random
import time

# ── 🔑 OPENROUTER API КЛЮЧ ───────────────────────────────────────────────────
OPENROUTER_API_KEY = "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"
# ─────────────────────────────────────────────────────────────────────────────

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="🧟 Zombie Apocalypse Simulator", page_icon="🧟", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Creepster&family=Oswald:wght@400;600;700&family=Share+Tech+Mono&display=swap');
html, body, [data-testid="stAppViewContainer"] { background-color:#060606 !important; color:#e0e0e0 !important; font-family:'Oswald',sans-serif; }
[data-testid="stAppViewContainer"] > .main > div:first-child { padding-top: 0.5rem !important; }
section[data-testid="stSidebar"] { display:none; }
.block-container { padding-top: 0.5rem !important; }
.hero { background:linear-gradient(135deg,#1a0000 0%,#080808 40%,#001200 100%); border:1px solid #3d0000; border-radius:12px; padding:2.5rem 2rem 2rem; margin-bottom:1.5rem; text-align:center; position:relative; overflow:hidden; }
.hero::before { content:''; position:absolute; inset:0; background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(255,0,0,0.02) 2px,rgba(255,0,0,0.02) 4px); pointer-events:none; }
.hero h1 { font-family:'Creepster',cursive; font-size:3.8rem; margin:0; letter-spacing:4px; color:#ff2222; text-shadow:0 0 40px #ff000088,0 0 80px #ff000033; animation:flicker 4s infinite; }
@keyframes flicker { 0%,19%,21%,23%,25%,54%,56%,100%{opacity:1} 20%,22%,24%,55%{opacity:0.85} }
.hero .subtitle { color:#777; font-size:1rem; margin-top:.6rem; letter-spacing:1px; }
.hero .links { margin-top:1rem; }
.hero .links a { color:#ff5555; text-decoration:none; font-size:.82rem; margin:0 .75rem; }
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin:1.5rem 0; }
@media(max-width:768px){.metric-grid{grid-template-columns:repeat(2,1fr);}}
.metric-card { background:#111; border:1px solid #222; border-radius:10px; padding:1.2rem 1rem; text-align:center; transition:all .25s; position:relative; overflow:hidden; }
.metric-card::after { content:''; position:absolute; bottom:0; left:0; right:0; height:2px; background:#ff3333; transform:scaleX(0); transition:transform .25s; }
.metric-card:hover { border-color:#ff3333; transform:translateY(-2px); }
.metric-card:hover::after { transform:scaleX(1); }
.metric-card .label { font-size:.72rem; color:#666; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:.4rem; font-family:'Share Tech Mono',monospace; }
.metric-card .value { font-size:2rem; font-weight:700; font-family:'Share Tech Mono',monospace; }
.metric-card .sub { font-size:.78rem; color:#555; margin-top:.2rem; }
.red{color:#ff4444;} .green{color:#44ff88;} .blue{color:#4488ff;} .amber{color:#ffaa44;}
.section-header { font-family:'Oswald',sans-serif; font-size:1.25rem; font-weight:600; border-left:3px solid #ff3333; padding-left:.75rem; margin:1.8rem 0 1rem; color:#ddd; letter-spacing:1px; text-transform:uppercase; }
.rule-card { background:#111; border:1px solid #222; border-left:4px solid #ff3333; border-radius:8px; padding:1rem 1.25rem; margin-bottom:.75rem; transition:background .2s; }
.rule-card:hover{background:#161616;}
.rule-card .rule-title { font-size:1rem; font-weight:600; color:#ff6666; margin-bottom:.35rem; font-family:'Oswald',sans-serif; }
.rule-card .rule-text { color:#999; font-size:.9rem; line-height:1.55; }
.banner { border-radius:8px; padding:1rem 1.25rem; margin:1rem 0; font-size:.93rem; line-height:1.55; }
.banner-red{background:#1a0000;border:1px solid #550000;color:#ff8888;}
.banner-green{background:#001a0a;border:1px solid #005522;color:#55ffaa;}
.banner-yellow{background:#1a1200;border:1px solid #554400;color:#ffcc55;}
.banner-blue{background:#00101a;border:1px solid #003355;color:#55aaff;}
.char-card { background:linear-gradient(135deg,#0f0000,#000f00); border:1px solid #330000; border-radius:12px; padding:1.5rem; text-align:center; animation:fadeIn .5s ease; }
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.char-name { font-family:'Creepster',cursive; font-size:2rem; color:#ff4444; letter-spacing:2px; }
.char-nickname { font-family:'Share Tech Mono',monospace; color:#888; font-size:.9rem; margin-top:.25rem; }
.survival-bar-bg { background:#1a1a1a; border-radius:20px; height:22px; overflow:hidden; border:1px solid #2a2a2a; margin:1rem 0 .5rem; }
.survival-bar-fill { height:100%; border-radius:20px; display:flex; align-items:center; justify-content:flex-end; padding-right:8px; font-size:.75rem; font-weight:700; font-family:'Share Tech Mono',monospace; }
.event-card { background:#1a0a00; border:1px solid #553300; border-left:4px solid #ff8800; border-radius:8px; padding:1rem 1.25rem; margin:.5rem 0; animation:fadeIn .4s ease; }
.event-card .event-title { color:#ffaa44; font-weight:600; font-size:1rem; margin-bottom:.3rem; }
.event-card .event-text { color:#999; font-size:.88rem; }
.lb-row { display:flex; align-items:center; gap:1rem; background:#111; border:1px solid #222; border-radius:8px; padding:.75rem 1rem; margin-bottom:.5rem; }
.lb-rank { font-family:'Share Tech Mono',monospace; font-size:1.2rem; width:2rem; text-align:center; }
.lb-name { flex:1; font-weight:600; color:#ddd; }
.lb-city { color:#555; font-size:.85rem; }
.lb-score { font-family:'Share Tech Mono',monospace; font-size:1.1rem; font-weight:700; }
.lb-gold{color:#ffd700;} .lb-silver{color:#c0c0c0;} .lb-bronze{color:#cd7f32;} .lb-other{color:#666;}
.scenario-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:1rem 0; }
@media(max-width:768px){.scenario-grid{grid-template-columns:1fr;}}
.scenario-card { background:#111; border:1px solid #222; border-radius:10px; padding:1.25rem; text-align:center; }
.sc-title { font-family:'Oswald'; font-size:1.1rem; font-weight:700; letter-spacing:1px; margin-bottom:.5rem; }
.sc-survival { font-family:'Share Tech Mono'; font-size:2rem; font-weight:700; margin:.5rem 0; }
.sc-desc { color:#666; font-size:.82rem; line-height:1.5; }
.kz-city-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.75rem; margin:1rem 0; }
@media(max-width:600px){.kz-city-grid{grid-template-columns:repeat(2,1fr);}}
.kz-city-card { background:#111; border:1px solid #222; border-radius:8px; padding:.9rem .75rem; text-align:center; }
.kz-city-card .city-name { font-size:.95rem; font-weight:600; color:#ddd; margin-bottom:.3rem; }
.stTabs [data-baseweb="tab"] { color:#666; font-family:'Oswald',sans-serif; }
.stTabs [aria-selected="true"] { color:#ff4444 !important; border-bottom-color:#ff4444 !important; }
.stButton > button { background:linear-gradient(135deg,#990000,#cc0000) !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; font-family:'Oswald',sans-serif !important; letter-spacing:1px !important; transition:all .2s !important; text-transform:uppercase !important; }
.stButton > button:hover { background:linear-gradient(135deg,#cc0000,#ff0000) !important; box-shadow:0 4px 20px #ff000044 !important; }
[data-testid="stSidebar"]{display:none !important;}
[data-testid="collapsedControl"]{display:none !important;}
#MainMenu,footer,header{visibility:hidden;}

/* ---------- news ticker ---------- */
.ticker-wrap {
    position:fixed; bottom:0; left:0; right:0; z-index:9999;
    background:linear-gradient(90deg,#0a0000,#1a0000,#0a0000);
    border-top:1px solid #550000;
    padding:.4rem 0; overflow:hidden;
}
.ticker-label {
    display:inline-block; background:#cc0000;
    color:white; font-family:'Share Tech Mono',monospace;
    font-size:.78rem; font-weight:700; letter-spacing:2px;
    padding:.2rem .75rem; margin-right:1rem;
    vertical-align:middle;
}
.ticker-track {
    display:inline-block;
    white-space:nowrap;
    animation:ticker-scroll 55s linear infinite;
    font-family:'Share Tech Mono',monospace;
    font-size:.78rem; color:#ff6666; letter-spacing:.5px;
}
.ticker-track:hover { animation-play-state:paused; }
@keyframes ticker-scroll {
    from { transform:translateX(100vw); }
    to   { transform:translateX(-100%); }
}
.ticker-item { margin-right:4rem; }
.ticker-item::before { content:'🔴 '; }
</style>
""", unsafe_allow_html=True)

# ── News ticker ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-wrap">
    <span class="ticker-label">⚠ СРОЧНО</span>
    <span class="ticker-track">
        <span class="ticker-item">Алматы захвачен зомби — эвакуация остановлена</span>
        <span class="ticker-item">Армия окружила периметр Астаны — въезд запрещён</span>
        <span class="ticker-item">Учёные в Сеуле сообщают о частичной вакцине — испытания продолжаются</span>
        <span class="ticker-item">Мост через Иртыш взорван — зомби отрезаны от севера</span>
        <span class="ticker-item">Актау объявлен последним безопасным городом — полуостров под защитой</span>
        <span class="ticker-item">R₀ вируса достиг 4.2 — ВОЗ объявляет пандемию зомби</span>
        <span class="ticker-item">Пентагон активировал CONPLAN 8888 — операция началась</span>
        <span class="ticker-item">CDC подтверждает: карантин снижает R₀ ниже 1 — есть надежда</span>
        <span class="ticker-item">Шымкент держится — жители организовали оборону по правилам выживания</span>
        <span class="ticker-item">Запасы Твинки на исходе — моральный дух выживших падает</span>
        <span class="ticker-item">Вирус мутировал в Бразилии — β увеличился до 0.8</span>
        <span class="ticker-item">Японские учёные завершили SIR-моделирование — прогноз неутешительный</span>
    </span>
</div>
""", unsafe_allow_html=True)

# ── Data & session state ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:    return pd.read_csv("data/epidemic_data.csv")
    except: return pd.read_csv("epidemic_data.csv")

df = load_data()

if "lang" not in st.session_state:
    st.session_state["lang"] = "KZ"
if "leaderboard" not in st.session_state:
    st.session_state["leaderboard"] = [
        {"name":"Данияр","city":"Астана","profession":"Военный / Полицейский","score":85,"verdict":"✅"},
        {"name":"Максат","city":"Актау","profession":"Инженер / IT специалист","score":78,"verdict":"✅"},
        {"name":"Айгерим","city":"Алматы","profession":"Врач / Медработник","score":71,"verdict":"✅"},
        {"name":"Сабина","city":"Шымкент","profession":"Менеджер / Офисный работник","score":34,"verdict":"⚠️"},
        {"name":"Арман","city":"Атырау","profession":"Блогер / Инфлюенсер 😄","score":12,"verdict":"💀"},
    ]
if "events_log" not in st.session_state:
    st.session_state["events_log"] = []

RANDOM_EVENTS = [
    {"emoji":"💉","title":"Найдена вакцина!","desc":"Учёные разработали частичную вакцину. Скорость заражения снижена на 30%.","beta_mult":0.7,"gamma_mult":1.0},
    {"emoji":"🪖","title":"Армия начала зачистку!","desc":"Военные развернули операцию. Скорость уничтожения зомби удвоилась.","beta_mult":1.0,"gamma_mult":2.0},
    {"emoji":"☣️","title":"Мутация вируса!","desc":"Вирус мутировал — стал в 2 раза заразнее. Карантин теряет эффективность.","beta_mult":2.0,"gamma_mult":1.0},
    {"emoji":"🏙️","title":"Паника в городах!","desc":"Люди бегут из городов хаотично. Карантин нарушен — заражение ускорилось.","beta_mult":1.5,"gamma_mult":0.8},
    {"emoji":"📡","title":"Экстренное радиовещание!","desc":"Власти наладили связь. Население получило инструкции — потери снижены.","beta_mult":0.85,"gamma_mult":1.3},
    {"emoji":"💥","title":"Взрыв на заводе!","desc":"Промышленная авария изолировала очаг заражения.","beta_mult":0.6,"gamma_mult":1.0},
    {"emoji":"🌧️","title":"Ураган!","desc":"Стихийное бедствие замедлило всех — и зомби, и выживших.","beta_mult":0.75,"gamma_mult":0.75},
    {"emoji":"🐕","title":"Собаки-детекторы!","desc":"Обученные собаки помогают обнаруживать заражённых раньше.","beta_mult":0.9,"gamma_mult":1.4},
]

# ── Language switcher ─────────────────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="column"]:has(button[kind="primary"]) button,
div[data-testid="column"]:has(button[kind="secondary"]) button {
    padding: .2rem .5rem !important;
    font-size: .78rem !important;
    min-height: 0 !important;
    height: 2rem !important;
    letter-spacing: .5px !important;
}
</style>
""", unsafe_allow_html=True)

lc0, lc1, lc2, lc3, lc_end = st.columns([5, 0.6, 0.6, 0.6, 0.2])
with lc1:
    if st.button("🇰🇿 ҚАЗ", use_container_width=True,
                 type="primary" if st.session_state["lang"]=="KZ" else "secondary"):
        st.session_state["lang"] = "KZ"; st.rerun()
with lc2:
    if st.button("🇷🇺 РУС", use_container_width=True,
                 type="primary" if st.session_state["lang"]=="RU" else "secondary"):
        st.session_state["lang"] = "RU"; st.rerun()
with lc3:
    if st.button("🇺🇸 ENG", use_container_width=True,
                 type="primary" if st.session_state["lang"]=="EN" else "secondary"):
        st.session_state["lang"] = "EN"; st.rerun()

lang = st.session_state["lang"]

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero" style="margin-top:0;padding:1.5rem 2rem 1.5rem;">
    <h1>🧟 ZOMBIE APOCALYPSE SIMULATOR</h1>
    <p class="subtitle">{t("hero_subtitle", lang)}</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    t("tab_simulator",lang), t("tab_events",lang), t("tab_scenarios",lang),
    t("tab_character",lang), t("tab_data",lang),
    t("tab_zombie",lang), t("tab_ai",lang),
    "🤖 ML" if lang=="EN" else ("🤖 МЛ-модель" if lang=="RU" else "🤖 МЛ-үлгі"),
    t("tab_about",lang)
])

# ── Navigation guide ──────────────────────────────────────────────────────────
nav_titles = {
    "RU": "📖 Как пользоваться симулятором",
    "EN": "📖 How to use the simulator",
    "KZ": "📖 Симуляторды қалай пайдалану керек",
}
nav_tabs = {
    "RU": [
        ("🧟", "1. Симулятор", "Выбери страну или настрой параметры вручную → нажми ЗАПУСТИТЬ → смотри как распространяется вирус зомби на графике"),
        ("🎲", "2. События", "Нажимай кнопку 🎲 чтобы применить случайное событие — вакцина, мутация, армия. Смотри как это меняет ход эпидемии"),
        ("📊", "3. Сценарии", "Сравни три варианта развития эпидемии: без мер / с карантином / с вакциной. Также можно сравнить две страны"),
        ("👤", "4. Персонаж", "Введи своё имя и данные → узнай свой шанс выживания → получи PDF сертификат выжившего"),
        ("📈", "5. Данные", "Реальные данные COVID-19 по 15 странам — графики R₀, вакцинации, смертности"),
        ("📖", "6. О проекте", "Описание проекта, SIR-модель, стек технологий, глоссарий терминов"),
        ("🧟", "7. Если ты зомби", "Юмористический раздел — как эффективно устроить апокалипсис. Adversarial Attack анализ 😄"),
        ("🤖", "8. ИИ-аналитик", "Задай вопрос ИИ-эпидемиологу: о пандемиях, вакцинах, защите от вирусов"),
        ("🔬", "9. ML-модель", "Random Forest классификатор — предсказывает выживаемость на основе машинного обучения"),
    ],
    "EN": [
        ("🧟", "1. Simulator", "Choose a country or set parameters manually → click RUN → watch how the zombie virus spreads on the chart"),
        ("🎲", "2. Events", "Press 🎲 to apply a random event — vaccine, mutation, army. See how it changes the epidemic"),
        ("📊", "3. Scenarios", "Compare three epidemic scenarios: no measures / quarantine / vaccine. Also compare two countries"),
        ("👤", "4. Character", "Enter your name and data → find out your survival chance → get a PDF survivor certificate"),
        ("📈", "5. Data", "Real COVID-19 data across 15 countries — R₀, vaccination, mortality charts"),
        ("📖", "6. About", "Project description, SIR model, tech stack, glossary of terms"),
        ("🧟", "7. If You're a Zombie", "Humorous section — how to efficiently cause an apocalypse. Adversarial Attack analysis 😄"),
        ("🤖", "8. AI Analyst", "Ask an AI epidemiologist: about pandemics, vaccines, virus protection"),
        ("🔬", "9. ML Model", "Random Forest classifier — predicts survival based on machine learning"),
    ],
    "KZ": [
        ("🧟", "1. Симулятор", "Елді таңда немесе параметрлерді қолмен орнат → ІСКЕ ҚОСУ → вирустың таралуын графикте байқа"),
        ("🎲", "2. Оқиғалар", "Кездейсоқ оқиға қолдану үшін 🎲 батырмасын басыңыз — вакцина, мутация, әскер"),
        ("📊", "3. Сценарийлер", "Үш сценарийді салыстыр: шарасыз / карантин / вакцина. Екі елді де салыстыруға болады"),
        ("👤", "4. Кейіпкер", "Атыңды және деректерді енгіз → тіршілік ету мүмкіндігіңді біл → PDF сертификат ал"),
        ("📈", "5. Деректер", "15 ел бойынша нақты COVID-19 деректері — R₀, вакцинация, өлім-жітім графиктері"),
        ("📖", "6. Жоба туралы", "Жоба сипаттамасы, SIR моделі, технологиялар стегі, терминдер сөздігі"),
        ("🧟", "7. Егер зомби болсаң", "Юмористикалық бөлім — апокалипсисті тиімді ұйымдастыру жолы 😄"),
        ("🤖", "8. ЖИ-аналитик", "ЖИ-эпидемиологқа сұрақ қой: пандемия, вакцина, вирустардан қорғану"),
        ("🔬", "9. МЛ-үлгі", "Random Forest классификаторы — машиналық оқыту негізінде тіршілік ету мүмкіндігін болжайды"),
    ],
}

with st.expander(nav_titles.get(lang, nav_titles["RU"]), expanded=False):
    tabs_info = nav_tabs.get(lang, nav_tabs["RU"])
    cols = st.columns(3)
    for i, (emoji, title, desc) in enumerate(tabs_info):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#111;border:1px solid #222;border-left:3px solid #ff3333;border-radius:8px;padding:.9rem 1rem;margin-bottom:.75rem;min-height:110px;">
                <div style="font-size:1.4rem;margin-bottom:.3rem;">{emoji}</div>
                <div style="color:#ff6666;font-weight:600;font-size:.9rem;margin-bottom:.4rem;">{title}</div>
                <div style="color:#666;font-size:.8rem;line-height:1.4;">{desc}</div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SIMULATOR
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    with st.expander(t("params_title", lang), expanded=True):
        st.markdown(f"**{t('country_label', lang)}**")
        country_choice = st.selectbox("", [t("manual",lang)]+list(df["country"].values), key="country", label_visibility="collapsed")
        if country_choice != t("manual", lang):
            row = df[df["country"]==country_choice].iloc[0]
            db, dg, dp, dq = float(row["peak_beta"]), float(row["gamma"]), int(row["population"]), 0.3
        else:
            db, dg, dp, dq = 0.30, 0.10, 1_000_000, 0.30
        c1,c2,c3 = st.columns(3)
        with c1:
            population     = st.slider(t("sl_population",lang), 10_000, 10_000_000, dp, 10_000)
            infected_start = st.slider(t("sl_zombies",lang), 1, 1000, 10)
        with c2:
            beta  = st.slider(t("sl_beta",lang), 0.05, 1.0, db, 0.01)
            gamma = st.slider(t("sl_gamma",lang), 0.01, 0.5, dg, 0.01)
        with c3:
            quarantine = st.slider(t("sl_quarantine",lang), 0.0, 0.9, dq, 0.05)
            days       = st.slider(t("sl_days",lang), 30, 365, 180, 10)

    run_btn = st.button(t("run_btn", lang), type="primary", use_container_width=True)

    if run_btn or "last_run" in st.session_state:
        if run_btn:
            with st.spinner(t("spinner", lang)):
                time.sleep(1.2)
            st.markdown("""<script>(function(){try{var ctx=new(window.AudioContext||window.webkitAudioContext)();function growl(freq,start,dur,vol){var o=ctx.createOscillator();var g=ctx.createGain();o.connect(g);g.connect(ctx.destination);o.type='sawtooth';o.frequency.setValueAtTime(freq,ctx.currentTime+start);o.frequency.exponentialRampToValueAtTime(freq*0.4,ctx.currentTime+start+dur);g.gain.setValueAtTime(0,ctx.currentTime+start);g.gain.linearRampToValueAtTime(vol,ctx.currentTime+start+0.05);g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+start+dur);o.start(ctx.currentTime+start);o.stop(ctx.currentTime+start+dur);}growl(180,0.0,0.6,0.3);growl(120,0.2,0.5,0.2);growl(90,0.5,0.8,0.25);}catch(e){}})();</script>""", unsafe_allow_html=True)
            S,I,R = run_sir_model(population, infected_start, beta, gamma, days, quarantine)
            stats = get_summary_stats(S, I, R, population)
            R0    = round(beta*(1-quarantine)/gamma, 2)
            st.session_state["last_run"] = (S,I,R,stats,R0,population,beta,gamma,quarantine,days)
        else:
            S,I,R,stats,R0,population,beta,gamma,quarantine,days = st.session_state["last_run"]

        sr = stats["survival_rate"]
        csr = "green" if sr>50 else ("amber" if sr>25 else "red")
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="label">{t("m_survivors",lang)}</div><div class="value {csr}">{stats['survivors']:,}</div><div class="sub">{sr}%</div></div>
            <div class="metric-card"><div class="label">{t("m_peak_zombies",lang)}</div><div class="value red">{stats['peak_zombies']:,}</div><div class="sub">{t("m_day",lang)} {stats['peak_day']}</div></div>
            <div class="metric-card"><div class="label">{t("m_zombified",lang)}</div><div class="value amber">{stats['total_zombified']:,}</div><div class="sub">{round(100-sr,1)}%</div></div>
            <div class="metric-card"><div class="label">{t("m_r0",lang)}</div><div class="value {'red' if R0>1 else 'green'}">{R0}</div><div class="sub">{'⚠️ '+t("m_growing",lang) if R0>1 else '✅ '+t("m_fading",lang)}</div></div>
        </div>""", unsafe_allow_html=True)

        if R0>1: st.markdown(f'<div class="banner banner-red">⚠️ <b>R₀={R0}</b> — {t("r0_warn",lang,r=R0)}</div>', unsafe_allow_html=True)
        else:    st.markdown(f'<div class="banner banner-green">✅ <b>R₀={R0}</b> — {t("r0_good",lang)}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">{t("chart_title",lang)}</div>', unsafe_allow_html=True)
        dr = list(range(days))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dr,y=S.tolist(),mode="lines",name=t("legend_s",lang),line=dict(color="#44ff88",width=2.5)))
        fig.add_trace(go.Scatter(x=dr,y=I.tolist(),mode="lines",name=t("legend_i",lang),line=dict(color="#ff3333",width=2.5),fill="tozeroy",fillcolor="rgba(255,51,51,0.07)"))
        fig.add_trace(go.Scatter(x=dr,y=R.tolist(),mode="lines",name=t("legend_r",lang),line=dict(color="#4488ff",width=2.5)))
        fig.add_vline(x=stats["peak_day"],line_dash="dash",line_color="#ff6666",annotation_text=f"{t('peak_label',lang)} {stats['peak_day']}",annotation_font_color="#ff6666")
        fig.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),
            xaxis=dict(title=t("chart_days",lang),gridcolor="#161616",color="#666"),
            yaxis=dict(title=t("chart_count",lang),gridcolor="#161616",color="#666"),
            legend=dict(orientation="h",y=1.08,bgcolor="rgba(0,0,0,0)"),hovermode="x unified",height=400,margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<div class="banner banner-blue">{t("chart_note",lang)}</div>', unsafe_allow_html=True)

        Sn,In,Rn = run_sir_model(population,infected_start,beta,gamma,days,0.0)
        stn = get_summary_stats(Sn,In,Rn,population)
        st.markdown(f'<div class="section-header">{t("quarantine_hdr",lang)}</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dr,y=In.tolist(),mode="lines",name=t("no_quarantine",lang),line=dict(color="#ff3333",width=2,dash="dot")))
        fig2.add_trace(go.Scatter(x=dr,y=I.tolist(),mode="lines",name=f"{t('with_quarantine',lang)} {int(quarantine*100)}%",line=dict(color="#44ff88",width=2.5)))
        fig2.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),
            xaxis=dict(title=t("chart_days",lang),gridcolor="#161616",color="#666"),
            yaxis=dict(title="Zombies",gridcolor="#161616",color="#666"),
            legend=dict(orientation="h",y=1.08,bgcolor="rgba(0,0,0,0)"),hovermode="x unified",height=280,margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig2, use_container_width=True)
        saved = stn["total_zombified"] - stats["total_zombified"]
        if saved>0: st.markdown(f'<div class="banner banner-blue">{t("saved",lang,n=f"{saved:,}")}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">{t("rules_hdr",lang)}</div>', unsafe_allow_html=True)
        for r in get_survival_rules(stats, beta, gamma, quarantine):
            st.markdown(f'<div class="rule-card"><div class="rule-title">{r["emoji"]} Rule #{r["number"]}: {r["title"]}</div><div class="rule-text">{r["reason"]}</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">{t("result_hdr",lang)}</div>', unsafe_allow_html=True)
        if sr>50:   st.markdown(f'<div class="banner banner-green">{t("win",lang)}</div>', unsafe_allow_html=True)
        elif sr>20: st.markdown(f'<div class="banner banner-yellow">{t("mid",lang)}</div>', unsafe_allow_html=True)
        else:       st.markdown(f'<div class="banner banner-red">{t("lose",lang)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;padding:4rem 1rem;"><div style="font-size:6rem;">🧟</div><h3 style="color:#555;font-family:Creepster,cursive;font-size:2rem;">{t("welcome",lang)}</h3></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — RANDOM EVENTS
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-header">{t("events_hdr",lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#555;font-size:.9rem;margin-bottom:1.5rem;">{t("events_desc",lang)}</p>', unsafe_allow_html=True)

    ec1,ec2 = st.columns(2)
    with ec1:
        ev_pop  = st.slider(t("sl_population",lang), 100_000, 5_000_000, 1_000_000, 100_000, key="ev_pop")
        ev_beta = st.slider(t("sl_beta",lang), 0.05, 1.0, 0.35, 0.01, key="ev_beta")
    with ec2:
        ev_gamma = st.slider(t("sl_gamma",lang), 0.01, 0.5, 0.10, 0.01, key="ev_gamma")
        ev_quar  = st.slider(t("sl_quarantine",lang), 0.0, 0.9, 0.3, 0.05, key="ev_quar")

    if st.button(t("events_btn",lang), use_container_width=True):
        event = random.choice(RANDOM_EVENTS)
        nb = min(1.0, ev_beta*event["beta_mult"])
        ng = min(0.5, ev_gamma*event["gamma_mult"])
        Sb,Ib,Rb = run_sir_model(ev_pop,10,ev_beta,ev_gamma,180,ev_quar)
        Sa,Ia,Ra = run_sir_model(ev_pop,10,nb,ng,180,ev_quar)
        stb = get_summary_stats(Sb,Ib,Rb,ev_pop)
        sta = get_summary_stats(Sa,Ia,Ra,ev_pop)
        st.session_state["events_log"].append({"event":event,"before":stb,"after":sta,"Ib":Ib.tolist(),"Ia":Ia.tolist(),"Sb":Sb.tolist(),"Sa":Sa.tolist()})

    if st.session_state["events_log"]:
        lt = st.session_state["events_log"][-1]
        ev = lt["event"]
        st.markdown(f'<div class="event-card"><div class="event-title">{ev["emoji"]} {ev["title"]}</div><div class="event-text">{ev["desc"]}</div></div>', unsafe_allow_html=True)

        diff = lt["after"]["survival_rate"] - lt["before"]["survival_rate"]
        dc   = "#44ff88" if diff>0 else "#ff4444"
        ds   = "+" if diff>0 else ""
        st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0;">
            <div class="metric-card"><div class="label">{t('events_before',lang)}</div><div class="value amber">{lt['before']['survival_rate']}%</div><div class="sub">{t('survived_lbl',lang)}</div></div>
            <div class="metric-card"><div class="label">{t('events_after',lang)}</div><div class="value" style="color:{dc};">{lt['after']['survival_rate']}%</div><div class="sub">({ds}{diff:.1f}%)</div></div>
        </div>""", unsafe_allow_html=True)

        dr = list(range(180))
        fev = go.Figure()
        fev.add_trace(go.Scatter(x=dr,y=lt["Ib"],mode="lines",name=f"🧟 {t('chart_days',lang)} ДО",line=dict(color="#ff6666",width=2,dash="dot")))
        fev.add_trace(go.Scatter(x=dr,y=lt["Ia"],mode="lines",name=f"🧟 Зомби ПОСЛЕ ({ev['emoji']})",line=dict(color="#ffaa44",width=2.5)))
        fev.add_trace(go.Scatter(x=dr,y=lt["Sb"],mode="lines",name="😊 Люди ДО",line=dict(color="#44aa66",width=1.5,dash="dot")))
        fev.add_trace(go.Scatter(x=dr,y=lt["Sa"],mode="lines",name="😊 Люди ПОСЛЕ",line=dict(color="#44ff88",width=2.5)))
        fev.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),
            xaxis=dict(title="Дни",gridcolor="#161616",color="#666"),yaxis=dict(title="Количество",gridcolor="#161616",color="#666"),
            legend=dict(orientation="h",y=1.12,bgcolor="rgba(0,0,0,0)"),hovermode="x unified",height=360,margin=dict(l=0,r=0,t=50,b=0))
        st.plotly_chart(fev, use_container_width=True)

        if len(st.session_state["events_log"])>1:
            st.markdown(f'<div class="section-header">{t("events_history",lang)}</div>', unsafe_allow_html=True)
            for i,en in enumerate(reversed(st.session_state["events_log"][-5:])):
                d  = en["after"]["survival_rate"]-en["before"]["survival_rate"]
                sg = "+" if d>0 else ""
                cl = "#44ff88" if d>0 else "#ff4444"
                st.markdown(f'<div class="event-card" style="opacity:{1-i*0.15:.2f};"><div class="event-title">{en["event"]["emoji"]} {en["event"]["title"]}<span style="float:right;color:{cl};font-family:Share Tech Mono;">{sg}{d:.1f}%</span></div><div class="event-text">{en["event"]["desc"]}</div></div>', unsafe_allow_html=True)

        if st.button(t("events_clear",lang), key="clear_ev"):
            st.session_state["events_log"] = []; st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — SCENARIOS + COMPARISON
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-header">{t("scenarios_hdr",lang)}</div>', unsafe_allow_html=True)
    sc1,sc2 = st.columns(2)
    with sc1:
        sc_pop  = st.slider(t("sl_population",lang), 100_000, 5_000_000, 1_000_000, 100_000, key="sc_pop")
        sc_beta = st.slider(t("sl_beta",lang), 0.05, 1.0, 0.35, 0.01, key="sc_beta")
    with sc2:
        sc_gamma = st.slider(t("sl_gamma",lang), 0.01, 0.5, 0.10, 0.01, key="sc_gamma")

    if st.button(t("sc_btn",lang), use_container_width=True, key="sc_btn") or "sc_done" in st.session_state:
        if st.session_state.get("sc_btn_pressed") or "sc_done" not in st.session_state:
            st.session_state["sc_done"] = (sc_pop, sc_beta, sc_gamma)
        sp, sb, sg = st.session_state["sc_done"]

        scenarios = [
            {"name":t("sc_no_measures",lang),"emoji":"💀","q":0.0,"b":sb,"color":"#ff3333","border":"#550000","desc":t("sc_desc_none",lang)},
            {"name":t("sc_quarantine",lang),"emoji":"🛡️","q":0.5,"b":sb,"color":"#ffaa44","border":"#554400","desc":t("sc_desc_quar",lang)},
            {"name":t("sc_vaccine",lang),"emoji":"💉","q":0.0,"b":sb*0.3,"color":"#44ff88","border":"#005522","desc":t("sc_desc_vacc",lang)},
        ]
        results = []
        for sc in scenarios:
            S_,I_,R_ = run_sir_model(sp,10,sc["b"],sg,180,sc["q"])
            results.append({"sc":sc,"stats":get_summary_stats(S_,I_,R_,sp),"I":I_})

        html = '<div class="scenario-grid">'
        for r in results:
            s=r["sc"]; st_=r["stats"]
            html += f'<div class="scenario-card" style="border-left:4px solid {s["color"]};"><div style="font-size:2.5rem;margin-bottom:.5rem;">{s["emoji"]}</div><div class="sc-title" style="color:{s["color"]};">{s["name"]}</div><div class="sc-survival" style="color:{s["color"]};">{st_["survival_rate"]}%</div><div style="color:#666;font-size:.8rem;">{t("sc_survived",lang)} · {t("sc_peak_day",lang)} {st_["peak_day"]}</div><div class="sc-desc" style="margin-top:.5rem;">{s["desc"]}</div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

        fsc = go.Figure()
        dr  = list(range(180))
        for r,c in zip(results,["#ff3333","#ffaa44","#44ff88"]):
            fsc.add_trace(go.Scatter(x=dr,y=r["I"].tolist(),mode="lines",name=f'{r["sc"]["emoji"]} {r["sc"]["name"]}',line=dict(color=c,width=2.5)))
        fsc.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),
            xaxis=dict(title=t("chart_days",lang),gridcolor="#161616",color="#666"),yaxis=dict(title=t("chart_zombies",lang),gridcolor="#161616",color="#666"),
            legend=dict(orientation="h",y=1.1,bgcolor="rgba(0,0,0,0)"),hovermode="x unified",height=360,margin=dict(l=0,r=0,t=50,b=0))
        st.plotly_chart(fsc, use_container_width=True)

    st.markdown(f'<div class="section-header">{t("compare_hdr",lang)}</div>', unsafe_allow_html=True)
    clist = list(df["country"].values)
    cc1,cc2 = st.columns(2)
    with cc1: ca = st.selectbox(t("country1",lang), clist, index=min(8,len(clist)-1), key="cmp_a")
    with cc2: cb = st.selectbox(t("country2",lang), clist, index=min(1,len(clist)-1), key="cmp_b")
    cd = st.slider(t("sl_days",lang), 30, 365, 180, 10, key="cmp_days")

    if st.button(t("compare_btn",lang), use_container_width=True) or "cmp_done" in st.session_state:
        if "cmp_done" not in st.session_state or st.session_state.get("cmp_btn_new"):
            st.session_state["cmp_done"] = (ca, cb, cd)
        xa,xb,xd = st.session_state["cmp_done"]
        ra = df[df["country"]==xa].iloc[0]; rb = df[df["country"]==xb].iloc[0]
        Sa,Ia,Ra = run_sir_model(int(ra["population"]),10,float(ra["peak_beta"]),float(ra["gamma"]),xd,0.3)
        Sb,Ib,Rb = run_sir_model(int(rb["population"]),10,float(rb["peak_beta"]),float(rb["gamma"]),xd,0.3)
        sta = get_summary_sets(Sa,Ia,Ra,int(ra["population"])) if False else get_summary_stats(Sa,Ia,Ra,int(ra["population"]))
        stb = get_summary_stats(Sb,Ib,Rb,int(rb["population"]))

        mc1,mc2 = st.columns(2)
        for col,cn,st_,row in [(mc1,xa,sta,ra),(mc2,xb,stb,rb)]:
            with col:
                c="#44ff88" if st_["survival_rate"]>50 else ("#ffaa44" if st_["survival_rate"]>25 else "#ff4444")
                st.markdown(f'<div class="metric-card" style="margin-bottom:.75rem;"><div class="label">🌍 {cn}</div><div class="value" style="color:{c};">{st_["survival_rate"]}%</div><div class="sub">{t("sc_survived",lang)} · R₀={row["R0"]:.2f}</div></div>', unsafe_allow_html=True)

        dr = list(range(xd))
        fcmp = go.Figure()
        fcmp.add_trace(go.Scatter(x=dr,y=(Ia/int(ra["population"])*100).tolist(),mode="lines",name=f"🧟 {xa}",line=dict(color="#ff5555",width=2.5)))
        fcmp.add_trace(go.Scatter(x=dr,y=(Ib/int(rb["population"])*100).tolist(),mode="lines",name=f"🧟 {xb}",line=dict(color="#4488ff",width=2.5,dash="dash")))
        fcmp.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),
            xaxis=dict(title=t("chart_days",lang),gridcolor="#161616",color="#666"),yaxis=dict(title=t("infected_pct",lang),gridcolor="#161616",color="#666"),
            legend=dict(orientation="h",y=1.1,bgcolor="rgba(0,0,0,0)"),hovermode="x unified",height=340,margin=dict(l=0,r=0,t=50,b=0))
        st.plotly_chart(fcmp, use_container_width=True)
        winner = xa if sta["survival_rate"]>stb["survival_rate"] else xb
        st.markdown(f'<div class="banner banner-green">🏆 Побеждает <b>{winner}</b> — больше выживших при одинаковом карантине 30%.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHARACTER + LEADERBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="section-header">{t("char_hdr",lang)}</div>', unsafe_allow_html=True)

    cl,cr = st.columns([1,1], gap="large")
    with cl:
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin-bottom:.2rem;">{t("char_name_lbl",lang)}</p>', unsafe_allow_html=True)
        char_name = st.text_input("",placeholder=t("char_name_ph",lang),key="char_name",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">{t("char_city_lbl",lang)}</p>', unsafe_allow_html=True)
        char_city = st.selectbox("",["Актау","Алматы","Астана","Шымкент","Атырау","Павлодар","Семей","Тараз","Другой"],key="char_city",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">{t("char_prof_lbl",lang)}</p>', unsafe_allow_html=True)
        char_profession = st.selectbox("",["Военный / Полицейский","Врач / Медработник","Фермер / Охотник","Спортсмен / Тренер","Инженер / IT специалист","Учитель / Учёный","Менеджер / Офисный работник","Блогер / Инфлюенсер 😄"],key="char_prof",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">{t("char_age_lbl",lang)}</p>', unsafe_allow_html=True)
        char_age = st.slider("",10,70,25,key="char_age",label_visibility="collapsed")

        st.markdown('<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">🎯 СПЕЦ-НАВЫКИ</p>', unsafe_allow_html=True)
        skills = st.multiselect("", [
            "🏹 Стрельба из лука",
            "💊 Медицина и первая помощь",
            "🚗 Экстремальное вождение",
        ], key="skills", label_visibility="collapsed")

        st.markdown('<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">🎒 ИНВЕНТАРЬ (макс. 3 предмета)</p>', unsafe_allow_html=True)
        inventory = st.multiselect("", [
            "🩹 Аптечка (+10%)",
            "🔫 Дробовик (+15%)",
            "🥫 Консервы (+8%)",
            "🎸 Гитара (моральный дух +5%)",
        ], max_selections=3, key="inventory", label_visibility="collapsed")

    with cr:
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin-bottom:.2rem;">{t("char_cardio_lbl",lang)}</p>', unsafe_allow_html=True)
        cardio = st.slider("",1,10,5,key="cardio",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">{t("char_food_lbl",lang)}</p>', unsafe_allow_html=True)
        food_days = st.slider("",0,30,3,key="food",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">{t("char_rules_lbl",lang)}</p>', unsafe_allow_html=True)
        knows_rules = st.slider("",0,10,3,key="knows",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .2rem;">{t("char_group_lbl",lang)}</p>', unsafe_allow_html=True)
        group = st.slider("",1,10,1,key="group",label_visibility="collapsed")
        st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .5rem;">{t("char_extra_lbl",lang)}</p>', unsafe_allow_html=True)
        double_tap = st.toggle(t("char_dtap",lang))
        has_weapon = st.toggle(t("char_weapon",lang))

    st.markdown("<br>", unsafe_allow_html=True)
    calc_btn = st.button(t("char_btn",lang), use_container_width=True)

    if calc_btn and char_name:
        city_danger  = {"Алматы":0.95,"Астана":0.90,"Шымкент":0.85,"Атырау":0.65,"Павлодар":0.70,"Семей":0.72,"Тараз":0.75,"Актау":0.60,"Другой":0.55}
        prof_bonus   = {"Военный / Полицейский":25,"Врач / Медработник":18,"Фермер / Охотник":20,"Спортсмен / Тренер":22,"Инженер / IT специалист":12,"Учитель / Учёный":10,"Менеджер / Офисный работник":5,"Блогер / Инфлюенсер 😄":2}
        nicknames_pool = {
            "Военный / Полицейский":      ["Командир","Спецназ","Страж","Альфа","Железный кулак","Снайпер","Капитан","Шериф"],
            "Врач / Медработник":         ["Доктор","Санитар","Целитель","Медик","Скальпель","Антидот","Витамин","Подорожник"],
            "Фермер / Охотник":           ["Следопыт","Волк","Охотник за головами","Дикарь","Лесник","Выживший","Гроза Теплиц","Ковбой"],
            "Спортсмен / Тренер":         ["Марафонец","Ракета","Железный","Спринтер","Непобедимый","Молния","Бегун","Физрук","Фитоняшка","Киборг"],
            "Инженер / IT специалист":    ["Хакер","Оракул","Кибер","Баг","Системщик","Тыжпрограммист","Ошибка 404","Дата-Сатанист"],
            "Учитель / Учёный":           ["Профессор","Мудрец","Архивариус","Аналитик","Стратег","Энциклопедия","Теоретик","Ботаник-Киллер"],
            "Менеджер / Офисный работник":["Планировщик","Офисный Рэмбо","Менеджер Судьбы","Отчётник","Дедлайн","Сын Маминой Подруги","Планктон","Клерк-невидимка"],
            "Блогер / Инфлюенсер 😄":    ["Жертва","Контент","Лайкнул и умер","Сторис","Последний пост","Дизлайк","Аутсайдер","ТикТок-Воин","Инфоцыган","0 просмотров"],
        }
        # Веса редкости — легендарные клички выпадают редко 🎲
        nicknames_weights = {
            "Военный / Полицейский":      [10, 10, 10, 8, 6, 8, 10, 2],           # Шериф — редкий
            "Врач / Медработник":         [10, 10, 10, 10, 8, 8, 3, 1],            # Подорожник — легендарный
            "Фермер / Охотник":           [10, 8, 6, 8, 10, 10, 2, 3],             # Гроза Теплиц — легендарный
            "Спортсмен / Тренер":         [10, 8, 8, 10, 6, 10, 10, 5, 3, 2],     # Киборг — легендарный
            "Инженер / IT специалист":    [8, 8, 10, 10, 10, 5, 3, 1],             # Дата-Сатанист — легендарный
            "Учитель / Учёный":           [10, 10, 6, 10, 8, 8, 10, 2],            # Ботаник-Киллер — легендарный
            "Менеджер / Офисный работник":[10, 8, 8, 10, 10, 1, 5, 3],             # Сын Маминой Подруги — легендарный
            "Блогер / Инфлюенсер 😄":    [10, 10, 6, 10, 8, 8, 10, 5, 2, 1],     # 0 просмотров — легендарный
        }
        avatars_pool = {
            "Военный / Полицейский":      ["🪖","🔫","🛡️","⚔️","🎖️","🪃","🗡️"],
            "Врач / Медработник":         ["🩺","💉","🏥","🧬","🩻","💊","🧪"],
            "Фермер / Охотник":           ["🪓","🏹","🌾","🐺","🦅","🔪","🪤"],
            "Спортсмен / Тренер":         ["🏃","🏋️","⚡","🥊","🏆","🎽","👟"],
            "Инженер / IT специалист":    ["💻","🔧","🤖","📡","⚙️","🖥️","🔌"],
            "Учитель / Учёный":           ["🔬","📚","🧪","🔭","🎓","📐","🗺️"],
            "Менеджер / Офисный работник":["💼","📊","🗂️","☕","📎","🖨️","📋"],
            "Блогер / Инфлюенсер 😄":    ["📱","📸","💅","🤳","☠️","🪦","📉"],
        }

        key = f"char_{char_name}_{char_profession}"
        if key not in st.session_state:
            w = nicknames_weights.get(char_profession)
            st.session_state[key] = {
                "nickname": random.choices(nicknames_pool[char_profession], weights=w)[0],
                "avatar":   random.choice(avatars_pool[char_profession]),
            }
        nickname = st.session_state[key]["nickname"]
        avatar   = st.session_state[key]["avatar"]

        # ── Расчёт скора ──
        score  = cardio*3.5 + prof_bonus[char_profession] + (1-city_danger[char_city])*20
        score += (8 if double_tap else 0) + (12 if has_weapon else 0)
        score += food_days*0.8 + knows_rules*1.5 + min(group,5)*1.2
        score -= max(0, char_age-40)*0.8

        # Инвентарь
        inv_bonus = {"🩹 Аптечка (+10%)":10,"🔫 Дробовик (+15%)":15,"🥫 Консервы (+8%)":8,"🎸 Гитара (моральный дух +5%)":5}
        for item in inventory:
            score += inv_bonus.get(item, 0)

        # Спец-навыки
        mimicry_activated = False
        if "🏹 Стрельба из лука" in skills:      score += 12
        if "💊 Медицина и первая помощь" in skills: score += 15
        if "🚗 Экстремальное вождение" in skills:   score += 10
        if "🎭 Метод Мюррея (мимикрия под зомби)" in skills:
            if random.random() < 0.05:  # 5% шанс обнуления
                score = 0
                mimicry_activated = True
            else:
                score += 25

        score += random.uniform(-3,3)
        score  = max(2, min(98, round(score)))

        if score>=70: bc="linear-gradient(90deg,#00aa44,#44ff88)"; verdict=t("verdict_win",lang); vc="#44ff88"; vs="✅"
        elif score>=45: bc="linear-gradient(90deg,#aa6600,#ffaa44)"; verdict=t("verdict_mid",lang); vc="#ffaa44"; vs="⚠️"
        else: bc="linear-gradient(90deg,#880000,#ff3333)"; verdict=t("verdict_lose",lang); vc="#ff4444"; vs="💀"

        if mimicry_activated:
            st.markdown('<div class="banner banner-red">💥 МИМИКРИЯ ПРОВАЛИЛАСЬ! Свои же открыли огонь — шанс выживания обнулён! Это и есть тот самый 5%...</div>', unsafe_allow_html=True)

        # Звук
        sound_url = "https://www.myinstants.com/media/sounds/zombie-sound.mp3" if score < 45 else "https://www.myinstants.com/media/sounds/level-up.mp3"
        st.markdown(f'<audio autoplay><source src="{sound_url}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

        # Карточка персонажа
        st.markdown(f"""
        <style>
        @keyframes revealCard {{
            0%   {{ opacity:0; transform:scale(0.8) translateY(30px); }}
            60%  {{ transform:scale(1.03) translateY(-5px); }}
            100% {{ opacity:1; transform:scale(1) translateY(0); }}
        }}
        @keyframes barGrow {{ from {{ width: 0%; }} to {{ width: {score}%; }} }}
        .char-card-anim {{ background:linear-gradient(135deg,#0f0000,#000f00); border:1px solid #330000; border-radius:12px; padding:1.5rem; text-align:center; animation: revealCard 0.7s cubic-bezier(0.34,1.56,0.64,1) forwards; }}
        .bar-anim {{ height:100%; border-radius:20px; background:{bc}; display:flex; align-items:center; justify-content:flex-end; padding-right:8px; font-size:.75rem; font-weight:700; font-family:'Share Tech Mono',monospace; color:#000; animation: barGrow 1.2s ease-out 0.5s both; }}
        </style>
        <div class="char-card-anim">
            <div style="font-size:4.5rem;margin-bottom:.5rem;">{avatar}</div>
            <div style="font-family:'Creepster',cursive;font-size:2.2rem;color:#ff4444;letter-spacing:2px;">{char_name}</div>
            <div style="font-family:'Share Tech Mono',monospace;color:#888;font-size:.9rem;margin-top:.25rem;">
                {t("nickname_lbl",lang)}: «{nickname}» · {char_city} · {char_age} {t("age_lbl",lang)}
            </div>
            <div style="font-size:.78rem;color:#555;margin:.8rem 0 .3rem;font-family:'Share Tech Mono';letter-spacing:1px;">{t("survival_lbl",lang)}</div>
            <div style="background:#1a1a1a;border-radius:20px;height:22px;overflow:hidden;border:1px solid #2a2a2a;margin:.5rem 0;">
                <div class="bar-anim">{score}%</div>
            </div>
            <div style="font-size:1.15rem;font-weight:600;margin-top:.75rem;color:{vc};">{verdict}</div>
        </div>""", unsafe_allow_html=True)

        # ── Radar Chart ──
        st.markdown('<div class="section-header">📊 Radar Chart — Профиль выжившего</div>', unsafe_allow_html=True)

        city_safety = round((1 - city_danger.get(char_city, 0.6)) * 10, 1)
        skill_score = round(len(skills) * 2.5, 1)
        inv_score   = round(len(inventory) * 3, 1)
        age_score   = round(max(0, 10 - max(0, char_age-40)*0.3), 1)

        categories = ['Кардио','Безопасность\nгорода','Навыки','Инвентарь','Запас еды','Знание правил','Возраст']
        values     = [cardio, city_safety, skill_score, inv_score, min(food_days/3,10), knows_rules, age_score]

        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(255,50,50,0.15)',
            line=dict(color='#ff4444', width=2),
            marker=dict(color='#ff4444', size=6),
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='#111',
                radialaxis=dict(visible=True, range=[0,10], gridcolor='#333', color='#555', tickfont=dict(size=9, color='#555')),
                angularaxis=dict(gridcolor='#333', color='#888', tickfont=dict(size=10, color='#aaa')),
            ),
            paper_bgcolor='#080808', plot_bgcolor='#080808',
            font=dict(color='#ccc', family='Oswald'),
            showlegend=False, height=380,
            margin=dict(l=60, r=60, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # ── AI Insights — XAI объяснение ──
        st.markdown('<div class="section-header">🧠 AI Insights — Что повлияло на результат</div>', unsafe_allow_html=True)

        factors = {
            'Кардио': cardio * 3.5,
            'Профессия': prof_bonus[char_profession],
            'Безопасность города': (1-city_danger.get(char_city,0.6))*20,
            'Навыки': len(skills)*8,
            'Инвентарь': sum(inv_bonus.get(i,0) for i in inventory),
            'Запас еды': food_days*0.8,
            'Знание правил': knows_rules*1.5,
            'Оружие/Double Tap': (8 if double_tap else 0)+(12 if has_weapon else 0),
        }
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        top3 = [f for f,v in sorted_factors[:3] if v > 0]
        low3 = [f for f,v in sorted_factors[-3:] if v < 5]

        st.markdown(f"""
        <div style="background:#0a0a1a;border:1px solid #003355;border-left:4px solid #4488ff;border-radius:10px;padding:1.25rem;margin:.5rem 0;">
            <div style="color:#4488ff;font-weight:700;font-size:1rem;margin-bottom:.75rem;">🔍 Анализ персонажа: {char_name} «{nickname}»</div>
            <div style="color:#ccc;line-height:1.7;font-size:.92rem;">
                {'<br>'.join([f'✅ <b>{f}</b> — ключевой фактор выживания (вклад: +{v:.0f} очков)' for f,v in sorted_factors[:3] if v > 0])}
                <br><br>
                {'<br>'.join([f'⚠️ <b>{f}</b> — слабое место, снижает шансы' for f,v in sorted_factors[-2:] if v < 5]) if low3 else ''}
                <br><br>
                📊 <b>Итоговый вклад по факторам:</b> {' | '.join([f'{f}: {v:.0f}пт' for f,v in sorted_factors[:5]])}
            </div>
        </div>""", unsafe_allow_html=True)

        # Добавляем в таблицу лидеров
        st.session_state["leaderboard"].append({"name":char_name,"city":char_city,"profession":char_profession,"score":score,"verdict":vs})
        st.session_state["leaderboard"].sort(key=lambda x:x["score"],reverse=True)
        st.success(t("added_lb",lang,n=char_name))

        # ── PDF Сертификат ──
        st.markdown('<div class="section-header">📄 Сертификат выжившего</div>', unsafe_allow_html=True)

        try:
            from fpdf import FPDF

            # Транслитерация для PDF (fpdf2 не поддерживает кириллицу без доп. шрифтов)
            def tr(text):
                import re
                text = re.sub(r'[^\u0000-\u024F\u0400-\u04FF ]', '', str(text))
                m = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y',
                     'к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f',
                     'х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
                     'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo','Ж':'Zh','З':'Z','И':'I','Й':'Y',
                     'К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F',
                     'Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Sch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu','Я':'Ya',
                     'қ':'q','ң':'ng','ғ':'gh','ү':'u','ұ':'u','і':'i','ә':'a','ө':'o','һ':'h',
                     'Қ':'Q','Ң':'Ng','Ғ':'Gh','Ү':'U','Ұ':'U','І':'I','Ә':'A','Ө':'O','Һ':'H',
                     '«':'"','»':'"','—':'-','–':'-'}
                return ''.join(m.get(c, c) for c in text).strip()

            class ZombieCert(FPDF):
                def header(self):
                    self.set_fill_color(6, 6, 6)
                    self.rect(0, 0, 210, 297, 'F')
                    self.set_draw_color(255, 34, 34)
                    self.set_line_width(2)
                    self.rect(8, 8, 194, 281)
                    self.set_line_width(0.5)
                    self.rect(11, 11, 188, 275)

            pdf = ZombieCert()

            # Подключаем DejaVuSans — поддерживает кириллицу
            import os
            font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
            font_bold_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans-Bold.ttf')
            font_italic_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans-Oblique.ttf')
            use_cyrillic = os.path.exists(font_path)

            if use_cyrillic:
                pdf.add_font('DejaVu', '', font_path, uni=True)
                pdf.add_font('DejaVu', 'B', font_bold_path, uni=True)
                pdf.add_font('DejaVu', 'I', font_italic_path, uni=True)
                fn = 'DejaVu'
            else:
                fn = 'Helvetica'

            def sf(style='', size=11):
                pdf.set_font(fn, style, size)

            # Локализованные тексты для PDF
            pdf_labels = {
                'RU': {
                    'cert': 'СЕРТИФИКАТ ВЫЖИВШЕГО',
                    'file': f'ЛИЧНОЕ ДЕЛО № ZAS-2026-{random.randint(1000,9999)}',
                    'name': 'ИМЯ:', 'nick': 'ПРОЗВИЩЕ:', 'city': 'ГОРОД:',
                    'prof': 'ПРОФЕССИЯ:', 'age': 'ВОЗРАСТ:', 'years': 'лет',
                    'skills': 'СПЕЦ-НАВЫКИ:', 'inv': 'ИНВЕНТАРЬ:',
                    'chance': 'ШАНС ВЫЖИВАНИЯ',
                    'v1': 'ВЫЖИВЕШЬ!', 'v2': 'ШАНСЫ ЕСТЬ. ДЕРЖИСЬ.',
                    'v3': 'ПОЧТИ БЕЗНАДЁЖНО. КАРДИО.',
                    'footer': f'Zombie Apocalypse Simulator | Data Science & AI | Максат Омаров | 2026',
                },
                'EN': {
                    'cert': 'SURVIVOR CERTIFICATE',
                    'file': f'PERSONAL FILE No. ZAS-2026-{random.randint(1000,9999)}',
                    'name': 'NAME:', 'nick': 'NICKNAME:', 'city': 'CITY:',
                    'prof': 'PROFESSION:', 'age': 'AGE:', 'years': 'y.o.',
                    'skills': 'SPECIAL SKILLS:', 'inv': 'INVENTORY:',
                    'chance': 'SURVIVAL CHANCE',
                    'v1': 'YOU WILL SURVIVE!', 'v2': 'CHANCES EXIST. HOLD ON.',
                    'v3': 'ALMOST HOPELESS. DO CARDIO.',
                    'footer': f'Zombie Apocalypse Simulator | Data Science & AI | Maksat Omarov | 2026',
                },
                'KZ': {
                    'cert': 'ТІРШІЛІК ЕТКЕН СЕРТИФИКАТЫ',
                    'file': f'ЖЕКЕ ІС № ZAS-2026-{random.randint(1000,9999)}',
                    'name': 'АТЫ:', 'nick': 'ЛАҚАП АТЫ:', 'city': 'ҚАЛА:',
                    'prof': 'МАМАНДЫҚ:', 'age': 'ЖАС:', 'years': 'жас',
                    'skills': 'СПЕЦ-ДАҒДЫЛАР:', 'inv': 'ИНВЕНТАРЬ:',
                    'chance': 'ТІРШІЛІК ЕТУ МҮМКІНДІГІ',
                    'v1': 'ТІРШІЛІК ЕТЕСІҢ!', 'v2': 'МҮМКІНДІК БАР. ҰСТА.',
                    'v3': 'ҮМІТСІЗ ДЕРЛІК. КАРДИО.',
                    'footer': f'Zombie Apocalypse Simulator | Data Science & AI | Максат Омаров | 2026',
                },
            }
            L = pdf_labels.get(lang, pdf_labels['RU'])

            pdf.add_page()

            sf('B', 26)
            pdf.set_text_color(255, 34, 34)
            pdf.set_y(30)
            pdf.cell(0, 12, 'ZOMBIE APOCALYPSE SIMULATOR', align='C', ln=True)
            sf('B', 15)
            pdf.set_text_color(200, 200, 200)
            pdf.cell(0, 8, L['cert'], align='C', ln=True)

            pdf.set_draw_color(255, 34, 34)
            pdf.set_line_width(0.5)
            pdf.line(30, pdf.get_y()+4, 180, pdf.get_y()+4)
            pdf.ln(12)

            sf('B', 11)
            pdf.set_text_color(255, 100, 100)
            pdf.cell(0, 7, L['file'], align='C', ln=True)
            pdf.ln(8)

            name_val = char_name if use_cyrillic else tr(char_name)
            nick_val = f'"{nickname}"' if use_cyrillic else tr(f'"{nickname}"')
            city_val = char_city if use_cyrillic else tr(char_city)
            prof_val = char_profession if use_cyrillic else tr(char_profession)

            data_rows = [
                (L['name'], name_val),
                (L['nick'], nick_val),
                (L['city'], city_val),
                (L['prof'], prof_val),
                (L['age'], f'{char_age} {L["years"]}'),
            ]
            for label, value in data_rows:
                sf('B', 11)
                pdf.set_text_color(255, 100, 100)
                pdf.cell(55, 9, label)
                sf('', 11)
                pdf.set_text_color(220, 220, 220)
                pdf.cell(0, 9, value, ln=True)

            pdf.ln(5)
            if skills:
                sf('B', 11)
                pdf.set_text_color(255, 100, 100)
                pdf.cell(0, 9, L['skills'], ln=True)
                sf('', 10)
                pdf.set_text_color(180, 180, 180)
                for s in skills:
                    s_val = s if use_cyrillic else tr(s)
                    pdf.cell(0, 7, f'  - {s_val}', ln=True)

            if inventory:
                pdf.ln(2)
                sf('B', 11)
                pdf.set_text_color(255, 100, 100)
                pdf.cell(0, 9, L['inv'], ln=True)
                sf('', 10)
                pdf.set_text_color(180, 180, 180)
                for item in inventory:
                    item_val = item if use_cyrillic else tr(item)
                    pdf.cell(0, 7, f'  - {item_val}', ln=True)

            pdf.ln(8)
            pdf.set_draw_color(255, 34, 34)
            pdf.line(30, pdf.get_y(), 180, pdf.get_y())
            pdf.ln(8)
            sf('B', 20)
            color = (68,255,136) if score>=70 else ((255,170,68) if score>=45 else (255,68,68))
            pdf.set_text_color(*color)
            pdf.cell(0, 12, f'{L["chance"]}: {score}%', align='C', ln=True)
            sf('B', 14)
            verdict_pdf = L['v1'] if score>=70 else (L['v2'] if score>=45 else L['v3'])
            pdf.cell(0, 8, verdict_pdf, align='C', ln=True)

            pdf.ln(10)
            sf('I', 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, L['footer'], align='C', ln=True)

            import io
            pdf_output = pdf.output()
            if isinstance(pdf_output, bytearray):
                pdf_bytes = bytes(pdf_output)
            elif isinstance(pdf_output, str):
                pdf_bytes = pdf_output.encode('latin-1')
            else:
                pdf_bytes = pdf_output

            st.download_button(
                label="📥 СКАЧАТЬ СЕРТИФИКАТ (PDF)",
                data=pdf_bytes,
                file_name=f"zombie_cert_{tr(char_name)}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except ImportError:
            st.markdown('<div class="banner banner-yellow">⚠️ Установи fpdf2: добавь <b>!pip install fpdf2 -q</b> в ячейку 1 Colab и перезапусти</div>', unsafe_allow_html=True)

        # Советы
        tips = []
        if cardio<5: tips.append(t("tip_cardio",lang))
        if not double_tap: tips.append(t("tip_dtap",lang))
        if not has_weapon: tips.append(t("tip_weapon",lang))
        if food_days<5:
            em,ti,tx = t("tip_food",lang)
            tips.append((em, ti, f"{food_days} {tx}"))
        if city_danger.get(char_city,0.6)>0.8:
            em,ti,tx = t("tip_city",lang)
            tips.append((em, ti, f"{char_city} {tx}"))
        if group==1: tips.append(t("tip_group",lang))
        if not tips: tips.append(t("tip_great",lang))
        st.markdown(f'<div class="section-header">{t("tips_hdr",lang)}</div>', unsafe_allow_html=True)
        for em,ti,tx in tips:
            st.markdown(f'<div class="rule-card"><div class="rule-title">{em} {ti}</div><div class="rule-text">{tx}</div></div>', unsafe_allow_html=True)

    elif calc_btn:
        st.markdown(f'<div class="banner banner-yellow">{t("char_no_name",lang)}</div>', unsafe_allow_html=True)

    # Leaderboard
    st.markdown(f'<div class="section-header">{t("lb_hdr",lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#555;font-size:.88rem;margin-bottom:1rem;">{t("lb_desc",lang)}</p>', unsafe_allow_html=True)
    medals = ["🥇","🥈","🥉"]; mclass = ["lb-gold","lb-silver","lb-bronze"]
    for i,en in enumerate(st.session_state["leaderboard"][:10]):
        rm = medals[i] if i<3 else f"#{i+1}"
        rc = mclass[i] if i<3 else "lb-other"
        sc = "#44ff88" if en["score"]>=70 else ("#ffaa44" if en["score"]>=45 else "#ff4444")
        st.markdown(f'<div class="lb-row"><div class="lb-rank {rc}">{rm}</div><div><div class="lb-name">{en["name"]} {en["verdict"]}</div><div class="lb-city">{en["city"]} · {en["profession"][:30]}</div></div><div class="lb-score" style="color:{sc};">{en["score"]}%</div></div>', unsafe_allow_html=True)
    if st.button(t("lb_clear",lang), key="clear_lb"):
        st.session_state["leaderboard"] = []; st.rerun()

    st.markdown(f'<div class="section-header">{t("kz_cities_hdr",lang)}</div>', unsafe_allow_html=True)
    kzc = [("Алматы","2.1 млн",t("kz_crit",lang),"#ff3333"),("Астана","1.4 млн",t("kz_high",lang),"#ff5555"),("Шымкент","1.2 млн","🟠 "+t("kz_high",lang),"#ff7733"),("Атырау","350к",t("kz_mid",lang),"#ffaa44"),("Павлодар","340к",t("kz_mid",lang),"#ffcc44"),("Актау","220к",t("kz_low",lang),"#44ff88")]
    st.markdown('<div class="kz-city-grid">'+''.join([f'<div class="kz-city-card"><div class="city-name">{c}</div><div style="color:#555;font-size:.78rem;margin-bottom:.3rem;">{p}</div><div style="font-family:Share Tech Mono;font-size:.85rem;color:{cl};">{d}</div></div>' for c,p,d,cl in kzc])+'</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="banner banner-blue">{t("aktau_safe",lang)}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — EDA
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(f'<div class="section-header">{t("data_hdr",lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="banner banner-blue">{t("data_source",lang)}</div>', unsafe_allow_html=True)

    # ── Объяснение расчёта β и γ ──
    formula_text = {
        "RU": """
        <div style="background:#0a0a1a;border:1px solid #003355;border-left:4px solid #4488ff;border-radius:10px;padding:1.25rem;margin-bottom:1rem;">
            <div style="color:#4488ff;font-weight:700;font-size:1rem;margin-bottom:.75rem;">🔬 Как рассчитаны β и γ из реальных данных COVID-19?</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;color:#ccc;font-size:.9rem;line-height:1.7;">
                <div>
                    <b style="color:#ff4444;">γ (гамма) — скорость устранения:</b><br>
                    <code style="background:#111;padding:.2rem .5rem;border-radius:4px;">γ = 1 / средняя_продолжительность_болезни</code><br>
                    Для COVID-19 средняя длительность ≈ 10-14 дней<br>
                    → γ = 1/12 ≈ <b>0.083</b><br><br>
                    Данные: ВОЗ, национальные минздравы
                </div>
                <div>
                    <b style="color:#ff4444;">β (бета) — скорость заражения:</b><br>
                    <code style="background:#111;padding:.2rem .5rem;border-radius:4px;">β = R₀ × γ</code><br>
                    R₀ берётся из научных публикаций по COVID-19<br>
                    Пример: R₀=2.5, γ=0.083 → β = <b>0.208</b><br><br>
                    Данные: Our World in Data, CDC, WHO
                </div>
            </div>
            <div style="margin-top:.75rem;color:#888;font-size:.82rem;">
                📌 При выборе страны в симуляторе автоматически загружаются эти параметры. 
                Например: <b>Казахстан</b> → β=0.35, γ=0.10, R₀=3.5 (на основе реальных данных вспышки 2020-2021)
            </div>
        </div>
        """,
        "EN": """
        <div style="background:#0a0a1a;border:1px solid #003355;border-left:4px solid #4488ff;border-radius:10px;padding:1.25rem;margin-bottom:1rem;">
            <div style="color:#4488ff;font-weight:700;font-size:1rem;margin-bottom:.75rem;">🔬 How are β and γ calculated from real COVID-19 data?</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;color:#ccc;font-size:.9rem;line-height:1.7;">
                <div>
                    <b style="color:#ff4444;">γ (gamma) — removal rate:</b><br>
                    <code style="background:#111;padding:.2rem .5rem;border-radius:4px;">γ = 1 / average_disease_duration</code><br>
                    For COVID-19 average duration ≈ 10-14 days<br>
                    → γ = 1/12 ≈ <b>0.083</b><br><br>
                    Source: WHO, national health ministries
                </div>
                <div>
                    <b style="color:#ff4444;">β (beta) — infection rate:</b><br>
                    <code style="background:#111;padding:.2rem .5rem;border-radius:4px;">β = R₀ × γ</code><br>
                    R₀ taken from scientific publications<br>
                    Example: R₀=2.5, γ=0.083 → β = <b>0.208</b><br><br>
                    Source: Our World in Data, CDC, WHO
                </div>
            </div>
            <div style="margin-top:.75rem;color:#888;font-size:.82rem;">
                📌 When selecting a country in the simulator, these parameters are loaded automatically from our dataset.
            </div>
        </div>
        """,
        "KZ": """
        <div style="background:#0a0a1a;border:1px solid #003355;border-left:4px solid #4488ff;border-radius:10px;padding:1.25rem;margin-bottom:1rem;">
            <div style="color:#4488ff;font-weight:700;font-size:1rem;margin-bottom:.75rem;">🔬 β және γ нақты COVID-19 деректерінен қалай есептеледі?</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;color:#ccc;font-size:.9rem;line-height:1.7;">
                <div>
                    <b style="color:#ff4444;">γ (гамма) — жою жылдамдығы:</b><br>
                    <code style="background:#111;padding:.2rem .5rem;border-radius:4px;">γ = 1 / орташа_ауру_ұзақтығы</code><br>
                    COVID-19 үшін орташа ұзақтық ≈ 10-14 күн<br>
                    → γ = 1/12 ≈ <b>0.083</b><br><br>
                    Дереккөз: ДДҰ, ұлттық денсаулық министрліктері
                </div>
                <div>
                    <b style="color:#ff4444;">β (бета) — жұқтыру жылдамдығы:</b><br>
                    <code style="background:#111;padding:.2rem .5rem;border-radius:4px;">β = R₀ × γ</code><br>
                    R₀ ғылыми жарияланымдардан алынады<br>
                    Мысал: R₀=2.5, γ=0.083 → β = <b>0.208</b><br><br>
                    Дереккөз: Our World in Data, CDC, WHO
                </div>
            </div>
            <div style="margin-top:.75rem;color:#888;font-size:.82rem;">
                📌 Симуляторда ел таңдаған кезде бұл параметрлер автоматты түрде жүктеледі.
            </div>
        </div>
        """,
    }
    st.markdown(formula_text[lang], unsafe_allow_html=True)
    st.dataframe(df.style.format({"population":"{:,.0f}","total_cases":"{:,.0f}","total_deaths":"{:,.0f}","infection_rate_pct":"{:.2f}%","mortality_rate_pct":"{:.2f}%","vaccination_rate_pct":"{:.1f}%","peak_beta":"{:.3f}","gamma":"{:.3f}","R0":"{:.2f}"}), use_container_width=True, height=350)

    ec1,ec2 = st.columns(2)
    with ec1:
        st.markdown(f'<div class="section-header">{t("r0_chart",lang)}</div>', unsafe_allow_html=True)
        ds = df.sort_values("R0",ascending=True)
        fr = go.Figure(go.Bar(x=ds["R0"],y=ds["country"],orientation="h",marker_color=["#ff3333" if r>2 else "#44ff88" for r in ds["R0"]],text=[f"{r:.2f}" for r in ds["R0"]],textposition="outside"))
        fr.add_vline(x=1,line_dash="dash",line_color="#ffaa44",annotation_text="R₀=1",annotation_font_color="#ffaa44")
        fr.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),height=380,xaxis=dict(title="R₀",gridcolor="#161616",color="#555"),yaxis=dict(color="#888"),margin=dict(l=0,r=60,t=10,b=0))
        st.plotly_chart(fr, use_container_width=True)
    with ec2:
        st.markdown(f'<div class="section-header">{t("vacc_chart",lang)}</div>', unsafe_allow_html=True)
        fv = px.scatter(df,x="vaccination_rate_pct",y="mortality_rate_pct",size="total_cases",color="continent",hover_name="country",text="country",labels={"vaccination_rate_pct":t("vacc_x",lang),"mortality_rate_pct":t("vacc_y",lang),"continent":t("continent_lbl",lang)},color_discrete_sequence=["#ff4444","#44ff88","#4488ff","#ffaa44","#ff44ff","#44ffff"])
        fv.update_traces(textposition="top center",textfont_size=8)
        fv.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),height=380,xaxis=dict(gridcolor="#161616",color="#555"),yaxis=dict(gridcolor="#161616",color="#555"),legend=dict(bgcolor="rgba(0,0,0,0)"),margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fv, use_container_width=True)

    st.markdown(f'<div class="section-header">{t("cases_chart",lang)}</div>', unsafe_allow_html=True)
    dc = df.sort_values("total_cases",ascending=False)
    fc = go.Figure(go.Bar(x=dc["country"],y=dc["total_cases"],marker=dict(color=dc["total_cases"],colorscale=[[0,"#330000"],[1,"#ff3333"]]),opacity=0.9))
    fc.update_layout(plot_bgcolor="#080808",paper_bgcolor="#080808",font=dict(color="#ccc",family="Oswald"),height=300,xaxis=dict(color="#666"),yaxis=dict(title=t("cases_yaxis",lang),gridcolor="#161616",color="#666"),margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fc, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 9 — ABOUT
# ════════════════════════════════════════════════════════════════════════════
with tab9:
    # Кнопка скачивания презентации
    pptx_path = os.path.join(os.path.dirname(__file__), 'Zombie_Presentation.pptx')
    if os.path.exists(pptx_path):
        with open(pptx_path, 'rb') as f:
            pptx_bytes = f.read()
        dl_label = {"RU": "📥 Скачать презентацию проекта (.pptx)", "EN": "📥 Download project presentation (.pptx)", "KZ": "📥 Жоба презентациясын жүктеу (.pptx)"}
        st.download_button(
            label=dl_label.get(lang, dl_label["RU"]),
            data=pptx_bytes,
            file_name="Zombie_Apocalypse_Simulator.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )
        st.markdown('<br>', unsafe_allow_html=True)

    a1,a2 = st.columns([3,2])
    with a1:
        st.markdown(f"""## 🔬 {t('about_hdr',lang) if 'about_hdr' in __import__('translations').TRANSLATIONS else 'О проекте'}

{t('about_body',lang)}

{t('about_why_zombie',lang)}
{t('about_why_body',lang)}

{t('about_precedents',lang)}
- **CDC** — [Preparedness 101: Zombie Apocalypse](https://web.archive.org/web/2023/https://www.cdc.gov/phpr/zombie/index.html) *(archived)*
- **Pentagon** — [CONPLAN 8888](https://foreignpolicy.com/2014/05/13/exclusive-the-pentagon-has-a-plan-to-stop-the-zombie-apocalypse-seriously/)

{t('about_sir_title',lang)}
```
dS/dt = -β × S × I / N
dI/dt =  β × S × I / N − γ × I
dR/dt =  γ × I
R₀ = β/γ  →  R₀>1  |  R₀<1
```

---
🐙 **GitHub:** [zombie-apocalypse-simulator](https://github.com/maksatomarov-droid/zombie-apocalypse-simulator)
        """)

        # ── Glossary ──────────────────────────────────────────────────────
        st.markdown(f'<div class="section-header">{t("glossary_hdr",lang)}</div>', unsafe_allow_html=True)

        glossary_data = {
            "RU": [
                ("SIR", "Susceptible · Infected · Recovered",
                 "Математическая модель эпидемии, делящая население на три группы: S — здоровые (могут заразиться), I — заражённые (зомби), R — выбывшие (иммунные или мёртвые). Используется ВОЗ и учёными для моделирования COVID-19, гриппа, кори."),
                ("R₀ (R-ноль)", "Basic Reproduction Number — базовое репродуктивное число",
                 "Показывает, сколько людей в среднем заразит один больной. R₀ = 2 → каждый зомби кусает 2 человека. Если R₀ > 1 — эпидемия растёт. Если R₀ < 1 — затухает сама по себе. Для COVID-19 было 2–3, для кори — 12–18."),
                ("β (бета)", "Transmission Rate — скорость передачи вируса",
                 "Греческая буква β. Показывает насколько быстро вирус передаётся от заражённого к здоровому. Высокий β = вирус очень заразный (как корь). Низкий β = передаётся медленно."),
                ("γ (гамма)", "Recovery/Removal Rate — скорость выздоровления или устранения",
                 "Греческая буква γ. Показывает как быстро заражённые перестают быть источником угрозы. В нашей модели: скорость уничтожения зомби или их естественного разложения."),
                ("COVID-19", "Coronavirus Disease 2019",
                 "Инфекционное заболевание, вызванное коронавирусом SARS-CoV-2. Наш датасет основан на реальных данных COVID-19 — параметры β и γ рассчитаны по реальным вспышкам в 15 странах."),
                ("EDA", "Exploratory Data Analysis — разведочный анализ данных",
                 "Первый шаг в любом Data Science проекте. В нашем проекте EDA — вкладка '📈 Данные' с графиками по 15 странам."),
                ("NPI", "Non-Pharmaceutical Interventions — немедикаментозные меры",
                 "Карантин, маски, социальная дистанция. В нашей модели карантин = NPI. Именно NPI применяли все страны в начале COVID-19 до появления вакцин."),
                ("CONPLAN 8888", "Contingency Plan 8888 — план Пентагона",
                 "Реальный рассекреченный документ США. Написан в 2011 году как учебный сценарий для военных. Официальное название: 'Counter-Zombie Dominance Operations'."),
                ("Model Explainability", "Объяснимость модели",
                 "Умение объяснить результат модели в понятном формате. Правила выживания — это наш способ explainability: вместо 'R₀=3.2' мы говорим 'Правило #1: Кардио'."),
            ],
            "EN": [
                ("SIR", "Susceptible · Infected · Recovered",
                 "Mathematical epidemic model dividing population into three groups: S — healthy (can be infected), I — infected (zombies), R — removed (immune or dead). Used by WHO and scientists to model COVID-19, flu, measles."),
                ("R₀ (R-zero)", "Basic Reproduction Number",
                 "Shows how many people one infected person infects on average. R₀ = 2 → each zombie bites 2 people. If R₀ > 1 — epidemic grows. If R₀ < 1 — fades on its own. COVID-19 was 2–3, measles — 12–18."),
                ("β (beta)", "Transmission Rate",
                 "Greek letter β. Shows how quickly the virus spreads from infected to healthy. High β = very contagious (like measles). Low β = spreads slowly."),
                ("γ (gamma)", "Recovery/Removal Rate",
                 "Greek letter γ. Shows how quickly infected people stop being a threat — recover, die or are isolated. In our model: the rate of zombie elimination."),
                ("COVID-19", "Coronavirus Disease 2019",
                 "Infectious disease caused by SARS-CoV-2 coronavirus. Our dataset is based on real COVID-19 data — β and γ parameters calculated from real outbreaks in 15 countries."),
                ("EDA", "Exploratory Data Analysis",
                 "First step in any Data Science project. In our project EDA is the '📈 Data' tab with charts across 15 countries."),
                ("NPI", "Non-Pharmaceutical Interventions",
                 "Quarantine, masks, social distancing. In our model quarantine = NPI. All countries used NPI at the start of COVID-19 before vaccines."),
                ("CONPLAN 8888", "Pentagon Contingency Plan 8888",
                 "Real declassified US document. Written in 2011 as a training scenario for military officers. Official name: 'Counter-Zombie Dominance Operations'."),
                ("Model Explainability", "Model Explainability",
                 "The ability to explain a model's result in understandable terms. Survival Rules Rules are our explainability method: instead of 'R₀=3.2' we say 'Rule #1: Cardio'."),
            ],
            "KZ": [
                ("SIR", "Susceptible · Infected · Recovered",
                 "Халықты үш топқа бөлетін эпидемияның математикалық моделі: S — сау (жұқтыруы мүмкін), I — жұқтырған (зомби), R — шыққандар (иммунды немесе өлі). ДДҰ және ғалымдар COVID-19, тұмауды модельдеу үшін қолданады."),
                ("R₀ (R-ноль)", "Базалық репродуктивтік сан",
                 "Бір ауру адам орташа қанша адамды жұқтыратынын көрсетеді. R₀ = 2 → әр зомби 2 адамды тістейді. R₀ > 1 болса — эпидемия өседі. R₀ < 1 болса — өздігінен азаяды."),
                ("β (бета)", "Вирустың берілу жылдамдығы",
                 "Грек әрпі β. Вирустың жұқтырғаннан сауға қаншалықты тез таралатынын көрсетеді. Жоғары β = өте жұқпалы вирус. Төмен β = баяу таралады."),
                ("γ (гамма)", "Сауығу/жою жылдамдығы",
                 "Грек әрпі γ. Жұқтырғандар қаншалықты тез қауіп төндіруді тоқтататынын көрсетеді. Біздің модельде: зомбиді жою жылдамдығы."),
                ("COVID-19", "2019 Коронавирус ауруы",
                 "SARS-CoV-2 коронавирусы тудыратын жұқпалы ауру. Біздің деректер жиыны 15 елдегі нақты COVID-19 деректеріне негізделген."),
                ("EDA", "Барлаушылық деректер талдауы",
                 "Кез келген Data Science жобасының бірінші қадамы. Біздің жобада EDA — '📈 Деректер' қойындысы."),
                ("NPI", "Дәрілік емес шаралар",
                 "Карантин, маска, әлеуметтік қашықтық. Біздің модельде карантин = NPI."),
                ("CONPLAN 8888", "Пентагон жоспары 8888",
                 "АҚШ-тың нақты жасырын жасырылмаған құжаты. 2011 жылы әскери офицерлерге арналған оқу сценарийі ретінде жазылған."),
                ("Model Explainability", "Модельді түсіндіру",
                 "Модель нәтижесін түсінікті форматта түсіндіру мүмкіндігі. Зомбиленд ережелері — біздің explainability әдісіміз."),
            ],
        }

        glossary = glossary_data.get(lang, glossary_data["RU"])
        for term, full, explain in glossary:
            st.markdown(f"""
            <div class="rule-card" style="border-left-color:#4488ff;">
                <div class="rule-title" style="color:#66aaff;">📌 {term}
                    <span style="font-size:.8rem;color:#555;font-weight:400;margin-left:.5rem;">= {full}</span>
                </div>
                <div class="rule-text">{explain}</div>
            </div>
            """, unsafe_allow_html=True)

    with a2:
        st.markdown(f"""
{t('stack_hdr',lang)}

| {t('stack_tool',lang)} | {t('stack_use',lang)} |
|---|---|
| Python | {t('stack_py',lang)} |
| NumPy | {t('stack_np',lang)} |
| Pandas | {t('stack_pd',lang)} |
| Plotly | {t('stack_pl',lang)} |
| Streamlit | {t('stack_st',lang)} |
| GitHub | {t('stack_gh',lang)} |
| Gemini AI | {t('tab_ai',lang)} |

{t('dataset_hdr',lang)}
{t('dataset_body',lang)}

{t('author_hdr',lang)}

**Максат Омаров**

{t('course',lang)}
        """)

# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — ЕСЛИ ТЫ ЗОМБИ 😄
# ════════════════════════════════════════════════════════════════════════════
with tab6:
    zombie_titles = {
        "RU": "🧟 ПОЗДРАВЛЯЕМ! ТЫ СТАЛ ЗОМБИ",
        "EN": "🧟 CONGRATULATIONS! YOU ARE NOW A ZOMBIE",
        "KZ": "🧟 ҚҰТТЫҚТАЙМЫЗ! СЕН ЗОМБИГЕ АЙНАЛДЫҢ",
    }
    zombie_sub = {
        "RU": "Руководство по максимально эффективному апокалипсису",
        "EN": "Guide to the most effective apocalypse",
        "KZ": "Ең тиімді апокалипсис бойынша нұсқаулық",
    }
    st.markdown(f"""
    <div class="hero" style="background:linear-gradient(135deg,#001a00 0%,#080808 40%,#1a0000 100%);border-color:#005500;">
        <h1 style="color:#44ff44;text-shadow:0 0 40px #00ff0088;">{zombie_titles[lang]}</h1>
        <p class="subtitle">{zombie_sub[lang]}</p>
    </div>
    """, unsafe_allow_html=True)

    tips_ru = [
        ("🦷", "Правило Зомби #1 — Кусай правильно",
         "Не трать энергию на бег. Зомби побеждают числом, а не скоростью. Иди туда где много людей — торговые центры, стадионы, офисы в обеденный перерыв. КПД укуса там максимальный.",
         "Торговые центры · Стадионы · Корпоративы"),
        ("🧠", "Правило Зомби #2 — Целевая аудитория",
         "Приоритет: блогеры и инфлюенсеры. Они медленные (много времени в телефоне). После укуса первыми начнут снимать Stories — бесплатная реклама твоей эпидемии.",
         "Блогеры · Инфлюенсеры · Офисные менеджеры"),
        ("📍", "Правило Зомби #3 — Лучшие локации",
         "ТОП мест по эффективности: 1) Торговые центры в выходной, 2) Концерты и фестивали, 3) Митинги и собрания, 4) Переполненный транспорт. Избегай: деревни, военные базы, фермы.",
         "Высокая плотность = высокий β"),
        ("🚫", "Правило Зомби #4 — Кого избегать",
         "Военные (γ сразу вырастет), врачи (могут найти антидот), фермеры с топорами (правило #1 выживания работает в обе стороны), IT-шники (напишут алгоритм против тебя). Максат Омаров тоже опасен — он уже всё смоделировал.",
         "⚠️ Высокий риск для зомби"),
        ("📊", "Правило Зомби #5 — Математика апокалипсиса",
         "Помни: тебе нужен R₀ > 1. При β=0.5 и γ=0.1 твой R₀=5 — отличный результат! Держись подальше от карантинных зон — они снижают твой β.",
         "Цель: R₀ > 1"),
        ("🧟", "Правило Зомби #6 — Групповая тактика",
         "Зомби сильнее в группе. Орда из 1000 зомби снижает γ людей до нуля. В нашей SIR-модели это рост I при снижении S. Объединяйся!",
         "Сила в числах"),
    ]

    disclaimer = {
        "RU": "⚠️ Это юмористический контент в стиле фильма «Зомбиленд». Все советы вымышлены и служат для развлечения и демонстрации SIR-модели с точки зрения «другой стороны». Не кусайте людей в реальной жизни 🧟",
        "EN": "⚠️ Humorous content in the style of 'Survival Rules'. All tips are fictional. Do not bite people in real life 🧟",
        "KZ": "⚠️ Бұл «Зомбиленд» стилінде юмористикалық мазмұн. Барлық кеңестер ойдан шығарылған. Нақты өмірде адамдарды тістемеңіз 🧟",
    }
    st.markdown(f'<div class="banner banner-green">{t("zombie_disclaimer",lang)}</div>', unsafe_allow_html=True)

    zombie_tips = {
        "RU": [
            ("🦷","Правило Зомби #1 — Кусай правильно","Не трать энергию на бег. Иди туда где много людей — торговые центры, стадионы, офисы. КПД укуса там максимальный.","Торговые центры · Стадионы · Корпоративы"),
            ("🧠","Правило Зомби #2 — Целевая аудитория","Приоритет: блогеры и инфлюенсеры. После укуса первыми начнут снимать Stories — бесплатная реклама эпидемии.","Блогеры · Инфлюенсеры"),
            ("📍","Правило Зомби #3 — Лучшие локации","ТОП: 1) Торговые центры, 2) Концерты, 3) Митинги, 4) Транспорт. Избегай: деревни, военные базы, фермы.","Высокая плотность = высокий β"),
            ("🚫","Правило Зомби #4 — Кого избегать","Военные (γ вырастет), врачи (найдут антидот), фермеры с топорами, IT-шники. Максат Омаров опасен — он всё смоделировал.","⚠️ Высокий риск"),
            ("📊","Правило Зомби #5 — Математика апокалипсиса","Тебе нужен R₀ > 1. При β=0.5 и γ=0.1 твой R₀=5 — отличный результат! Избегай карантинных зон.","Цель: R₀ > 1"),
            ("🧟","Правило Зомби #6 — Групповая тактика","Орда из 1000 зомби снижает γ до нуля. В SIR-модели это рост I при снижении S. Объединяйся!","Сила в числах"),
        ],
        "EN": [
            ("🦷","Zombie Rule #1 — Bite Right","Don't waste energy running. Go where people gather — malls, stadiums, offices. Maximum bite efficiency there.","Malls · Stadiums · Corporate events"),
            ("🧠","Zombie Rule #2 — Target Audience","Priority: bloggers and influencers. After being bitten they'll start posting Stories — free epidemic advertising.","Bloggers · Influencers"),
            ("📍","Zombie Rule #3 — Best Locations","TOP: 1) Malls, 2) Concerts, 3) Rallies, 4) Transport. Avoid: villages, military bases, farms.","High density = high β"),
            ("🚫","Zombie Rule #4 — Who to Avoid","Military (γ spikes), doctors (antidote), farmers with axes, IT guys. Maxat Omarov is dangerous — he modeled everything.","⚠️ High risk"),
            ("📊","Zombie Rule #5 — Apocalypse Math","You need R₀ > 1. With β=0.5 and γ=0.1 your R₀=5 — excellent! Avoid quarantine zones.","Goal: R₀ > 1"),
            ("🧟","Zombie Rule #6 — Group Tactics","A horde of 1000 zombies reduces human γ to zero. In SIR model: I rises as S falls. Unite!","Strength in numbers"),
        ],
        "KZ": [
            ("🦷","Зомби ережесі #1 — Дұрыс тістеу","Жүгіруге энергия жұмсама. Адам көп жерге бар — сауда орталықтары, стадиондар, кеңселер.","Сауда орталықтары · Стадиондар"),
            ("🧠","Зомби ережесі #2 — Мақсатты аудитория","Басымдық: блогерлер. Тістелгеннен кейін Stories түсіреді — тегін жарнама!","Блогерлер · Инфлюенсерлер"),
            ("📍","Зомби ережесі #3 — Ең жақсы орындар","ТОП: 1) Сауда орталықтары, 2) Концерттер, 3) Жиналыстар, 4) Көлік. Болдырма: ауылдар, әскери базалар.","Жоғары тығыздық = жоғары β"),
            ("🚫","Зомби ережесі #4 — Кімнен аулақ болу","Әскерилер, дәрігерлер, балталы фермерлер, IT мамандары. Максат Омаров қауіпті — ол бәрін модельдеді.","⚠️ Жоғары тәуекел"),
            ("📊","Зомби ережесі #5 — Математика","R₀ > 1 керек. β=0.5 және γ=0.1 кезінде R₀=5 — тамаша! Карантин аймақтарынан аулақ бол.","Мақсат: R₀ > 1"),
            ("🧟","Зомби ережесі #6 — Топтық тактика","1000 зомби ордасы γ-ны нөлге дейін азайтады. SIR моделінде I өседі, S азаяды. Бірігіңдер!","Күш — санда"),
        ],
    }
    for emoji, title, desc, tag in zombie_tips.get(lang, zombie_tips["RU"]):
        st.markdown(f"""
        <div class="rule-card" style="border-left-color:#44ff44;">
            <div class="rule-title" style="color:#44ff88;">{emoji} {title}
                <span style="float:right;font-size:.75rem;background:#002200;color:#44ff88;padding:.1rem .5rem;border-radius:4px;font-family:'Share Tech Mono',monospace;">{tag}</span>
            </div>
            <div class="rule-text">{desc}</div>
        </div>""", unsafe_allow_html=True)

    sir_note = {
        "RU": "📊 Связь с SIR-моделью: каждый совет влияет на β (скорость заражения) и γ (скорость устранения). Выбор локации = повышение β. Избегание военных = снижение γ. Это и есть математика апокалипсиса!",
        "EN": "📊 SIR connection: each tip affects β (infection rate) and γ (removal rate). Location choice = raising β. Avoiding military = lowering γ. This IS the math!",
        "KZ": "📊 SIR байланысы: әр кеңес β және γ параметрлеріне тікелей әсер етеді. Бұл — апокалипсис математикасы!",
    }
    st.markdown(f'<div class="banner banner-blue" style="margin-top:1.5rem;">{t("zombie_sir_note",lang)}</div>', unsafe_allow_html=True)

    # ── Adversarial Attack научный блок ──
    st.markdown('<br>', unsafe_allow_html=True)
    adv_title = {"RU": "🔬 Adversarial Attack — Научный анализ с позиции атакующего", "EN": "🔬 Adversarial Attack — Scientific Analysis from the Attacker's Perspective", "KZ": "🔬 Adversarial Attack — Шабуылдаушы тұрғысынан ғылыми талдау"}
    adv_desc = {
        "RU": "В Data Science <b>Adversarial Attack</b> — это метод анализа системы путём поиска её слабых мест с позиции противника. Мы применяем этот принцип к эпидемиологии: моделируем распространение вируса как будто мы — атакующая сторона.",
        "EN": "In Data Science, an <b>Adversarial Attack</b> is a method of analyzing a system by finding its weaknesses from an adversary's perspective. We apply this principle to epidemiology: modeling virus spread as if we are the attacking side.",
        "KZ": "Data Science-та <b>Adversarial Attack</b> — бұл жүйені қарсылас тұрғысынан оның осал жерлерін іздеу арқылы талдау әдісі.",
    }
    st.markdown(f'<div class="section-header">{adv_title[lang]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#aaa;font-size:.9rem;margin-bottom:1rem;">{adv_desc[lang]}</p>', unsafe_allow_html=True)

    # Симулятор типов зомби
    zombie_type_title = {"RU": "🧟 Выбери тип зомби — Adversarial Simulation", "EN": "🧟 Choose Zombie Type — Adversarial Simulation", "KZ": "🧟 Зомби түрін таңда — Adversarial Simulation"}
    st.markdown(f'<div class="section-header">{zombie_type_title[lang]}</div>', unsafe_allow_html=True)

    # Простое объяснение
    simple_exp = {
        "RU": "👇 Выбери тип зомби и место — симулятор покажет насколько опасна эпидемия. R₀ > 1 = эпидемия растёт. R₀ < 1 = затухает.",
        "EN": "👇 Choose zombie type and location — the simulator shows how dangerous the epidemic is. R₀ > 1 = epidemic grows. R₀ < 1 = fades.",
        "KZ": "👇 Зомби түрі мен орынды таңда — симулятор эпидемияның қаншалықты қауіпті екенін көрсетеді. R₀ > 1 = өседі. R₀ < 1 = азаяды.",
    }
    st.markdown(f'<p style="color:#888;font-size:.88rem;margin-bottom:1rem;background:#111;padding:.6rem 1rem;border-radius:6px;border-left:3px solid #ff4444;">{simple_exp[lang]}</p>', unsafe_allow_html=True)

    zc1, zc2 = st.columns(2)
    with zc1:
        zombie_types = {
            "RU": ["🏃 Бегун (Runner) — высокий β, низкий γ", "🦺 Танк (Tank) — низкий β, очень низкий γ", "🧠 Умный (Smart) — средний β, адаптивный", "🐢 Медленный (Slow) — очень низкий β"],
            "EN": ["🏃 Runner — high β, low γ", "🦺 Tank — low β, very low γ", "🧠 Smart — medium β, adaptive", "🐢 Slow — very low β"],
            "KZ": ["🏃 Жүгіруші — жоғары β, төмен γ", "🦺 Танк — төмен β, өте төмен γ", "🧠 Ақылды — орташа β, бейімделгіш", "🐢 Баяу — өте төмен β"],
        }
        zombie_type = st.selectbox("", zombie_types[lang], key="zombie_type_sel", label_visibility="collapsed")

        locations = {
            "RU": ["🏪 Торговый центр (плотность: очень высокая)", "🏟️ Стадион (плотность: высокая)", "🚇 Метро/Транспорт (плотность: высокая)", "🏫 Школа/Офис (плотность: средняя)", "🌳 Парк (плотность: низкая)", "🏚️ Деревня (плотность: очень низкая)"],
            "EN": ["🏪 Shopping Mall (density: very high)", "🏟️ Stadium (density: high)", "🚇 Metro/Transport (density: high)", "🏫 School/Office (density: medium)", "🌳 Park (density: low)", "🏚️ Village (density: very low)"],
            "KZ": ["🏪 Сауда орталығы (тығыздық: өте жоғары)", "🏟️ Стадион (тығыздық: жоғары)", "🚇 Метро/Көлік (тығыздық: жоғары)", "🏫 Мектеп/Кеңсе (тығыздық: орташа)", "🌳 Саябақ (тығыздық: төмен)", "🏚️ Ауыл (тығыздық: өте төмен)"],
        }
        location = st.selectbox("", locations[lang], key="zombie_loc_sel", label_visibility="collapsed")

    with zc2:
        # Параметры на основе выбора
        type_params = {"Runner":"🏃", "Бегун":"🏃", "Жүгіруші":"🏃",
                       "Tank":"🦺", "Танк":"🦺",
                       "Smart":"🧠", "Умный":"🧠", "Ақылды":"🧠",
                       "Slow":"🐢", "Медленный":"🐢", "Баяу":"🐢"}
        beta_gamma = {"🏃": (0.8, 0.05), "🦺": (0.25, 0.02), "🧠": (0.5, 0.08), "🐢": (0.15, 0.12)}
        loc_params  = {"Mall":1.0,"Торговый":1.0,"Сауда":1.0,
                       "Stadium":0.85,"Стадион":0.85,
                       "Metro":0.80,"Метро":0.80,
                       "School":0.55,"Школа":0.55,"Мектеп":0.55,
                       "Park":0.30,"Парк":0.30,"Саябақ":0.30,
                       "Village":0.15,"Деревня":0.15,"Ауыл":0.15}

        # Определяем тип по первому слову
        zt_word = zombie_type.replace("🏃","").replace("🦺","").replace("🧠","").replace("🐢","").strip().split()[0]
        zl_word = location.replace("🏪","").replace("🏟️","").replace("🚇","").replace("🏫","").replace("🌳","").replace("🏚️","").strip().split()[0]

        matched_emoji = "🏃"
        for k, v in type_params.items():
            if k in zt_word:
                matched_emoji = v
                break

        b_base, g_base = beta_gamma.get(matched_emoji, (0.4, 0.1))

        loc_mult = 0.5
        for k, v in loc_params.items():
            if k in zl_word:
                loc_mult = v
                break

        b_final = round(min(b_base * (1 + loc_mult), 0.99), 2)
        r0_adv = round(b_final / g_base, 2)

        color_r0 = "#ff3333" if r0_adv > 3 else ("#ffaa44" if r0_adv > 1 else "#44ff88")
        verdict_adv = {
            "RU": "🧟 ОТЛИЧНЫЙ ДЕНЬ! Кусай всех!" if r0_adv > 3 else ("⚠️ НЕПЛОХО. Продолжай кусать" if r0_adv > 1 else "😢 ПРОВАЛ. Тебя уничтожают..."),
            "EN": "🧟 EXCELLENT DAY! Bite everyone!" if r0_adv > 3 else ("⚠️ NOT BAD. Keep biting" if r0_adv > 1 else "😢 FAILURE. You're being eliminated..."),
            "KZ": "🧟 ТАМАША КҮН! Барлығын тістей!" if r0_adv > 3 else ("⚠️ ЖАМАН ЕМЕС. Тістей бер" if r0_adv > 1 else "😢 СӘТСІЗДІК. Сені жояды..."),
        }

        st.markdown(f"""
        <div style="background:#0a0a0a;border:1px solid #330000;border-radius:10px;padding:1.25rem;text-align:center;">
            <div style="color:#888;font-size:.8rem;font-family:'Share Tech Mono';margin-bottom:.5rem;">РЕЗУЛЬТАТ СИМУЛЯЦИИ</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.5rem;margin:.75rem 0;">
                <div style="background:#111;border-radius:6px;padding:.5rem;">
                    <div style="color:#555;font-size:.7rem;">β — скорость заражения</div>
                    <div style="color:#ff4444;font-size:1.4rem;font-weight:700;">{b_final}</div>
                    <div style="color:#444;font-size:.65rem;">чем выше = опаснее</div>
                </div>
                <div style="background:#111;border-radius:6px;padding:.5rem;">
                    <div style="color:#555;font-size:.7rem;">γ — скорость устранения</div>
                    <div style="color:#4488ff;font-size:1.4rem;font-weight:700;">{g_base}</div>
                    <div style="color:#444;font-size:.65rem;">чем выше = лучше для людей</div>
                </div>
                <div style="background:#111;border-radius:6px;padding:.5rem;">
                    <div style="color:#555;font-size:.7rem;">R₀ = β ÷ γ</div>
                    <div style="color:{color_r0};font-size:1.4rem;font-weight:700;">{r0_adv}</div>
                    <div style="color:#444;font-size:.65rem;">1 зомби заражает {r0_adv} чел.</div>
                </div>
            </div>
            <div style="font-size:1.2rem;font-weight:700;color:{color_r0};margin-top:.5rem;">{verdict_adv[lang]}</div>
        </div>""", unsafe_allow_html=True)

    adv_explain = {
        "RU": f"🎓 <b>Научный вывод:</b> Тип зомби «{zombie_type}» в локации «{location}» даёт R₀ = {r0_adv}. {'Каждый зомби заражает более 3 человек — эпидемия неудержима.' if r0_adv>3 else ('R₀ > 1 — эпидемия растёт, но поддаётся контролю при карантине.' if r0_adv>1 else 'R₀ < 1 — эпидемия затухает сама по себе.')} Этот анализ демонстрирует принцип Adversarial Attack: понимая стратегию «атакующего», мы можем эффективнее выстраивать защиту.",
        "EN": f"🎓 <b>Scientific conclusion:</b> Zombie type «{zombie_type}» at location «{location}» gives R₀ = {r0_adv}. {'Each zombie infects 3+ people — epidemic is unstoppable.' if r0_adv>3 else ('R₀ > 1 — epidemic grows but can be controlled with quarantine.' if r0_adv>1 else 'R₀ < 1 — epidemic fades on its own.')} This analysis demonstrates the Adversarial Attack principle: by understanding the attacker's strategy, we can build better defenses.",
        "KZ": f"🎓 <b>Ғылыми қорытынды:</b> «{zombie_type}» зомби түрі «{location}» орнында R₀ = {r0_adv} береді. Adversarial Attack принципі: шабуылдаушының стратегиясын түсіну арқылы қорғанысты тиімдірек құруға болады.",
    }
    st.markdown(f'<div class="banner banner-blue" style="margin-top:1rem;">{adv_explain[lang]}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 7 — OPENROUTER AI ANALYST
# ════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown(f'<div class="section-header">{t("ai_hdr",lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#555;font-size:.9rem;margin-bottom:1.5rem;">{t("ai_desc",lang)}</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="banner banner-blue"><b>{t("ai_examples",lang)}</b><br>• {t("ai_ex1",lang)}<br>• {t("ai_ex2",lang)}<br>• {t("ai_ex3",lang)}<br>• {t("ai_ex4",lang)}</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="color:#aaa;font-size:1rem;font-weight:600;margin:.8rem 0 .3rem;">{t("ai_question_lbl",lang)}</p>', unsafe_allow_html=True)
    ai_question = st.text_area("", placeholder=t("ai_ex1",lang), key="ai_q", label_visibility="collapsed", height=100)

    ask_btn = st.button(t("ai_btn",lang), use_container_width=True, key="ask_ai")

    if ask_btn:
        if not ai_question.strip():
            st.markdown(f'<div class="banner banner-yellow">{t("ai_no_q",lang)}</div>', unsafe_allow_html=True)
        else:
            with st.spinner(t("ai_thinking",lang)):
                try:
                    import urllib.request, json as _json

                    system_prompt = {
                        "RU": "Ты — ИИ-эпидемиолог и учёный Data Science. Отвечай на вопросы про эпидемии, вирусы, вакцины и пандемии. Используй научный язык но объясняй просто. Упоминай SIR-модели, R₀, β, γ где уместно. Отвечай структурированно с эмодзи. Отвечай на русском языке.",
                        "KZ": "Сен — ЖИ-эпидемиолог және Data Science ғалымысың. Эпидемия, вирустар, вакциналар туралы сұрақтарға жауап бер. SIR модельдерін, R₀, β, γ атап өт. Қазақ тілінде жауап бер.",
                        "EN": "You are an AI epidemiologist and Data Science scientist. Answer questions about epidemics, viruses, vaccines and pandemics. Mention SIR models, R₀, β, γ where appropriate. Answer in English.",
                    }

                    payload = _json.dumps({
                        "model": "google/gemma-4-26b-a4b-it:free",
                        "messages": [
                            {"role": "system", "content": system_prompt.get(lang, system_prompt["RU"])},
                            {"role": "user", "content": ai_question}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1200,
                    }).encode("utf-8")

                    req = urllib.request.Request(
                        "https://openrouter.ai/api/v1/chat/completions",
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                            "HTTP-Referer": "https://zombie-simulator.app",
                            "X-Title": "Zombie Apocalypse Simulator"
                        }
                    )
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        result = _json.loads(resp.read())

                    answer = result["choices"][0]["message"]["content"]

                    st.markdown(f'<div class="section-header">{t("ai_answer_hdr",lang)}</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="background:#0a0a1a;border:1px solid #003355;border-left:4px solid #4488ff;border-radius:10px;padding:1.5rem;margin:.5rem 0;line-height:1.7;color:#ccc;font-size:.95rem;">
                        {answer.replace(chr(10), '<br>')}
                    </div>""", unsafe_allow_html=True)

                    if "ai_history" not in st.session_state:
                        st.session_state["ai_history"] = []
                    st.session_state["ai_history"].append({"q": ai_question, "a": answer})

                except Exception as e:
                    st.markdown(f'<div class="banner banner-red">❌ Ошибка: {str(e)[:150]}</div>', unsafe_allow_html=True)

    if "ai_history" in st.session_state and len(st.session_state["ai_history"]) > 1:
        st.markdown('<div class="section-header">📋 История вопросов</div>', unsafe_allow_html=True)
        for item in reversed(st.session_state["ai_history"][:-1][-3:]):
            with st.expander(f"💬 {item['q'][:60]}..."):
                st.markdown(item['a'])

# ════════════════════════════════════════════════════════════════════════════
# TAB 8 — MACHINE LEARNING: Random Forest Classifier
# ════════════════════════════════════════════════════════════════════════════
with tab8:
    ml_titles = {
        "RU": "🤖 Machine Learning — Классификатор выживаемости",
        "EN": "🤖 Machine Learning — Survival Classifier",
        "KZ": "🤖 Machine Learning — Тіршілік ету классификаторы",
    }
    ml_desc = {
        "RU": "Random Forest обучен на синтетических данных выживших. Модель предсказывает шанс выживания и объясняет какие факторы влияют больше всего (XAI — Explainable AI).",
        "EN": "Random Forest trained on synthetic survivor data. The model predicts survival chance and explains which factors matter most (XAI — Explainable AI).",
        "KZ": "Random Forest синтетикалық тіршілік еткендер деректерінде оқытылған. Модель тіршілік ету мүмкіндігін болжайды және қандай факторлар маңызды екенін түсіндіреді (XAI).",
    }
    st.markdown(f'<div class="section-header">{ml_titles[lang]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#555;font-size:.9rem;margin-bottom:1rem;">{ml_desc[lang]}</p>', unsafe_allow_html=True)

    try:
        import numpy as np
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        import plotly.graph_objects as go

        # ── Генерация синтетического датасета ──
        np.random.seed(42)
        n = 1000

        cardio_s      = np.random.randint(1, 11, n)
        age_s         = np.random.randint(10, 71, n)
        food_s        = np.random.randint(0, 31, n)
        rules_s       = np.random.randint(0, 11, n)
        group_s       = np.random.randint(1, 11, n)
        weapon_s      = np.random.randint(0, 2, n)
        dtap_s        = np.random.randint(0, 2, n)
        prof_s        = np.random.randint(0, 8, n)   # 0=военный ... 7=блогер
        city_danger_s = np.random.uniform(0.4, 1.0, n)

        prof_bonus_arr = [25,18,20,22,12,10,5,2]
        prof_bonus_s   = np.array([prof_bonus_arr[p] for p in prof_s])

        score_s = (cardio_s*3.5 + prof_bonus_s +
                   (1-city_danger_s)*20 + dtap_s*8 + weapon_s*12 +
                   food_s*0.8 + rules_s*1.5 + np.minimum(group_s,5)*1.2 -
                   np.maximum(0, age_s-40)*0.8 + np.random.uniform(-5,5,n))
        score_s = np.clip(score_s, 2, 98)
        survived_s = (score_s >= 50).astype(int)

        df_ml = pd.DataFrame({
            'cardio':      cardio_s,
            'age':         age_s,
            'food':        food_s,
            'rules':       rules_s,
            'group':       group_s,
            'weapon':      weapon_s,
            'double_tap':  dtap_s,
            'profession':  prof_s,
            'city_danger': city_danger_s,
            'survived':    survived_s
        })

        feat_cols = ['cardio','age','food','rules','group','weapon','double_tap','profession','city_danger']
        feat_names = {
            "RU": ['Кардио','Возраст','Запас еды','Знание правил','Группа','Оружие','Double Tap','Профессия','Опасность города'],
            "EN": ['Cardio','Age','Food supply','Rule knowledge','Group','Weapon','Double Tap','Profession','City danger'],
            "KZ": ['Кардио','Жас','Азық-түлік','Ережелер','Топ','Қару','Қос атыс','Мамандық','Қала қауіпі'],
        }

        X = df_ml[feat_cols].values
        y = df_ml['survived'].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        rf.fit(X_train, y_train)
        acc = accuracy_score(y_test, rf.predict(X_test))

        # ── Метрики ──
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1rem 0;">
            <div class="metric-card"><div class="label">📊 {'Точность модели' if lang=='RU' else ('Model Accuracy' if lang=='EN' else 'Модель дәлдігі')}</div><div class="value green">{acc*100:.1f}%</div></div>
            <div class="metric-card"><div class="label">🌲 {'Деревьев' if lang=='RU' else ('Trees' if lang=='EN' else 'Ағаштар')}</div><div class="value amber">100</div></div>
            <div class="metric-card"><div class="label">📋 {'Обучающих примеров' if lang=='RU' else ('Training samples' if lang=='EN' else 'Оқыту үлгілері')}</div><div class="value">{len(X_train)}</div></div>
        </div>""", unsafe_allow_html=True)

        # ── Feature Importance ──
        st.markdown(f'<div class="section-header">📊 {"Feature Importance — Что важнее всего для выживания?" if lang=="RU" else ("Feature Importance — What matters most for survival?" if lang=="EN" else "Feature Importance — Тіршілік ету үшін не маңызды?")}</div>', unsafe_allow_html=True)

        fi = rf.feature_importances_
        names = feat_names.get(lang, feat_names["RU"])
        sorted_idx = np.argsort(fi)[::-1]

        fig_fi = go.Figure(go.Bar(
            x=[fi[i] for i in sorted_idx],
            y=[names[i] for i in sorted_idx],
            orientation='h',
            marker=dict(
                color=[fi[i] for i in sorted_idx],
                colorscale=[[0,'#550000'],[0.5,'#ff4444'],[1,'#44ff88']],
                showscale=False
            ),
            text=[f'{fi[i]*100:.1f}%' for i in sorted_idx],
            textposition='outside',
        ))
        fig_fi.update_layout(
            plot_bgcolor='#080808', paper_bgcolor='#080808',
            font=dict(color='#ccc', family='Oswald'),
            height=380,
            xaxis=dict(title='Importance', gridcolor='#161616', color='#666'),
            yaxis=dict(color='#aaa'),
            margin=dict(l=120, r=60, t=20, b=40)
        )
        st.plotly_chart(fig_fi, use_container_width=True)

        # ── Предсказание для текущего персонажа ──
        st.markdown(f'<div class="section-header">🎯 {"Предскажи для своего персонажа" if lang=="RU" else ("Predict for your character" if lang=="EN" else "Өз кейіпкерің үшін болжа")}</div>', unsafe_allow_html=True)

        mc1, mc2 = st.columns(2)
        with mc1:
            ml_cardio   = st.slider("Cardio" if lang=="EN" else ("Кардио" if lang=="RU" else "Кардио"), 1, 10, 5, key="ml_cardio")
            ml_age      = st.slider("Age" if lang=="EN" else ("Возраст" if lang=="RU" else "Жас"), 10, 70, 25, key="ml_age")
            ml_food     = st.slider("Food (days)" if lang=="EN" else ("Еда (дней)" if lang=="RU" else "Азық (күн)"), 0, 30, 5, key="ml_food")
            ml_rules    = st.slider("Rules known" if lang=="EN" else ("Правил выживания" if lang=="RU" else "Ережелер"), 0, 10, 5, key="ml_rules")
        with mc2:
            ml_group    = st.slider("Group size" if lang=="EN" else ("Размер группы" if lang=="RU" else "Топ мөлшері"), 1, 10, 3, key="ml_group")
            ml_weapon   = st.toggle("⚔️ Weapon" if lang=="EN" else ("⚔️ Есть оружие" if lang=="RU" else "⚔️ Қару бар"), key="ml_wpn")
            ml_dtap     = st.toggle("🔫 Double Tap", key="ml_dtap")
            ml_prof     = st.selectbox("Profession" if lang=="EN" else ("Профессия" if lang=="RU" else "Мамандық"),
                options=list(range(8)),
                format_func=lambda x: ["Военный/Полицейский","Врач","Фермер/Охотник","Спортсмен","Инженер/IT","Учитель","Менеджер","Блогер"][x],
                key="ml_prof")
            ml_city     = st.slider("City danger" if lang=="EN" else ("Опасность города" if lang=="RU" else "Қала қауіпі"), 0.4, 1.0, 0.6, 0.05, key="ml_city")

        ml_input = np.array([[ml_cardio, ml_age, ml_food, ml_rules, ml_group,
                               int(ml_weapon), int(ml_dtap), ml_prof, ml_city]])
        ml_pred  = rf.predict(ml_input)[0]
        ml_prob  = rf.predict_proba(ml_input)[0][1] * 100

        color = "#44ff88" if ml_prob >= 60 else ("#ffaa44" if ml_prob >= 40 else "#ff4444")
        verdict_ml = ("✅ ВЫЖИВЕШЬ!" if lang=="RU" else ("✅ YOU'LL SURVIVE!" if lang=="EN" else "✅ ТІРШІЛІК ЕТЕСІҢ!")) if ml_pred==1 else \
                     ("💀 НЕ ВЫЖИВЕШЬ" if lang=="RU" else ("💀 YOU WON'T SURVIVE" if lang=="EN" else "💀 ТІРШІЛІК ЕТПЕЙСІҢ"))

        st.markdown(f"""
        <div style="background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:1.5rem;text-align:center;margin-top:1rem;">
            <div style="font-size:.85rem;color:#555;margin-bottom:.5rem;font-family:'Share Tech Mono',monospace;">
                {'ПРОГНОЗ RANDOM FOREST' if lang=='RU' else ('RANDOM FOREST PREDICTION' if lang=='EN' else 'RANDOM FOREST БОЛЖАМЫ')}
            </div>
            <div style="font-size:3rem;font-weight:700;color:{color};font-family:'Creepster',cursive;">{ml_prob:.1f}%</div>
            <div style="font-size:1.2rem;color:{color};margin:.5rem 0;">{verdict_ml}</div>
            <div style="background:#1a1a1a;border-radius:20px;height:18px;overflow:hidden;margin:.75rem 0;">
                <div style="width:{ml_prob}%;height:100%;background:linear-gradient(90deg,#880000,{color});border-radius:20px;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        # XAI объяснение
        top3_idx = np.argsort(fi)[::-1][:3]
        top3_names = [names[i] for i in top3_idx]
        st.markdown(f"""
        <div class="banner banner-blue" style="margin-top:1rem;">
            🧠 <b>XAI (Explainable AI):</b> {'Топ-3 важнейших фактора: ' if lang=='RU' else ('Top-3 most important factors: ' if lang=='EN' else 'Үздік-3 маңызды фактор: ')}
            <b>{top3_names[0]}</b> ({fi[top3_idx[0]]*100:.1f}%),
            <b>{top3_names[1]}</b> ({fi[top3_idx[1]]*100:.1f}%),
            <b>{top3_names[2]}</b> ({fi[top3_idx[2]]*100:.1f}%)
        </div>""", unsafe_allow_html=True)

    except ImportError:
        st.markdown('<div class="banner banner-yellow">⚠️ Установи scikit-learn: <b>pip install scikit-learn</b></div>', unsafe_allow_html=True)
