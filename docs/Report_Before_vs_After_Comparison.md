# OsdagBridge LaTeX Report Generator — Before vs. After Refactoring Report

**Project:** OsdagBridge (Osdag Bridge Design Plugin)  
**Target Repository:** [https://github.com/vdadheech/OsdagBridge](https://github.com/vdadheech/OsdagBridge) (`dev` branch)  
**Commits:** [`b461cea`](https://github.com/vdadheech/OsdagBridge/commit/b461cead9aab96b421af008482288d88fc25fa84), [`6c6afee`](https://github.com/vdadheech/OsdagBridge/commit/6c6afee3a4d228bc6793bed91be9e67ee22ec272)  
**Date:** 2026-11-23

---

## 1. Executive Summary & Comparison Matrix

The table below summarizes the six core design and layout defects present in the legacy report generator alongside the architectural solutions implemented in the refactored code.

| Feature / Defect | Before Refactoring (Legacy) | After Refactoring (Refactored) | Impact & Benefit |
|---|---|---|---|
| **1. Multi-Page Table Headers** | Multi-page tables used bare `tabular` or unconfigured `longtable`. Headers vanished on subsequent pages. | Every multi-page table implements full 4-stage `longtable` continuation (`\endfirsthead`, `\endhead`, `\endfoot`, `\endlastfoot`). | Eliminates ambiguity on multi-page checks; column headers repeat on all pages. |
| **2. Footer Overlap (Row G4 on Page 30)** | Tables ran too close to bottom margin (`1in`). Multirow cells split awkwardly, with row "G4" bleeding over the green footer rule. | Geometry bottom set to `1.15in`, `footskip=0.55in`, row stretch `1.18`, `\needspace{5\baselineskip}` before girder blocks, and non-breaking `\\*`. | Zero footer overlap. Clean page transitions; multirow cells stay intact. |
| **3. Chapter 3 Load Tables** | Live loads & footpaths were cramped in a single 4-row key-value table. No dedicated unit columns; vehicles lumped in one string. | Split into **Table 3.3 (Vehicular Live Loads)** and **Table 3.4 (Footpath Loads)**. Explicit unit columns; filters to UI-selected vehicles. | Full compliance with IRC:6 reporting norms; clear display of IF, Braking, and Centrifugal forces. |
| **4. Section 5.5 UR Charts** | No visual demand/capacity plots existed. All checks were dense numerical text. | Auto-generated high-resolution bar charts for **Girders, Deck Slab, Cross Bracing, and End Diaphragms** with red dashed line at $\text{UR} = 1.0$. | Instant visual assessment of structural safety margins and governing members. |
| **5. Chapter 7 Material Quantity Charts** | Pure text BOM Table 7.1 with no graphical visualization of material distribution. | Added **Section 7.2** with dual visual charts: **Structural Steel Tonnage Breakdown** and **Concrete Volume ($\text{m}^3$) vs. Rebar Weight (MT)**. | Clear visualization of structural steel components and concrete-to-rebar ratios. |
| **6. Architecture & Styling** | Hardcoded LaTeX styling, colors, and margins scattered across 10+ chapter files. Hard dependency on `openseespy`. | Centralized in `styles.py`. All chapter files import from it. Standalone `_extract_osdag_summary()` in `report_utils.py`. | Maintainable single source of truth; safe execution across all environments. |

---

## 2. Detailed Technical Comparison by Requirement

### 2.1. Repeating Table Headers (`LongTable`)

#### Before: Missing Headers on Subsequent Pages
```latex
\begin{longtable}{|L{2.2cm}|L{1.8cm}|p{3.8cm}|p{3.8cm}|p{3.8cm}|}
\caption{\textbf{Girder General Information}}
\hline
\textbf{Girder} & \textbf{Member ID} & \textbf{Design Mode} & \textbf{Girder Type} & \textbf{Girder Symmetry} \\[6pt]
\hline
% [NO \endfirsthead, NO \endhead]
% On page 2, table continues with bare rows and no header!
G1 & G1M1 & Optimized & Welded I & Symmetrical \\[8pt] \hline
G2 & G2M1 & Optimized & Welded I & Symmetrical \\[8pt] \hline
\end{longtable}
```

#### After: Standard 4-Stage Repeating LongTable Header
```latex
\begin{longtable}{|L{2.2cm}|L{1.8cm}|p{3.8cm}|p{3.8cm}|p{3.8cm}|}
\caption{\textbf{Girder General Information}}\\
\hline
\textbf{Girder} & \textbf{Member ID} & \textbf{Design Mode} & \textbf{Girder Type} & \textbf{Girder Symmetry} \\[6pt]
\hline
\endfirsthead
\hline
\multicolumn{5}{c}{\small\textit{(Girder General Information --- Continued from previous page)}} \\[4pt]
\hline
\textbf{Girder} & \textbf{Member ID} & \textbf{Design Mode} & \textbf{Girder Type} & \textbf{Girder Symmetry} \\[6pt]
\hline
\endhead
\hline
\multicolumn{5}{r}{\small\textit{Continued on next page\ldots}} \\
\endfoot
\hline
\endlastfoot
% Rows continue cleanly with repeating headers on every page!
G1 & G1M1 & Optimized & Welded I & Symmetrical \\[8pt] \hline
\end{longtable}
```

---

### 2.2. Footer Overlap Fix (Row "G4" on Page 30)

#### Before: Unprotected Multirow Breaking Over Footer
In Table 5.10 (*Serviceability -- Deflection Checks*), each girder G1..G4 had a two-row multirow entry. With a default 1-inch bottom margin and standard `\\[6pt]` row terminators, G4 broke across the bottom of page 30 and its bottom border bled over `\fancyfoot`.

#### After: Guarded Page Boundaries
```latex
% Preamble geometry in report_generator.py:
\usepackage[a4paper, margin=1in, bottom=1.15in, footskip=0.55in]{geometry}
\renewcommand{\arraystretch}{1.18}
\setlength{\extrarowheight}{1.5pt}
\BeforeBeginEnvironment{longtable}{\needspace{6\baselineskip}}
\AtBeginEnvironment{longtable}{\raggedbottom}

% Table 5.10 row generation in chap5.py:
\needspace{5\baselineskip}
\multirow{2}{*}{\makecell{G4}} & Live Load Deflection, $\delta_{LL}$ (mm) & L/800 = 30.0 mm & 14.100 mm & PASS \\*[6pt]
\cline{2-5}
 & Total Load Deflection, $\delta_{total}$ (mm) & L/600 = 40.0 mm & 22.200 mm & PASS \\[6pt]
\hline
```

---

### 2.3. Chapter 3 Load Tables Split

#### Before: Single Merged Table
```latex
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Live Loads (LL)}}
\hline
\textbf{parameter} & \textbf{value} \\ \hline
\textnormal{Vehicles Considered} & Class A, Class 70R (Wheeled) \\[6pt] \hline
\textnormal{Impact Factor (IRC 6)} & Class A: 1.154, Class AA/70R: 1.088 \\[6pt] \hline
\textnormal{Braking Load (IRC 6)} & 392.40 kN (40.00 tonnes) \\[6pt] \hline
\textnormal{Footpath Live Load (if applicable)} & 4.000 kN/m² \\[6pt] \hline
\end{longtable}
```

#### After: Decoupled Tables with Dedicated Unit Columns

**Table 3.3: Vehicular Live Loads (LL) --- per IRC 6**
- Columns: `Vehicle Class`, `Impact Factor`, `Braking Force (kN)`, `Centrifugal Force (kN)`, `Reference Standard`
- Filters dynamically to only the vehicles selected in the UI's Loading tab.

**Table 3.4: Pedestrian Footpath Loads --- per IRC 6**
- Columns: `Location`, `Intensity (kN/m²)`, `Width (m)`, `Total Load (kN/m)`, `Reference Standard`
- Formatted with explicit width, linear load, and IRC:6 Cl. 206.1 references.

---

### 2.4. Section 5.5: Utilization Ratio (UR) Charts

- Auto-generated Matplotlib bar charts for:
  1. **Girders:** Peak DCR per girder across governing load cases.
  2. **Concrete Deck Slab:** Sagging, hogging, cantilever overhang, punching shear, and one-way shear URs.
  3. **Cross Bracing:** Compression and tension member efficiencies.
  4. **End Diaphragms:** Member efficiencies across all pairs.
- Distinct **red dashed reference line at $\text{UR} = 1.0$** labeled *UR = 1.0 (Limit)*.
- Values annotated directly above each bar in high-resolution PNG format.

---

### 2.5. Chapter 7: Material Quantity Charts

- Added **Section 7.2: Material Quantity Breakdown Charts**:
  - **Chart A:** Structural Steel Tonnage breakdown by component (Girders, Cross Bracing, End Diaphragms, Shear Studs).
  - **Chart B:** Dual-axis bar chart comparing Concrete Volume ($\text{m}^3$, green bars) versus Reinforcement Steel Weight ($\text{MT}$, red bars).
- Table 7.1 converted to LongTable with repeating continuation headers.

---

## 3. Summary of Deliverables

1. **GitHub Repository:** [https://github.com/vdadheech/OsdagBridge](https://github.com/vdadheech/OsdagBridge) (`dev` branch)
2. **Technical Documentation:** `docs/Technical_Changes.md` and `docs/Report_Before_vs_After_Comparison.md`
3. **Collaborator:** Reminder to invite `Nidhikhare12` via [Repo Settings > Collaborators](https://github.com/vdadheech/OsdagBridge/settings/access).
