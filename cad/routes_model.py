"""The 3D wiring and plumbing plans (H28). Every run of data/routes.yaml is swept at its real outside diameter along
the centreline cad/routes.py resolved on the layout, each bend at the radius the routing gave it (a fitting where a
pipe turns at one), in one colour per system. The body, the chassis and the fit-out are a faint ghost around them.

Two viewer models, trailer-electrical and trailer-plumbing, each with its part metadata for the hover tip and the
part card (cad/partsmeta.py, `route`), and build/trailer/routes.json: the runs, their schedules by group and by priced
line, the SVC check rows and the ten closest approaches, for the Electrical and Plumbing pages (Services.astro)."""
from __future__ import annotations

import json
import math
import re
import shutil
from pathlib import Path

from build123d import Box, Circle, Compound, Edge, Plane, Pos, Solid, Wire, sweep

from . import routes as R
from .model.prims import rgba

# colour and legend label per system, in the legend's order; the colours are the models' and the drawings'
SYSTEM_STYLE = {
    "dc48": ("#d62728", "48 V DC"),
    "pv": ("#ff7f0e", "PV strings"),
    "dc24": ("#c9a800", "24 V DC"),
    "dc12": ("#8c564b", "12 V DC"),
    "data": ("#9467bd", "Data and sensor cables"),
    "ac230": ("#2b2b2b", "230 V AC, in conduit under the floor"),
    "lamps": ("#e377c2", "Lamps and brakes (7-core)"),
    "fresh": ("#1f77b4", "Cold water"),
    "hot": ("#e6550d", "Hot water and the DauerShower loop"),
    "waste": ("#7f7f7f", "Wastes and drains"),
    "vent": ("#17becf", "Tank breathers"),
    "diesel": ("#2ca02c", "Diesel"),
    "refrigerant": ("#b87333", "Refrigerant line set"),
}
MODELS = {
    "trailer-electrical": dict(systems=R.ELECTRICAL, title="Electrical runs", drawing="CT-602"),
    "trailer-plumbing": dict(systems=("fresh", "hot", "waste", "vent", "diesel", "refrigerant"), title="Pipes and hoses", drawing="CT-612"),
}
GHOST_ALPHA = 0.07
GHOST_SKIP = ("keep_clear",)


def _name(res: dict, line: str) -> str:
    """A run end's name: its fixture's description, else its block's name, up to the first comma."""
    f = res["fixtures"].get(line)
    if f:
        return f["what"].split(",")[0]
    for b in res["blocks"]:
        if b.get("iid") == line or b.get("id") == line:
            return (b.get("name") or line).split(",")[0]
    return line


def circuit_of(run: dict, res: dict) -> str:
    """The tree's middle level: a 230 V run's circuit, a DC run's protective source, a pipe's source."""
    if run["system"] == "ac230":
        m = re.match(r"C\d+", run["id"])
        if m:
            loads = {c["id"]: c["load"] for c in res["svc"]["electrical"]["circuits"]}
            return f"Circuit {m.group(0)}, {loads.get(m.group(0), '').split(',')[0]}".rstrip(", ")
        return "Circuit supply, the MultiPlus-II and the board"
    return f"From {_name(res, run['from']['line'])}"


def _wire(run: dict):
    """The run's centreline as lines and the bends' arcs, tangent to each other."""
    pts = [tuple(p) for p in run["points"]]
    edges, cur = [], pts[0]
    for c in run["corners"]:
        if c.get("t", 0.0) <= 1e-6 or "p0" not in c:
            continue
        p0 = c["p0"] if math.dist(cur, c["p0"]) > 0.05 else cur
        if p0 is not cur:
            edges.append(Edge.make_line(cur, p0))
        edges.append(Edge.make_three_point_arc(p0, c["mid"], c["p1"]))
        cur = c["p1"]
    if math.dist(cur, pts[-1]) > 0.05:
        edges.append(Edge.make_line(cur, pts[-1]))
    return Wire(edges)


