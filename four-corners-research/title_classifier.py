"""Classify people from job title only. Do not use ChatGPT Audience / Seniority / Moorgate columns."""

from __future__ import annotations

import re

# Kill even if the title also mentions people/HR/learning
KILL_IF = re.compile(
    r"""
    business\s*partner|\bhrbp\b|people\s*partner|
    talent\s*acquisition|talent\s*attraction|recruit(ment|er)|
    reward|compensation|benefits|
    employee\s*relations|\ber\b|
    payroll|pensions?|
    procurement|
    intern(al)?\s*comm|
    diversity|inclusion|\bdei\b|\bedi\b|
    well-?being|wellbeing|
    coordinator|officer(?!\s*officer)|advisor|adviser|specialist|administrator|
    consultant(?!\s*officer)|
    chief\s*financial|group\s*cfo|\bcfo\b|finance\s*director|
    chief\s*executive|\bceo\b|managing\s*director|
    chief\s*operating|\bcoo\b|operations\s*director|
    chief\s*technology|\bcto\b|chief\s*information|\bcio\b|
    chief\s*of\s*staff|co-?founder|
    sustainability\s*officer
    """,
    re.I | re.X,
)

# These "officer" matches would also hit CHRO/CPO — handle C-level people first.

C_PEOPLE = re.compile(
    r"""
    chief\s*people|chief\s*human|\bchro\b|\bcpo\b|
    chief\s*talent|chief\s*learning|\bclo\b|
    evp,?\s*group\s*chief\s*talent
    """,
    re.I | re.X,
)

LND = re.compile(
    r"""
    \bl\s*&\s*d\b|learning\s*&\s*development|learning\s+and\s+development|
    \blearning\b|leadership\s+development|
    \bcapability\b|
    skills,?\s*learning|knowledge\s*&\s*learning|
    apprenticeship
    """,
    re.I | re.X,
)

OD = re.compile(
    r"organisational\s+development|organizational\s+development|\bod\b",
    re.I,
)

TALENT_ACQ = re.compile(
    r"talent\s*acquisition|talent\s*attraction|recruit",
    re.I,
)

TALENT_DEV = re.compile(
    r"""
    talent\s*development|talent\s*&\s*development|talent\s+and\s+development|
    talent\s*management|head\s+of\s+talent(?!\s*acquisition)|
    director\s+of\s+talent(?!\s*acquisition)|
    global\s+head\s+of\s+talent(?!\s*acquisition)|
    people\s*&\s*talent|talent\s*&\s*learning|talent\s+and\s+learning
    """,
    re.I | re.X,
)

HR_DIRECTOR = re.compile(
    r"""
    (head|director|vp|vice\s*president|chief)\b.*\b(hr|human\s*resources|people)\b|
    \b(hr|human\s*resources|people)\s+(director|head)|
    people\s*&\s*culture\s+director|group\s+hr\s+director|
    head\s+of\s+people|head\s+of\s+hr|head\s+of\s+human|
    people\s+director|people\s+&\s+culture
    """,
    re.I | re.X,
)

HR_OPS = re.compile(
    r"people\s*operations|hr\s*operations|hr\s*services|people\s*services|hr\s*systems|hr\s*ops",
    re.I,
)

SENIOR = re.compile(
    r"""
    \bchief\b|\bdirector\b|\bhead\s+of\b|\bhead,\b|
    \bvp\b|vice\s*president|\bevp\b|
    associate\s+director|group\s+head|global\s+head|
    senior\s+director
    """,
    re.I | re.X,
)

MID = re.compile(
    r"\bmanager\b|\blead\b|\bpartner\b|\bsenior\s+(hr|human|people|learning|talent)",
    re.I,
)

FALSE_LEARNING = re.compile(
    r"machine\s*learning|deep\s*learning|e-?learning\s*product|product\s+learning",
    re.I,
)

FALSE_OD = re.compile(
    r"product\s+officer|head\s+of\s+.*product|commodities|payments?\s*&\s*fx",
    re.I,
)


def _norm(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").replace("\u00a0", " ")).strip()


def classify_title(position: str) -> dict:
    p = _norm(position)
    low = p.lower()

    function = "not_people"
    keep = "kill"
    priority = ""
    seniority = "unknown"
    reason = ""

    if not p:
        return dict(
            function="empty",
            seniority="unknown",
            keep="kill",
            priority="",
            reason="no_title",
        )

    # Seniority from tokens
    if SENIOR.search(p):
        seniority = "senior_leader"
    elif MID.search(p):
        seniority = "mid"
    else:
        seniority = "other"

    # Function
    if FALSE_LEARNING.search(p):
        function = "not_people"
        keep = "kill"
        reason = "not_lnd_false_positive"
    elif TALENT_ACQ.search(p) and not re.search(r"development|learning", low):
        function = "talent_acquisition"
        keep = "kill"
        reason = "recruitment_not_buyer"
    elif (OD.search(p) and not FALSE_OD.search(p)) and (
        "development" in low or re.search(r"\bod\b", low)
    ):
        function = "OD"
    elif LND.search(p) and not FALSE_LEARNING.search(p):
        function = "L&D"
    elif TALENT_DEV.search(p):
        function = "talent_development"
    elif C_PEOPLE.search(p) or HR_DIRECTOR.search(p):
        if HR_OPS.search(p) and not re.search(r"learning|talent development|od\b", low):
            function = "HR_ops"
        else:
            function = "HR_people_leader"
    elif re.search(r"\bhr\b|human resources|people", low):
        function = "HR_other"
    else:
        function = "not_people"

    # Kill list (after function, so CPO is not killed as "officer")
    if function == "not_people":
        keep = "kill"
        reason = reason or "not_lnd_hr_talent_od"
    elif function == "talent_acquisition":
        keep = "kill"
        reason = "recruitment_not_buyer"
    elif function == "HR_ops":
        keep = "kill"
        reason = "hr_ops_not_learning_owner"
    elif KILL_IF.search(p) and function not in ("L&D", "OD", "talent_development", "HR_people_leader"):
        keep = "kill"
        reason = "kill_pattern"
        function = function if function != "not_people" else "not_people"
    elif seniority != "senior_leader":
        keep = "kill"
        reason = "not_head_director_chief"
    else:
        # senior + relevant function
        if function in ("L&D", "OD"):
            keep = "keep"
            priority = "P1_L&D_OD"
            reason = "senior_lnd_or_od"
        elif function == "talent_development":
            keep = "keep"
            priority = "P2_talent_dev"
            reason = "senior_talent_development"
        elif function == "HR_people_leader":
            keep = "keep"
            priority = "P3_hr_people"
            reason = "senior_hr_or_people_leader"
        else:
            keep = "kill"
            reason = "senior_but_not_target_function"

    # HRBP / partner always kill even if "Head of HR Business Partnering"
    if re.search(r"business\s*partner|people\s*partner", p, re.I) and function != "L&D":
        if "head of hr business partnering" in low or "head of people partnering" in low:
            keep = "kill"
            priority = ""
            reason = "hrbp_lead_not_learning_owner"
            function = "HRBP"

    if re.search(r"business\s*partner", p, re.I) and seniority != "senior_leader":
        keep = "kill"
        function = "HRBP" if function.startswith("HR") or function == "HR_other" else function
        reason = "hrbp"

    return dict(
        function=function,
        seniority=seniority,
        keep=keep,
        priority=priority,
        reason=reason,
    )
