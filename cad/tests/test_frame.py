"""The 3D frame solver (cad/frame.py) against closed-form results."""
import math

import numpy as np
import pytest

from cad.frame import E_STEEL, G_STEEL, Frame, Section, end_actions

SEC = Section("RHS 150x50x3", A=1140.0, I_strong=2.99e6, I_weak=0.526e6, J=1.50e6)
L, P, T = 1000.0, 1000.0, 1.0e6


def _cantilever(direction, depth_dir, n=4):
    """Cantilever along `direction`, fixed at the origin, with n elements."""
    f = Frame()
    d = np.asarray(direction, float) / np.linalg.norm(direction)
    pts = [tuple(d * L * k / n) for k in range(n + 1)]
    idx = f.chain(pts, SEC, depth_dir, "beam")
    return f, idx, d


@pytest.mark.parametrize("direction,depth_dir", [((1, 0, 0), (0, 0, 1)), ((0, 1, 0), (0, 0, 1)), ((3, 4, 0), (0, 0, 1)),
                                                 ((1, 0, 0), (0, 1, 0))])
def test_cantilever_tip_deflection_and_root_moment(direction, depth_dir):
    f, idx, d = _cantilever(direction, depth_dir)
    loads = np.zeros(6 * len(f.nodes))
    loads[6 * idx[-1] + 2] = -P  # downward tip load
    res = f.solve(loads, [(idx[0], k) for k in range(6)])
    strong = np.allclose(depth_dir, (0, 0, 1))
    I = SEC.I_strong if strong else SEC.I_weak
    assert res.u[6 * idx[-1] + 2] == pytest.approx(-P * L ** 3 / (3 * E_STEEL * I), rel=1e-9)
    root = end_actions(res.forces[0])[0]
    m = abs(root["My"]) if strong else abs(root["Mz"])
    assert m == pytest.approx(P * L, rel=1e-9)
    assert res.reactions[(idx[0], 2)] == pytest.approx(P, rel=1e-9)


def test_simply_supported_midspan_moment_and_deflection():
    f = Frame()
    n = 10
    idx = f.chain([(L * k / n, 0, 0) for k in range(n + 1)], SEC, (0, 0, 1), "beam")
    loads = np.zeros(6 * len(f.nodes))
    loads[6 * idx[n // 2] + 2] = -P
    sup = [(idx[0], 0), (idx[0], 1), (idx[0], 2), (idx[0], 3), (idx[-1], 1), (idx[-1], 2)]
    res = f.solve(loads, sup)
    assert res.u[6 * idx[n // 2] + 2] == pytest.approx(-P * L ** 3 / (48 * E_STEEL * SEC.I_strong), rel=1e-9)
    mid = end_actions(res.forces[n // 2 - 1])[1]
    assert abs(mid["My"]) == pytest.approx(P * L / 4, rel=1e-9)


def test_torsion_twist_and_reaction():
    f, idx, d = _cantilever((1, 0, 0), (0, 0, 1))
    loads = np.zeros(6 * len(f.nodes))
    loads[6 * idx[-1] + 3] = T
    res = f.solve(loads, [(idx[0], k) for k in range(6)])
    assert res.u[6 * idx[-1] + 3] == pytest.approx(T * L / (G_STEEL * SEC.J), rel=1e-9)
    assert abs(end_actions(res.forces[0])[0]["T"]) == pytest.approx(T, rel=1e-9)
    assert res.reactions[(idx[0], 3)] == pytest.approx(-T, rel=1e-9)


def test_portal_frame_equilibrium():
    """A three-dimensional frame: the reactions balance the loads in force and moment."""
    f = Frame()
    a, b, c, e = (f.node(p) for p in ((0, 0, 0), (0, 0, 800), (1200, 300, 800), (1200, 300, 0)))
    f.add(a, b, SEC, (1, 0, 0), "post")
    f.add(b, c, SEC, (0, 0, 1), "beam")
    f.add(c, e, SEC, (1, 0, 0), "post")
    loads = np.zeros(6 * len(f.nodes))
    loads[6 * b:6 * b + 3] = (500.0, -300.0, -2000.0)
    loads[6 * c + 2] = -1500.0
    sup = [(a, k) for k in range(6)] + [(e, k) for k in range(6)]
    res = f.solve(loads, sup)
    xyz = np.asarray(f.nodes)
    F = np.zeros(3)
    M = np.zeros(3)
    for nd in range(len(f.nodes)):
        r = np.array([res.reactions.get((nd, k), 0.0) for k in range(6)])
        q = loads[6 * nd:6 * nd + 6] + r
        F += q[:3]
        M += q[3:] + np.cross(xyz[nd], q[:3])
    assert np.abs(F).max() < 1e-6 and np.abs(M).max() < 1e-3
    assert math.isfinite(res.u.max())
