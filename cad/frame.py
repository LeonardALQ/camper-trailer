"""Linear 3D frame solver by the direct stiffness method (numpy), for the chassis analysis (CHASSIS.md).

Units: N, mm, MPa. Each element is a straight Euler-Bernoulli beam with 6 degrees of freedom at each end
(three translations, three rotations). Its local x axis runs from node i to node j. Local z is the section's
depth direction, so `Iz_depth` (bending in the x-z plane, curvature across the depth) is the section's strong
axis Ix, and `Iy_width` (bending in the x-y plane) is its weak axis Iy. Shear deformation is ignored.

cad/tests/test_frame.py checks the solver against closed-form results.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

E_STEEL = 200_000.0
G_STEEL = 80_000.0


@dataclass(frozen=True)
class Section:
    name: str
    A: float           # mm2
    I_strong: float    # mm4, bending across the depth (about the section's x axis)
    I_weak: float      # mm4, bending across the width (about the section's y axis)
    J: float           # mm4, torsion constant
    rigid: bool = False


RIGID = Section("rigid link", A=1.0e5, I_strong=1.0e10, I_weak=1.0e10, J=1.0e10, rigid=True)


@dataclass
class Element:
    i: int
    j: int
    sec: Section
    depth_dir: tuple[float, float, float]
    member: str
    E: float = E_STEEL
    G: float = G_STEEL

    def axes(self, xyz: np.ndarray) -> tuple[np.ndarray, float]:
        """Rows are the local x, y and z unit vectors in global coordinates."""
        d = xyz[self.j] - xyz[self.i]
        L = float(np.linalg.norm(d))
        ex = d / L
        ref = np.asarray(self.depth_dir, dtype=float)
        ez = ref - ref.dot(ex) * ex
        if np.linalg.norm(ez) < 1e-9:
            raise ValueError(f"{self.member}: depth direction is parallel to the element axis")
        ez /= np.linalg.norm(ez)
        ey = np.cross(ez, ex)
        return np.vstack([ex, ey, ez]), L

    def k_local(self, L: float) -> np.ndarray:
        s, E, G = self.sec, self.E, self.G
        k = np.zeros((12, 12))
        ea, gj = E * s.A / L, G * s.J / L
        k[0, 0] = k[6, 6] = ea
        k[0, 6] = k[6, 0] = -ea
        k[3, 3] = k[9, 9] = gj
        k[3, 9] = k[9, 3] = -gj
        # bending in the x-y plane (displacement v, rotation about z) uses the weak axis
        self._bend(k, 1, 5, 7, 11, E * s.I_weak, L, sign=1.0)
        # bending in the x-z plane (displacement w, rotation about y) uses the strong axis
        self._bend(k, 2, 4, 8, 10, E * s.I_strong, L, sign=-1.0)
        return k

    @staticmethod
    def _bend(k, v1, r1, v2, r2, EI, L, sign):
        a, b, c, d = 12 * EI / L ** 3, 6 * EI / L ** 2, 4 * EI / L, 2 * EI / L
        b *= sign
        idx = [v1, r1, v2, r2]
        m = np.array([[a, b, -a, b], [b, c, -b, d], [-a, -b, a, -b], [b, d, -b, c]])
        for p in range(4):
            for q in range(4):
                k[idx[p], idx[q]] += m[p, q]


@dataclass
class Result:
    u: np.ndarray                    # nodal displacements, 6 per node
    reactions: dict[tuple[int, int], float]
    forces: list[np.ndarray]         # element end forces in local axes, 12 each (on the element, at i then j)


@dataclass
class Frame:
    nodes: list[tuple[float, float, float]] = field(default_factory=list)
    elements: list[Element] = field(default_factory=list)
    tags: dict[str, int] = field(default_factory=dict)

    def node(self, p, tag: str | None = None, tol: float = 0.5) -> int:
        """Index of the node at p, created if no node lies within tol."""
        p = tuple(float(v) for v in p)
        for k, q in enumerate(self.nodes):
            if abs(q[0] - p[0]) < tol and abs(q[1] - p[1]) < tol and abs(q[2] - p[2]) < tol:
                if tag:
                    self.tags[tag] = k
                return k
        self.nodes.append(p)
        if tag:
            self.tags[tag] = len(self.nodes) - 1
        return len(self.nodes) - 1

    def add(self, i: int, j: int, sec: Section, depth_dir, member: str) -> Element:
        el = Element(i, j, sec, tuple(depth_dir), member)
        self.elements.append(el)
        return el

    def chain(self, points, sec: Section, depth_dir, member: str) -> list[int]:
        """Elements along a polyline of points, one element per segment. Returns the node indices."""
        idx = [self.node(p) for p in points]
        for a, b in zip(idx, idx[1:]):
            self.add(a, b, sec, depth_dir, member)
        return idx

    def solve(self, loads: np.ndarray, supports: list[tuple[int, int]]) -> Result:
        """loads: 6 n vector of nodal forces and moments. supports: (node, dof) pairs held at zero displacement."""
        return self.prepare(supports).solve(loads)

    def prepare(self, supports: list[tuple[int, int]]) -> "Solver":
        """Assemble and factorise once for a set of supports, then solve any number of load vectors."""
        return Solver(self, supports)


class Solver:
    def __init__(self, frame: Frame, supports: list[tuple[int, int]]):
        from scipy.linalg import lu_factor
        xyz = np.asarray(frame.nodes)
        n = 6 * len(frame.nodes)
        K = np.zeros((n, n))
        self.cache = []
        for el in frame.elements:
            R, L = el.axes(xyz)
            T = np.zeros((12, 12))
            for b in range(4):
                T[3 * b:3 * b + 3, 3 * b:3 * b + 3] = R
            kl = el.k_local(L)
            dofs = np.r_[6 * el.i:6 * el.i + 6, 6 * el.j:6 * el.j + 6]
            K[np.ix_(dofs, dofs)] += T.T @ kl @ T
            self.cache.append((T, kl, dofs))
        self.K, self.n, self.supports = K, n, list(supports)
        fixed = sorted({6 * nd + d for nd, d in supports})
        self.free = np.setdiff1d(np.arange(n), fixed)
        self.lu = lu_factor(K[np.ix_(self.free, self.free)])

    def solve(self, loads: np.ndarray) -> Result:
        from scipy.linalg import lu_solve
        u = np.zeros(self.n)
        u[self.free] = lu_solve(self.lu, loads[self.free])
        r = self.K @ u - loads
        reactions = {(nd, d): float(r[6 * nd + d]) for nd, d in self.supports}
        forces = [kl @ (T @ u[dofs]) for T, kl, dofs in self.cache]
        return Result(u, reactions, forces)


def end_actions(f: np.ndarray) -> list[dict[str, float]]:
    """Internal actions at the two element ends from its local end forces: N (tension +), V and M about the
    local y and z axes, and T. At end j the sign is that of the force on the element, at end i it is negated, so
    each value reads as the action the element carries at that end."""
    out = []
    for k, s in ((0, -1.0), (6, 1.0)):
        out.append(dict(N=s * f[k], Vy=s * f[k + 1], Vz=s * f[k + 2], T=s * f[k + 3], My=s * f[k + 4], Mz=s * f[k + 5]))
    return out
