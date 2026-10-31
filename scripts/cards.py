"""Genera stats.svg y langs.svg para el README con la API de GitHub (corre en el workflow)."""
import json, os, urllib.request
from collections import Counter

USER = "Alexp9103"
Q = """query($u:String!){user(login:$u){
  contributionsCollection{totalCommitContributions totalPullRequestContributions totalIssueContributions contributionCalendar{totalContributions}}
  repositories(first:100,ownerAffiliations:OWNER,isFork:false){totalCount nodes{stargazerCount languages(first:10){edges{size node{name color}}}}}}}"""

req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
                             {"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"})
u = json.load(urllib.request.urlopen(req))["data"]["user"]
c, repos = u["contributionsCollection"], u["repositories"]

BG, FG, AC, MUTED = "#0a1220", "#c9d1d9", "#ff7a1a", "#8b949e"
filas = [("Contribuciones (año)", c["contributionCalendar"]["totalContributions"]), ("Commits", c["totalCommitContributions"]),
         ("Pull requests", c["totalPullRequestContributions"]), ("Repos", repos["totalCount"]),
         ("Estrellas", sum(r["stargazerCount"] for r in repos["nodes"]))]
txt = "".join(f'<text x="25" y="{70 + i*24}" fill="{FG}">{k}</text><text x="300" y="{70 + i*24}" fill="#fff" text-anchor="end" font-weight="700">{v}</text>' for i, (k, v) in enumerate(filas))
open("stats.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="330" height="195" font-family="Segoe UI,Ubuntu,sans-serif" font-size="14"><rect width="330" height="195" rx="8" fill="{BG}"/><text x="25" y="35" fill="{AC}" font-size="17" font-weight="700">Estadísticas de GitHub</text>{txt}</svg>')

size, color = Counter(), {}
for r in repos["nodes"]:
    for e in r["languages"]["edges"]:
        size[e["node"]["name"]] += e["size"]; color[e["node"]["name"]] = e["node"]["color"] or MUTED
top = size.most_common(8); total = sum(v for _, v in top) or 1
x, barra, ley = 25, "", ""
for i, (n, v) in enumerate(top):
    w = 280 * v / total
    barra += f'<rect x="{x:.1f}" y="50" width="{w:.1f}" height="8" fill="{color[n]}"/>'; x += w
    ley += f'<circle cx="{30 + (i % 2)*150}" cy="{80 + (i//2)*22}" r="5" fill="{color[n]}"/><text x="{42 + (i % 2)*150}" y="{85 + (i//2)*22}" fill="{FG}">{n} {100*v/total:.1f}%</text>'
open("langs.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="330" height="195" font-family="Segoe UI,Ubuntu,sans-serif" font-size="13"><rect width="330" height="195" rx="8" fill="{BG}"/><text x="25" y="35" fill="{AC}" font-size="17" font-weight="700">Lenguajes más usados</text><clipPath id="r"><rect x="25" y="50" width="280" height="8" rx="4"/></clipPath><g clip-path="url(#r)">{barra}</g>{ley}</svg>')
