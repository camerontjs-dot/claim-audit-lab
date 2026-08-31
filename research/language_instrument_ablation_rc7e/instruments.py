"""Bounded non-LLM RC7E instrument adapters.

Every language instrument receives untouched raw source. Shared runtime families
are explicit and are not counted as independent merely because annotators differ.
"""
from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Any

from research.language_instrument_ablation_rc7e.contract import make_receipt, proposal, unavailable_receipt

EVENTS={"review","inspect","approve","sign","release"}
PAST={"review":"reviewed","inspect":"inspected","approve":"approved","sign":"signed","release":"released"}

def norm(s: Any) -> str:
    return re.sub(r"\s+"," ",str(s).strip(" \t\n.,:;").lower())

def anchor(raw:str,text:str,start:int|None=None,**extra)->dict[str,Any]:
    if start is None:start=raw.lower().find(str(text).lower())
    row={"text":str(text),**extra}
    if isinstance(start,int) and start>=0:row.update(start=start,end=start+len(str(text)),text=raw[start:start+len(str(text))])
    return row

class RC7DBaseline:
    instrument_id="rc7d_deterministic"
    identity={"base_commit":"253af5313e93932875bdd5956ac46246f3796271","reader_version":"rc7d-d-multi-reader-v1"}
    principle="frozen lexical/rule/finite-state multi-reader bank"
    def run(self,raw:str):
        from research.semantic_operator_jurisdiction_rc7d_d.multi_readers import run_multi
        native=run_multi(raw);dims=[];atoms=[];anchors=[]
        for r in native.get("receipts",[]):
            if r.get("status")!="CLAIMED":continue
            d=r.get("dimension");dims.append(d);ids=[]
            for sp in r.get("spans",[]):
                ids.append(len(anchors));anchors.append({"start":sp.get("start"),"end":sp.get("end"),"text":sp.get("text"),"native_operator":r.get("operator_id")})
            for a in r.get("atoms",[]):atoms.append(proposal(d,a,scorable=True,anchor_ids=ids,note=r.get("operator_id")))
        return make_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,status="CLAIMED" if dims else "NOT_APPLICABLE",proposed_dimensions=dims,anchors=anchors,candidate_atoms=atoms,jurisdiction=["permission","role_binding","quantifier","exception","temporal","subclass","probability","quantitative"],limitations=["known RC7D-D scope/segmentation failures preserved"],native_output=native)

class QuantulumInstrument:
    instrument_id="quantulum3";identity={"package":"quantulum3","version":"0.10.0","classifier":False};principle="quantitative/unit extraction"
    def run(self,raw:str):
        t=time.perf_counter()
        try:
            from quantulum3 import parser
            qs=parser.parse(raw);anchors=[];rows=[];native=[]
            for q in qs:
                surface=getattr(q,"surface",str(q));span=getattr(q,"span",None);a={"text":surface}
                if isinstance(span,tuple) and len(span)==2:a.update(start=int(span[0]),end=int(span[1]))
                anchors.append(a);unit=getattr(getattr(q,"unit",None),"name",None)
                native.append({"surface":surface,"value":getattr(q,"value",None),"unit":unit,"span":span})
                rows.append(proposal("quantitative",{"kind":"quantity_measurement","surface":norm(surface),"value":getattr(q,"value",None),"unit":unit or "dimensionless"},scorable=False,anchor_ids=[len(anchors)-1],note="native quantity retained; no coercion to RC7D taxonomy"))
            return make_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["quantitative"] if rows else [],anchors=anchors,candidate_atoms=rows,jurisdiction=["explicit quantities/units"],limitations=["does not bind quantity to event scope","native atom intentionally unscored against RC7D taxonomy"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,error=f"{type(e).__name__}:{e}")

