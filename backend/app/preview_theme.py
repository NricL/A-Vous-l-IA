"""Local-only presentation adapter; the shared parcours template is untouched."""

THEME_SCRIPT = """
(() => {
  const param = new URLSearchParams(window.location.search).get("scoutTheme");
  const theme =
    param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);
})();
"""

THEME_CSS = """
:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}
"""

PARCOURS_CSS = """
* { box-sizing:border-box; }
body { margin:0; font:16px/1.6 "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
  background:var(--cp-bg); color:var(--cp-text); }
.page { max-width:800px; margin:auto; padding:32px 24px 64px; }
.preview-banner { padding:16px 24px; background:var(--cp-accent-soft); border-bottom:1px solid var(--cp-border);
  color:var(--cp-text); overflow-wrap:anywhere; }
.preview-banner p { margin:4px 0; }
h1 { font-size:clamp(26px,5vw,38px); line-height:1.2; }
h2 { font-size:21px; }
a { color:var(--cp-link); }
.eyebrow { text-transform:uppercase; color:var(--cp-accent); font-size:12px; letter-spacing:.1em; font-weight:700; }
.resume,.note,footer,.duree,#prog-label { color:var(--cp-text-muted); }
.carte,.contexte { padding:16px; margin:20px 0; background:var(--cp-surface); border:1px solid var(--cp-border); border-radius:16px; }
.puces { display:flex; flex-wrap:wrap; gap:8px; }
.puce { background:var(--cp-surface); border:1px solid var(--cp-border); padding:4px 12px; border-radius:.625rem; font-size:13px; }
.puce.sensible { border-color:var(--cp-warning); }
.tester-rapidement,button { display:inline-block; color:var(--cp-accent-fg); background:var(--cp-accent);
  border:0; padding:10px 16px; border-radius:.625rem; font:inherit; cursor:pointer; text-decoration:none; }
.tester-rapidement { margin-top:20px; }
.tester-rapidement:hover,button:hover { background:var(--cp-accent-hover); }
:focus-visible { outline:3px solid var(--cp-accent); outline-offset:4px; }
.progression { position:sticky; top:0; z-index:5; background:var(--cp-bg); padding:12px 0; margin:24px 0; }
.progression .texte { display:flex; justify-content:space-between; gap:12px; font-size:13px; }
.barre { height:6px; background:var(--cp-border); border-radius:.625rem; overflow:hidden; }
.barre>div { height:100%; width:0%; background:var(--cp-accent); }
.parcours { margin-top:24px; }
.etape { position:relative; padding-left:52px; margin-bottom:16px; }
.marqueur { position:absolute; left:0; top:8px; width:36px; height:36px; display:grid; place-items:center;
  border:1px solid var(--cp-border); border-radius:.625rem; background:var(--cp-surface); font-weight:700; }
.faite .marqueur { background:var(--cp-accent); color:var(--cp-accent-fg); }
details { background:var(--cp-surface); border:1px solid var(--cp-border); border-radius:16px; overflow:hidden; }
summary { padding:16px; cursor:pointer; display:flex; gap:12px; align-items:baseline; }
summary .titre { flex:1; font-weight:700; font-size:18px; min-width:0; }
summary .duree,.chevron { font-size:12px; }
summary .chevron { color:var(--cp-text-muted); }
.contenu,.contenu-qw { padding:0 16px 16px; border-top:1px solid var(--cp-border); }
.source { white-space:pre-wrap; overflow-wrap:anywhere; }
.resume,.coche label,summary .titre { overflow-wrap:anywhere; }
.reflexion { padding-left:20px; }
.choix { border:0; padding:0; }
.choix label,.preparation label,.contexte label { display:block; margin:8px 0; }
.contexte label,.choix legend { font-weight:700; }
.coche,.valider { display:flex; gap:12px; align-items:baseline; padding:12px 0; border-bottom:1px solid var(--cp-border); }
.coche small { display:block; color:var(--cp-text-muted); }
input { accent-color:var(--cp-accent); }
select,textarea { width:100%; font:inherit; padding:12px; color:var(--cp-text); background:var(--cp-surface);
  border:1px solid var(--cp-border-strong); border-radius:.625rem; }
textarea { resize:vertical; }
.critere { border-left:3px solid var(--cp-accent); padding:12px; background:var(--cp-surface-soft); margin-top:16px; }
.ticket { margin:16px 0; background:var(--cp-surface-soft); color:var(--cp-text); border:1px solid var(--cp-border); border-radius:.625rem; overflow:hidden; }
.ticket .bandeau { padding:12px; display:flex; justify-content:space-between; gap:12px; align-items:center; border-bottom:1px solid var(--cp-border); font-weight:700; }
.ticket pre { font:13px/1.6 Consolas, "Courier New", Courier, monospace; padding:16px; white-space:pre-wrap; overflow-wrap:anywhere; }
.aide-element { margin:12px 0; }
.quickwin-accordion { margin-top:24px; }
#prompt-demarrage { scroll-margin-top:100px; }
footer { margin-top:40px; padding-top:16px; border-top:1px solid var(--cp-border); font-size:13px; }
@media(max-width:480px) { .page { padding:24px 12px; } .etape { padding-left:40px; } .marqueur { width:30px; height:30px; }
  summary { flex-wrap:wrap; padding:12px; gap:8px; } summary .titre { flex-basis:100%; } .ticket .bandeau { flex-wrap:wrap; } }
@media(prefers-reduced-motion:reduce) { * { scroll-behavior:auto; transition:none; } }
"""
