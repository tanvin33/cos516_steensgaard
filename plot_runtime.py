import matplotlib.pyplot as plt
import numpy as np

def plot_constraints_vs_runtime():
    #constraints = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
    #runtime = [0.285660, 0.664231, 0.937014, 1.525256, 1.880278, 1.931543, 2.384522, 2.539082, 2.821481, 3.240975]

    constraints = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
    runtime = [0.187535, 0.290561, 0.437670, 0.606819, 0.774943, 0.882693, 1.196928, 1.397740, 1.716502, 1.805702]


    if len(constraints) != len(runtime):
        raise ValueError("Bad data input")

    plt.figure()
    plt.plot(constraints, runtime, marker='o')
    plt.xlabel("Number of Constraints")
    plt.ylabel("Runtime in Seconds")
    plt.title("Number of Constraints vs. Runtime for Test Program #2")
    plt.grid(True)

    plt.savefig("plot.png", dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved plot")

plot_constraints_vs_runtime()