def run_solid(run: dict):
    """The run swept at its outside diameter. A path the sweep cannot follow falls back to one cylinder per straight of
    the dense centreline, so every run is in the model."""
    r = run["od"] / 2
    try:
        w = _wire(run)
        e0 = w.edges()[0]
        prof = Plane(origin=e0 @ 0, z_dir=e0 % 0) * Circle(r)
        s = sweep(prof, path=w)
        solid = s.solids()[0] if hasattr(s, "solids") and s.solids() else s
        valid = solid.is_valid if isinstance(solid.is_valid, bool) else solid.is_valid()  # a property in build123d 0.13
        if valid and solid.volume > 0:
            return solid
    except Exception:  # noqa: BLE001 - the fallback below keeps the run in the model
        pass
    cyl = []
    for a, b in R._segs(run["dense"]):
        d, ln = R._unit(R._sub(b, a))
        if ln > 0.2:
            cyl.append(Solid.make_cylinder(r, ln, Plane(origin=a, z_dir=d)))
    return Compound(children=cyl)


SHELL = ("BD-01", "BD-02", "BD-03", "BD-04")    # the floor, roof and walls: the ghost's boxes that keep their edges


def _ghost(res: dict) -> Compound:
    """The body, the chassis and the fit-out as faint boxes, for orientation."""
    kids = []
    for b in res["blocks"]:
        box = b.get("box")
        if not box or b.get("keep_clear"):
            continue
        dx, dy, dz = box[3] - box[0], box[4] - box[1], box[5] - box[2]
        if min(dx, dy, dz) <= 0.01:
            continue
        s = Pos((box[0] + box[3]) / 2, (box[1] + box[4]) / 2, (box[2] + box[5]) / 2) * Box(dx, dy, dz)
        s.label = f"{b['iid']} {b.get('name') or b['iid']}".replace("/", "-")
        s.color = rgba("#9aa5ad", GHOST_ALPHA)
        kids.append(s)
    return Compound(label="Ghost: body, chassis and fit-out", children=kids)


def _box(bx, label: str, colour: str, alpha: float):
    s = Pos((bx[0] + bx[3]) / 2, (bx[1] + bx[4]) / 2, (bx[2] + bx[5]) / 2) * Box(bx[3] - bx[0], bx[4] - bx[1], bx[5] - bx[2])
    s.label = label.replace("/", "-")
    s.color = rgba(colour, alpha)
    return s


def _supports(res: dict) -> Compound:
    """The cable supports the design adds (the SP fixtures) and the 230 V's conduit zones, above and under the floor,
    so the model shows what holds a cable where SVC-12 counts it held (I2-36)."""
    ns = res["ns"]
    kids = [_box(tuple(R._eval(v, ns) for v in z["box"]), f"Conduit: {z['what']}", "#4d4d4d", 0.35)
            for z in res["data"]["rules"].get("conduit", [])]
    kids += [_box(f["box"], f"{k} {f['what']}", "#aab7b8", 0.6) for k, f in res["fixtures"].items() if f.get("support")]
    return Compound(label="Cable supports and the 230 V conduits", children=kids)


def _frames(res: dict) -> Compound:
    """The floor's transit frames at their real depth (I2-34): each frame's body, its rim on the floor and its C wedge."""
    colours = {"body": ("#9aa5ad", 0.85), "rim": ("#c8cfd2", 0.85), "C wedge": ("#566573", 1.0)}
    kids = [_box(f["box"], f"{f['gland']} transit frame, {f['part']}", *colours[f["part"]]) for f in R.frame_solids(res)]
    return Compound(label="Floor transit frames G9, G15 and G20", children=kids)


def meta_of(run: dict, res: dict, drawing: str) -> dict:
    """A run's part metadata: the hover tip shows its id, what it feeds and its length; the card adds the rest."""
    kind = "Cable" if run["system"] in R.ELECTRICAL else ("Hose" if "hose" in run["kind_what"].lower() else "Pipe")
    size = (f"{run['size']:g} mm2" if run["system"] in R.ELECTRICAL and run["cores"] <= 2 and run["size"] is not None and run["kind"] not in ("utp", "sig", "lamp7")
            else f"{run['od']:g} mm outside")
    return dict(
        id=run["id"], iid=run["id"], name=run["feeds"], group=SYSTEM_STYLE[run["system"]][1], system=run["system"],
        material=run["cable"], mass_kg=run["mass_kg"], mass_growth_kg=None, maturity="calculated",
        basis="routed length times the cable's or pipe's mass per metre", source="data/routes.yaml, cad/routes.py",
        drawing=drawing, price_aud=run["aud"], price_basis=f"in {run['priced_in']}" if run.get("priced_in") else None,
        price_note=f"{run['length_m']:.2f} m at AUD {run['aud_m']:.2f}/m with {res['data']['rules']['waste_pct']} % waste", load="tare",
        route=dict(feeds=run["feeds"], ends=f"{_name(res, run['from']['line'])} to {_name(res, run['to']['line'])}",
                   kind=kind, cable=run["cable"], size=size, od_mm=run["od"], length_m=run["length_m"],
                   protection=run.get("protection"), circuit=circuit_of(run, res), fittings=run["fittings"],
                   drop_pct=run.get("vd_pct"), size_why=run.get("size_why")))


