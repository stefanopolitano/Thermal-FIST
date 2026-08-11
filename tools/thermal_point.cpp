#include <cmath>
#include <cstdlib>
#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "HRGBase.h"
#include "HRGEV.h"
#include "HRGVDW.h"

using namespace thermalfist;

namespace {
std::string sanitize_key(const std::string& in) {
  std::string out;
  out.reserve(in.size());
  for (char ch : in) {
    if (std::isalnum(static_cast<unsigned char>(ch))) {
      out.push_back(ch);
    } else {
      out.push_back('_');
    }
  }
  return out;
}
}

void SetResonanceWidthIntegration(ThermalModelBase* model, int width_mode_int) {
  ThermalParticle::ResonanceWidthIntegration width_mode =
      ThermalParticle::ZeroWidth;
  if (width_mode_int == ThermalParticle::ZeroWidth) {
    printf("Using ZeroWidth resonance treatment.\n");
    width_mode = ThermalParticle::ZeroWidth;
  } else if (width_mode_int == ThermalParticle::BWTwoGamma) {
    printf("Using BWTwoGamma resonance treatment.\n");
    width_mode = ThermalParticle::BWTwoGamma;
  } else if (width_mode_int == ThermalParticle::eBWconstBR) {
    printf("Using eBWconstBR resonance treatment.\n");
    width_mode = ThermalParticle::eBWconstBR;
  } else {
    std::cerr << "Warning: Invalid width_mode_int " << width_mode_int
              << ". Defaulting to ZeroWidth.\n";
    width_mode = ThermalParticle::ZeroWidth;
  }
  model->SetUseWidth(width_mode);
}

void SetStatistics(ThermalModelBase* model, bool enable) {
  if (enable) {
    printf("Using Quantum statistics.\n");
  } else {
    printf("Using Boltzmann statistics.\n");
  }
  model->SetStatistics(enable);
}

void SetFeeddownType(Feeddown::Type& feeddown_type, int feeddown_type_int) {
  if (feeddown_type_int >= Feeddown::Primordial &&
      feeddown_type_int <= Feeddown::Strong) {
    feeddown_type = static_cast<Feeddown::Type>(feeddown_type_int);
    printf("Using feeddown type %d.\n", feeddown_type_int);
  } else {
    std::cerr << "Warning: Invalid feeddown_type_int " << feeddown_type_int
              << ". Defaulting to StabilityFlag.\n";
    feeddown_type = Feeddown::StabilityFlag;
  }
}

