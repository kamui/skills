#!/usr/bin/env python3
"""Exercise working-tree snapshots through the review_context.py CLI.

Usage: python3 scripts/test_review_context.py
Inputs: disposable local repositories, with no network access.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('review_context.py').resolve()


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.write('tracked', 'base\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'Initial')
        self.head = self.git('rev-parse', 'HEAD').strip()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, capture_output=True,
                                text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def write(self, path, text):
        (self.root / path).write_text(text, encoding='utf-8')

    def snapshot(self, *args, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), '--worktree', '--json', *args],
                                cwd=self.root, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        if code:
            self.assertIn('snapshot-failed', result.stderr)
            return result
        return json.loads(result.stdout)

    def test_files_and_index_are_preserved(self):
        self.write('tracked', 'staged\n')
        self.git('add', 'tracked')
        self.write('tracked', 'working\n')
        self.write('untracked', 'include me\n')
        self.write('.gitignore', 'ignored\n')
        self.write('ignored', 'exclude me\n')
        before = (self.root / '.git/index').read_bytes()
        refs = self.git('show-ref')
        context = self.snapshot()
        snap = context['snapshot']
        self.assertEqual(snap['source_head'], self.head)
        self.assertEqual(snap['parent'], self.head)
        self.assertEqual(snap['chain'], 'first')
        self.assertEqual(self.git('rev-parse', snap['head'] + '^').strip(), self.head)
        self.assertEqual(self.git('show', snap['head'] + ':tracked'), 'working\n')
        self.assertEqual(self.git('show', snap['head'] + ':untracked'), 'include me\n')
        self.assertNotIn('ignored', self.git('ls-tree', '--name-only', snap['head']).splitlines())
        self.assertEqual(before, (self.root / '.git/index').read_bytes())
        self.assertEqual(refs, self.git('show-ref'))
        self.assertEqual((self.root / 'tracked').read_text(encoding='utf-8'), 'working\n')
        self.assertEqual(self.git('show', '-s', '--format=%B', snap['head']).strip(),
                         f'review-code snapshot source={self.head}')
        # Staged deletion with the working file retained must restore that file.
        self.git('rm', '--cached', '-f', 'tracked')
        next_snap = self.snapshot()['snapshot']
        self.assertEqual(self.git('show', next_snap['head'] + ':tracked'), 'working\n')
        self.assertEqual(next_snap['tree'], snap['tree'])

    def test_chaining_delta_stability_and_reset(self):
        self.write('tracked', 'first\n')
        first = self.snapshot()['snapshot']
        same = self.snapshot('--parent', first['head'])['snapshot']
        self.assertEqual(same['tree'], first['tree'])
        self.write('tracked', 'second\n')
        second = self.snapshot('--parent', first['head'])['snapshot']
        self.assertEqual(second['chain'], 'chained')
        self.git('merge-base', '--is-ancestor', first['head'], second['head'])
        self.assertEqual(self.git('diff', first['head'] + '...' + second['head']),
                         self.git('diff', first['head'], second['head']))
        self.assertIn('+second', self.git('diff', first['head'] + '...' + second['head']))
        self.git('add', '.')
        self.git('commit', '-qm', 'User commit')
        moved = self.git('rev-parse', 'HEAD').strip()
        reset = self.snapshot('--parent', second['head'])['snapshot']
        self.assertEqual(reset['chain'], 'reset')
        self.assertEqual(reset['parent'], moved)
        self.assertEqual(reset['source_head'], moved)
        self.assertEqual(self.git('rev-parse', reset['head'] + '^').strip(), moved)

    def test_store_and_unborn_head(self):
        self.write('tracked', 'dirty\n')
        store = Path(self.temp.name) / 'context.json'
        output = self.snapshot('--store', str(store))
        saved = json.loads(store.read_text(encoding='utf-8'))['context']
        self.assertEqual(output['snapshot'], saved['snapshot'])
        self.assertEqual(saved['head'], saved['snapshot']['head'])
        self.assertEqual(saved['manifest'][0]['path'], 'tracked')
        self.git('checkout', '--orphan', 'unborn')
        self.snapshot(code=2)

    def test_submodule_gitlink_and_dirty_content(self):
        child = Path(self.temp.name) / 'child'
        child.mkdir()
        parent = self.root
        self.root = child
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.write('file', 'one\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'Child')
        child_head = self.git('rev-parse', 'HEAD').strip()
        self.root = parent
        self.git('-c', 'protocol.file.allow=always', 'submodule', 'add', '-q', str(child), 'module')
        self.write('module/file', 'dirty\n')
        snap = self.snapshot()['snapshot']
        self.assertEqual(self.git('ls-tree', snap['head'], 'module').split('\t')[0],
                         f'160000 commit {child_head}')
        self.assertEqual(snap['dirty_submodules'], ['module'])

    def test_untracked_clean_filter(self):
        self.git('config', 'filter.upper.clean', "tr 'a-z' 'A-Z'")
        self.write('.gitattributes', 'new filter=upper\n')
        self.write('new', 'lowercase\n')
        snap = self.snapshot()['snapshot']
        self.assertEqual(self.git('show', snap['head'] + ':new'), 'LOWERCASE\n')
        self.assertEqual((self.root / 'new').read_text(encoding='utf-8'), 'lowercase\n')


if __name__ == '__main__':
    unittest.main()
