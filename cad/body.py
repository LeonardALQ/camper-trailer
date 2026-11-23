"""Body design to planning level (BODY.md): sandwich panel, insert, joint, mount, end wall, roof joint and twist
checks for the body in the trailer layout (cad/trailer.py), from data/body/body.yaml and research report 12.

Revision B (20 Nov 2026) is the body for the LandCruiser 79: 4,420 mm long with a fixed roof bonded to the walls, a
full rear wall and no garage. The bike wheel, chock, L-track and generator loads left the body with the garage, so a
person's foot governs the floor. The rear wall replaces the garage portal as the box's rear diaphragm.
"""
from __future__ import annotations

import math
from functools import cached_property

import numpy as np
import yaml

from .partsdb import DATA

BODY_YAML = DATA / "body" / "body.yaml"
G = 9.81
MOUNTED = ("body", "roof", "bed", "living", "payload", "electrical", "hvac", "wet_room")   # systems on the body (the drawbar box is on the drawbar)


def load_data() -> dict:
    return yaml.safe_load(BODY_YAML.read_text())


def side_projections(lay) -> list[dict]:
    """What stands proud of the side walls' outer skins, as Y extents in DIM-01, for the overall width (DIM-01, DIM-05):
    each side-wall opening's `proj` (data/body/body.yaml), each side-wall gland's (data/services.yaml) and the joiners
    along both edges. The side marker lamps and reflectors are left out, as ADR 43/04's definition and VSB1 5.2 leave out
    lamps and reflectors."""
    d, V = load_data(), lay.V
    hb = V["half_bw"]
    glands = yaml.safe_load((DATA / "services.yaml").read_text())["glands"]
    out = [dict(name="floor and roof-to-wall joiners", wall=s, proj=d["width"]["joiner_proj"]) for s in ("kerb", "road")]
    out += [dict(name=o["name"], wall=o["wall"], proj=o["proj"], id=o["id"]) for o in d["openings"] if o.get("proj")]
    out += [dict(name=g["what"], wall=g["at"], proj=g["proj"], id=g["id"]) for g in glands if g.get("proj")]
    for p in out:
        s = 1 if p["wall"] == "road" else -1
        p["y0"], p["y1"] = sorted((s * hb, s * (hb + p["proj"])))
    return out


def _wall_section(th: dict, t_out: float, core: float, t_in: float, member: dict | None, x_c: float = 0.0,
                  insert: dict | None = None, window: dict | None = None) -> dict:
    """Steady conduction in a half strip of the side wall, `th["strip_mm"]` wide, at one member on the inner skin (or
    none), per metre of member length. Cells of `th["cell_mm"]`: x along the wall from a symmetry plane, y through the
    wall from the outer face. The member's centre stands `x_c` from that plane, so x_c above zero models a pair of
    members 2 x_c apart. An `insert` (w, k) fills the core beside the member's far edge, and a `window` (U) takes the
    rest of the strip as one material through the wall's thickness with that U-value on ISO 6946's films. The outer and
    inner faces lose heat through Rse and Rsi, and the strip's far edge is adiabatic. Returns the coldest inside surface
    over the wall (the window's own surface left out), the member's coldest cell and the heat through the strip, W per
    metre of member."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    h, kk = th["cell_mm"], th["k"]
    depth = t_out + core + t_in
    nx, ny = round(th["strip_mm"] / h), round(depth / h)
    y = (np.arange(ny) + 0.5) * h
    x = (np.arange(nx) + 0.5) * h
    Y, X = np.meshgrid(y, x, indexing="ij")
    k = np.full((ny, nx), kk["xps"])
    k[Y < t_out] = kk["grp"]
    k[Y > depth - t_in] = kk["grp"]
    al = np.zeros((ny, nx), dtype=bool)
    wall_cols = np.ones(nx, dtype=bool)
    if member:
        y1 = depth - t_in
        y0 = y1 - member["depth"]
        half, t = member["width"] / 2, member["wall"]
        al = (abs(X - x_c) < half) & (Y > y0) & (Y < y1)
        k[al] = kk["aluminium"]
        k[(abs(X - x_c) < half - t) & (Y > y0 + t) & (Y < y1 - t)] = kk["air"]
        al &= k == kk["aluminium"]
        edge = x_c + half
        if insert:
            k[(X > edge) & (X < edge + insert["w"]) & (Y > t_out) & (Y < depth - t_in)] = insert["k"]
            edge += insert["w"]
        if window:
            k[:, x > edge] = depth / 1000 / (1 / window["U"] - th["rsi_heat"] - th["rse"])
            wall_cols = x < edge
    idx = np.arange(nx * ny).reshape(ny, nx)
    hm = h / 1000.0
    rows, cols, vals = [], [], []
    diag = np.zeros(nx * ny)
    for a, b in ((k[:, :-1], k[:, 1:]), (k[:-1, :], k[1:, :])):
        g = (2 * a * b / (a + b)).ravel()                         # W/K per metre of member between neighbouring cells
        i, j = ((idx[:, :-1], idx[:, 1:]) if a.shape[1] == nx - 1 else (idx[:-1, :], idx[1:, :]))
        i, j = i.ravel(), j.ravel()
        rows += [i, j]
        cols += [j, i]
        vals += [-g, -g]
        np.add.at(diag, i, g)
        np.add.at(diag, j, g)
    g_out = hm / (th["rse"] + hm / 2 / k[0, :])                   # outer face, per column
    g_in = hm / (th["rsi"] + hm / 2 / k[-1, :])                   # inner face, per column
    rhs = np.zeros(nx * ny)
    np.add.at(diag, idx[0, :], g_out)
    np.add.at(diag, idx[-1, :], g_in)
    rhs[idx[0, :]] += g_out * th["t_out"]
    rhs[idx[-1, :]] += g_in * th["t_in"]
    A = sp.csr_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(nx * ny)]),
                                                        np.concatenate(cols + [np.arange(nx * ny)]))), shape=(nx * ny, nx * ny))
    T = spsolve(A.tocsc(), rhs).reshape(ny, nx)
    q_in = g_in * (th["t_in"] - T[-1, :])                         # W per metre of member through each column's inner face
    tsi = th["t_in"] - q_in / hm * th["rsi"]
    return dict(tsi_min=float(tsi[wall_cols].min()), t_member=float(T[al].min()) if al.any() else None, q_w_m=float(q_in.sum()))


def _wall_line(th: dict, t_out: float, core: float, t_in: float, member: dict, others: list, inserts: list, holes: list) -> dict:
    """Steady conduction across the side wall, `th["strip_mm"]` each side of one member on the inner skin, as built
    around it: the other members near it (their centres, mm from this one's), the insert strips (x0, x1, k) that fill
    the core and the openings beyond them (x0, x1, U), each taken through the wall's thickness as one material with its
    U-value on ISO 6946's films. Both ends adiabatic. Every neighbour is taken at the section's height, though a window
    covers only part of the member's length, so this is a bound. Returns the coldest inside surface over the member."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    h, kk = th["cell_mm"], th["k"]
    depth = t_out + core + t_in
    L = th["strip_mm"]
    nx, ny = round(2 * L / h), round(depth / h)
    y = (np.arange(ny) + 0.5) * h
    x = (np.arange(nx) + 0.5) * h - L
    Y, X = np.meshgrid(y, x, indexing="ij")
    k = np.full((ny, nx), kk["xps"])
    k[Y < t_out] = kk["grp"]
    k[Y > depth - t_in] = kk["grp"]
    y1 = depth - t_in
    y0 = y1 - member["depth"]
    half, t = member["width"] / 2, member["wall"]
    for xc in [0.0] + list(others):
        box = (abs(X - xc) < half) & (Y > y0) & (Y < y1)
        k[box] = kk["aluminium"]
        k[(abs(X - xc) < half - t) & (Y > y0 + t) & (Y < y1 - t)] = kk["air"]
    for ins in inserts:                                # (x0, x1, k), through the core, or (x0, x1, k, "channel"), the members' depth only
        a, c, kv = ins[:3]
        k[(X > a) & (X < c) & (((Y > y0) & (Y < y1)) if len(ins) > 3 else ((Y > t_out) & (Y < depth - t_in)))] = kv
    over = abs(x) < half
    for a, c, U in holes:
        k[:, (x > a) & (x < c)] = depth / 1000 / (1 / U - th["rsi_heat"] - th["rse"])
    idx = np.arange(nx * ny).reshape(ny, nx)
    hm = h / 1000.0
    rows, cols, vals = [], [], []
    diag = np.zeros(nx * ny)
    for a, b in ((k[:, :-1], k[:, 1:]), (k[:-1, :], k[1:, :])):
        g = (2 * a * b / (a + b)).ravel()
        i, j = ((idx[:, :-1], idx[:, 1:]) if a.shape[1] == nx - 1 else (idx[:-1, :], idx[1:, :]))
        i, j = i.ravel(), j.ravel()
        rows += [i, j]
        cols += [j, i]
        vals += [-g, -g]
        np.add.at(diag, i, g)
        np.add.at(diag, j, g)
    g_out = hm / (th["rse"] + hm / 2 / k[0, :])
    g_in = hm / (th["rsi"] + hm / 2 / k[-1, :])
    rhs = np.zeros(nx * ny)
    np.add.at(diag, idx[0, :], g_out)
    np.add.at(diag, idx[-1, :], g_in)
    rhs[idx[0, :]] += g_out * th["t_out"]
    rhs[idx[-1, :]] += g_in * th["t_in"]
    A = sp.csr_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(nx * ny)]),
                                                        np.concatenate(cols + [np.arange(nx * ny)]))), shape=(nx * ny, nx * ny))
    T = spsolve(A.tocsc(), rhs).reshape(ny, nx)
    tsi = th["t_in"] - g_in * (th["t_in"] - T[-1, :]) / hm * th["rsi"]
    return dict(tsi=float(tsi[over].min()))


def _plate_k(a: float, b: float, D: float, nu: float, S: float) -> np.ndarray:
    """Stiffness of an a x b rectangle of a Mindlin plate, the MITC4 element of Bathe and Dvorkin (1985), whose transverse
    shear is sampled at the edge midpoints so a thin plate does not lock. DOFs per node (w, rotation x, rotation y), the
    nodes anticlockwise from (0, 0). Bending on 2 x 2 Gauss points with D (N mm), shear with S (N/mm)."""
    Db = D * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    xi_n, et_n = np.array([-1, 1, 1, -1]), np.array([-1, -1, 1, 1])
    K = np.zeros((12, 12))
    g = 1 / math.sqrt(3)
    for xi in (-g, g):
        for et in (-g, g):
            B = np.zeros((3, 12))
            B[0, 1::3] = xi_n * (1 + et_n * et) / (2 * a)
            B[1, 2::3] = et_n * (1 + xi_n * xi) / (2 * b)
            B[2, 1::3], B[2, 2::3] = B[1, 2::3], B[0, 1::3]
            K += B.T @ Db @ B * a * b / 4

    def strain(n0, n1, length, rot):
        r = np.zeros(12)
        r[3 * n0], r[3 * n1] = -1 / length, 1 / length
        r[3 * n0 + rot] = r[3 * n1 + rot] = 0.5
        return r
    for p, q in ((strain(0, 1, a, 1), strain(3, 2, a, 1)), (strain(0, 3, b, 2), strain(1, 2, b, 2))):
        K += S * a * b / 3 * (np.outer(p, p) + np.outer(q, q) + 0.5 * (np.outer(p, q) + np.outer(q, p)))
    return K


def _grid(lines, step: float) -> np.ndarray:
    """Grid coordinates through every line given, no wider apart than `step`."""
    lines = sorted({round(v, 3) for v in lines})
    out = [lines[0]]
    for a, b in zip(lines, lines[1:]):
        n = max(1, math.ceil((b - a) / step - 1e-9))
        out += [a + (b - a) * (i + 1) / n for i in range(n)]
    return np.array(out)