int main(int argc, char* argv[]) {
  // Load parameters from command line arguments
  const std::string list_file = argv[1];
  const std::string decays_file = argv[2];
  const int model_type = std::atoi(argv[3]);
  const double T = std::atof(argv[4]);
  const double V = std::atof(argv[5]);
  const double muB = std::atof(argv[6]);
  const double muQ = std::atof(argv[7]);
  const double muS = std::atof(argv[8]);
  const double muC = std::atof(argv[9]);
  const double gammaQ = std::atof(argv[10]);
  const double gammaS = std::atof(argv[11]);
  const double gammaC = std::atof(argv[12]);
  const int width_mode_int = std::atoi(argv[13]);
  const int feeddown_type_int = std::atoi(argv[14]);
  const int statistics_int = std::atoi(argv[15]);
  const std::string outdir = argv[16];
  const std::string outlabel = argv[17];
  const bool debug = std::atoi(argv[18]);

  printf("Input parameters:\n");
  printf("  list_file: %s\n", list_file.c_str());
  printf("  decays_file: %s\n", decays_file.c_str());
  printf("  model_type: %d\n", model_type);
  printf("  T: %f GeV\n", T);
  printf("  muB: %f GeV\n", muB);
  printf("  muQ: %f GeV\n", muQ);
  printf("  muS: %f GeV\n", muS);
  printf("  V: %f fm^3\n", V);
  printf("  gammaQ: %f\n", gammaQ);
  printf("  gammaS: %f\n", gammaS);
  printf("  gammaC: %f\n", gammaC);
  printf("  width_mode_int: %d\n", width_mode_int);
  printf("  feeddown_type_int: %d\n", feeddown_type_int);
  printf("  statistics_int: %d\n", statistics_int);

  // Initialize the thermal model based on the input parameters
  ThermalParticleSystem tps(list_file, decays_file);
  ThermalModelBase* model = nullptr;
  if (model_type == 0) {
    printf("Using Charm-Canonical HRG model.\n");
    model = new ThermalModelCanonicalCharm(&tps);
  } else if (model_type == 1) {
    printf("Using Ideal HRG model.\n");
    model = new ThermalModelCanonical(&tps);
  } else if (model_type == 2) {
    printf("Using Strangeness-Canonical HRG model.\n");
    model = new ThermalModelCanonicalStrangeness(&tps);
  } else {
    std::cerr << "Error: Unsupported model_type " << model_type << ". Only 2 (Charm-Canonical HRG) is implemented in this tool.\n";
    return 3;
  }
  Feeddown::Type feeddown_type = Feeddown::StabilityFlag;
  SetStatistics(model, statistics_int);
  SetFeeddownType(feeddown_type, feeddown_type_int);
  SetResonanceWidthIntegration(model, width_mode_int);
  model->SetTemperature(T);
  model->SetVolume(V);
  model->SetElectricChemicalPotential(muQ);
  model->SetBaryonChemicalPotential(muB);
  model->SetStrangenessChemicalPotential(muS);
  model->SetGammaq(gammaQ);
  model->SetGammaS(gammaS);
  model->SetGammaC(gammaC);
  model->SetBaryonCharge(0);
  model->SetElectricCharge(0);
  model->SetStrangeness(0);
  model->SetCharm(0);
  //model->ConstrainMuS(true);
  //model->ConstrainMuQ(true);
  //model->SetQoverB(0.4);

  // dummp full configuration for debugging
  // crete output debug file
  if (debug) {
     printf("Debug mode enabled. Writing thermal model configuration to debug file.\n");
     
     std::ofstream debug_out(outdir + "/debug_" + outlabel + ".txt");
     debug_out << "Thermal model configuration:\n";
     debug_out << "  Temperature (T): " << T << " GeV\n";
     debug_out << "  Volume (V): " << V << " fm^3\n";
     debug_out << "  Baryon chemical potential (muB): " << muB << " GeV\n";
     debug_out << "  Electric chemical potential (muQ): " << muQ << " GeV\n";
     debug_out << "  Strangeness chemical potential (muS): " << muS << " GeV\n";
     debug_out << "  Charm chemical potential (muC): " << muC << " GeV\n";
     debug_out << "  Gamma_q: " << gammaQ << "\n";
     debug_out << "  Gamma_S: " << gammaS << "\n";
     debug_out << "  Gamma_C: " << gammaC << "\n";
     debug_out << "  Resonance width mode: " << width_mode_int << "\n";
     debug_out << "  Feeddown type: " << feeddown_type_int << "\n";
     debug_out << "  Statistics: " << (statistics_int ? "Quantum" : "Boltzmann") << "\n";
     debug_out.close();
  }
  
  model->FixParameters();
  model->CalculateDensities();
  //model->CalculateFluctuations();
  const double abs_charm_density = model->CalculateAbsoluteCharmDensity();

  // Create a struct to hold charm ground state yields and a vector to store them.
  struct CharmYieldEntry {
    long long pdg;
    std::string key;
    double value;
  };
  std::vector<CharmYieldEntry> charm_ground_yields;

  // Loop over all particles and calculate yields for charm ground states (charm > 0).
  printf("Calculating yields for charm ground states (feeddown type %d)...\n", feeddown_type_int);
  printf("Total number of particles in the system: %zu\n", model->TPS()->Particles().size());
  for (const auto& part : model->TPS()->Particles()) {
    //if (!part.IsStable())          continue; // Only consider stable particles
    if (part.Charm() <= 0)         continue; // Only consider charm > 0 ground states
    if (part.AbsoluteCharm() < 0.5) continue; // Skip if absolute charm is less than 0.5 (to avoid non-charm or very low charm states)

    const long long pdg = part.PdgId();
    const double primordial_density = model->GetDensity(pdg, Feeddown::Primordial);
    const double strong_density = model->GetDensity(pdg, Feeddown::Strong);
    const double weak_density = model->GetDensity(pdg, Feeddown::Weak);
    const double yield =
        model->GetDensity(pdg, Feeddown::Weak) * model->Volume();
    const double yield_primordial =
        model->GetDensity(pdg, Feeddown::Primordial) * model->Volume();
    const double yield_strong =
        model->GetDensity(pdg, Feeddown::Strong) * model->Volume();
    const double yield_weak =
        model->GetDensity(pdg, Feeddown::Weak) * model->Volume();
    const double yield_stability_flag =
        model->GetDensity(pdg, Feeddown::StabilityFlag) * model->Volume();
    
        const std::string key =
        "Nch_" + sanitize_key(part.Name()) + "_pdg" +
        std::to_string(pdg);

    // Print yields for Ds and D+
    if (abs(pdg) == 411 || abs(pdg) == 431) {
       //printf("Volume = %f fm^3\n", model->Volume());
       //printf("PDG: %lld, yield = %f (primordial density = %e)\n", abs(pdg), yield_primordial, primordial_density);
       //printf("PDG: %lld, yield = %f (strong density = %e)\n", abs(pdg), yield_strong, strong_density);
       printf("PDG: %lld, yield = %f (yield_primordial = %f, yield_weak = %f, yield_stability_flag = %f)\n", abs(pdg), yield_stability_flag, yield_primordial, yield_weak, yield_stability_flag);
    }

    charm_ground_yields.push_back({pdg, key, yield});
  }

  std::sort(charm_ground_yields.begin(), charm_ground_yields.end(),
            [](const CharmYieldEntry& a, const CharmYieldEntry& b) {
              return a.pdg < b.pdg;
            });

  double total_charm_yield = model->CalculateAbsoluteCharmDensity() * model->Volume() / 2.0;
  std::cout << "RESULT=" << total_charm_yield << "\n";

  delete model;
  return 0;
}