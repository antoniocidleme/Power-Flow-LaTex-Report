import pandas as pd
import numpy as np
import pandapower as pp

class PFResult:
    def __init__(self, df_bus, df_line, df_trafo, df_gen, df_data_info, df_data_bus, df_data_line, df_data_trafo):
        self.df_bus = df_bus
        self.df_line = df_line
        self.df_trafo = df_trafo
        self.df_gen = df_gen
        self.df_data_info = df_data_info
        self.df_data_bus = df_data_bus
        self.df_data_line = df_data_line
        self.df_data_trafo = df_data_trafo

def power_flow_calculator(arquivo):
    df_parameters = pd.read_excel(
        arquivo,
        header=2,
        usecols="C"
    ).dropna()
    df_buses = pd.read_excel(
        arquivo,
        header=3,
        usecols="E:O"
    )
    df_lines = pd.read_excel(
        arquivo,
        header=3,
        usecols="Q:V"
    ).dropna()
    df_trafos = pd.read_excel(
        arquivo,
        header=3,
        usecols="X:AG"
    ).dropna()

    SlackBus = df_parameters.iloc[0,0] # No.
    Frequency = df_parameters.iloc[1,0]   # Hz
    Vbase_kv = df_parameters.iloc[2,0]  # kV
    Sbase = df_parameters.iloc[3,0] # MVA
    tolerance = df_parameters.iloc[4,0]
    max_interations = df_parameters.iloc[5,0]

    Zbase = (Vbase_kv**2) / Sbase   # ohm
    Cbase = (Sbase * 1e6) / (2*np.pi*Frequency*(Vbase_kv*1e3)**2)    # F

    # Dataframe ajusts
    df_buses = df_buses.dropna(subset=[df_buses.columns[0], df_buses.columns[1]])
    df_buses.iloc[:, [2,3]] = df_buses.iloc[:, [2,3]].fillna(0)
    df_gen = df_buses.iloc[:, [0] + list(range(4,9))].dropna(subset=[df_buses.columns[4], df_buses.columns[8]])
    generators_info_complete = list(zip(df_gen.iloc[:,0], df_gen.iloc[:,1], df_gen.iloc[:,2], df_gen.iloc[:,3], df_gen.iloc[:,4], df_gen.iloc[:,5]))
    df_cap = df_buses.iloc[:, [0, 9, 10]].dropna(subset=df_buses.columns[10]).fillna(0)

    # Infos in Tuples
    buses_info = list(zip(df_buses.iloc[:,0], df_buses.iloc[:,1]))
    lines_info = list(zip(df_lines.iloc[:,0], df_lines.iloc[:,1], df_lines.iloc[:,2], df_lines.iloc[:,3], df_lines.iloc[:,4], df_lines.iloc[:,5]))
    loads_info = list(zip(df_buses.iloc[:,0], df_buses.iloc[:,2], df_buses.iloc[:,3]))
    generators_info = [t for t in generators_info_complete if t[0] != SlackBus]
    capacitors_info = list(zip(df_cap.iloc[:,0], df_cap.iloc[:,1], df_cap.iloc[:,2]))
    transformers_info = list(zip(df_trafos.iloc[:,0], df_trafos.iloc[:,1], df_trafos.iloc[:,2], df_trafos.iloc[:,3], df_trafos.iloc[:,4], df_trafos.iloc[:,5], df_trafos.iloc[:,6], df_trafos.iloc[:,7], df_trafos.iloc[:,8], df_trafos.iloc[:,9]))

    # Create System
    net = pp.create_empty_network(sn_mva=Sbase, f_hz=Frequency)

    # Buses
    buses = {}
    for num, vn in buses_info:
        buses[num] = pp.create_bus(
            net,
            vn_kv=vn,
            name=f"Barra {num}"
        )

    # Slack Bus
    pp.create_ext_grid(
        net,
        bus=buses[SlackBus],
        vm_pu=1.0,
        va_degree=0,
        name="GS1"
    )

    # Lines
    for i, (fb, tb, r_pu, x_pu, bsh_pu, imax) in enumerate(lines_info):
        pp.create_line_from_parameters(
            net,
            from_bus=buses[fb],
            to_bus=buses[tb],
            length_km=1.0,
            r_ohm_per_km=r_pu * Zbase,
            x_ohm_per_km=x_pu * Zbase,
            c_nf_per_km=bsh_pu * Cbase * 1e9,  # bsh = 2*(bsh/2)
            max_i_ka=imax,
            name=f"Line {fb}-{tb}"
        )

    # Loads
    for i, (b, p, q) in enumerate(loads_info):
        pp.create_load(
            net,
            buses[b],
            p_mw=p,
            q_mvar=q,
            name=f"Load {i+1}"
        )

    # Generators
    for i, (b, p, v, pmax, qmin, qmax) in enumerate(generators_info):
        pp.create_gen(
            net,
            bus=buses[b],
            p_mw=p,
            vm_pu=v,
            min_q_mvar=qmin,
            max_q_mvar=qmax,
            max_p_mw=pmax,
            name=f"GS{i+2}"
        )

    # Capacitors
    for i, (b, p, q) in enumerate(capacitors_info):
        pp.create_shunt(
            net,
            bus=buses[b],
            p_mw=p*Sbase,
            q_mvar=-q*Sbase,
            name=f"C{b}"
        )

    # Transformers
    for i, (hb, lb, sn, vh, vl, r, x, pfe, i0, sd) in enumerate(transformers_info):
        pp.create_transformer_from_parameters(
            net,
            hv_bus=buses[hb],
            lv_bus=buses[lb],
            sn_mva=sn,
            vn_hv_kv=vh,
            vn_lv_kv=vl,
            vkr_percent=r,
            vk_percent=x,
            pfe_kw=pfe,
            i0_percent=i0,
            shift_degree=sd,
            name=f"Trafo {i+1}"
        )

    # Power Flow
    pp.runpp(
        net,
        algorithm="nr",
        tolerance_mva=float(tolerance),
        max_iteration=int(max_interations),
        init="flat"
    )

    # Dataframes
    df_results_buses = pd.DataFrame({
        "Bus": df_buses.iloc[:,0].astype(int),
        "Voltage_pu": net.res_bus.iloc[:,0],
        "Angle_deg": net.res_bus.iloc[:,1],
        "P_MW": net.res_bus.iloc[:,2],
        "Q_MVAr": net.res_bus.iloc[:,3]
    })
    df_results_lines = pd.DataFrame({
        "From": df_lines.iloc[:,0],
        "To": df_lines.iloc[:,1],
        "F:T_P_MW": net.res_line.iloc[:,0],
        "F:T_Q_MVAr": net.res_line.iloc[:,1],
        "T:F_P_MW": net.res_line.iloc[:,2],
        "T:F_Q_MVAr": net.res_line.iloc[:,3],
        "Losses_P_MW": net.res_line.iloc[:,4],
        "Losses_Q_MVAr": net.res_line.iloc[:,5]
    })
    df_results_transformers = pd.DataFrame({
        "High_Bus": df_trafos.iloc[:,0].astype(int),
        "Low_Bus": df_trafos.iloc[:,1].astype(int),
        "H:L_P_MW": net.res_trafo.iloc[:,0] ,
        "H:L_Q_MVAr": net.res_trafo.iloc[:,1] ,
        "L:H_P_MW": net.res_trafo.iloc[:,2] ,
        "L:H_Q_MVAr": net.res_trafo.iloc[:,3] ,
        "Losses_P_MW": net.res_trafo.iloc[:,4] ,
        "Losses_Q_MVAr": net.res_trafo.iloc[:,5],
        "High_I_kA": net.res_trafo.iloc[:,6],
        "Low_I_kA": net.res_trafo.iloc[:,7]
    })
    df_for_gen = df_buses.set_index("No.")
    lst_slack = [SlackBus, net.res_ext_grid.iloc[0,0], net.res_ext_grid.iloc[0,1], df_for_gen.loc[SlackBus, "Pmax (MW)"], df_for_gen.loc[SlackBus, "Qmin (MVAr)"], df_for_gen.loc[SlackBus, "Qmax (MVAr)"]]
    df_results_generators = pd.DataFrame([{
        "Bus": lst_slack[0],
        "P_MW": float(lst_slack[1]),
        "Q_MVAr": float(lst_slack[2]),
        "Pmax_MW": float(lst_slack[3]),
        "Qmin_MVAr": float(lst_slack[4]),
        "Qmax_MVAr": float(lst_slack[5])
    }])
    for i, gen in enumerate(generators_info):
        lst_gen = [gen[0], net.res_gen.iloc[i, 0], net.res_gen.iloc[i, 1], gen[3], gen[4], gen[5]]
        df_results_generators.loc[len(df_results_generators)] = lst_gen
    df_results_generators["Bus"] = df_results_generators["Bus"].astype(int)

    return PFResult(df_results_buses, df_results_lines, df_results_transformers, df_results_generators, df_parameters, df_buses, df_lines, df_trafos)


if __name__ == "__main__":

    file = "data.xlsx"
    res = power_flow_calculator(file)

    print(res.df_data_info)
    print(res.df_data_bus)
    print(res.df_data_line)
    print(res.df_data_trafo)
    print(res.df_bus)
    print(res.df_line)
    print(res.df_trafo)
    print(res.df_gen)
