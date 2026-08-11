import matplotlib as mpl 
import seaborn as sns
import numpy as np
from array import array
import ROOT
def set_matplotlib_palette(paletteName):
    n_colors = 255
    cmap = mpl.colormaps[paletteName]
    colors = cmap(np.linspace(0, 1, n_colors))
    stopsList = list(np.linspace(0, 1, n_colors-1))+[1]
    stops = array('d',stopsList)
    red = array('d', colors[:, 0])
    green = array('d', colors[:, 1])
    blue = array('d', colors[:, 2])
    ROOT.TColor.CreateGradientColorTable(n_colors, stops, red, green, blue, 255)
    ROOT.gStyle.SetNumberContours(255)

def get_discrete_matplotlib_palette(paletteName, n_colors=10):
    try:
        cmap = mpl.colormaps[paletteName]
        colors = cmap.colors
    except:
        colors = sns.color_palette(paletteName, n_colors=n_colors)
    ROOTColorIndices = []
    ROOTColors = []
    for color in colors:
        idx = ROOT.TColor.GetFreeColorIndex()
        ROOTColors.append(ROOT.TColor(idx, color[0], color[1], color[2],"color%i" % idx))
        ROOTColorIndices.append(idx)
        
    return ROOTColorIndices, ROOTColors

def create_upper_lower_limit(graph):
    npoints = graph.GetN()
    graph_low = ROOT.TGraph(npoints)
    graph_high = ROOT.TGraph(npoints)
    graph_low.SetLineColor(graph.GetLineColor())
    graph_high.SetLineColor(graph.GetLineColor())
    graph_low.SetLineWidth(3)
    graph_high.SetLineWidth(3)
    for ipt in range(npoints):
        graph_low.SetPoint(ipt, graph.GetPointX(ipt), graph.GetPointY(ipt)-graph.GetErrorYlow(ipt))
        graph_high.SetPoint(ipt, graph.GetPointX(ipt), graph.GetPointY(ipt)+graph.GetErrorYhigh(ipt))
    return graph_low, graph_high

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPadRightMargin(0.03)
ROOT.gStyle.SetPadLeftMargin(0.15)
ROOT.gStyle.SetPadTopMargin(0.05)
ROOT.gStyle.SetPadBottomMargin(0.14)
ROOT.gStyle.SetOptLogx(1)
ROOT.gStyle.SetLabelSize(0.045, "XYZ")
ROOT.gStyle.SetTitleSize(0.045, "XYZ")
ROOT.gStyle.SetTitleOffset(1.2, "X")
mult_unc_low = [0.05, 0.07, np.sqrt(0.11**2 + 0.09**2)/2, np.sqrt((0.21/4)**2 + (0.15/4)**2 + (0.13/2)**2), np.sqrt(0.21**2 + 0.18**2)/2, 0.36]
mult_unc_high = [0.07, 0.10, np.sqrt(0.16**2 + 0.13**2)/2, np.sqrt((0.18/4)**2 + (0.19/4)**2 + (0.19/2)**2), np.sqrt(0.27**2 + 0.24**2)/2, 0.42]

color_alice = ROOT.kBlack #kGray+3
color_lf = ROOT.kRed-7

colors, cols = get_discrete_matplotlib_palette('tab20')
color_pythia_pp = colors[2]
color_pythia_pbpb = colors[3]
color_epos_pp = colors[6]
color_epos_pbpb = colors[6]
color_shm_pp = ROOT.kMagenta+3
color_shm_pbpb = ROOT.kAzure+3
color_thermalfist_pbpb = ROOT.kBlue+3
color_thermalfist_pbpb_reso = ROOT.kCyan+3

infile_pp = ROOT.TFile.Open("ds_over_dp_ratio_ptint_pp.root")
graph_pp_stat = infile_pp.Get("gstat_ds_over_dp_ptint")
graph_pp_syst = infile_pp.Get("gsyst_tot_nobr_ds_over_dp_ptint")
graph_pp_stat.SetLineWidth(2)
graph_pp_syst.SetLineWidth(2)
graph_pp_stat.SetLineColor(color_alice)
graph_pp_syst.SetLineColor(color_alice)
graph_pp_stat.SetMarkerColor(color_alice)
graph_pp_stat.SetMarkerStyle(56)
graph_pp_stat.SetMarkerSize(1.2)
graph_pp_syst.SetFillStyle(0)
graph_pp_stat_border = graph_pp_stat.Clone()
graph_pp_stat_border.SetMarkerStyle(56)
graph_pp_stat_border.SetMarkerColor(ROOT.kBlack)
graph_pp_stat_border.SetLineColor(ROOT.kBlack)
graph_doubleratio_pp_stat = graph_pp_stat.Clone("graph_doubleratio_pp_stat")
graph_doubleratio_pp_syst = graph_pp_syst.Clone("graph_doubleratio_pp_syst")
graph_doubleratio_pp_stat_border = graph_pp_stat_border.Clone("graph_doubleratio_pp_stat_border")
nmult = graph_pp_stat.GetN()
den = graph_pp_stat.GetPointY(nmult-1)
unc_stat_den = graph_pp_stat_border.GetErrorYlow(nmult-1)
unc_syst_low_den = graph_pp_syst.GetErrorYlow(nmult-1)
unc_syst_high_den = graph_pp_syst.GetErrorYhigh(nmult-1)
for imult in range(nmult):
    num = graph_pp_stat.GetPointY(imult)
    unc_stat_num = graph_pp_stat_border.GetErrorYlow(imult)
    unc_syst_low_num = graph_pp_syst.GetErrorYlow(imult)
    unc_syst_high_num = graph_pp_syst.GetErrorYhigh(imult)
    ratio = num / den if imult < nmult-1 else -100000.
    unc_stat = np.sqrt(unc_stat_num**2/num**2 + unc_stat_den**2/den**2) * ratio if imult < nmult-1 else 0.
    unc_syst_low = np.sqrt(unc_syst_low_num**2/num**2 + unc_syst_low_den**2/den**2) * ratio if imult < nmult-1 else 0.
    unc_syst_high = np.sqrt(unc_syst_high_num**2/num**2 + unc_syst_high_den**2/den**2) * ratio if imult < nmult-1 else 0.
    graph_doubleratio_pp_stat.SetPoint(imult, graph_pp_stat.GetPointX(imult), ratio)
    graph_doubleratio_pp_syst.SetPoint(imult, graph_pp_stat.GetPointX(imult), ratio)
    graph_doubleratio_pp_stat_border.SetPoint(imult, graph_pp_stat.GetPointX(imult), ratio)
    graph_doubleratio_pp_stat.SetPointError(imult, 0., 0., unc_stat, unc_stat)
    graph_doubleratio_pp_syst.SetPointError(imult, mult_unc_low[nmult-imult-1]*5, mult_unc_high[nmult-imult-1]*5, unc_syst_low, unc_syst_high)
    graph_doubleratio_pp_stat_border.SetPointError(imult, 0., 0., unc_stat, unc_stat)
    graph_pp_syst.SetPointError(imult, mult_unc_low[nmult-imult-1]*5, mult_unc_high[nmult-imult-1]*5,
                                graph_pp_syst.GetErrorYlow(imult),
                                graph_pp_syst.GetErrorYhigh(imult))
    graph_pp_stat.SetPointError(imult, 0., 0.,
                                graph_pp_stat.GetErrorYlow(imult),
                                graph_pp_stat.GetErrorYhigh(imult))
