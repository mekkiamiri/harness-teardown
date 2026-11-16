"""Le générateur de variantes : une variante par pièce, chacune valide et privée de cette seule pièce."""
import json
import tempfile
import unittest
from pathlib import Path

from tests.aide import PLUGIN

import variants


class TestVariantes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.donnees = variants.charger_pieces()
        cls.variantes = variants.generer(Path(cls.tmp.name) / "v", donnees=cls.donnees)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_noms(self):
        attendus = {"complet", "vide"} | {f"sans-{p['id']}" for p in self.donnees["pieces"]}
        self.assertEqual(set(self.variantes), attendus)

    def test_toutes_valides(self):
        for nom, dossier in self.variantes.items():
            with self.subTest(variante=nom):
                self.assertEqual(variants.valider(dossier), [])

    def test_chaque_variante_perd_exactement_sa_piece(self):
        tous = {p["id"] for p in self.donnees["pieces"]}
        self.assertEqual(variants.pieces_presentes(self.variantes["complet"], self.donnees), tous)
        self.assertEqual(variants.pieces_presentes(self.variantes["vide"], self.donnees), set())
        for p in self.donnees["pieces"]:
            with self.subTest(piece=p["id"]):
                restantes = variants.pieces_presentes(self.variantes[f"sans-{p['id']}"], self.donnees)
                self.assertEqual(restantes, tous - {p["id"]})

    def test_hooks_retires_du_json(self):
        for p in self.donnees["pieces"]:
            for script in p["retrait"]["scripts_hooks"]:
                with self.subTest(piece=p["id"]):
                    hooks = self.variantes[f"sans-{p['id']}"] / "hooks" / "hooks.json"
                    self.assertNotIn(script, hooks.read_text(encoding="utf-8"))
                    self.assertIn(script, (self.variantes["complet"] / "hooks" / "hooks.json").read_text())

    def test_source_intacte(self):
        self.assertEqual(variants.valider(PLUGIN), [])
        self.assertEqual(variants.pieces_presentes(PLUGIN, self.donnees),
                         {p["id"] for p in self.donnees["pieces"]})


class TestValidateur(unittest.TestCase):
    """Le validateur doit vraiment détecter les plugins cassés."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = variants.generer(Path(self.tmp.name) / "v")["complet"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifeste_absent(self):
        (self.p / ".claude-plugin" / "plugin.json").unlink()
        self.assertTrue(variants.valider(self.p))

    def test_nom_reserve(self):
        f = self.p / ".claude-plugin" / "plugin.json"
        f.write_text(json.dumps({"name": "claude-katas"}))
        self.assertTrue(variants.valider(self.p))

    def test_script_de_hook_manquant(self):
        (self.p / "scripts" / "garde_tests.py").unlink()
        self.assertTrue(any("garde_tests.py" in e for e in variants.valider(self.p)))

    def test_skill_sans_description(self):
        (self.p / "skills" / "planifier" / "SKILL.md").write_text("# rien\n")
        self.assertTrue(variants.valider(self.p))

    def test_hooks_sans_enveloppe(self):
        (self.p / "hooks" / "hooks.json").write_text(json.dumps({"Stop": []}))
        self.assertTrue(variants.valider(self.p))


class TestSortie(unittest.TestCase):
    def test_refuse_le_depot_et_ses_parents(self):
        from tests.aide import RACINE
        for cible in (RACINE, RACINE.parent, RACINE / "plugin", RACINE / "plugin" / "skills"):
            with self.subTest(cible=cible):
                with self.assertRaises(ValueError):
                    variants.verifier_sortie(cible, PLUGIN)

    def test_refuse_un_dossier_etranger_non_vide(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "precieux.txt").write_text("x")
            with self.assertRaises(ValueError):
                variants.generer(Path(tmp))
            self.assertTrue((Path(tmp) / "precieux.txt").exists())

    def test_regenere_son_propre_dossier(self):
        with tempfile.TemporaryDirectory() as tmp:
            variants.generer(Path(tmp) / "v")
            variants.generer(Path(tmp) / "v")
            self.assertTrue((Path(tmp) / "v" / variants.MARQUEUR).exists())

    def test_cli_refuse(self):
        import io
        from contextlib import redirect_stderr
        from tests.aide import RACINE
        with redirect_stderr(io.StringIO()):
            self.assertEqual(variants.main(["--sortie", str(RACINE)]), 2)
        self.assertTrue((RACINE / "teardown" / "pieces.json").exists())


class TestManifesteDesPieces(unittest.TestCase):
    def test_champs(self):
        donnees = variants.charger_pieces()
        ids = [p["id"] for p in donnees["pieces"]]
        self.assertEqual(len(ids), len(set(ids)))
        for p in donnees["pieces"]:
            with self.subTest(piece=p["id"]):
                for champ in ("id", "type", "etiquette", "hypothese", "comment_retirer", "retrait", "prediction"):
                    self.assertTrue(p.get(champ), champ)
                self.assertIn(p["etiquette"], ("compense", "gouverne", "témoin"))
                self.assertTrue(set(p["prediction"].values()) <= {"+", "0", "?", "—"})
                self.assertEqual(set(p["prediction"]), {"petit", "moyen", "grand"})
        etiquettes = {p["etiquette"] for p in donnees["pieces"]}
        self.assertEqual(etiquettes, {"compense", "gouverne", "témoin"})
        temoins = [p for p in donnees["pieces"] if p["etiquette"] == "témoin"]
        self.assertEqual([p["id"] for p in temoins], ["temoin-neutre"])

    def test_temoin_sans_effet(self):
        """Aucun composant chargé du plugin ne mentionne le dossier témoin (le README n'est pas chargé)."""
        for f in PLUGIN.rglob("*"):
            if f.is_file() and "temoin" not in f.parts and "__pycache__" not in f.parts and f.name != "README.md":
                self.assertNotIn("temoin/", f.read_text(encoding="utf-8", errors="ignore"), str(f))


if __name__ == "__main__":
    unittest.main()
