"""The hinge crossmember's bottom wall under the hinge bar's front fillets (xt_hinges `bar` `wall`, CHS-18, FAT-24).

On RHS 150 x 100 x 6 each run's front fillet stands on the bottom wall's flat at the middle of its width, so the wall
bends under it. The wall is a plate, part of the closed section: its edges are held by the section's corners and webs,
and the webs by the top wall. Take each wall as a plate strip along the crossmember and unfold the section about its
corners. The frame model's beam carries the section's own bending and twist, so what is left is the section's change of
shape: with the walls stiff in their own planes the corners do not move, and a rigid corner turns both walls meeting in
it by the same angle. Unfolded, the four walls are one plate continuous over line supports at the corners. The front
fillet stands on the section's plane of symmetry, half-way between the webs, so half the perimeter is modelled, from
the bottom wall's middle (the fillet's line) round the front corner and up the front web to the top wall's middle, with
no slope across either middle line. Along the crossmember the plate runs from one rail's inner face to the other's.

The plate is solved by Bogner-Fox-Schmit rectangles (w, w_s, w_y, w_sy at each node, exact in pure bending), Kirchhoff
plates, E 200 GPa, nu 0.3. Each run's stiffness is the force a rigid run of the bar's length pushes into the wall per mm
of the wall's deflection under it, the bar being some 40 times stiffer than the wall over 80 mm. The bounds of what the
model cannot know: the corners at the walls' mid-planes, spans b - t and d - t (the soft bound), or at the ends of the
flats, b - 2 ro and d - 2 ro, the corners taken as points (the stiff bound), and the crossmember's ends welded to the
rails' 4 mm webs pinned or clamped. The filler under each front cheek, which stands under the outer run's front half and
ties the wall to the bar near the rail, is left out of both, on the soft side."""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu

E, NU = 200_000.0, 0.3


def _hermite(h: float, xi: np.ndarray):
    """The 1D Hermite cubics on an element `h` long at the points xi in [0, 1]: values, first and second derivatives
    along the element, each (4, n) for (w at 0, slope at 0, w at h, slope at h)."""
    N = np.array([1 - 3 * xi ** 2 + 2 * xi ** 3, h * (xi - 2 * xi ** 2 + xi ** 3), 3 * xi ** 2 - 2 * xi ** 3, h * (-xi ** 2 + xi ** 3)])
    d1 = np.array([-6 * xi + 6 * xi ** 2, h * (1 - 4 * xi + 3 * xi ** 2), 6 * xi - 6 * xi ** 2, h * (-2 * xi + 3 * xi ** 2)]) / h
    d2 = np.array([-6 + 12 * xi, h * (-4 + 6 * xi), 6 - 12 * xi, h * (-2 + 6 * xi)]) / h ** 2
    return N, d1, d2


# local dof order: node (i, j) with i, j in {0, 1} along s and y, each node (w, w_s, w_y, w_sy). In the 1D functions the
# index for node i along a direction is 2 i (value) or 2 i + 1 (slope).
_NODES = ((0, 0), (1, 0), (1, 1), (0, 1))
_DOF = [(2 * i + a, 2 * j + b) for i, j in _NODES for a, b in ((0, 0), (1, 0), (0, 1), (1, 1))]


def _curvatures(hs: float, hy: float, xi: np.ndarray, eta: np.ndarray):
    """B rows (w_ss, w_yy, 2 w_sy) of the 16 element dofs at points (xi, eta), each (16, n)."""
    Ns, s1, s2 = _hermite(hs, xi)
    Ny, y1, y2 = _hermite(hy, eta)
    wss = np.array([s2[a] * Ny[b] for a, b in _DOF])
    wyy = np.array([Ns[a] * y2[b] for a, b in _DOF])
    wsy = np.array([2 * s1[a] * y1[b] for a, b in _DOF])
    return wss, wyy, wsy


@lru_cache(maxsize=None)
def _element(hs: float, hy: float, t: float) -> np.ndarray:
    """The 16 x 16 bending stiffness of an hs x hy rectangle of a plate t thick, 4 x 4 Gauss points."""
    g, wg = np.polynomial.legendre.leggauss(4)
    g, wg = (g + 1) / 2, wg / 2
    XI, ETA = np.meshgrid(g, g, indexing="ij")
    W = np.outer(wg, wg).ravel() * hs * hy
    wss, wyy, wsy = _curvatures(hs, hy, XI.ravel(), ETA.ravel())
    D = E * t ** 3 / (12 * (1 - NU ** 2))
    Dm = D * np.array([[1, NU, 0], [NU, 1, 0], [0, 0, (1 - NU) / 2]])
    B = np.stack([wss, wyy, wsy])                    # (3, 16, n)
    return np.einsum("ian,ij,jbn,n->ab", B, Dm, B, W)


def _grid(breaks: list[float], h: float) -> np.ndarray:
    """Node coordinates through every break, each stretch cut into equal elements no longer than h."""
    xs = [breaks[0]]
    for a, b in zip(breaks, breaks[1:]):
        n = max(1, math.ceil((b - a) / h - 1e-9))
        xs += list(np.linspace(a, b, n + 1)[1:])
    return np.array(xs)