graph_doubleratio_pp_stat.RemovePoint(nmult-1)
graph_doubleratio_pp_stat_border.RemovePoint(nmult-1)
graph_doubleratio_pp_syst.RemovePoint(nmult-1)

infile_pbpb = ROOT.TFile.Open("ds_over_dp_ratio_ptint_pbpb.root")
graph_pbpb_stat = infile_pbpb.Get("gstat_ds_over_dp_ptint")
graph_pbpb_syst = infile_pbpb.Get("gsyst_tot_nobr_ds_over_dp_ptint")
graph_pbpb_stat_border = infile_pbpb.Get("gstat_ds_over_dp_ptint")
graph_pbpb_stat.SetLineWidth(2)
graph_pbpb_stat.SetLineColor(color_alice)
graph_pbpb_stat.SetMarkerColor(color_alice)
graph_pbpb_syst.SetLineWidth(2)
graph_pbpb_syst.SetLineColor(color_alice)
graph_pbpb_syst.SetFillStyle(0)
graph_pbpb_stat.SetMarkerStyle(ROOT.kFullDoubleDiamond)
graph_pbpb_stat.SetMarkerSize(1.)
graph_pbpb_stat_border.SetMarkerStyle(ROOT.kOpenDoubleDiamond)
graph_pbpb_stat_border.SetMarkerColor(ROOT.kBlack)
graph_pbpb_stat_border.SetLineColor(ROOT.kBlack)
graph_pbpb_vscent_stat = graph_pbpb_stat.Clone("graph_pbpb_vscent_stat")
graph_pbpb_vscent_syst = graph_pbpb_syst.Clone("graph_pbpb_vscent_syst")
graph_doubleratio_pbpb_stat = graph_pbpb_stat.Clone("graph_doubleratio_pbpb_stat")
graph_doubleratio_pbpb_syst = graph_pbpb_syst.Clone("graph_doubleratio_pbpb_syst")
graph_doubleratio_pbpb_stat_border = graph_pbpb_stat_border.Clone("graph_doubleratio_pbpb_stat_border")
nmult = graph_pbpb_stat.GetN()
for imult in range(nmult):
    num = graph_pbpb_stat.GetPointY(imult)
    unc_stat_num = graph_pbpb_stat_border.GetErrorYlow(imult)
    unc_syst_low_num = graph_pbpb_syst.GetErrorYlow(imult)
    unc_syst_high_num = graph_pbpb_syst.GetErrorYhigh(imult)
    ratio = num / den
    unc_stat = np.sqrt(unc_stat_num**2/num**2 + unc_stat_den**2/den**2) * ratio
    unc_syst_low = np.sqrt(unc_syst_low_num**2/num**2 + unc_syst_low_den**2/den**2) * ratio
    unc_syst_high = np.sqrt(unc_syst_high_num**2/num**2 + unc_syst_high_den**2/den**2) * ratio
    graph_doubleratio_pbpb_stat.SetPoint(imult, graph_pbpb_stat.GetPointX(imult), ratio)
    graph_doubleratio_pbpb_syst.SetPoint(imult, graph_pbpb_stat.GetPointX(imult), ratio)
    graph_doubleratio_pbpb_stat_border.SetPoint(imult, graph_pbpb_stat.GetPointX(imult), ratio)
    graph_doubleratio_pbpb_stat.SetPointError(imult, graph_pbpb_stat.GetErrorXlow(imult), graph_pbpb_stat.GetErrorXhigh(imult), unc_stat, unc_stat)
    graph_doubleratio_pbpb_syst.SetPointError(imult, graph_pbpb_syst.GetErrorXlow(imult), graph_pbpb_syst.GetErrorXhigh(imult), unc_syst_low, unc_syst_high)
    graph_doubleratio_pbpb_stat_border.SetPointError(imult, graph_pbpb_stat.GetErrorXlow(imult), graph_pbpb_stat.GetErrorXhigh(imult), unc_stat, unc_stat)
    graph_pbpb_vscent_stat.SetPoint(imult, 5 + imult*10, num)
    graph_pbpb_vscent_syst.SetPoint(imult, 5 + imult*10, num)
    graph_pbpb_vscent_stat.SetPointError(imult, 5, 5, unc_stat_num, unc_stat_num)
    graph_pbpb_vscent_syst.SetPointError(imult, 5, 5, unc_syst_low_num, unc_syst_high_num)

