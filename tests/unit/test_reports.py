from __future__ import annotations

import io

from PIL import Image

from reports.pdf_builder import PDFReportBuilder


def test_pdf_report_builder_creates_valid_pdf() -> None:
    marked_image = io.BytesIO()
    Image.new("RGB", (640, 360), color=(24, 72, 90)).save(marked_image, format="PNG")
    marked_image.seek(0)
    snapshot = {
        "report_number": "RPT-VDA-TEST-R01",
        "analysis_number": "VDA-TEST",
        "generated_at": "2026-07-30 00:00 UTC",
        "company": {
            "company_name": "Apex Vehicle Assurance",
            "phone": "+94 11 000 0000",
            "email": "claims@example.test",
            "tax_label": "VAT",
            "report_footer": "Human review is required.",
        },
        "customer": {
            "full_name": "Test Policyholder",
            "customer_code": "CUS-TEST",
            "nic_or_passport": "TEST123",
            "phone_primary": "+94 77 000 0000",
        },
        "vehicle": {
            "registration_number": "ABC-1234",
            "make": "Toyota",
            "model": "Aqua",
            "manufactured_year": 2020,
            "colour": "White",
            "vehicle_type": "Car",
        },
        "damages": [
            {
                "final_damage_class": "dent",
                "vehicle_part": "Front door",
                "severity": "moderate",
                "confidence": 0.82,
                "description": "Dent across the front door panel.",
                "estimated_cost": 25000,
            }
        ],
        "_annotated_image_path": marked_image,
        "currency_code": "LKR",
        "totals": {"subtotal": 25000, "tax": 3750, "discount": 0, "total": 28750},
    }
    output = io.BytesIO()
    PDFReportBuilder.build_report_pdf(snapshot, output)
    content = output.getvalue()
    assert content.startswith(b"%PDF")
    assert len(content) > 2500