def build(res: dict, name: str) -> tuple[Compound, dict]:
    """One viewer model: the ghost, then system > circuit > run."""
    spec = MODELS[name]
    meta, systems = {}, []
    for sys_id in spec["systems"]:
        runs = [r for r in res["runs"] if r["system"] == sys_id]
        if not runs:
            continue
        colour, label = SYSTEM_STYLE[sys_id]
        circuits: dict[str, list] = {}
        for run in runs:
            s = run_solid(run)
            s.label = f"{run['id']} {run['feeds']}".replace("/", "-")
            s.color = rgba(colour, 1.0)
            circuits.setdefault(circuit_of(run, res), []).append(s)
            meta[run["id"]] = meta_of(run, res, spec["drawing"])
        kids = [Compound(label=c.replace("/", "-"), children=v) for c, v in circuits.items()]
        systems.append(Compound(label=label.replace("/", "-"), children=kids))
    if name == "trailer-electrical":
        systems.append(_supports(res))
    systems.append(_frames(res))
    root = Compound(label=name, children=[_ghost(res), *systems])
    return root, meta


def _round(o, nd: int):
    if isinstance(o, float):
        return round(o, nd)
    if isinstance(o, list):
        return [_round(v, nd) for v in o]
    return o


def viewer_json(name: str, root: Compound) -> str:
    """three-cad-viewer JSON at a tessellation coarse enough for 126 tubes (1.5 mm chord, 0.7 rad), with positions to
    0.1 mm and normals to 0.001, which keeps each model under the site's 8 MB per file."""
    from .export import _viewer_js
    js = _viewer_js(name, root, deviation=1.5, angular_tolerance=0.7)
    shapes = json.loads(js[js.index("{"): js.rindex("}") + 1])

    def walk(o, ghost=False):
        ghost = ghost or str(o.get("name", "")).startswith("Ghost")
        for p in o.get("parts") or []:
            walk(p, ghost)
        sh = o.get("shape")
        if isinstance(sh, dict):
            # the ghost's boxes are faces only, so the runs stand out, and the body shell keeps its outline
            if ghost and not str(o.get("name", "")).startswith(SHELL):
                for k in ("edges", "edge_types", "segments_per_edge", "obj_vertices"):
                    if k in sh:
                        sh[k] = []
            for k, nd in (("vertices", 1), ("edges", 1), ("obj_vertices", 1), ("normals", 3)):
                if k in sh:
                    sh[k] = _round(sh[k], nd)
    walk(shapes)
    return json.dumps(shapes, separators=(",", ":"))