infile_oo = ROOT.TFile.Open("ds_over_dp_ratio_ptint_oo.root")
graph_oo_stat = infile_oo.Get("gstat_ds_over_dp_ptint")
graph_oo_syst = infile_oo.Get("gsyst_tot_nobr_ds_over_dp_ptint")
graph_oo_stat_border = infile_oo.Get("gstat_ds_over_dp_ptint")
graph_oo_stat.SetLineWidth(2)
graph_oo_stat.SetLineColor(color_alice)
graph_oo_stat.SetMarkerColor(color_alice)
graph_oo_syst.SetLineWidth(2)
graph_oo_syst.SetLineColor(color_alice)
graph_oo_syst.SetFillStyle(0)
graph_oo_stat.SetMarkerStyle(ROOT.kFullCircle)
graph_oo_stat.SetMarkerSize(1.)
graph_oo_stat_border.SetMarkerStyle(ROOT.kOpenCircle)
graph_oo_stat_border.SetMarkerColor(ROOT.kBlack)
graph_oo_stat_border.SetLineColor(ROOT.kBlack)
graph_oo_vscent_stat = graph_oo_stat.Clone("graph_oo_vscent_stat")
graph_oo_vscent_syst = graph_oo_syst.Clone("graph_oo_vscent_syst")
graph_doubleratio_oo_stat = graph_oo_stat.Clone("graph_doubleratio_oo_stat")
graph_doubleratio_oo_syst = graph_oo_syst.Clone("graph_doubleratio_oo_syst")
graph_doubleratio_oo_stat_border = graph_oo_stat_border.Clone("graph_doubleratio_oo_stat_border")
nmult = graph_oo_stat.GetN()
for imult in range(nmult):
    num = graph_oo_stat.GetPointY(imult)
    unc_stat_num = graph_oo_stat_border.GetErrorYlow(imult)
    unc_syst_low_num = graph_oo_syst.GetErrorYlow(imult)
    unc_syst_high_num = graph_oo_syst.GetErrorYhigh(imult)
    ratio = num / den
    unc_stat = np.sqrt(unc_stat_num**2/num**2 + unc_stat_den**2/den**2) * ratio
    unc_syst_low = np.sqrt(unc_syst_low_num**2/num**2 + unc_syst_low_den**2/den**2) * ratio
    unc_syst_high = np.sqrt(unc_syst_high_num**2/num**2 + unc_syst_high_den**2/den**2) * ratio
    graph_oo_syst.SetPointError(imult, graph_oo_syst.GetErrorXlow(imult)*5, graph_oo_syst.GetErrorXhigh(imult)*5, unc_syst_low_num, unc_syst_high_num)
    graph_doubleratio_oo_stat.SetPoint(imult, graph_oo_stat.GetPointX(imult), ratio)
    graph_doubleratio_oo_syst.SetPoint(imult, graph_oo_stat.GetPointX(imult), ratio)
    graph_doubleratio_oo_stat_border.SetPoint(imult, graph_oo_stat.GetPointX(imult), ratio)
    graph_doubleratio_oo_stat.SetPointError(imult, graph_oo_stat.GetErrorXlow(imult), graph_oo_stat.GetErrorXhigh(imult), unc_stat, unc_stat)
    graph_doubleratio_oo_syst.SetPointError(imult, graph_oo_syst.GetErrorXlow(imult), graph_oo_syst.GetErrorXhigh(imult), unc_syst_low, unc_syst_high)
    graph_doubleratio_oo_stat_border.SetPointError(imult, graph_oo_stat.GetErrorXlow(imult), graph_oo_stat.GetErrorXhigh(imult), unc_stat, unc_stat)
    graph_oo_vscent_stat.SetPoint(imult, 5 + imult*10, num)
    graph_oo_vscent_syst.SetPoint(imult, 5 + imult*10, num)
    graph_oo_vscent_stat.SetPointError(imult, 5, 5, unc_stat_num, unc_stat_num)
    graph_oo_vscent_syst.SetPointError(imult, 5, 5, unc_syst_low_num, unc_syst_high_num)

infile_pythia_pp = ROOT.TFile.Open("PYTHIA8_Ds_over_Dplus_pp13dot6TeV_vsMult_ptInt.root")
graph_pythia_pp = infile_pythia_pp.Get("graph_ds_over_dp_p_ft0m_pt0.0_100.0_Mode2ModDstar")
graph_pythia_pp.SetLineWidth(2)
graph_pythia_pp.SetMarkerSize(0)
graph_pythia_pp.SetLineColorAlpha(color_pythia_pp, 0.7) #ROOT.kGreen+2, 0.3)
graph_pythia_pp.SetFillColorAlpha(color_pythia_pp, 0.7) #ROOT.kGreen+2, 0.3)

infile_pythia_pbpb = ROOT.TFile.Open("PYTHIA8_Ds_over_Dplus_PbPb5dot36_vsMult_ptint.root")
graph_pythia_pbpb = infile_pythia_pbpb.Get("graph_ds_over_dp_p_ft0m_pt0.0_100.0_AngantyrModDstar")
graph_pythia_pbpb.SetLineWidth(2)
graph_pythia_pbpb.SetMarkerSize(0)
graph_pythia_pbpb.SetLineColorAlpha(color_pythia_pbpb, 0.7) #ROOT.kGreen+2, 0.3)
graph_pythia_pbpb.SetFillColorAlpha(color_pythia_pbpb, 0.7) #ROOT.kGreen+2, 0.3)

graph_epos_pp = []
infile_epos_pp = ROOT.TFile.Open("EPOS4HQ_Ds_over_Dplus_pp13dot6TeV_vsMult_ptint.root")
graph_epos_pp = infile_epos_pp.Get("graph_ds_over_dp_p_ft0m_pt0.0_100.0_Frag+coal")
graph_epos_pp.SetLineWidth(2)
graph_epos_pp.SetMarkerSize(0)
graph_epos_pp.SetLineColorAlpha(color_epos_pp, 0.5) #ROOT.kBlack, 0.3)
graph_epos_pp.SetFillColorAlpha(color_epos_pp, 0.5) #ROOT.kBlack, 0.3)

#infile_shm_pp = ROOT.TFile.Open("./TAMU_pp_13TeV_vsmult_DsOverDp.root")
#graph_shm_pp = infile_shm_pp.Get("graph_ds_over_dp_pdg_T170_pt1.0_2.0")
#graph_shm_pp.SetLineWidth(5)
#graph_shm_pp.SetMarkerSize(0)
#graph_shm_pp.SetLineColorAlpha(color_shm_pp, 0.5) #ROOT.kBlack, 0.3)
#graph_shm_pp.SetFillColorAlpha(color_shm_pp, 0.5) #ROOT.kBlack, 0.3)

infile_epos_pbpb = ROOT.TFile.Open("EPOS4HQ_Ds_over_Dplus_PbPb5dot02TeV_vsMult_ptint.root")
graph_epos_pbpb = infile_epos_pbpb.Get("graph_ds_over_dp_p_ft0m_pt0.0_100.0_Frag+coal")
graph_epos_pbpb.SetLineWidth(2)
graph_epos_pbpb.SetMarkerSize(0)
graph_epos_pbpb.SetLineColorAlpha(color_epos_pbpb, 0.5) #ROOT.kBlack, 0.3)
graph_epos_pbpb.SetFillColorAlpha(color_epos_pbpb, 0.5) #ROOT.kBlack, 0.3)

infile_epos_oo = ROOT.TFile.Open("EPOS4HQ_Ds_over_Dplus_OO5dot02TeV_vsMult_ptint.root")
graph_epos_oo = infile_epos_oo.Get("graph_ds_over_dp_p_ft0m_pt0.0_100.0_Frag+coal")
graph_epos_oo.SetLineWidth(2)
graph_epos_oo.SetMarkerSize(0)
graph_epos_oo.SetLineColorAlpha(color_epos_pbpb, 0.5) #ROOT.kBlack, 0.3)
graph_epos_oo.SetFillColorAlpha(color_epos_pbpb, 0.5) #ROOT.kBlack, 0.3)

# npart -> nch conversion for GSI-Heidelberg SHMc
dnch_deta = [1858, 1253, 848, 559, 351, 205, 110, 53, 23.2]
unc_dnch_deta = [48, 33, 25, 19, 14, 11, 8, 5, 2.8]
npart = [358.0, 263.1, 188.4, 130.6, 86.5, 53.7, 30.5, 15.4, 6.8]
unc_npart = [1.3, 1.3, 1.3, 1.4, 1.5, 1.1, 0.8, 0.4, 0.2]
graph_nch_vs_npart = ROOT.TGraphAsymmErrors(len(npart))
for ipt, _ in enumerate(npart):
    graph_nch_vs_npart.SetPoint(ipt, npart[ipt], dnch_deta[ipt])
    graph_nch_vs_npart.SetPointError(ipt, unc_npart[ipt], unc_npart[ipt], unc_dnch_deta[ipt], unc_dnch_deta[ipt])

