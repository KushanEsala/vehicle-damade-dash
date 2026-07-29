from __future__ import annotations

import streamlit as st


def inject_custom_theme() -> None:
    """Apply the branded Apex Assurance application shell."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0');

        :root {
          --canvas: #F4F7F9;
          --surface: #FFFFFF;
          --surface-soft: #EDF3F6;
          --navy: #102A43;
          --navy-deep: #091D2E;
          --blue: #1F5A7A;
          --teal: #0F766E;
          --amber: #B96A16;
          --danger: #B42335;
          --ink: #18212B;
          --muted: #637381;
          --line: #D8E2E8;
          --shadow: 0 12px 35px rgba(16, 42, 67, .08);
        }

        /* Remove Streamlit product chrome and development controls. */
        #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
        [data-testid="stStatusWidget"], [data-testid="stHeaderActionElements"],
        [data-testid="stAppDeployButton"], button[title="View fullscreen"] {
          display: none !important;
          visibility: hidden !important;
        }
        [data-testid="stHeader"] {
          background: transparent !important;
          height: 0 !important;
        }

        html, body, [class*="css"], .stApp {
          font-family: "DM Sans", sans-serif;
          color: var(--ink);
        }
        .stApp { background: var(--canvas); }
        .main .block-container {
          max-width: 1380px;
          padding-top: 2rem;
          padding-bottom: 4rem;
        }
        h1, h2, h3, .brand-name {
          font-family: "Manrope", sans-serif !important;
          letter-spacing: -.025em;
          color: var(--navy) !important;
        }

        [data-testid="stSidebar"] {
          background: var(--navy-deep);
          border-right: 1px solid rgba(255,255,255,.08);
          min-width: 17rem;
        }
        [data-testid="stSidebarContent"] { padding-top: .7rem; }
        [data-testid="stSidebar"] * { color: #DCE8EF; }
        [data-testid="stSidebarNav"] { padding-top: .35rem; }
        [data-testid="stSidebarNav"] span { font-size: .91rem; }
        [data-testid="stSidebarNav"] a {
          border-radius: 9px;
          margin: 2px 10px;
          padding: .55rem .7rem;
          transition: background .16s ease, color .16s ease;
        }
        [data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,.07); }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
          background: #EAF4F3 !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] * {
          color: var(--navy-deep) !important;
          font-weight: 700;
        }
        [data-testid="stSidebarNav"] header {
          color: #7791A2 !important;
          font-size: .68rem;
          font-weight: 800;
          letter-spacing: .13em;
          text-transform: uppercase;
        }
        .material-symbols-rounded {
          font-family: "Material Symbols Rounded" !important;
          font-weight: normal;
          font-style: normal;
          font-size: 22px;
          line-height: 1;
          letter-spacing: normal;
          text-transform: none;
          display: inline-block;
          white-space: nowrap;
          word-wrap: normal;
          direction: ltr;
          -webkit-font-feature-settings: "liga";
          -webkit-font-smoothing: antialiased;
        }
        .brand-lockup {
          display: flex;
          gap: .75rem;
          align-items: center;
          padding: .85rem 1rem 1.1rem;
          margin: 0 .35rem .35rem;
          border-bottom: 1px solid rgba(255,255,255,.11);
        }
        .brand-mark {
          width: 38px; height: 38px; border-radius: 10px;
          display: grid; place-items: center;
          color: #EAF4F3;
          background: var(--teal);
          box-shadow: 0 8px 20px rgba(15,118,110,.28);
        }
        .brand-name { color: #FFFFFF !important; font-size: .88rem; font-weight: 800; letter-spacing: .06em; }
        .brand-subtitle { color: #87A0AF !important; font-size: .72rem; margin-top: 2px; }
        .appearance-label {
          display:flex; align-items:center; gap:.45rem;
          margin:1rem 1rem .2rem;
          color:#87A0AF !important;
          font-size:.7rem; font-weight:800;
          letter-spacing:.09em; text-transform:uppercase;
        }
        .appearance-label * { color:#87A0AF !important; }
        .sidebar-account {
          display: flex; gap: .65rem; align-items: center;
          margin: 1.25rem .7rem .65rem; padding: .75rem;
          background: rgba(255,255,255,.05);
          border: 1px solid rgba(255,255,255,.08);
          border-radius: 10px;
        }
        .sidebar-account-icon { color: #76C7BD !important; }
        .sidebar-account-name { font-weight: 700; font-size: .86rem; color: #FFF !important; }
        .sidebar-account-role { color: #76C7BD !important; text-transform: uppercase; letter-spacing: .09em; font-size: .65rem; font-weight: 800; }

        div[data-testid="stMetric"], .erp-card {
          background: var(--surface);
          border: 1px solid var(--line);
          border-radius: 14px;
          box-shadow: var(--shadow);
        }
        div[data-testid="stMetric"] { padding: 1rem 1.15rem; }
        div[data-testid="stMetricValue"] { color: var(--navy); font-family: "Manrope", sans-serif; font-weight: 800; }
        div[data-testid="stMetricLabel"] { color: var(--muted); font-size: .82rem; }
        div[data-testid="stMetricLabel"] * { color: var(--muted) !important; }
        .erp-card { padding: 1.25rem 1.4rem; margin-bottom: 1rem; }
        .erp-card-header { color: var(--navy); font-family: "Manrope"; font-weight: 800; margin-bottom: .55rem; }

        .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
          border-radius: 9px;
          min-height: 2.65rem;
          font-weight: 700;
          border-color: #B9C9D3;
          transition: transform .15s ease, box-shadow .15s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
          transform: translateY(-1px);
          box-shadow: 0 7px 18px rgba(16,42,67,.12);
        }
        button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
          background: var(--navy) !important;
          border-color: var(--navy) !important;
          color: white !important;
        }
        div[data-baseweb="input"], div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] {
          background: white !important;
          border-color: #C9D6DE !important;
          border-radius: 9px !important;
        }
        .stTextInput .react-aria-TextField > div,
        .stTextArea .react-aria-TextField > div {
          background: white !important;
          border-color: #C9D6DE !important;
        }
        .stTextInput input, .stTextArea textarea {
          color: var(--ink) !important;
          -webkit-text-fill-color: var(--ink) !important;
        }
        .stTextInput label, .stTextArea label, .stSelectbox label,
        .stNumberInput label, .stFileUploader label {
          color: var(--ink) !important;
          font-weight: 600 !important;
        }
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primaryFormSubmit"] {
          background: var(--navy) !important;
          border-color: var(--navy) !important;
          color: white !important;
        }
        /* Theme every native Streamlit widget instead of only the page shell. */
        .main [data-testid="stWidgetLabel"] p,
        .main [data-testid="stWidgetLabel"] span,
        .main .stCheckbox label p,
        .main .stRadio label p,
        .main .stToggle label p {
          color: var(--ink) !important;
        }
        .main [data-baseweb="tab-list"] {
          background: transparent !important;
          border-bottom: 1px solid var(--line) !important;
        }
        .main [data-baseweb="tab"] {
          background: transparent !important;
          border-bottom-color: transparent !important;
        }
        .main [data-baseweb="tab"] p,
        .main [data-baseweb="tab"] span {
          color: var(--muted) !important;
        }
        .main [data-baseweb="tab"][aria-selected="true"] {
          border-bottom-color: var(--teal) !important;
        }
        .main [data-baseweb="tab"][aria-selected="true"] p,
        .main [data-baseweb="tab"][aria-selected="true"] span {
          color: var(--teal) !important;
          font-weight: 800 !important;
        }
        .main div[data-baseweb="select"] > div,
        .main .stSelectbox [role="button"],
        .main .stMultiSelect [role="button"] {
          background: var(--surface) !important;
          border-color: #C9D6DE !important;
          color: var(--ink) !important;
        }
        .main div[data-baseweb="select"] *,
        .main .stSelectbox [role="button"] *,
        .main .stMultiSelect [role="button"] * {
          color: var(--ink) !important;
        }
        [role="listbox"], [data-baseweb="popover"] {
          background: var(--surface) !important;
          color: var(--ink) !important;
        }
        [role="option"], [role="option"] * {
          color: var(--ink) !important;
        }
        [role="option"]:hover, [role="option"][aria-selected="true"] {
          background: var(--surface-soft) !important;
        }
        .main [data-testid="stExpander"],
        .main [data-testid="stFileUploaderDropzone"],
        .main [data-testid="stForm"] {
          background: var(--surface) !important;
          border-color: var(--line) !important;
        }
        .main [data-testid="stExpander"] summary *,
        .main [data-testid="stFileUploaderDropzone"] * {
          color: var(--ink) !important;
        }
        .main button[data-testid="stBaseButton-secondary"],
        .main button[data-testid="stBaseButton-secondaryFormSubmit"] {
          background: var(--surface) !important;
          border-color: var(--line) !important;
          color: var(--ink) !important;
        }
        .main button[data-testid="stBaseButton-secondary"] *,
        .main button[data-testid="stBaseButton-secondaryFormSubmit"] * {
          color: var(--ink) !important;
        }
        .main div[data-testid="stAlert"] {
          border: 1px solid var(--line) !important;
        }
        .main div[data-testid="stAlert"] p,
        .main div[data-testid="stAlert"] span {
          color: inherit !important;
        }
        [data-testid="stDataFrame"] {
          border: 1px solid var(--line);
          border-radius: 12px;
          overflow: hidden;
          background: white;
        }

        .badge { display:inline-flex; padding:.24rem .58rem; border-radius:999px; font-size:.7rem; font-weight:800; letter-spacing:.04em; text-transform:uppercase; }
        .badge-verified { background:#E7F6F2; color:#08756A; border:1px solid #B7E2D9; }
        .badge-caution { background:#FFF3E0; color:#9A5410; border:1px solid #F4D4A6; }
        .badge-danger { background:#FCEBED; color:#A72235; border:1px solid #F1C3CA; }
        .badge-analysis { background:#E8F1F8; color:#1F5A7A; border:1px solid #C5DCEA; }
        .badge-neutral { background:#EEF2F4; color:#5D6B78; border:1px solid #D7E0E5; }

        .evidence-rail {
          display:flex; align-items:center; justify-content:space-between; gap:.35rem;
          background:white; border:1px solid var(--line); border-radius:12px;
          padding:.75rem 1rem; margin-bottom:1.25rem; box-shadow:var(--shadow);
          overflow-x:auto;
        }
        .rail-step { white-space:nowrap; color:#738391; font-size:.78rem; font-weight:700; }
        .rail-step.active { color:var(--teal); }
        .rail-step.completed { color:var(--blue); }
        .rail-arrow { color:#B8C6CF; }

        .login-shell {
          max-width: 1080px; margin: 5vh auto 0; display:grid;
          grid-template-columns: 1.05fr .95fr; min-height: 620px;
          background:white; border:1px solid var(--line); border-radius:22px;
          overflow:hidden; box-shadow:0 28px 80px rgba(16,42,67,.16);
          animation: loginEnter .45s cubic-bezier(.2,.8,.2,1) both;
        }
        .login-story {
          padding:3.6rem; color:white;
          background: linear-gradient(145deg, #091D2E 0%, #123C56 63%, #0F766E 145%);
          position:relative;
        }
        .login-kicker { color:#79D0C4; letter-spacing:.16em; font-size:.72rem; font-weight:800; }
        .login-title { color:white !important; font-size:2.55rem; line-height:1.08; margin:1.15rem 0; }
        .login-copy { color:#BCD0DC; max-width:32rem; line-height:1.65; }
        .login-trust { margin-top:7rem; padding-top:1.2rem; border-top:1px solid rgba(255,255,255,.15); color:#A9C0CD; font-size:.8rem; }
        .login-form-heading { text-align:center; margin:1.1rem 0 1.6rem; }
        .login-form-heading p { color:var(--muted); margin:.3rem 0 0; }
        .login-mobile-brand { display:none; }
        @keyframes loginEnter { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

        @media (max-width: 760px) {
          .main .block-container { padding:1rem .85rem 3rem; }
          [data-testid="stSidebar"] { min-width: 15rem; }
          .login-shell { display:block; min-height:0; margin:1.25rem 0 0; border-radius:16px; }
          .login-story { display:none; }
          .login-mobile-brand { display:block; text-align:center; margin:1rem 0; color:var(--teal); font-weight:800; letter-spacing:.08em; }
          .evidence-rail { justify-content:flex-start; }
        }
        @media (min-width: 761px) {
          [data-testid="stSidebar"] {
            left: 0 !important;
            transform: none !important;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after { animation-duration:.01ms !important; transition-duration:.01ms !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("dark_mode", True):
        st.markdown(
            """
            <style>
            :root {
              --canvas:#07111B;
              --surface:#0D1B27;
              --surface-soft:#132737;
              --navy:#E8F2F7;
              --navy-deep:#06121D;
              --blue:#65A9CF;
              --teal:#55C7B6;
              --amber:#F1B461;
              --danger:#FF8291;
              --ink:#E8F0F4;
              --muted:#9AAEBA;
              --line:#243A49;
              --shadow:0 14px 38px rgba(0,0,0,.26);
            }
            .stApp { color-scheme:dark; }
            [data-testid="stSidebar"] { background:#06121D; }
            div[data-testid="stMetric"], .erp-card, [data-testid="stDataFrame"],
            .evidence-rail, .login-shell {
              background:var(--surface) !important;
            }
            .stTextInput .react-aria-TextField > div,
            .stTextArea .react-aria-TextField > div,
            div[data-baseweb="select"] > div {
              background:#102330 !important;
              border-color:#314959 !important;
            }
            .stTextInput input, .stTextArea textarea {
              color:var(--ink) !important;
              -webkit-text-fill-color:var(--ink) !important;
            }
            div[data-testid="stAlert"] { color:var(--ink); }
            code { background:#08131D !important; color:#6ED6C5 !important; }
            .login-story {
              background:linear-gradient(145deg,#03101A 0%,#0A2A3C 65%,#0F665F 145%);
            }
            button[data-testid="stBaseButton-primary"],
            button[data-testid="stBaseButton-primaryFormSubmit"] {
              background:#2C7A78 !important;
              border-color:#4DA69D !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            :root {
              --canvas:#F4F7F9;
              --surface:#FFFFFF;
              --surface-soft:#EDF3F6;
              --navy:#102A43;
              --navy-deep:#091D2E;
              --blue:#1F5A7A;
              --teal:#0F766E;
              --amber:#B96A16;
              --danger:#B42335;
              --ink:#18212B;
              --muted:#637381;
              --line:#D8E2E8;
              --shadow:0 12px 35px rgba(16,42,67,.08);
            }
            .stApp {
              color-scheme:light !important;
              background:#F4F7F9 !important;
              color:#18212B !important;
            }
            [data-testid="stSidebar"] { background:#091D2E !important; }
            div[data-testid="stMetric"], .erp-card, [data-testid="stDataFrame"],
            .evidence-rail, .login-shell, .main [data-testid="stForm"],
            .main [data-testid="stExpander"], .main [data-testid="stFileUploaderDropzone"] {
              background:#FFFFFF !important;
              border-color:#D8E2E8 !important;
            }
            div[data-testid="stMetricValue"] *,
            div[data-testid="stMetricValue"] {
              color:#102A43 !important;
            }
            div[data-testid="stMetricLabel"] *,
            .main [data-testid="stWidgetLabel"] *,
            .main .stCheckbox label *,
            .main .stRadio label *,
            .main .stToggle label * {
              color:#637381 !important;
            }
            .stTextInput .react-aria-TextField > div,
            .stTextArea .react-aria-TextField > div,
            .main div[data-baseweb="select"] > div,
            .main .stSelectbox [role="button"],
            .main .stMultiSelect [role="button"] {
              background:#FFFFFF !important;
              border-color:#C9D6DE !important;
              color:#18212B !important;
            }
            .stTextInput input, .stTextArea textarea,
            .main div[data-baseweb="select"] *,
            .main .stSelectbox [role="button"] *,
            .main .stMultiSelect [role="button"] * {
              color:#18212B !important;
              -webkit-text-fill-color:#18212B !important;
            }
            .main [data-baseweb="tab"] p,
            .main [data-baseweb="tab"] span { color:#637381 !important; }
            .main [data-baseweb="tab"][aria-selected="true"] p,
            .main [data-baseweb="tab"][aria-selected="true"] span {
              color:#0F766E !important;
            }
            [role="listbox"], [data-baseweb="popover"] {
              background:#FFFFFF !important;
              color:#18212B !important;
            }
            [role="option"], [role="option"] * { color:#18212B !important; }
            [role="option"]:hover, [role="option"][aria-selected="true"] {
              background:#EDF3F6 !important;
            }
            .main button[data-testid="stBaseButton-secondary"],
            .main button[data-testid="stBaseButton-secondaryFormSubmit"] {
              background:#FFFFFF !important;
              border-color:#C9D6DE !important;
              color:#18212B !important;
            }
            .main button[data-testid="stBaseButton-secondary"] *,
            .main button[data-testid="stBaseButton-secondaryFormSubmit"] * {
              color:#18212B !important;
            }
            code { background:#E7EDF1 !important; color:#075E58 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