def _wall_plate(x0: float, x1: float, H: float, cuts: list, members: list, supports: list, panel, p: float, step: float,
                corner: float = 0.0) -> dict:
    """A side wall as a Mindlin plate (MITC4) at a uniform net pressure p (MPa), simply supported along the floor and roof
    joiners (z 0 and H) and the end walls (x0 and x1), and on each line in `supports` (x, z0, z1). `cuts` are the openings
    (u0, u1, z0, z1): their panel is left out and their own wind load goes to their edges by 45 degree lines, as a window
    or a door bears on its frame all round. `members` (x, z0, z1, EI, GA, GJ) are beams along their grid line with their
    own bending, shear and St Venant torsion, and its `ends` (z0, z1, EI, GA) are the blocks that carry its shear to the
    joiners. Returns the deflection field, each member's largest moment, line load and end shear, the plate's largest
    principal moment and its largest transverse shear per mm, both away from the cut-outs' corners (within `corner`), where a
    re-entrant corner concentrates it."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    clip = lambda v, lo, hi: min(max(v, lo), hi)  # noqa: E731
    X = _grid([x0, x1] + [clip(v, x0, x1) for c in cuts for v in c[:2]] + [m["x"] for m in members] + [s[0] for s in supports], step)
    Z = _grid([0, H] + [clip(v, 0, H) for c in cuts for v in c[2:]] + [v for m in members for v in (m["z0"], m["z1"])], step)
    nx, nz = len(X), len(Z)
    N = 3 * nx * nz
    node = lambda i, j: j * nx + i  # noqa: E731
    xc, zc = (X[:-1] + X[1:]) / 2, (Z[:-1] + Z[1:]) / 2
    rows, cols, vals, elems, cache = [], [], [], [], {}
    f = np.zeros(N)
    used = np.zeros(nx * nz, dtype=bool)
    for j in range(nz - 1):
        for i in range(nx - 1):
            if any(c[0] < xc[i] < c[1] and c[2] < zc[j] < c[3] for c in cuts):
                continue
            a, b = X[i + 1] - X[i], Z[j + 1] - Z[j]
            key = (round(a, 4), round(b, 4))
            if key not in cache:
                cache[key] = _plate_k(a, b, panel.D, panel.nu, panel.S)
            ns = [node(i, j), node(i + 1, j), node(i + 1, j + 1), node(i, j + 1)]
            dofs = np.array([3 * n + q for n in ns for q in range(3)])
            rows.append(np.repeat(dofs, 12))
            cols.append(np.tile(dofs, 12))
            vals.append(cache[key].ravel())
            f[3 * np.array(ns)] += p * a * b / 4
            used[ns] = True
            elems.append((a, b, dofs))
    for u0, u1, z0, z1 in cuts:                       # each opening's load to the nearest point of its nearest edge
        cu = np.linspace(u0, u1, max(2, int((u1 - u0) / 5)) + 1)
        cz = np.linspace(z0, z1, max(2, int((z1 - z0) / 5)) + 1)
        dA = (cu[1] - cu[0]) * (cz[1] - cz[0])
        CU, CZ = np.meshgrid((cu[:-1] + cu[1:]) / 2, (cz[:-1] + cz[1:]) / 2, indexing="ij")
        near = np.stack([CU - u0, u1 - CU, CZ - z0, z1 - CZ]).argmin(axis=0)
        for e, (at, vertical) in enumerate(((u0, True), (u1, True), (z0, False), (z1, False))):
            pos = (CZ if vertical else CU)[near == e]
            line, fixed = (Z, int(np.argmin(abs(X - at)))) if vertical else (X, int(np.argmin(abs(Z - at))))
            idx = np.clip(np.searchsorted(line, pos) - 1, 0, len(line) - 2)
            t = (pos - line[idx]) / (line[idx + 1] - line[idx])
            for sel, wgt in ((idx, 1 - t), (idx + 1, t)):
                ns = node(fixed, sel) if vertical else node(sel, fixed)
                np.add.at(f, 3 * ns, p * dA * wgt)
    beams = []
    for m in members:
        i = int(np.argmin(abs(X - m["x"])))
        for j in range(nz - 1):
            inside = Z[j] >= m["z0"] - 1e-6 and Z[j + 1] <= m["z1"] + 1e-6
            end = next((e for e in m.get("ends", []) if Z[j] >= e["z0"] - 1e-6 and Z[j + 1] <= e["z1"] + 1e-6), None)
            if not inside and end is None:
                continue
            seg = m if inside else dict(m, EI=end["EI"], GA=end["GA"], GJ=0.0, end=True)   # a block or pad at the member's end
            L = Z[j + 1] - Z[j]
            dofs = np.array([3 * node(i, j), 3 * node(i, j) + 1, 3 * node(i, j) + 2, 3 * node(i, j + 1), 3 * node(i, j + 1) + 1, 3 * node(i, j + 1) + 2])
            ke = np.zeros((6, 6))
            gv = np.array([-1 / L, 0, 0.5, 1 / L, 0, 0.5])             # the beam's shear, sampled at mid-length
            ke += seg["GA"] * L * np.outer(gv, gv)
            for q, stiff in ((2, seg["EI"]), (1, seg["GJ"])):               # bending on the y rotation, torsion on the x rotation
                ke[np.ix_([q, q + 3], [q, q + 3])] += stiff / L * np.array([[1, -1], [-1, 1]])
            rows.append(np.repeat(dofs, 6))
            cols.append(np.tile(dofs, 6))
            vals.append(ke.ravel())
            beams.append((seg, j, L, dofs))
    K = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
    fixed = np.repeat(~used, 3)
    w_dof = lambda i, j: 3 * node(i, j)  # noqa: E731
    for i in range(nx):
        fixed[w_dof(i, 0)] = fixed[w_dof(i, nz - 1)] = True
    for j in range(nz):
        fixed[w_dof(0, j)] = fixed[w_dof(nx - 1, j)] = True
    for xs, za, zb in supports:
        i = int(np.argmin(abs(X - xs)))
        for j in np.nonzero((Z >= za - 1e-6) & (Z <= zb + 1e-6))[0]:
            fixed[w_dof(i, j)] = True
    free = ~fixed
    u = np.zeros(N)
    u[free] = spsolve(K[free][:, free].tocsc(), f[free])
    w = np.where(used.reshape(nz, nx), u[0::3].reshape(nz, nx), 0.0)
    mem = {}
    for m, j, L, dofs in beams:
        M = m["EI"] * (u[dofs[5]] - u[dofs[2]]) / L
        V = m["GA"] * ((u[dofs[3]] - u[dofs[0]]) / L + (u[dofs[2]] + u[dofs[5]]) / 2)
        r = mem.setdefault(m["name"], dict(M=0.0, z=0.0, V=[], V_end=0.0))
        if m.get("end"):
            r["V_end"] = max(r["V_end"], abs(V))
            continue
        r["V"].append(((Z[j] + Z[j + 1]) / 2, V))
        if abs(M) > abs(r["M"]):
            r.update(M=M, z=(Z[j] + Z[j + 1]) / 2)
    for r in mem.values():                            # the member's line load: the change in its shear from one element to the next
        r["q"] = max((abs(v1 - v0) / (z1 - z0) for (z0, v0), (z1, v1) in zip(r["V"], r["V"][1:])), default=0.0)
        del r["V"]
    Db = panel.D * np.array([[1, panel.nu, 0], [panel.nu, 1, 0], [0, 0, (1 - panel.nu) / 2]])
    m_max = q_max = 0.0
    q_at = m_at = (0.0, 0.0)
    corners = [(cx, cz) for c in cuts for cx in c[:2] for cz in c[2:]]      # the core's shear left out next to a cut-out's corners
    sgn = np.array([-1, 1, 1, -1])
    for a, b, dofs in elems:
        ue = u[dofs]
        kx = ue[1::3] @ (sgn / (2 * a))
        ky = ue[2::3] @ (np.array([-1, -1, 1, 1]) / (2 * b))
        kxy = ue[1::3] @ (np.array([-1, -1, 1, 1]) / (2 * b)) + ue[2::3] @ (sgn / (2 * a))
        mx, my, mxy = Db @ np.array([kx, ky, kxy])
        mp = abs((mx + my) / 2) + math.hypot((mx - my) / 2, mxy)
        gx = (ue[3] - ue[0] + ue[6] - ue[9]) / (2 * a) + ue[1::3].mean()
        gy = (ue[9] - ue[0] + ue[6] - ue[3]) / (2 * b) + ue[2::3].mean()
        q = panel.S * math.hypot(gx, gy)
        xe, ze = float(X[dofs[0] // 3 % nx]) + a / 2, float(Z[dofs[0] // 3 // nx]) + b / 2
        if any(abs(xe - cx) < corner and abs(ze - cz) < corner for cx, cz in corners):
            continue                                  # F5-02: the skins and the core read away from the square-cut corners
        if mp > m_max:
            m_max, m_at = mp, (xe, ze)
        if q > q_max:
            q_max, q_at = q, (xe, ze)
    return dict(X=X, Z=Z, w=w, members=mem, m_max=m_max, m_at=m_at, q_max=q_max, q_at=q_at)


def _w_sat(t: float) -> float:
    """Saturation humidity ratio, g/kg, at t C and 101.3 kPa (Magnus, as research report 19's model)."""
    p = 0.61094 * math.exp(17.625 * t / (t + 243.04))
    return 622 * p / (101.325 - p)


def _dew(w: float) -> float:
    """Dew point, C, of air holding w g/kg."""
    lo, hi = -40.0, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _w_sat(mid) < w else (lo, mid)
    return lo


class Panel:
    def __init__(self, key: str, d: dict):
        self.key, self.d = key, d
        self.name = d["name"]
        self.t1, self.t2 = d["skins"]
        self.c = d["core"]["c"]
        self.dd = self.c + (self.t1 + self.t2) / 2          # skin centre spacing
        self.E, self.G, self.ult = d["E"], d["G"], d["ult"]
        self.nu = self.E / (2 * self.G) - 1                 # the skins taken as isotropic
        self.core = d["core"]
        st = d.get("stiffener")
        self.D_stiff = st["E"] * st["I"] / st["pitch"] if st else 0.0   # stiffeners smeared over their pitch, N mm2/mm

    @property
    def D(self) -> float:
        """Bending stiffness per mm width, N mm2/mm."""
        return self.E * self.t1 * self.t2 * self.dd ** 2 / (self.t1 + self.t2)

    @property
    def S(self) -> float:
        """Shear stiffness per mm width, N/mm."""
        return self.core["Gc"] * self.dd ** 2 / self.c

    @property
    def wrinkling(self) -> float:
        Ec = 2.5 * self.core["Gc"]                           # foam core, Ec about 2.5 Gc (assumption)
        return 0.5 * (self.E * Ec * self.core["Gc"]) ** (1 / 3)

    @property
    def Gt(self) -> float:
        """In-plane shear stiffness of the two skins, N/mm."""
        return self.G * (self.t1 + self.t2)

    def plate_gj(self, b: float) -> float:
        """Torsion constant times G of a strip of width b twisting on its own, N mm2 (open section)."""
        return b * self.G * min(self.t1, self.t2) * 2 * self.dd ** 2 / 2

    def one_way(self, P: float, patch_w: float, span: float, a: float | None = None) -> dict:
        """Point load P (N) on a one-way span between supports, `a` from the nearer support (midspan if None).
        Effective width = patch width + span / 2."""
        a = span / 2 if a is None else a
        b = patch_w + span / 2
        M = P * a * (span - a) / span
        V = P * max(a, span - a) / span
        sig = M / (min(self.t1, self.t2) * self.dd * b)
        tau = V / (self.dd * b)
        defl = P * a ** 2 * (span - a) ** 2 / (3 * self.D * b * span) + P * a * (span - a) / (self.S * b * span)
        return dict(M=M, V=V, b_eff=b, skin_mpa=sig, core_mpa=tau, defl_mm=defl)

    def uniform(self, w_mpa: float, span: float) -> dict:
        """Uniform pressure w (N/mm2) on a one-way strip, simply supported. The deflection counts the panel's own
        stiffeners, smeared over their pitch. The skin stress leaves them out."""
        M = w_mpa * span ** 2 / 8
        V = w_mpa * span / 2
        return dict(skin_mpa=M / (min(self.t1, self.t2) * self.dd), core_mpa=V / self.dd,
                    defl_mm=5 * w_mpa * span ** 4 / (384 * (self.D + self.D_stiff)) + w_mpa * span ** 2 / (8 * self.S))

    def utils(self, r: dict, crit: dict, compression: bool = True) -> dict:
        """Utilisations against report 12's criteria: skin at half its ultimate (and half the wrinkling stress when
        in compression), core shear at half its strength."""
        us = r["skin_mpa"] / (crit["skin_factor"] * self.ult)
        if compression:
            us = max(us, r["skin_mpa"] / (crit["wrinkling_factor"] * self.wrinkling))
        uc = r["core_mpa"] / (crit["core_factor"] * self.core["shear"])
        return dict(skin=us, core=uc, util=max(us, uc), governing="skin" if us >= uc else "core shear")


class Body:
    """The body checks for one layout of the trailer (cad/trailer.py)."""

    def __init__(self, lay, tr):
        self.lay, self.tr = lay, tr
        self.d = load_data()
        self.V = lay.V
        self.p = {k: Panel(k, v) for k, v in self.d["panels"].items()}
        self.crit = self.d["criteria"]
        V = self.V
        self.raiser_gap = 2 * (V["rail_c"] - V["rail_w"] / 2)        # between the raisers' inner faces
        self.raiser_span = 2 * V["rail_c"]                             # raiser centre to raiser centre
        self.edge_span = V["half_bw"] - V["wall_t"] / 2 - (V["rail_c"] + V["rail_w"] / 2)   # raiser face to the wall
        self.stations = sorted(lay.chassis.station_x(s) for s in lay.chassis.stations)

    # ------------------------------------------------------------------ what stands on the floor
    @cached_property
    def mounted(self) -> dict:
        """Mass on the body mounts per trailer case, scaled as the chassis analysis scales (heaviest case at the ATM)."""
        rows = {}
        for c in self.tr.cases:
            lines = [(b, m) for b, m in self.lay.case_lines(c) if b.system in MOUNTED and m > 0 and b.cog]
            m = sum(mm for _, mm in lines)
            z = sum(mm * b.cog[2] for b, mm in lines) / m
            tot = sum(mm for _, mm in self.lay.case_lines(c))
            rows[c.id] = dict(kg=m, cog_z=z, total_kg=tot)
        k = max(1.0, self.tr.caps()["plated"] / max(r["total_kg"] for r in rows.values()))
        worst = max(rows, key=lambda c: rows[c]["kg"])
        return dict(cases=rows, scale=k, worst=worst, kg=rows[worst]["kg"] * k, cog_z=rows[worst]["cog_z"])

    # ------------------------------------------------------------------ panels (report 12 section 3)
    def panel_checks(self) -> list[dict]:
        L, cr, f, w, rf = self.d["loads"], self.crit, self.p["floor"], self.p["wall"], self.p["roof"]
        V = self.V
        out = []

        def row(cid, what, panel, r, case, compression=True, extra=""):
            u = panel.utils(r, cr, compression)
            out.append(dict(id=cid, what=what, case=case, skin_mpa=r["skin_mpa"], core_mpa=r["core_mpa"],
                            util=u["util"], governing=u["governing"], extra=extra, defl_mm=r.get("defl_mm")))

        span = self.raiser_span
        ft = L["foot"]
        r = f.one_way(3 * ft["kg"] * G, min(ft["patch"]), span)
        bearing = 3 * ft["kg"] * G / (ft["patch"][0] * ft["patch"][1])
        r["core_mpa"] = max(r["core_mpa"], bearing * cr["core_factor"] / cr["bearing_factor"] *
                            f.core["shear"] / f.core["compression"])
        row("BDY-03", "Floor under a foot midway between the raisers, with bearing on the core", f, r, "LC2, 3 g",
            extra=f"bearing {bearing:.2f} MPa against {cr['bearing_factor'] * f.core['compression']:.2f} MPa")
        pitch = max(b - a for a, b in zip(self.stations, self.stations[1:]))
        r = f.uniform(3 * L["floor_edge_kg_m2"] * G / 1e6, pitch)
        row("BDY-04", f"Floor edge beside the raisers between outriggers {pitch:.0f} mm apart", f, r, "LC2, 3 g")
        # side wall in the ultimate wind, spanning from the floor to the roof-to-wall joiner. The skins are checked without
        # the stiffeners, and each stiffener for the share of the load its stiffness draws
        wu, ws = self.wind()
        r = w.uniform(wu["kpa"] / 1000, V["interior_h"])
        st = w.d["stiffener"]
        share = w.D_stiff / (w.D + w.D_stiff)
        m_st = share * wu["kpa"] / 1000 * st["pitch"] * V["interior_h"] ** 2 / 8
        s_st = m_st * st["depth"] / 2 / st["I"]
        u_st = s_st / (st["fy"] / cr["metal_factor"])
        # the member's share reaches it from the outer skin through the XPS behind it, in compression or, in suction, tension
        s_xps = share * wu["kpa"] / 1000 * st["pitch"] / st["width"]
        v_r = self.tr.td["stability"]["overturn"]["tie_down"]["v_r_ms"]       # STB-05's gust, region B's 500-year wind
        v500 = v_r * self.d["wind"]["Mzcat"]
        f500 = (v500 / wu["V"]) ** 2
        a_xps = cr["core_factor"] * w.core["compression"]
        row("BDY-06", f"Side wall in the ultimate wind, {wu['kpa']:.2f} kPa net at {wu['V']:.0f} m/s, floor to the roof joiner ({V['interior_h']:.0f} mm)",
            w, r, "Wind, ultimate", extra=(f"the member takes {100 * share:.0f} % of its bay's load, {s_st:.0f} MPa against {st['fy'] / cr['metal_factor']:.0f} MPa, "
                                          f"utilisation {u_st:.2f}. The {st['break']:g} mm of XPS behind it carries {s_xps:.3f} MPa against "
                                          f"{a_xps:.2f} MPa. Strapped down, at STB-05's gust, region B's 500-year wind at 3 m, {v_r:g} m/s "
                                          f"times {self.d['wind']['Mzcat']:g}, {v500:.1f} m/s, the member works at {u_st * f500:.2f} and the skins at "
                                          f"{w.utils(r, cr)['util'] * f500:.2f}. BDY-25 checks the walls with their openings"))
        if max(u_st, s_xps / a_xps) > out[-1]["util"]:
            out[-1].update(util=max(u_st, s_xps / a_xps), governing="member" if u_st >= s_xps / a_xps else "XPS behind the member")
        # the fixed roof with the bonded solar array and its own weight, spanning between the walls
        sol = sum(b.mass_kg for b in self.lay.blocks if b.system == "roof")
        q = 3 * (rf.d["kg_m2"] + sol / (V["body_length"] * V["body_width"] / 1e6)) * G / 1e6
        r = rf.uniform(q, V["body_width"] - V["wall_t"])
        row("BDY-07", f"Fixed roof with the {sol:.0f} kg solar array, spanning between the walls", rf, r, "LC2, 3 g")
        cuts = self.cutouts()
        if cuts:
            w26 = max(cuts, key=lambda c: c["util"])
            out.append(dict(id="BDY-26", what=f"Floor round its {len(cuts)} cut-outs over 60 mm, with their H200 inserts", case="LC2, 3 g",
                            skin_mpa=w26["skin_mpa"], core_mpa=w26["core_mpa"], util=w26["util"], governing=f"{w26['gland']}, {w26['governing']}",
                            extra=". ".join(c["text"] for c in cuts), defl_mm=None, cutouts=cuts))
        self.roof_defl = rf.uniform(q / 3, V["body_width"] - V["wall_t"])["defl_mm"]
        self.floor_defl = f.one_way(ft["kg"] * G, min(ft["patch"]), span)["defl_mm"]
        self.wall_defl = w.uniform(ws["kpa"] / 1000, V["interior_h"])["defl_mm"]
        self.wall_defl_bare = Panel("wall", {**w.d, "stiffener": None}).uniform(ws["kpa"] / 1000, V["interior_h"])["defl_mm"]
        return out

    def cutouts(self) -> list[dict]:
        """BDY-26 (I2-27): the floor round each cut-out over 60 mm (data/services.yaml `cutouts`), under BDY-03's foot standing
        beside it and BDY-04's 160 kg/m2, both at 3 g, on the one-way span between the raisers. The strip's effective width
        loses the cut-out's length, the skins and the H200 insert at its edge carry Kirsch's factor, and the H80 at the
        insert's outer edge the factor fallen off to there. Where the cut-out takes a raiser's bearer strip away, the floor
        bridges the gap along the raiser with a foot at its middle and bears on the insert at the gap's two ends."""
        import yaml
        from .partsdb import DATA
        cu = self.d.get("cutouts")
        rows = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8")).get("cutouts") or []
        if not cu or not rows:
            return []
        f, cr, L, V = self.p["floor"], self.crit, self.d["loads"], self.V
        ins, kt = cu["insert"], cu["kt"]
        span, ft = self.raiser_span, L["foot"]
        t = min(f.t1, f.t2)
        P = 3 * ft["kg"] * G
        q = 3 * L["floor_edge_kg_m2"] * G / 1e6
        r_in, r_out = V["rail_c"] - V["rail_w"] / 2, V["rail_c"] + V["rail_w"] / 2      # the raiser's bearer strip across Y
        skin_lim = min(cr["skin_factor"] * f.ult, cr["wrinkling_factor"] * f.wrinkling)
        out = []
        for c in rows:
            ya = abs(c["y"])
            y0, y1 = ya - c["h"] / 2, ya + c["h"] / 2
            near = min(abs(y0 - V["rail_c"]), abs(y1 - V["rail_c"]), abs(ya - V["rail_c"]))
            far = min(max(abs(y0 - V["rail_c"]), abs(y1 - V["rail_c"])), span / 2)
            a = max(abs(ya - V["rail_c"]), min(ft["patch"]) / 2)                       # the foot beside it, from the raiser
            bn = min(ft["patch"]) + span / 2 - c["w"]
            M, Vf = P * a * (span - a) / span, P * (span - a) / span
            m_u, v_u = q * far * (span - far) / 2, q * (span / 2 - min(near, span / 2))
            rows_u = [("skin, a foot beside it", kt * M / (t * f.dd * bn), skin_lim),
                      ("skin, 160 kg/m2", kt * m_u / (t * f.dd), skin_lim),
                      ("insert in shear, a foot beside it", kt * Vf / (f.dd * bn), cr["core_factor"] * ins["shear"]),
                      ("insert in shear, 160 kg/m2", kt * v_u / f.dd, cr["core_factor"] * ins["shear"])]
            a_eq = (c["w"] + c["h"]) / 4
            x2 = (a_eq / (a_eq + ins["width"])) ** 2
            k_out = 1 + x2 / 2 + 1.5 * x2 ** 2                                         # Kirsch at the insert's outer edge
            rows_u.append(("H80 beyond the insert", k_out * max(Vf / (f.dd * bn), v_u / f.dd), cr["core_factor"] * f.core["shear"]))
            over = max(0.0, min(y1, r_out) - max(y0, r_in))
            if over > 0:
                R = q * (span / 2 + self.edge_span / 2)                                 # the raiser's line load from the floor
                bb = min(ft["patch"]) + c["w"] / 2
                Mb = P * c["w"] / 4 + R * c["w"] ** 2 / 8
                end = P / 2 + R * c["w"] / 2
                rows_u += [("skin, bridging the raiser's gap", kt * Mb / (t * f.dd * bb), skin_lim),
                           ("insert in shear, bridging the gap", kt * end / (f.dd * bb), cr["core_factor"] * ins["shear"]),
                           ("insert bearing on the strip at the gap's ends", end / (V["rail_w"] * ins["width"]), cr["bearing_factor"] * ins["compression"])]
            parts = [dict(part=p, mpa=s, limit_mpa=lim, util=s / lim) for p, s, lim in rows_u]
            g = max(parts, key=lambda p: p["util"])
            skin = max(p["mpa"] for p in parts if p["part"].startswith("skin"))
            core = max(p["mpa"] for p in parts if "shear" in p["part"] or "H80" in p["part"])
            text = (f"{c['gland']} {c['w']:g} x {c['h']:g} mm at X {c['x']:,.0f}, Y {c['y']:+,.0f}: "
                    + (f"over {over:.0f} mm of the raiser's bearer strip, " if over > 0 else f"{max(0.0, (r_in - y1) if y1 <= r_in else (y0 - r_out)):.0f} mm from the raiser's strip, ")
                    + f"{g['part']} {g['mpa']:.2f} MPa against {g['limit_mpa']:.2f} MPa ({g['util']:.2f})")
            out.append(dict(gland=c["gland"], x=c["x"], y=c["y"], w=c["w"], h=c["h"], over_strip_mm=over, parts=parts, util=g["util"],
                            governing=g["part"], skin_mpa=skin, core_mpa=core, text=text))
        return out

    def wind(self) -> tuple[dict, dict]:
        """The ultimate and serviceability net pressures on a side wall, kPa (data/body/body.yaml `wind`, AS/NZS 1170.2)."""
        wd = self.d["wind"]
        c = wd["cpe"] - wd["cpi"]
        vs = wd["V_s"] * wd["Mzcat"]
        return (dict(V=wd["V_u"], kpa=0.6 * wd["V_u"] ** 2 * c / 1000), dict(V=vs, kpa=0.6 * vs ** 2 * c / 1000))

    def deflections(self) -> list[dict]:
        cr, V = self.crit, self.V
        self.panel_checks() if not hasattr(self, "roof_defl") else None
        return [dict(id="DEF-B1", what="Floor under a foot at 1 g", mm=self.floor_defl, limit_mm=self.raiser_span / cr["floor_span_ratio"]),
                dict(id="DEF-B2", what="Fixed roof with the solar array at 1 g", mm=self.roof_defl, limit_mm=(V["body_width"] - V["wall_t"]) / cr["roof_span_ratio"]),
                dict(id="DEF-B3", what=(f"Side wall in region {self.d['wind']['region']}'s 25-year wind, {self.wind()[1]['kpa']:.2f} kPa net at "
                                        f"{self.wind()[1]['V']:.1f} m/s, with its members on the inner skin ({self.wall_defl_bare:.1f} mm without them)"),
                     mm=self.wall_defl, limit_mm=V["interior_h"] / cr["wall_span_ratio"])]

    # ------------------------------------------------------------------ inserts and the roof joint
    def roof(self) -> dict:
        """The fixed roof bonded into the roof-to-wall joiner, in report 12's 40 m/s uplift (roof down at 110 km/h into a
        36 km/h headwind), against the bond's tensile strength over the joiner leg, with half of it allowed."""
        V, tw, L = self.V, self.d["twist"], self.d["loads"]
        perim = 2 * (V["body_length"] + V["body_width"])
        # BD-02 as weighed in the mass schedule, its insert strips with it, and the solar array: the figure BODY.md gives
        roof_kg = sum(b.mass_kg for b in self.lay.blocks if b.id == "BD-02" or b.system == "roof")
        net = max(0.0, L["uplift_40ms_n"] - roof_kg * G)
        q = L["uplift_40ms_n"] / perim
        allow = 0.5 * tw["bond_tension_strength"] * tw["bond_width"]
        return dict(uplift_n=L["uplift_40ms_n"], roof_kg=roof_kg, net_n=net, perimeter_mm=perim, q_n_mm=q, allow_n_mm=allow, util=q / allow)

    def inserts(self) -> list[dict]:
        """Working loads on the panel fixings against half their rated load (report 12 section 3, MAT-05)."""
        L, cr = self.d["loads"], self.crit
        screws = L["bed_rails"] * L["rail_screws"]
        f_night = L["bed_night_factor"] * L["bed_kg"] * G / screws    # the bed down with two sleepers moving on it
        f_travel = 3 * L["bed_travel_kg"] * G / screws               # LC2, 3 g on the moving bed at its day stop
        f_rail = max(f_night, f_travel)
        st = self.p["wall"].d["stiffener"]
        aw = self.awning()
        rows = [dict(id="INS-01", what=(f"Lift-bed rail screw, 1/4 in self-drilling, {L['rail_screw_mm']:g} mm under the head, through the inner skin "
                                        f"into the {st['name'].split(' 6060')[0]} hardpoint's {st['wall']:g} mm wall, shear"), n=f_rail, rated_n=L["rail_screw_rated_n"],
                     case=(f"{L['bed_night_factor']:g} x the {L['bed_kg']:.0f} kg bed at night" if f_night >= f_travel else
                           f"LC2, 3 g on the {L['bed_travel_kg']:.0f} kg moving bed") + f", over {screws} screws"),
                dict(id="INS-02", what=f"Awning bracket bolt, {aw['bolt']} through the roof's kerb-edge insert strip, tension in travel",
                     n=aw["travel_n"], rated_n=aw["rated_tension_n"],
                     case=(f"LC2, 3 g on the {aw['kg']:.1f} kg awning taken as a pull, a bracket's share on its inner bolt with prying "
                           f"{aw['cog_lever_mm']:.0f} over {aw['bolt_pitch_mm']:.0f} mm")),
                dict(id="INS-03", what=f"Awning bracket bolt, {aw['bolt']}, tension with the canopy open in a {aw['check_kmh']:.0f} km/h gust, a check of the fixing only",
                     n=aw["open_n"], rated_n=aw["rated_tension_n"],
                     case=(f"{aw['q_pa']:.0f} Pa, Cp,n {aw['cpn']:g} on the {aw['canopy_m2']:g} m2 canopy, half of it at the case "
                           f"({aw['case_n'] / 1000:.2f} kN), the legs pegged, a bracket's share on its inner bolt with prying "
                           f"{aw['canopy_lever_mm']:.0f} over {aw['bolt_pitch_mm']:.0f} mm"))]
        for r in rows:
            r["util"] = r["n"] / (cr["insert_factor"] * r["rated_n"])
        return rows

    def rail_screw(self) -> dict:
        """CT-202 detail D (F4-10): how far a lift-bed rail screw reaches, from under its head. The rail's web, the inner skin
        and the bond bring it to the member's face, and a longer screw than `back_mm` would touch the member's back wall,
        and one longer than `skin_mm` the outer skin."""
        L, wl = self.d["loads"], self.p["wall"]
        st = wl.d["stiffener"]
        face = L["rail_web_mm"] + wl.t2 + self.d["thermal"]["bond_mm"]
        return dict(length_mm=L["rail_screw_mm"], face_mm=face, into_mm=L["rail_screw_mm"] - face,
                    back_mm=face + st["depth"] - st["wall"], skin_mm=face + st["depth"] + st["break"])

    def awning(self) -> dict:
        """The Fiamma F80s on the roof's kerb edge (data/body/body.yaml `awning`): its bracket bolts in travel (INS-02) and
        with the canopy open in wind (INS-03), and where its legs put the lead bar (BDY-23)."""
        a, V = self.d["awning"], self.V
        b = self.lay.find(a["line"])
        m = b.mass_kg
        nb = a["brackets"]
        travel = 3 * m * G / nb * max(1.0, a["cog_lever_mm"] / a["bolt_pitch_mm"])
        v = a["check_kmh"] / 3.6
        q = 0.6 * v ** 2
        case_n = 0.5 * q * a["cpn"] * a["canopy_m2"]
        open_n = case_n / nb * max(1.0, a["canopy_lever_mm"] / a["bolt_pitch_mm"])
        z_case = b.box[2] + a["canopy_drop_mm"]                 # where the canopy leaves the case
        z_bar_max = a["leg_max_mm"] + a["leg_head_mm"]          # the lead bar on fully extended legs, level ground
        pitch_full = math.degrees(math.asin(max(0.0, z_case - z_bar_max) / a["extension_mm"]))
        z_bar = z_case - a["extension_mm"] * math.sin(math.radians(a["pitch_deg"]))
        leg = z_bar - a["leg_head_mm"]
        return dict(a, kg=m, travel_n=travel, q_pa=q, case_n=case_n, open_n=open_n, z_case=z_case, z_bar_max=z_bar_max,
                    pitch_full_deg=pitch_full, z_bar=z_bar, leg_mm=leg, reach_mm=a["leg_max_mm"] - leg)

    def cold_bridge(self) -> dict:
        """BDY-22: steady two-dimensional conduction through the side wall at one of its members on the inner skin, on the
        design cold night (data/body/body.yaml `thermal`). Half the strip, from the member's centreline (symmetry) to
        `strip_mm` (adiabatic), on a square grid. Returns the coldest inside surface over the member, the member's own
        temperature (the HappiJac rails screwed to it run at about the same), the plain wall's surface and the extra heat
        loss per metre of member, both ways from its centreline."""
        th, wl = self.d["thermal"], self.p["wall"]
        st, jn = wl.d["stiffener"], self.d["joiners"]
        k = th["k"]
        mc = self.members_clear()
        single = _wall_section(th, wl.t1, wl.c, wl.t2, st)
        plain = _wall_section(th, wl.t1, wl.c, wl.t2, None)
        ends_at = self.member_ends()
        sections = self.member_sections(mc, ends_at)
        beside = min(sections, key=lambda q: q["mid"])
        ins = min((s["width_mm"] for s in mc["side_inserts"]), default=None)
        gap = min((q["gap_mm"] for q in mc["pairs"]), default=None)
        dT = th["t_in"] - th["t_out"]
        heat = dict(th, rsi=th["rsi_heat"])                     # the heat loss figure on ISO 6946's film
        psi = 2 * (_wall_section(heat, wl.t1, wl.c, wl.t2, st)["q_w_m"] - _wall_section(heat, wl.t1, wl.c, wl.t2, None)["q_w_m"]) / dT
        # along the member: a fin between the inside and outside air. One-dimensional conductances over the member's width
        # leave out its side paths, which makes the fin longer and its ends colder
        w, d, t, brk = st["width"], st["depth"], st["wall"], st["break"]
        kA = k["aluminium"] * (w * d - (w - 2 * t) * (d - 2 * t)) * 1e-6
        g_in = w / 1000 / (th["rsi"] + wl.t2 / 1000 / k["grp"])
        g_out = w / 1000 / (brk / 1000 / k["xps"] + wl.t1 / 1000 / k["grp"] + th["rse"])
        m = math.sqrt((g_in + g_out) / kA)
        tm = single["t_member"]
        ends = {name: self._member_end(e, kA * m, tm, min(q[name] for q in sections)) for name, e in ends_at.items()}
        cover = jn["cover"]
        joiner = th["t_in"] - dT * th["rsi"] / (th["rsi"] + cover["t_mm"] / 1000 / k[cover["k"]])
        # the dew point on the generators, where they stand (F5-04): what still runs there (report 19's moisture model)
        gm = th["generator_mode"]
        gen = {}
        for pos, units in gm["positions"].items():
            e2 = gm["e2_m3h"] if "e2" in units else 0.0
            qp = e2 + (gm["respa_m3h"] if "respa" in units else 0.0)
            eps = gm["eps_lat"] * e2 / qp
            gen[pos] = dict(q=qp, dew=_dew(gm["w_out_factor"] * _w_sat(th["t_out"]) + gm["moisture_g_h"] / (1.2 * qp * (1 - eps))))
        gen_pos = max(gen, key=lambda p: gen[p]["dew"])
        dew_gen, q = gen[gen_pos]["dew"], gen[gen_pos]["q"]
        each = self.V["ceiling_z"] - self.V["floor_underside_z"] - ends_at["foot"]["at_mm"] - ends_at["head"]["at_mm"]
        length_m = len(mc["members"]) * each / 1000
        need = th["dew_point"] + th["margin_k"]
        where = dict(mid=single["tsi_min"], beside=beside["mid"], foot=ends["foot"]["tsi"], head=ends["head"]["tsi"], joiner=joiner)
        gov = min(where, key=where.get)
        return dict(tsi_min=where[gov], governs=gov, where=where, tsi_mid=single["tsi_min"], t_member=tm, tsi_plain=plain["tsi_min"],
                    need=need, ends=ends, fin_mm=1000 / m, rsi=th["rsi"], dew_gen=dew_gen, insert_mm=ins, pair_gap_mm=gap,
                    beside_member=beside["member"], sections=sections, door_u=th["door_u"],
                    insert_k=k[th["insert"]], window_u=th["window_u"], cover_mm=cover["t_mm"],
                    need_gen=dew_gen + th["margin_k"], gen_m3h=q, gen=gen, gen_pos=gen_pos, psi=psi, length_m=length_m, w_k=psi * length_m,
                    members=th["members"], member=st["name"], brk=brk, t_out=th["t_out"], t_in=th["t_in"], dew=th["dew_point"],
                    bare=th["bare_panels_w_k"], bridges=th["bridges_w_k"])

    def member_sections(self, mc: dict, ends_at: dict) -> list[dict]:
        """BDY-22 across each wall member as it stands (F4-02, F4-04): its neighbours within the section's strip, the other
        members, W1's and W2's side inserts with their windows beyond, and the doors' and windows' 70 mm insert strips (taken
        as rigid PVC, a bound) with the door or window beyond. At mid-length every neighbour counts. At the foot and the head
        only the openings that reach that height, as the doors reach the floor."""
        th, wl, ru, V = self.d["thermal"], self.p["wall"], self.d["members_rule"], self.V
        st, k = wl.d["stiffener"], th["k"]
        half, L = st["width"] / 2, th["strip_mm"]
        ops = [o for o in self.openings() if o["wall"] in ("kerb", "road") and not o.get("gland")]
        cache, out = {}, []
        for iid, wall, x in mc["members"]:
            others = tuple(round(x2 - x, 1) for i2, w2, x2 in mc["members"] if w2 == wall and i2 != iid and abs(x2 - x) < L + half)
            feats = []                                                  # (insert, hole, z0, z1) beside this member
            for si in mc["side_inserts"]:
                if si["member"] == iid:
                    o = next(o for o in ops if o["id"] == si["opening"])
                    sgn = 1 if V["body_x0"] + o["u0"] > x else -1
                    a, c = sgn * half, sgn * (half + si["width_mm"])
                    feats.append(((min(a, c), max(a, c), k[th["insert"]]), (min(c, sgn * L), max(c, sgn * L), th["window_u"]), o["z0"], o["z1"]))
            for o in ops:
                if o["id"] in ru["side_inserts"]["openings"] or not any(o.get("line", "").startswith(q) for q in ru["strip_lines"]):
                    continue
                u0, u1 = V["body_x0"] + o["u0"] - x, V["body_x0"] + o["u1"] - x
                if u1 + ru["strip_mm"] < -L or u0 - ru["strip_mm"] > L:
                    continue
                U = th["window_u"] if o["line"].startswith("WN-") else th["door_u"]
                feats.append(((u0 - ru["strip_mm"], u0, k[th["strip_k"]]), (u0, u1, U), o["z0"], o["z1"]))
                feats.append(((u1, u1 + ru["strip_mm"], k[th["strip_k"]]), None, o["z0"], o["z1"]))
            for p in mc["shared"]:                                      # F5-03: the H200 fill in the pair's one channel
                if iid in p["members"]:
                    x2 = next(x3 for i3, _, x3 in mc["members"] if i3 != iid and i3 in p["members"])
                    sgn = 1 if x2 > x else -1
                    a, c = sgn * half, sgn * (abs(x2 - x) - half)
                    feats.append(((min(a, c), max(a, c), k[th["insert"]], "channel"), None, -math.inf, math.inf))
            row = dict(member=iid, wall=wall)
            for name, zs in (("mid", None), ("foot", ends_at["foot"]["z"]), ("head", ends_at["head"]["z"])):
                use = [f for f in feats if zs is None or f[2] - 1e-6 <= zs <= f[3] + 1e-6]
                key = (others, tuple(f[0] for f in use), tuple(f[1] for f in use if f[1]))
                if key not in cache:
                    cache[key] = _wall_line(th, wl.t1, wl.c, wl.t2, st, others, [f[0] for f in use], [f[1] for f in use if f[1]])["tsi"]
                row[name] = cache[key]
            out.append(row)
        return out

    def member_ends(self) -> dict:
        """Where each wall member ends against its joiners (BDY-22, F4-01), mm from the wall's bottom and top edges. At its
        foot it stands on its insulating bearing block `foot_clear_mm` above the floor joiner's inner leg, which wraps the
        inner skin to `inner_leg_mm` (with its flange), so the leg overlaps none of it. At its head it stops `end_gap_mm`
        under the wall's top insert strip, and the roof joiner's inner leg reaches `inner_leg_mm` down the inner skin."""
        st, jn, V = self.p["wall"].d["stiffener"], self.d["joiners"], self.V
        foot = jn["floor"]["inner_leg_mm"] + st["foot_clear_mm"]
        head = jn["top_strip_mm"] + st["end_gap_mm"]
        return dict(foot=dict(at_mm=foot, leg_mm=jn["floor"]["inner_leg_mm"], clear_mm=st["foot_clear_mm"], gap_mm=st["foot_clear_mm"],
                              block_w=st["block_mm"], z=foot - V["floor_t"]),
                    head=dict(at_mm=head, leg_mm=jn["roof"]["inner_leg_mm"], clear_mm=head - jn["roof"]["inner_leg_mm"],
                              gap_mm=st["end_gap_mm"], block_w=st["head_pad_mm"], z=V["interior_h"] - head))

    def _member_end(self, e: dict, fin_g: float, tm: float, tsi_mid: float) -> dict:
        """The drop in a member's temperature at one end, a fin's end losing heat to a joiner taken at the outside air (a
        bound). Three paths: through the rigid PVC block or pad and the XPS beside it, over the clearance to the floor
        joiner's leg or the gap under the top insert strip, along the inner skin to the joiner's leg, and, where a leg
        overlaps the member, through the bond and the skin between them (the path F4-01 found)."""
        th, wl = self.d["thermal"], self.p["wall"]
        st, k = wl.d["stiffener"], th["k"]
        w, d = st["width"], st["depth"]
        clear = max(e["clear_mm"], 1.0) / 1000
        g = (k["pvc"] * e["block_w"] + k["xps"] * (w - e["block_w"])) * d * 1e-6 / (e["gap_mm"] / 1000)
        g += k["grp"] * wl.t2 * w * 1e-6 / clear
        overlap = max(0.0, e["leg_mm"] - e["at_mm"])
        g += w * overlap * 1e-6 / (th["bond_mm"] / 1000 / k["ms"] + wl.t2 / 1000 / k["grp"])
        drop = g * (tm - th["t_out"]) / (fin_g + g)
        return dict(e, drop_k=drop, tsi=tsi_mid - drop, g_w_k=g, overlap_mm=overlap)

    def members_clear(self) -> dict:
        """FIT-07 (F3-02): each wall member against the cut-outs, insert strips and glands on its side wall, and the bays
        the members, the kitchen tower's sides, the partition and the end walls leave (data/body/body.yaml `members_rule`).
        The lift bed's hardpoints stand behind its rails."""
        V, lay, ru = self.V, self.lay, self.d["members_rule"]
        st = self.p["wall"].d["stiffener"]
        x0, half = V["body_x0"], st["width"] / 2
        side = lambda y: "road" if y > 0 else "kerb"  # noqa: E731
        mem = [(b.iid, side(b.cog[1]), b.cog[0]) for b in lay.blocks if b.id in ru["members"]]
        mem += [(f"LB-06 at {b.iid}", side(b.cog[1]), b.cog[0]) for b in lay.blocks if b.id == ru["hardpoints_at"]]
        obs, side_inserts = [], []
        si = ru["side_inserts"]
        ops = [o for o in self.openings() if o["wall"] in ("kerb", "road")]
        for o in ops:
            a, c = x0 + o["u0"], x0 + o["u1"]
            if o["id"] in si["openings"]:
                # F4-02: an S4's clamp bears on a solid edge at W1's and W2's sides too. Each side insert fills the core from
                # the cut-out to the hardpoint beside it, bonded into the hardpoint's routed channel
                for edge, sgn in ((a, -1), (c, 1)):
                    near = min(mem, key=lambda q: abs(q[2] - edge) if q[1] == o["wall"] else math.inf)
                    width = (near[2] - half - edge) if sgn > 0 else (edge - (near[2] + half))
                    side_inserts.append(dict(opening=o["id"], member=near[0], wall=o["wall"], width_mm=width))
                    obs.append((o["wall"], min(edge, edge + sgn * width), max(edge, edge + sgn * width),
                                f"{o['id']}'s side insert", near[0]))
                continue
            strip = ru["strip_mm"] if any(o.get("line", "").startswith(p) for p in ru["strip_lines"]) else 0
            what = f"{o['id']} ({o['name'].split(',')[0]})" + (f" with its {strip:g} mm insert strip" if strip else "")
            obs.append((o["wall"], a - strip, c + strip, what, None))
        as_openings = {o["id"] for o in ops}
        for g in yaml.safe_load((DATA / "services.yaml").read_text())["glands"]:
            if g["at"] in ("kerb", "road") and g["id"] not in as_openings:
                gw = g.get("w", g["d"])
                obs.append((g["at"], g["x"] - gw / 2, g["x"] + gw / 2, f"gland {g['id']}", None))
        strips = []
        for sp in ru.get("strips", []):            # a horizontal fixing strip stops clear_mm short of each member it meets
            bb = lay.find(sp["block"]).box
            wall = side((bb[1] + bb[4]) / 2)
            pieces = [(bb[0], bb[3])]
            for _, w2, x in mem:
                if w2 != wall:
                    continue
                lo, hi = x - half - ru["clear_mm"], x + half + ru["clear_mm"]
                pieces = [q for a, c in pieces for q in (((a, c),) if hi <= a or lo >= c else tuple(
                    p for p in ((a, lo), (hi, c)) if p[1] - p[0] > 1e-6))]
            strips += [(wall, a, c, sp["name"]) for a, c in pieces]
        obs += [s + (None,) for s in strips]
        rows = []
        for iid, wall, x in mem:
            gaps = [(max(o0 - (x + half), (x - half) - o1), what) for w2, o0, o1, what, shares in obs if w2 == wall and shares != iid]
            g, what = min(gaps)
            shared = [s for s in side_inserts if s["member"] == iid]
            rows.append(dict(member=iid, wall=wall, x=x, gap_mm=g, to=what, shares=[s["opening"] for s in shared]))
        pairs = []
        for i, (a_id, a_w, a_x) in enumerate(mem):
            for b_id, b_w, b_x in mem[i + 1:]:
                if a_w == b_w and abs(a_x - b_x) - 2 * half < ru["clear_mm"] * 4:
                    pairs.append(dict(members=(a_id, b_id), wall=a_w, gap_mm=abs(a_x - b_x) - 2 * half))
        # F5-03: two members closer than clear_mm share one routed channel with an H200 fill bonded between them, so no
        # thin fin of XPS is left to rout. Each such pair is listed in `shared_channels` by its block ids
        def _is(iid, ref):
            return iid in (ref, f"LB-06 at {ref}")
        for p in pairs:
            p["shared"] = any((_is(p["members"][0], x) and _is(p["members"][1], y)) or (_is(p["members"][0], y) and _is(p["members"][1], x))
                              for x, y in ru.get("shared_channels", []))
        shared = [p for p in pairs if p["shared"]]
        bays = {}
        for wall in ("kerb", "road"):
            xs = [x0 + V["end_wall_t"], V["body_x1"] - V["end_wall_t"]] + [x for _, w2, x in mem if w2 == wall]
            for bid in ru["bounds"]:
                bb = lay.find(bid).box
                if (wall == "road" and bb[4] >= V["half_bw"] - V["wall_t"] - 60) or (wall == "kerb" and bb[1] <= -V["half_bw"] + V["wall_t"] + 60):
                    xs += [bb[0], bb[3]]
            xs = sorted(xs)
            bays[wall] = max(b - a for a, b in zip(xs, xs[1:]))
        worst = min(r["gap_mm"] for r in rows)
        probs = [f"{r['member']} on the {r['wall']} side is {r['gap_mm']:.0f} mm from {r['to']}" for r in rows if r["gap_mm"] < ru["clear_mm"] - 1e-6]
        probs += [f"a {w2} side bay is {v:.0f} mm wide" for w2, v in bays.items() if v > st["pitch"] + 1e-6]
        probs += [f"{s['opening']}'s side insert beside {s['member']} is {s['width_mm']:.0f} mm, under {si['min_mm']:g} mm"
                  for s in side_inserts if s["width_mm"] < si["min_mm"] - 1e-6]
        probs += [f"{p['members'][0]} and {p['members'][1]} on the {p['wall']} side are {p['gap_mm']:.1f} mm apart and share no routed channel"
                  for p in pairs if p["gap_mm"] < ru["clear_mm"] - 1e-6 and not p["shared"]]
        probs += [f"{p['members'][0]} and {p['members'][1]} overlap" for p in pairs if p["gap_mm"] < 0]
        return dict(ok=not probs, shared=shared, problems=probs, rows=rows, worst_mm=worst, bays=bays, pitch=st["pitch"], clear_mm=ru["clear_mm"],
                    width=st["width"], strips=strips, side_inserts=side_inserts, insert_min_mm=si["min_mm"], pairs=pairs,
                    members=mem)

    def wall_plates(self) -> dict:
        """BDY-24 and BDY-25 (F4-04): each side wall as a plate from the front wall to the rear wall with every opening cut
        out and every member on its line, so the bays that hold openings carry their real load. Supported along the floor
        and roof joiners, at the end walls and on the kitchen tower's sides and the partition, as FIT-07 bounds the bays.
        The model is linear, so it is solved once at 1 kPa and scaled to BDY-10's and BDY-06's winds and STB-05's gust."""
        V, wl, lay = self.V, self.p["wall"], self.lay
        st, ru = wl.d["stiffener"], self.d["members_rule"]
        mc, ends = self.members_clear(), self.member_ends()
        w, d, t = st["width"], st["depth"], st["wall"]
        area = w * d - (w - 2 * t) * (d - 2 * t)
        J = 4 * ((w - t) * (d - t)) ** 2 * t / (2 * ((w - t) + (d - t)))        # Bredt's thin-walled closed section
        props = dict(EI=st["E"] * st["I"], GA=st["G"] * area * d / (w + d), GJ=st["G"] * J)
        x0, x1, H = V["body_x0"] + V["end_wall_t"], V["body_x1"] - V["end_wall_t"], V["interior_h"]
        bk = self.d["blocks"]
        blocks = [dict(z0=0.0, z1=ends["foot"]["z"], EI=bk["E"] * ends["foot"]["block_w"] * d ** 3 / 12, GA=bk["G"] * ends["foot"]["block_w"] * d),
                  dict(z0=ends["head"]["z"], z1=H, EI=bk["E"] * ends["head"]["block_w"] * d ** 3 / 12, GA=bk["G"] * ends["head"]["block_w"] * d)]
        out = {}
        for wall in ("kerb", "road"):
            ops = [o for o in self.openings() if o["wall"] == wall]
            cuts = [(V["body_x0"] + o["u0"], V["body_x0"] + o["u1"], o["z0"], o["z1"]) for o in ops]
            mem = [dict(props, name=iid, x=x, z0=ends["foot"]["z"], z1=ends["head"]["z"], ends=blocks) for iid, w2, x in mc["members"] if w2 == wall]
            sup = []
            for bid in ru["bounds"]:
                bb = lay.find(bid).box
                if (wall == "road" and bb[4] >= V["half_bw"] - V["wall_t"] - 60) or (wall == "kerb" and bb[1] <= -V["half_bw"] + V["wall_t"] + 60):
                    sup += [(bb[0], bb[2] - V["floor_z"], bb[5] - V["floor_z"]), (bb[3], bb[2] - V["floor_z"], bb[5] - V["floor_z"])]
            r = _wall_plate(x0, x1, H, cuts, mem, sup, wl, 1e-3, self.d["plate"]["step_mm"], self.d["plate"]["corner_mm"])
            j, i = np.unravel_index(np.argmax(r["w"]), r["w"].shape)
            lines = sorted({x0, x1} | {m["x"] for m in mem} | {s[0] for s in sup})
            bays = []
            for a, b in zip(lines, lines[1:]):
                sel = (r["X"] >= a - 1e-6) & (r["X"] <= b + 1e-6)
                held = [o["id"] for o, c in zip(ops, cuts) if c[0] < b and c[1] > a]
                bays.append(dict(x0=a, x1=b, w_mm=float(r["w"][:, sel].max()), openings=held))
            mm = max(r["members"].items(), key=lambda kv: abs(kv[1]["M"]))
            out[wall] = dict(w_mm=float(r["w"].max()), at_x=float(r["X"][i]), at_z=float(r["Z"][j]), bays=bays,
                             member=mm[0], member_nmm=abs(mm[1]["M"]), member_z=mm[1]["z"],
                             member_q=max(v["q"] for v in r["members"].values()), m_max=r["m_max"], q_max=r["q_max"],
                             q_at=r["q_at"], m_at=r["m_at"], v_end=max(v["V_end"] for v in r["members"].values()))
        return dict(walls=out, props=props, J=J, step=self.d["plate"]["step_mm"], corner=self.d["plate"]["corner_mm"],
                    block_area=min(ends["foot"]["block_w"], ends["head"]["block_w"]) * d)

    def plate_checks(self) -> dict:
        """BDY-24 at BDY-10's wind and BDY-25 at BDY-06's, from the plates at 1 kPa. Each wall member at its yield over 1.5,
        the skins at half their ultimate and half their wrinkling stress, the core in shear at half its strength and the XPS
        behind a member at half its compressive strength (BDY-06's criteria)."""
        pl, wl, cr = self.wall_plates(), self.p["wall"], self.crit
        st = wl.d["stiffener"]
        wu, ws = self.wind()
        v500 = self.tr.td["stability"]["overturn"]["tie_down"]["v_r_ms"] * self.d["wind"]["Mzcat"]
        defl = {k: dict(v, w_s=v["w_mm"] * ws["kpa"]) for k, v in pl["walls"].items()}
        strength = {}
        for k, v in pl["walls"].items():
            f = wu["kpa"]
            s_mem = v["member_nmm"] * f * st["depth"] / 2 / st["I"]
            s_skin = v["m_max"] * f / (min(wl.t1, wl.t2) * wl.dd)
            tau = v["q_max"] * f / wl.dd
            xps = v["member_q"] * f / st["width"]
            blk = v["v_end"] * f / pl["block_area"]
            u = dict(member=s_mem / (st["fy"] / cr["metal_factor"]),
                     skins=max(s_skin / (cr["skin_factor"] * wl.ult), s_skin / (cr["wrinkling_factor"] * wl.wrinkling)),
                     core=tau / (cr["core_factor"] * wl.core["shear"]), xps=xps / (cr["core_factor"] * wl.core["compression"]),
                     blocks=blk / (cr["core_factor"] * self.d["blocks"]["shear_mpa"]))
            gov = max(u, key=u.get)
            strength[k] = dict(s_member=s_mem, s_skin=s_skin, tau=tau, xps=xps, blk=blk, v_end=v["v_end"] * f, utils=u, governing=gov, util=u[gov],
                               q_at=v["q_at"], m_at=v["m_at"])
        f500 = (v500 / wu["V"]) ** 2
        for q in strength.values():
            # strapped down at STB-05's gust (reported): the governing item's factor on its own strength
            sk = "ultimate" if q["s_skin"] / (cr["skin_factor"] * wl.ult) >= q["s_skin"] / (cr["wrinkling_factor"] * wl.wrinkling) else "wrinkling stress"
            cap, s, on = dict(member=(st["fy"], q["s_member"], "yield"),
                              skins=(wl.ult if sk == "ultimate" else wl.wrinkling, q["s_skin"], sk),
                              core=(wl.core["shear"], q["tau"], "shear strength"), xps=(wl.core["compression"], q["xps"], "compressive strength"),
                              blocks=(self.d["blocks"]["shear_mpa"], q["blk"], "shear strength"))[q["governing"]]
            q["at500"] = dict(util=q["util"] * f500, factor=cap / (s * f500), on=on)
        limit = self.V["interior_h"] / cr["wall_span_ratio"]
        return dict(defl=defl, strength=strength, ws=ws, wu=wu, v500=v500, f500=f500, limit_mm=limit, props=pl["props"],
                    step=pl["step"], corner=pl["corner"], block_shear=self.d["blocks"]["shear_mpa"])

    def cradle(self) -> dict:
        """The split's outdoor unit and its cradle on the rear wall (BDY-21): the stays carry the vertical load to the
        chassis, and the wall's bolts the overturning moment, the pull away from the wall and the sideways load, against
        half their rated loads. The pull-through rating uses the body mounts' spreader rule on the bolt's pad."""
        cd, cr, V = self.d["cradle"], self.crit, self.V
        sp = self.d["mounts"]["fallback"]["spreader"]
        lines = [self.lay.find(i) for i in cd["lines"]]
        m = sum(b.mass_kg for b in lines)
        d = sum(b.mass_kg * b.cog[0] for b in lines) / m - V["body_x1"]      # centre of gravity behind the rear wall
        a, n, W = cd["accel"], cd["bolts"], m * G
        wl = self.p["wall"]
        pull_rated = 4 * cd["pad_side_mm"] * (wl.t1 * sp["skin_shear"] + wl.c * sp["insert_shear"]) / 2
        t_moment = a["down_g"] * W * d / cd["row_lever_mm"] / 2                # the top row's two bolts hold the overturning moment
        t_pull = a["along_g"] * W / n                                           # the unit pulled away from the wall
        t_side = a["side_g"] * W * d / cd["column_spacing_mm"] / 2              # the sideways load's twist on the bolt columns
        tension = t_moment + t_pull + t_side
        shear = a["side_g"] * W / n
        st = cd["stays"]
        stay_n = a["down_g"] * W / st["n"]
        p_cr = math.pi ** 2 * st["E"] * st["I_min"] / st["L"] ** 2
        u = dict(bolt_tension=tension / (cr["insert_factor"] * pull_rated), bolt_shear=shear / (cr["insert_factor"] * cd["shear_rated_n"]),
                 stay_buckling=stay_n / (p_cr / st["buckling_factor"]), stay_yield=stay_n / (st["A"] * st["fy"] / cr["metal_factor"]))
        gov = max(u, key=u.get)
        return dict(mass_kg=m, offset_mm=d, tension_n=tension, shear_n=shear, pull_rated_n=pull_rated, shear_rated_n=cd["shear_rated_n"],
                    stay_n=stay_n, stay_pcr_n=p_cr, stays=st, utils=u, governing=gov.replace("_", " "), util=u[gov])

    # ------------------------------------------------------------------ the body as a torsion box (report 12 section 4)
    def box_gj(self, lid_structural: bool) -> dict:
        """GJ of the body box, N mm2. With the roof bonded into its joiner the body is one closed cell of the floor, the walls
        and the roof (`lid_structural`, the upper bound). The lower bound neglects the roof joint: an open U of the floor
        and the walls, as report 12 took for the latched lid."""
        V, p, tw = self.V, self.p, self.d["twist"]
        b = V["body_width"] - V["wall_t"]
        zf = V["floor_z"] - p["floor"].d["t"] / 2
        h = V["ceiling_z"] + p["roof"].d["t"] / 2 - zf
        walls, floor = p["wall"].Gt, p["floor"].Gt
        A = b * h
        gj_c = 4 * A ** 2 / (2 * h / walls + b / floor + b / (p["roof"].Gt * tw["roof_joint_factor"]))
        gj_o = p["floor"].plate_gj(b) + 2 * p["wall"].plate_gj(h)
        return dict(body=gj_c if lid_structural else gj_o, closed=gj_c, open=gj_o, A=A, h=h, b=b)

    def segments(self, lid_structural: bool) -> list[tuple[float, float, float]]:
        """(x0, x1, GJ) per bay between stations: the body box is the same cell all along."""
        gj = self.box_gj(lid_structural)["body"]
        return [(x0, x1, gj) for x0, x1 in zip(self.stations, self.stations[1:])]

    def _run(self, an, items, acc, **kw) -> dict:
        res, _ = an.run_static(items, acc, **kw)
        signed = [-res.forces[k][3] for k, _, _ in an.fm.body_elements]
        tor = [(x0, x1, abs(t)) for (k, x0, x1), t in zip(an.fm.body_elements, signed)]
        xs = [x0 for _, x0, _ in an.fm.body_elements] + [an.fm.body_elements[-1][2]]
        per_station = {round(x): abs((signed[i - 1] if i > 0 else 0.0) - (signed[i] if i < len(signed) else 0.0)) / 1e6
                       for i, x in enumerate(xs)}
        posts = [(x, sd, -res.forces[k][0], where) for k, x, sd, where in an.fm.mount_posts]   # + tension: the bolt is pulled
        gm = max(an.stresses(res).items(), key=lambda kv: kv[1]["eq"])
        worst = max(posts, key=lambda p: abs(p[2]))
        return dict(chassis_deg=an.twist(res), max_body_torque_knm=max(t for *_, t in tor) / 1e6,
                    station_torque_knm=per_station, segments=[dict(x0=x0, x1=x1, torque_knm=t / 1e6) for x0, x1, t in tor],
                    mount_force_n=abs(worst[2]), mount_worst=[worst[0], worst[1], worst[3]], mount_pulled=worst[2] > 0,
                    chassis_mpa=gm[1]["eq"], chassis_member=gm[0])

    def twist(self) -> dict:
        """LC5a (one wheel in a hole, travelling) and LC5b (one corner steady wound to 875 kg at tare, parked) with the
        body tied to the chassis at every station, for both bounds on the roof. LC5a takes the case and diagonal with the
        most chassis twist in the bare-frame analysis. The body's share is the part of the bare chassis twist it
        removes: 1 - (twist with the body) / (bare twist)."""
        from .chassis_fea import Analysis
        ch = self.lay.chassis
        bare = self.tr.chassis_results(self.lay)
        case_id, diag = bare["twist"]["case"].split(" (diagonal ")
        sgn = 1 if diag.startswith("A") else -1
        lcs = {l["id"]: l for l in ch.data["load_cases"]}
        lc, lb = lcs["LC5a"], lcs["LC5b"]
        hub_y = ch.suspension[0]["contact"][1]
        out = dict(case=bare["twist"]["case"], torque_knm=lc["torque_nmm"] / 1e6, bare_deg=bare["twist"]["deg"],
                   bare_lc5a_mpa=bare["governing"]["LC5a"]["eq"], bare_lc5b_mpa=bare["governing"]["LC5b"]["eq"])
        tc1 = next(c for c in self.tr.cases if c.id == "TC1")
        for key, lid in (("open", False), ("closed", True)):
            segs = self.segments(lid)
            an = Analysis(self.lay, self.tr, ch, body=segs)
            c, items, _, _ = next(t for t in an.scaled_cases([case_id]))
            a = self._run(an, items, lc["accel"][0], twist_n=sgn * lc["torque_nmm"] / (2 * abs(hub_y)))
            b = self._run(an, an.items(tc1), lb["accel"][0], steady_n=lb["steady_kg"] * G)
            a["share"] = 1 - a["chassis_deg"] / out["bare_deg"]
            a["torque_share"] = a["max_body_torque_knm"] / out["torque_knm"]
            a["chassis_util"] = a["chassis_mpa"] / (ch.fy / lc["factor"])
            b["chassis_util"] = b["chassis_mpa"] / (ch.fy / lb["factor"])
            a["gj"] = [dict(x0=x0, x1=x1, gj=gj) for x0, x1, gj in segs]
            out[key] = a
            out[key + "_lc5b"] = b
        # the body checks take the bound that loads the body most, per quantity
        both = [out["open"], out["closed"]]
        out["design"] = dict(max_body_torque_knm=max(r["max_body_torque_knm"] for r in both),
                             mount_force_n=max(r["mount_force_n"] for r in both),
                             mount_force_lc5b_n=max(out[k]["mount_force_n"] for k in ("open_lc5b", "closed_lc5b")))
        return out

    # ------------------------------------------------------------------ joints, portal and mounts under the body's share
    @cached_property
    def tw(self) -> dict:
        return self.twist()

    def joints(self) -> list[dict]:
        """Shear flow q = T / 2A from the body's share of LC5a in the skins and the bonded joints, with the larger body
        torque of the two bounds on the roof."""
        gj, cr, p = self.box_gj(True), self.crit, self.p
        T = self.tw["design"]["max_body_torque_knm"] * 1e6
        q = T / (2 * gj["A"])
        bond = self.d["twist"]["bond_shear_strength"] * self.d["twist"]["bond_width"]
        rows = []
        for key, what in (("wall", "Side wall skins in shear"), ("floor", "Floor skins in shear"), ("roof", "Roof skins in shear")):
            pn = p[key]
            tau = q / (pn.t1 + pn.t2)
            allow = cr["skin_factor"] * pn.ult / math.sqrt(3)
            rows.append(dict(id=f"JNT-{key}", what=what, value=tau, unit="MPa", limit=allow, util=tau / allow))
        rows.append(dict(id="JNT-bond", what="Bonded joiner leg, MS polymer, shear flow per mm", value=q, unit="N/mm",
                         limit=0.5 * bond, util=q / (0.5 * bond)))
        return rows

    def end_wall(self) -> dict:
        """The rear wall as the box's rear diaphragm (report 12 section 5). The torque the floor bolts put into the box at the
        stations in its rear half has to be held in shape at the rear wall, so the wall racks under F = T / 2h, h the
        cell height, for LC5a and LC5b and both bounds on the roof. The 2,330 mm panel less its openings at the worst
        height takes F in shear in its skins, and its bonded joiners take F along their length."""
        V, cr, tw = self.V, self.crit, self.d["twist"]
        gj = self.box_gj(True)
        x_mid = (V["body_x0"] + V["body_x1"]) / 2
        runs = {k: self.tw[k] for k in ("open", "closed", "open_lc5b", "closed_lc5b")}
        T_by = {k: sum(v for x, v in r["station_torque_knm"].items() if x >= x_mid) for k, r in runs.items()}
        gov = max(T_by, key=T_by.get)
        T = T_by[gov] * 1e6
        F = T / (2 * gj["h"])
        wl = self.p["wall"]
        rear = [o for o in self.openings() if o["wall"] == "rear"]
        cut = max((sum(o["w"] for o in rear if o["z0"] <= z <= o["z1"]) for z in {q["z0"] for q in rear} | {q["z1"] for q in rear}), default=0.0)
        w = 2 * V["half_in"] - cut
        tau = F / (w * (wl.t1 + wl.t2))
        allow = cr["skin_factor"] * wl.ult / math.sqrt(3)
        q = F / (2 * V["half_in"])
        bond = 0.5 * tw["bond_shear_strength"] * tw["bond_width"]
        util = max(tau / allow, q / bond)
        return dict(case=gov, torque_knm=T / 1e6, force_n=F, width_mm=w, tau_mpa=tau, allow_mpa=allow, q_n_mm=q, bond_n_mm=bond,
                    util=util, governing="skins in shear" if tau / allow >= q / bond else "bonded joiner")

    def face_capacity(self) -> float:
        """Yield-line capacity of the 3 mm raiser or outrigger top face under the Hollo-Bolt's flared sleeve (CIDECT
        design guide 3, transverse plate on an RHS face, with beta = eta = sleeve diameter / face width)."""
        m = self.d["mounts"]
        beta = m["collar"] / m["face_b"]
        return m["fy"] * m["face_t"] ** 2 / (1 - beta) * (2 * beta + 4 * math.sqrt(1 - beta))

    def mounts(self) -> dict:
        """Hollo-Bolt forces at the 36 mounts under LC2 to LC5a (report 12 section 4). One bolt into each raiser and
        each outrigger tip at every station. Shear shares equally. The LC4 overturning moment shares by the bolts' Y
        squared. The twist moment the body takes off the chassis at a station goes to that station's two raiser
        bolts as a couple, with no help from the outrigger tips (conservative). Weight relieves each bolt by its
        share of 1 g."""
        md, V = self.d["mounts"], self.V
        mt = self.mounted
        m, zc = mt["kg"], mt["cog_z"]
        n_st = len(self.stations)
        n = n_st * md["per_station"]
        ys = [V["rail_c"], md["outrigger_tip_y"]]
        sum_y2 = n_st * 2 * sum(y * y for y in ys)
        W1 = m * G / n                                     # 1 g share per bolt
        h = zc - V["floor_underside_z"]
        cases = {}
        cases["LC2"] = dict(shear=0.0, tension=0.0, note=f"3 g down: every bolt in compression, {3 * W1 / 1000:.2f} kN")
        cases["LC3"] = dict(shear=0.8 * m * G / n, tension=0.0, note="0.8 g braking shared by every bolt")
        M4 = 0.5 * m * G * h
        t4 = M4 * md["outrigger_tip_y"] / sum_y2 - W1
        cases["LC4"] = dict(shear=0.5 * m * G / n, tension=max(0.0, t4), note=f"0.5 g sideways, overturning {M4 / 1e6:.1f} kNm")
        W1t = mt["cases"]["TC1"]["kg"] * G / n
        f5b = self.tw["design"]["mount_force_lc5b_n"]
        cases["LC5b"] = dict(shear=0.0, tension=max(0.0, f5b - W1t),
                             note=(f"a corner steady wound to 875 kg at tare: the largest bolt force {f5b / 1000:.2f} kN, either bound "
                                   f"on the roof, less its 1 g share of the tare body's weight"))
        f5 = self.tw["design"]["mount_force_n"]
        cases["LC5a"] = dict(shear=0.0, tension=max(0.0, f5 - W1),
                             note=(f"the largest raiser bolt force in the frame model with the body, {f5 / 1000:.2f} kN, either bound "
                                   f"on the roof, less its 1 g share of weight"))
        face = self.face_capacity()
        worst_t = max(c["tension"] for c in cases.values())
        worst_s = max(c["shear"] for c in cases.values())
        u_t = worst_t / md["swl_tension_n"]
        u_f = worst_t / (face / 1.5)
        u_s = worst_s / md["swl_shear_n"]
        flat = md["face_b"] - 4 * md["face_t"]
        hb = dict(util_tension=u_t, util_face=u_f, util_shear=u_s, util=max(u_t, u_f, u_s), fits=md["collar"] <= flat,
                  passes=max(u_t, u_f, u_s) <= 1.0 and md["collar"] <= flat)
        # the fallback: M12 8.8 into a welded nut plate
        fb = md["fallback"]
        bolt = fb["As"] * fb["fu"] / fb["bolt_factor"]
        pl = fb["plate"]
        plate = 1.5 * pl["fy"] * pl["l"] * pl["t"] ** 2 / 6 / (pl["span"] / 4) / 1.5     # bending capacity at fy / 1.5
        weld = 0.6 * fb["weld"]["fuw"] * 0.7 * fb["weld"]["leg"] * fb["weld"]["length"] * 0.8 / 1.5
        sp = fb["spreader"]
        punch = 4 * sp["side"] * (self.p["floor"].t1 * sp["skin_shear"] + self.p["floor"].c * sp["insert_shear"]) / 2
        fbu = dict(bolt=worst_t / bolt, plate=worst_t / plate, weld=worst_t / weld, pull_through=worst_t / punch, shear=worst_s / (0.62 * fb["As"] * fb["fu"] / 3))
        gov = max(fbu, key=fbu.get)
        use = "fallback" if md.get("design") == "nut_plate" or not hb["passes"] else "HB10"
        return dict(bolts=n, mass_kg=m, cog_z=zc, case=mt["worst"], scale=mt["scale"], cases=cases, face_n=face,
                    tension_n=worst_t, shear_n=worst_s, hb10=hb, flat_mm=flat, fallback=dict(utils=fbu, governing=gov, util=fbu[gov],
                    bolt_n=bolt, plate_n=plate, weld_n=weld, pull_through_n=punch), uses=use,
                    util=hb["util"] if use == "HB10" else fbu[gov],
                    governing=("HB10" if use == "HB10" else f"M12 8.8 nut plate fallback, {gov.replace('_', ' ')}"))

    # ------------------------------------------------------------------ openings (report 12 sections 5 and 7)
    def openings(self) -> list[dict]:
        """Every opening as a rectangle on its wall, in the wall's own (u, z) coordinates: u along the trailer from the
        body front for the side walls, Y for the end walls. The kitchen and the entry door follow their blocks."""
        V, out = self.V, []
        for o in self.d["openings"]:
            r = dict(o)
            if o.get("from"):
                b = self.lay.find(o["from"])
                if o["wall"] in ("kerb", "road"):
                    r["x"] = b.box[0] - V["body_x0"] + (o["w"] - (b.box[3] - b.box[0])) / -2 if o["from"] == "BD-07" else b.box[0] - V["body_x0"]
                    r["w"] = o["w"] if o["from"] == "BD-07" else b.box[3] - b.box[0]
                else:
                    r["y"] = (b.box[1] + b.box[4]) / 2
                    r["w"] = b.box[4] - b.box[1]
            u0 = r["x"] if o["wall"] in ("kerb", "road") else r["y"] - r["w"] / 2
            r.update(u0=u0, u1=u0 + r["w"], z0=r["z"], z1=r["z"] + r["h"], area_m2=r["w"] * r["h"] / 1e6)
            out.append(r)
        # a gland larger than the rule's size is an opening too (F4-05): its centre in DIM-01 (data/services.yaml)
        for g in yaml.safe_load((DATA / "services.yaml").read_text())["glands"]:
            w, h = g.get("w", g["d"]), g.get("h", g["d"])
            if g["at"] not in ("kerb", "road", "front", "rear") or max(w, h) <= self.d["rules"]["gland_mm"]:
                continue
            u0 = (g["x"] - V["body_x0"] if g["at"] in ("kerb", "road") else g["y"]) - w / 2
            z0 = g["z"] - V["floor_z"] - h / 2
            out.append(dict(id=g["id"], wall=g["at"], name=g["what"], w=w, h=h, x=u0, z=z0, proj=g.get("proj"), gland=True,
                            u0=u0, u1=u0 + w, z0=z0, z1=z0 + h, area_m2=w * h / 1e6))
        return out

    def openings_check(self) -> dict:
        """Report 12's rules: 300 mm of full wall between neighbouring openings, 150 mm to a panel edge and nothing within
        300 mm of the rear corners."""
        V, ru = self.V, self.d["rules"]
        ops = self.openings()
        probs, worst = [], math.inf
        L, Hh = V["body_length"], V["interior_h"]
        for wall in ("kerb", "road", "front", "rear"):
            w = sorted((o for o in ops if o["wall"] == wall), key=lambda o: o["u0"])
            lo, hi = (0.0, L) if wall in ("kerb", "road") else (-V["half_in"], V["half_in"])
            for o in w:
                e = min(o["u0"] - lo, hi - o["u1"], Hh - o["z1"])
                if wall in ("kerb", "road"):
                    e = min(e, (hi - ru["rear_corner_mm"]) - o["u1"] + ru["edge_mm"])
                worst = min(worst, e - ru["edge_mm"])
                if e < ru["edge_mm"] - 1e-6:
                    probs.append(f"{o['id']} is {e:.0f} mm from a panel edge or the rear corner rule")
            for i, a in enumerate(w):
                for b in w[i + 1:]:
                    overlap_z = min(a["z1"], b["z1"]) - max(a["z0"], b["z0"])
                    du = b["u0"] - a["u1"]
                    dz = max(b["z0"] - a["z1"], a["z0"] - b["z1"])
                    gap = du if overlap_z > 0 else (max(du, dz) if du > 0 else dz)
                    worst = min(worst, gap - ru["between_mm"])
                    if gap < ru["between_mm"] - 1e-6:
                        probs.append(f"{a['id']} and {b['id']} on the {wall} wall are {gap:.0f} mm apart")
        return dict(ok=not probs, problems=probs, margin_mm=worst, count=len(ops))

    # ------------------------------------------------------------------ everything, for the build and the checks
    def results(self) -> dict:
        panels = self.panel_checks()
        return dict(panels=panels, deflections=self.deflections(), roof=self.roof(), inserts=self.inserts(), cradle=self.cradle(),
                    thermal=self.cold_bridge(), awning=self.awning(), members=self.members_clear(), plates=self.plate_checks(),
                    openings=self.openings(), openings_check=self.openings_check(),
                    twist=self.tw, gj=self.box_gj(True),
                    joints=self.joints(), end_wall=self.end_wall(), mounts=self.mounts(),
                    mounted=self.mounted, panel_data={k: dict(name=p.name, D_knm2_per_m=p.D / 1e6, S_kn_per_m=p.S,
                                                             wrinkling_mpa=p.wrinkling, kg_m2=p.d["kg_m2"], t=p.d["t"])
                                                      for k, p in self.p.items()})


def check_row(c, res: dict) -> dict:
    """A trailer check row for a body_* check (data/checks.yaml)."""
    item = c.body["item"] if c.body else None
    if c.type == "body_panel":
        r = next(p for p in res["panels"] if p["id"] == item)
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=f"{r['governing']}, {r['case']}",
                    detail=(f"{r['what']}: skin {r['skin_mpa']:.1f} MPa, core shear {r['core_mpa']:.3f} MPa, utilisation "
                            f"{r['util']:.2f} ({r['governing']}){', ' + r['extra'] if r['extra'] else ''}"))
    if c.type == "body_deflection":
        r = next(d for d in res["deflections"] if d["id"] == item)
        return dict(limit=f"<= {r['limit_mm']:.1f} mm", measured=round(r["mm"], 1), unit="mm", margin=round(r["limit_mm"] - r["mm"], 1),
                    ok=r["mm"] <= r["limit_mm"], governing=r["what"], detail=f"{r['what']}: {r['mm']:.1f} mm against {r['limit_mm']:.1f} mm")
    if c.type == "body_insert":
        r = max(res["inserts"], key=lambda r: r["util"])
        return dict(limit="<= half the rated load", measured=round(r["n"] / 1000, 2), unit="kN", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=r["what"],
                    detail=". ".join(f"{i['what']}: {i['n'] / 1000:.2f} kN against {i['rated_n'] / 2000:.2f} kN ({i['case']})" for i in res["inserts"]))
    if c.type == "body_cradle":
        r = res["cradle"]
        u = r["utils"]
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3), ok=r["util"] <= 1.0,
                    governing=r["governing"],
                    detail=(f"{r['mass_kg']:.0f} kg, its centre of gravity {r['offset_mm']:.0f} mm behind the rear wall. Wall bolts: {r['tension_n'] / 1000:.2f} kN "
                            f"of tension against half the {r['pull_rated_n'] / 1000:.0f} kN pull-through ({u['bolt_tension']:.2f}), {r['shear_n'] / 1000:.2f} kN of "
                            f"shear against half of {r['shear_rated_n'] / 1000:.0f} kN ({u['bolt_shear']:.2f}). Each stay, {r['stays']['name']}, "
                            f"{r['stay_n'] / 1000:.2f} kN at 3 g against {r['stay_pcr_n'] / 1000:.1f} kN to buckle over {r['stays']['L']:,.0f} mm "
                            f"({u['stay_buckling']:.2f} with a factor of {r['stays']['buckling_factor']:g})"))
    if c.type == "body_thermal":
        t = res["thermal"]
        need = max(t["need"], t["need_gen"])
        m = t["tsi_min"] - need
        e, wh = t["ends"], t["where"]
        names = dict(mid="over a member at mid-length", foot="over a member at its foot", head="over a member at its head",
                     beside=f"over {t['beside_member']} at mid-length, beside its neighbours", joiner="over a joiner's foam cover")
        return dict(limit=f">= {need:.0f} C, the dew point {t['dew']:.0f} C plus 4 K", measured=round(t["tsi_min"], 1), unit="C",
                    margin=round(m, 1), ok=m >= -1e-6,
                    governing=f"inside surface {names[t['governs']]}, Rsi {t['rsi']:g} m2K/W, {t['t_out']:.0f} C outside, {t['t_in']:.0f} C inside",
                    detail=(f"{t['member']} with {t['brk']:g} mm of XPS behind it ({', '.join(t['members'])}, {t['length_m']:.1f} m in all), at ISO "
                            f"13788's Rsi of {t['rsi']:g} m2K/W. On the design cold night the inside surface over it is {t['tsi_mid']:.1f} C at "
                            f"mid-length and the member {t['t_member']:.1f} C"
                            + f" in a plain wall. Across each member as it stands, with W1's and W2's {t['insert_mm']:.0f} to 28 mm side inserts "
                            f"({t['insert_k']:g} W/mK) and the windows beyond them (U {t['window_u']:g} W/m2K, est.), the doors' insert strips taken as "
                            f"rigid PVC and the doors beyond them (U {t['door_u']:g} W/m2K, est.), and the two members {t['pair_gap_mm']:.1f} mm apart "
                            f"behind the bed with the H200 fill between them, the coldest is {t['beside_member']} at {wh['beside']:.1f} C, every neighbour taken at its height"
                            + f". Each member stands on a {e['foot']['block_w']:g} mm wide rigid PVC bearing block {e['foot']['clear_mm']:g} mm above the "
                            f"floor joiner's inner leg, which wraps the inner skin to {e['foot']['leg_mm']:g} mm, so its foot is {e['foot']['at_mm']:g} mm "
                            f"above the wall's bottom edge and no leg overlaps it. With the joiner taken at the outside air, through the block, the XPS "
                            f"and the inner skin, the surface is {e['foot']['tsi']:.1f} C at the foot, and {e['head']['tsi']:.1f} C at the head, on a "
                            f"{e['head']['block_w']:g} mm rigid PVC pad {e['head']['gap_mm']:g} mm under the top insert strip and {e['head']['clear_mm']:g} mm "
                            f"below the roof joiner's leg (the member a fin of "
                            f"{t['fin_mm']:.0f} mm). The joiners themselves, taken at the outside air under {t['cover_mm']:g} mm of closed-cell foam, "
                            f"{wh['joiner']:.1f} C. The plain wall is {t['tsi_plain']:.1f} C. On the generators, ahead of the drawbar or behind the trailer, "
                            f"e2 fans A and B and the RESPA-CF2, {t['gen']['ahead']['q']:.0f} m3/h, hold the dew point at {t['gen']['ahead']['dew']:.1f} C, "
                            f"and off the kerb side, fans A and B stopped, the RESPA-CF2 alone, {t['gen']['kerb']['q']:.0f} m3/h, at "
                            f"{t['gen']['kerb']['dew']:.1f} C, so {t['need_gen']:.1f} C there (F5-04). Each metre of member "
                            f"adds {t['psi']:.3f} W/K of heat loss on ISO 6946's film, {t['w_k']:.2f} W/K in all, {100 * t['w_k'] / t['bare']:.1f} % of "
                            f"the bare panels' {t['bare']:g} W/K beside report 19's {t['bridges']:g} W/K for the joiners, mount bolts and inserts"))
    if c.type == "body_members":
        r = res["members"]
        tight = min(r["rows"], key=lambda q: q["gap_mm"])
        si = r["side_inserts"]
        return dict(limit=f">= {r['clear_mm']:g} mm clear, bays <= {r['pitch']:,.0f} mm", measured=round(r["worst_mm"], 0), unit="mm",
                    margin=round(r["worst_mm"] - r["clear_mm"], 0), ok=r["ok"], governing=f"{tight['member']} to {tight['to']}",
                    detail=(". ".join(f"{q['member']} on the {q['wall']} side at X {q['x']:,.0f}: {q['gap_mm']:.0f} mm from {q['to']}"
                                      + (f", and it shares its routed channel with {' and '.join(q['shares'])}'s side insert" if q["shares"] else "")
                                      for q in r["rows"])
                            + f". The widest bay is {r['bays']['kerb']:,.0f} mm on the kerb side and {r['bays']['road']:,.0f} mm on the road side, "
                            f"against {r['pitch']:,.0f} mm. The rule's exception: at W1's and W2's sides the insert fills the core from the cut-out "
                            f"to the hardpoint, {min(s['width_mm'] for s in si):.0f} to {max(s['width_mm'] for s in si):.0f} mm, at least "
                            f"{r['insert_min_mm']:g} mm, so an S4's clamp bears on a solid edge and no XPS is left to rout between them"
                            + "".join(f". Member to member the rule is the same {r['clear_mm']:g} mm, or one routed channel for both with an "
                                      f"H200 fill bonded between them: {p['members'][0]} and {p['members'][1]}, {p['gap_mm']:.1f} mm apart on the "
                                      f"{p['wall']} side, share one" for p in r["shared"])
                            + (". " + ". ".join(r["problems"]) if r["problems"] else "")))
    if c.type in ("body_plate_defl", "body_plate_strength"):
        p = res["plates"]
        if c.type == "body_plate_defl":
            k, v = max(p["defl"].items(), key=lambda kv: kv[1]["w_s"])
            ws = p["ws"]["kpa"]
            bays = ". ".join(f"The {w2} wall's largest deflection in each bay: " + ", ".join(f"{b['w_mm'] * ws:.1f} mm from X {b['x0']:,.0f} to {b['x1']:,.0f}" + (f" ({' '.join(b['openings'])})" if b["openings"] else "")
                                                    for b in q["bays"] if b["x1"] - b["x0"] > 60) for w2, q in p["defl"].items())
            return dict(limit=f"<= {p['limit_mm']:.1f} mm", measured=round(v["w_s"], 1), unit="mm", margin=round(p["limit_mm"] - v["w_s"], 1),
                        ok=v["w_s"] <= p["limit_mm"] + 1e-9, governing=f"the {k} wall at X {v['at_x']:,.0f}, {v['at_z']:,.0f} mm above the floor",
                        detail=(f"each side wall as a Mindlin plate (MITC4, {p['step']:g} mm elements) from the front wall to the rear wall, every "
                                f"opening cut out with its wind load on its edges, the members as beams with their own bending, shear and torsion "
                                f"(EI {p['props']['EI'] / 1e6:,.0f} N m2, GJ {p['props']['GJ'] / 1e6:,.0f} N m2), in region B's 25-year wind, {ws:.2f} kPa net. "
                                f"{bays}"))
        k, v = max(p["strength"].items(), key=lambda kv: kv[1]["util"])
        return dict(limit="<= 1.00 utilisation", measured=round(v["util"], 3), unit="", margin=round(1 - v["util"], 3), ok=v["util"] <= 1.0,
                    governing=f"the {k} wall, {v['governing']}",
                    detail=(f"the plates of BDY-24 at {p['wu']['kpa']:.2f} kPa net, {p['wu']['V']:.0f} m/s. The skins and the core are read "
                            f"{p['corner']:g} mm or more from the cut-outs' corners (F5-02): the model cuts each corner square, where the stress grows "
                            f"without limit as the mesh is refined, and the cut-outs' real corners are radiused (CT-201). "
                            + ". ".join(f"The {w2} wall: the worst member {q['s_member']:.0f} MPa ({q['utils']['member']:.2f}), skins {q['s_skin']:.1f} MPa "
                                        f"({q['utils']['skins']:.2f}) at X {q['m_at'][0]:,.0f}, {q['m_at'][1]:,.0f} mm up, core shear {q['tau']:.3f} MPa "
                                        f"({q['utils']['core']:.2f}) at X {q['q_at'][0]:,.0f}, {q['q_at'][1]:,.0f} mm up, the XPS behind a member {q['xps']:.3f} MPa ({q['utils']['xps']:.2f}), and a member's end shear "
                                        f"{q['v_end']:.0f} N through its rigid PVC block or pad, {q['blk']:.1f} MPa ({q['utils']['blocks']:.2f} of half "
                                        f"its {p['block_shear']:g} MPa, est.)" for w2, q in p["strength"].items())
                            + f". Strapped down, at STB-05's {p['v500']:.1f} m/s gust, the {k} wall's "
                            f"{dict(member='worst member', skins='skins', core='core shear', xps='XPS behind a member', blocks='end blocks')[v['governing']]} "
                            f"works at {v['at500']['util']:.2f}, a factor of {v['at500']['factor']:.2f} on its {v['at500']['on']}. H23 checks the walls' "
                            f"strength at {p['wu']['V']:.0f} m/s, so this figure is reported"))
    if c.type == "body_awning":
        a = res["awning"]
        return dict(limit="reported", measured=round(a["reach_mm"], 0), unit="mm", margin=None, ok=a["reach_mm"] >= 0,
                    governing=f"the legs at a {a['pitch_deg']:g} degree pitch on level ground",
                    detail=(f"the canopy leaves the case at Z {a['z_case']:,.0f} and runs out {a['extension_mm']:,.0f} mm. With the legs at full reach, "
                            f"{a['leg_max_mm']:,.0f} mm (est.), the lead bar stands at Z {a['z_bar_max']:,.0f} and the canopy falls "
                            f"{a['pitch_full_deg']:.1f} degrees. Set for {a['pitch_deg']:g} degrees, the lead bar stands at Z {a['z_bar']:,.0f} on legs "
                            f"of {a['leg_mm']:,.0f} mm, which keep {a['reach_mm']:,.0f} mm of reach for ground that falls away. Where it falls further, "
                            f"the legs at full reach give a steeper pitch"))
    if c.type == "body_roof":
        r = res["roof"]
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3), ok=r["util"] <= 1.0,
                    governing="roof-to-wall joiner bond in tension",
                    detail=(f"{r['uplift_n'] / 1000:.2f} kN of uplift on the roof ({r['roof_kg']:.0f} kg with the solar array) over "
                            f"{r['perimeter_mm'] / 1000:.1f} m of joiner, {r['q_n_mm']:.2f} N/mm against {r['allow_n_mm']:.0f} N/mm, "
                            "taking none of the roof's weight off"))
    if c.type == "body_twist":
        t = res["twist"]
        o, cl = t["open"], t["closed"]
        return dict(limit="reported", measured=round(cl["share"] * 100, 1), unit="%", margin=None, ok=True,
                    governing=t["case"],
                    detail=(f"LC5a {t['torque_knm']:.1f} kNm, {t['case']}. Bare chassis {t['bare_deg']:.3f} degree. Roof bonded "
                            f"(the design): the body takes {100 * cl['share']:.0f} %, chassis {cl['chassis_deg']:.3f} degree. Lower bound, "
                            f"roof joint neglected: {100 * o['share']:.0f} %, chassis {o['chassis_deg']:.3f} degree"))
    if c.type == "body_joint":
        r = max(res["joints"], key=lambda r: r["util"])
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=r["what"],
                    detail=". ".join(f"{j['what']} {j['value']:.2f} {j['unit']} against {j['limit']:.2f}" for j in res["joints"]))
    if c.type == "body_end_wall":
        e = res["end_wall"]
        return dict(limit="<= 1.00 utilisation", measured=round(e["util"], 3), unit="", margin=round(1 - e["util"], 3), ok=e["util"] <= 1.0,
                    governing=e["governing"],
                    detail=(f"{e['torque_knm']:.1f} kNm into the rear half of the box ({e['case']}), racking {e['force_n'] / 1000:.2f} kN. Rear wall "
                            f"skins {e['tau_mpa']:.2f} MPa in shear against {e['allow_mpa']:.1f} MPa over {e['width_mm']:.0f} mm of full panel, "
                            f"joiner {e['q_n_mm']:.2f} N/mm against {e['bond_n_mm']:.1f} N/mm"))
    if c.type == "body_mount":
        m = res["mounts"]
        hb, fb = m["hb10"], m["fallback"]
        return dict(limit="<= 1.00 utilisation", measured=round(m["util"], 3), unit="", margin=round(1 - m["util"], 3),
                    ok=m["util"] <= 1.0, governing=m["governing"],
                    detail=(f"{m['bolts']} mounts on {m['mass_kg']:.0f} kg ({m['case']} at the ATM): worst tension {m['tension_n'] / 1000:.2f} kN, "
                            f"shear {m['shear_n'] / 1000:.2f} kN. HB10: {hb['util']:.2f} of its 8.5 kN safe working load"
                            f"{'. The design uses the M12 8.8 bolt into a welded nut plate (CH-P14)' if m['uses'] == 'fallback' else ''}: bolt "
                            f"{fb['bolt_n'] / 1000:.1f} kN, plate {fb['plate_n'] / 1000:.1f} kN, weld {fb['weld_n'] / 1000:.1f} kN, floor pull-through "
                            f"{fb['pull_through_n'] / 1000:.1f} kN, governing {fb['governing'].replace('_', ' ')} at {fb['util']:.2f}. "
                            + " ".join(f"{k}: {v['note']}." for k, v in m["cases"].items())))
    if c.type == "body_openings":
        o = res["openings_check"]
        return dict(limit=">= 300 mm between, 150 mm to an edge", measured=round(o["margin_mm"], 0), unit="mm", margin=round(o["margin_mm"], 0),
                    ok=o["ok"], governing=". ".join(o["problems"][:2]) or "every rule met",
                    detail=(f"{o['count']} openings. " + (". ".join(o["problems"]) if o["problems"] else
                            f"Every opening keeps the spacing rules, the tightest by {o['margin_mm']:.0f} mm")))
    raise ValueError(f"unknown body check type {c.type}")