infile_shm_pbpb = ROOT.TFile.Open("Ds2Dp_GSI_SHMc.root")
graph_cor1 = infile_shm_pbpb.Get("Ds2Dp_cor1")
graph_cor2 = infile_shm_pbpb.Get("Ds2Dp_cor2")

graph_shm_pbpb = ROOT.TGraphAsymmErrors(1)

ipt = 0
for ix in range(graph_cor2.GetN()):
    ratio = (graph_cor2.GetPointY(ix) + graph_cor1.GetPointY(ix)) / 2
    ratio_unc = abs(graph_cor2.GetPointY(ix) - graph_cor1.GetPointY(ix)) / 2
    npart = graph_cor1.GetPointX(ix)
    if npart < 40:
        continue
    graph_shm_pbpb.SetPoint(ipt, graph_nch_vs_npart.Eval(npart), ratio)
    graph_shm_pbpb.SetPointError(ipt, 0.1, 0.1, ratio_unc, ratio_unc)
    ipt += 1

graph_shm_pbpb.SetLineWidth(3)
graph_shm_pbpb.SetMarkerSize(0)
graph_shm_pbpb.SetLineColorAlpha(color_shm_pbpb, 0.5) #ROOT.kBlack, 0.3)
graph_shm_pbpb.SetFillColorAlpha(color_shm_pbpb, 0.5) #ROOT.kBlack, 0.3)

infile_thermalfist_pbpb = ROOT.TFile.Open("Ds2Dp_ThermalFIST_SHMc.root")
graph_thermalfist_pbpb_vscent = infile_thermalfist_pbpb.Get("graph_ds_dp_cent")
graph_thermalfist_pbpb = ROOT.TGraphAsymmErrors(1)

infile_thermalfist_pbpb_reso = ROOT.TFile.Open("/home/spolitan/alice/Thermal-FIST/tools/gammac_scan_canonical_withstrange_thermal_points_charmreso_final/optimised_gammaC/fist_scan_optimised_results.root")
graph_thermalfist_pbpb_vscent_reso = infile_thermalfist_pbpb_reso.Get("graph_ds_dp_cent")
graph_thermalfist_pbpb_reso = ROOT.TGraphAsymmErrors(1)



for ix in range(graph_thermalfist_pbpb_vscent.GetN()):
    ratio = graph_thermalfist_pbpb_vscent.GetPointY(ix)
    ratio_unc = graph_thermalfist_pbpb_vscent.GetErrorYlow(ix)
    graph_thermalfist_pbpb.SetPoint(ix, dnch_deta[ix], ratio)
    graph_thermalfist_pbpb.SetPointError(ix, unc_dnch_deta[ix], unc_dnch_deta[ix], ratio_unc, ratio_unc)
graph_thermalfist_pbpb.SetLineWidth(3)
graph_thermalfist_pbpb.SetMarkerSize(0)
graph_thermalfist_pbpb.SetLineColorAlpha(color_thermalfist_pbpb, 0.5) #ROOT.kBlack, 0.3)
graph_thermalfist_pbpb.SetFillColorAlpha(color_thermalfist_pbpb, 0.5) #ROOT.kBlack, 0.3)

for ix in range(graph_thermalfist_pbpb_vscent_reso.GetN()):
    ratio = graph_thermalfist_pbpb_vscent_reso.GetPointY(ix)
    ratio_unc = graph_thermalfist_pbpb_vscent_reso.GetErrorYlow(ix)
    print(f"ix: {ix}, dnch_deta[ix]: {dnch_deta[ix]}, ratio: {ratio}, ratio_unc: {ratio_unc}")
    graph_thermalfist_pbpb_reso.SetPoint(ix, dnch_deta[ix], ratio)
    graph_thermalfist_pbpb_reso.SetPointError(ix, unc_dnch_deta[ix], unc_dnch_deta[ix], ratio_unc, ratio_unc)
graph_thermalfist_pbpb_reso.SetLineWidth(3)
graph_thermalfist_pbpb_reso.SetMarkerSize(0)
graph_thermalfist_pbpb_reso.SetLineColorAlpha(color_thermalfist_pbpb_reso, 0.5) #ROOT.kBlack, 0.3)
graph_thermalfist_pbpb_reso.SetFillColorAlpha(color_thermalfist_pbpb_reso, 0.5) #ROOT.kBlack, 0.3)



c = ROOT.TCanvas("canvas", "canvas", 500, 500)

leg_data = ROOT.TLegend(0.18, 0.7, 0.7, 0.85)
leg_data.SetTextSize(0.04)
leg_data.SetBorderSize(0)
leg_data.SetFillStyle(0)
leg_data.SetMargin(0.1)
leg_data.AddEntry(graph_pbpb_stat, "Pb#minusPb,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.36 TeV", "p")
leg_data.AddEntry(graph_oo_stat, "OO,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.36 TeV", "p")
leg_data.AddEntry(graph_pp_stat, "pp,#kern[0.3]{#sqrt{#it{s}}} = 13.6 TeV", "p")

leg_data_border = ROOT.TLegend(0.18, 0.7, 0.7, 0.85)
leg_data_border.SetTextSize(0.04)
leg_data_border.SetBorderSize(0)
leg_data_border.SetFillStyle(0)
leg_data_border.SetMargin(0.1)
leg_data_border.AddEntry(graph_pbpb_stat_border, "Pb#minusPb,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.36 TeV", "p")
leg_data_border.AddEntry(graph_oo_stat_border, "OO,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.36 TeV", "p")
leg_data_border.AddEntry(graph_pp_stat_border, "pp,#kern[0.3]{#sqrt{#it{s}}} = 13.6 TeV", "p")

leg_model = ROOT.TLegend(0.2, 0.25, 0.95, 0.4)
leg_model.SetTextSize(0.03)
leg_model.SetBorderSize(0)
leg_model.SetFillStyle(0)
leg_model.SetMargin(0.1)
leg_model.SetNColumns(2)
leg_model.AddEntry(graph_pythia_pp, "PYTHIA 8 CRMode2", "f")
#leg_model.AddEntry(graph_shm_pp, "CE-SHMc", "f")
leg_model.AddEntry(graph_pythia_pbpb, "PYTHIA 8 Angantyr", "f")
leg_model.AddEntry(graph_thermalfist_pbpb, "ThermalFIST SHMc", "f")
leg_model.AddEntry(graph_thermalfist_pbpb_reso, "ThermalFIST SHMc (with reso)", "f")
#odel.AddEntry(graph_epos_pp, "EPOS4HQ", "f")
#odel.AddEntry(graph_shm_pbpb, "GSI-Heidelberg SHMc", "f")

