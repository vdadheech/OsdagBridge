# =============================================================================
# Material Quantity Charts — Chapter 7
# =============================================================================
# Two charts:
#   A) Structural Steel Tonnage by component (Girders, Bracing, Diaphragms)
#   B) Concrete Volume (m³) vs Reinforcement Weight (MT) — dual-axis bar chart
# =============================================================================

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os
import tempfile

from osdagbridge.core.reports.styles import (
    CHART_DPI,
    CHART_FIGSIZE,
    CHART_FIGSIZE_SMALL,
    CHART_FONT_FAMILY,
    CHART_GRID_ALPHA,
    CHART_GRID_STYLE,
    CHART_ANNOT_FONTSIZE,
    CHART_TITLE_FONTSIZE,
    CHART_LABEL_FONTSIZE,
    STEEL_PALETTE,
    CONCRETE_COLOR,
    REBAR_COLOR,
)


def generate_steel_tonnage_chart(steel_data: dict, tmp_dir=None) -> str:
    """Generate a bar chart of structural steel tonnage by component.

    Parameters
    ----------
    steel_data : dict
        ``{"Girders": tonnage, "Cross Bracing": tonnage, ...}``
    tmp_dir : str | None
        Output directory (auto-created if None).

    Returns
    -------
    str
        Absolute path to the saved PNG.
    """
    plt.rcParams["font.family"] = CHART_FONT_FAMILY
    labels = list(steel_data.keys())
    values = list(steel_data.values())

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE_SMALL)
    colors = STEEL_PALETTE[: len(labels)]
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=0.6)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.01,
            f"{val:.2f} MT",
            ha="center",
            va="bottom",
            fontsize=CHART_ANNOT_FONTSIZE + 1,
        )

    ax.set_title(
        "Structural Steel Tonnage by Component",
        fontsize=CHART_TITLE_FONTSIZE,
        fontweight="bold",
    )
    ax.set_ylabel("Weight (Metric Tonnes)", fontsize=CHART_LABEL_FONTSIZE)
    ax.set_xlabel("Component", fontsize=CHART_LABEL_FONTSIZE)
    ax.grid(axis="y", linestyle=CHART_GRID_STYLE, alpha=CHART_GRID_ALPHA)
    plt.tight_layout()

    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "steel_tonnage.png")
    fig.savefig(path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_concrete_rebar_chart(
    concrete_m3: list,
    rebar_mt: list,
    component_labels: list,
    tmp_dir=None,
) -> str:
    """Generate a dual-axis bar chart: Concrete Volume vs Rebar Weight.

    Parameters
    ----------
    concrete_m3 : list[float]
        Concrete volumes per component.
    rebar_mt : list[float]
        Reinforcement weights per component.
    component_labels : list[str]
        Component names for x-axis.
    tmp_dir : str | None
        Output directory.

    Returns
    -------
    str
        Absolute path to the saved PNG.
    """
    plt.rcParams["font.family"] = CHART_FONT_FAMILY
    x = np.arange(len(component_labels))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=CHART_FIGSIZE)
    ax2 = ax1.twinx()

    b1 = ax1.bar(
        x - width / 2,
        concrete_m3,
        width,
        label="Concrete (m³)",
        color=CONCRETE_COLOR,
        edgecolor="black",
        linewidth=0.6,
    )
    b2 = ax2.bar(
        x + width / 2,
        rebar_mt,
        width,
        label="Reinforcement (MT)",
        color=REBAR_COLOR,
        edgecolor="black",
        linewidth=0.6,
    )

    ax1.set_xlabel("Component", fontsize=CHART_LABEL_FONTSIZE)
    ax1.set_ylabel("Concrete Volume (m³)", fontsize=CHART_LABEL_FONTSIZE, color=CONCRETE_COLOR)
    ax2.set_ylabel("Rebar Weight (MT)", fontsize=CHART_LABEL_FONTSIZE, color=REBAR_COLOR)
    ax1.set_xticks(x)
    ax1.set_xticklabels(component_labels, rotation=15, ha="right")
    ax1.set_title(
        "Concrete Volume vs Reinforcement Weight",
        fontsize=CHART_TITLE_FONTSIZE,
        fontweight="bold",
    )

    lines = [b1, b2]
    labels_leg = [l.get_label() for l in lines]
    ax1.legend(lines, labels_leg, loc="upper left", fontsize=10)
    ax1.grid(axis="y", linestyle=CHART_GRID_STYLE, alpha=CHART_GRID_ALPHA - 0.1)
    plt.tight_layout()

    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "concrete_rebar.png")
    fig.savefig(path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def collect_quantity_data(input_dict: dict) -> dict:
    """Extract material quantity data from the input_dict (after BOM injection).

    Returns
    -------
    dict with keys:
        "steel"     : dict {component: tonnage}
        "concrete"  : list of volumes (m³)
        "rebar"     : list of weights (MT)
        "components": list of component label strings
    """
    def _float(v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    steel = {}
    # Girders
    g_wt = _float(input_dict.get("steel_girders_wt_total"))
    if g_wt > 0:
        steel["Girders"] = g_wt

    # Cross Bracing — sum of top + bottom + diagonal chords
    cb_total = (
        _float(input_dict.get("bracing_top_wt_total"))
        + _float(input_dict.get("bracing_bot_wt_total"))
        + _float(input_dict.get("bracing_diag_wt_total"))
    )
    if cb_total > 0:
        steel["Cross Bracing"] = cb_total

    # End Diaphragms (may not have a separate key — check)
    ed_wt = _float(input_dict.get("diaphragm_wt_total"))
    if ed_wt > 0:
        steel["End Diaphragms"] = ed_wt

    # Shear Studs
    stud_wt = _float(input_dict.get("shear_studs_wt_total"))
    if stud_wt > 0:
        steel["Shear Studs"] = stud_wt

    # Concrete and Rebar
    concrete_vols = []
    rebar_wts = []
    comp_labels = []

    deck_vol = _float(input_dict.get("concrete_deck_vol_total"))
    deck_rebar = _float(input_dict.get("rebar_deck_wt_total"))
    if deck_vol > 0 or deck_rebar > 0:
        comp_labels.append("Deck Slab")
        concrete_vols.append(deck_vol)
        rebar_wts.append(deck_rebar)

    cb_vol = _float(input_dict.get("crash_barrier_vol_total"))
    cb_rebar = _float(input_dict.get("crash_barrier_wt_total"))
    if cb_vol > 0 or cb_rebar > 0:
        comp_labels.append("Crash Barrier")
        concrete_vols.append(cb_vol)
        rebar_wts.append(cb_rebar)

    return {
        "steel": steel,
        "concrete": concrete_vols,
        "rebar": rebar_wts,
        "components": comp_labels,
    }


def generate_all_quantity_charts(input_dict: dict, tmp_dir=None) -> dict:
    """Generate both material quantity charts.

    Returns
    -------
    dict
        ``{"steel_tonnage": path, "concrete_rebar": path}``
        Keys are omitted when data is insufficient.
    """
    data = collect_quantity_data(input_dict)
    paths = {}

    if data["steel"]:
        paths["steel_tonnage"] = generate_steel_tonnage_chart(data["steel"], tmp_dir)

    if data["components"] and any(v > 0 for v in data["concrete"] + data["rebar"]):
        paths["concrete_rebar"] = generate_concrete_rebar_chart(
            data["concrete"], data["rebar"], data["components"], tmp_dir
        )

    return paths