class Plate:
    """The plate on a grid of nodes `s_nodes` x `y_nodes`, `t` thick, its dofs in `fixed` held at zero, factorised once."""

    def __init__(self, s_nodes, y_nodes, t: float, fixed: set, t_until: tuple[float, float] | None = None):
        """`t_until` (thickness, s) makes the plate that thick from s = 0 to s, a seat plate's bending in place of the
        wall's (the study of CHASSIS.md item 15)."""
        self.s, self.y, self.t = s_nodes, y_nodes, t
        self.t_of = t_of = lambda i: t_until[0] if t_until and s_nodes[i + 1] <= t_until[1] + 1e-9 else t
        ns, ny = len(s_nodes), len(y_nodes)
        self.nid = lambda i, j: i * ny + j
        rows, cols, vals = [], [], []
        for i in range(ns - 1):
            for j in range(ny - 1):
                ke = _element(round(s_nodes[i + 1] - s_nodes[i], 9), round(y_nodes[j + 1] - y_nodes[j], 9), t_of(i))
                dofs = np.array([4 * self.nid(i + a, j + b) + k for a, b in _NODES for k in range(4)])
                rows.append(np.repeat(dofs, 16))
                cols.append(np.tile(dofs, 16))
                vals.append(ke.ravel())
        self.n = 4 * ns * ny
        K = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(self.n, self.n)).tocsc()
        fix = np.array(sorted(4 * nd + k for nd, k in fixed), dtype=int)
        self.free = np.setdiff1d(np.arange(self.n), fix)
        self.lu = splu(K[self.free][:, self.free].tocsc())

    def solve(self, f: np.ndarray) -> np.ndarray:
        u = np.zeros(self.n)
        u[self.free] = self.lu.solve(f[self.free])
        return u.reshape(-1, 4)

    def line_load(self, i: int, y0: float, y1: float, total: float) -> np.ndarray:
        """Consistent nodal loads of `total` N spread evenly along node line s_nodes[i] from y0 to y1, both on nodes."""
        f = np.zeros(self.n)
        q = total / (y1 - y0)
        for j in range(len(self.y) - 1):
            a, b = self.y[j], self.y[j + 1]
            if a >= y0 - 1e-6 and b <= y1 + 1e-6:
                h = b - a
                for nd, (fw, fm) in ((self.nid(i, j), (q * h / 2, q * h * h / 12)), (self.nid(i, j + 1), (q * h / 2, -q * h * h / 12))):
                    f[4 * nd] += fw
                    f[4 * nd + 2] += fm
        return f

    def mean_w(self, u: np.ndarray, i: int, y0: float, y1: float) -> float:
        """The mean deflection along node line s_nodes[i] from y0 to y1, both on nodes."""
        tot = 0.0
        for j in range(len(self.y) - 1):
            a, b = self.y[j], self.y[j + 1]
            if a >= y0 - 1e-6 and b <= y1 + 1e-6:
                h = b - a
                w0, wy0 = u[self.nid(i, j)][[0, 2]]
                w1, wy1 = u[self.nid(i, j + 1)][[0, 2]]
                tot += h / 2 * (w0 + w1) + h * h / 12 * (wy0 - wy1)
        return tot / (y1 - y0)

    def moment_s(self, u: np.ndarray, s: float, y_lo: float, y_hi: float) -> float:
        """The largest bending moment across the s direction (N mm per mm) on the line at s, for y from y_lo to y_hi."""
        i0 = min(int(np.searchsorted(self.s, s, side="right")) - 1, len(self.s) - 2)
        D = E * self.t_of(i0) ** 3 / (12 * (1 - NU ** 2))
        hs = self.s[i0 + 1] - self.s[i0]
        xi = np.array([(s - self.s[i0]) / hs])
        best = 0.0
        for j in range(len(self.y) - 1):
            if self.y[j + 1] < y_lo - 1e-6 or self.y[j] > y_hi + 1e-6:
                continue
            hy = self.y[j + 1] - self.y[j]
            ue = np.concatenate([u[self.nid(i0 + a, j + b)] for a, b in _NODES])
            for eta in (0.0, 0.25, 0.5, 0.75, 1.0):
                wss, wyy, _ = _curvatures(hs, hy, xi, np.array([eta]))
                best = max(best, abs(D * (ue @ wss[:, 0] + NU * ue @ wyy[:, 0])))
        return best


SHARES = (1 / 6, 2 / 3, 1 / 6)          # the frame model's weld points at each run's ends and centre (FrameModel._weld_runs)


