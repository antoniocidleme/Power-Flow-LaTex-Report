import pandas as pd
import numpy as np
import power_flow_calculator as pfc
import os

def power_flow_report_latex(res):
    df_results_buses = res.df_bus
    df_results_lines = res.df_line
    df_results_transformers = res.df_trafo
    df_results_generators = res.df_gen
    df_buses = res.df_data_bus
    df_lines = res.df_data_line
    df_trafos = res.df_data_trafo

    SlackBus = res.df_data_info.iloc[0,0]
    Sbase = res.df_data_info.iloc[3,0]
    
    text = ""
    text += "\\documentclass{article}\n\\usepackage{geometry}\n\\usepackage{pdflscape}\n\\usepackage{makecell}\n\\usepackage{adjustbox}\n\\usepackage{tikz}\n\\usetikzlibrary{calc}\n\\usetikzlibrary{arrows.meta}\n"
    text += "\\geometry{top=50pt, left=10pt, right=10pt}\n\\title{\\textbf{POWER FLOW ANALYSIS} \\vspace{15pt} \\\\ %d - Bus System}\n\\date{\\vspace{-20pt}\\today}\n" % (int(df_buses.shape[0]))
    text += "\\begin{document}\n\\maketitle\n"

    n_buses = len(df_results_buses)
    text += "\\vspace*{\\fill}\n\\begin{center}\n"
    text += "\\begin{tikzpicture}[auto, node distance=2cm, bus/.style={draw, circle, minimum size=0.9cm, inner sep=0pt, font=\\fontsize{15pt}{10pt}\\selectfont}, midarrow/.style={thick, -{Stealth[length=4mm, width=3mm]}}, hightrafo/.style={draw, circle, minimum size=0.8cm}, lowtrafo/.style={draw, circle, minimum size=0.7cm}]\n"
    for i in range(0, n_buses):
        n_ang = 360 / n_buses
        x = 5 * np.cos(np.deg2rad(n_ang * i))
        y = 5 * np.sin(np.deg2rad(n_ang * i))
        text += "\\node[bus] (B%d) at (%f, %f) {%d};\n" % (i+1, x, y, i+1)

    n_lines = len(df_results_lines)
    for i in range(0, n_lines):
        f = int(df_results_lines.iloc[i,0])
        t = int(df_results_lines.iloc[i,1])
        text += "\\draw (B%d) -- (B%d);\n" % (f, t)
        
        if df_results_lines.iloc[i,2] >= 0:
            text += f"\\draw[midarrow] (B{f}) -- ($(B{f})!0.5!(B{t})$);\n"
        else:
            text += f"\\draw[midarrow] (B{t}) -- ($(B{t})!0.5!(B{f})$);\n"
    
    n_trafos = len(df_results_transformers)
    for i in range(0,n_trafos):
        h = int(df_trafos.iloc[i,0])
        l = int(df_trafos.iloc[i,1])
        h_lig = ""
        l_lig = ""
        if df_results_transformers.iloc[i,2] >= 0:
            if df_trafos.iloc[i,9] == 30:
                h_lig = "$\\Delta$"
                l_lig = "Y"
            elif df_trafos.iloc[i,9] == -30:
                h_lig = "Y"
                l_lig = "$\\Delta$"
        elif df_results_transformers.iloc[i,2] < 0:
            if df_trafos.iloc[i,9] == 30:
                h_lig = "Y"
                l_lig = "$\\Delta$"
            elif df_trafos.iloc[i,9] == -30:
                h_lig = "$\\Delta$"
                l_lig = "Y"
        text += "\\node[hightrafo] (HT%d) at ($(B%d)!0.45!(B%d)$) {%s};\n" % (i+1, h, l, h_lig)
        text += "\\node[lowtrafo] (LT%d) at ($(B%d)!0.55!(B%d)$) {%s};\n" % (i+1, h, l, l_lig)
        text += "\\draw (B%d) -- (HT%d);\n" % (h, i+1)
        text += "\\draw (LT%d) -- (B%d);\n" % (i+1, l)
        if df_results_transformers.iloc[i,2] >= 0:
            text += "\\draw[midarrow] (B%d) -- ($(B%d)!0.5!(HT%d)$);\n" % (h, h, i+1)
        else:
            text += "\\draw[midarrow] (B%d) -- ($(B%d)!0.5!(LT%d)$);\n" % (l, l, i+1)
    text += "\\end{tikzpicture}\n\\end{center}\n\\vspace{40pt} \\large \\centering $\\longrightarrow$ indicates the direction of active power flow.\n\\vspace*{\\fill}\n\\newpage\n"
    
    text += "{\\centering \\section*{System Data}}\n"
    text += "\\begin{center}\n"
    text += "Buses\\\\\n\\vspace{5pt}\n"
    text += "\\begin{tabular}{|c c|c c|c c c c|c c|}\n\\hline\n"
    text += "\\multicolumn{2}{|c|}{Bus} & \\multicolumn{2}{c|}{Load} & \\multicolumn{4}{c|}{Generator} & \\multicolumn{2}{c|}{Shunt}  \\\\\n\\cline{1-10}\n"
    text += "No. & $V_n$ (kV) & P (MW) & Q (MW) & P (MW) & $P_{max}$ (MW) & $Q_{min}$ (MVAr) & $Q_{max}$ (MVAr) & G (pu) & B (pu) \\\\\n\\hline\n"
    for i in range(0, df_buses.shape[0]):
        b, vn, pl, ql, pg, vm, pmax, qmin, qmax, gs, bs = ["--" if pd.isna(x) else x for x in df_buses.iloc[i, :11]]
        text += f"{int(b)}"
        text += " & "
        text += f"{vn}"
        text += " & "
        text += f"{pl:5.2f}" if isinstance(pl, (int, float)) else str(pl)
        text += " & "
        text += f"{ql:5.2f}" if isinstance(ql, (int, float)) else str(ql)
        text += " & "
        text += f"{pg:5.2f}" if isinstance(pg, (int, float)) else str(pg)
        text += " & "
        text += f"{pmax:5.2f}" if isinstance(pmax, (int, float)) else str(pmax)
        text += " & "
        text += f"{qmin:5.2f}" if isinstance(qmin, (int, float)) else str(qmin)
        text += " & "
        text += f"{qmax:5.2f}" if isinstance(qmax, (int, float)) else str(qmax)
        text += " & "
        text += f"{gs:5.2f}" if isinstance(gs, (int, float)) else str(gs)
        text += " & "
        text += f"{bs:5.2f}" if isinstance(bs, (int, float)) else str(bs)
        text += " \\\\\n"
    text += "\\hline\n\\end{tabular}\n\\end{center}\n"

    # lines
    if df_lines.shape[0] > 0:
        text += "\\begin{center}\n"
        text += "Lines\\\\\n\\vspace{5pt}\n"
        text += "\\begin{tabular}{|c|c|c|c|c|c|}\n\\hline\n"
        text += "From & To & R (pu) & X (pu) & $B_{sh}$ (pu) & $I_{max}$ (kA) \\\\\n\\hline\n"
        for i in range(0, df_lines.shape[0]):
            f, t, r, x, bsh, imax = df_lines.iloc[i, :6]
            text += f"{int(f)} & {int(t)} & {r} & {x} & {bsh} & {imax} \\\\\n"
        text += "\\hline\n\\end{tabular}\n\\end{center}\n"

    # trafos
    if df_trafos.shape[0] > 0:
        text += "\\begin{center}\n"
        text += "Transformers\\\\\n\\vspace{5pt}\n"
        text += "\\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}\n\\hline\n"
        text += "High Bus & Low Bus & $S_n$ (MVA) & $V_n$ High (kV) & $V_n$ Low (kV) & R (\\%) & X (\\%) & $P_{fe}$ (kW) & $I_{0}$ (\\%) & Shift ($^\\circ$) \\\\\n\\hline\n"
        for i in range(0, df_trafos.shape[0]):
            h, l, s, vh, vl, r, x, pfe, i0, shift = df_trafos.iloc[i, :10]
            text += f"{int(h)} & {int(l)} & {s} & {vh} & {vl} & {r} & {x} & {pfe} & {i0} & {shift} \\\\\n"
        text += "\\hline\n\\end{tabular}\n\\end{center}\n"

    text += "\\newpage\n{\\centering \\section*{Results}}"
    text += "\\begin{center}\n"
    text += "Buses\\\\\n\\vspace{5pt}\n"
    text += "\\begin{tabular}{|c|c|c|c|c|}\n\\hline\n"
    text += "Bus & $V_{mag}$ (pu) & $V_{ang}$ ($^\\circ$) & P (MW) & Q (MVAr) \\\\\n\\hline\n"
    for i in range(0, df_results_buses.shape[0]):
        b, vm, va, p, q = df_results_buses.iloc[i, :5]
        text += f"{int(b)} & {vm:7.3f} & {va:7.3f} & {p:5.2f} & {q:5.2f} \\\\\n"
    text += "\\hline\n\\end{tabular}\n\\end{center}\n"


    # lines
    if df_results_lines.shape[0] > 0:
        text += "\\begin{center}\n"
        text += "Lines\\\\\n\\vspace{5pt}\n"
        text += "\\begin{tabular}{|c|c|c|c|c|c|c|c|}\n\\hline\n"
        text += "From & To & F:T P (MW) & F:T Q (MVAr) & T:F P (MW) & T:F Q (MVAr) & $P_{losses}$ (MW) & $Q_{losses}$ (MVAr) \\\\\n\\hline\n"
        for i in range(0, df_results_lines.shape[0]):
            f, t, ftp, ftq, tfp, tfq, lp, lq = df_results_lines.iloc[i, :8]
            text += f"{int(f)} & {int(t)} & {ftp:7.3f} & {ftq:7.3f} & {tfp:7.3f} & {tfq:7.3f} & {lp:7.3f} & {lq:7.3f} \\\\\n"
        text += "\\hline\n\\end{tabular}\n\\end{center}\n"

    # trafos
    if df_results_transformers.shape[0] > 0:
        text += "\\begin{center}\n"
        text += "Transformers\\\\\n\\vspace{5pt}\n"
        text += "\\begin{tabular}{|c|c|c|c|c|c|c|c|}\n\\hline\n"
        text += "High Bus & Low Bus & H:L P (MW) & H:L Q (MVAr) & L:H P (MW) & L:H Q (MVAr) & $P_{losses}$ (MW) & $Q_{losses}$ (MVAr) \\\\\n\\hline\n"
        for i in range(0, df_results_transformers.shape[0]):
            h, l, hlp, hlq, lhp, lhq, lp, lq = df_results_transformers.iloc[i, :8]
            text += f"{int(h)} & {int(l)} & {hlp:7.3f} & {hlq:7.3f} & {lhp:7.3f} & {lhq:7.3f} & {lp:7.3f} & {lq:7.3f} \\\\\n"
        text += "\\hline\n\\end{tabular}\n\\end{center}\n"


    text += "\\begin{center}\n"
    text += "Generators\\\\\n\\vspace{5pt}\n"
    text += "\\begin{tabular}{|c|c|c|c|c|c|}\n\\hline\n"
    text += "Bus & P (MW) & Q (MVAr) & $P_{max}$ (MW) & $Q_{min}$ (MVAr) & $Q_{max}$ (MVAr) \\\\\n\\hline\n"
    for i in range(0, df_results_generators.shape[0]):
        b, p, q, pmax, qmin, qmax = df_results_generators.iloc[i, :6]
        text += f"{int(b)} & {p:7.3f} & {q:7.3f} & {pmax:7.3f} & {qmin:7.3f} & {qmax:7.3f} \\\\\n"  
    text += "\\hline\n\\end{tabular}\n\\end{center}\n"
    
    lst_bus = []
    lst_type = []
    for i in range(0, df_buses.shape[0]):
        element = [0,0,0]
        if df_buses.loc[i, "Pl (MW)"] != 0 or df_buses.loc[i, "Ql (MVAr)"] != 0:
            element[0] = 1
        if pd.notna(df_buses.loc[i, "Pmax (MW)"]):
            element[1] = 1
        if df_buses.loc[i, "G (pu)"] != 0 or df_buses.loc[i, "B (pu)"] != 0: 
            if pd.notna(df_buses.loc[i, "G (pu)"]) or pd.notna(df_buses.loc[i, "B (pu)"]):
                element[2] = 1
        lst_bus.append(element)
        if i == SlackBus - 1:
            lst_type.append("SL")
        elif element[1] == 1:
            lst_type.append("PV")
        else:
            lst_type.append("PQ")
    
    # lst_flow
    lst_flow = []
    for i in range(0, df_buses.shape[0]):
        aux_emp = 0
        lst_flow_bus = []
        for j in range(0, df_results_lines.shape[0]):
            if df_results_lines.iloc[j,0] == i+1:
                lst_flow_bus.append([int(df_results_lines.iloc[j,1]), float(df_results_lines.iloc[j,2]), float(df_results_lines.iloc[j,3])])
                aux_emp = 1
            elif df_results_lines.iloc[j,1] == i+1:
                lst_flow_bus.append([int(df_results_lines.iloc[j,0]), float(df_results_lines.iloc[j,4]), float(df_results_lines.iloc[j,5])])
                aux_emp = 1
        for j in range(0, df_results_transformers.shape[0]):
            if df_results_transformers.iloc[j,0] == i+1:
                lst_flow_bus.append([int(df_results_transformers.iloc[j,1]), float(df_results_transformers.iloc[j,2]), float(df_results_transformers.iloc[j,3])])
                aux_emp = 1
            elif df_results_transformers.iloc[j,1] == i+1:
                lst_flow_bus.append([int(df_results_transformers.iloc[j,0]), float(df_results_transformers.iloc[j,4]), float(df_results_transformers.iloc[j,5])])
                aux_emp = 1
        if aux_emp == 0:
            lst_flow_bus.append([0,0,0])
        lst_flow.append(lst_flow_bus)

    text += "\\begin{landscape}\n\\vspace*{\\fill}\n"
    text += "\\begin{center}\n\\begin{adjustbox}{width=\\textwidth}\n\\begin{tabular}{|c c c c c|c c|c c|c c|c c c|}\n\\hline\n"
    text += "\\multicolumn{5}{|c|}{Bus} & \\multicolumn{2}{c|}{Generation} & \\multicolumn{2}{c|}{Load} & \\multicolumn{2}{c|}{Shunt} & \\multicolumn{3}{c|}{Line Flow} \\\\\n\\hline\n"
    text += "No. & Type & $V_{base}$ (kV) & $V_{mag}$ (pu) & $V_{ang}$ ($^\\circ$) & P (MW) & Q (MVAr) & P (MW) & Q (MVAr) & G (MW) & B (MVAr) & To Bus & $P_{losses}$ (MW) & $Q_{losses}$ (MVAr) \\\\\n\\hline\n"

    cont_qgen = 0
    for i in range(0, df_buses.shape[0]):
        b, vn, pl, ql, pg, vm, pmax, qmin, qmax, gs, bs = [0 if pd.isna(x) else x for x in df_buses.iloc[i, :11]]
        t = lst_type[i]
        vmr, var = df_results_buses.iloc[i, 1:3]
        pgr = 0
        qgr = 0
        if lst_bus[i][1] == 1:
            pgr = df_results_generators.iloc[cont_qgen, 1]
            qgr = df_results_generators.iloc[cont_qgen, 2]
            cont_qgen += 1
        text += "%d & %s & %g & %.3f & %.3f & %g & %g & %g & %g & %g & %g" % (int(b), t, vn, vmr, var, pgr, qgr, pl, ql, gs*Sbase, bs*Sbase)
        if lst_flow[i][0][0] == 0:
            text += " & & & \\\\\n"
        else:
            text += " & \\makecell[t]{"
            for j in range(0, len(lst_flow[i])-1):
                text += "%d \\\\ " % (lst_flow[i][j][0])
            text += "%d}" % (lst_flow[i][-1][0])
            text += " & \\makecell[t]{"
            for j in range(0, len(lst_flow[i])-1):
                text += "%5.2f \\\\ " % (lst_flow[i][j][1])
            text += "%5.2f}" % (lst_flow[i][-1][1])
            text += " & \\makecell[t]{"
            for j in range(0, len(lst_flow[i])-1):
                text += "%5.2f \\\\ " % (lst_flow[i][j][2])
            text += "%5.2f} \\\\\n" % (lst_flow[i][-1][2])
    text += "\\hline\n\\end{tabular}\n\\end{adjustbox}\n\\end{center}\n\\vspace*{\\fill}\n\\newpage\n"

    text += "\\vspace*{\\fill}\n\\begin{center}\n"
    text += "\\begin{tikzpicture}[auto, node distance=2cm, bus/.style={draw, circle, minimum size=0.9cm, inner sep=0pt, font=\\fontsize{15pt}{10pt}\\selectfont}, midarrow/.style={thick, -{Stealth[length=4mm, width=3mm]}}, hightrafo/.style={draw, circle, minimum size=0.8cm}, lowtrafo/.style={draw, circle, minimum size=0.7cm}, ftflow/.style={pos=0.2, above, sloped, font=\\fontsize{0.5pt}{10pt}\\selectfont}, tfflow/.style={pos=0.8, above, sloped, font=\\fontsize{0.5pt}{10pt}\\selectfont}, trafoflow/.style={midway, above=0.8pt, sloped, font=\\tiny}]\n"
    for i in range(0, n_buses):
        n_ang = 360 / n_buses
        x = 6 * np.cos(np.deg2rad(n_ang * i))
        y = 6 * np.sin(np.deg2rad(n_ang * i))
        text += "\\node[bus] (B%d) at (%f, %f) {%d};\n" % (i+1, x, y, i+1)

    n_lines = len(df_results_lines)
    for i in range(0, n_lines):
        f = int(df_results_lines.iloc[i,0])
        t = int(df_results_lines.iloc[i,1])
        text += "\\draw (B%d) -- (B%d) " % (f, t)
        if df_results_lines.iloc[i,3] >= 0:
            text += "node[ftflow] {%5.2f + j%5.2f MVA} " % (df_results_lines.iloc[i,2], abs(df_results_lines.iloc[i,3]))
        else:
            text += "node[ftflow] {%5.2f - j%5.2f MVA} " % (df_results_lines.iloc[i,2], abs(df_results_lines.iloc[i,3]))
        if df_results_lines.iloc[i,5] >= 0:
            text += "node[tfflow] {%5.2f + j%5.2f MVA};\n" % (df_results_lines.iloc[i,4], abs(df_results_lines.iloc[i,5]))
        else:
            text += "node[tfflow] {%5.2f - j%5.2f MVA};\n" % (df_results_lines.iloc[i,4], abs(df_results_lines.iloc[i,5]))
        if df_results_lines.iloc[i,2] >= 0:
            text += f"\\draw[midarrow] (B{f}) -- ($(B{f})!0.5!(B{t})$);\n"
        else:
            text += f"\\draw[midarrow] (B{t}) -- ($(B{t})!0.5!(B{f})$);\n"
    
    n_trafos = len(df_results_transformers)
    for i in range(0,n_trafos):
        h = int(df_trafos.iloc[i,0])
        l = int(df_trafos.iloc[i,1])
        h_lig = ""
        l_lig = ""
        if df_results_transformers.iloc[i,2] >= 0:
            if df_trafos.iloc[i,9] == 30:
                h_lig = "$\\Delta$"
                l_lig = "Y"
            elif df_trafos.iloc[i,9] == -30:
                h_lig = "Y"
                l_lig = "$\\Delta$"
        elif df_results_transformers.iloc[i,2] < 0:
            if df_trafos.iloc[i,9] == 30:
                h_lig = "Y"
                l_lig = "$\\Delta$"
            elif df_trafos.iloc[i,9] == -30:
                h_lig = "$\\Delta$"
                l_lig = "Y"
        text += "\\node[hightrafo] (HT%d) at ($(B%d)!0.45!(B%d)$) {%s};\n" % (i+1, h, l, h_lig)
        text += "\\node[lowtrafo] (LT%d) at ($(B%d)!0.55!(B%d)$) {%s};\n" % (i+1, h, l, l_lig)
        text += "\\draw (B%d) -- (HT%d) " % (h, i+1)
        if df_results_transformers.iloc[i,3] >= 0:
            text += "node[trafoflow] {%5.2f + j%5.2f MVA};\n" % (df_results_transformers.iloc[i,2], abs(df_results_transformers.iloc[i,3]))
        else:
            text += "node[trafoflow] {%5.2f - j%5.2f MVA};\n" % (df_results_transformers.iloc[i,2], abs(df_results_transformers.iloc[i,3]))
        text += "\\draw (LT%d) -- (B%d) " % (i+1, l)
        if df_results_transformers.iloc[i,5] >= 0:
            text += "node[trafoflow] {%5.2f + j%5.2f MVA};\n" % (df_results_transformers.iloc[i,4], abs(df_results_transformers.iloc[i,5]))
        else:
            text += "node[trafoflow] {%5.2f - j%5.2f MVA};\n" % (df_results_transformers.iloc[i,4], abs(df_results_transformers.iloc[i,5]))
        if df_results_transformers.iloc[i,2] >= 0:
            text += "\\draw[midarrow] (B%d) -- ($(B%d)!0.5!(HT%d)$);\n" % (h, h, i+1)
        else:
            text += "\\draw[midarrow] (B%d) -- ($(B%d)!0.5!(LT%d)$);\n" % (l, l, i+1)

    n_bus = len(lst_bus)
    cont_g = 1
    for i in range(0, n_bus):
        ang0 = 360 * i / n_bus
        x = 6 * np.cos(np.deg2rad(ang0))
        y = 6 * np.sin(np.deg2rad(ang0))
        ang_elements = 0
        if sum(lst_bus[i]) == 2:
            ang_elements = 30
        elif sum(lst_bus[i]) == 3:
            ang_elements = 45
        if lst_bus[i][1] == 1:
            if ang_elements == 30:
                gx = x + 1.5 * np.cos(np.deg2rad(ang0 + 30))
                gy = y + 1.5 * np.sin(np.deg2rad(ang0 + 30))
            else:
                gx = x + 1.5 * np.cos(np.deg2rad(ang0))
                gy = y + 1.5 * np.sin(np.deg2rad(ang0))
            text += "\\node[bus] (G%d) at (%f, %f) {$\\sim$};\n" % (cont_g, gx, gy)
            text += "\\draw (B%d) -- (G%d);\n" % (i+1, cont_g)
            text += "\\path (%f, %f) -- (%f, %f) node[midway, above, sloped, font=\\small] {%g MW} node[midway, below, sloped, font=\\small] {%g MVAr};\n" % (gx, gy, 3.2*(gx-x)+x, 3.2*(gy-y)+y, df_results_generators.iloc[cont_g-1,1], df_results_generators.iloc[cont_g-1,2])
            cont_g += 1
        if lst_bus[i][0] == 1:
            if ang_elements == 45:
                lx = x + 2 * np.cos(np.deg2rad(ang0 + 45))
                ly = y + 2 * np.sin(np.deg2rad(ang0 + 45))
            elif ang_elements == 30:
                if lst_bus[i][1] == 0:
                    lx = x + 2 * np.cos(np.deg2rad(ang0 + 30))
                    ly = y + 2 * np.sin(np.deg2rad(ang0 + 30))
                if lst_bus[i][1] == 1:
                    lx = x + 2 * np.cos(np.deg2rad(ang0 - 30))
                    ly = y + 2 * np.sin(np.deg2rad(ang0 - 30))
            elif ang_elements == 0:
                lx = x + 2 * np.cos(np.deg2rad(ang0))
                ly = y + 2 * np.sin(np.deg2rad(ang0))
            text += "\\draw[midarrow] (B%d) -- (%f, %f);\n" % (i+1, lx, ly)
            text += "\\path (%f, %f) -- (%f, %f) node[midway, above, sloped, font=\\small] {%g MW} node[midway, below, sloped, font=\\small] {%g MVAr};\n" % (lx, ly, 1.8*(lx-x)+x, 1.8*(ly-y)+y, df_buses.iloc[i,2], df_buses.iloc[i,3])
        if lst_bus[i][2] == 1:
            cAx0 = x + 1.2 * np.cos(np.deg2rad(ang0 - ang_elements))
            cAy0 = y + 1.2 * np.sin(np.deg2rad(ang0 - ang_elements))
            cAx1 = cAx0 + 0.4 * np.cos(np.deg2rad(ang0 + 90 - ang_elements))
            cAy1 = cAy0 + 0.4 * np.sin(np.deg2rad(ang0 + 90 - ang_elements))
            cAx2 = cAx0 + 0.4 * np.cos(np.deg2rad(ang0 - 90 - ang_elements))
            cAy2 = cAy0 + 0.4 * np.sin(np.deg2rad(ang0 - 90 - ang_elements))
            text += "\\draw (B%d) -- (%f, %f);\n" % (i+1, cAx0, cAy0)
            text += "\\draw (%f, %f) -- (%f, %f);\n" % (cAx1, cAy1, cAx2, cAy2)
            cBx0 = x + 1.4 * np.cos(np.deg2rad(ang0 - ang_elements))
            cBy0 = y + 1.4 * np.sin(np.deg2rad(ang0 - ang_elements))
            cBx1 = cBx0 + 0.4 * np.cos(np.deg2rad(ang0  + 90 - ang_elements))
            cBy1 = cBy0 + 0.4 * np.sin(np.deg2rad(ang0  + 90 - ang_elements))
            cBx2 = cBx0 + 0.4 * np.cos(np.deg2rad(ang0  - 90 - ang_elements))
            cBy2 = cBy0 + 0.4 * np.sin(np.deg2rad(ang0  - 90 - ang_elements))
            text += "\\draw (%f, %f) -- (%f, %f);\n" % (cBx1, cBy1, cBx2, cBy2)
            cCx0 = x + 1.7 * np.cos(np.deg2rad(ang0 - ang_elements))
            cCy0 = y + 1.7 * np.sin(np.deg2rad(ang0 - ang_elements))
            cCx1 = cCx0 + 0.3 * np.cos(np.deg2rad(ang0 + 90 - ang_elements))
            cCy1 = cCy0 + 0.3 * np.sin(np.deg2rad(ang0 + 90 - ang_elements))
            cCx2 = cCx0 + 0.3 * np.cos(np.deg2rad(ang0 - 90 - ang_elements))
            cCy2 = cCy0 + 0.3 * np.sin(np.deg2rad(ang0 - 90 - ang_elements))
            text += "\\draw (%f, %f) -- (%f, %f);\n" % (cBx0, cBy0, cCx0, cCy0)
            text += "\\draw (%f, %f) -- (%f, %f);\n" % (cCx1, cCy1, cCx2, cCy2)
            cDx0 = x + 1.8 * np.cos(np.deg2rad(ang0 - ang_elements))
            cDy0 = y + 1.8 * np.sin(np.deg2rad(ang0 - ang_elements))
            cDx1 = cDx0 + 0.2 * np.cos(np.deg2rad(ang0 + 90 - ang_elements))
            cDy1 = cDy0 + 0.2 * np.sin(np.deg2rad(ang0 + 90 - ang_elements))
            cDx2 = cDx0 + 0.2 * np.cos(np.deg2rad(ang0 - 90 - ang_elements))
            cDy2 = cDy0 + 0.2 * np.sin(np.deg2rad(ang0 - 90 - ang_elements))
            text += "\\draw (%f, %f) -- (%f, %f);\n" % (cDx1, cDy1, cDx2, cDy2)
            cEx0 = x + 1.9 * np.cos(np.deg2rad(ang0 - ang_elements))
            cEy0 = y + 1.9 * np.sin(np.deg2rad(ang0 - ang_elements))
            cEx1 = cEx0 + 0.1 * np.cos(np.deg2rad(ang0 + 90 - ang_elements))
            cEy1 = cEy0 + 0.1 * np.sin(np.deg2rad(ang0 + 90 - ang_elements))
            cEx2 = cEx0 + 0.1 * np.cos(np.deg2rad(ang0 - 90 - ang_elements))
            cEy2 = cEy0 + 0.1 * np.sin(np.deg2rad(ang0 - 90 - ang_elements))
            text += "\\draw (%f, %f) -- (%f, %f);\n" % (cEx1, cEy1, cEx2, cEy2)
            if pd.isna(df_buses.iloc[i,9]):
                df_buses.iloc[i,9] = 0
            text += "\\path (%f, %f) -- (%f, %f) node[midway, above, sloped, font=\\small] {%g MW} node[midway, below, sloped, font=\\small] {%g MVAr};\n" % (cEx0, cEy0, 2*(cEx0-x)+x, 2*(cEy0-y)+y, df_buses.iloc[i,9]*Sbase, df_buses.iloc[i,10]*Sbase)
    text += "\\end{tikzpicture}\n\\end{center}\n\\vspace*{\\fill}\n\\end{landscape}\n"
    text += "\\end{document}"
    
    return text

def power_flow_report_latex_save(power_flow_results, output_dir, file_tex_name):
    text_latex = power_flow_report_latex(power_flow_results)
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, file_tex_name)
    try:
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(text_latex)
        if os.path.getsize(tex_path) > 0:
            print("File saved successfully!")
        else:
            print("The file was saved, but it's empty. Please try again.")
    except Exception as e:
        print(f"Error: {e}")


file = "data.xlsx"
res = pfc.power_flow_calculator(file)

latex_text = power_flow_report_latex(res)
print(latex_text) # for print latex text in terminal

dir = r"C:\Example\Folder"
latex_file_name = "power_flow_report.tex"
power_flow_report_latex_save(res, dir, latex_file_name) # for save .tex document