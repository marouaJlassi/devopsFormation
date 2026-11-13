import base64, html, json, os, shutil, urllib.request
from datetime import datetime, timezone
from pathlib import Path

E = html.escape
OUT = Path("pipeline-report")
OUT.mkdir(exist_ok=True)
K = {"crit": 0, "high": 0}

STAGES = [
    ("Maven Build", "🔨", "Compile et package le projet."),
    ("Tests Unitaires + Coverage", "🧪", "Tests unitaires et couverture JaCoCo."),
    ("Trivy FS Scan", "🛡️", "Vulnérabilités dans le code et les dépendances."),
    ("Deploy to Nexus", "📦", "Publie l'artefact Maven sur Nexus."),
    ("SonarQube Analysis", "🔍", "Bugs, vulnérabilités et code smells."),
    ("Docker Build", "🐳", "Construit l'image Docker."),
    ("Trivy Image Scan", "🛡️", "Vulnérabilités dans l'image Docker."),
    ("Docker Push", "🚀", "Publie l'image sur Docker Hub."),
    ("Docker Compose", "🧩", "Lance les conteneurs."),
    ("Deploy to Kubernetes", "☸️", "Déploie sur Minikube."),
    ("Monitoring with Grafana Prometheus", "📈", "Prometheus, Grafana et cAdvisor."),
]

ST = {
    "SUCCESS": ("Réussi", "ok"), "FAILED": ("Échoué", "ko"),
    "UNSTABLE": ("Instable", "warn"), "ABORTED": ("Annulé", "warn"),
    "NOT_EXECUTED": ("Non exécuté", "mute"), "IN_PROGRESS": ("En cours", "info"),
}

