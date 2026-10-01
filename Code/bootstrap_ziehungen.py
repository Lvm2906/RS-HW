# bootstrap_ziehungen.py — Stufe 2, Schritt 6 (Mechanik, Cowork, 28.09.2026)
#
# Erzeugt die Residuen-Ziehungen fuer den Residuen-Bootstrap EINMAL und speichert sie, damit
# Klaus' Implementierung und die Referenzimplementierung exakt dieselben 2000 Replikationen rechnen
# (METHODIK §2 Pkt. 4, Festlegungen 28.09.2026).
#
# Konvention: Zeile r der Matrix = Replikation r; Spalte j = j-tes Paar des Regimes in
# chronologischer Reihenfolge; Eintrag = Index des gezogenen Residuums (0-basiert, chronologisch).
# Reihenfolge der Ziehung: erst Krise (2000 x 132), dann ruhig (2000 x 231), ein Generator, Seed 42.
from pathlib import Path
import numpy as np

SEED, B, N_KRISE, N_RUHIG = 42, 2000, 132, 231
BASIS = Path(__file__).parent.parent

rng = np.random.default_rng(SEED)
idx_krise = rng.integers(0, N_KRISE, size=(B, N_KRISE))
idx_ruhig = rng.integers(0, N_RUHIG, size=(B, N_RUHIG))
np.savez_compressed(BASIS / "Abgaben" / "bootstrap_ziehungen.npz",
                    idx_krise=idx_krise.astype(np.int16), idx_ruhig=idx_ruhig.astype(np.int16),
                    seed=SEED, B=B)
print("gespeichert:", idx_krise.shape, idx_ruhig.shape, "Seed", SEED)
