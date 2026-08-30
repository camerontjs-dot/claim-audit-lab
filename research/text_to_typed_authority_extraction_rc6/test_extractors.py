import unittest
from research.text_to_typed_authority_extraction_rc6 import extractor_regex as a
from research.text_to_typed_authority_extraction_rc6 import extractor_tokens as b

class ExtractorSentinels(unittest.TestCase):
    def test_simple_membership(self):
        text="Lena is a certified inspector. Certified inspectors log seals."; q="Lena is a certified inspector."
        self.assertEqual(a.extract(text,q)["status"],"unknown")
        self.assertEqual(b.extract(text,q)["status"],"unknown")

    def test_ontology_escape(self):
        text="Most inspectors log seals."; q="Every inspector logs seals."
        self.assertEqual(a.extract(text,q)["reason"],"ontology_escape")
        self.assertEqual(b.extract(text,q)["reason"],"ontology_escape")

    def test_only_necessary_condition(self):
        text="Only licensed inspectors may open the vault. Nia is a licensed inspector."; q="Nia may open the vault."
        for ext in (a,b):
            r=ext.extract(text,q); self.assertEqual(r["status"],"resolved"); self.assertEqual(r["case"]["authority"]["membership"],"member")

    def test_role_order(self):
        text="Mira approved Jalen."; q="Jalen approved Mira."
        for ext in (a,b):
            r=ext.extract(text,q); self.assertEqual(r["status"],"resolved"); self.assertEqual(r["case"]["query"]["roles"]["subject"],"Jalen")

if __name__=="__main__": unittest.main()