class StanzaFamily:
    identity={"package":"stanza","version":"1.14.0","language":"en","processors":"tokenize,pos,lemma,depparse,constituency","use_gpu":False}
    def __init__(self):self.nlp=None;self.error=None
    def _load(self):
        if self.nlp is None and self.error is None:
            try:
                import stanza
                self.nlp=stanza.Pipeline(lang="en",processors="tokenize,pos,lemma,depparse,constituency",use_gpu=False,verbose=False,download_method=None)
            except Exception as e:self.error=f"{type(e).__name__}:{e}"
    def analyze(self,raw):
        self._load()
        if self.error:raise RuntimeError(self.error)
        return self.nlp(raw)
    def ud_receipt(self,raw:str):
        t=time.perf_counter();iid="stanza_ud";principle="morphology plus Universal-Dependencies syntax"
        try:
            doc=self.analyze(raw);anchors=[];rows=[];native=[]
            for si,s in enumerate(doc.sentences):
                words={int(w.id):w for w in s.words if isinstance(w.id,int)};children=defaultdict(list)
                for w in words.values():children[int(w.head)].append(w)
                def phrase(w):
                    ids=set()
                    def walk(x):
                        if x.id in ids:return
                        ids.add(x.id)
                        for c in children.get(int(x.id),[]):
                            if c.deprel!="punct":walk(c)
                    walk(w);return " ".join(words[i].text for i in sorted(ids) if i in words)
                for w in words.values():
                    native.append({"sentence":si,"id":w.id,"text":w.text,"lemma":w.lemma,"upos":w.upos,"head":w.head,"deprel":w.deprel})
                    lem=norm(w.lemma or w.text);kids=children.get(int(w.id),[])
                    if lem not in EVENTS or not str(w.upos).startswith("V"):continue
                    active=[x for x in kids if x.deprel=="nsubj"];passive=[x for x in kids if str(x.deprel).startswith("nsubj:pass")];objs=[x for x in kids if x.deprel in {"obj","iobj"}];agents=[x for x in kids if x.deprel=="obl:agent"]
                    subj=obj=None
                    if passive and agents:subj,obj=phrase(agents[0]),phrase(passive[0])
                    elif active and objs:subj,obj=phrase(active[0]),phrase(objs[0])
                    if subj and obj:
                        pol="negative" if any(norm(c.lemma or c.text) in {"not","never","no"} for c in kids) else "positive"
                        anchors.append(anchor(raw,s.text,sentence=si,verb_node=w.id));rows.append(proposal("role_binding",{"kind":"event","predicate":lem,"subject":norm(subj),"object":norm(obj),"polarity":pol},scorable=True,anchor_ids=[len(anchors)-1],note="UD argument binding"))
            return make_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=principle,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["role_binding"] if rows else [],anchors=anchors,candidate_atoms=rows,jurisdiction=["dependency-visible predicate/argument binding","attached surface negation"],limitations=["not SRL","coordination/control/ellipsis not normalized"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=principle,error=f"{type(e).__name__}:{e}")
    def constituency_receipt(self,raw:str):
        t=time.perf_counter();iid="stanza_constituency";principle="constituency phrase structure"
        try:
            doc=self.analyze(raw);anchors=[];rows=[];native=[]
            for si,s in enumerate(doc.sentences):
                tree=str(s.constituency);native.append({"sentence":si,"tree":tree});low=s.text.lower();marker=next((m for m in ("if","unless","provided that","assuming that") if re.search(rf"\b{re.escape(m)}\b",low)),None)
                if marker and "SBAR" in tree:
                    anchors.append(anchor(raw,s.text,sentence=si,tree=tree));rows.append(proposal("conditional",{"kind":"conditional_scope","marker":marker,"condition":norm(s.text),"consequent":"unresolved"},scorable=False,anchor_ids=[len(anchors)-1],note="construction observed; no semantic decomposition"))
            return make_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=principle,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["conditional"] if rows else [],anchors=anchors,candidate_atoms=rows,jurisdiction=["phrase structure","conditional construction detection"],limitations=["no truth-conditional decomposition","conditional atom unscored"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=principle,error=f"{type(e).__name__}:{e}")

