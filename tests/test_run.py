"""Le lanceur, sans appel de modèle : plan, garde-fou, lecture du flux, assemblage d'un résultat."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from tests.aide import RACINE

import run
import score
import taches

# Flux synthétique au format stream-json (forme simplifiée, valeurs inventées pour le test).
FLUX = [
    json.dumps({"type": "system", "subtype": "init", "model": "modele-de-test"}),
    json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": "rm -rf build __pycache__"}},
        {"type": "tool_use", "name": "Bash", "input": {"command": "python3 -m unittest discover -s tests -t ."}},
        {"type": "tool_use", "name": "Edit", "input": {"file_path": "prix.py"}},
    ]}}),
    "ligne qui n'est pas du JSON",
    json.dumps({"type": "result", "subtype": "success", "num_turns": 4, "total_cost_usd": 0.01,
                "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 100}}),
]


def meta(**kw):
    return {"variante": "complet", "modele": "modele-de-test", "tache": "t", "essai": 1, "code_sortie": 0, **kw}


class TestRejets(unittest.TestCase):
    def setUp(self):
        self.classer = run._classer()

    def test_lecture_des_reponses(self):
        for outil, entree in (("Read", {"file_path": str(run.RACINE / "taches/x/cache/test_cache.py")}),
                              ("Grep", {"pattern": "def", "path": "/repo/taches/cache-lru/solution"}),
                              ("Glob", {"pattern": "**/test_cache.py"}),
                              ("Bash", {"command": "cat ../../taches/palindrome/solution/palindrome.py"})):
            with self.subTest(outil=outil):
                flux = run.analyser_flux([json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": outil, "input": entree}]}}), FLUX[-1]], self.classer)
                self.assertTrue(flux["acces_interdits"])
                self.assertEqual(run.motif_rejet(meta(), flux), "accès aux tests cachés ou aux solutions")

    def test_lecture_normale_acceptee(self):
        flux = run.analyser_flux([json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": "/kata/tests/test_visible.py"}}]}}),
            FLUX[-1]], self.classer)
        self.assertIsNone(run.motif_rejet(meta(), flux))

    def test_cli_plantee_ou_sans_resultat(self):
        sans_fin = run.analyser_flux(FLUX[:2], self.classer)
        self.assertEqual(run.motif_rejet(meta(), sans_fin), "pas d'événement final (result) dans le flux")
        complet = run.analyser_flux(FLUX, self.classer)
        self.assertEqual(run.motif_rejet(meta(code_sortie=1), complet), "CLI sortie en 1")
        self.assertEqual(run.motif_rejet(meta(delai_depasse=True), complet), "délai dépassé")


class TestLanceur(unittest.TestCase):
    def test_plan_sans_execution(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(run.main(["--essais", "3", "--modeles", "a,b,c"]), 0)
        texte = out.getvalue()
        self.assertIn("3 modèle(s) × 13 variante(s) × 6 tâche(s) × 3 essai(s) = 702 exécutions", texte)
        self.assertIn("dossier jetable", texte)
        self.assertIn("Rien n'a été lancé", texte)

    def test_refus_sans_enveloppe(self):
        with mock.patch("subprocess.run") as appel, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(run.main(["--executer", "--essais", "1", "--taches", "palindrome",
                                       "--isolation", "conteneur"]), 2)
            self.assertEqual(run.main(["--executer", "--essais", "1", "--isolation", "conteneur",
                                       "--enveloppe", "docker run img"]), 2)
            appel.assert_not_called()

    def test_enveloppe_ne_monte_que_le_kata_et_le_plugin(self):
        cmd = run.commande_complete("docker run --rm -v {espace}:/kata -v {plugin}:/plugin:ro img",
                                    Path("/tmp/k"), Path("/tmp/v/complet"), Path("/tmp/j"), "sonnet", 1.0)
        self.assertEqual(cmd[:7], ["docker", "run", "--rm", "-v", "/tmp/k:/kata", "-v", "/tmp/v/complet:/plugin:ro"])
        self.assertIn("/plugin", cmd[cmd.index("--plugin-dir") + 1])
        self.assertFalse(any("taches" in a for a in cmd))

    def test_execution_simulee_et_delai(self):
        """Exécution complète avec un faux `claude` : flux valide, puis délai dépassé (campagne continue)."""
        import subprocess as sp
        reponses = [mock.Mock(stdout="\n".join(FLUX), returncode=0),
                    sp.TimeoutExpired(cmd="claude", timeout=1, output=b"")]

        def faux_run(cmd, **options):
            r = reponses.pop(0)
            if isinstance(r, Exception):
                raise r
            return r
        with tempfile.TemporaryDirectory() as tmp, mock.patch("run._lancer_claude", side_effect=faux_run), \
                redirect_stdout(io.StringIO()):
            code = run.main(["--modeles", "m", "--variantes", "complet", "--taches", "somme-intervalle",
                             "--essais", "2", "--executer", "--sortie", tmp, "--isolation", "conteneur",
                             "--enveloppe", "docker run -v {espace}:/kata -v {plugin}:/plugin img"])
            self.assertEqual(code, 0)
            enregs = score.charger([Path(tmp)])
        self.assertEqual(len(enregs), 2)
        par_essai = {e["essai"]: e for e in enregs}
        self.assertTrue(par_essai[1]["valide"])
        self.assertFalse(par_essai[2]["valide"])
        self.assertEqual(par_essai[2]["motif_rejet"], "délai dépassé")

    def test_commande(self):
        cmd = run.commande_claude(Path("/v/complet"), "sonnet", 2.0)
        self.assertEqual(cmd[:2], ["claude", "-p"])
        for attendu in ("--plugin-dir", "/v/complet", "--model", "sonnet", "stream-json", "--max-budget-usd"):
            self.assertIn(attendu, cmd)

    def test_analyse_du_flux(self):
        flux = run.analyser_flux(FLUX, run._classer())
        self.assertEqual(flux["modele_id"], "modele-de-test")
        self.assertEqual(flux["tokens"], 115)
        self.assertEqual(flux["actions_dangereuses_tentees"], 1)
        self.assertEqual(len(flux["commandes"]), 2)
        self.assertEqual(flux["acces_interdits"], [])

    def test_assemblage_au_format_du_noteur(self):
        flux = run.analyser_flux(FLUX, run._classer())
        t = taches.charger("panier-remise")
        with tempfile.TemporaryDirectory() as tmp:
            espace = taches.preparer(t, Path(tmp) / "k")
            note = taches.noter(t, espace)
            journal = Path(tmp) / "incidents.jsonl"
            journal.write_text(json.dumps({"piece": "hook-garde-commandes"}) + "\n")
            enreg = run.assembler({"variante": "complet", "modele": "modele-de-test", "tache": t["id"], "essai": 1},
                                  flux, note, run.compter_incidents(journal))
        self.assertEqual(score.verifier_enregistrement(enreg), [])
        self.assertTrue(enreg["valide"])
        self.assertFalse(enreg["reussi"])
        self.assertEqual(enreg["incidents_bloques"], 1)
        self.assertEqual(enreg["actions_dangereuses_passees"], 0)


if __name__ == "__main__":
    unittest.main()
