"""
Quantum Mechanics — concepts in Python code (no physics library needed)
Run with: python3 quantum_concepts.py

We use pure math (math, cmath, random) to illustrate the ideas.
"""

import math
import cmath
import random


# ── 1. Wave-particle duality: double-slit simulation ─────────────────────────

def double_slit():
    """
    Without observing which slit → interference pattern (wave).
    With observer → two bands (particle).
    We model probability of landing at each screen position.
    """
    print("\n── Double-Slit Experiment ──")
    screen_width = 40
    slit1, slit2 = 10, 30   # slit positions on screen

    print("No observer (wave interference):")
    row = ""
    for x in range(screen_width):
        # Wave: amplitude from each slit, add them (interference)
        amp1 = math.cos(abs(x - slit1) * 0.5)
        amp2 = math.cos(abs(x - slit2) * 0.5)
        intensity = (amp1 + amp2) ** 2
        row += "█" if intensity > 0.5 else ("▒" if intensity > 0 else " ")
    print(" " + row)

    print("With observer (particle, no interference):")
    row = ""
    for x in range(screen_width):
        # Particle: independent probability from each slit
        p1 = max(0, 1 - abs(x - slit1) / 8)
        p2 = max(0, 1 - abs(x - slit2) / 8)
        intensity = p1 + p2
        row += "█" if intensity > 0.8 else ("▒" if intensity > 0.3 else " ")
    print(" " + row)


# ── 2. Wave function and probability ─────────────────────────────────────────

def wave_function():
    """
    A simple Gaussian wave packet: the particle is most likely found near center.
    |ψ(x)|² is the probability density.
    """
    print("\n── Wave Function — Probability Distribution ──")
    center = 20
    width = 5    # σ (sigma), how spread out

    print("Probability of finding particle at each position:")
    total = 0
    probs = []
    for x in range(40):
        # Gaussian: bell curve centered at 'center'
        psi_sq = math.exp(-((x - center) ** 2) / (2 * width ** 2))
        probs.append(psi_sq)
        total += psi_sq

    for x, p in enumerate(probs):
        bar = "█" * int(p / max(probs) * 20)
        print(f"  x={x:2d} | {bar}")


# ── 3. Superposition and measurement (collapse) ───────────────────────────────

def superposition():
    """
    A qubit can be in state |0⟩, |1⟩, or any superposition α|0⟩ + β|1⟩
    where |α|² + |β|² = 1.
    Measurement collapses it: probability |α|² for 0, |β|² for 1.
    """
    print("\n── Superposition & Measurement ──")

    def make_qubit(angle_degrees):
        """angle 0° = pure |0⟩, 90° = pure |1⟩, 45° = equal superposition."""
        theta = math.radians(angle_degrees)
        alpha = math.cos(theta)   # amplitude for |0⟩
        beta = math.sin(theta)    # amplitude for |1⟩
        return alpha, beta

    def measure(alpha, beta, n=1000):
        """Simulate n measurements. Returns count of 0s and 1s."""
        p0 = alpha ** 2   # probability of measuring 0
        zeros = sum(1 for _ in range(n) if random.random() < p0)
        return zeros, n - zeros

    for angle in [0, 30, 45, 60, 90]:
        a, b = make_qubit(angle)
        zeros, ones = measure(a, b)
        print(f"  angle={angle:2d}°  α={a:.3f} β={b:.3f}  "
              f"→ measured 0: {zeros/10:.1f}%  1: {ones/10:.1f}%")


# ── 4. Heisenberg Uncertainty Principle ───────────────────────────────────────

