"""Generate synthetic, Harry Potter-inspired ESG disclosure PDFs.

Run:
    python3 Datasets/KPIs/generate.py
Outputs 4 PDFs into Datasets/KPIs/.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

HERE = Path(__file__).resolve().parent


@dataclass
class Disclosure:
    filename: str
    company: str
    tagline: str
    country: str
    eu_member_state: str
    region: str
    sector: str
    industry: str
    entity_type: str
    listing_status: str
    size_band: str
    fiscal_year: int
    currency: str
    revenue_usd: float
    total_assets_usd: float
    employees: int
    csrd_applicable: bool
    # metrics
    scope1: float
    scope2: float
    scope3: float
    energy_mwh: float
    renewable_pct: float
    water_m3: float
    waste_t: float
    recycled_pct: float
    female_ratio: float
    board_indep_pct: float
    incidents: int
    esg_score: float
    notes: List[str]


DISCLOSURES: List[Disclosure] = [
    Disclosure(
        filename="dumbledore_industries_fy2024.pdf",
        company="Dumbledore Industries plc",
        tagline="Sustainability & CSRD Disclosure Report — Fiscal Year 2024",
        country="United Kingdom",
        eu_member_state="",
        region="Northern Europe",
        sector="Energy/Utilities",
        industry="Renewable Energy",
        entity_type="Public",
        listing_status="Listed",
        size_band="Large",
        fiscal_year=2024,
        currency="GBP",
        revenue_usd=2_850_000_000,
        total_assets_usd=5_120_000_000,
        employees=7_420,
        csrd_applicable=True,
        scope1=18_240,
        scope2=7_115,
        scope3=142_300,
        energy_mwh=312_400,
        renewable_pct=86.4,
        water_m3=221_700,
        waste_t=4_820,
        recycled_pct=88.2,
        female_ratio=0.44,
        board_indep_pct=72.0,
        incidents=1,
        esg_score=78.9,
        notes=[
            "Aligned to ESRS E1 with a 2030 absolute reduction target of -55% vs 2019 baseline.",
            "Scope 3 breakdown reported across 11 of the 15 GHG Protocol categories.",
            "Limited assurance provided by Phoenix Audit LLP for FY2024 disclosures.",
        ],
    ),
    Disclosure(
        filename="longbottom_botanicals_fy2024.pdf",
        company="Longbottom Botanicals Ltd.",
        tagline="Annual ESG Statement — Reporting Period FY2024",
        country="Ireland",
        eu_member_state="Ireland",
        region="Western Europe",
        sector="Consumer Goods/Retail",
        industry="Packaged Food",
        entity_type="Private",
        listing_status="Unlisted",
        size_band="Medium",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=312_500_000,
        total_assets_usd=489_000_000,
        employees=1_185,
        csrd_applicable=True,
        scope1=9_560,
        scope2=4_215,
        scope3=74_820,
        energy_mwh=46_700,
        renewable_pct=41.8,
        water_m3=112_500,
        waste_t=6_210,
        recycled_pct=63.5,
        female_ratio=0.52,
        board_indep_pct=50.0,
        incidents=2,
        esg_score=64.1,
        notes=[
            "Transitioning suppliers to Rainforest Alliance / organic certifications by 2027.",
            "Implementing regenerative-agriculture supplier program across Herbologist network.",
        ],
    ),
    Disclosure(
        filename="flamel_biotech_fy2024.pdf",
        company="Flamel Biotech SA",
        tagline="Non-Financial Disclosure — Fiscal Year 2024",
        country="France",
        eu_member_state="France",
        region="Western Europe",
        sector="Healthcare/Pharma",
        industry="Biotech",
        entity_type="Public",
        listing_status="Listed",
        size_band="Large",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=1_640_000_000,
        total_assets_usd=2_980_000_000,
        employees=4_380,
        csrd_applicable=True,
        scope1=12_840,
        scope2=15_220,
        scope3=382_600,
        energy_mwh=154_900,
        renewable_pct=58.0,
        water_m3=612_400,
        waste_t=9_760,
        recycled_pct=58.2,
        female_ratio=0.41,
        board_indep_pct=58.0,
        incidents=6,
        esg_score=61.7,
        notes=[
            "Scope 3 dominates footprint (>10x Scope 1+2); supplier engagement program expanded to Tier 2.",
            "Four pharmacovigilance incidents and two minor data-protection events disclosed during FY2024.",
            "Elixir-of-Life research unit excluded from quantitative disclosure per qualitative materiality assessment.",
        ],
    ),
    Disclosure(
        filename="ollivander_craftwork_fy2024.pdf",
        company="Ollivander Craftwork Ltd.",
        tagline="Sustainability Note FY2024",
        country="United Kingdom",
        eu_member_state="",
        region="Northern Europe",
        sector="Consumer Goods/Retail",
        industry="Luxury Goods",
        entity_type="Private",
        listing_status="Unlisted",
        size_band="Small",
        fiscal_year=2024,
        currency="GBP",
        revenue_usd=42_800_000,
        total_assets_usd=61_200_000,
        employees=214,
        csrd_applicable=False,
        scope1=1_420,
        scope2=890,
        scope3=4_620,
        energy_mwh=6_240,
        renewable_pct=18.4,
        water_m3=3_120,
        waste_t=182,
        recycled_pct=39.0,
        female_ratio=0.29,
        board_indep_pct=25.0,
        incidents=0,
        esg_score=48.5,
        notes=[
            "Family-owned heritage maker; governance is owner-operated with a two-member advisory board.",
            "Renewable share constrained by tenanted workshop in a listed historic building in Diagon Alley.",
        ],
    ),
    Disclosure(
        filename="nimbus_transit_fy2024.pdf",
        company="Nimbus Transit plc",
        tagline="Integrated Annual & Sustainability Report — FY2024",
        country="Ireland",
        eu_member_state="Ireland",
        region="Western Europe",
        sector="Automotive/Transport",
        industry="Passenger Airline",
        entity_type="Public",
        listing_status="Listed",
        size_band="Large",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=4_220_000_000,
        total_assets_usd=6_540_000_000,
        employees=12_480,
        csrd_applicable=True,
        scope1=862_400,
        scope2=11_920,
        scope3=147_800,
        energy_mwh=2_884_500,
        renewable_pct=4.2,
        water_m3=182_300,
        waste_t=21_800,
        recycled_pct=37.8,
        female_ratio=0.41,
        board_indep_pct=63.6,
        incidents=3,
        esg_score=42.8,
        notes=[
            "Jet fuel consumption drives more than 95% of the Scope 1 footprint.",
            "SAF (sustainable aviation fuel) offtake agreement signed with Fleur Delacour Aviation Fuels AG for 2027 onwards.",
            "ESRS E1 transition plan anchored to IATA fleet renewal trajectory.",
        ],
    ),
    Disclosure(
        filename="hogsmeade_civil_works_fy2024.pdf",
        company="Hogsmeade Civil Works Ltd.",
        tagline="Annual Disclosure FY2024 — Built environment",
        country="United Kingdom",
        eu_member_state="",
        region="Northern Europe",
        sector="Construction/Industrials",
        industry="Civil Engineering",
        entity_type="Private",
        listing_status="Unlisted",
        size_band="Large",
        fiscal_year=2024,
        currency="GBP",
        revenue_usd=684_500_000,
        total_assets_usd=912_300_000,
        employees=4_220,
        csrd_applicable=False,
        scope1=42_300,
        scope2=17_840,
        scope3=518_600,
        energy_mwh=128_400,
        renewable_pct=22.1,
        water_m3=382_500,
        waste_t=64_800,
        recycled_pct=51.2,
        female_ratio=0.18,
        board_indep_pct=44.0,
        incidents=11,
        esg_score=51.3,
        notes=[
            "Scope 3 is dominated by embodied carbon in concrete, rebar, and steel inputs.",
            "Safety incidents reported under LTIFR and RIDDOR frameworks; H&S review underway.",
            "Company is UK-domiciled and not currently in CSRD scope; monitoring non-EU threshold tests.",
        ],
    ),
    Disclosure(
        filename="gringotts_financial_fy2024.pdf",
        company="Gringotts Financial Group AG",
        tagline="Non-Financial Information Statement — FY2024",
        country="Germany",
        eu_member_state="Germany",
        region="Western Europe",
        sector="Financial Services",
        industry="Retail Banking",
        entity_type="Public",
        listing_status="Listed",
        size_band="Large",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=8_240_000_000,
        total_assets_usd=185_600_000_000,
        employees=28_540,
        csrd_applicable=True,
        scope1=1_840,
        scope2=9_150,
        scope3=3_418_200,
        energy_mwh=311_800,
        renewable_pct=78.4,
        water_m3=64_200,
        waste_t=2_380,
        recycled_pct=83.6,
        female_ratio=0.48,
        board_indep_pct=68.4,
        incidents=4,
        esg_score=66.8,
        notes=[
            "Scope 3 is dominated by Category 15 financed emissions (commercial + retail loan book).",
            "PCAF-aligned methodology used for financed emissions; coverage at 71% of on-balance-sheet exposures.",
            "Aligned with Partnership for Biodiversity Accounting Financials (PBAF) pilot disclosures.",
        ],
    ),
    Disclosure(
        filename="weasley_forge_fy2024.pdf",
        company="Weasley Forge & Alloys SRL",
        tagline="Sustainability Report — FY2024",
        country="Romania",
        eu_member_state="Romania",
        region="Central Europe",
        sector="Manufacturing",
        industry="Steel",
        entity_type="Private",
        listing_status="Unlisted",
        size_band="Large",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=542_800_000,
        total_assets_usd=784_500_000,
        employees=3_820,
        csrd_applicable=True,
        scope1=1_248_000,
        scope2=182_400,
        scope3=614_500,
        energy_mwh=3_182_400,
        renewable_pct=17.6,
        water_m3=892_400,
        waste_t=141_800,
        recycled_pct=65.4,
        female_ratio=0.14,
        board_indep_pct=40.0,
        incidents=14,
        esg_score=38.7,
        notes=[
            "Integrated blast-furnace route; EAF conversion feasibility study completed in Q3.",
            "Industrial safety incidents reported under ILO framework; independent review commissioned.",
            "Covered by the EU Emissions Trading System (EU ETS); carbon cost provisioned in opex.",
        ],
    ),
    Disclosure(
        filename="pensieve_systems_fy2024.pdf",
        company="Pensieve Systems AS",
        tagline="ESG & CSRD Disclosure Statement FY2024",
        country="Estonia",
        eu_member_state="Estonia",
        region="Northern Europe",
        sector="Technology",
        industry="Enterprise Software",
        entity_type="Public",
        listing_status="Listed",
        size_band="Medium",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=285_400_000,
        total_assets_usd=312_800_000,
        employees=1_640,
        csrd_applicable=True,
        scope1=184,
        scope2=4_210,
        scope3=23_900,
        energy_mwh=38_200,
        renewable_pct=91.8,
        water_m3=8_420,
        waste_t=178,
        recycled_pct=77.5,
        female_ratio=0.42,
        board_indep_pct=71.4,
        incidents=1,
        esg_score=74.2,
        notes=[
            "Compute footprint covered under Category 1 (purchased goods/services) via hyperscaler PPA pass-through.",
            "100% renewable-backed data centers across Helsinki, Tallinn, and Frankfurt regions.",
            "SBTi near-term target validated at 1.5°C pathway.",
        ],
    ),
    Disclosure(
        filename="patronus_networks_fy2024.pdf",
        company="Patronus Networks SA",
        tagline="Annual Non-Financial Statement FY2024",
        country="Spain",
        eu_member_state="Spain",
        region="Southern Europe",
        sector="Telecommunications",
        industry="Mobile Operator",
        entity_type="Public",
        listing_status="Listed",
        size_band="Large",
        fiscal_year=2024,
        currency="EUR",
        revenue_usd=3_820_000_000,
        total_assets_usd=6_184_000_000,
        employees=11_240,
        csrd_applicable=True,
        scope1=24_180,
        scope2=184_600,
        scope3=418_200,
        energy_mwh=1_648_300,
        renewable_pct=68.0,
        water_m3=142_800,
        waste_t=8_420,
        recycled_pct=58.9,
        female_ratio=0.38,
        board_indep_pct=54.5,
        incidents=2,
        esg_score=62.4,
        notes=[
            "Radio-access network energy intensity improved by 11% year-on-year.",
            "5G edge buildout traded off with aggressive PPA procurement to preserve RE100 commitment.",
            "End-of-life handset take-back reached 42% of units sold, tracked under ESRS E5.",
        ],
    ),
]


def _styles():
    ss = getSampleStyleSheet()
    ss.add(
        ParagraphStyle(
            name="Title1",
            parent=ss["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            spaceAfter=4,
        )
    )
    ss.add(
        ParagraphStyle(
            name="Sub",
            parent=ss["Normal"],
            fontName="Helvetica",
            fontSize=11,
            textColor=colors.HexColor("#5a6473"),
            spaceAfter=14,
        )
    )
    ss.add(
        ParagraphStyle(
            name="H2",
            parent=ss["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            spaceBefore=14,
            spaceAfter=6,
            textColor=colors.HexColor("#0f172a"),
        )
    )
    ss.add(
        ParagraphStyle(
            name="Body",
            parent=ss["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
        )
    )
    ss.add(
        ParagraphStyle(
            name="Mono",
            parent=ss["Code"],
            fontName="Courier",
            fontSize=9,
            leading=12,
        )
    )
    return ss


def _kv_table(rows, colw=(62 * mm, 100 * mm)):
    t = Table(rows, colWidths=colw, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#5a6473")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#0f172a")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e8ef")),
            ]
        )
    )
    return t


def _metrics_table(rows):
    header = [["Metric", "Value", "Unit", "Framework"]]
    data = header + rows
    t = Table(
        data,
        colWidths=(70 * mm, 36 * mm, 24 * mm, 40 * mm),
        hAlign="LEFT",
    )
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f6")),
                ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#1f2937")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e8ef")),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("ALIGN", (2, 1), (2, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _fmt(v):
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v) if v else "—"


def build_pdf(d: Disclosure) -> Path:
    out = HERE / d.filename
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"{d.company} — ESG FY{d.fiscal_year}",
        author="esg.intel synthetic",
    )
    ss = _styles()
    story = []

    story.append(Paragraph(d.company, ss["Title1"]))
    story.append(Paragraph(d.tagline, ss["Sub"]))

    story.append(Paragraph("1. Reporting entity", ss["H2"]))
    story.append(
        _kv_table(
            [
                ["Legal name", d.company],
                ["Entity type", d.entity_type],
                ["Listing status", d.listing_status],
                ["Country of incorporation", d.country],
                ["EU member state", d.eu_member_state or "—"],
                ["Region", d.region],
                ["Sector", d.sector],
                ["Industry", d.industry],
                ["Company size band", d.size_band],
                ["Fiscal year", str(d.fiscal_year)],
                ["Reporting currency", d.currency],
            ]
        )
    )
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Financial and workforce scale", ss["H2"]))
    story.append(
        _kv_table(
            [
                ["Net revenue (USD)", _fmt(d.revenue_usd)],
                ["Total assets (USD)", _fmt(d.total_assets_usd)],
                ["Headcount (employees)", _fmt(d.employees)],
                ["CSRD applicability", _fmt(d.csrd_applicable)],
            ]
        )
    )

    story.append(Paragraph("3. Environmental disclosures (ESRS E1–E5)", ss["H2"]))
    story.append(
        _metrics_table(
            [
                ["Scope 1 emissions", _fmt(d.scope1), "tCO2e", "ESRS E1 / GHG"],
                ["Scope 2 emissions (market-based)", _fmt(d.scope2), "tCO2e", "ESRS E1 / GHG"],
                ["Scope 3 emissions", _fmt(d.scope3), "tCO2e", "ESRS E1 / GHG"],
                ["Energy consumption", _fmt(d.energy_mwh), "MWh", "ESRS E1"],
                ["Renewable energy share", _fmt(d.renewable_pct), "%", "ESRS E1"],
                ["Water withdrawal", _fmt(d.water_m3), "m3", "ESRS E3"],
                ["Waste generated", _fmt(d.waste_t), "tonnes", "ESRS E5"],
                ["Waste recycled share", _fmt(d.recycled_pct), "%", "ESRS E5"],
            ]
        )
    )
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Social & governance disclosures (ESRS S1, G1)", ss["H2"]))
    story.append(
        _metrics_table(
            [
                ["Employee count (period average)", _fmt(d.employees), "FTE", "ESRS S1"],
                ["Female employee ratio", _fmt(d.female_ratio), "0-1", "ESRS S1"],
                ["Board independence", _fmt(d.board_indep_pct), "%", "ESRS G1"],
                ["Reportable incidents", _fmt(d.incidents), "count", "ESRS G1"],
                ["Internal ESG score", _fmt(d.esg_score), "0-100", "internal"],
            ]
        )
    )

    story.append(PageBreak())

    story.append(Paragraph("5. Methodology and notes", ss["H2"]))
    for n in d.notes:
        story.append(Paragraph("• " + n, ss["Body"]))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            (
                "This disclosure is a synthetic demonstration document produced for "
                "esg.intel platform testing. Figures are illustrative and not audited. "
                "Reporting boundary: operational control. Consolidation: financial control. "
                "Reporting period: 1 January to 31 December {year}."
            ).format(year=d.fiscal_year),
            ss["Body"],
        )
    )

    story.append(Paragraph("6. Governance statement", ss["H2"]))
    story.append(
        Paragraph(
            (
                f"{d.company} operates under a {d.entity_type.lower()} governance "
                f"structure. Board independence stands at {d.board_indep_pct:.0f}%. "
                "The audit committee oversees sustainability reporting with quarterly "
                "review cycles. Whistleblower policies are in force and aligned with "
                "ESRS G1 requirements."
            ),
            ss["Body"],
        )
    )

    story.append(Paragraph("7. CSRD applicability self-assessment", ss["H2"]))
    story.append(
        Paragraph(
            (
                f"Based on FY{d.fiscal_year} thresholds (employees > 250, net turnover "
                f"> EUR 50M, total assets > EUR 25M), CSRD applicability is declared as "
                f"{'YES' if d.csrd_applicable else 'NO'}. "
                + (
                    "The company is in scope from the first reporting year applicable "
                    "to its size band."
                    if d.csrd_applicable
                    else "The company is below the large-undertaking thresholds and is "
                    "not currently in CSRD scope, but monitors threshold proximity."
                )
            ),
            ss["Body"],
        )
    )

    doc.build(story)
    return out


def main() -> None:
    os.makedirs(HERE, exist_ok=True)
    for d in DISCLOSURES:
        p = build_pdf(d)
        print(f"wrote {p.relative_to(HERE.parent.parent)} ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