def model(sec, length: float, runs: list[tuple[float, float]], corners: str = "mid", ends: str = "pinned", h: float = 4.0,
          toe: float = 6.0, seat: float | None = None) -> dict:
    """The wall under the hinge bar's front fillet, for an RHS `sec` (b the width of the wall the fillets stand on, d the
    webs' depth, t, ro) `length` mm between the rails' inner faces, `runs` as (y0, y1) from one rail's face. Each run's
    fillet is three line loads, its stretches at the frame model's weld points (SHARES). The run's flexibility C, each
    stretch's mean deflection under 1 N on each, gives under a rigid bar, which moves the three alike, the force each
    stretch takes per mm, `points` (N/mm, C^-1 times ones), and `k` their sum, the run's stiffness. `uniform` is the run's
    stiffness under its load spread evenly, on the soft side of `k`. `hot_spot` is the structural stress across the wall
    at the fillet's toe, `toe` mm from its line, under the rigid bar's spread, per N of the run's force (MPa per N).
    `corners` "mid" or "flat" and `ends` "pinned" or "clamped" are the bounds (see the module)."""
    if corners == "mid":
        half, web = (sec.b - sec.t) / 2, sec.d - sec.t
    else:
        half, web = (sec.b - 2 * sec.ro) / 2, sec.d - 2 * sec.ro
    S = 2 * half + web                                  # half the unfolded perimeter
    s_nodes = _grid([0.0, toe, half, half + web, S], h)
    cuts = [v for y0, y1 in runs for v in (y0, y0 + SHARES[0] * (y1 - y0), y1 - SHARES[2] * (y1 - y0), y1)]
    y_nodes = _grid(sorted({0.0, length, *cuts}), h)
    ns, ny = len(s_nodes), len(y_nodes)
    nid = lambda i, j: i * ny + j
    i_sup = [int(np.argmin(abs(s_nodes - v))) for v in (half, half + web)]
    fixed = set()
    for j in range(ny):
        for i in (0, ns - 1):                           # no slope across either middle line
            fixed |= {(nid(i, j), 1), (nid(i, j), 3)}
        for i in i_sup:                                 # the corners hold the walls' deflection along them
            fixed |= {(nid(i, j), 0), (nid(i, j), 2)}
    for j in (0, ny - 1):                               # the ends at the rails' webs
        for i in range(ns):
            fixed |= {(nid(i, j), 0), (nid(i, j), 1)}
            if ends == "clamped":
                fixed |= {(nid(i, j), 2), (nid(i, j), 3)}
    pl = Plate(s_nodes, y_nodes, sec.t, fixed, (seat, half) if seat else None)
    out = []
    for y0, y1 in runs:
        st = [y0, y0 + SHARES[0] * (y1 - y0), y1 - SHARES[2] * (y1 - y0), y1]
        segs = list(zip(st, st[1:]))
        # 1 N on the whole section is half a newton on the half modelled
        us = [pl.solve(pl.line_load(0, a, b, 0.5)) for a, b in segs]
        C = np.array([[pl.mean_w(u, 0, a, b) for u in us] for a, b in segs])
        pts = np.linalg.solve(C, np.ones(3))
        u_bar = sum(p * u for p, u in zip(pts, us))
        u_even = pl.solve(pl.line_load(0, y0, y1, 0.5))
        m = pl.moment_s(u_bar, toe, y0 - 10, y1 + 10)
        m_even = pl.moment_s(u_even, toe, y0 - 10, y1 + 10)
        tb = seat or sec.t
        out.append(dict(y0=y0, y1=y1, points=[float(p) for p in pts], k=float(pts.sum()),
                        uniform=float(1.0 / pl.mean_w(u_even, 0, y0, y1)), hot_spot=float(6 * m / tb ** 2 / pts.sum()),
                        hot_even=float(6 * m_even / tb ** 2)))
    return dict(corners=corners, ends=ends, h=h, S=S, half=half, web=web, runs=out)


def bounds(sec, length: float, runs: list[tuple[float, float]], h: float = 4.0) -> dict:
    """The model on each corner and end bound, keyed "corners/ends"."""
    return {f"{c}/{e}": model(sec, length, runs, c, e, h) for c in ("mid", "flat") for e in ("pinned", "clamped")}


def check_square_plate(a: float = 100.0, t: float = 6.0, h: float = 2.5) -> float:
    """Timoshenko and Woinowsky-Krieger's Table 23: a simply supported square plate under a central point load deflects
    0.01160 P a^2 / D. Returns the model's coefficient, for the test."""
    s_nodes = _grid([0.0, a / 2, a], h)
    y_nodes = _grid([0.0, a / 2, a], h)
    ns, ny = len(s_nodes), len(y_nodes)
    nid = lambda i, j: i * ny + j
    fixed = set()
    for j in range(ny):
        for i in (0, ns - 1):
            fixed |= {(nid(i, j), 0), (nid(i, j), 2)}
    for i in range(ns):
        for j in (0, ny - 1):
            fixed |= {(nid(i, j), 0), (nid(i, j), 1)}
    pl = Plate(s_nodes, y_nodes, t, fixed)
    c = nid(int(np.argmin(abs(s_nodes - a / 2))), int(np.argmin(abs(y_nodes - a / 2))))
    f = np.zeros(pl.n)
    f[4 * c] = 1.0
    u = pl.solve(f)
    return u[c, 0] * E * t ** 3 / (12 * (1 - NU ** 2)) / a ** 2
