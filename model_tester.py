from __future__ import annotations

import io
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

try:
    import torch
    from ultralytics import YOLO
    TORCH_AVAILABLE = True
except Exception as _torch_err:
    TORCH_AVAILABLE = False
    torch = None
    YOLO = None



PROJECT_DIR = Path(__file__).resolve().parent
RUN_DIR = PROJECT_DIR / "Runscomplete" / "runs" / "vehicle_damage_seg-2"
DAMAGE_MODEL_PATH = RUN_DIR / "weights" / "best.pt"
RESULTS_CSV = RUN_DIR / "results.csv"
DATASET_YAML = PROJECT_DIR / "prepared_dataset.yaml"

VEHICLE_MODEL_NAME = "yolov8n.pt"
VEHICLE_CLASS_IDS = {2, 3, 5, 7}  # car, motorcycle, bus, truck in COCO
CLASS_COLORS = {
    "scratch": (255, 188, 66),
    "dent": (70, 190, 255),
    "tear": (255, 99, 132),
    "missing_part": (176, 116, 255),
    "broken_lamp": (255, 224, 92),
    "puncture": (76, 220, 155),
    "broken_glass": (70, 225, 235),
}


st.set_page_config(
    page_title="Vehicle Damage Inspector",
    page_icon="🚘",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #090d12; color: #e9f0f5; }
      [data-testid="stHeader"] { background: rgba(9, 13, 18, 0.82); }
      .hero {
        padding: 2rem 2.2rem;
        border: 1px solid #26313d;
        border-radius: 22px;
        background:
          radial-gradient(circle at 92% 10%, rgba(44, 207, 165, .18), transparent 30%),
          linear-gradient(145deg, #121a23, #0d131a);
        margin-bottom: 1.2rem;
      }
      .eyebrow {
        color: #50dbb7; font-size: .76rem; font-weight: 800;
        letter-spacing: .16em; text-transform: uppercase;
      }
      .hero h1 {
        margin: .4rem 0 .55rem; font-size: clamp(2rem, 4vw, 3.4rem);
        letter-spacing: -.045em; line-height: 1;
      }
      .hero p { max-width: 760px; color: #aab8c5; font-size: 1.05rem; margin: 0; }
      div[data-testid="stMetric"] {
        background: #101820; border: 1px solid #26313d;
        padding: 1rem; border-radius: 16px;
      }
      div[data-testid="stFileUploader"] {
        border: 1px dashed #3e5668; border-radius: 18px; padding: .5rem;
        background: #0d141b;
      }
      .good { color: #50dbb7; font-weight: 700; }
      .warn { color: #ffbd59; font-weight: 700; }
      .small-note { color: #91a1ae; font-size: .88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">YOLOv8 segmentation · local analysis</div>
      <h1>Vehicle Damage Inspector</h1>
      <p>Upload a vehicle photo to confirm that a supported vehicle is present,
      locate visible damage, inspect confidence scores and review the trained
      model's validation record.</p>
    </section>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_damage_model() -> YOLO | None:
    if not TORCH_AVAILABLE:
        return None
    if not DAMAGE_MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model not found: {DAMAGE_MODEL_PATH}")
    return YOLO(str(DAMAGE_MODEL_PATH))


@st.cache_resource
def load_vehicle_model() -> YOLO | None:
    if not TORCH_AVAILABLE:
        return None
    return YOLO(VEHICLE_MODEL_NAME)


def runtime_device() -> int | str:
    if not TORCH_AVAILABLE or torch is None:
        return "cpu"
    return 0 if torch.cuda.is_available() else "cpu"


def intersection_ratio(damage_box: np.ndarray, vehicle_box: np.ndarray) -> float:
    dx1, dy1, dx2, dy2 = damage_box
    vx1, vy1, vx2, vy2 = vehicle_box
    ix1, iy1 = max(dx1, vx1), max(dy1, vy1)
    ix2, iy2 = min(dx2, vx2), min(dy2, vy2)
    intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    damage_area = max(1.0, (dx2 - dx1) * (dy2 - dy1))
    return intersection / damage_area


def damage_matches_vehicle(damage_box: np.ndarray, vehicle_boxes: list[np.ndarray]) -> bool:
    if not vehicle_boxes:
        return False
    x1, y1, x2, y2 = damage_box
    center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
    for vehicle_box in vehicle_boxes:
        vx1, vy1, vx2, vy2 = vehicle_box
        center_inside = vx1 <= center_x <= vx2 and vy1 <= center_y <= vy2
        if center_inside or intersection_ratio(damage_box, vehicle_box) >= 0.20:
            return True
    return False


def annotate(
    image: np.ndarray,
    vehicle_rows: list[dict],
    damage_rows: list[dict],
) -> np.ndarray:
    canvas = cv2.cvtColor(image.copy(), cv2.COLOR_RGB2BGR)
    mask_layer = canvas.copy()

    for row in damage_rows:
        color = CLASS_COLORS.get(row["damage"], (255, 255, 255))
        bgr = (color[2], color[1], color[0])
        polygon = row.get("polygon")
        if polygon is not None and len(polygon) >= 3:
            points = np.asarray(polygon, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(mask_layer, [points], bgr)

    canvas = cv2.addWeighted(mask_layer, 0.34, canvas, 0.66, 0)

    for row in vehicle_rows:
        x1, y1, x2, y2 = map(int, row["box"])
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (155, 222, 80), 2)
        label = f'{row["vehicle"]} {row["confidence"]:.0%}'
        cv2.putText(canvas, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (155, 222, 80), 2)

    for row in damage_rows:
        x1, y1, x2, y2 = map(int, row["box"])
        rgb = CLASS_COLORS.get(row["damage"], (255, 255, 255))
        bgr = (rgb[2], rgb[1], rgb[0])
        polygon = row.get("polygon")
        if polygon is not None and len(polygon) >= 3:
            points = np.asarray(polygon, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(canvas, [points], True, bgr, 2)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), bgr, 2)
        label = f'{row["damage"].replace("_", " ")} {row["confidence"]:.0%}'
        text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.58, 2)
        top = max(0, y1 - text_size[1] - 12)
        cv2.rectangle(canvas, (x1, top), (x1 + text_size[0] + 10, y1), bgr, -1)
        cv2.putText(canvas, label, (x1 + 5, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (10, 14, 18), 2)

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)


def analyze_image(
    image: np.ndarray,
    damage_confidence: float,
    vehicle_confidence: float,
    require_vehicle: bool,
) -> tuple[np.ndarray, list[dict], list[dict], list[dict]]:
    v_model = load_vehicle_model()
    d_model = load_damage_model()

    if v_model is None or d_model is None:
        # Fallback when PyTorch native DLL cannot be loaded
        return image.copy(), [], [], []

    device = runtime_device()
    vehicle_result = v_model.predict(
        image,
        conf=vehicle_confidence,
        iou=0.50,
        device=device,
        verbose=False,
    )[0]

    vehicle_rows: list[dict] = []
    vehicle_boxes: list[np.ndarray] = []
    if vehicle_result.boxes is not None:
        for box, confidence, class_id in zip(
            vehicle_result.boxes.xyxy.cpu().numpy(),
            vehicle_result.boxes.conf.cpu().numpy(),
            vehicle_result.boxes.cls.cpu().numpy().astype(int),
        ):
            if class_id in VEHICLE_CLASS_IDS:
                vehicle_boxes.append(box)
                vehicle_rows.append(
                    {
                        "vehicle": vehicle_result.names[class_id],
                        "confidence": float(confidence),
                        "box": box,
                    }
                )

    damage_result = d_model.predict(
        image,
        conf=damage_confidence,
        iou=0.50,
        retina_masks=True,
        device=device,
        verbose=False,
    )[0]

    accepted: list[dict] = []
    rejected: list[dict] = []
    polygons = damage_result.masks.xy if damage_result.masks is not None else []
    if damage_result.boxes is not None:
        boxes = damage_result.boxes.xyxy.cpu().numpy()
        confidences = damage_result.boxes.conf.cpu().numpy()
        class_ids = damage_result.boxes.cls.cpu().numpy().astype(int)
        for index, (box, confidence, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            row = {
                "damage": damage_result.names[class_id],
                "confidence": float(confidence),
                "box": box,
                "polygon": polygons[index] if index < len(polygons) else None,
            }
            if not require_vehicle or damage_matches_vehicle(box, vehicle_boxes):
                accepted.append(row)
            else:
                rejected.append(row)

    return annotate(image, vehicle_rows, accepted), vehicle_rows, accepted, rejected


def validation_summary() -> pd.Series | None:
    if not RESULTS_CSV.is_file():
        return None
    results = pd.read_csv(RESULTS_CSV)
    metric = "metrics/mAP50-95(M)"
    return results.loc[results[metric].idxmax()]


test_tab, validation_tab = st.tabs(["Test an image", "Model validation"])

with test_tab:
    with st.sidebar:
        st.subheader("Detection controls")
        damage_confidence = st.slider("Damage confidence", 0.10, 0.90, 0.30, 0.05)
        vehicle_confidence = st.slider("Vehicle confidence", 0.10, 0.90, 0.25, 0.05)
        require_vehicle = st.toggle("Require vehicle confirmation", value=True)
        st.caption(
            "Vehicle confirmation blocks damage predictions that do not overlap a detected car, "
            "motorcycle, bus or truck. Disable it for tightly cropped close-ups."
        )
        st.divider()
        device_name = torch.cuda.get_device_name(0) if (TORCH_AVAILABLE and torch is not None and torch.cuda.is_available()) else "CPU"
        st.markdown(f"**Runtime:** {device_name}")
        st.markdown(f"**Damage model:** `{DAMAGE_MODEL_PATH.name}`")

    uploaded = st.file_uploader(
        "Upload a JPG, JPEG, PNG or WEBP vehicle image",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=False,
    )

    if uploaded is None:
        st.info("Upload a vehicle image to begin. The image stays on this computer.")
    else:
        try:
            pil_image = Image.open(uploaded).convert("RGB")
            image_array = np.asarray(pil_image)
        except Exception as error:
            st.error(f"Could not read this image: {error}")
            st.stop()

        analyze = st.button("Analyze vehicle damage", type="primary", width="stretch")
        if analyze:
            with st.spinner("Confirming vehicle and segmenting visible damage…"):
                annotated, vehicles, damages, rejected = analyze_image(
                    image_array,
                    damage_confidence,
                    vehicle_confidence,
                    require_vehicle,
                )

            vehicle_confirmed = bool(vehicles)
            max_confidence = max((item["confidence"] for item in damages), default=0.0)
            metric_columns = st.columns(4)
            metric_columns[0].metric("Vehicle check", "Confirmed" if vehicle_confirmed else "Not confirmed")
            metric_columns[1].metric("Vehicles", len(vehicles))
            metric_columns[2].metric("Damage regions", len(damages))
            metric_columns[3].metric("Top confidence", f"{max_confidence:.0%}" if damages else "—")

            if require_vehicle and not vehicle_confirmed:
                st.warning(
                    "No supported vehicle was confidently detected. Damage predictions were withheld. "
                    "For a close-up vehicle crop, lower vehicle confidence or disable vehicle confirmation."
                )
            elif not damages:
                st.info("No damage region exceeded the selected confidence threshold.")
            else:
                st.success(f"Vehicle confirmed. {len(damages)} damage region(s) passed validation.")

            original_column, result_column = st.columns(2)
            with original_column:
                st.image(image_array, caption="Original", width="stretch")
            with result_column:
                st.image(annotated, caption="Validated damage overlay", width="stretch")

            if damages:
                table = pd.DataFrame(
                    {
                        "Damage": [row["damage"].replace("_", " ").title() for row in damages],
                        "Confidence": [f'{row["confidence"]:.1%}' for row in damages],
                    }
                )
                st.dataframe(table, hide_index=True, width="stretch")

                output = io.BytesIO()
                Image.fromarray(annotated).save(output, format="PNG")
                st.download_button(
                    "Download annotated result",
                    data=output.getvalue(),
                    file_name="vehicle_damage_result.png",
                    mime="image/png",
                    width="stretch",
                )

            if rejected:
                st.caption(
                    f"{len(rejected)} prediction(s) were rejected because they did not overlap a confirmed vehicle."
                )

with validation_tab:
    st.subheader("Saved validation record")
    st.caption(
        "These values come from the held-out validation split used during training. "
        "They describe the model, not the uploaded image."
    )
    best_row = validation_summary()
    if best_row is None:
        st.warning("Training result history was not found.")
    else:
        columns = st.columns(4)
        columns[0].metric("Best epoch", int(best_row["epoch"]))
        columns[1].metric("Mask precision", f'{best_row["metrics/precision(M)"]:.1%}')
        columns[2].metric("Mask recall", f'{best_row["metrics/recall(M)"]:.1%}')
        columns[3].metric("Mask mAP50–95", f'{best_row["metrics/mAP50-95(M)"]:.1%}')

        secondary = st.columns(3)
        secondary[0].metric("Mask mAP50", f'{best_row["metrics/mAP50(M)"]:.1%}')
        secondary[1].metric("Box mAP50", f'{best_row["metrics/mAP50(B)"]:.1%}')
        secondary[2].metric("Box mAP50–95", f'{best_row["metrics/mAP50-95(B)"]:.1%}')

    plot_columns = st.columns(2)
    for column, filename, caption in (
        (plot_columns[0], "results.png", "Training and validation history"),
        (plot_columns[1], "confusion_matrix_normalized.png", "Normalized confusion matrix"),
    ):
        path = RUN_DIR / filename
        if path.is_file():
            column.image(str(path), caption=caption, width="stretch")

    st.divider()
    st.subheader("Run validation again")
    if DATASET_YAML.is_file():
        st.caption(
            "This evaluates best.pt against the configured validation dataset. "
            "It may take several minutes on CPU."
        )
        if st.button("Run live model validation"):
            with st.spinner("Validating the model against the held-out images…"):
                metrics = load_damage_model().val(
                    data=str(DATASET_YAML),
                    split="val",
                    device=runtime_device(),
                    plots=False,
                    verbose=False,
                )
            live_columns = st.columns(4)
            live_columns[0].metric("Box mAP50", f"{metrics.box.map50:.1%}")
            live_columns[1].metric("Box mAP50–95", f"{metrics.box.map:.1%}")
            live_columns[2].metric("Mask mAP50", f"{metrics.seg.map50:.1%}")
            live_columns[3].metric("Mask mAP50–95", f"{metrics.seg.map:.1%}")
    else:
        st.info("Live validation is unavailable because prepared_dataset.yaml was not found.")

st.caption(
    "Prototype decision support only. Predictions must be reviewed by a person and should not be used "
    "as the sole basis for repair, safety or insurance decisions."
)