# ------------------------------------------------------------------ check rows and the pages' data
def check_rows(res: dict, ev: dict) -> list[dict]:
    """SVC-01 to SVC-13 as check rows (data/routes.yaml `checks`), each with its limit, measured value and governing run."""
    rows = []
    for c in res["data"].get("checks") or []:
        e = ev[c["kind"]]
        row = dict(id=c["id"], title=c["title"], type="services", severity=c["severity"], why=c["why"], source=c.get("source"),
                   ok=e["ok"], problems=e["problems"][:20], sub="")
        if c["kind"] in ("clearance", "kit_clearance"):
            g = e["closest"][0] if e["closest"] else None
            row.update(limit=f"at least {e['limit']:g} mm", measured=e["smallest"], unit="mm",
                       margin=None if e["smallest"] is None else round(e["smallest"] - e["limit"], 1),
                       governing=g and f"{g['run']} to {g['part']}")
        elif c["kind"] == "bends":
            row.update(limit="each bend at or above the run's least bending radius", measured=e["margin"], unit="mm",
                       margin=e["margin"], governing="tightest bend's spare radius")
        elif c["kind"] == "separation":
            row.update(limit=f"at least {e['limit']:g} mm", measured=e["smallest"], unit="mm",
                       margin=None if e["smallest"] is None else round(e["smallest"] - e["limit"], 1), governing=e["governing"])
        elif c["kind"] == "terminal_face":
            row.update(limit=f"at least {e['limit']:g} mm, {', '.join(e['exempt'])} sleeved and exempt", measured=e["smallest"], unit="mm",
                       margin=None if e["smallest"] is None else round(e["smallest"] - e["limit"], 1),
                       governing=e["near"][0]["run"] if e["near"] else None)
        elif c["kind"] == "coverage":
            row.update(limit="every load, outlet, water outlet and fixture has its run, joined up from its source", measured=e["n"] - len(e["problems"]), unit="served",
                       margin=-len(e["problems"]), governing=f"{e['n']} needs")
        elif c["kind"] == "drops":
            fd = "".join(f", the truck's feed {f['line']} {f['limit_pct']:g} % of its own" +
                         (f" and {f.get('floor_of', 'the load')} at least {f['floor_v']:g} V" if f.get("floor_v") is not None else "") for f in e["feeds"])
            row.update(limit=f"DC 2 % at the design current, 230 V 5 %{fd}", measured=round(100 * e["use"], 1), unit="% of the limit",
                       margin=round(100 * (1 - e["use"]), 1), governing=e["governing"])
        elif c["kind"] == "falls":
            row.update(limit=f"at least 1:{1 / res['data']['rules']['fall']:.0f}", measured=e["slope"], unit="fall",
                       margin=None if e["slope"] is None else round(e["slope"] - res["data"]["rules"]["fall"], 4), governing="flattest level leg")
        elif c["kind"] == "glands":
            fits = res["svc"]["fittings"]
            row.update(limit=f"{fits['web_mm']:g} mm between fittings, {fits['spanner_mm']:g} mm round a locknut, none in a keep-clear box",
                       measured=e["margin"], unit="mm spare", margin=e["margin"], governing=e["governing"])
        elif c["kind"] == "ratings":
            row.update(limit="each cable's design current and its device at most its rating where it lies (Ib <= In <= Iz)",
                       measured=e["margin"], unit="A spare", margin=e["margin"], governing=e["governing"])
        elif c["kind"] == "supports":
            row.update(limit=f"each cable's longest unsupported span at most {e['limit']:g} mm", measured=e["longest"], unit="mm",
                       margin=e["margin"], governing=e["governing"])
        elif c["kind"] == "heat":
            hr = res["data"]["rules"]["heat"]
            row.update(limit=f"cables {hr['line_mm']['ELV']:g} mm (ELV) and {hr['line_mm']['ac230']:g} mm (230 V) from {', '.join(hr['lines'])}, the hot surfaces' own distances",
                       measured=e["margin"], unit="mm spare", margin=e["margin"], governing=e["governing"])
        elif c["kind"] == "spacing":
            sp = res["data"]["rules"]["spacing"]
            ac = sorted({v.get("ac230", 0) for v in sp["wet"].values() if v})
            row.update(limit=f"each run's radius plus {sp['gap_mm']:g} mm, a wet line {ac[0]:g} to {ac[-1]:g} mm from 230 V by its kind, lane neighbours may touch",
                       measured=e["margin"], unit="mm spare", margin=e["margin"],
                       governing=f"{e['governing']}, {e['pairs']} pairs measured, {e['overlaps']} overlapping")
        row["detail"] = ". ".join(e["problems"][:3]) if e["problems"] else f"{row.get('governing') or ''}".strip()
        row["status"] = ("PASS" if row["ok"] else "FAIL") if c["severity"] == "fail" else ("MEETS LIMIT" if row["ok"] else "REPORTED")
        rows.append(row)
    return rows


