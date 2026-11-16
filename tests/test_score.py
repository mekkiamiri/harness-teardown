"""Le noteur. Les nombres ci-dessous sont des données synthétiques de test, pas des mesures."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.aide import RACINE

import score
import variants


def exec_(variante, modele, reussi, tokens, essai=1, tache="t1", bloques=0, passees=0, modifies=False):
    return {"variante": variante, "modele": modele, "tache": tache, "essai": essai, "reussi": reussi,
            "tokens": tokens, "incidents_bloques": bloques, "actions_dangereuses_passees": passees,
            "tests_modifies": modifies}


SYNTHETIQUE = [
    exec_("complet", "petit", True, 1000), exec_("complet", "petit", True, 1000, essai=2),
    exec_("sans-skill-corriger", "petit", True, 1500), exec_("sans-skill-corriger", "petit", False, 1500, essai=2),
    exec_("sans-hook-garde-commandes", "petit", True, 900, passees=2),
    exec_("complet", "grand", True, 2000, bloques=1),
]


class TestScore(unittest.TestCase):
    def setUp(self):
        self.donnees = variants.charger_pieces()

    def ligne(self, lignes, variante):
        return next(l for l in lignes if l["variante"] == variante)

    def test_deltas(self):
        lignes = score.tableau(SYNTHETIQUE, self.donnees, ["petit", "grand"])
        c = self.ligne(lignes, "sans-skill-corriger")["modeles"]["petit"]
        self.assertEqual(c["delta_reussite_pts"], -50.0)
        self.assertEqual(c["delta_tokens_pct"], 50.0)
        self.assertIsNone(self.ligne(lignes, "sans-skill-corriger")["modeles"]["grand"])
        g = self.ligne(lignes, "sans-hook-garde-commandes")["modeles"]["petit"]
        self.assertEqual(g["actions_dangereuses_passees"], 2)
        self.assertEqual(self.ligne(lignes, "sans-skill-corriger")["etiquette"], "compense")

    def test_toutes_les_pieces_ont_une_ligne(self):
        lignes = score.tableau([], self.donnees, [])
        self.assertEqual(len(lignes), len(self.donnees["pieces"]) + 2)

    def test_tableau_vide_a_mesurer(self):
        md = score.en_markdown(score.tableau([], self.donnees, []), [])
        self.assertIn("à mesurer", md)
        self.assertNotRegex(md, r"[+-]\d")

    def test_markdown_avec_donnees(self):
        md = score.en_markdown(score.tableau(SYNTHETIQUE, self.donnees, ["petit", "grand"]), ["petit", "grand"])
        self.assertIn("| skill-corriger | compense | -50.0 pts | à mesurer |", md)

    def test_format_invalide(self):
        self.assertTrue(score.verifier_enregistrement({"variante": "x"}))
        mauvais = dict(SYNTHETIQUE[0], tokens=-1)
        self.assertTrue(score.verifier_enregistrement(mauvais))
        mauvais = dict(SYNTHETIQUE[0], reussi="oui")
        self.assertTrue(score.verifier_enregistrement(mauvais))
        self.assertEqual(score.verifier_enregistrement(SYNTHETIQUE[0]), [])

    def test_chargement_dossier_et_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "petit" / "complet"
            d.mkdir(parents=True)
            (d / "t1-1.json").write_text(json.dumps(SYNTHETIQUE[0]))
            (Path(tmp) / "lot.json").write_text(json.dumps(SYNTHETIQUE[1:]))
            (d / "t1-1.stream.jsonl").write_text("pas du json\n")
            self.assertEqual(len(score.charger([Path(tmp)])), len(SYNTHETIQUE))
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(score.main([tmp, "--json"]), 0)
            self.assertIn("delta_reussite_pts", out.getvalue())

    def test_cli_sans_resultats(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(score.main([]), 0)
        self.assertIn("à mesurer", out.getvalue())


if __name__ == "__main__":
    unittest.main()
