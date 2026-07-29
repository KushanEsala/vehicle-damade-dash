from __future__ import annotations

import io
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import sys
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from ml.pipeline import get_pipeline
from ui.layout import render_page_header

render_page_header("YOLO Model Test Workbench", "Upload any vehicle photo to test damage detection & vehicle confirmation models", "MODEL TESTER", allowed_roles=["admin"])

pipeline = get_pipeline()

uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Source Image")
        st.image(pil_image, use_container_width=True)

    with st.spinner("Processing image with YOLO models..."):
        try:
            result = pipeline.process(image_bytes)

            with col2:
                st.subheader("Model Annotations")
                annotated_bgr = result["annotated_image"]
                annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
                st.image(annotated_rgb, use_container_width=True)

            st.divider()
            st.subheader("Inspection Diagnostics")
            d1, d2, d3 = st.columns(3)
            d1.metric("Vehicle Confirmed", "YES" if result["vehicle_confirmed"] else "NO")
            d2.metric("Vehicle Class / Conf", f"{result['vehicle_detection']['vehicle_class']} ({result['vehicle_detection']['confidence']:.1%})" if result['vehicle_detection'] else "None")
            d3.metric("Accepted Damage Count", len(result["accepted_damages"]))

            if result["accepted_damages"]:
                st.markdown("### Accepted Damage Predictions")
                table_rows = []
                for d in result["accepted_damages"]:
                    table_rows.append({
                        "Class": d["final_damage_class"],
                        "Confidence": f"{d['confidence']:.1%}",
                        "Severity": d["severity"].title(),
                        "Estimated Cost": f"LKR {d['estimated_cost']:,.2f}",
                    })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Inference pipeline execution error: {e}")
