# =============================================================================
# Utilization Ratio (UR) Bar Charts — Section 5.5
# =============================================================================
# Auto-generates bar charts of Demand / Capacity for:
#   • Girders
#   • Deck Slab
#   • Cross Bracing
#   • End Diaphragms
# Each chart shows a red dashed reference line at UR = 1.0.
# =============================================================================

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import tempfile

from osdagbridge.core.reports.styles import (
    CHART_BAR_COLOR,
    CHART_BAR_DANGER,
    CHART_DPI,
    CHART_FIGSIZE,
    CHART_FONT_FAMILY,
    CHART_GRID_ALPHA,
    CHART_GRID_STYLE,
    CHART_UR_LIMIT,
    CHART_UR_LINE_CLR,
    CHART_ANNOT_FONTSIZE,
    CHART_TITLE_FONTSIZE,
    CHART_LABEL_FONTSIZE,
)


def _bar_color(ur_value: float) -> str:
    """Return red if UR > 1.0, else blue."""
    return CHART_BAR_DANGER if ur_value > CHART_UR_LIMIT else CHART_BAR_COLOR


def generate_ur_chart(component_name, labels, ur_values, tmp_dir=None):
    """Generate a single UR bar chart and save as PNG.

    Parameters
    ----------
    component_name : str
        Human-readable name, e.g. "Girders".
    labels : list[str]
        X-axis labels (member IDs).
    ur_values : list[float]
        Utilization ratios (Demand / Capacity).
    tmp_dir : str | None
        Directory for the output PNG.  Auto-created if None.

    Returns
    -------
    str
        Absolute path to the saved PNG.
    """
    plt.rcParams["font.family"] = CHART_FONT_FAMILY
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

    colors = [_bar_color(u) for u in ur_values]
    bars = ax.bar(labels, ur_values, color=colors, edgecolor="black", linewidth=0.6)

    # Red dashed UR = 1.0 reference line
    ax.axhline(
        y=CHART_UR_LIMIT,
        color=CHART_UR_LINE_CLR,
        linestyle="--",
        linewidth=1.5,
        label=f"UR = {CHART_UR_LIMIT:.1f} (Limit)",
    )

    # Value annotations on bars
    for bar, val in zip(bars, ur_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=CHART_ANNOT_FONTSIZE,
        )

    ax.set_title(
        f"Utilization Ratio — {component_name}",
        fontsize=CHART_TITLE_FONTSIZE,
        fontweight="bold",
    )
    ax.set_xlabel("Member / Location", fontsize=CHART_LABEL_FONTSIZE)
    ax.set_ylabel("UR (Demand / Capacity)", fontsize=CHART_LABEL_FONTSIZE)
    ax.set_ylim(0, max(max(ur_values) * 1.15, 1.2))
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle=CHART_GRID_STYLE, alpha=CHART_GRID_ALPHA)

    plt.tight_layout()

    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, f"ur_{component_name.replace(' ', '_').lower()}.png")
    fig.savefig(path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def collect_ur_data(bridge) -> dict:
    """Extract UR data from the ReportDataBridge for all four component groups.

    Returns
    -------
    dict
        ``{component_name: {"labels": [...], "values": [...]}}``
        Only components with data are included.
    """
    from osdagbridge.core.reports.report_utils import get_girder_entries
    from osdagbridge.core.utils.common import (
        KEY_TS_NO_OF_GIRDERS,
        KEY_UTIL_FLEXURE,
        KEY_UTIL_SHEAR,
        KEY_UTIL_LTB,
        KEY_UTIL_INTERACTION,
    )

    result = {}

    # ── 1. Girders ────────────────────────────────────────────────────────────
    girder_entries = get_girder_entries(bridge.input_dict)
    if not girder_entries:
        try:
            n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        except (TypeError, ValueError):
            n = 1
        girder_entries = [(f"G{i}", f"M1") for i in range(1, n + 1)]

    per_girder = (
        (bridge.output_dict.get("design_results", {}) or {})
        .get("per_girder", {})
        or {}
    )
    g_labels, g_urs = [], []
    for gi, (lbl, _) in enumerate(girder_entries, start=1):
        gd = per_girder.get(f"G{gi}", {}) or {}
        checks = gd.get("checks") or []
        if checks:
            worst = max(checks, key=lambda c: c.get("dcr") or 0.0)
            g_labels.append(lbl or f"G{gi}")
            g_urs.append(float(worst.get("dcr", 0.0)))
    if g_labels:
        result["Girders"] = {"labels": g_labels, "values": g_urs}

    # ── 2. Deck Slab ──────────────────────────────────────────────────────────
    deck_rpt = bridge.output_dict.get("deck_report_values", {}) or {}
    dd_results = bridge.output_dict.get("deck_design_results", {}) or {}
    d_labels, d_urs = [], []
    ur_keys = [
        (k, v)
        for k, v in dd_results.items()
        if str(k).startswith("ur_") and v is not None
    ]
    for k, v in ur_keys:
        try:
            d_labels.append(k.replace("ur_", "").replace("_", " ").title())
            d_urs.append(float(v))
        except (TypeError, ValueError):
            pass
    if d_labels:
        result["Deck Slab"] = {"labels": d_labels, "values": d_urs}

    # ── 3. Cross Bracing ──────────────────────────────────────────────────────
    cb_labels, cb_urs = [], []
    pairs = bridge.get_cb_pairs()
    for pair in pairs:
        for member in ("diagonal", "chord"):
            _, ftype = bridge.get_cb_governing_force(pair, member)
            eff = bridge.get_cb_efficiency(pair, member, ftype)
            try:
                cb_labels.append(f"{pair} {member.title()}")
                cb_urs.append(float(eff))
            except (TypeError, ValueError):
                pass
    if cb_labels:
        result["Cross Bracing"] = {"labels": cb_labels, "values": cb_urs}

    # ── 4. End Diaphragms ─────────────────────────────────────────────────────
    # End diaphragms use the same helpers when configured as bracing
    ed_results = bridge.output_dict.get("end_diaphragm_design_results", {}) or {}
    if ed_results:
        from osdagbridge.core.bridge_types.plate_girder.results_data import (
            _extract_osdag_summary,
        )

        ed_labels, ed_urs = [], []
        for pair_key, members in ed_results.items():
            if not isinstance(members, dict):
                continue
            for member_key, force_types in members.items():
                if not isinstance(force_types, dict):
                    continue
                for ft_key, raw in force_types.items():
                    try:
                        summary = _extract_osdag_summary(raw or {})
                        eff = summary.get("efficiency")
                        if eff is not None:
                            ed_labels.append(f"{pair_key} {member_key}")
                            ed_urs.append(float(eff))
                    except Exception:
                        pass
        if ed_labels:
            result["End Diaphragms"] = {"labels": ed_labels, "values": ed_urs}

    return result


def generate_all_ur_charts(bridge, tmp_dir=None):
    """Generate UR bar charts for all available component groups.

    Returns
    -------
    dict
        ``{component_name: png_path}``
    """
    data = collect_ur_data(bridge)
    paths = {}
    for name, info in data.items():
        if info["labels"]:
            paths[name] = generate_ur_chart(
                name, info["labels"], info["values"], tmp_dir
            )
    return paths
