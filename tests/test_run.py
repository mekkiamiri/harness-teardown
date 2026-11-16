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


class TestLanceur(unittest.TestCase):
    def test_plan_sans_execution(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(run.main(["--essais", "3"]), 0)
        texte = out.getvalue()
        self.assertIn("3 modèle(s) × 12 variante(s) × 6 tâche(s) × 3 essai(s) = 648 exécutions", texte)
        self.assertIn("Rien n'a été lancé", texte)

    def test_refus_hors_conteneur(self):
        with mock.patch.dict(os.environ, {"TEARDOWN_CONTENEUR": ""}), \
                mock.patch("subprocess.run") as appel, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(run.main(["--executer", "--essais", "1", "--taches", "palindrome"]), 2)
            appel.assert_not_called()

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

    def test_assemblage_au_format_du_noteur(self):
        flux = run.analyser_flux(FLUX, run._classer())
        t = taches.charger("panier-remise")
        with tempfile.TemporaryDirectory() as tmp:
            espace = taches.preparer(t, Path(tmp) / "k")
            note = taches.noter(t, espace)
            journal = Path(tmp) / "incidents.jsonl"
            journal.write_text(json.dumps({"piece": "hook-garde-commandes"}) + "\n")
            enreg = run.assembler({"variante": "complet", "modele": "sonnet", "tache": t["id"], "essai": 1},
                                  flux, note, run.compter_incidents(journal))
        self.assertEqual(score.verifier_enregistrement(enreg), [])
        self.assertFalse(enreg["reussi"])
        self.assertEqual(enreg["incidents_bloques"], 1)
        self.assertEqual(enreg["actions_dangereuses_passees"], 0)


if __name__ == "__main__":
    unittest.main()
