#!/usr/bin/env python3
"""
Generate 1025 Parcours Pages from Excel Case Database
Produces static HTML pages with telemetry instrumentation
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from typing import Optional

# Jinja2 template (simplified version for demo)
PARCOURS_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow, noarchive">
    <title>{{ case_title }} - Parcours Avoulia</title>
    <link rel="stylesheet" href="/assets/parcours.css">
    <script src="/src/appinsights-instrumentation.html" defer></script>
</head>
<body data-case-hash="{{ case_hash }}">
    <div id="app" class="parcours-container">
        <header>
            <h1>{{ case_title }}</h1>
            <p class="subtitle">Parcours de mise en œuvre</p>
        </header>

        <section id="validation" class="etape" data-step-number="1" data-step-name="Étape 1: Validation">
            <details open>
                <summary>Étape 1 – Validation (2 min)</summary>
                <div class="etape-content">
                    <p>{{ validation_questions }}</p>
                    <div class="coche">
                        <input type="checkbox" id="q1" /> <label for="q1">Q1: {{ question_1 }}</label>
                        <input type="checkbox" id="q2" /> <label for="q2">Q2: {{ question_2 }}</label>
                        <input type="checkbox" id="q3" /> <label for="q3">Q3: {{ question_3 }}</label>
                    </div>
                </div>
            </details>
        </section>

        <div class="transition">✓ OK, c'est pour vous. Voici le parcours ({{ duration }})</div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: 17%"></div>
            <span class="progress-text">Étape 1/6</span>
        </div>

        {% for i in range(2, 7) %}
        <section id="etape{{ i }}" class="etape" data-step-number="{{ i }}" data-step-name="Étape {{ i }}">
            <details>
                <summary>Étape {{ i }}</summary>
                <div class="etape-content">
                    <p>{{ steps[i-2] }}</p>
                    <div class="coche">
                        <input type="checkbox" /> <label>Action {{ i }}</label>
                    </div>
                </div>
            </details>
        </section>
        {% endfor %}

        <section class="quickwin-accordion">
            <details>
                <summary>💡 Quick Win (Optionnel)</summary>
                <div class="accordion-content">
                    <p>{{ quickwin }}</p>
                    <button data-copie class="btn-copy">Copier le prompt</button>
                </div>
            </details>
        </section>

        <footer>
            <p>Page générée: {{ generated_at }}</p>
            <p>Source: {{ source_ref }}</p>
        </footer>
    </div>

    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .parcours-container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        .etape {{ border: 1px solid #ddd; margin: 1rem 0; border-radius: 4px; }}
        .etape summary {{ padding: 1rem; cursor: pointer; background: #f5f5f5; }}
        .etape-content {{ padding: 1rem; }}
        .coche {{ margin-top: 1rem; }}
        .coche input {{ margin-right: 0.5rem; }}
        .transition {{ text-align: center; margin: 2rem 0; font-weight: bold; color: #1976d2; }}
        .progress-bar {{ width: 100%; height: 8px; background: #ddd; border-radius: 4px; margin: 1rem 0; }}
        .progress-fill {{ height: 100%; background: #4caf50; border-radius: 4px; }}
        .progress-text {{ display: block; text-align: center; margin-top: 0.5rem; font-size: 0.9rem; color: #666; }}
        .quickwin-accordion summary {{ background: #fff3cd; padding: 1rem; cursor: pointer; }}
        .btn-copy {{ padding: 0.5rem 1rem; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .btn-copy:hover {{ background: #1565c0; }}
        footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #999; font-size: 0.85rem; }}
    </style>
</body>
</html>
'''


def generate_case_hash(case_id: str, salt: Optional[str] = None) -> str:
    """Generate URL-safe hash from case ID."""
    if salt is None:
        salt = os.getenv('AVOULIA_SALT', 'dev-salt-12345')
    data = f"{case_id}|{salt}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()[:16]


def load_sample_cases(count: int = 1025) -> list[dict]:
    """
    Load sample cases from Excel (mock data for now).
    In production, this would load from the actual Excel file.
    """
    cases = []
    for i in range(1, count + 1):
        case_id = f"UC-{i:04d}"
        cases.append({
            'case_id': case_id,
            'title': f"Cas d'usage {i}: Implémentation IA pour PME",
            'description': f"Parcours complet pour la mise en œuvre du cas {case_id}",
            'questions': [
                f"Est-ce applicable à votre contexte?",
                f"Avez-vous les prérequis?",
                f"Êtes-vous prêt à commencer?",
            ],
            'steps': [
                f"Étape 2 pour {case_id}: Préparation",
                f"Étape 3 pour {case_id}: Mise en place",
                f"Étape 4 pour {case_id}: Formation",
                f"Étape 5 pour {case_id}: Déploiement",
                f"Étape 6 pour {case_id}: Suivi",
            ],
            'quickwin': f"Prompt rapide pour tester: 'Comment implémenter {case_id}?'",
            'duration': '~2.5h',
        })
    return cases


def generate_pages(output_dir: str = 'generated_pages', count: int = 1025):
    """
    Generate all parcours pages.
    
    Args:
        output_dir: Directory to save generated pages
        count: Number of cases to generate (default 1025)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Loading {count} cases...")
    cases = load_sample_cases(count)
    
    salt = os.getenv('AVOULIA_SALT', 'dev-salt-12345')
    pages_generated = 0
    
    print(f"📝 Generating pages...")
    for case in cases:
        case_hash = generate_case_hash(case['case_id'], salt)
        
        # Simple template substitution (replace Jinja2 with basic string replacements for demo)
        page_html = PARCOURS_PAGE_TEMPLATE
        page_html = page_html.replace('{{ case_title }}', case['title'])
        page_html = page_html.replace('{{ case_hash }}', case_hash)
        page_html = page_html.replace('{{ validation_questions }}', case['questions'][0])
        page_html = page_html.replace('{{ question_1 }}', case['questions'][0])
        page_html = page_html.replace('{{ question_2 }}', case['questions'][1])
        page_html = page_html.replace('{{ question_3 }}', case['questions'][2])
        page_html = page_html.replace('{{ duration }}', case['duration'])
        page_html = page_html.replace('{{ steps[0] }}', case['steps'][0])
        page_html = page_html.replace('{{ steps[1] }}', case['steps'][1])
        page_html = page_html.replace('{{ steps[2] }}', case['steps'][2])
        page_html = page_html.replace('{{ steps[3] }}', case['steps'][3])
        page_html = page_html.replace('{{ steps[4] }}', case['steps'][4])
        page_html = page_html.replace('{{ quickwin }}', case['quickwin'])
        page_html = page_html.replace('{{ generated_at }}', 'now')
        page_html = page_html.replace('{{ source_ref }}', case['case_id'])
        
        # Save page
        page_file = output_path / f"{case_hash}.html"
        page_file.write_text(page_html, encoding='utf-8')
        
        pages_generated += 1
        if pages_generated % 100 == 0:
            print(f"  ✓ Generated {pages_generated}/{count}")
    
    print(f"\n✅ Generated {pages_generated} pages in {output_path}")
    print(f"📊 Sample page: {output_path / generate_case_hash('UC-0001', salt)}.html")
    return pages_generated


if __name__ == '__main__':
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1025
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'generated_pages'
    
    print(f"🚀 Avoulia Parcours Page Generator")
    print(f"📊 Target: {count} pages")
    print(f"📁 Output: {output_dir}\n")
    
    generated = generate_pages(output_dir, count)
    print(f"\n✨ Done!")