text_ALICE = ROOT.TLatex(0.2, 0.88, 'ALICE Preliminary')
text_ALICE.SetNDC()
text_ALICE.SetTextFont(42)
text_ALICE.SetTextSize(0.055)

text_y = ROOT.TLatex(0.8, 0.88, "|#it{y}|#kern[0.4]{<}#kern[0.2]{0.5}")
text_y.SetNDC()
text_y.SetTextFont(42)
text_y.SetTextSize(0.04)

text_pt = ROOT.TLatex(0.2, 0.65, "#it{p}_{T} > 0")
text_pt.SetNDC()
text_pt.SetTextFont(42)
text_pt.SetTextSize(0.04)

text_unc = ROOT.TLatex(0.2, 0.17, "pp and OO uncertainty on#kern[0.3]{#it{x}}-axis scaled by 5")
text_unc.SetNDC()
text_unc.SetTextFont(42)
text_unc.SetTextSize(0.03)

text_brunc = ROOT.TLatex()
text_brunc.SetNDC()
text_brunc.SetTextFont(42)
text_brunc.SetTextSize(0.03)

h_frame = c.cd().DrawFrame(
    1., 0.01, 5000., 0.95,
    ";#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}| < 0.5};#it{#sigma}(D_{s}^{#plus})/#it{#sigma}(D^{#plus})"
)
h_frame.GetYaxis().SetDecimals()

graph_pythia_pp.DrawClone("3")
graph_pythia_pp_low, graph_pythia_pp_high = create_upper_lower_limit(graph_pythia_pp)
graph_pythia_pp_low.DrawClone("l")
graph_pythia_pp_high.DrawClone("l")
graph_pythia_pbpb.DrawClone("3")
graph_pythia_pbpb_low, graph_pythia_pbpb_high = create_upper_lower_limit(graph_pythia_pbpb)
graph_pythia_pbpb_low.DrawClone("l")
graph_pythia_pbpb_high.DrawClone("l")
#graph_shm_pp.DrawClone("3")
#graph_shm_pp_low, graph_shm_pp_high = create_upper_lower_limit(graph_shm_pp)
#graph_shm_pp_low.DrawClone("l")
#graph_shm_pp_high.DrawClone("l")
#graph_shm_pbpb.DrawClone("3")
#graph_shm_pbpb_low, graph_shm_pbpb_high = create_upper_lower_limit(graph_shm_pbpb)
#graph_shm_pbpb_low.DrawClone("l")
#graph_shm_pbpb_high.DrawClone("l")
graph_thermalfist_pbpb.DrawClone("3")
graph_thermalfist_pbpb_low, graph_thermalfist_pbpb_high = create_upper_lower_limit(graph_thermalfist_pbpb)
graph_thermalfist_pbpb_low.Draw("l")
graph_thermalfist_pbpb_high.Draw("l")
graph_thermalfist_pbpb_reso.DrawClone("3")
graph_thermalfist_pbpb_reso_low, graph_thermalfist_pbpb_reso_high = create_upper_lower_limit(graph_thermalfist_pbpb_reso)
graph_thermalfist_pbpb_reso_low.Draw("l")
graph_thermalfist_pbpb_reso_high.Draw("l")
'''
graph_epos_pp.DrawClone("3")
graph_epos_pp_low, graph_epos_pp_high = create_upper_lower_limit(graph_epos_pp)
graph_epos_pp_low.Draw("l")
graph_epos_pp_high.Draw("l")
graph_epos_pbpb.DrawClone("3")
graph_epos_pbpb_low, graph_epos_pbpb_high = create_upper_lower_limit(graph_epos_pbpb)
graph_epos_pbpb_low.Draw("l")
graph_epos_pbpb_high.Draw("l")
graph_epos_oo.DrawClone("3")
graph_epos_oo_low, graph_epos_oo_high = create_upper_lower_limit(graph_epos_oo)
graph_epos_oo_low.Draw("l")
graph_epos_oo_high.Draw("l")
'''
graph_pp_syst.DrawClone("2")
graph_pp_stat.DrawClone("pz")
graph_pp_stat_border.DrawClone("pz")
graph_oo_syst.DrawClone("2")
graph_oo_stat.DrawClone("pz")
graph_oo_stat_border.DrawClone("pz")
graph_pbpb_syst.DrawClone("2")
graph_pbpb_stat.DrawClone("pz")
graph_pbpb_stat_border.DrawClone("pz")
text_ALICE.Draw()
text_y.Draw()
leg_data.Draw()
leg_data_border.Draw()
text_unc.Draw()
text_brunc.DrawLatex(0.2, 0.21, '#lower[-0.03]{^{+4.0}}')
text_brunc.DrawLatex(0.2, 0.21, '_{#minus3.8}')
text_brunc.DrawLatex(0.2, 0.21, '#kern[.12]{% BR uncertainty not shown}')
text_pt.Draw()
leg_model.Draw()
c.cd().Modified()
c.cd().Update()