class CoreNLPFamily:
    identity={"runtime":"Stanford CoreNLP","version":"4.5.10","license":"GPL-3.0","annotators":"tokenize,ssplit,pos,lemma,ner,depparse,natlog,openie,coref,quote"}
    def __init__(self):self.client=None;self.error=None
    def _load(self):
        if self.client is None and self.error is None:
            try:
                from stanza.server import CoreNLPClient
                self.client=CoreNLPClient(annotators=["tokenize","ssplit","pos","lemma","ner","depparse","natlog","openie","coref","quote"],timeout=120000,memory="4G",be_quiet=True,properties={"quote.attribution":"true"});self.client.start()
            except Exception as e:self.error=f"{type(e).__name__}:{e}"
    def close(self):
        if self.client:
            try:self.client.stop()
            except Exception:pass
    def analyze(self,raw):
        self._load()
        if self.error:raise RuntimeError(self.error)
        return self.client.annotate(raw,output_format="json")
    def openie_receipt(self,raw):
        t=time.perf_counter();iid="corenlp_openie";p="Open Information Extraction"
        try:
            data=self.analyze(raw);anchors=[];rows=[];native=[];scores=[]
            for si,s in enumerate(data.get("sentences",[])):
                for tr in s.get("openie",[]):
                    native.append(tr);rel=norm(tr.get("relation",""));subj=norm(tr.get("subject",""));obj=norm(tr.get("object",""));lem=next((v for v in EVENTS if re.search(rf"\b{v}(?:ed|s|ing)?\b",rel)),None)
                    if tr.get("confidence") is not None:scores.append({"type":"openie_confidence","value":tr.get("confidence")})
                    if lem and subj and obj:
                        txt=f"{tr.get('subject','')} {tr.get('relation','')} {tr.get('object','')}";anchors.append(anchor(raw,txt,sentence=si,native_confidence=tr.get("confidence")));rows.append(proposal("role_binding",{"kind":"event","predicate":lem,"subject":subj,"object":obj,"polarity":"negative" if re.search(r"\b(not|never|no)\b",rel) else "positive"},scorable=True,anchor_ids=[len(anchors)-1]))
            return make_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["role_binding"] if rows else [],anchors=anchors,candidate_atoms=rows,native_scores=scores,jurisdiction=["S-R-O propositions"],limitations=["scope overgeneralization possible","shared CoreNLP family"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,error=f"{type(e).__name__}:{e}")
    def natlog_receipt(self,raw):
        t=time.perf_counter();iid="corenlp_natlog";p="natural-logic quantifier/polarity/scope"
        try:
            data=self.analyze(raw);anchors=[];rows=[];native=[]
            for si,s in enumerate(data.get("sentences",[])):
                for ti,tok in enumerate(s.get("tokens",[])):
                    if "polarity" in tok or "operator" in tok:native.append({k:tok.get(k) for k in ("index","word","lemma","pos","polarity","operator") if k in tok})
                    if norm(tok.get("word","")) in {"all","every","each","some","no","none"} or "operator" in tok:
                        anchors.append({"start":tok.get("characterOffsetBegin"),"end":tok.get("characterOffsetEnd"),"text":tok.get("word"),"sentence":si,"token":ti,"operator":tok.get("operator"),"polarity":tok.get("polarity")});rows.append(proposal("quantifier",None,scorable=False,anchor_ids=[len(anchors)-1],note="operator/polarity observed; no population+predicate normalization"))
            return make_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["quantifier"] if rows else [],anchors=anchors,candidate_atoms=rows,jurisdiction=["natural-logic operators/polarity"],limitations=["not full epistemic/deontic/counterfactual factuality","shared CoreNLP family"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,error=f"{type(e).__name__}:{e}")
    def sutime_receipt(self,raw):
        t=time.perf_counter();iid="corenlp_sutime";p="temporal expression extraction/normalization"
        try:
            data=self.analyze(raw);anchors=[];rows=[];native=[]
            for si,s in enumerate(data.get("sentences",[])):
                for em in s.get("entitymentions",[]):
                    if em.get("ner") not in {"DATE","TIME","DURATION","SET"}:continue
                    native.append(em);text=em.get("text","");b=em.get("characterOffsetBegin");anchors.append({"start":b,"end":em.get("characterOffsetEnd"),"text":text,"sentence":si,"normalizedNER":em.get("normalizedNER")});prefix=raw[max(0,(b or 0)-18):(b or 0)].lower() if isinstance(b,int) else "";rel=next((v for word,v in (("before","before"),("after","after"),("until","until"),("as of","as_of"),("since","since")) if re.search(rf"\b{re.escape(word)}\s*$",prefix)),None);rows.append(proposal("temporal",{"kind":"temporal_scope","relation":rel,"reference":norm(text)} if rel else None,scorable=bool(rel),anchor_ids=[len(anchors)-1],note="temporal expression" if not rel else "adjacent explicit relation"))
            return make_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["temporal"] if rows else [],anchors=anchors,candidate_atoms=rows,jurisdiction=["temporal expressions","adjacent explicit ordering relation"],limitations=["not full event ordering","shared CoreNLP family"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,error=f"{type(e).__name__}:{e}")
    def coref_quote_receipt(self,raw):
        t=time.perf_counter();iid="corenlp_coref_quote";p="discourse coreference and quote attribution"
        try:
            data=self.analyze(raw);rows=[];anchors=[];native={"corefs":data.get("corefs",{}),"quotes":data.get("quotes",[])}
            for chain,mentions in data.get("corefs",{}).items():
                names=[norm(m.get("text","")) for m in mentions if m.get("text")]
                if len(names)>=2:rows.append(proposal("coreference",{"kind":"coreference_chain","mentions":names},scorable=True,note=f"chain {chain}"))
            for q in data.get("quotes",[]):
                speaker=q.get("canonicalSpeaker") or q.get("speaker");text=q.get("text") or q.get("quote")
                if speaker and text and norm(speaker) not in {"unknown","null","none"}:
                    anchors.append({"start":q.get("characterOffsetBegin"),"end":q.get("characterOffsetEnd"),"text":text,"speaker":speaker});rows.append(proposal("attribution",{"kind":"attribution","speaker":norm(speaker),"quote":norm(text)},scorable=True,anchor_ids=[len(anchors)-1]))
            dims=sorted({r["dimension"] for r in rows})
            return make_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=dims,anchors=anchors,candidate_atoms=rows,jurisdiction=["within-document coreference","direct quote attribution"],limitations=["does not establish truth of attributed proposition","shared CoreNLP family"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=iid,instrument_identity=self.identity,measurement_principle=p,error=f"{type(e).__name__}:{e}")

