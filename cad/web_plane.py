"""The hinge crossmembers' webs under the hinge bar's fillets that stand over them (xt_hinges `bar` `web`, CHS-18,
FAT-26, I2-125).

A fillet over a web passes its run's force into the web's bottom edge, and the web spreads it up through its depth to
the section's shear flow. The frame model's beam carries the crossmember's bending and shear as plane sections, and its
rigid links reach each weld point from the beam's axis, so what it leaves out is the web's own stretch under the run,
the load's spread up the web. Take the web as a plate in plane stress, t thick, along the crossmember from one rail's
inner face to the other's, loaded on its bottom edge by the run's force spread evenly along the run, with the bottom
wall's share beside the web as a bar along that edge. The web is held along a line over it where the beam takes the
load, and the run's stiffness is its force over the web's mean deflection under it (work conjugate). The bounds of
what the model cannot know: the web held at the top wall's mid-plane, so the whole depth stretches (the soft bound), or
at the beam's axis, half-way up, so half of it does (the stiff bound), each with the crossmember's ends held at the
rails. Where two webs stand together, as at the middle seam of two RHS seam welded side by side, t is both.

Bilinear plane-stress rectangles (Q4, 2 x 2 Gauss points), E 200 GPa, nu 0.3. A check: a strip held along its top edge
and pulled evenly along its whole bottom edge stretches by P h / (E t L), which the model gives to 0.1 %."""
from __future__ import annotations

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu

E, NU = 200_000.0, 0.3


def _q4(hy: float, hz: float, t: float) -> np.ndarray:
    """The 8 x 8 plane-stress stiffness of an hy x hz rectangle t thick, nodes (0,0), (1,0), (1,1), (0,1), each (uy, uz)."""
    D = E / (1 - NU ** 2) * np.array([[1, NU, 0], [NU, 1, 0], [0, 0, (1 - NU) / 2]])
    k = np.zeros((8, 8))
    g = 1 / np.sqrt(3)
    for xi in (-g, g):
        for eta in (-g, g):
            dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)],
                                  [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
            dy, dz = dN[0] * 2 / hy, dN[1] * 2 / hz
            B = np.zeros((3, 8))
            B[0, 0::2], B[1, 1::2], B[2, 0::2], B[2, 1::2] = dy, dz, dz, dy
            k += B.T @ D @ B * t * hy * hz / 4
    return k


def model(span: float, height: float, t: float, flange: float, runs: list[tuple[float, float]], h: float = 4.0,
          hold: str = "both", ends: bool = True) -> list[float]:
    """Each run's stiffness, N/mm, on a web `span` long between the rails' inner faces and `height` from its bottom edge
    to the line it is held along (`hold` "both" ways or "up" and down only), t thick, with a bar of area `flange` along
    its bottom edge, under the run's force spread evenly over (y0, y1) on that edge, the ends held up and down at the
    rails unless `ends` is False."""
    ny, nz = max(round(span / h), 1), max(round(height / h), 1)
    hy, hz = span / ny, height / nz
    nid = lambda i, j: j * (ny + 1) + i                                # noqa: E731
    n = (ny + 1) * (nz + 1)
    ke = _q4(hy, hz, t)
    rows, cols, vals = [], [], []
    for j in range(nz):
        for i in range(ny):
            nodes = (nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1))
            dofs = np.array([[2 * q, 2 * q + 1] for q in nodes]).ravel()
            rows.append(np.repeat(dofs, 8))
            cols.append(np.tile(dofs, 8))
            vals.append(ke.ravel())
    if flange:
        kb = E * flange / hy
        for i in range(ny):
            a, b = 2 * nid(i, 0), 2 * nid(i + 1, 0)
            rows.append(np.array([a, a, b, b]))
            cols.append(np.array([a, b, a, b]))
            vals.append(np.array([kb, -kb, -kb, kb]))
    K = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(2 * n, 2 * n)).tocsc()
    fixed = {2 * nid(i, nz) + 1 for i in range(ny + 1)} | ({2 * nid(i, j) + 1 for j in range(nz + 1) for i in (0, ny)} if ends else set())
    if hold == "both":
        fixed |= {2 * nid(i, nz) for i in range(ny + 1)}
    else:
        fixed.add(2 * nid(0, nz))
    free = np.array(sorted(set(range(2 * n)) - fixed))
    lu = splu(K[free][:, free])
    ys = np.linspace(0.0, span, ny + 1)
    out = []
    for y0, y1 in runs:
        f = np.zeros(2 * n)
        for i in range(ny):                                            # each element's share of the line load, by overlap
            a, b = max(ys[i], y0), min(ys[i + 1], y1)
            if b > a:
                for q, w in ((i, (ys[i + 1] - (a + b) / 2) / hy), (i + 1, ((a + b) / 2 - ys[i]) / hy)):
                    f[2 * nid(q, 0) + 1] -= (b - a) / (y1 - y0) * w
        u = np.zeros(2 * n)
        u[free] = lu.solve(f[free])
        out.append(1.0 / float(f @ u))
    return out


def check_strip() -> float:
    """A strip held along its top edge and pulled evenly along its whole bottom edge: the model's stiffness over the
    stretch's E t L / h, its ends free and no bar, which a uniform stress gives exactly."""
    span, height, t = 400.0, 100.0, 6.0
    k = model(span, height, t, 0.0, [(0.0, span)], h=5.0, hold="up", ends=False)[0]
    return k / (E * t * span / height)
