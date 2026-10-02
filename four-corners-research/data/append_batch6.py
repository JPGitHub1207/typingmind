#!/usr/bin/env python3
"""Append batch 6 higher-education rows and one discovered marketing course."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V = "2026-10-02"
NP = "NOT PUBLISHED"

ORG_FIELDS = list(csv.DictReader((ROOT / "education_training_provider_universe.csv").open()).fieldnames)
PROD_FIELDS = list(csv.DictReader((ROOT / "education_training_products.csv").open()).fieldnames)
SRC_FIELDS = list(csv.DictReader((ROOT / "education_training_sources.csv").open()).fieldnames)
next_id = len(list(csv.DictReader((ROOT / "education_training_sources.csv").open()))) + 1


def org(**kwargs):
    row = {k: NP for k in ORG_FIELDS}
    row["last_verified_date"] = V
    row.update(kwargs)
    return row


def prod(**kwargs):
    row = {k: NP for k in PROD_FIELDS}
    row["verified_date"] = V
    row["source_publication_or_update_date"] = NP
    row.update(kwargs)
    return row


sources = []


def src(org_name, product, url, stype, what, current="current", notes=""):
    global next_id
    sources.append(
        {
            "source_id": f"S{next_id:03d}",
            "organisation_name": org_name,
            "product_name": product,
            "url": url,
            "source_type": stype,
            "publication_or_update_date": NP,
            "verified_date": V,
            "what_it_evidences": what,
            "current_or_archived": current,
            "notes": notes,
        }
    )
    next_id += 1


J = "J Higher education professional development"
A = "A Marketing and admissions"
E = "E AI digital EdTech CRM"

orgs = [
    org(
        organisation_name="Advance HE",
        website="https://www.advance-he.ac.uk/",
        legal_company_name_if_found="ADVANCE HE",
        company_number_if_found="04931031",
        organisation_type="charity",
        primary_markets="Higher education providers and their staff applying for fellowship",
        education_segments="Universities",
        headquarters_or_country="York Science Park, Innovation Way, York YO10 5BR",
        estimated_model="qualification delivery",
        core_positioning="Fellowship applications are priced by category and by whether the person is at a member institution. Institutional membership itself was not given a public subscription price on the FAQ.",
        strapline_or_headline="Fellowship fees from no cost, for accredited member-institution staff, up to £1,130 for a direct Principal Fellow application.",
        repeated_buzzwords="fellowship; accredited provision; member institution",
        named_partners=NP,
        named_clients=NP,
        free_offers="Accredited provision is no cost for an individual from a member institution.",
        newsletter_or_community="My Advance HE account",
        companies_house_notes="Charitable company 04931031, charity 1101607. Active. Previous name The Higher Education Academy until 26 March 2018. Registered office York Science Park. VAT on fellowship fees is not stated. Membership subscription price NOT PUBLISHED.",
    ),
    org(
        organisation_name="Jisc",
        website="https://www.jisc.ac.uk/",
        legal_company_name_if_found="Jisc",
        company_number_if_found="05747339",
        organisation_type="charity",
        primary_markets="UK further and higher education members, plus non-member organisations that can buy some modules",
        education_segments="FE colleges; universities; specialist colleges. One module page also names multi-academy trusts, schools and independent higher education as non-member buyers.",
        headquarters_or_country="4 Portwall Lane, Bristol BS1 6NB",
        estimated_model="membership",
        core_positioning="Membership body for digital services. Training is listed as an optional extra. One AI module publishes a non-member price. A general current training price list was not confirmed.",
        strapline_or_headline="Digital training is an optional extra to membership. One AI module is included for members and £50 plus VAT for eligible non-members.",
        repeated_buzzwords="membership; digital capability; optional extra",
        named_partners="Jisc Services Limited 02881024 is a wholly owned subsidiary, stated on the company page.",
        named_clients=NP,
        free_offers="Some modules are described as free to members. A public free trial is mentioned for reviewing a downloadable module.",
        newsletter_or_community=NP,
        companies_house_notes="Company number 05747339, charity 1149740 and Scotland SC053607, VAT GB 197 0632 86, printed on the Jisc company page. A 2023 module price list was not used.",
    ),
    org(
        organisation_name="Independent Schools Association",
        website="https://www.isaschools.org.uk/",
        legal_company_name_if_found="THE INDEPENDENT SCHOOLS ASSOCIATION",
        company_number_if_found="00045867",
        organisation_type="membership body",
        primary_markets="Independent schools, via short online courses for leaders and marketing staff",
        education_segments="Independent schools",
        headquarters_or_country="ISA House, Great Chesterford Court, Great Chesterford, Saffron Walden CB10 1PF",
        estimated_model="productised training",
        core_positioning="Membership association. A live October 2026 marketing course is priced for members and non-members. A June 2026 marketing course is closed.",
        strapline_or_headline="Online marketing course on 13 October 2026 at £140 for members and £170 for non-members.",
        repeated_buzzwords="ROI; enquiries; independent schools",
        named_partners="Rachel Hadley-Leonard of RHL Consulting is the named trainer and also teaches on the AMCIS diploma.",
        named_clients=NP,
        free_offers=NP,
        newsletter_or_community=NP,
        companies_house_notes="Active company limited by guarantee 00045867, incorporated 6 November 1895, charity 1158943. Registered office Great Chesterford. The course page does not print the number. Discovered from a current events page, not from the original seed list.",
    ),
]

products = [
    prod(
        organisation_name="Advance HE",
        product_name="Fellowship direct and accredited applications",
        product_category=J,
        target_buyer="Higher education staff seeking Associate, Fellow, Senior or Principal Fellowship",
        target_sector="Higher education",
        problem_solved="Professional recognition against the fellowship descriptors",
        format="Application and peer review, or an institution's accredited scheme",
        price_ex_vat="Associate Fellow: accredited member institution no cost; accredited non-member £155; direct member £155; direct non-member £310. Fellow: no cost; £225; £225; £450. Senior Fellow: no cost; £335; £335; £670. Principal Fellow: no cost; £565; £565; £1,130. VAT status NOT PUBLISHED. Fees subject to annual review.",
        membership_price="Institutional membership subscription NOT PUBLISHED. Member-institution employees pay the subsidised column.",
        what_is_included="One resubmission within four weeks if referred, without a further fee. A later new application pays a full fee. Payment is due on submission unless a voucher code is used.",
        tangible_outputs="Fellowship award, or a referred outcome with feedback",
        assessment_or_certificate="Peer review. Outcomes are award or refer.",
        source_url="https://www.advance-he.ac.uk/fellowship/frequently-asked-questions",
        evidence_notes="Four categories are one fee table, so they are one product family with the prices in the price field. Consultancy and event discounts for members were not priced.",
        analysis_likely_strategic_purpose="qualification",
        analysis_likely_cost_to_serve="medium",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="A higher fellowship category, or institutional accreditation",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="Recognition can be free inside a membership and several hundred pounds outside it.",
    ),
    prod(
        organisation_name="Jisc",
        product_name="Ethical and responsible AI in education module",
        product_category=E,
        target_buyer="Staff at Jisc member colleges and universities, and eligible non-members including trusts and schools",
        target_sector="Further and higher education, with non-member schools and trusts named",
        problem_solved="A short self-paced module on benefits and risks of AI in education",
        format="Self-paced digital learning module",
        live_or_on_demand="On demand",
        duration="One hour. Beginner level.",
        learner_total_hours_if_published="One hour",
        price_ex_vat="Jisc members: inclusive to membership. Non-member not-for-profit and international academic institutions: £50 + VAT.",
        what_is_included="The module. Download and host on a VLE is offered, with pricing on a separate modules page that was not opened. A trial for review is mentioned.",
        tangible_outputs=NP,
        assessment_or_certificate=NP,
        source_url="https://www.jisc.ac.uk/training/ethical-and-responsible-ai-in-education",
        evidence_notes="Direct page fetch was blocked. The price, one-hour length and member rule are from the public page text returned in search. Listed dates 1 March 2026 and 1 April 2026 had passed by 2 October 2026. A later open date was not confirmed. The higher-education catalogue lists training as an optional extra and does not publish a general tariff.",
        analysis_likely_strategic_purpose="lead gen",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="Membership, a VLE licence, or other paid training",
        analysis_similarity_to_four_corners="medium",
        analysis_what_four_corners_can_learn="A one-hour AI module can be free to members and £50 plus VAT to everyone else, which is far below a half-day school AI workshop.",
    ),
    prod(
        organisation_name="Independent Schools Association",
        product_name="Marketing Works",
        product_category=A,
        target_buyer="Heads, deputies and people responsible for marketing in independent schools",
        target_sector="Independent schools",
        problem_solved="Choosing marketing activity that has a return in enquiries, conversions or brand visibility",
        format="Online course",
        live_or_on_demand="Live online",
        duration="13 October 2026, 9.30am to 3pm",
        expert_live_hours_if_published="9.30am to 3pm, including breaks. A net teaching-hour figure is NOT PUBLISHED.",
        cohort_length="One day",
        price_ex_vat="ISA member £140; non-member £170. VAT status NOT PUBLISHED.",
        what_is_included="Case studies, ROI discussion and practical ideas. A template pack or written report is not described. Trainer is Rachel Hadley-Leonard.",
        tangible_outputs="Ideas the delegate can adapt. No toolkit is listed.",
        report_included="No",
        source_url="https://www.isaschools.org.uk/event-calendar/marketing-works-case-studies-and-ideas-that-have-a-return-on-investment-10-26.html",
        evidence_notes="Bookings were open on 2 October 2026. A 4 June 2026 ISA marketing and admissions course at £130 and £160 was closed and is not this product.",
        analysis_likely_strategic_purpose="low-risk entry",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="medium",
        analysis_likely_route_to_next_sale="The trainer's consultancy, RHL Consulting, is described in the biography and is not a priced ISA product.",
        analysis_similarity_to_four_corners="high",
        analysis_what_four_corners_can_learn="A one-day independent-school marketing course with open bookings is £140 to £170, with VAT unstated, and does not include an implementation clinic.",
    ),
]

src("Advance HE", "Fellowship direct and accredited applications", "https://www.advance-he.ac.uk/fellowship/frequently-asked-questions", "official_site", "Fellowship fee table")
src("Advance HE", "Organisation", "https://find-and-update.company-information.service.gov.uk/company/04931031", "companies_house", "ADVANCE HE 04931031")
src("Advance HE", "Organisation", "https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/charity-details/4004291/full-print", "regulator", "Charity 1101607")
src("Jisc", "Ethical and responsible AI in education module", "https://www.jisc.ac.uk/training/ethical-and-responsible-ai-in-education", "official_site", "Member inclusive; non-member £50 + VAT; one hour", notes="Direct fetch blocked. Text taken from the public page extract. Listed 2026 dates had passed.")
src("Jisc", "Organisation", "https://www.jisc.ac.uk/about-us/company-and-charity-details", "official_site", "Company 05747339, charities and Bristol office")
src("Jisc", "Organisation", "https://beta.jisc.ac.uk/membership/our-catalogue-of-services-for-higher-education", "official_site", "Training listed as an optional extra. No general price.")
src("Independent Schools Association", "Marketing Works", "https://www.isaschools.org.uk/event-calendar/marketing-works-case-studies-and-ideas-that-have-a-return-on-investment-10-26.html", "official_site", "£140 and £170 on 13 October 2026")
src("Independent Schools Association", "Organisation", "https://find-and-update.company-information.service.gov.uk/company/00045867", "companies_house", "THE INDEPENDENT SCHOOLS ASSOCIATION")


def main():
    with (ROOT / "education_training_provider_universe.csv").open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=ORG_FIELDS, quoting=csv.QUOTE_MINIMAL).writerows(orgs)
    with (ROOT / "education_training_products.csv").open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=PROD_FIELDS, quoting=csv.QUOTE_MINIMAL).writerows(products)
    with (ROOT / "education_training_sources.csv").open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=SRC_FIELDS, quoting=csv.QUOTE_MINIMAL).writerows(sources)
    print(f"added orgs={len(orgs)} products={len(products)} sources={len(sources)}")


if __name__ == "__main__":
    main()
