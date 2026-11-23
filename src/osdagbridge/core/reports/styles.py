# =============================================================================
# OsdagBridge Report — Centralized Style Module
# =============================================================================
# All formatting constants (fonts, colors, margins, table styles, header/footer
# themes, padding, chart defaults) live here.  Every chapter file imports its
# formatting from this single source of truth.
# =============================================================================

# ── Colors ────────────────────────────────────────────────────────────────────
OSDAG_GREEN       = "91B014"            # brand accent (HTML hex)
TABLE_HEADER_BG   = "0.90, 0.90, 0.90"  # light gray RGB fractions
TABLE_ALT_ROW_BG  = "0.96, 0.96, 0.96"
CHART_BAR_COLOR   = "#2196F3"           # blue bar fill
CHART_BAR_DANGER  = "#F44336"           # red when UR > 1
CHART_UR_LINE_CLR = "red"               # reference-line colour

# ── Fonts & Sizes ─────────────────────────────────────────────────────────────
DOC_FONT_SIZE     = "12pt"
TABLE_FONT_CMD    = r"\small"
HEADING_SIZE_CMD  = r"\large\bfseries"

# ── Page Geometry ─────────────────────────────────────────────────────────────
# Adjusted bottom margin (1.15in) and explicit footskip (0.55in) prevent table
# content (such as row G4 on page 30) from bleeding into the footer area.
GEOMETRY = {
    "paper":        "a4paper",
    "top":          "1in",
    "bottom":       "1.15in",       # extra clearance for footer
    "left":         "1in",
    "right":        "1in",
    "headheight":   "14pt",
    "footskip":     "0.55in",       # footer offset from text body
}

# ── Table Spacing & Padding ───────────────────────────────────────────────────
TAB_COL_SEP       = "6pt"
ARRAY_STRETCH     = "1.18"          # improved readability & row separation
LT_PRE            = "0pt"
LT_POST           = "6pt"
ARRAY_RULE_WIDTH  = "0.5pt"
EXTRA_ROW_HEIGHT  = "1.5pt"          # row padding prevents cramped cell text
# Minimum baselineskips of space required before starting a new table/longtable
NEEDSPACE_LINES   = 6

# ── Header / Footer theme (fancyhdr) ─────────────────────────────────────────
FOOTER_LEFT_TEXT  = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
FOOTER_RIGHT_FMT  = r"Page \thepage\ of \pageref{LastPage}"
HEADER_RULE_HT    = "1pt"
FOOTER_RULE_HT    = "1pt"

# ── LongTable repeating-header helper ────────────────────────────────────────
def make_longtable_header(ncols: int, header_row_tex: str, caption_text: str = "") -> str:
    """Generate complete \\endfirsthead, \\endhead, \\endfoot, \\endlastfoot block.
    
    Parameters
    ----------
    ncols : int
        Number of columns.
    header_row_tex : str
        The header row text, e.g. r"\\textbf{Parameter} & \\textbf{Value} \\\\[6pt]"
    caption_text : str, optional
        Caption text for continuation header.
    """
    cont_text = f"({caption_text} --- Continued from previous page)" if caption_text else "(Continued from previous page)"
    return (
        r"\endfirsthead" + "\n"
        + r"\hline" + "\n"
        + r"\multicolumn{" + str(ncols) + r"}{c}{\small\textit{" + cont_text + r"}} \\[4pt]" + "\n"
        + r"\hline" + "\n"
        + header_row_tex + "\n"
        + r"\hline" + "\n"
        + r"\endhead" + "\n"
        + r"\hline" + "\n"
        + r"\multicolumn{" + str(ncols) + r"}{r}{\small\textit{Continued on next page\ldots}} \\" + "\n"
        + r"\endfoot" + "\n"
        + r"\hline" + "\n"
        + r"\endlastfoot" + "\n"
    )

def longtable_continuation_header(ncols: int) -> str:
    """Compact continuation block for longtables where caller repeats header directly."""
    return (
        r"\endfirsthead" + "\n"
        + r"\hline" + "\n"
        + r"\multicolumn{" + str(ncols) + r"}{r}{\small\textit{(continued from previous page)}} \\" + "\n"
        + r"\hline" + "\n"
        + r"\endhead" + "\n"
        + r"\hline" + "\n"
        + r"\multicolumn{" + str(ncols) + r"}{r}{\small\textit{Continued on next page\ldots}} \\" + "\n"
        + r"\endfoot" + "\n"
        + r"\hline" + "\n"
        + r"\endlastfoot" + "\n"
    )

# ── Chart Defaults (Matplotlib) ──────────────────────────────────────────────
CHART_FIGSIZE        = (10, 5)
CHART_FIGSIZE_SMALL  = (8, 5)
CHART_UR_LIMIT       = 1.0
CHART_DPI            = 150
CHART_FONT_FAMILY    = "DejaVu Sans"
CHART_GRID_STYLE     = ":"
CHART_GRID_ALPHA     = 0.5
CHART_ANNOT_FONTSIZE = 9
CHART_TITLE_FONTSIZE = 13
CHART_LABEL_FONTSIZE = 11

# ── Steel tonnage chart palette ───────────────────────────────────────────────
STEEL_PALETTE = ["#1565C0", "#42A5F5", "#90CAF9", "#64B5F6", "#1E88E5"]
CONCRETE_COLOR = "#43A047"
REBAR_COLOR    = "#E53935"

# ── Convenience: preamble geometry string ─────────────────────────────────────
def geometry_options_str() -> str:
    """Return the \\usepackage[...]{geometry} option string."""
    opts = ", ".join(f"{k}={v}" for k, v in GEOMETRY.items())
    return opts
