#!/usr/bin/env python3
import os
import subprocess
import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np
import ROOT

# -------------------------------------------------
# Build Thermal-FIST with tools
# -------------------------------------------------
def build_thermal_fist(repo_path, build_dir):
    build_path = os.path.join(repo_path, build_dir)
    os.makedirs(build_path, exist_ok=True)

    print("#" * 40)
    print("Configuring CMake with BUILD_TOOLS=ON...")
    subprocess.run(
        ["cmake", repo_path, "-B", build_path, "-DBUILD_TOOLS=ON"],
        check=True
    )

    print("#" * 40)
    print("Building Thermal-FIST library and examples...")
    subprocess.run(
        ["cmake", "--build", build_path, "--parallel"],
        check=True
    )

    # Compile thermal_point helper manually
    exe_path = os.path.join(build_path, "bin", "tools", "thermal_point")
    if not os.path.exists(os.path.dirname(exe_path)):
        os.makedirs(os.path.dirname(exe_path))

    lib_path = os.path.join(build_path, "lib")  # <- the actual library folder
    print("#" * 40)
    print("Compiling thermal_point helper manually...")
    compile_cmd = [
        "c++",
        "-std=c++17",
        os.path.join(repo_path, "tools", "thermal_point.cpp"),
        "-I", os.path.join(repo_path, "include"),
        "-L", lib_path,
        "-lThermalFIST",
        "-Wl,-rpath," + lib_path,
        "-o", exe_path,
    ]
    subprocess.run(compile_cmd, check=True)

    if not os.path.isfile(exe_path):
        raise RuntimeError(f"thermal_point executable not found at {exe_path}")

    print(f"thermal_point is ready at: {exe_path}")
    return exe_path

