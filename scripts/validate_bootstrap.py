#!/usr/bin/env python3
"""Validate the documentation bootstrap; performs no network or remote writes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys


def main() -> int:
    root=Path(__file__).resolve().parents[1]
    try:
        data=json.loads((root/'docs/backlog.json').read_text(encoding='utf-8'))
        phases=data['phases']
        assert [p['phase'] for p in phases]==[f'{n:02}' for n in range(7)], 'Phase sequence differs'
        assert all(len(p['tasks'])==6 for p in phases), 'Expected 6 tasks per phase'
        ids=[t['id'] for p in phases for t in p['tasks']]
        assert len(ids)==len(set(ids))==42, 'Expected 42 unique tasks'
        md=(root/'AionCrafter_Project_Prompt.md').read_text(encoding='utf-8')
        section=md.split('## 13. Complete implementation backlog')[1].split('## 14.')[0]
        md_ids=re.findall(r'- \[[ x]\] \*\*`([^`]+)`',section)
        assert ids==md_ids, 'Backlog differs from master brief'
        html=(root/'AionCrafter_Roadmap.html').read_text(encoding='utf-8')
        assert all(tid in html for tid in ids), 'HTML is missing task IDs'
        assert 'aioncrafter-roadmap-v1' in html, 'Storage key changed'
        assert '## 21. Architectural control' in md, 'Missing architecture protocol'
        completed=[t['id'] for p in phases for t in p['tasks'] if t['status']=='COMPLETE']
        assert all(t.get('evidence') for p in phases for t in p['tasks'] if t['status']=='COMPLETE'), 'Completion lacks evidence'
        assert all(t['status'] in {'NOT_STARTED','IN_PROGRESS','BLOCKED','COMPLETE','DEFERRED'} for p in phases for t in p['tasks']), 'Invalid status'
        progress=json.loads((root/'docs/roadmap-progress.json').read_text(encoding='utf-8'))
        assert progress['completed']==completed, 'Roadmap progress differs from backlog'
        assert data['gates']=={'A':'UNVERIFIED','B':'UNVERIFIED'}, 'Gate changes need separate evidence review'
        for rel in ('AGENTS.md','README.md','docs/PROJECT_STATE.md','docs/NEXT_CHAT_PROMPT.md',
                    'docs/GITHUB_DELIVERY.md','docs/handoffs/architecture-control-2026-10-04.md'):
            assert (root/rel).is_file(), f'Missing {rel}'
        manifest=json.loads((root/'docs/ARTIFACT_MANIFEST.json').read_text(encoding='utf-8'))
        for item in manifest['files']:
            path=root/item['path']
            assert path.is_file(), f'Missing {item["path"]}'
            assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'], f'Checksum mismatch: {path}'
        print(f'PASS: 7 phases, 42 stable task IDs, 6 tasks per phase.')
        print(f'PASS: {len(completed)} tasks carry completion evidence; both external gates remain UNVERIFIED.')
        print(f'PASS: {len(manifest["files"])} artifact checksums and required handoff files.')
        print('PASS: brief/backlog/roadmap task IDs agree; original HTML storage key retained.')
        print('Scope: documentation/package checks only. No app or remote integration tests.')
        return 0
    except (AssertionError, KeyError, ValueError, OSError, IndexError) as exc:
        print(f'FAIL: {exc}',file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
