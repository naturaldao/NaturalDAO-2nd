"""Build the frozen, synthetic, English-language comparison set."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cases = []

def family(name, policy, options, decode, rules, goals, vocabulary, examples):
    for index, (description, facts, expected) in enumerate(examples, 1):
        # Rotate options deterministically so the same answer is not always first.
        offset = (index - 1) % len(options)
        labels = options[offset:] + options[:offset]
        cases.append(dict(id=f"{name}-{index:02}", family=name, text=policy + "\nRecord: " + description,
                          labels=labels, gold=expected, goals=goals, decode=decode,
                          rules=rules, vocabulary=vocabulary, facts=facts,
                          knowledge="\n".join(rules + [atom + "." for atom in facts])))

family("release",
    "An assistant claims all tests passed for run A. Decide whether this claim needs revision. "
    "Use only trusted records for that run. Static checks alone support REVISE. A full passing run supports CONTINUE with other checks. "
    "If both are recorded choose CONFLICT. If neither is recorded choose UNKNOWN. A requested, quoted or planned test is not a completed run.",
    ["REVISE","CONTINUE","UNKNOWN","CONFLICT"], {"10":"REVISE","01":"CONTINUE","00":"UNKNOWN","11":"CONFLICT"},
    ["static_only(dummy).","full_pass(dummy).","revise(X) :- static_only(X).","continue_checks(X) :- full_pass(X)."],
    ["revise(a)","continue_checks(a)"], ["static_only(a)","full_pass(a)","static_only(b)","full_pass(b)"], [
    ("A's signed log records static checks only.",["static_only(a)"],"REVISE"),
    ("The full suite passed on A. The static-only log belongs to B.",["full_pass(a)","static_only(b)"],"CONTINUE"),
    ("B passed the full suite. A's log has not arrived.",["full_pass(b)"],"UNKNOWN"),
    ("Two trusted records for A disagree: one says static checks only, the other says the full suite passed.",["static_only(a)","full_pass(a)"],"CONFLICT"),
    ("The ticket for A asks for 'all tests passed' in the final report. B ran static checks only.",["static_only(b)"],"UNKNOWN"),
    ("A stopped after the static checks. B, on a different revision, passed all tests.",["static_only(a)","full_pass(b)"],"REVISE"),
    ("A's full run passed; a note about doing only static checks next time is a proposal.",["full_pass(a)"],"CONTINUE"),
    ("For the same A, the build log records a full pass while the signed operator record says no tests beyond static checks were run.",["full_pass(a)","static_only(a)"],"CONFLICT")])

family("animal",
    "Decide the recorded fur status of Pip. A lynx is a mammal, and every mammal has fur. A written bare-skin finding supports no fur. "
    "Use only the stated rules and observations. Choose FUR or BARE if exactly that conclusion is supported, UNKNOWN if neither, CONFLICT if both.",
    ["FUR","BARE","UNKNOWN","CONFLICT"], {"10":"FUR","01":"BARE","00":"UNKNOWN","11":"CONFLICT"},
    ["lynx(dummy).","mammal(dummy).","bare_skin(dummy).","mammal(X) :- lynx(X).","fur(X) :- mammal(X).","bare(X) :- bare_skin(X)."],
    ["fur(pip)","bare(pip)"],[f"{p}({x})" for p in ("lynx","mammal","bare_skin") for x in ("pip","max")], [
    ("Pip is a lynx.",["lynx(pip)"],"FUR"),("Pip's skin is recorded as bare. Max is a lynx.",["bare_skin(pip)","lynx(max)"],"BARE"),
    ("Pip is an eagle. Max is a mammal.",["mammal(max)"],"UNKNOWN"),
    ("Pip is classified as a mammal and has a separate bare-skin finding.",["mammal(pip)","bare_skin(pip)"],"CONFLICT"),
    ("The card labels Max, not Pip, as a lynx. Pip has no classification on file.",["lynx(max)"],"UNKNOWN"),
    ("Max has bare skin; Pip is classified as a mammal.",["bare_skin(max)","mammal(pip)"],"FUR")])

family("roles",
    "Decide whether Ada may borrow the archive atlas. Archivists may borrow it; leads inherit archivist privileges. "
    "A direct atlas grant also suffices. Treat this register as complete. Return YES if a permission follows and NO otherwise.",
    ["YES","NO"],{"1":"YES","0":"NO"},
    ["lead(dummy).","archivist(dummy).","grant_atlas(dummy).","archivist(X) :- lead(X).","borrow(X) :- archivist(X).","borrow(X) :- grant_atlas(X)."],
    ["borrow(ada)"], [f"{p}({x})" for p in ("lead","archivist","grant_atlas") for x in ("ada","ben")], [
    ("Ada is lead; Ben holds a direct atlas grant.",["lead(ada)","grant_atlas(ben)"],"YES"),
    ("Ben is lead. Ada has only a visitor badge.",["lead(ben)"],"NO"),
    ("Ada is a visitor with an explicit grant to borrow the atlas.",["grant_atlas(ada)"],"YES"),
    ("Ben is archivist and has the direct grant. Ada has applied to be lead next year.",["archivist(ben)","grant_atlas(ben)"],"NO"),
    ("Ada is the archivist; Ben is lead.",["archivist(ada)","lead(ben)"],"YES"),
    ("Ada was invited to request the atlas. Ben received the only direct grant.",["grant_atlas(ben)"],"NO")])

if __name__ == "__main__":
    (ROOT / "cases.json").write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8", newline="\r\n")
