"""Draw the one-page VendorFlow workflow PDF (docs/VendorFlow_workflow.pdf)."""

from __future__ import annotations

import pymupdf

OUTPUT = "docs/VendorFlow_workflow.pdf"
WIDTH, HEIGHT = 842, 595  # A4 landscape, points

INK = (0.12, 0.16, 0.22)
MUTED = (0.42, 0.47, 0.53)
FAINT = (0.85, 0.87, 0.90)
PAPER = (1, 1, 1)
TEAL = (0.06, 0.46, 0.43)
TEAL_BG = (0.94, 0.98, 0.98)
GREEN = (0.02, 0.47, 0.34)
GREEN_BG = (0.93, 0.99, 0.96)
AMBER = (0.71, 0.33, 0.04)
AMBER_BG = (1.0, 0.98, 0.93)
RED = (0.73, 0.11, 0.11)
RED_BG = (0.99, 0.95, 0.95)
SLATE_BG = (0.965, 0.972, 0.98)


def text_width(text: str, size: float, bold: bool = False) -> float:
    return pymupdf.get_text_length(text, fontname="hebo" if bold else "helv", fontsize=size)


def wrap(text: str, max_width: float, size: float, bold: bool = False) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if text_width(candidate, size, bold) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def write(
    page: pymupdf.Page,
    x: float,
    y: float,
    text: str,
    size: float = 8,
    bold: bool = False,
    color: tuple[float, float, float] = INK,
    leading: float = 1.35,
) -> float:
    page.insert_text((x, y), text, fontname="hebo" if bold else "helv", fontsize=size, color=color)
    return y + size * leading


def block(
    page: pymupdf.Page,
    x: float,
    y: float,
    width: float,
    text: str,
    size: float = 7.2,
    bold: bool = False,
    color: tuple[float, float, float] = MUTED,
    leading: float = 1.45,
) -> float:
    for line in wrap(text, width, size, bold):
        y = write(page, x, y, line, size, bold, color, leading)
    return y


def box(
    page: pymupdf.Page,
    rect: pymupdf.Rect,
    fill: tuple[float, float, float] = PAPER,
    stroke: tuple[float, float, float] = FAINT,
    width: float = 0.8,
    radius: float = 0.12,
) -> None:
    try:
        page.draw_rect(rect, color=stroke, fill=fill, width=width, radius=radius)
    except TypeError:  # older PyMuPDF without rounded corners
        page.draw_rect(rect, color=stroke, fill=fill, width=width)


def arrow(
    page: pymupdf.Page,
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[float, float, float] = MUTED,
    head: float = 4.2,
) -> None:
    page.draw_line(start, end, color=color, width=0.9)
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 0.001)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    base_x, base_y = x2 - ux * head, y2 - uy * head
    page.draw_polyline(
        [
            (x2, y2),
            (base_x + px * head * 0.62, base_y + py * head * 0.62),
            (base_x - px * head * 0.62, base_y - py * head * 0.62),
            (x2, y2),
        ],
        color=color,
        fill=color,
        width=0.4,
        closePath=True,
    )


def eyebrow(page: pymupdf.Page, x: float, y: float, label: str, color: tuple[float, float, float] = MUTED) -> None:
    text = label.upper()
    write(page, x, y, text, 6.8, True, color)
    page.draw_line((x, y + 4), (x + text_width(text, 6.8, True) + 2, y + 4), color=color, width=0.6)


