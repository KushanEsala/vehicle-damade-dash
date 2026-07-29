from __future__ import annotations

import streamlit as st


def inject_custom_theme() -> None:
    """Injects standard dark automotive inspection CSS theme into Streamlit."""
    st.markdown(
        """
        <style>
          /* Core Canvas & Font */
          .stApp {
            background-color: #090D12;
            color: #E9F0F5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          }

          /* Header bar */
          [data-testid="stHeader"] {
            background: rgba(9, 13, 18, 0.88);
            backdrop-filter: blur(12px);
          }
          [data-testid="stSidebarNav"] {
            padding-top: 1rem;
          }
          [data-testid="stSidebarNav"] a {
            border-radius: 8px;
            margin-bottom: 2px;
            font-weight: 600;
          }

          /* Main Container Paddings */
          .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1320px;
          }

          /* Metric Cards */
          div[data-testid="stMetric"] {
            background: #101820;
            border: 1px solid #26313D;
            padding: 1.1rem 1.3rem;
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
          }
          div[data-testid="stMetricValue"] {
            color: #E9F0F5;
            font-weight: 700;
            font-size: 1.8rem;
          }
          div[data-testid="stMetricLabel"] {
            color: #91A1AE;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }

          /* Buttons */
          .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.18s ease-in-out;
          }
          .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1778B0, #105782);
            border: 1px solid #288AC2;
            color: #FFFFFF;
          }
          .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #1D8AC9, #13699D);
            border-color: #50DBB7;
          }

          /* Form Inputs */
          div[data-baseweb="input"] input, div[data-baseweb="select"] {
            background-color: #101820 !important;
            color: #E9F0F5 !important;
            border-color: #26313D !important;
            border-radius: 10px !important;
          }

          /* Tables */
          [data-testid="stDataFrame"] {
            border: 1px solid #26313D;
            border-radius: 12px;
            overflow: hidden;
          }

          /* Inspection Cards */
          .erp-card {
            background: #101820;
            border: 1px solid #26313D;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.2rem;
          }
          .erp-card-header {
            font-size: 1.15rem;
            font-weight: 700;
            color: #E9F0F5;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid #17222D;
            padding-bottom: 0.5rem;
          }

          /* Status Badges */
          .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }
          .badge-verified { background: rgba(80, 219, 183, 0.15); color: #50DBB7; border: 1px solid rgba(80, 219, 183, 0.35); }
          .badge-caution  { background: rgba(255, 189, 89, 0.15); color: #FFBD59; border: 1px solid rgba(255, 189, 89, 0.35); }
          .badge-danger   { background: rgba(255, 89, 100, 0.15); color: #FF5964; border: 1px solid rgba(255, 89, 100, 0.35); }
          .badge-analysis { background: rgba(70, 190, 255, 0.15); color: #46BEFF; border: 1px solid rgba(70, 190, 255, 0.35); }
          .badge-neutral  { background: rgba(145, 161, 174, 0.15); color: #91A1AE; border: 1px solid rgba(145, 161, 174, 0.35); }

          /* Inspection Evidence Rail */
          .evidence-rail {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #101820;
            border: 1px solid #26313D;
            border-radius: 14px;
            padding: 0.85rem 1.2rem;
            margin-bottom: 1.5rem;
          }
          .rail-step {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.88rem;
            font-weight: 600;
            color: #91A1AE;
          }
          .rail-step.active { color: #50DBB7; }
          .rail-step.completed { color: #46BEFF; }
          .rail-arrow { color: #26313D; font-size: 1.1rem; }

          /* Custom Alert Box */
          .erp-alert {
            padding: 1rem 1.2rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            font-size: 0.92rem;
          }
          .erp-alert-info { background: #101F2C; border-left: 4px solid #46BEFF; color: #D0ECFF; }
          .erp-alert-success { background: #0E241E; border-left: 4px solid #50DBB7; color: #D0F7EC; }
          .erp-alert-warning { background: #262012; border-left: 4px solid #FFBD59; color: #FFEBCB; }
          .erp-alert-danger { background: #261214; border-left: 4px solid #FF5964; color: #FFCDD1; }
        </style>
        """,
        unsafe_allow_html=True,
    )