def summary(res: dict, ev: dict) -> dict:
    rows = []
    for r in res["runs"]:
        rows.append(dict(id=r["id"], kind=r["kind"], system=r["system"], system_label=SYSTEM_STYLE[r["system"]][1], group=r["group"],
                         circuit=circuit_of(r, res), feeds=r["feeds"], ends=f"{_name(res, r['from']['line'])} to {_name(res, r['to']['line'])}",
                         cable=r["cable"], size=r["size"], od=r["od"], length_m=r["length_m"], mass_kg=r["mass_kg"], aud=r["aud"],
                         priced_in=r.get("priced_in"), protection=r.get("protection"), vd_pct=r.get("vd_pct"), size_why=r.get("size_why"),
                         fittings=r["fittings"], amps=r.get("amps"), price_basis=r.get("price_basis"), mass_basis=r.get("mass_basis")))
    legend = [dict(system=k, colour=c, label=lab, model=next(m for m, s in MODELS.items() if k in s["systems"]))
              for k, (c, lab) in SYSTEM_STYLE.items()]
    kinds: dict[str, dict] = {}
    for r in res["runs"]:
        k = kinds.setdefault(r["kind"], dict(kind=r["kind"], what=r["kind_what"], length_m=0.0, mass_kg=0.0, aud=0.0, runs=0, fittings=0,
                                             priced_in=r.get("priced_in")))
        k["length_m"] += r["length_m"]
        k["mass_kg"] += r["mass_kg"]
        k["aud"] += r["aud"]
        k["runs"] += 1
        k["fittings"] += r["fittings"]
    priced = []
    for p in res["data"].get("priced") or []:
        got = [kinds[k] for k in p["kinds"] if k in kinds]
        routed = sum(g["fittings"] if p["unit"] == "fittings" else g["length_m"] for g in got)
        priced.append(dict(p, routed=round(routed, 1), larger="routed" if routed > p["quantity"] + 1e-6 else "priced"))
    return dict(runs=rows, totals=R.totals(res), checks=check_rows(res, ev), closest=ev["clearance"]["closest"],
                terminal_face=ev["terminal_face"]["near"][:6], legend=legend, rules=res["data"]["rules"],
                kinds=[dict(v, length_m=round(v["length_m"], 2), mass_kg=round(v["mass_kg"], 2), aud=round(v["aud"], 2)) for v in kinds.values()],
                priced=priced)


def allowance(rep: dict | None, line: str = "BD-11") -> dict | None:
    """A mass line's allowance from the trailer's mass schedule, for the pages' comparison with the routed runs."""
    if not rep:
        return None
    e = next((x for x in rep.get("schedule", []) if x.get("id") == line), None)
    return None if e is None else dict(line=line, item=e.get("item"), mass_kg=e.get("mass_kg"), source=e.get("source"), price_aud=e.get("price_aud"))


def write_outputs(lay, out: Path, lookup=None, site: Path | None = None, rep: dict | None = None) -> dict:
    """Resolve the routes on the solved layout, write both viewer models with their parts files, routes.json, and the
    site's copies (site/public/models, site/src/data/generated). Returns the summary, whose `checks` the trailer's
    report carries. `rep` is the trailer's report, for BD-11's allowance."""
    from .partsmeta import write as write_parts
    res = R.resolve(lay)
    ev = R.evaluate(res)
    data = summary(res, ev)
    data["bd11"] = allowance(rep)
    data["bd11_routed_kg"] = round(data["totals"]["lines"].get("BD-11", {}).get("mass_kg", 0.0), 2)
    out.mkdir(parents=True, exist_ok=True)
    (out / "routes.json").write_text(json.dumps(data, separators=(",", ":"), default=str), encoding="utf-8")
    for name in MODELS:
        root, meta = build(res, name)
        path = out / f"{name}.viewer.json"
        path.write_text(viewer_json(name, root))
        write_parts(path, lambda key, m=meta: m.get(key) or (lookup(key) if lookup else None))
    if site is not None:
        models, gen = site / "public" / "models", site / "src" / "data" / "generated"
        models.mkdir(parents=True, exist_ok=True)
        gen.mkdir(parents=True, exist_ok=True)
        for name in MODELS:
            shutil.copyfile(out / f"{name}.viewer.json", models / f"{name}.json")
            shutil.copyfile(out / f"{name}.parts.json", models / f"{name}.parts.json")
        shutil.copyfile(out / "routes.json", gen / "routes.json")
    return data
