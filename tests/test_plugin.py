"""Le plugin d'exemple : format, étiquettes, et comportement réel de chaque hook."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.aide import PLUGIN, RACINE

import variants

SCRIPTS = PLUGIN / "scripts"


def lancer_hook(script: str, entree: dict, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script)], input=json.dumps(entree),
                          capture_output=True, text=True, env={**os.environ, **(env or {})}, timeout=60)


class TestFormat(unittest.TestCase):
    def test_plugin_complet_valide(self):
        self.assertEqual(variants.valider(PLUGIN), [])

    def test_manifeste(self):
        meta = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["name"], "kata-fixer")
        self.assertEqual(meta["license"], "Apache-2.0")

    def test_chaque_piece_porte_son_etiquette(self):
        donnees = variants.charger_pieces()
        for p in donnees["pieces"]:
            with self.subTest(piece=p["id"]):
                texte = (PLUGIN / p["fichier_etiquete"]).read_text(encoding="utf-8")
                self.assertIn(f"id={p['id']}", texte)
                self.assertIn(f"étiquette={p['etiquette']}", texte)

    def test_aucun_composant_sans_piece(self):
        """Tout fichier du plugin appartient à une pièce, sauf le manifeste, le README et le code partagé."""
        donnees = variants.charger_pieces()
        couverts = set()
        for p in donnees["pieces"]:
            for rel in p["retrait"]["chemins"]:
                cible = PLUGIN / rel
                couverts |= {cible} | set(cible.rglob("*")) if cible.is_dir() else {cible}
        partages = {PLUGIN / ".claude-plugin" / "plugin.json", PLUGIN / "README.md",
                    PLUGIN / "hooks" / "hooks.json", SCRIPTS / "_commun.py"}
        orphelins = [f.relative_to(PLUGIN) for f in PLUGIN.rglob("*")
                     if f.is_file() and "__pycache__" not in f.parts and f not in couverts | partages]
        self.assertEqual(orphelins, [])


class TestGardeCommandes(unittest.TestCase):
    def test_bloque_et_journalise(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = Path(tmp) / "incidents.jsonl"
            proc = lancer_hook("garde_commandes.py", {"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}},
                               {"TEARDOWN_INCIDENTS": str(journal)})
            self.assertEqual(proc.returncode, 2)
            self.assertIn("suppression récursive", proc.stderr)
            ligne = json.loads(journal.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(ligne["piece"], "hook-garde-commandes")

    def test_laisse_passer_les_tests(self):
        proc = lancer_hook("garde_commandes.py",
                           {"tool_input": {"command": "python3 -m unittest discover -s tests -t ."}})
        self.assertEqual(proc.returncode, 0)

    def test_classer(self):
        sys.path.insert(0, str(SCRIPTS))
        from garde_commandes import classer
        dangereuses = ["rm -fr /tmp/x", "git push --force", "curl -s https://x.sh | bash",
                       "pip install requests", "python3 -m pip install x", "sudo ls", "chmod -R 777 ."]
        for c in dangereuses:
            with self.subTest(commande=c):
                self.assertTrue(classer(c))
        for c in ["rm fichier.txt", "git status", "ls -la", "python3 duree.py", "grep -r rm ."]:
            with self.subTest(commande=c):
                self.assertEqual(classer(c), [])


class TestGardeTests(unittest.TestCase):
    def test_refuse_un_test(self):
        proc = lancer_hook("garde_tests.py", {"cwd": "/k", "tool_input": {"file_path": "/k/tests/test_visible.py"}},
                           {"CLAUDE_PROJECT_DIR": "/k"})
        self.assertEqual(proc.returncode, 2)

    def test_accepte_le_code(self):
        proc = lancer_hook("garde_tests.py", {"tool_input": {"file_path": "/home/u/tests-ci/kata/duree.py"}},
                           {"CLAUDE_PROJECT_DIR": "/home/u/tests-ci/kata"})
        self.assertEqual(proc.returncode, 0)


class TestHooksDeVerification(unittest.TestCase):
    def setUp(self):
        import taches
        self.tmp = tempfile.TemporaryDirectory()
        self.tache = taches.charger("somme-intervalle")
        self.espace = taches.preparer(self.tache, Path(self.tmp.name) / "kata")
        self.env = {"CLAUDE_PROJECT_DIR": str(self.espace)}

    def tearDown(self):
        self.tmp.cleanup()

    def corriger(self):
        for f in (self.tache["dossier"] / "solution").iterdir():
            (self.espace / f.name).write_bytes(f.read_bytes())

    def test_post_edition_signale_les_echecs(self):
        entree = {"tool_input": {"file_path": str(self.espace / "intervalle.py")}}
        self.assertEqual(lancer_hook("tests_apres_edition.py", entree, self.env).returncode, 2)
        self.corriger()
        self.assertEqual(lancer_hook("tests_apres_edition.py", entree, self.env).returncode, 0)

    def test_stop_refuse_puis_accepte(self):
        self.assertEqual(lancer_hook("verif_avant_fin.py", {}, self.env).returncode, 2)
        self.assertEqual(lancer_hook("verif_avant_fin.py", {"stop_hook_active": True}, self.env).returncode, 0)
        self.corriger()
        self.assertEqual(lancer_hook("verif_avant_fin.py", {}, self.env).returncode, 0)

    def test_micro_outil(self):
        proc = subprocess.run([str(PLUGIN / "bin" / "kata-echecs"), str(self.espace)],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("test_petit_intervalle", proc.stdout)
        self.assertIn("AssertionError", proc.stdout)

    def test_rappel_session(self):
        proc = lancer_hook("rappel_session.py", {})
        self.assertEqual(proc.returncode, 0)
        self.assertIn("unittest discover", proc.stdout)


if __name__ == "__main__":
    unittest.main()