# -------------------------------------------------
# Run thermal_point with given parameters
# -------------------------------------------------
def run_thermal_point(executable, params):

    cmd = [
        executable,
        str(params["particle_list"]),
        str(params["decays_list"]),
        str(params["model_type"]),
        str(params["T"]),
        str(params["V"]),
        str(params["muB"]),
        str(params["muQ"]),
        str(params["muS"]),
        str(params["muC"]),
        str(params["gammaQ"]),
        str(params["gammaS"]),
        str(params["gammaC"]),
        str(params["width_mode"]),
        str(params["feeddown"] if "feeddown" in params else 1),
        str(params["statistics"] if "statistics" in params else 1)
    ]
    print("#" * 40)
    print("Running:")
    print(" ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stdout.strip().split("\n"):
        if line.startswith("RESULT="):
            total_charm_yield = float(line.split("=")[1])
            break
    print("#" * 40)
    print(f"Total charm yield from thermal point: {total_charm_yield}")
    print("#" * 40)

# -------------------------------------------------
# Run thermal_point for a scan over gammaC and V values
# -------------------------------------------------
def run_thermal_scan(executable, params, gammaC_values, gammaS_values, Vs, cents, dndy, outdir, outlabel, outfile):
    outfile_root = f"{outdir}/{outlabel}_scan_results.root"
    print(f"Saving scan results to {outfile_root}...")
    
    root_file = ROOT.TFile(outfile_root, "RECREATE")
    dnccbardy_values = {}
    graph_volume_cent = ROOT.TGraphAsymmErrors()
    graph_volume_cent.SetName("graph_volume_cent")
    graph_gammas_cent = ROOT.TGraphAsymmErrors()
    graph_gammas_cent.SetName("graph_gammas_cent")
    graph_optimised_gammaC_cent = ROOT.TGraphAsymmErrors()
    graph_optimised_gammaC_cent.SetName("graph_optimised_gammaC_cent")
    graph_dndy_cent = ROOT.TGraphAsymmErrors()
    graph_dndy_cent.SetName("graph_dndy_cent")
    graph_dndy_cent.SetLineColor(ROOT.kRed)
    graph_dndy_cent.SetMarkerColor(ROOT.kRed)
    graph_dnccbar_gammaC = []
    graph_dummy = []
    graph_vertical_lines = []

    canv = ROOT.TCanvas("canv", "canv", 800, 800)
    canv.Divide(3,3)
    legend = ROOT.TLegend(0.2, 0.75, 0.6, 0.9)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    for icent, (Vcent, cent, gammaC_vals, gammaS_vals) in enumerate(zip(Vs, cents, gammaC_values, gammaS_values)):
        print(f"\n\nStarting scan for centrality {cent} with V values {Vcent} and gammaS values {gammaS_vals} and gammaC values {gammaC_vals}")
        cent_mean = (cent[0] + cent[1]) / 2
        delta_cent = (cent[1] - cent[0]) / 2
        dnccbardy_values[cent_mean] = {}
        dnccbardy_values[cent_mean]['cent_min'] = cent[0]
        dnccbardy_values[cent_mean]['cent_max'] = cent[1]
        graph_volume_cent.SetPoint(icent, cent_mean, Vcent[0]) # Use Vmin for central value
        graph_gammas_cent.SetPoint(icent, cent_mean, gammaS_vals[0]) # Use gammaS at Vmin for central value
        graph_volume_cent.SetPointError(icent, delta_cent, delta_cent, Vcent[0] - Vcent[1], Vcent[2] - Vcent[0]) # Use Vmin - Vcent and Vmax - Vcent as uncertainties
        graph_gammas_cent.SetPointError(icent, delta_cent, delta_cent, gammaS_vals[0] - gammaS_vals[1], gammaS_vals[2] - gammaS_vals[0]) # Use gammaS at Vmin - gammaS at Vcent and gammaS at Vmax - gammaS at Vcent as uncertainties
        
        outdir_cent = f"{outdir}/cent_{cent[0]}_{cent[1]}"
        os.makedirs(outdir_cent, exist_ok=True)
        params["outdir"] = outdir_cent

        graph_dnccbar_gammaC.append(ROOT.TGraphAsymmErrors())
        for iV, (V, gammaS) in enumerate(zip(Vcent, gammaS_vals)): # Loop over V and gammaS (cent, min, max value) which depends centrality (dnch/deta)
            params["V"] = V
            params["gammaS"] = gammaS

            for igammaC, gammaC in enumerate(gammaC_vals): # Scan over gammaC values
                params["gammaC"] = gammaC
                dnccbardy_values[cent_mean][f'gammaC_{igammaC}'] = gammaC
                dnccbardy_values[cent_mean][f'gammaS_{igammaC}'] = gammaS
                dnccbardy_values[cent_mean][f'V_{iV}'] = V
                # adjust outlabel for debbugging
                params["outlabel"] = f"{outlabel}_cent_{cent[0]}_{cent[1]}_gammaC_{gammaC:.2f}_gammaS_{gammaS:.2f}_V_{V:.0f}"
                graph_dnccbar_gammaC[-1].SetName(f"graph_dnccbar_gammaC_cent_{cent[0]}_{cent[1]}_gammaC_{gammaC:.2f}_gammaS_{gammaS:.2f}_V_{V:.0f}")
                graph_dnccbar_gammaC[-1].GetXaxis().SetTitle("gammaC")
                graph_dnccbar_gammaC[-1].GetYaxis().SetTitle("dnccbardy")


                cmd = [
                    executable,
                    str(params["particle_list"]),
                    str(params["decays_list"]),
                    str(params["model_type"]),
                    str(params["T"]),
                    str(params["V"]),
                    str(params["muB"]),
                    str(params["muQ"]),
                    str(params["muS"]),
                    str(params["muC"]),
                    str(params["gammaQ"]),
                    str(params["gammaS"]),
                    str(params["gammaC"]),
                    str(params["width_mode"]),
                    str(params["feeddown"] if "feeddown" in params else 1),
                    str(params["statistics"] if "statistics" in params else 1),
                    str(params["outdir"]),
                    str(params["outlabel"]),
                    str(params["debug"])
                ]

                print("#" * 40)
                print("Running:")
                print(" ".join(cmd))
            
                result = subprocess.run(cmd, capture_output=True, text=True)
                for line in result.stdout.strip().split("\n"):
                    if line.startswith("RESULT="):
                        total_charm_yield = float(line.split("=")[1])
                        break
                if total_charm_yield is None:
                    print(f"WARNING: no result for gammaC={gammaC} V={V}, stderr:\n{result.stderr}")
                    continue
                dnccbardy_values[cent_mean][f'dnccbardy_gammaC_{igammaC}_V_{iV}'] = total_charm_yield

        dnccbardy_cent_values = [dnccbardy_values[cent_mean][f'dnccbardy_gammaC_{igammaC}_V_0'] for igammaC in range(len(gammaC_vals))] # Use Vcent for central value
        dnccbardy_cent_values_lower = [dnccbardy_values[cent_mean][f'dnccbardy_gammaC_{igammaC}_V_0'] - dnccbardy_values[cent_mean][f'dnccbardy_gammaC_{igammaC}_V_1'] for igammaC in range(len(gammaC_vals))] # Use Vmax - Vcent as lower uncertainty
        dnccbardy_cent_values_upper = [dnccbardy_values[cent_mean][f'dnccbardy_gammaC_{igammaC}_V_2'] - dnccbardy_values[cent_mean][f'dnccbardy_gammaC_{igammaC}_V_0'] for igammaC in range(len(gammaC_vals))] # Use Vmax - Vcent as upper uncertainty

        for idnc, (dnccbardy, dnccbardy_lower, dnccbardy_upper, gammaC) in enumerate(zip(dnccbardy_cent_values, dnccbardy_cent_values_lower, dnccbardy_cent_values_upper, gammaC_vals)):
            graph_dnccbar_gammaC[-1].SetPoint(idnc, gammaC, dnccbardy)
            graph_dnccbar_gammaC[-1].SetPointError(idnc, delta_cent, delta_cent, dnccbardy_lower, dnccbardy_upper)
        
        # fit with pol1 to find the gammaC value that matches the dndy from the xsec list if
        if params["model_type"] == 2: # Only perform the fit for the charm-canonical model, since for the strangeness-canonical the dependence on gammaC is expected to be very weak and the fit would be unstable
            fit_func = ROOT.TF1("pol1", "[0]+[1]*x", gammaC_vals[0], gammaC_vals[-1])
        else:
            fit_func = ROOT.TF1("pol1", "[0]+[1]*x+[2]*x*x", gammaC_vals[0], gammaC_vals[-1])
        graph_dnccbar_gammaC[-1].Fit(fit_func, "S")
        # extract the gammaC value that corresponds to the dndy from the xsec list
        dndy_target = dndy[icent][0]
        if params["model_type"] == 2:
            gammaC_opt = (dndy_target - fit_func.GetParameter(0)) / fit_func.GetParameter(1)
            gammac_opt_min = (dndy[icent][1] - fit_func.GetParameter(0)) / fit_func.GetParameter(1)
            gammac_opt_max = (dndy[icent][2] - fit_func.GetParameter(0)) / fit_func.GetParameter(1)
        else:
            a = fit_func.GetParameter(2)
            b = fit_func.GetParameter(1)
            c = fit_func.GetParameter(0) - dndy_target
            discriminant = b**2 - 4*a*c
            sqrt_disc = np.sqrt(discriminant)
            gammaC_opt = (-b + sqrt_disc) / (2*a) # Choose the solution with the +sqrt since we expect gammaC to be positive and the fit parameter a is expected to be positive since dnccbardy should increase with gammaC
            gammac_opt_min = (-b + np.sqrt(b**2 - 4*a*(fit_func.GetParameter(0) - dndy[icent][1]))) / (2*a)
            gammac_opt_max = (-b + np.sqrt(b**2 - 4*a*(fit_func.GetParameter(0) - dndy[icent][2]))) / (2*a)
        graph_dndy_cent.SetPoint(icent, cent_mean, dndy_target)
        graph_dndy_cent.SetPointError(icent, delta_cent, delta_cent, dndy_target - dndy[icent][1], dndy[icent][2] - dndy_target)
        graph_optimised_gammaC_cent.SetPoint(icent, cent_mean, gammaC_opt)
        graph_optimised_gammaC_cent.SetPointError(icent, delta_cent, delta_cent, gammac_opt_min, gammac_opt_max)

        graph_dnccbar_gammaC[-1].Write()

        # plot dummy band corresponding to the dndy from the xsec list
        graph_dummy.append(ROOT.TGraphAsymmErrors())
        graph_dummy[-1].SetPoint(0, (min(gammaC_vals) + max(gammaC_vals)) / 2, dndy_target)
        graph_dummy[-1].SetPointError(0, (max(gammaC_vals) - min(gammaC_vals)) / 2, (max(gammaC_vals) - min(gammaC_vals)) / 2, dndy_target - dndy[icent][1], dndy[icent][2] - dndy_target)
        graph_dummy[-1].SetFillColorAlpha(ROOT.kRed+1, 0.3)
        graph_dummy[-1].SetLineWidth(0)


        canv.cd(icent + 1)
        graph_dnccbar_gammaC[-1].GetXaxis().SetTitle("#gammaC")
        graph_dnccbar_gammaC[-1].GetYaxis().SetTitle("d#it{N}_{c#bar{c}}/dy")
        graph_dnccbar_gammaC[-1].SetTitle(f"Centrality {cent[0]}-{cent[1]}%")
        graph_dnccbar_gammaC[-1].GetYaxis().SetTitleOffset(1.2)
        graph_dnccbar_gammaC[-1].GetYaxis().SetRangeUser(0, max(dnccbardy_cent_values) * 1.5)
        graph_dnccbar_gammaC[-1].GetYaxis().SetNdivisions(505)
        graph_dnccbar_gammaC[-1].GetYaxis().SetLabelSize(0.04)
        graph_dnccbar_gammaC[-1].GetYaxis().SetTitleSize(0.04)
        graph_dnccbar_gammaC[-1].GetYaxis().SetDecimals()
        graph_dnccbar_gammaC[-1].Draw("APEZ")
        graph_dummy[-1].Draw("5 SAME")
        # draw vertical dotted line corresponding to the optimised gammaC value
        graph_vertical_lines.append(ROOT.TLine(gammaC_opt, 0, gammaC_opt, max(dnccbardy_cent_values) * 1.5))
        graph_vertical_lines[-1].SetLineStyle(ROOT.kDotted)
        graph_vertical_lines[-1].SetLineWidth(2)
        graph_vertical_lines[-1].SetLineColor(ROOT.kGray+1)
        graph_vertical_lines[-1].Draw("SAME")
        graph_vertical_lines.append(ROOT.TLine(gammac_opt_min, 0, gammac_opt_min, max(dnccbardy_cent_values) * 1.5))
        graph_vertical_lines[-1].SetLineStyle(ROOT.kDotted)
        graph_vertical_lines[-1].SetLineWidth(2)
        graph_vertical_lines[-1].SetLineColor(ROOT.kGray+1)
        graph_vertical_lines[-1].Draw("SAME")
        graph_vertical_lines.append(ROOT.TLine(gammac_opt_max, 0, gammac_opt_max, max(dnccbardy_cent_values) * 1.5))
        graph_vertical_lines[-1].SetLineStyle(ROOT.kDotted)
        graph_vertical_lines[-1].SetLineWidth(2)
        graph_vertical_lines[-1].SetLineColor(ROOT.kGray+1)
        graph_vertical_lines[-1].Draw("SAME")
        if icent == 0:
            legend.AddEntry(graph_dummy[-1], "d#it{N}_{c#bar{c}}/dy from xsec", "F")
            legend.Draw()
        print(f"Completed scan for centrality {cent_mean} with V values {Vcent} and gammaC values {gammaC_vals}")

    graph_dndy_cent.Write()
    graph_gammas_cent.Write()
    graph_volume_cent.Write()  
    graph_optimised_gammaC_cent.Write() 
    canv.Write()
    canv.SaveAs(f"{outdir}/{outlabel}_scan_results.pdf")
    root_file.Close()

    return dnccbardy_values

# -------------------------------------------------
# Set object style
# -------------------------------------------------
def set_object_style(obj, color):
    obj.SetLineColor(color)
    obj.SetMarkerColor(color)
    obj.SetLineWidth(2)
    obj.SetMarkerStyle(20)
    obj.SetMarkerSize(1.2)

# -------------------------------------------------
# Run thermal_point for a scan over gammaC and V values
# -------------------------------------------------
def run_thermal_optimised(executable, params, gammaC_values, gammaS_values, Vs, cents, dndy, outdir, outlabel):
    ds_dp = {}
    outdir_optimised = f"{outdir}/optimised_gammaC"
    os.makedirs(outdir_optimised, exist_ok=True)
    outfile_optimised = f"{outdir_optimised}/{outlabel}_optimised_results.root"
    outfile = ROOT.TFile(outfile_optimised, "RECREATE")
    print(f"Saving optimised results to {outfile_optimised}...")
    graph_ds_dp_cent = ROOT.TGraphAsymmErrors()
    graph_ds_cent = ROOT.TGraphAsymmErrors()
    graph_dp_cent = ROOT.TGraphAsymmErrors()
    graph_ds_dp_cent.SetName("graph_ds_dp_cent")
    graph_ds_dp_cent.GetXaxis().SetTitle("centrality")
    graph_ds_dp_cent.GetYaxis().SetTitle("Ds+/D+")
    graph_ds_cent.SetName("graph_ds_cent")
    graph_ds_cent.GetXaxis().SetTitle("centrality")
    graph_ds_cent.GetYaxis().SetTitle("Ds+")
    graph_dp_cent.SetName("graph_dp_cent")
    graph_dp_cent.GetXaxis().SetTitle("centrality")
    graph_dp_cent.GetYaxis().SetTitle("D+")

    canvas = ROOT.TCanvas("canv_optimised", "canv_optimised", 1200, 600)
    canvas.Divide(2,1)
    legend = ROOT.TLegend(0.5, 0.7, 0.8, 0.8)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)


    for icent, (Vcent, cent, gammaC_vals, gammaS_vals) in enumerate(zip(Vs, cents, gammaC_values, gammaS_values)):
        print(f"\n\nStarting scan for centrality {cent} with V values {Vcent} and gammaC values {gammaC_vals}")
        cent_mean = (cent[0] + cent[1]) / 2
        delta_cent = (cent[1] - cent[0]) / 2
        ds_dp[cent_mean] = {}
        ds_dp[cent_mean]['cent_min'] = cent[0]
        ds_dp[cent_mean]['cent_max'] = cent[1]
        outdir_cent = f"{outdir}/cent_{cent[0]}_{cent[1]}"
        os.makedirs(outdir_cent, exist_ok=True)
        params["outdir"] = outdir_cent

        dplus_yield = []
        dsplus_yield = []
        ds_dp_cent_values = []
        for iV, (V, gammaC, gammaS) in enumerate(zip(Vcent, gammaC_vals, gammaS_vals)): # Loop over V and gammaS (cent, min, max value) which depends centrality (dnch/deta)
            params["V"] = V
            params["gammaC"] = gammaC
            params["gammaS"] = gammaS

            # adjust outlabel for debbugging
            params["outlabel"] = f"{outlabel}_cent_{cent[0]}_{cent[1]}_gammaC_{gammaC:.2f}_V_{V:.0f}"
            cmd = [
                executable,
                str(params["particle_list"]),
                str(params["decays_list"]),
                str(params["model_type"]),
                str(params["T"]),
                str(params["V"]),
                str(params["muB"]),
                str(params["muQ"]),
                str(params["muS"]),
                str(params["muC"]),
                str(params["gammaQ"]),
                str(params["gammaS"]),
                str(params["gammaC"]),
                str(params["width_mode"]),
                str(params["feeddown"] if "feeddown" in params else 1),
                str(params["statistics"] if "statistics" in params else 1),
                str(params["outdir"]),
                str(params["outlabel"]),
                str(params["debug"])
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            for line in result.stdout.strip().split("\n"):
                print(line)
                if line.startswith("PDG: 411"):
                    dplus_yield.append(float(line.split("yield = ")[1].split(" ")[0]))
                if line.startswith("PDG: 431"):
                    dsplus_yield.append(float(line.split("yield = ")[1].split(" ")[0]))
        #input(f"Centrality {cent_mean}: D+ yield = {dplus_yield[-1]:.3f}, Ds+ yield = {dsplus_yield[-1]:.3f}")
                
                # checking resonance feeddown contribution to Ds+ yield
                #if line.startswith("PDG: 100423"):
                #    print(f"Resonance feeddown contribution to Ds+ yield from D(23S1)0 2643 is {line.split('yield = ')[1].split(' ')[0]}")
                #    dsplus_yield[0] += float(line.split("yield = ")[1].split(" ")[0])
                #    print(f"Updated Ds+ yield including feeddown from D(23S1)0 2643 is {dsplus_yield[0]}")
                #if line.startswith("PDG: 100413"):
                #    dsplus_yield[0] += float(line.split("yield = ")[1].split(" ")[0])
                #    print(f"Updated Ds+ yield including feeddown from D(23S1)+ 2643 is {dsplus_yield[0]}")
                #    dsplus_yield[0] += float(line.split("yield = ")[1].split(" ")[0])
                #    print(f"Updated Ds+ yield including feeddown from D(23S1)+ 2643 is {dsplus_yield[0]}")

        # store lines in a text file for debugging
        with open(f"{outdir_cent}/results.txt", "w") as f:
            f.write(result.stdout)

        if dplus_yield[0] == 0:
            print(f"WARNING: D+ yield is zero for centrality {cent_mean}, cannot compute Ds+/D+ ratio")
            ds_dp[cent_mean]['ds_dplus_ratio'] = 0
            ds_dp[cent_mean]['ds_dplus_uncertainty_low'] = 0
            ds_dp[cent_mean]['ds_dplus_uncertainty_high'] = 0
            continue

        ds_dplus_ratio = dsplus_yield[0] / dplus_yield[0] # Use Vcent for central value
        ds_dplus_min = dsplus_yield[1] / dplus_yield[1] # Use Vmax for minimum value
        ds_dplus_max = dsplus_yield[2] / dplus_yield[2] # Use Vmin for maximum value
        ds_dplus_uncertainty_low = ds_dplus_ratio - ds_dplus_min
        ds_dplus_uncertainty_high = ds_dplus_max - ds_dplus_ratio
        print(f"Centrality {cent_mean}: Ds+/D+ = {ds_dplus_ratio:.3f} with uncertainties [{ds_dplus_uncertainty_low:.3f}, {ds_dplus_uncertainty_high:.3f}]")
        print(f"Centrality {cent_mean}: Ds+/D+(min) = {ds_dplus_min:.3f}, Ds+/D+(max) = {ds_dplus_max:.3f}")
        print(f"Centrality {cent_mean}: D+ yield = {dplus_yield[0]:.3f} with uncertainties [{dplus_yield[1]:.3f}, {dplus_yield[2]:.3f}]")
        print(f"Centrality {cent_mean}: Ds+ yield = {dsplus_yield[0]:.3f} with uncertainties [{dsplus_yield[1]:.3f}, {dsplus_yield[2]:.3f}]")
        #input()
        
        graph_ds_dp_cent.SetPoint(icent, cent_mean, ds_dplus_ratio)
        graph_ds_dp_cent.SetPointError(icent, delta_cent, delta_cent, ds_dplus_uncertainty_low, ds_dplus_uncertainty_high)
        graph_ds_cent.SetPoint(icent, cent_mean, dsplus_yield[0])
        graph_ds_cent.SetPointError(icent, delta_cent, delta_cent, np.abs(dsplus_yield[1] - dsplus_yield[0])/2, np.abs(dsplus_yield[1] - dsplus_yield[0])/2) # Use Vmin - Vcent and Vmax - Vcent
        graph_dp_cent.SetPoint(icent, cent_mean, dplus_yield[0])
        graph_dp_cent.SetPointError(icent, delta_cent, delta_cent, np.abs(dplus_yield[1] - dplus_yield[0])/2, np.abs(dplus_yield[1] - dplus_yield[0])/2) # Use Vmin - Vcent and Vmax - Vcent

    set_object_style(graph_ds_dp_cent, ROOT.kBlack)
    set_object_style(graph_ds_cent, ROOT.kRed+1)
    set_object_style(graph_dp_cent, ROOT.kAzure+4)

    canvas.cd(1).SetLogy()
    graph_dp_cent.GetYaxis().SetTitleOffset(1.2)
    graph_dp_cent.GetYaxis().SetRangeUser(0.001, 100)   
    graph_dp_cent.GetYaxis().SetLabelSize(0.04)
    graph_dp_cent.GetYaxis().SetTitleSize(0.04)
    graph_dp_cent.GetYaxis().SetDecimals()
    graph_dp_cent.GetYaxis().SetTitle("Yield")
    graph_dp_cent.GetXaxis().SetTitle("centrality (%)")
    graph_dp_cent.Draw("APEZ ")
    graph_ds_cent.Draw("PEZ SAME")
    legend.AddEntry(graph_ds_cent, "D_{s}^{+}", "P")
    legend.AddEntry(graph_dp_cent, "D^{+}", "P")
    legend.Draw()
    
    canvas.cd(2)
    graph_ds_dp_cent.GetYaxis().SetTitleOffset(1.2)
    graph_ds_dp_cent.GetYaxis().SetRangeUser(0.42, 0.84) # Set a fixed range for the ratio plot
    graph_ds_dp_cent.GetYaxis().SetLabelSize(0.04)
    graph_ds_dp_cent.GetYaxis().SetTitleSize(0.04)
    graph_ds_dp_cent.GetYaxis().SetDecimals()
    graph_ds_dp_cent.GetYaxis().SetMaxDigits(2)
    graph_ds_dp_cent.GetXaxis().SetTitle("centrality (%)")
    graph_ds_dp_cent.GetYaxis().SetTitle("#it{#sigma}(D_{s}^{+})/#it{#sigma}(D^{+})")
    graph_ds_dp_cent.Draw("APZ")
    canvas.Update()
    canvas.SaveAs(f"{outdir}/{outlabel}_optimised_results.pdf")

    graph_ds_dp_cent.Write()
    graph_ds_cent.Write()
    graph_dp_cent.Write()
    outfile.Close()

    return ds_dp

# -------------------------------------------------
# Get volume from dnch/deta
# -------------------------------------------------
def get_volume_from_dnchdeta(dnch_deta):
    # Taken from https://arxiv.org/pdf/2011.14328
    return 3 * 2.4 * dnch_deta

# -------------------------------------------------
# Get gammaS from dnch/deta
# -------------------------------------------------
def get_gammaS_from_dnchdeta(dnch_deta):
    # Taken from https://arxiv.org/pdf/1906.03145
    return 1 - 0.25 * np.exp(-dnch_deta / 59)

# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file with parameters"
    )
    args = parser.parse_args()

    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)

    repo_path = config.get("thermal_fist_path", ".")
    build_dir = config.get("build_dir", "build")
    xsec_list = config.get("xsec_list", None)
    scan_params = config.get("scan_params", None)

    # Build and get executable
    exe = build_thermal_fist(repo_path, build_dir)

    # Run single point
    if xsec_list is None:
        print("No xsec_list provided, running single thermal point")
        run_thermal_point(exe, config)
    else:
        print(f"xsec_list provided, running thermal points for each xsec in {xsec_list}")
        cents, dndy, dnchdetas, Vs, gammaS_values = [], [], [], [], [] # Store centrality, xsec, dnch/deta, and V for each point (cent, min, max)
        with open(xsec_list) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split()
                cents.append([float(parts[0]), float(parts[1])])
                dndy.append([float(parts[11]), float(parts[11]) - float(parts[12]), float(parts[11]) + float(parts[13])])
                dnchdetas.append([float(parts[2]), float(parts[2]) - float(parts[3]), float(parts[2]) + float(parts[3])])
                Vs.append([get_volume_from_dnchdeta(dnchdetas[-1][0]), get_volume_from_dnchdeta(dnchdetas[-1][1]), get_volume_from_dnchdeta(dnchdetas[-1][2])])
                gammaS_values.append([get_gammaS_from_dnchdeta(dnchdetas[-1][0]), get_gammaS_from_dnchdeta(dnchdetas[-1][1]), get_gammaS_from_dnchdeta(dnchdetas[-1][2])])
                print(f"Extracted dndy: {dndy[-1][0]} with uncertainties {dndy[-1][1:]} for centrality {cents[-1]} with V = {Vs[-1]}")

        outdir = config["outdir"]
        outlabel = config["outlabel"]
        os.makedirs(outdir, exist_ok=True)
        outfile = f"{outdir}/{outlabel}_scan_results.root"

        if scan_params['perform_scan']:
            gammaC_values = []
            
            for icent, (minvals, maxvals, step) in enumerate(zip(scan_params['mins'], scan_params['maxs'], scan_params['npoints'])):
                gammaC_values.append([])
                for i in range(step):
                    gc = minvals + i * (maxvals - minvals) / (step - 1)
                    if gc > maxvals:
                        break
                    gammaC_values[-1].append(gc)
                print(f"Generated gammaC values for centrality {cents[icent]}: {gammaC_values[-1]}")

            run_thermal_scan(exe, config, gammaC_values, gammaS_values, Vs, cents, dndy, outdir, outlabel, outfile)
        else:
            print("Scan not requested, running single thermal point with list of optimised gammaC values for each centrality")
            #optimised_file = ROOT.TFile(f"{outdir}/{outlabel}_scan_results.root", "READ")
            optimised_file = ROOT.TFile(f"/home/spolitan/alice/Thermal-FIST/tools/gammac_scan_charm_canonical_withstrange_thermal_points_std/fist_scan_scan_results.root", "READ")
            graph_optimised_gammaC_cent = optimised_file.Get("graph_optimised_gammaC_cent")
            optimised_gammaC_values = []
            for icent in range(graph_optimised_gammaC_cent.GetN()):
                cent_mean = graph_optimised_gammaC_cent.GetX()[icent]
                gammaC_opt = graph_optimised_gammaC_cent.GetY()[icent]
                gammaC_opt_err_low = graph_optimised_gammaC_cent.GetEYlow()[icent]
                gammaC_opt_err_high = graph_optimised_gammaC_cent.GetEYhigh()[icent]
                print(f"Optimised gammaC for centrality {cent_mean} is {gammaC_opt:.2f} with uncertainty [{gammaC_opt - gammaC_opt_err_low:.2f}, {gammaC_opt + gammaC_opt_err_high:.2f}]")
                optimised_gammaC_values.append((gammaC_opt, gammaC_opt - gammaC_opt_err_low, gammaC_opt + gammaC_opt_err_high))
            run_thermal_optimised(exe, config, optimised_gammaC_values, gammaS_values, Vs, cents, dndy, outdir, outlabel)

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    main()