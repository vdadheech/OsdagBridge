from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.styles import make_longtable_header


def ch1_project_info(m):
    return r"""
\chapter{Project Information}

This section records all project metadata as entered by the designer.

\section{Project and Design Team Details}
\label{sec:project-details}

\begin{longtable}{|L{5.5cm}|L{9.5cm}|}
\caption{\textbf{Project and Design Team Details}}\\
\hline
\textbf{Parameter} & \textbf{Details} \\[6pt]
\hline
""" + make_longtable_header(2, r"\textbf{Parameter} & \textbf{Details} \\[6pt]", "Project and Design Team Details") + r"""
\textnormal{Project Name} & """ + _tex(m.project_name) + r""" \\[6pt]
\hline
\textnormal{Project Location} & """ + _tex(m.project_location) + r""" \\[6pt]
\hline
\textnormal{Designer} & """ + _tex(m.designer) + r""" \\[6pt]
\hline
\textnormal{Reviewer} & """ + _tex(m.reviewer) + r""" \\[6pt]
\hline
\textnormal{Organization} & """ + _tex(m.company) + r""" \\[6pt]
\hline
\textnormal{Client} & """ + _tex(m.client) + r""" \\[6pt]
\hline
\textnormal{Software Version} & OsdagBridge \\[6pt]
\hline
\end{longtable}


\section{Applicable Codes and Standards}
\label{sec:codes}

\begin{itemize}
\item Indian Roads Congress (IRC) 5: General Features of Design
\item Indian Roads Congress (IRC) 6: Loads and Load Combinations
\item Indian Roads Congress (IRC) 22: Composite Construction (Limit State Design)
\item Indian Roads Congress (IRC) 24: Steel Road Bridges (Limit State Method)
\item Indian Roads Congress (IRC) 112: Concrete Road Bridges (deck design)
\item Indian Roads Congress Special Publication (IRC SP) 114: Seismic Design of Road Bridges
\item Indian Standard (IS) 800: General Construction in Steel
\item Indian Standard (IS) 2062: Hot Rolled Structural Steel Specification
\item Indian Standard (IS) 6006: Steel Bearings
\end{itemize}
"""