def get_stages():
    build_url = os.getenv("BUILD_URL", "").rstrip("/")
    user, token = os.getenv("JENKINS_USER"), os.getenv("JENKINS_TOKEN")
    if not (build_url and user and token):
        print("Variables Jenkins manquantes")
        return {}
    auth = base64.b64encode(f"{user}:{token}".encode()).decode()
    req = urllib.request.Request(build_url + "/wfapi/describe",
                                 headers={"Authorization": f"Basic {auth}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return {s["name"]: s for s in json.load(r).get("stages", [])}
    except Exception as exc:
        print("API Jenkins indisponible:", exc)
        return {}

def dur(ms):
    m, s = divmod(int((ms or 0) / 1000), 60)
    return f"{m} min {s:02d} s" if m else f"{s} s"

NA = "<p class='muted'>Rapport introuvable.</p>"

def trivy(path):
    def run():
        p = Path(path)
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return NA
        shutil.copy2(p, OUT / p.name)
        vulns = [v for r in (d.get("Results") or []) for v in (r.get("Vulnerabilities") or [])]
        crit = sum(1 for v in vulns if v.get("Severity") == "CRITICAL")
        high = sum(1 for v in vulns if v.get("Severity") == "HIGH")
        K["crit"] += crit
        K["high"] += high
        vulns.sort(key=lambda v: (v.get("Severity") != "CRITICAL", v.get("PkgName", "")))
        out = (f"<p><b class='ko-t'>{crit}</b> critiques — <b class='warn-t'>{high}</b> élevées</p>")
        if vulns:
            rows = "".join(
                f"<tr><td>{E(v.get('Severity',''))}</td><td>{E(v.get('VulnerabilityID',''))}</td>"
                f"<td>{E(v.get('PkgName',''))}</td><td>{E(v.get('InstalledVersion',''))}</td>"
                f"<td>{E(v.get('FixedVersion') or '—')}</td></tr>" for v in vulns[:40])
            out += ("<div class='scroll'><table><thead><tr><th>Sévérité</th><th>CVE</th><th>Paquet</th>"
                    f"<th>Installée</th><th>Corrigée</th></tr></thead><tbody>{rows}</tbody></table></div>")
        else:
            out += "<p class='good'>✔ Aucune vulnérabilité.</p>"
        return out + f"<p><a class='btn' href='{E(p.name)}'>Télécharger le JSON</a></p>"
    return run

def sonar():
    return ("<p><a class='btn' target='_blank' "
            "href='http://127.0.0.1:9000/dashboard?id=devopsbackend'>Ouvrir SonarQube</a></p>")

def jacoco():
    base = os.getenv("BUILD_URL", "#")
    return f"<p><a class='btn' target='_blank' href='{E(base)}JaCoCo_Coverage/'>Ouvrir JaCoCo</a></p>"

DET = {
    "Trivy FS Scan": trivy("trivy-report.json"),
    "Trivy Image Scan": trivy("trivy-image-report.json"),
    "SonarQube Analysis": sonar,
    "Tests Unitaires + Coverage": jacoco,
}

CSS = """
:root{--bg:#f4f6fb;--card:#fff;--text:#1d2433;--muted:#6b7488;--line:#e4e8f0;--ok:#16a34a;--ko:#dc2626;--warn:#d97706;--info:#2563eb;--mute:#8b94a7;--accent:#4f46e5}
@media(prefers-color-scheme:dark){:root{--bg:#0f1420;--card:#171e2e;--text:#e6e9f2;--muted:#9aa3b8;--line:#263049}}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.55}
.wrap{max-width:1050px;margin:0 auto;padding:28px 18px 60px}
header{background:linear-gradient(135deg,#4f46e5,#0ea5e9);color:#fff;border-radius:18px;padding:28px 30px;margin-bottom:22px}
header h1{margin:0 0 6px}.meta{display:flex;flex-wrap:wrap;gap:10px 22px;margin-top:14px;font-size:.88rem}
.global{display:inline-block;margin-top:14px;padding:6px 14px;border-radius:999px;background:rgba(255,255,255,.2);font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.kpi b{display:block;font-size:1.8rem}.kpi span{color:var(--muted);font-size:.85rem}
.kpi.ok b{color:var(--ok)}.kpi.ko b{color:var(--ko)}.kpi.warn b{color:var(--warn)}
.stage{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--mute);border-radius:16px;padding:18px 22px;margin-bottom:14px}
.stage.ok{border-left-color:var(--ok)}.stage.ko{border-left-color:var(--ko)}.stage.warn{border-left-color:var(--warn)}.stage.info{border-left-color:var(--info)}
.head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.head h2{margin:0;font-size:1.1rem}
.badge{padding:4px 12px;border-radius:999px;font-size:.8rem;font-weight:700;color:#fff;background:var(--mute)}
.badge.ok{background:var(--ok)}.badge.ko{background:var(--ko)}.badge.warn{background:var(--warn)}.badge.info{background:var(--info)}
.desc,.muted{color:var(--muted)}.facts{font-size:.85rem;color:var(--muted);margin-bottom:8px}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;font-size:.85rem}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--line)}th{background:var(--bg);color:var(--muted)}
.btn{display:inline-block;padding:7px 14px;border-radius:9px;background:var(--accent);color:#fff;text-decoration:none;font-size:.85rem;font-weight:600}
.good{color:var(--ok);font-weight:600}.ko-t{color:var(--ko)}.warn-t{color:var(--warn)}
footer{text-align:center;color:var(--muted);font-size:.8rem;margin-top:30px}
"""

jobs = get_stages()
total = {"ok": 0, "ko": 0, "other": 0}
sections = ""
for name, icon, desc in STAGES:
    job = jobs.get(name)
    label, cls = ST.get(job.get("status"), ("Inconnu", "mute")) if job else ("Non trouvé", "mute")
    total[cls if cls in ("ok", "ko") else "other"] += 1
    facts = f"Stage : <code>{E(name)}</code>"
    if job:
        facts += f" — Durée : {dur(job.get('durationMillis'))}"
    try:
        details = DET.get(name, lambda: "")()
    except Exception as exc:
        details = f"<p class='muted'>Erreur : {E(str(exc))}</p>"
    sections += (f"<section class='stage {cls}'><div class='head'><h2>{icon} {E(name)}</h2>"
                 f"<span class='badge {cls}'>{label}</span></div><p class='desc'>{E(desc)}</p>"
                 f"<div class='facts'>{facts}</div>{details}</section>")

if total["ko"]:
    verdict = f"⚠️ {total['ko']} stage(s) en échec"
elif total["ok"] == len(STAGES):
    verdict = "✅ Tous les stages sont réussis"
else:
    verdict = "ℹ️ Certains stages sont ignorés ou introuvables"

now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
env = os.getenv
page = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rapport Jenkins — {E(env('JOB_NAME',''))}</title><style>{CSS}</style></head>
<body><div class="wrap"><header><h1>Rapport du pipeline Jenkins</h1>
<p>{E(env('JOB_NAME',''))} — qualité, sécurité et déploiements</p>
<div class="meta"><span>🔖 Commit : <b>{E(env('GIT_SHORT',''))}</b></span>
<span>🔗 <a style="color:#fff" href="{E(env('BUILD_URL','#'))}">Build #{E(env('BUILD_NUMBER',''))}</a></span>
<span>🕒 {now}</span></div><div class="global">{E(verdict)}</div></header>
<div class="cards">
<div class="kpi ok"><b>{total['ok']}</b><span>Stages réussis</span></div>
<div class="kpi ko"><b>{total['ko']}</b><span>Stages échoués</span></div>
<div class="kpi warn"><b>{total['other']}</b><span>Autres</span></div>
<div class="kpi ko"><b>{K['crit']}</b><span>Vulnérabilités critiques</span></div>
<div class="kpi warn"><b>{K['high']}</b><span>Vulnérabilités élevées</span></div>
</div>{sections}<footer>Généré par Jenkins — {now}</footer></div></body></html>"""

(OUT / "index.html").write_text(page, encoding="utf-8")
print("Rapport généré : pipeline-report/index.html")