def build() -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=WIDTH, height=HEIGHT)
    page.draw_rect(pymupdf.Rect(0, 0, WIDTH, HEIGHT), color=PAPER, fill=PAPER)

    # ---------------- header ----------------
    page.draw_rect(pymupdf.Rect(0, 0, WIDTH, 4), color=TEAL, fill=TEAL)
    write(page, 34, 42, "VendorFlow", 21, True, INK)
    write(page, 34, 58, "End-to-end onboarding workflow", 9.6, False, MUTED)

    tag = "P0 · deterministic rules · fictional VF-DEMO data"
    page.insert_text(
        (WIDTH - 34 - text_width(tag, 7.4, True), 42), tag,
        fontname="hebo", fontsize=7.4, color=TEAL,
    )
    slogan = "Form is primary · the PDF is optional"
    page.insert_text(
        (WIDTH - 34 - text_width(slogan, 8), 58), slogan,
        fontname="helv", fontsize=8, color=MUTED,
    )
    page.draw_line((34, 70), (WIDTH - 34, 70), color=FAINT, width=0.9)

    # ---------------- column A: intake ----------------
    ax, aw = 34, 190
    eyebrow(page, ax, 92, "Intake")
    intake = [
        ("Spot-check vendor", "10 fictional records; each runs once before it is a genuine duplicate."),
        ("Editable form", "10 required fields, prefilled and free to change."),
        ("Optional PDF", "none · matching · conflicting, chosen per vendor."),
    ]
    y = 102
    for index, (title, detail) in enumerate(intake):
        height = 26 + len(wrap(detail, aw - 20, 6.9)) * 9.8
        box(page, pymupdf.Rect(ax, y, ax + aw, y + height), PAPER, FAINT)
        write(page, ax + 10, y + 15, title, 8.6, True, INK)
        block(page, ax + 10, y + 27, aw - 20, detail, 6.9)
        y += height
        if index < len(intake) - 1:
            arrow(page, (ax + aw / 2, y + 2), (ax + aw / 2, y + 9))
            y += 11

    note_y = y + 8
    box(page, pymupdf.Rect(ax, note_y, ax + aw, note_y + 32), TEAL_BG, TEAL_BG)
    block(page, ax + 9, note_y + 12, aw - 18, "No file is needed: the happy path still reaches Approved.", 6.8, False, TEAL)

    # form fields, two columns
    fields_y = note_y + 48
    write(page, ax, fields_y, "FORM FIELDS", 6.8, True, MUTED)
    fields = [
        "legal name", "country", "state code", "GSTIN", "PAN",
        "bank account name", "bank account number", "IFSC",
        "contact email", "vendor category",
    ]
    for index, field in enumerate(fields):
        col, row = index % 2, index // 2
        fx = ax + col * 96
        fy = fields_y + 14 + row * 11.5
        page.draw_circle((fx + 2.2, fy - 2.2), 1.5, color=FAINT, fill=FAINT)
        write(page, fx + 7, fy, field, 6.9, False, MUTED)

    legend_y = fields_y + 14 + 5 * 11.5 + 14
    page.draw_line((ax, legend_y), (ax + aw, legend_y), color=FAINT, width=0.6)
    legend = [
        (TEAL, "teal stage: forms the decision"),
        (GREEN, "approved"),
        (AMBER, "pending, needs follow-up"),
        (RED, "rejected"),
    ]
    for index, (color, label) in enumerate(legend):
        ly = legend_y + 12 + index * 10.5
        page.draw_rect(pymupdf.Rect(ax, ly - 5, ax + 8, ly + 1), color=color, fill=color, width=0)
        write(page, ax + 13, ly, label, 6.6, False, MUTED)

    # ---------------- column B: pipeline ----------------
    bx, bw = 268, 288
    eyebrow(page, bx, 92, "Pipeline · 7 stages · every run, in order")
    stages = [
        ("1", "Intake received", "Pydantic validates the form snapshot."),
        ("2", "Optional document extraction", "PyMuPDF text; skipped when no file is attached."),
        ("3", "Field validation", "GSTIN, PAN, IFSC, email, account, state code formats."),
        ("4", "Cross-field consistency", "Legal name vs bank name · GSTIN prefix vs state · PDF vs fields."),
        ("5", "Duplicate / blocklist", "Legal name or GSTIN in history · synthetic blocklist."),
        ("6", "Decision + follow-up", "Rules set the status and one concrete next step."),
        ("7", "Persist", "Supabase, or session fallback when unset."),
    ]
    top, row_h, gap = 102, 46, 9
    for index, (number, title, detail) in enumerate(stages):
        ry = top + index * (row_h + gap)
        highlight = index >= 5
        box(page, pymupdf.Rect(bx, ry, bx + bw, ry + row_h), TEAL_BG if highlight else PAPER, TEAL if highlight else FAINT, 0.9 if highlight else 0.8)
        page.draw_circle((bx + 16, ry + 15), 8.6, color=TEAL, fill=TEAL)
        page.insert_text(
            (bx + 16 - text_width(number, 8, True) / 2, ry + 18), number,
            fontname="hebo", fontsize=8, color=PAPER,
        )
        write(page, bx + 30, ry + 18, title, 8.9, True, INK)
        block(page, bx + 30, ry + 30, bw - 40, detail, 6.8)
        if index < len(stages) - 1:
            arrow(page, (bx + bw / 2, ry + row_h), (bx + bw / 2, ry + row_h + gap))

    # ---------------- column C: decision + outcome ----------------
    cx, cw = 588, 220
    eyebrow(page, cx, 92, "Decision")

    link_y = top + 5 * (row_h + gap) + row_h / 2
    page.draw_line((bx + bw, link_y), (cx - 12, link_y), color=TEAL, width=0.9)
    arrow(page, (cx - 12, link_y), (cx - 3, link_y), TEAL)

    rules = [
        ("1", "BLOCKLIST_MATCH", "Rejected"),
        ("2", "any failing check", "Pending"),
        ("3", "everything passes", "Approved"),
    ]
    write(page, cx, 104, "RULES, IN ORDER OF PRECEDENCE", 6.4, True, MUTED)
    for index, (number, condition, outcome) in enumerate(rules):
        ry = 116 + index * 11.5
        write(page, cx, ry, number, 6.6, True, MUTED)
        write(page, cx + 10, ry, condition, 6.9, False, INK)
        page.insert_text(
            (cx + cw - text_width(outcome, 6.9, True), ry), outcome,
            fontname="hebo", fontsize=6.9, color=INK,
        )

    statuses = [
        ("Approved", "Every check passed. No reason code is raised.", GREEN, GREEN_BG),
        (
            "Pending",
            (
                "GSTIN_FORMAT · PAN_FORMAT · IFSC_FORMAT · EMAIL_FORMAT · "
                "BANK_ACCOUNT_FORMAT · STATE_CODE_FORMAT · GSTIN_STATE_MISMATCH · "
                "NAME_VS_BANK_ACCOUNT · DUPLICATE_VENDOR · DOCUMENT_VS_FIELDS"
            ),
            AMBER, AMBER_BG,
        ),
        ("Rejected", "BLOCKLIST_MATCH only. The synthetic blocklist is the sole rejection rule.", RED, RED_BG),
    ]
    sy = 152
    for label, detail, color, bg in statuses:
        height = 24 + len(wrap(detail, cw - 22, 6.5)) * 8.8
        box(page, pymupdf.Rect(cx, sy, cx + cw, sy + height), bg, bg, 0.6)
        page.draw_rect(pymupdf.Rect(cx, sy, cx + 3.2, sy + height), color=color, fill=color, width=0)
        write(page, cx + 11, sy + 15, label, 9, True, color)
        if label == "Pending":
            note = "follow-up required"
            page.insert_text(
                (cx + cw - 11 - text_width(note, 6.2, True), sy + 15), note,
                fontname="hebo", fontsize=6.2, color=AMBER,
            )
        block(page, cx + 11, sy + 24, cw - 22, detail, 6.5, False, MUTED, 1.32)
        sy += height + 7

    eyebrow(page, cx, sy + 4, "Storage")
    box(page, pymupdf.Rect(cx, sy + 12, cx + cw, sy + 46), SLATE_BG, FAINT)
    block(page, cx + 10, sy + 23, cw - 20, "Supabase Postgres when secrets are set; otherwise a session-only fallback, stated in the UI.", 6.7)

    uy = sy + 60
    eyebrow(page, cx, uy, "Surface")
    box(page, pymupdf.Rect(cx, uy + 8, cx + cw, uy + 42), SLATE_BG, FAINT)
    block(page, cx + 10, uy + 19, cw - 20, "Live run, stage by stage · History of every decision · Overview dashboard.", 6.7)

    # ---------------- demo path band ----------------
    band_y = 494
    page.draw_line((34, band_y), (WIDTH - 34, band_y), color=FAINT, width=0.9)
    write(page, 34, band_y + 14, "FIVE-MINUTE DEMO PATH", 6.8, True, MUTED)

    demo = [
        ("Saffron · form only", "Approved", GREEN),
        ("Meridian · conflicting PDF", "Pending · DOCUMENT_VS_FIELDS", AMBER),
        ("Kiran · bank name differs", "Pending · NAME_VS_BANK_ACCOUNT", AMBER),
        ("Pinnacle · blocklist", "Rejected · BLOCKLIST_MATCH", RED),
    ]
    chip_w, chip_gap = 188, 8
    for index, (label, outcome, color) in enumerate(demo):
        dx = 34 + index * (chip_w + chip_gap)
        rect = pymupdf.Rect(dx, band_y + 22, dx + chip_w, band_y + 56)
        box(page, rect, PAPER, FAINT)
        page.draw_rect(pymupdf.Rect(dx, band_y + 22, dx + 3, band_y + 56), color=color, fill=color, width=0)
        write(page, dx + 10, band_y + 35, f"{index + 1}", 7, True, MUTED)
        write(page, dx + 20, band_y + 35, label, 7.4, True, INK)
        write(page, dx + 20, band_y + 47, outcome, 6.6, False, color)

    # ---------------- footer ----------------
    footer_y = HEIGHT - 22
    facts = (
        "Format checks only — no GSTN, PAN, IFSC or bank registry was queried  ·  no outbound email  ·  "
        "Gemini cannot approve or reject (GEMINI_ENABLED=false)"
    )
    write(page, 34, footer_y, facts, 6.8, False, MUTED)
    stamp = "github.com/harshanchez/VendorFlow"
    page.insert_text(
        (WIDTH - 34 - text_width(stamp, 6.8), footer_y), stamp,
        fontname="helv", fontsize=6.8, color=MUTED,
    )

    doc.set_metadata(
        {
            "title": "VendorFlow — end-to-end onboarding workflow",
            "author": "Harsh",
            "subject": "Deterministic vendor onboarding demo, P0 workflow",
            "keywords": "VendorFlow, onboarding, workflow, Streamlit, Supabase",
        }
    )
    doc.save(OUTPUT, deflate=True, garbage=3)
    doc.close()
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    build()
