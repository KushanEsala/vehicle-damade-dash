from __future__ import annotations

from io import BytesIO
from typing import Any, BinaryIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from xml.sax.saxutils import escape


class PDFReportBuilder:
    """Builds a restrained, printable insurance damage assessment PDF."""

    NAVY = colors.HexColor("#102A43")
    BLUE = colors.HexColor("#1F5A7A")
    TEAL = colors.HexColor("#0F766E")
    INK = colors.HexColor("#18212B")
    MUTED = colors.HexColor("#5D6B78")
    LINE = colors.HexColor("#D7E0E7")
    PALE = colors.HexColor("#F3F7FA")

    @classmethod
    def build_report_pdf(cls, snapshot: dict[str, Any], stream: BinaryIO | BytesIO) -> None:
        styles = getSampleStyleSheet()
        title = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=cls.NAVY,
            alignment=TA_LEFT,
            spaceAfter=3 * mm,
        )
        eyebrow = ParagraphStyle(
            "Eyebrow",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=cls.TEAL,
            spaceAfter=1.5 * mm,
        )
        section = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=cls.NAVY,
            spaceBefore=5 * mm,
            spaceAfter=2.5 * mm,
        )
        body = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=cls.INK,
        )
        small = ParagraphStyle(
            "Small",
            parent=body,
            fontSize=7.5,
            leading=10,
            textColor=cls.MUTED,
        )
        money = ParagraphStyle(
            "Money",
            parent=body,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        )

        company = snapshot.get("company", {})
        customer = snapshot.get("customer", {})
        vehicle = snapshot.get("vehicle", {})
        totals = snapshot.get("totals", {})
        currency = snapshot.get("currency_code", "LKR")

        doc = SimpleDocTemplate(
            stream,
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=15 * mm,
            bottomMargin=16 * mm,
            title=f"Damage Assessment {snapshot.get('report_number', '')}",
            author=company.get("company_name", "Vehicle Insurance ERP"),
        )

        story: list[Any] = [
            Paragraph("VEHICLE DAMAGE ASSESSMENT", eyebrow),
            Paragraph(company.get("company_name", "Vehicle Insurance Company"), title),
        ]

        header_data = [
            [
                Paragraph(
                    f"<b>Report</b><br/>{snapshot.get('report_number', 'Pending')}<br/>"
                    f"<b>Analysis</b><br/>{snapshot.get('analysis_number', '')}",
                    body,
                ),
                Paragraph(
                    f"<b>Generated</b><br/>{snapshot.get('generated_at', '')}<br/>"
                    f"<b>Contact</b><br/>{company.get('phone', '')} · {company.get('email', '')}",
                    body,
                ),
            ]
        ]
        story.append(cls._table(header_data, [85 * mm, 77 * mm], header=True))
        story.append(Paragraph("Policyholder and vehicle", section))
        details = [
            ["Policyholder", customer.get("full_name", "—"), "Customer ID", customer.get("customer_code", "—")],
            ["NIC / Passport", customer.get("nic_or_passport") or "—", "Phone", customer.get("phone_primary", "—")],
            ["Registration", vehicle.get("registration_number", "—"), "Vehicle", f"{vehicle.get('make', '')} {vehicle.get('model', '')}".strip()],
            ["Year / Colour", f"{vehicle.get('manufactured_year') or '—'} / {vehicle.get('colour', '—')}", "Type", vehicle.get("vehicle_type", "—")],
        ]
        story.append(cls._table(details, [28 * mm, 53 * mm, 28 * mm, 53 * mm]))

        annotated_image_path = snapshot.get("_annotated_image_path")
        if annotated_image_path:
            try:
                damage_image = Image(annotated_image_path)
                max_width, max_height = 162 * mm, 88 * mm
                scale = min(max_width / damage_image.imageWidth, max_height / damage_image.imageHeight)
                damage_image.drawWidth = damage_image.imageWidth * scale
                damage_image.drawHeight = damage_image.imageHeight * scale
                story.extend(
                    [
                        Paragraph("Marked vehicle damage", section),
                        damage_image,
                        Spacer(1, 2 * mm),
                        Paragraph("Detected damage areas are marked on the inspected vehicle image.", small),
                    ]
                )
            except Exception:
                # A report must still be produced if an older stored image is
                # unavailable. The findings and costs remain authoritative.
                pass

        story.append(Paragraph("Verified damage findings", section))
        damage_rows: list[list[Any]] = [["Damage", "Vehicle part", "Severity", "Confidence", "Estimated cost"]]
        damages = snapshot.get("damages") or []
        if damages:
            for damage in damages:
                confidence = damage.get("confidence")
                damage_rows.append(
                    [
                        Paragraph(
                            f"<b>{escape(str(damage.get('final_damage_class', '')).replace('_', ' ').title())}</b>"
                            f"<br/><font color='#5D6B78'>{escape(str(damage.get('description') or 'No additional description.'))}</font>",
                            body,
                        ),
                        damage.get("vehicle_part", "General panel"),
                        str(damage.get("severity", "")).title(),
                        f"{confidence:.1%}" if confidence is not None else "Manual",
                        Paragraph(f"{currency} {float(damage.get('estimated_cost', 0)):,.2f}", money),
                    ]
                )
        else:
            damage_rows.append(["No accepted damage findings", "", "", "", ""])
        story.append(cls._table(damage_rows, [35 * mm, 42 * mm, 27 * mm, 25 * mm, 33 * mm], first_row_header=True))

        story.append(Paragraph("Assessment total", section))
        total_rows = [
            ["Subtotal", f"{currency} {float(totals.get('subtotal', 0)):,.2f}"],
            [company.get("tax_label", "Tax"), f"{currency} {float(totals.get('tax', 0)):,.2f}"],
            ["Discount", f"{currency} {float(totals.get('discount', 0)):,.2f}"],
            ["Total estimated repair cost", f"{currency} {float(totals.get('total', 0)):,.2f}"],
        ]
        total_table = cls._table(total_rows, [106 * mm, 56 * mm])
        total_table.setStyle(TableStyle([("ALIGN", (1, 0), (1, -1), "RIGHT"), ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("TEXTCOLOR", (0, -1), (-1, -1), cls.NAVY), ("LINEABOVE", (0, -1), (-1, -1), 1, cls.TEAL)]))
        story.append(total_table)

        notes = snapshot.get("operator_notes")
        if notes:
            story.extend([Paragraph("Assessment notes", section), Paragraph(str(notes), body)])
        if snapshot.get("override_used"):
            story.extend(
                [
                    Paragraph("Review disclosure", section),
                    Paragraph(
                        f"Vehicle confirmation was reviewed and manually approved by an authorized operator. "
                        f"Reason: {snapshot.get('override_reason') or 'Recorded in the audit log.'}",
                        body,
                    ),
                ]
            )

        story.extend(
            [
                Spacer(1, 8 * mm),
                Paragraph(company.get("report_footer") or "This assessment supports human review and is not a repair authorization.", small),
                Paragraph("Generated from an immutable finalized assessment snapshot.", small),
            ]
        )
        doc.build(story, onFirstPage=cls._page_footer, onLaterPages=cls._page_footer)

    @classmethod
    def _table(
        cls,
        data: list[list[Any]],
        widths: list[float],
        *,
        header: bool = False,
        first_row_header: bool = False,
    ) -> Table:
        table = Table(data, colWidths=widths, repeatRows=1 if first_row_header else 0, hAlign="LEFT")
        commands: list[tuple[Any, ...]] = [
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("TEXTCOLOR", (0, 0), (-1, -1), cls.INK),
            ("GRID", (0, 0), (-1, -1), 0.45, cls.LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        if header:
            commands.extend([("BACKGROUND", (0, 0), (-1, -1), cls.PALE), ("BOX", (0, 0), (-1, -1), 0.8, cls.BLUE)])
        if first_row_header:
            commands.extend([("BACKGROUND", (0, 0), (-1, 0), cls.NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")])
        table.setStyle(TableStyle(commands))
        return table

    @classmethod
    def _page_footer(cls, canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setStrokeColor(cls.LINE)
        canvas.line(16 * mm, 11 * mm, 194 * mm, 11 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(cls.MUTED)
        canvas.drawString(16 * mm, 7 * mm, "Confidential insurance assessment")
        canvas.drawRightString(194 * mm, 7 * mm, f"Page {doc.page}")
        canvas.restoreState()
