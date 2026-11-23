# =============================================================================
# Chapter 3: Loads and Load Combinations — Refactored
# =============================================================================
# 1. Split vehicle live loads and footpath loads into separate tables.
# 2. Proper unit columns: Vehicle Class, Impact Factor, Braking Force (kN),
#    Centrifugal Force (kN), Standard Reference.
# 3. Only vehicles selected in UI Loading tab are displayed.
# 4. LongTable environments with repeating headers (\endfirsthead, \endhead).
# 5. Centralized formatting from styles.py.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import make_longtable_header


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = float(span) if span not in (None, "") else 0.0

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    try:
        lanes_int = int(lanes) if lanes not in (None, "") else 1
    except (TypeError, ValueError):
        lanes_int = 1

    try:
        braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
        braking_force_kN = braking_force_t * 9.81
        braking_str = f"{braking_force_kN:.2f}"
    except Exception:
        braking_str = "---"

    # Centrifugal force per IRC 6 Cl. 212: C = W * V^2 / (127 * R).
    # For straight bridges (typical for short-span steel girder bridges), C = 0.
    centrifugal_str = "0.00 (Straight)"

    # ── Separate Vehicle Live Loads Table (Only UI-Selected Vehicles) ─────────
    vehicle_rows = []

    if input_dict.get(KEY_LL_IRC_CLASS_A):
        try:
            im_a = 1.0 + IRC6_2017.cl_208_2_impact_factor(span_m)
            im_str = f"{im_a:.3f}"
        except Exception:
            im_str = "N/A"
        vehicle_rows.append([
            "IRC Class A",
            im_str,
            braking_str,
            centrifugal_str,
            "IRC 6 Cl. 204.1"
        ])

    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        try:
            im_70rw = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
            im_str = f"{im_70rw:.3f}"
        except Exception:
            im_str = "N/A"
        vehicle_rows.append([
            "IRC Class 70R (Wheeled)",
            im_str,
            braking_str,
            centrifugal_str,
            "IRC 6 Cl. 204.2"
        ])

    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        try:
            im_70rt = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
            im_str = f"{im_70rt:.3f}"
        except Exception:
            im_str = "N/A"
        vehicle_rows.append([
            "IRC Class 70R (Tracked)",
            im_str,
            braking_str,
            centrifugal_str,
            "IRC 6 Cl. 204.2"
        ])

    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        try:
            im_aaw = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
            im_str = f"{im_aaw:.3f}"
        except Exception:
            im_str = "N/A"
        vehicle_rows.append([
            "IRC Class AA (Wheeled)",
            im_str,
            braking_str,
            centrifugal_str,
            "IRC 6 Cl. 204.3"
        ])

    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        try:
            im_aat = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
            im_str = f"{im_aat:.3f}"
        except Exception:
            im_str = "N/A"
        vehicle_rows.append([
            "IRC Class AA (Tracked)",
            im_str,
            braking_str,
            centrifugal_str,
            "IRC 6 Cl. 204.3"
        ])

    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        vehicle_rows.append([
            "IRC Class SV (Special Vehicle)",
            "1.000",
            braking_str,
            centrifugal_str,
            "IRC 6 Annex B"
        ])

    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        try:
            im_bg = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
            im_str = f"{im_bg:.3f}"
        except Exception:
            im_str = "N/A"
        vehicle_rows.append([
            "IRC Class 70R (Bogie)",
            im_str,
            braking_str,
            centrifugal_str,
            "IRC 6 Cl. 204.2"
        ])

    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        vehicle_rows.append([
            "IRC Class Fatigue",
            "1.000",
            "---",
            "---",
            "IRC 6 Cl. 204.4"
        ])

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            c_name = c.get('name') if isinstance(c, dict) else str(c)
            vehicle_rows.append([
                _tex(c_name),
                "1.000",
                braking_str,
                centrifugal_str,
                "User Defined"
            ])

    if not vehicle_rows:
        vehicle_rows_tex = r"\multicolumn{5}{|c|}{\textit{No live load vehicle selected in Loading Tab}} \\[6pt]" + "\n" + r"\hline"
    else:
        v_lines = []
        for r in vehicle_rows:
            v_lines.append(
                r"\textnormal{" + _tex(r[0]) + r"} & "
                + _tex(r[1]) + r" & "
                + _tex(r[2]) + r" & "
                + _tex(r[3]) + r" & "
                + _tex(r[4]) + r" \\[6pt]" + "\n"
                + r"\hline"
            )
        vehicle_rows_tex = "\n".join(v_lines)

    # ── Separate Footpath Live Load Table ──────────────────────────────────────
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    fp_width = input_dict.get(KEY_TS_FOOTPATH_WIDTH, "1.5")
    try:
        fp_w_m = float(fp_width)
    except Exception:
        fp_w_m = 1.5

    has_fp = str(input_dict.get(KEY_FOOTPATH, "")).strip().lower() in ("yes", "true", "1")

    if has_fp:
        if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic", ""):
            try:
                fp_intensity = IRC6_2017.cl_206_1_footway_load()
            except Exception:
                fp_intensity = 4.0
            fp_int_str = f"{fp_intensity:.3f}"
            fp_ref = "IRC 6 Cl. 206.1"
        else:
            try:
                fp_intensity = float(fp_value)
                fp_int_str = f"{fp_intensity:.3f}"
            except Exception:
                fp_int_str = str(fp_value)
                fp_intensity = 4.0
            fp_ref = "User Specified"

        fp_total_linear = fp_intensity * fp_w_m
        fp_rows = [
            f"\\textnormal{{Pedestrian Footpath (Left)}} & {fp_int_str} & {fp_w_m:.2f} & {fp_total_linear:.2f} & {fp_ref} \\\\[6pt]\n\\hline",
            f"\\textnormal{{Pedestrian Footpath (Right)}} & {fp_int_str} & {fp_w_m:.2f} & {fp_total_linear:.2f} & {fp_ref} \\\\[6pt]\n\\hline",
        ]
        footpath_rows_tex = "\n".join(fp_rows)
    else:
        footpath_rows_tex = r"\multicolumn{5}{|c|}{\textit{Footpath not provided for this bridge configuration}} \\[6pt]" + "\n" + r"\hline"

    # ── Wind Load values ───────────────────────────────────────────────────────
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass

    # ── Seismic Load values ────────────────────────────────────────────────────
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah = _res.get("Ah")
            if not sl_av:
                sl_av = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    # ── Temperature Load values ───────────────────────────────────────────────
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise = f"{_bt_max - _mean:.2f}"
            tl_fall = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # ── Load Combinations ──────────────────────────────────────────────────────
    _LOAD_LABEL_MAP = {
        'dead_load': 'DL',
        'surfacing': 'SIDL',
        'live_load': 'LL',
        'wind_load': 'WL',
        'thermal_load': 'TL',
        'vehicle_collision': 'VC',
        'barge_impact': 'BI',
        'floating_bodies': 'FB',
        'seismic': 'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    lc_rows_str = "\n".join(lc_rows)

    hdr_dl  = r"\textbf{Parameter} & \textbf{Value} \\[6pt]"
    hdr_dw  = r"\textbf{Parameter} & \textbf{Value} \\[6pt]"
    hdr_veh = r"\textbf{Vehicle Class} & \textbf{Impact Factor} & \textbf{Braking Force (kN)} & \textbf{Centrifugal Force (kN)} & \textbf{Reference Standard} \\[6pt]"
    hdr_fp  = r"\textbf{Location} & \textbf{Intensity (kN/m$^2$)} & \textbf{Width (m)} & \textbf{Total Load (kN/m)} & \textbf{Reference Standard} \\[6pt]"
    hdr_wl  = r"\textbf{Parameter} & \textbf{Value} \\[6pt]"
    hdr_el  = r"\textbf{Parameter} & \textbf{Value} \\[6pt]"
    hdr_tl  = r"\textbf{Parameter} & \textbf{Value} \\[6pt]"
    hdr_lc  = r"\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]"

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design. In accordance with IRC:6, live loads are categorized into vehicular live loads and pedestrian footpath loads, each presented in a dedicated table below.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{9.5cm}|}
\caption{\textbf{Dead Load -- Self Weight}}\\
\hline
""" + hdr_dl + r"""
\hline
""" + make_longtable_header(2, hdr_dl, "Dead Load -- Self Weight") + r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{9.5cm}|}
\caption{\textbf{Dead Load for Surfacing (DW)}}\\
\hline
""" + hdr_dw + r"""
\hline
""" + make_longtable_header(2, hdr_dw, "Dead Load for Surfacing") + r"""
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{4.2cm}|C{2.6cm}|C{3.0cm}|C{3.0cm}|L{2.8cm}|}
\caption{\textbf{Vehicular Live Loads (LL) --- per IRC 6}}\\
\hline
""" + hdr_veh + r"""
\hline
""" + make_longtable_header(5, hdr_veh, "Vehicular Live Loads (LL)") + vehicle_rows_tex + r"""
\end{longtable}
\noindent\textit{Note: Only vehicles selected in the UI Loading tab are included. Braking force is calculated per IRC:6 Cl. 211. Centrifugal force is per IRC:6 Cl. 212.}

\vspace{1em}
\begin{longtable}{|L{4.5cm}|C{2.6cm}|C{2.2cm}|C{2.8cm}|L{3.0cm}|}
\caption{\textbf{Pedestrian Footpath Loads --- per IRC 6}}\\
\hline
""" + hdr_fp + r"""
\hline
""" + make_longtable_header(5, hdr_fp, "Pedestrian Footpath Loads") + footpath_rows_tex + r"""
\end{longtable}
\noindent\textit{Note: Footpath live load intensity is per IRC:6 Cl. 206.1 based on effective span length.}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{9.5cm}|}
\caption{\textbf{Wind Load (WL) --- per IRC 6}}\\
\hline
""" + hdr_wl + r"""
\hline
""" + make_longtable_header(2, hdr_wl, "Wind Load (WL)") + r"""
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{9.5cm}|}
\caption{\textbf{Earthquake Load (EL) --- per IRC 6}}\\
\hline
""" + hdr_el + r"""
\hline
""" + make_longtable_header(2, hdr_el, "Earthquake Load (EL)") + r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{9.5cm}|}
\caption{\textbf{Temperature Load (TL) --- per IRC 6}}\\
\hline
""" + hdr_tl + r"""
\hline
""" + make_longtable_header(2, hdr_tl, "Temperature Load (TL)") + r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|C{3.5cm}|p{12.0cm}|}
\caption{\textbf{Load Combinations}}\\
\hline
""" + hdr_lc + r"""
\hline
""" + make_longtable_header(2, hdr_lc, "Load Combinations") + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""