outfile_name = "ds_over_dplus_coal_vmult_wModels_ptint.pdf"
c.SaveAs(outfile_name)
'''
infile_lf_pp = ROOT.TFile.Open("ktopi_pp136.root")
graph_lf_pp = infile_lf_pp.Get("gr_uncor_sys") # names re swapped
graph_lf_pp_uncorr = infile_lf_pp.Get("gr_tot_sys")
graph_lf_pp_unscaled = graph_lf_pp.Clone("graph_lf_pp_tot_sys")
graph_lf_pp_uncorr.SetName("graph_lf_pp_uncor")
graph_lf_pp.SetLineWidth(2)
graph_lf_pp.SetLineColor(color_lf)
graph_lf_pp.SetMarkerColor(color_lf)
graph_lf_pp.SetMarkerStyle(ROOT.kOpenSquare)
graph_lf_pp.SetMarkerSize(1)
graph_lf_pp.SetFillStyle(0)
graph_lf_doubleratio_pp = graph_lf_pp.Clone("graph_lf_doubleratio_pp")
unc_uncorr_den = graph_lf_pp_uncorr.GetErrorYhigh(graph_lf_pp.GetN()-1)
unc_tot_den = graph_lf_pp.GetErrorYhigh(graph_lf_pp.GetN()-1)
unc_corr_den = np.sqrt(abs(graph_lf_pp.GetErrorYhigh(graph_lf_pp.GetN()-1)**2 - graph_lf_pp_uncorr.GetErrorYhigh(graph_lf_pp.GetN()-1)**2))
den = graph_lf_pp.GetPointY(graph_lf_pp.GetN()-1)
for imult in range(graph_lf_pp.GetN()):
    unc_uncorr_num = graph_lf_pp_uncorr.GetErrorYhigh(imult) if imult <  graph_lf_pp.GetN()-1 else 0.
    unc_corr_num = np.sqrt(abs(graph_lf_pp.GetErrorYhigh(imult)**2 - graph_lf_pp_uncorr.GetErrorYhigh(imult)**2)) if imult <  graph_lf_pp.GetN()-1 else 0.
    num = graph_lf_pp.GetPointY(imult) if imult <  graph_lf_pp.GetN()-1 else -10000.
    ratio = num / den
    unc_uncorr_ratio = np.sqrt(unc_uncorr_den**2/den**2 + unc_uncorr_num**2/num**2) * ratio 
    unc_corr_ratio = abs(unc_corr_den/den - unc_corr_num/num) * ratio
    unc_tot_ratio = np.sqrt(unc_uncorr_ratio**2 + unc_corr_ratio**2)
    graph_lf_doubleratio_pp.SetPoint(imult, graph_lf_pp.GetPointX(imult), ratio)
    graph_lf_doubleratio_pp.SetPointError(imult, graph_lf_pp.GetErrorXlow(imult)*5, unc_tot_ratio)
    graph_lf_pp.SetPoint(imult, graph_lf_pp.GetPointX(imult), graph_lf_pp.GetPointY(imult)*3.1)
    graph_lf_pp.SetPointError(imult, graph_lf_pp.GetErrorXlow(imult)*5, graph_lf_pp.GetErrorYhigh(imult)*3.1)
graph_lf_doubleratio_pp.RemovePoint(graph_lf_pp.GetN()-1)

infile_lf_pbpb = ROOT.TFile.Open("HEPData_K_over_pi_PbPb.root")
graph_lf_pbpb = infile_lf_pbpb.Get("Table 11/Graph1D_y2")
graph_lf_pbpb.SetLineWidth(2)
graph_lf_pbpb.SetLineColor(color_lf)
graph_lf_pbpb.SetMarkerColor(color_lf)
graph_lf_pbpb.SetMarkerStyle(ROOT.kFullTriangleUp)
graph_lf_pbpb.SetMarkerSize(1)
graph_lf_pbpb.SetFillStyle(0)
graph_lf_pbpb_mult = infile_lf_pbpb.Get("Table 11/Graph1D_y1")
graph_lf_doubleratio_pbpb = graph_lf_pbpb.Clone("graph_lf_doubleratio_pbpb")
graph_lf_pbpb_unscaled = graph_lf_pbpb.Clone("graph_lf_pbpb_tot_sys")
for imult in range(graph_lf_pbpb.GetN()):
    num = graph_lf_pbpb.GetPointY(imult)
    unc_num_high = graph_lf_pbpb.GetErrorYhigh(imult)
    unc_num_low = graph_lf_pbpb.GetErrorYlow(imult)
    ratio = num / den
    unc_low_ratio = np.sqrt(unc_num_low**2/num**2 + unc_tot_den**2/den**2) * ratio
    unc_high_ratio = np.sqrt(unc_num_high**2/num**2 + unc_tot_den**2/den**2) * ratio
    graph_lf_doubleratio_pbpb.SetPoint(imult, graph_lf_pbpb_mult.GetPointY(imult), ratio)
    graph_lf_doubleratio_pbpb.SetPointError(imult, graph_lf_pbpb_mult.GetErrorYlow(imult), graph_lf_pbpb_mult.GetErrorYhigh(imult),
                                            unc_low_ratio, unc_high_ratio)
    graph_lf_pbpb_unscaled.SetPoint(imult, graph_lf_pbpb_mult.GetPointY(imult), graph_lf_pbpb.GetPointY(imult))
    graph_lf_pbpb.SetPoint(imult, graph_lf_pbpb_mult.GetPointY(imult), graph_lf_pbpb.GetPointY(imult)*3.1)
    graph_lf_pbpb_unscaled.SetPointError(imult, graph_lf_pbpb_mult.GetErrorYlow(imult), graph_lf_pbpb_mult.GetErrorYhigh(imult),
                                         graph_lf_pbpb.GetErrorYlow(imult), graph_lf_pbpb.GetErrorYhigh(imult))
    graph_lf_pbpb.SetPointError(imult, graph_lf_pbpb_mult.GetErrorYlow(imult), graph_lf_pbpb_mult.GetErrorYhigh(imult),
                                graph_lf_pbpb.GetErrorYlow(imult)*3.1, graph_lf_pbpb.GetErrorYhigh(imult)*3.1)

leg_lf = ROOT.TLegend(0.2, 0.22, 0.8, 0.48)
leg_lf.SetTextSize(0.032)
leg_lf.SetBorderSize(0)
leg_lf.SetFillStyle(0)
leg_lf.SetMargin(0.1)
leg_lf.AddEntry(graph_pp_stat, "#it{#sigma}(D_{s}^{#plus})/#it{#sigma}(D^{#plus}), pp,#kern[0.3]{#sqrt{#it{s}}} = 13.6 TeV", "p")
leg_lf.AddEntry(graph_pbpb_stat, "#it{#sigma}(D_{s}^{#plus})/#it{#sigma}(D^{#plus}) Pb#minusPb,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.36 TeV", "p")
leg_lf.AddEntry(graph_oo_stat, "#it{#sigma}(D_{s}^{#plus})/#it{#sigma}(D^{#plus}) OO,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.36 TeV", "p")
leg_lf.AddEntry(graph_lf_pp, "#it{#sigma}(K^{#plus})/#it{#sigma}(#pi^{#plus}), pp,#kern[0.3]{#sqrt{#it{s}}} = 13.6 TeV", "p")
leg_lf.AddEntry(graph_lf_pbpb, "#it{#sigma}(K^{#plus})/#it{#sigma}(#pi^{#plus}), Pb#minusPb,#kern[0.2]{#sqrt{#it{s}_{NN}}} = 5.02 TeV", "p")
leg_lf.AddEntry("", "#scale[0.7]{Phys. Rev. C 101 (2020) 044907}", "")

c_lf = ROOT.TCanvas("c_lf", "c_lf", 500, 500)
h_frame = c_lf.cd().DrawFrame(
    1., 0.01, 5000., 0.95,
    ";#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}| < 0.5};strange-to-nonstrange ratio"
)
h_frame.GetYaxis().SetDecimals()
graph_lf_pp.DrawClone("2p")
graph_lf_pbpb.DrawClone("2p")
graph_pp_syst.DrawClone("2")
graph_pp_stat.DrawClone("pz")
graph_pp_stat_border.DrawClone("pz")
graph_pbpb_syst.DrawClone("2")
graph_pbpb_stat.DrawClone("pz")
graph_pbpb_stat_border.DrawClone("pz")
graph_oo_syst.DrawClone("2")
graph_oo_stat.DrawClone("pz")
graph_oo_stat_border.DrawClone("pz")
text_ALICE.Draw()
text_y.Draw()
text_unc.Draw()
text_brunc.DrawLatex(0.2, 0.21, '#lower[-0.03]{^{+4.0}}')
text_brunc.DrawLatex(0.2, 0.21, '_{#minus3.8}')
text_brunc.DrawLatex(0.2, 0.21, '#kern[.12]{% BR uncertainty not shown}')
leg_lf.Draw()
text_scale = ROOT.TLatex(0.75, 0.17, "K/#pi scaled by 3.1")
text_scale.SetNDC()
text_scale.SetTextFont(42)
text_scale.SetTextSize(0.03)
text_scale.Draw()
c_lf.cd().Modified()
c_lf.cd().Update()
c_lf.SaveAs("ds_over_dplus_vmult_wLF_ptint.pdf")

line_at_one = ROOT.TLine(1., 1., 5000., 1.)
line_at_one.SetLineWidth(2)
line_at_one.SetLineStyle(9)
line_at_one.SetLineColor(ROOT.kGray+2)

c_doubleratio_lf = ROOT.TCanvas("c_doubleratio_lf", "c_doubleratio_lf", 500, 500)
h_frame = c_doubleratio_lf.cd().DrawFrame(
    1., 0.01, 5000., 2.1,
    ";#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}| < 0.5};ratio to low-multiplicity pp"
)
h_frame.GetYaxis().SetDecimals()
line_at_one.Draw()
graph_lf_doubleratio_pp.DrawClone("2p")
graph_lf_doubleratio_pbpb.DrawClone("2p")
graph_doubleratio_pp_syst.DrawClone("2")
graph_doubleratio_pp_stat.DrawClone("pz")
graph_doubleratio_pp_stat_border.DrawClone("pz")
graph_doubleratio_pbpb_syst.DrawClone("2")
graph_doubleratio_pbpb_stat.DrawClone("pz")
graph_doubleratio_pbpb_stat_border.DrawClone("pz")
graph_doubleratio_oo_syst.DrawClone("2")
graph_doubleratio_oo_stat.DrawClone("pz")
graph_doubleratio_oo_stat_border.DrawClone("pz")
text_ALICE.Draw()
text_y.Draw()
text_unc.Draw()
leg_lf.Draw()
text_pt.SetY(0.82)
text_pt.Draw()
c_doubleratio_lf.cd().Modified()
c_doubleratio_lf.cd().Update()
c_doubleratio_lf.SaveAs("ds_over_dplus_ratio_to_lowmult_vmult_wLF_ptint.pdf")

# evaluate significance
n_mult_bins_pp = graph_pp_stat.GetN()
n_mult_bins_pp_plus_pbpb = n_mult_bins_pp+graph_pbpb_stat.GetN()
n_mult_bins = n_mult_bins_pp_plus_pbpb+graph_oo_stat.GetN()
graph_all = ROOT.TGraphAsymmErrors(n_mult_bins)
for imult in range(n_mult_bins):
    if imult < n_mult_bins_pp:
        mult = graph_pp_syst.GetPointX(imult)
        ratio = graph_pp_syst.GetPointY(imult)
        mult_unc_low = graph_pp_syst.GetErrorXlow(imult)/5
        mult_unc_high = graph_pp_syst.GetErrorXhigh(imult)/5
        ratio_unc_low = np.sqrt(graph_pp_syst.GetErrorYlow(imult)**2 + graph_pp_stat.GetErrorYlow(imult)**2)
        ratio_unc_high = np.sqrt(graph_pp_syst.GetErrorYhigh(imult)**2 + graph_pp_stat.GetErrorYhigh(imult)**2)
    elif imult < n_mult_bins_pp_plus_pbpb:
        mult = graph_pbpb_syst.GetPointX(imult-n_mult_bins_pp)
        ratio = graph_pbpb_syst.GetPointY(imult-n_mult_bins_pp)
        mult_unc_low = graph_pbpb_syst.GetErrorXlow(imult-n_mult_bins_pp)
        mult_unc_high = graph_pbpb_syst.GetErrorXhigh(imult-n_mult_bins_pp)
        ratio_unc_low = np.sqrt(graph_pbpb_syst.GetErrorYlow(imult-n_mult_bins_pp)**2 + graph_pbpb_stat.GetErrorYlow(imult-n_mult_bins_pp)**2)
        ratio_unc_high = np.sqrt(graph_pbpb_syst.GetErrorYhigh(imult-n_mult_bins_pp)**2 + graph_pbpb_stat.GetErrorYhigh(imult-n_mult_bins_pp)**2)
    else:
        mult = graph_oo_syst.GetPointX(imult-n_mult_bins_pp_plus_pbpb)
        ratio = graph_oo_syst.GetPointY(imult-n_mult_bins_pp_plus_pbpb)
        mult_unc_low = graph_oo_syst.GetErrorXlow(imult-n_mult_bins_pp_plus_pbpb)/5
        mult_unc_high = graph_oo_syst.GetErrorXhigh(imult-n_mult_bins_pp_plus_pbpb)/5
        ratio_unc_low = np.sqrt(graph_oo_syst.GetErrorYlow(imult-n_mult_bins_pp_plus_pbpb)**2 + graph_oo_stat.GetErrorYlow(imult-n_mult_bins_pp_plus_pbpb)**2)
        ratio_unc_high = np.sqrt(graph_oo_syst.GetErrorYhigh(imult-n_mult_bins_pp_plus_pbpb)**2 + graph_oo_stat.GetErrorYhigh(imult-n_mult_bins_pp_plus_pbpb)**2)
    graph_all.SetPoint(imult, mult, ratio)
    graph_all.SetPointError(imult, mult_unc_low, mult_unc_high, ratio_unc_low, ratio_unc_high)

graph_all.SetLineColor(ROOT.kBlack)
graph_all.SetMarkerColor(ROOT.kBlack)
graph_all.SetLineWidth(2)
graph_all.SetMarkerStyle(ROOT.kOpenDiamond)
func_all_pol0 = ROOT.TF1("func_all_pol0", "pol0")
func_all_pol0.SetLineColor(ROOT.kRed+1)
func_all_pol0.SetLineWidth(2)
func_all_pol1 = ROOT.TF1("func_all_pol1", "pol1")
func_all_pol1.SetLineColor(ROOT.kAzure+4)
func_all_pol1.SetLineWidth(2)
func_all_log = ROOT.TF1("func_all_log", "[0] + [1]*TMath::Log([2]*x)")
func_all_log.SetLineColor(ROOT.kGreen+2)
func_all_log.SetLineWidth(2)
graph_all.Fit("func_all_pol0")
graph_all.Fit("func_all_pol1", "+")
graph_all.Fit("func_all_log", "+")

lat_red = ROOT.TLatex()
lat_red.SetNDC()
lat_red.SetTextFont(42)
lat_red.SetTextSize(0.035)
lat_red.SetTextColor(ROOT.kRed+1)
lat_azure = ROOT.TLatex()
lat_azure.SetNDC()
lat_azure.SetTextFont(42)
lat_azure.SetTextSize(0.035)
lat_azure.SetTextColor(ROOT.kAzure+4)
lat_green = ROOT.TLatex()
lat_green.SetNDC()
lat_green.SetTextFont(42)
lat_green.SetTextSize(0.035)
lat_green.SetTextColor(ROOT.kGreen+2)

c_signif = ROOT.TCanvas("c_signif", "c_signif", 500, 500)
h_frame = c_signif.cd().DrawFrame(
    1., 0.01, 5000., 0.9,
    ";#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}| < 0.5};strange-to-nonstrange ratio"
)
c_signif.cd().SetLogx()
graph_all.Draw("pz")
func_all_pol0.Draw("same")
func_all_pol1.Draw("same")
chi2 = func_all_pol0.GetChisquare()
ndf = func_all_pol0.GetNDF()
prob = ROOT.TMath.Prob(chi2, ndf)
nsigma = ROOT.Math.normal_quantile_c(prob, 1)
lat_red.DrawLatex(0.2, 0.3, f"#chi^{{2}}/ndf={chi2/ndf:.1f}, prob={prob:.1e}, n#sigma(not flat)={nsigma:.2f}")
chi2 = func_all_pol1.GetChisquare()
ndf = func_all_pol1.GetNDF()
prob = ROOT.TMath.Prob(chi2, ndf)
nsigma = func_all_pol1.GetParameter(1)/func_all_pol1.GetParError(1)
lat_azure.DrawLatex(0.2, 0.25, f"#chi^{{2}}/ndf={chi2/ndf:.1f}, coef={func_all_pol1.GetParameter(1):.1e}#pm{func_all_pol1.GetParError(1):.1e}, n#sigma(coef>0)={nsigma:.2f}")
chi2 = func_all_log.GetChisquare()
ndf = func_all_log.GetNDF()
prob = ROOT.TMath.Prob(chi2, ndf)
nsigma = abs(ROOT.Math.normal_quantile_c(prob, 1))
lat_green.DrawLatex(0.2, 0.2, f"#chi^{{2}}/ndf={chi2/ndf:.1f}, prob={prob:.1e}, n#sigma={nsigma:.2f}")
c_signif.SaveAs("significance.pdf")

func_all_pol0_pp = ROOT.TF1("func_all_pol0_pp", "pol0")
func_all_pol0_pp.SetLineColor(ROOT.kGreen+2)
func_all_pol0_pp.SetLineWidth(2)
graph_all.Fit("func_all_pol0_pp", "R", "R", 3., 21.)
c_signif2 = ROOT.TCanvas("c_signif2", "c_signif2", 500, 500)
h_frame = c_signif2.cd().DrawFrame(
    1., 0.01, 5000., 0.9,
    ";#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}| < 0.5};strange-to-nonstrange ratio"
)
c_signif2.cd().SetLogx()
graph_all.Draw("pz")
chi2_pbpb_minus_pp = 0.
for imult in range(graph_all.GetN()):
    chi2_pbpb_minus_pp += (graph_all.GetPointY(imult) - func_all_pol0_pp.GetParameter(0))**2 / graph_all.GetErrorYlow(imult)**2
prob = ROOT.TMath.Prob(chi2_pbpb_minus_pp, graph_all.GetN())
chi2_pbpb_minus_pp = chi2_pbpb_minus_pp / graph_all.GetN()
lat_green.DrawLatex(0.2, 0.2, f"#chi^{{2}}/ndf(Pb#minusPb #minus pp)={chi2_pbpb_minus_pp:.1f}, n#sigma(Pb#minusPb > pp)={ROOT.Math.normal_quantile_c(prob, 1):.2f}")
c_signif2.SaveAs("significance2.pdf")

c_syst_cent = ROOT.TCanvas("c_syst_cent", "", 1000, 500)
c_syst_cent.Divide(2, 1)
h_frame = c_syst_cent.cd(1).DrawFrame(
    0., 0., 90, 0.9,
    ";FT0C percentile;D_{s}^{#plus}/D^{#plus}"
)
c_syst_cent.cd(1).SetLogx(0)
graph_pbpb_vscent_syst.Draw("2")
graph_pbpb_vscent_stat.Draw("pz")
func_vscent_pol1 = ROOT.TF1("func_vscent_pol1", "pol1")
func_vscent_pol1.SetLineColor(ROOT.kRed+1)
graph_pbpb_vscent_stat.Fit("func_vscent_pol1")
sigma_ratio = 3./90. * abs(func_vscent_pol1.GetParameter(1))
hist_syst_cent = ROOT.TH1F("hist_syst_cent", "", 9, 0., 90.)
hist_syst_tot = ROOT.TH1F("hist_syst_tot", "", 9, 0., 90.)
hist_syst_cent.SetLineWidth(2)
hist_syst_cent.SetLineColor(ROOT.kRed+1)
hist_syst_tot.SetLineWidth(2)
hist_syst_tot.SetLineColor(ROOT.kBlack)
for icent in range(graph_pbpb_vscent_syst.GetN()):
    hist_syst_cent.SetBinContent(icent+1, sigma_ratio * graph_pbpb_vscent_syst.GetPointX(icent))
    hist_syst_tot.SetBinContent(icent+1, graph_pbpb_vscent_syst.GetErrorYhigh(icent))
h_frame = c_syst_cent.cd(2).DrawFrame(
    0., 1.e-4, 90, 0.1,
    ";FT0C percentile;systematic uncertainty"
)
c_syst_cent.cd(2).SetLogx(0)
c_syst_cent.cd(2).SetLogy(1)
hist_syst_tot.Draw("same")
hist_syst_cent.Draw("same")
c_syst_cent.SaveAs("centrality_systematics.pdf")
'''
outfile = ROOT.TFile("ds_over_dplus_ratio_vmult_ptint.root", "recreate")
outfile.mkdir("single_ratios")
outfile.cd("single_ratios")
graph_pp_syst.SetName("graph_pp_syst_nobr")
graph_pp_syst.Write()
graph_pp_stat.SetName("graph_pp_stat")
graph_pp_stat.Write()
graph_pbpb_syst.SetName("graph_pbpb_syst_nobr")
graph_pbpb_syst.Write()
graph_pbpb_stat.SetName("graph_pbpb_stat")
graph_pbpb_stat.Write()
#graph_all.SetName("graph_pp_pbpb_totuncuncorr_nobr")
#graph_all.Write()
#graph_lf_pp_unscaled.Write()
#graph_lf_pp_uncorr.Write()
#graph_lf_pbpb_unscaled.Write()
outfile.cd()
outfile.mkdir("double_ratios")
outfile.cd("double_ratios")
#graph_lf_doubleratio_pp.GetYaxis().SetRangeUser(0.5, 1.5)
#graph_lf_doubleratio_pp.Write()
#graph_lf_doubleratio_pbpb.Write()
graph_doubleratio_pp_syst.Write()
graph_doubleratio_pp_stat.Write()
graph_doubleratio_pbpb_syst.Write()
graph_doubleratio_pbpb_stat.Write()
outfile.Close()