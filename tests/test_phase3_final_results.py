import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

from scripts.phase3_final_results import (ROOT, P1_FILES, P2_FILES, require_pinned_bytes, require_output_hash,
    check_run_links, asi_events, main_wealth, build_tables, readable_tables, table_filename,
    payload_hash, validate_bundle, sha)
from scripts.phase3_figures import render_figures, verify_figure_annotations, figure_payloads


def committed_tables():
    e={key:pd.read_csv(ROOT/f"results/phase2_results/{name}") for key,name in P2_FILES.items()}
    e.update({key:pd.read_csv(ROOT/f"docs/phase1/{name}") for key,name in P1_FILES.items()})
    return e


class TestPhase3Publication(unittest.TestCase):
    def test_pinned_evidence_allows_only_line_end_conversion(self):
        require_pinned_bytes(b"a,b\r\n1,2\r\n",b"a,b\n1,2\n","test")
        with self.assertRaisesRegex(ValueError,"frozen commit"):
            require_pinned_bytes(b"a,b\n1,3\n",b"a,b\n1,2\n","test")

    def test_output_fingerprint_rejects_stale_values(self):
        require_output_hash(b"x\n1\n",sha(b"x\r\n1\r\n"),"test")
        with self.assertRaisesRegex(ValueError,"Stale"):
            require_output_hash(b"x\n2\n",sha(b"x\n1\n"),"test")

    def test_run_id_and_dataset_vintage_must_match(self):
        p1={"run_id":"p1","price_snapshots":{m:{"sha256":"frozen"} for m in ("US","China","India")}}
        p2={"run_id":"p2","frozen_phase1_inputs":{m:{"sha256":"frozen"} for m in ("US","China","India")}}
        check_run_links(p1,p2,{"run_id":"p2"})
        with self.assertRaisesRegex(ValueError,"different source run"):
            check_run_links(p1,p2,{"run_id":"wrong"})
        p2["frozen_phase1_inputs"]["US"]["sha256"]="new-vintage"
        with self.assertRaisesRegex(ValueError,"vintages differ"):
            check_run_links(p1,p2,{"run_id":"p2"})

    def test_asi_comes_from_successive_actual_decisions(self):
        decisions=pd.DataFrame({"Date":pd.bdate_range("2020-01-01",periods=3),"Market":"US","Model":"Black-Litterman",
            "Target Weight Cap":1.,"Target Weights JSON":[json.dumps(w) for w in ({"A":.5,"B":.5},{"B":.3,"A":.7},{"A":.6,"B":.4})]})
        values=asi_events(decisions)
        np.testing.assert_allclose(values["ASI Event"],[.4,.2],atol=1e-12)
        self.assertEqual(len(values),2)
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            asi_events(pd.concat([decisions,decisions.iloc[:1]]))

    def test_wealth_uses_net_10bps_main_cap_and_initial_nav(self):
        dates=pd.bdate_range("2020-01-01",periods=2)
        daily=pd.DataFrame({"Date":list(dates)*2,"Market":"US","Model":"Black-Litterman",
            "Target Weight Cap":[1,1,.4,.4],"Net Return 10bps":[-.2,.25,1,1],"Gross Return":[.5,.5,2,2]})
        series=main_wealth(daily,"US","Black-Litterman")
        np.testing.assert_allclose(series["wealth"],[1,.8,1],atol=1e-12)
        self.assertEqual(series["observations"],2)
        self.assertEqual(series["dates"][0],series["dates"][1])

    def test_publication_tables_retain_source_values_units_and_phase(self):
        e=committed_tables(); tables=build_tables(e)
        np.testing.assert_allclose(tables[2]["Net Annualized Return"],e["principal"]["Annualized Return"],atol=0,rtol=0)
        self.assertTrue(tables[7]["Evidence Phase"].eq("Phase 1 supplementary").all())
        self.assertFalse(any(c in tables[6] for c in ("Max Drawdown","Recovery Trading Days","Volatility Spike")))
        for _,r in tables[7][tables[7].Term.eq("Alpha")].iterrows():
            source=e["factors"][e["factors"].Model.eq(r.Model)].iloc[0]
            self.assertEqual(r.Coefficient,source.Alpha)
            self.assertEqual(r["HAC t-statistic"],source.Alpha_t_stat)
            self.assertAlmostEqual(r["Alpha Annualized Arithmetic"],252*r.Coefficient)
        for _,r in tables[3][tables[3]["Target Weight Cap"].eq(.4)].iterrows():
            original=e["concentration"][e["concentration"].Market.eq(r.Market)&e["concentration"].Model.eq(r.Model)&e["concentration"]["Target Weight Cap"].eq(1)].iloc[0]
            self.assertAlmostEqual(r["Return Change vs 100% Cap (bps)"],10000*(r["Net Annualized Return"]-original["Annualized Return"]))
        self.assertIn("<0.0001",readable_tables(tables))

    def test_payloads_preserve_caps_sources_and_phase_boundaries(self):
        e=committed_tables(); tables=build_tables(e)
        e.update({"daily":pd.DataFrame(),"decisions":pd.DataFrame()})
        with patch("scripts.phase3_figures.main_wealth",return_value={"dates":["2020-01-01"],"wealth":[1.],"observations":0}), patch("scripts.phase3_figures.asi_events") as events:
            events.return_value=pd.DataFrame([{"Market":m,"Model":model,"Target Weight Cap":1.,"ASI Event":.1} for m in ("US","China","India") for model in ("Black-Litterman","Markowitz")])
            payloads=figure_payloads(e,tables)
        self.assertNotIn("07_crisis_drawdown_paths",payloads)
        self.assertEqual(payloads["08_us_factor_exposures"]["phase"],"Phase 1")
        for panel in payloads["04_matched_concentration"]["panels"]:
            for series in panel["series"]:
                self.assertEqual(series["x"],["100%","40%"])
                original=tables[3][tables[3].Market.eq(panel["market"])&tables[3].Model.eq(series["model"])]
                self.assertEqual(series["y"],[original[original["Target Weight Cap"].eq(c)]["Sharpe Ratio"].iloc[0] for c in (1,.4)])

    def test_svg_annotations_are_generated_and_checked(self):
        payload={"test":{"kind":"bars","title":"Synthetic figure verification","ylabel":"L1 distance","models":["Black-Litterman"],
            "source":["synthetic-test-only"],"phase":"Test","caption":"Synthetic",
            "rows":[{"market":m,"model":"Black-Litterman","value":.3,"annotation":"0.3000"} for m in ("US","China","India")]}}
        with tempfile.TemporaryDirectory() as temp:
            records=render_figures(payload,Path(temp))
            self.assertTrue((Path(temp)/"test.png").is_file())
            verify_figure_annotations(Path(temp)/"test.svg",records["test"]["annotations"])
            with self.assertRaisesRegex(ValueError,"annotation"):
                verify_figure_annotations(Path(temp)/"test.svg",["0.9999"])

    def test_changed_table_fails_even_if_output_hash_is_updated(self):
        e=committed_tables();e.update({"inputs":{},"p1":{"run_id":"p1"},"p2":{"run_id":"p2"}})
        tables=build_tables(e)
        payload={"test":{"source":["synthetic"],"phase":"Test"}}
        with tempfile.TemporaryDirectory() as temp, patch("scripts.phase3_final_results.validate_numeric_links"), patch("scripts.phase3_figures.figure_payloads",return_value=payload):
            out=Path(temp);(out/"figures").mkdir()
            for n,frame in tables.items():frame.to_csv(out/table_filename(n),index=False)
            (out/"FINAL_RESEARCH_TABLES.md").write_text(readable_tables(tables),encoding="utf-8")
            (out/"figures/test.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            manifest={"source_runs":{"Phase 1":"p1","Phase 2":"p2"},"inputs":{},"figures":{"test":{
                "payload_sha256":payload_hash(payload["test"]),"source_files":["synthetic"],"phase":"Test","annotations":[]}},
                "outputs":{}}
            path=out/"PHASE3_RUN_MANIFEST.json";path.write_text(json.dumps(manifest))
            self.assertEqual(validate_bundle(out,e)["status"],"PASS")
            bad=pd.read_csv(out/table_filename(2));bad.loc[0,"Net Annualized Return"]+=.01
            bad.to_csv(out/table_filename(2),index=False)
            manifest["outputs"][table_filename(2)]=sha((out/table_filename(2)).read_bytes())
            path.write_text(json.dumps(manifest))
            with self.assertRaises(AssertionError):validate_bundle(out,e)