class SuParSDP:
    instrument_id="supar_sdp";identity={"package":"supar","version":"1.1.4","model":"sdp-biaffine-en","representation":"DM","input_preprocessor":"independent stanza==1.14.0 tokenize,pos,lemma"};principle="semantic dependency graph (DM)"
    def __init__(self):self.parser=None;self.prep=None;self.error=None
    def _load(self):
        if self.parser is not None or self.error:return
        try:
            from supar import Parser
            import stanza
            self.prep=stanza.Pipeline(lang="en",processors="tokenize,pos,lemma",use_gpu=False,verbose=False,download_method=None);self.parser=Parser.load("sdp-biaffine-en")
        except Exception as e:self.error=f"{type(e).__name__}:{e}"
    def run(self,raw):
        t=time.perf_counter();self._load()
        if self.error:return unavailable_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,error=self.error,limitations=["conditional instrument; qualification required"])
        try:
            doc=self.prep(raw);rows=[];native=[]
            for si,s in enumerate(doc.sentences):
                toks=[(w.text,w.lemma or w.text,w.xpos or w.upos or "_") for w in s.words];parsed=self.parser.predict([toks],verbose=False)[0];conll=str(parsed);native.append({"sentence":si,"conll":conll});lines=[ln.split("\t") for ln in conll.splitlines() if ln and not ln.startswith("#")];tokens={int(c[0]):c for c in lines if c and c[0].isdigit()};incoming=defaultdict(list)
                for tid,c in tokens.items():
                    deps=c[8] if len(c)>8 else "_"
                    for dep in ([] if deps in {"","_"} else deps.split("|")):
                        if ":" in dep:
                            h,label=dep.split(":",1)
                            if h.isdigit():incoming[int(h)].append((tid,label))
                for head,edges in incoming.items():
                    h=tokens.get(head);lem=norm(h[2] if h and len(h)>2 else "")
                    if lem not in EVENTS:continue
                    a1=[tokens[i][1] for i,l in edges if l=="ARG1" and i in tokens];a2=[tokens[i][1] for i,l in edges if l=="ARG2" and i in tokens]
                    if a1 and a2:rows.append(proposal("role_binding",{"kind":"event","predicate":lem,"subject":norm(a1[0]),"object":norm(a2[0]),"polarity":"positive"},scorable=True,note="bounded DM ARG1/ARG2 mapping"))
            return make_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["role_binding"] if rows else [],candidate_atoms=rows,jurisdiction=["DM graph","simple ARG1/ARG2 event binding"],limitations=["DM labels are not PropBank roles","Stanza preprocessing independently rerun from raw","negation not normalized in v1"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=native)
        except Exception as e:return unavailable_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,error=f"{type(e).__name__}:{e}")

