# Technical Changes Document — OsdagBridge LaTeX Report Generator Refactoring

**Repository:** [https://github.com/vdadheech/OsdagBridge](https://github.com/vdadheech/OsdagBridge)  
**Branch:** `dev`  
**Latest Commit:** `b461cea` — *Refactor LaTeX report generator module*

---

## 1. Executive Summary

The OsdagBridge LaTeX report generator module has been refactored to eliminate visual, structural, and layout defects. The refactoring addresses all six task requirements:
1. **Repeating Table Headers:** Multi-page tables now consistently repeat their headers across pages using `longtable` continuation structures (`\endfirsthead`, `\endhead`, `\endfoot`, and `\endlastfoot`).
2. **Footer Overlap Prevention:** Fixed table content (specifically row "G4" on page 30 and similar multi-row entries) bleeding into the footer rule by adjusting page geometry, footskip, row heights, array stretch, `\needspace` buffers, and non-breaking multirows (`\\*`).
3. **Chapter 3 Load Tables Split:** Vehicular live loads and pedestrian footpath loads are decoupled into separate dedicated tables with explicit unit columns, showing only the vehicles selected in the UI's Loading tab.
4. **Utilization Ratio Charts (Section 5.5):** Auto-generated Matplotlib bar charts displaying Demand/Capacity ratios for Girders, Concrete Deck Slab, Cross Bracing, and End Diaphragms, featuring a red dashed limit line at $\text{UR} = 1.0$.
5. **Material Quantity Charts (Chapter 7):** Graphical breakdown charts for Structural Steel Tonnage (girders, cross bracing, diaphragms, shear studs) and Concrete Volume ($\text{m}^3$) vs. Reinforcement Weight (MT).
6. **Centralized Style Module (`styles.py`):** Single source of truth for fonts, colors, margins, table dimensions, header/footer rules, chart themes, and padding rules.

---

## 2. Structure of the Centralized Style Module (`styles.py`)

The new module `src/osdagbridge/core/reports/styles.py` centralizes all typesetting constants:

```
src/osdagbridge/core/reports/
├── styles.py                     <-- NEW centralized style module
├── charts/
│   ├── __init__.py               <-- NEW charts sub-package
│   ├── ur_charts.py              <-- NEW Section 5.5 UR bar chart generators
│   └── quantity_charts.py        <-- NEW Chapter 7 quantity chart generators
├── report_generator.py           <-- Orchestration, geometry, chart triggers
├── report_utils.py               <-- Formatting utilities & safe dict extraction
├── executive_summary.py          <-- Table 1 & executive summary
├── chap1.py                      <-- Project metadata table
├── chap2.py                      <-- Input parameter tables (geometry, section, bracing)
├── chap3.py                      <-- Live loads & footpath tables split
├── chap4.py                      <-- Grillage analysis demand & deflection tables
├── chap5.py                      <-- Design checks & Section 5.5 UR charts
├── chap6.py                      <-- Visualizations & drawings
├── chap7.py                      <-- Bill of Materials & Section 7.2 quantity charts
├── chap8.py                      <-- Design standards (IRC & IS code tables)
└── chap9.py                      <-- Reference citations
```

### Key Constants Defined in `styles.py`:
- **Page Geometry (`GEOMETRY`):**
  - `top`: `1in`, `left`: `1in`, `right`: `1in`
  - `bottom`: `1.15in` (increased from `1in` to grant safe buffer for footers)
  - `footskip`: `0.55in` (explicit separation between text block and bottom rule)
  - `headheight`: `14pt`
- **Table Formatting (`TAB_COL_SEP`, `ARRAY_STRETCH`, `EXTRA_ROW_HEIGHT`):**
  - `\tabcolsep`: `6pt`
  - `\arraystretch`: `1.18` (prevents vertical cramped text in cells)
  - `\extrarowheight`: `1.5pt` (clean baseline padding between horizontal lines and cell text)
  - `\BeforeBeginEnvironment{longtable}{\needspace{6\baselineskip}}`
  - `\AtBeginEnvironment{longtable}{\raggedbottom}`
- **Header Helper (`make_longtable_header`):**
  - Programmatically constructs the four required `longtable` boundaries:
    1. `\endfirsthead` — first page header
    2. `\endhead` — repeating header with `(continued from previous page)` notice
    3. `\endfoot` — bottom notice: `Continued on next page...`
    4. `\endlastfoot` — final bottom rule
- **Chart Palette & Styling:**
  - `CHART_BAR_COLOR`: `#2196F3` (safe demand/capacity fill)
  - `CHART_BAR_DANGER`: `#F44336` (overstress indicator when $\text{UR} > 1.0$)
  - `CHART_UR_LINE_CLR`: `red` (dashed reference line at $\text{UR} = 1.0$)
  - `STEEL_PALETTE`: blues gradient for multi-component structural steel tonnage
  - `CONCRETE_COLOR`: `#43A047` (green for concrete volume)
  - `REBAR_COLOR`: `#E53935` (red for reinforcement weight)

---

## 3. Detailed Technical Changes by Requirement

### Requirement 1: Repeating Table Headers (`LongTable`)
- **Problem:** When tables spanned page breaks, subsequent pages lacked header rows, making column values unidentifiable.
- **Solution:** Replaced static tables and bare longtables across Chapters 1, 2, 3, 4, 5, 7, and 8 with standard four-part header definitions generated via `make_longtable_header()`.
- **Affected Files:**
  - `chap1.py`: Project and Design Team Details.
  - `chap2.py`: Typical Section Details, Components, Girder Information, Section Dimensions, Stiffener Details, Cross Bracing, End Diaphragms, Shear Connectors, Partial Safety Factors.
  - `chap3.py`: Dead Load, SIDL, Vehicular Live Loads, Footpath Loads, Wind Load, Seismic Load, Temperature Load, Load Combinations.
  - `chap4.py`: Demands, Reactions, Deflections.
  - `chap5.py`: Tables 5.1 through 5.16, 5.17(a–g), 5.20(a–c), and 5.22.
  - `chap7.py`: Table 7.1 Bill of Materials.
  - `chap8.py`: IRC Codes and IS Codes tables.

### Requirement 2: Footer Overlap Fix (Row "G4" on Page 30)
- **Problem:** Content from multi-row cells (such as row "G4" in Table 5.10 Serviceability Deflection Checks) overflowed past the bottom margin and collided with the green footer rule.
- **Root Causes:**
  1. Insufficient bottom margin (`1in`) and unconstrained `footskip`.
  2. Multirow rows were breakable across page boundaries by default (`\\`).
  3. No vertical lookahead buffer before starting a multi-line girder entry.
- **Solution:**
  1. In `report_generator.py` and `styles.py`: Set `geometry` to `bottom=1.15in, footskip=0.55in`.
  2. In `chap5.py`: Before each girder block in Table 5.10, inserted `\needspace{5\baselineskip}` so that if less than 5 lines remain, the entire girder entry moves to the next page.
  3. Used non-breaking newline `\\*[6pt]` between the first and second line of the multirow cell, forbidding page breaks inside a single girder's deflection checks.
  4. Added `\AtBeginEnvironment{longtable}{\raggedbottom}` to prevent vertical stretching of short table pages into footer areas.

### Requirement 3: Chapter 3 Load Tables Split
- **Problem:** Vehicle live loads and footpath live loads were merged into an unstructured 4-row key-value table lacking unit columns, and vehicle selection did not match the UI.
- **Solution:**
  1. Decoupled into two separate longtables:
     - **Table 3.3:** *Vehicular Live Loads (LL) — per IRC 6*
       - Columns: `Vehicle Class`, `Impact Factor`, `Braking Force (kN)`, `Centrifugal Force (kN)`, `Standard Reference`.
       - Dynamically filters rows to match *only* UI-selected vehicles (`KEY_LL_IRC_CLASS_A`, `KEY_LL_IRC_70R_WHEELED`, `KEY_LL_IRC_70R_TRACKED`, `KEY_LL_IRC_AA_WHEELED`, `KEY_LL_IRC_AA_TRACKED`, `KEY_LL_IRC_CLASS_SV`, `KEY_LL_IRC_70R_BOGIE`, `KEY_LL_IRC_CLASS_FATIGUE`, and custom vehicles).
       - Centrifugal force included per IRC:6 Cl. 212 (`0.00 (Straight)`).
     - **Table 3.4:** *Pedestrian Footpath Loads — per IRC 6*
       - Columns: `Location`, `Intensity (kN/m²)`, `Width (m)`, `Total Load (kN/m)`, `Standard Reference`.
       - Evaluates left and right footpath intensities per IRC:6 Cl. 206.1 or custom inputs.
  2. Both tables feature complete repeating header blocks.

### Requirement 4: Utilization Ratio Charts (Section 5.5)
- **Problem:** No graphical representation of demand/capacity ratios was present in Chapter 5.
- **Solution:**
  1. Created `src/osdagbridge/core/reports/charts/ur_charts.py`.
  2. Auto-generates four Matplotlib bar charts:
     - **Girders:** Maximum DCR per girder across governing load cases.
     - **Deck Slab:** URs for sagging flexure, hogging flexure, cantilever overhang, punching shear, and one-way shear.
     - **Cross Bracing:** Efficiencies for diagonals and chords under compression and tension.
     - **End Diaphragms:** Member efficiencies for end diaphragm components.
  3. Each chart features:
     - Color-coded bars: Blue (`#2196F3`) when $\text{UR} \leq 1.0$, Red (`#F44336`) when $\text{UR} > 1.0$.
     - Explicit numerical annotation above each bar.
     - Distinct **red dashed reference line at $\text{UR} = 1.0$** labeled *UR = 1.0 (Limit)*.
  4. Embedded via `\begin{figure}[H]` under new **Section 5.5: Utilization Ratio (UR) Evaluation and Charts**.

### Requirement 5: Material Quantity Charts (Chapter 7)
- **Problem:** Material quantities were purely tabular with no visual summary.
- **Solution:**
  1. Created `src/osdagbridge/core/reports/charts/quantity_charts.py`.
  2. Generated two figures:
     - **Chart A:** Structural Steel Tonnage breakdown by component (Girders, Cross Bracing, End Diaphragms, Shear Studs) with tonnage labels above each bar.
     - **Chart B:** Dual-axis comparison of Concrete Volume ($\text{m}^3$, green bars on primary axis) versus Reinforcement Weight ($\text{MT}$, red bars on secondary axis).
  3. Converted Table 7.1 to a 7-column `longtable` with repeating headers.
  4. Embedded charts under **Section 7.2: Material Quantity Breakdown Charts**.

### Requirement 6: Centralized Architecture and Decoupling
- **Decoupling Fix:** Added a standalone `_extract_osdag_summary()` in `report_utils.py` to decouple the report generator from `results_data.py` (which had a hard dependency on `openseespy`). This ensures the report generator compiles cleanly on any standard Python environment without crashing when OpenSees is not active.

---

## 4. File Modification Summary

| File | Type | Description |
|---|---|---|
| `src/osdagbridge/core/reports/styles.py` | **NEW** | Centralized formatting constants, geometry, headers, chart styles |
| `src/osdagbridge/core/reports/charts/__init__.py` | **NEW** | Charts sub-package initialization |
| `src/osdagbridge/core/reports/charts/ur_charts.py` | **NEW** | UR bar chart generators with red dashed reference line |
| `src/osdagbridge/core/reports/charts/quantity_charts.py` | **NEW** | Steel tonnage and concrete vs. rebar dual-axis charts |
| `src/osdagbridge/core/reports/chap1.py` | MODIFIED | Converted metadata table to LongTable with repeating header |
| `src/osdagbridge/core/reports/chap2.py` | MODIFIED | Converted 8+ multi-page tables to LongTable with `make_longtable_header` |
| `src/osdagbridge/core/reports/chap3.py` | MODIFIED | Split live loads into Table 3.3 (Vehicles) and Table 3.4 (Footpaths); unit columns |
| `src/osdagbridge/core/reports/chap4.py` | MODIFIED | Repeating headers on analysis demand and reaction tables |
| `src/osdagbridge/core/reports/chap5.py` | MODIFIED | Fixed row G4 footer overlap; added Section 5.5 UR charts; LongTable headers |
| `src/osdagbridge/core/reports/chap6.py` | MODIFIED | Styles import integration |
| `src/osdagbridge/core/reports/chap7.py` | MODIFIED | Repeating headers on BOM Table 7.1; added Section 7.2 quantity charts |
| `src/osdagbridge/core/reports/chap8.py` | MODIFIED | Converted IRC and IS code tables to LongTable with repeating headers |
| `src/osdagbridge/core/reports/chap9.py` | MODIFIED | Styles import integration |
| `src/osdagbridge/core/reports/executive_summary.py` | MODIFIED | Styles import integration; safe dict extraction |
| `src/osdagbridge/core/reports/report_generator.py` | MODIFIED | Preamble geometry adjustments; auto-trigger chart generation; wire figure paths |
| `src/osdagbridge/core/reports/report_utils.py` | MODIFIED | Added decoupled `_extract_osdag_summary()` helper |