def uncertainty_principle():
    """
    Δx · Δp ≥ ℏ/2
    If we reduce position uncertainty, momentum uncertainty grows.
    """
    print("\n── Heisenberg Uncertainty Principle ──")
    hbar = 1.055e-34  # J·s

    print(f"  ℏ = {hbar:.3e} J·s")
    print(f"  Δx · Δp ≥ ℏ/2 = {hbar/2:.3e} J·s")
    print()

    position_uncertainties = [1e-10, 1e-11, 1e-12, 1e-13]
    for dx in position_uncertainties:
        dp_min = hbar / (2 * dx)
        print(f"  Δx = {dx:.0e} m  →  Δp ≥ {dp_min:.3e} kg·m/s")

    print("\n  Tighter position knowledge = larger momentum spread.")


# ── 5. Quantized energy levels (hydrogen atom) ───────────────────────────────

def energy_levels():
    """
    Electron in hydrogen: energy = -13.6 eV / n²
    Only discrete levels allowed — quantum jumps between them emit/absorb photons.
    """
    print("\n── Hydrogen Atom Energy Levels ──")
    E0 = -13.6  # eV (ground state energy)

    levels = {}
    for n in range(1, 8):
        E = E0 / n**2
        levels[n] = E
        bar = "─" * int(abs(E) * 2)
        print(f"  n={n}  E={E:8.3f} eV  |{bar}")

    print()
    print("Photon energies for transitions (emission lines):")
    for n_high in [3, 4, 5]:
        for n_low in range(1, n_high):
            delta_E = levels[n_high] - levels[n_low]  # negative = photon emitted
            wavelength_nm = 1240 / abs(delta_E)       # E=hc/λ, hc≈1240 eV·nm
            print(f"  n={n_high}→n={n_low}  ΔE={delta_E:7.3f} eV  λ={wavelength_nm:.1f} nm")


# ── 6. Quantum tunneling probability ─────────────────────────────────────────

def tunneling():
    """
    Transmission probability through a rectangular barrier:
    T ≈ exp(-2κL)   where κ = sqrt(2m(V-E))/ℏ
    """
    print("\n── Quantum Tunneling ──")
    hbar = 1.055e-34
    m_e = 9.109e-31   # electron mass kg
    eV  = 1.602e-19   # Joules per eV

    E = 1.0  # particle energy in eV
    V = 2.0  # barrier height in eV  (V > E → classical: impossible)

    kappa = math.sqrt(2 * m_e * (V - E) * eV) / hbar

    print(f"  Particle energy  E = {E} eV")
    print(f"  Barrier height   V = {V} eV  (classically forbidden)")
    print(f"  κ = {kappa:.3e} m⁻¹")
    print()

    for L_nm in [0.1, 0.5, 1.0, 2.0, 5.0]:
        L = L_nm * 1e-9   # nm → m
        T = math.exp(-2 * kappa * L)
        print(f"  Barrier width L={L_nm:.1f} nm → T = {T:.4e}  ({T*100:.6f}%)")

    print("\n  Tunneling drops exponentially with barrier width.")


# ── 7. Entanglement — correlated measurement simulation ──────────────────────

def entanglement():
    """
    Two entangled particles share a state. Measuring one instantly determines the other.
    Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    When Alice measures 0, Bob always gets 0. Alice 1 → Bob 1. (100% correlated)
    """
    print("\n── Quantum Entanglement ──")
    print("  Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2")
    print("  1000 measurements:")

    both_0, both_1, mixed = 0, 0, 0
    for _ in range(1000):
        # 50/50 collapse: both get same outcome
        outcome = random.choice([0, 1])
        alice = outcome
        bob = outcome    # always correlated
        if alice == 0 and bob == 0:
            both_0 += 1
        elif alice == 1 and bob == 1:
            both_1 += 1
        else:
            mixed += 1

    print(f"  Alice=0, Bob=0 : {both_0}")
    print(f"  Alice=1, Bob=1 : {both_1}")
    print(f"  Mismatched     : {mixed}")
    print(f"  Correlation    : {(both_0+both_1)/10:.1f}%  (classical max: 75%)")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    double_slit()
    wave_function()
    superposition()
    uncertainty_principle()
    energy_levels()
    tunneling()
    entanglement()
