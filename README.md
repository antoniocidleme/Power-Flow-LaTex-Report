# Power-Flow-LaTex-Report
Create a LaTeX power flow report from information in an Excel file using the Pandas Power library in Python.

Calculate power flow in an electrical system from a populated Excel spreadsheet using the panda power library in Python.

Generate a LaTeX report with result tables and diagrams indicating the information relevant to the power flow analysis.

Fill in the tables in data.xlsx and save it. Then specify the file path for use in the Python function power_flow_calculator(file).

The data.xlsx file is provided in the repository. The information in the load, generator and shunt capacitor columns can be left blank if the bar does not contain them. The remaining information must be filled in, even if it is zero.

The text of the latex report can be generated as a string in latex format using the response from the power_flow_calculator(file) function in the power_flow_report_latex(response) function.

To generate the .tex file, use the response from power_flow_calculator(file), the path of an folder, and a name for the .tex file in the function power_flow_report_latex_save(response, directory, "report.tex").

This repository provides a validation example.
