# Quantum Mechanics — Core Concepts Overview

## What is Quantum Mechanics?
Quantum mechanics (QM) is the branch of physics that describes nature at the scale of atoms and subatomic particles. At this scale, the classical (Newtonian) rules break down and particles behave in radically counterintuitive ways.

Classical physics: a ball has a definite position and speed at all times.
Quantum physics: a particle exists in a blur of possibilities until you measure it.

---

## 1. The Quantum World — Scale

Quantum effects dominate at sizes below ~100 nanometers (10⁻⁹ m).
- Atoms: ~0.1 nm
- Atomic nucleus: ~1 fm (femtometer = 10⁻¹⁵ m)
- Electrons, protons, neutrons, photons → quantum objects

At human scale, quantum effects average out and classical physics works fine.

---

## 2. Wave-Particle Duality

Every quantum object behaves as BOTH a wave and a particle depending on how you observe it.

- **As a wave**: it spreads out, interferes with itself (like ripples on water), and can pass through two slits simultaneously.
- **As a particle**: when detected, it hits a single point on a screen.

**Double-slit experiment** (key demonstration):
1. Fire electrons one at a time at a barrier with two slits.
2. Without measuring which slit → interference pattern (wave behavior).
3. With a detector at slits → no interference pattern (particle behavior).
“Observation” means any interaction that can get information about the electron’s path.

The act of measurement changes the outcome. Observation matters.

---

## 3. The Wave Function (ψ)

The wave function ψ (psi) is the mathematical object that contains all information about a quantum system.

- ψ is not a physical wave you can touch — it is a probability amplitude.
- |ψ|² gives the probability of finding the particle at a given location.
- Before measurement: the particle exists in all possible states simultaneously (superposition).
- After measurement: the wave function "collapses" to one definite state.

The Schrödinger equation describes how ψ evolves over time (deterministic between measurements).

---

## 4. Superposition

A quantum particle can be in multiple states at once until measured.

Classic analogy: Schrödinger's cat thought experiment.
- A cat in a sealed box is connected to a quantum event (radioactive decay).
- Until you open the box, the cat is theoretically both alive AND dead.
- Opening the box (measuring) collapses it to one outcome.

In real quantum computers: a qubit can be 0 AND 1 simultaneously. Measuring collapses it to 0 or 1.

---

## 5. Heisenberg Uncertainty Principle

You cannot simultaneously know both the exact position and exact momentum of a particle.

Δx · Δp ≥ ℏ/2

- Δx = uncertainty in position
- Δp = uncertainty in momentum
- ℏ = reduced Planck constant (≈ 1.055 × 10⁻³⁴ J·s)

This is NOT a limitation of instruments — it is a fundamental property of nature. The more precisely you pin down a particle's position, the less you can know about where it's going.

Similarly: energy and time are also an uncertainty pair (ΔE · Δt ≥ ℏ/2).

---

## 6. Quantization

Energy, charge, and other properties come in discrete chunks called quanta — not continuous.

**Photons**: light is made of discrete packets of energy.
E = hf
- h = Planck's constant (6.626 × 10⁻³⁴ J·s)
- f = frequency of light

**Atomic energy levels**: electrons in an atom can only occupy specific energy levels. They jump between levels by absorbing or emitting photons of exactly the right energy. This produces the emission spectra (colored lines) that uniquely identify each element.

---

## 7. Quantum Entanglement

Two particles can be correlated in such a way that measuring one instantly determines the state of the other, regardless of distance.

- Einstein called this "spooky action at a distance" and rejected it.
- Experiments (Bell's theorem tests, 1970s–present) prove entanglement is real.
- Entangled particles share a joint wave function — they are not independent.
- Measuring particle A instantly fixes the outcome for particle B.

Important: this cannot be used to transmit information faster than light (the outcome is random; you need a classical channel to compare results).

Applications: quantum cryptography, quantum teleportation (of states, not matter), quantum computing.

---

## 8. The Pauli Exclusion Principle

No two identical fermions (particles with half-integer spin: electrons, protons, neutrons) can occupy the same quantum state simultaneously.

This is why:
- Electrons fill different orbitals in atoms → explains chemistry and the periodic table.
- Matter is solid (electrons can't all collapse to the lowest energy state).
- Neutron stars don't collapse (neutron degeneracy pressure).

Bosons (photons, Higgs) do NOT follow this rule — lasers work because many photons can share the same state.

---

## 9. Spin

Quantum spin is an intrinsic form of angular momentum with no classical analogue. It is not literal spinning.

- Electrons have spin-1/2: can be spin-up (+½) or spin-down (−½).
- Spin determines magnetic properties and how particles interact with fields.
- Stern-Gerlach experiment (1922): passed silver atoms through a magnetic field — got two discrete spots instead of a smear, proving spin quantization.

Spin is the basis for MRI (magnetic resonance imaging) and quantum computing qubits.

---

## 10. Quantum Tunneling

A particle can pass through a potential energy barrier that classically it should not have enough energy to cross.

- The wave function has a non-zero value on the other side of the barrier.
- There is a finite probability the particle "tunnels" through.
- Probability decreases exponentially with barrier width and height.

Real-world consequences:
- Nuclear fusion in stars (protons tunnel through electrostatic repulsion).
- Radioactive alpha decay.
- Tunnel diodes and flash memory in electronics.
- Scanning tunneling microscopes (STM).

---

## 11. Interpretations of Quantum Mechanics

The math is agreed upon; what it means is debated.

| Interpretation | Core idea |
|---|---|
| Copenhagen | Wave function is just a calculation tool; collapse is real |
| Many-Worlds | Every measurement branches into parallel universes; no collapse |
| Pilot Wave (de Broglie-Bohm) | Particles have definite positions, guided by a real wave |
| QBism | Wave function represents an agent's beliefs, not physical reality |

None is experimentally distinguishable yet — this is philosophy of physics, not settled science.

---

## 12. Key Equations at a Glance

| Equation | Meaning |
|---|---|
| E = hf | Photon energy |
| E = mc² | Mass-energy equivalence (special relativity + QM → QFT) |
| Δx·Δp ≥ ℏ/2 | Uncertainty principle |
| iℏ ∂ψ/∂t = Ĥψ | Schrödinger equation (time evolution) |
| E_n = −13.6/n² eV | Hydrogen atom energy levels |

---

## 13. Applications of Quantum Mechanics

| Application | QM concept used |
|---|---|
| Lasers | Stimulated emission, energy levels |
| Semiconductors / transistors | Band gaps, quantum tunneling |
| MRI scanners | Nuclear spin |
| LED / OLED screens | Electron energy transitions |
| Quantum computers | Superposition, entanglement |
| Atomic clocks | Precise energy level transitions |
| Electron microscopes | Wave nature of electrons |

---

## Summary

| Concept | One-line description |
|---|---|
| Wave-particle duality | Every quantum object is both wave and particle |
| Wave function | Mathematical description of all possible states |
| Superposition | A system exists in multiple states until measured |
| Uncertainty principle | Position and momentum cannot both be exact |
| Quantization | Energy comes in discrete packets |
| Entanglement | Two particles share a single quantum state |
| Pauli exclusion | No two fermions in the same quantum state |
| Spin | Intrinsic angular momentum, discrete values |
| Tunneling | Particles can cross classically forbidden barriers |
