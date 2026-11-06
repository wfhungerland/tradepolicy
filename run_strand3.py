"""Run strand 3 end to end, in order, with timing. Stops at the first error.

  30 downloads (skips files already there)  31 ITPD-E panel  32 NAFTA validation
  33 tariff inputs  39 MAcMap baseline  34 US tariffs  35 EU border effects
  36 EU scenarios  38 transport  37 site export  40 comparison with the cloud run
Usage: python run_strand3.py            (all steps)
       python run_strand3.py 34 36 37   (only these steps)
"""
import subprocess
import sys
import time

STEPS = ["30_scenario_download.py", "31_itpd_panel.py", "32_validate_yotov.py", "33_tariff_inputs.py",
         "39_macmap_baseline.py", "34_scenario_us_tariffs.py", "35_eu_border_effects.py",
         "36_scenario_eu.py", "38_scenario_transport.py", "37_export_scenarios.py", "40_check_reproduction.py"]


def main():
    wanted = sys.argv[1:]
    steps = [s for s in STEPS if not wanted or s[:2] in wanted]
    for s in steps:
        t = time.time()
        print(f"\n=== {s}", flush=True)
        r = subprocess.run([sys.executable, s])
        print(f"=== {s} done in {time.time() - t:.0f} s (exit {r.returncode})", flush=True)
        if r.returncode != 0:
            print("Stopped. Send the last lines above to Claude.")
            sys.exit(r.returncode)
    print("\nAll steps done.")


if __name__ == "__main__":
    main()