class DebertaNLI:
    instrument_id="deberta_nli";identity={"model":"MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli","revision":"e5350efffb6dea3ad0962eafd0bc0b9e212a9ff8","task":"sequence-classification NLI","license":"MIT"};principle="bounded discriminative entailment relation measurement"
    def __init__(self):self.tok=None;self.model=None;self.error=None
    def _load(self):
        if self.model is not None or self.error:return
        try:
            import torch
            from transformers import AutoTokenizer,AutoModelForSequenceClassification
            self.torch=torch;self.tok=AutoTokenizer.from_pretrained(self.identity["model"],revision=self.identity["revision"]);self.model=AutoModelForSequenceClassification.from_pretrained(self.identity["model"],revision=self.identity["revision"]);self.model.eval()
        except Exception as e:self.error=f"{type(e).__name__}:{e}"
    def hyp(self,a):
        k=a.get("kind")
        if k=="event":
            p=norm(a.get("predicate",""));return f"{a.get('subject','')} did not {p} {a.get('object','')}." if a.get("polarity")=="negative" else f"{a.get('subject','')} {PAST.get(p,p)} {a.get('object','')}."
        if k=="necessary_permission_condition":return f"Only {a.get('population','')} may {a.get('predicate','')}."
        if k=="subclass":return f"{a.get('child','')} are a subclass of {a.get('parent','')}."
        if k=="exception":return f"{a.get('excluded','')} is an exception."
    def measure(self,raw,typed):
        t=time.perf_counter();self._load()
        if self.error:return unavailable_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,error=self.error)
        try:
            out=[];id2={int(k):str(v).lower() for k,v in dict(self.model.config.id2label).items()}
            for row in typed:
                a=row.get("atom");h=self.hyp(a) if isinstance(a,dict) else None
                if not h:continue
                inp=self.tok(raw,h,truncation=True,return_tensors="pt")
                with self.torch.no_grad():probs=self.torch.softmax(self.model(**inp).logits[0],-1).tolist()
                scores={id2.get(i,f"label_{i}"):float(v) for i,v in enumerate(probs)};out.append({"proposal_dimension":row.get("dimension"),"proposal_atom":a,"hypothesis":h,"scores":scores})
            return make_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,status="CLAIMED" if out else "NOT_APPLICABLE",native_scores=[{"type":"nli_relation","measurement":m} for m in out],jurisdiction=["source↔independently typed proposal relation"],limitations=["cannot originate atoms","scores do not grant authority","not cross-dimension calibrated"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output=out)
        except Exception as e:return unavailable_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,error=f"{type(e).__name__}:{e}")

class OWLRLReasoner:
    instrument_id="owlrl_reasoner";identity={"rdflib":"7.6.0","owlrl":"7.6.2","profile":"RDFS subclass closure only"};principle="symbolic reasoning over already-warranted typed propositions"
    def infer(self,raw,warranted):
        t=time.perf_counter()
        try:
            from rdflib import Graph,Namespace,RDFS,URIRef
            from owlrl import DeductiveClosure,RDFS_Semantics
            ex=Namespace("urn:rc7e:");g=Graph();prem=[]
            def u(s):return URIRef(ex+re.sub(r"[^a-z0-9]+","_",norm(s)))
            for a in warranted.get("subclass",[]):
                if a.get("kind")=="subclass":g.add((u(a["child"]),RDFS.subClassOf,u(a["parent"])));prem.append(a)
            before=set(g);DeductiveClosure(RDFS_Semantics).expand(g);rows=[]
            for c,_,p in g.triples((None,RDFS.subClassOf,None)):
                if (c,RDFS.subClassOf,p) in before or c==p:continue
                rows.append(proposal("subclass",{"kind":"subclass","child":str(c).split("urn:rc7e:")[-1].replace("_"," "),"parent":str(p).split("urn:rc7e:")[-1].replace("_"," ")},scorable=True,note="RDFS closure; premise lineage retained"))
            return make_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,status="CLAIMED" if rows else "NOT_APPLICABLE",proposed_dimensions=["subclass"] if rows else [],candidate_atoms=rows,jurisdiction=["closure over warranted subclass atoms"],limitations=["not raw-language interpretation","cannot rescue unwarranted premises"],runtime={"latency_s":time.perf_counter()-t,"load_status":"OK"},native_output={"premises":prem,"triple_count":len(g)})
        except Exception as e:return unavailable_receipt(raw,instrument_id=self.instrument_id,instrument_identity=self.identity,measurement_principle=self.principle,error=f"{type(e).__name__}:{e}")

def instrument_identities():
    return {"rc7d_deterministic":RC7DBaseline.identity,"quantulum3":QuantulumInstrument.identity,"stanza_ud":StanzaFamily.identity,"stanza_constituency":StanzaFamily.identity,"corenlp_openie":CoreNLPFamily.identity,"corenlp_natlog":CoreNLPFamily.identity,"corenlp_sutime":CoreNLPFamily.identity,"corenlp_coref_quote":CoreNLPFamily.identity,"supar_sdp":SuParSDP.identity,"deberta_nli":DebertaNLI.identity,"owlrl_reasoner":OWLRLReasoner.identity}
