#!/usr/bin/env python3
"""Append batch 5 safeguarding and SEND catalogue rows."""

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


F = "F Safeguarding governance legal HR"
G = "G SEND inclusion mental health"

orgs = [
    org(
        organisation_name="EduCare",
        website="https://www.educare.co.uk/",
        legal_company_name_if_found=NP,
        company_number_if_found=NP,
        organisation_type="publisher or platform",
        primary_markets="Schools and academy trusts buying an annual safeguarding e-learning licence",
        education_segments="Schools; multi-academy trusts",
        headquarters_or_country="UK. Sales phone 01926 436211. A company number is not printed on the pricing page.",
        estimated_model="platform subscription",
        core_positioning="Annual online safeguarding licence priced from pupil roll, with unlimited staff users and a large course library treated here as one commercial model.",
        strapline_or_headline="Online learning service from £410 for a school of up to 50 pupils.",
        repeated_buzzwords="safeguarding; duty of care; KCSIE; pupil roll; unlimited access",
        named_partners="YoungMinds and The Children's Society are named as course partners.",
        named_clients="Equals Trust is named in a savings claim. A head of education at West Midlands Ambulance Service is quoted.",
        free_offers="Quote form. A free trial is NOT PUBLISHED.",
        newsletter_or_community=NP,
        companies_house_notes="Unresolved. EDUCARE LEARNING LTD 01741045, Sheffield, is a name match only. The sales page does not print a number, and that registered office was not matched to the 01926 phone. A Tes brand relationship was not restated on the page reviewed.",
    ),
    org(
        organisation_name="High Speed Training",
        website="https://www.highspeedtraining.co.uk/",
        legal_company_name_if_found=NP,
        company_number_if_found=NP,
        organisation_type="commercial training company",
        primary_markets="Individual learners and school teams buying single online courses",
        education_segments="Early years; schools; FE colleges",
        headquarters_or_country="Riverside Business Park, Dansk Way, Ilkley, West Yorkshire LS29 8JZ",
        estimated_model="productised training",
        core_positioning="Per-learner online catalogue. Education safeguarding prices cluster between £20 and £65 plus VAT. Bulk discounts apply across the catalogue. The long tail is not rowed course by course.",
        strapline_or_headline="Online safeguarding courses updated for KCSIE 2026 and Working Together 2026, sold per learner.",
        repeated_buzzwords="City and Guilds; CPD; KCSIE; certificate; bulk discount",
        named_partners="Joanna Nicolas is named as a safeguarding author on the education course.",
        named_clients=NP,
        free_offers="Management Suite is included when buying for a team. Free training on how to use that suite is offered by email.",
        newsletter_or_community=NP,
        companies_house_notes="Candidate only: HIGH SPEED TRAINING LIMITED 06428976, Ilkley, active, SIC 82990. The course pages do not print the number or that address, so the number is not recorded in the company-number field.",
    ),
    org(
        organisation_name="NSPCC Learning",
        website="https://learning.nspcc.org.uk/",
        legal_company_name_if_found="THE NATIONAL SOCIETY FOR THE PREVENTION OF CRUELTY TO CHILDREN",
        company_number_if_found=NP,
        organisation_type="charity",
        primary_markets="Schools, academies and colleges buying safeguarding e-learning",
        education_segments="Schools; FE colleges",
        headquarters_or_country="UK. Learning phone 0116 234 7246.",
        estimated_model="productised training",
        core_positioning="Charity e-learning sold per person. Two education courses are recorded. Other role-specific modules are noted as a commoditised tail. Consultancy is offered and not priced.",
        strapline_or_headline="Safeguarding e-learning for schools at £35, with a £25 refresher.",
        repeated_buzzwords="elearning; certificate; safeguarding; schools",
        named_partners=NP,
        named_clients=NP,
        free_offers="Consultancy price is NOT PUBLISHED. A free course was not on the two pages reviewed.",
        newsletter_or_community=NP,
        companies_house_notes="Charity 216401, website nspcc.org.uk on the Charity Commission-derived record. A company number was not recorded. Learning sits on learning.nspcc.org.uk.",
    ),
    org(
        organisation_name="nasen",
        website="https://nasen.org.uk/",
        legal_company_name_if_found="THE NATIONAL ASSOCIATION FOR SPECIAL EDUCATIONAL NEEDS (NASEN)",
        company_number_if_found="02674379",
        organisation_type="charity",
        primary_markets="Schools, trusts, early years and specialist settings, and individual practitioners",
        education_segments="Early years; schools; multi-academy trusts; specialist settings",
        headquarters_or_country="nasen House, 4/5 Amber Business Village, Amber Close, Amington, Tamworth B77 4RP. Whole School SEND: Fox Court, 14 Gray's Inn Road, London WC1X 8HN.",
        estimated_model="membership",
        core_positioning="Free core membership, a low annual Plus tier, an organisational academy from a published floor, and one priced practitioner programme. Whole School SEND is the programme brand at the London address.",
        strapline_or_headline="Free core membership, Plus at £19.99 a year, and nasen Academy from £375 plus VAT.",
        repeated_buzzwords="SEND; inclusion; academy; membership",
        named_partners="Whole School SEND",
        named_clients=NP,
        free_offers="Core membership is free.",
        newsletter_or_community="nasen Connect is listed as a Plus benefit.",
        companies_house_notes="Charity 1007023. Charity Commission record gives company number 02674379 and working name NASEN. Registered-office match to Tamworth was not re-checked on the Companies House overview in this pass.",
    ),
    org(
        organisation_name="Autism Education Trust",
        website="https://www.autismeducationtrust.org.uk/",
        legal_company_name_if_found=NP,
        company_number_if_found=NP,
        organisation_type="charity",
        primary_markets="Local authorities, schools, trusts and training partners that license autism education training",
        education_segments="Early years; schools; post-16; local-authority education teams; multi-academy trusts",
        headquarters_or_country="UK. Address NOT PUBLISHED on the partner pages reviewed.",
        estimated_model="blended training and consultancy",
        core_positioning="Licensor. Partners pay a licence and may charge settings. A national delegate price is not published. The public site also uses the Neuroinclusive Education Network name.",
        strapline_or_headline="Autism training delivered by licensed partners. Licence fees are not published.",
        repeated_buzzwords="licence; training partner; professional development programme; local authority",
        named_partners="More than 110 training partners are claimed on the training page.",
        named_clients=NP,
        free_offers="Find a local partner. A free national course is NOT PUBLISHED.",
        newsletter_or_community=NP,
        companies_house_notes="Unresolved. The Autism Trust Limited, charity 1117657, company 05965790, was rejected as a namesake. Partner pages do not print a company number.",
    ),
]

products = [
    prod(
        organisation_name="EduCare",
        product_name="Online learning service for schools",
        product_category=F,
        target_buyer="Schools and academy trusts",
        target_sector="Schools",
        problem_solved="Staff safeguarding and duty-of-care training, with reporting for inspectors",
        format="Annual online licence",
        live_or_on_demand="On demand",
        duration="Annual licence. Individual course hours are not listed on the pricing page.",
        price_ex_vat="Prices start from £410 for a school of up to 50 pupils. VAT status NOT PUBLISHED. The fee uses pupil roll. Quote for other sizes.",
        membership_price="From £410 for up to 50 pupils, annual",
        what_is_included="More than 40 safeguarding and duty-of-care courses; unlimited access for teachers, support staff, volunteers and governors; updates when guidance such as KCSIE changes; reporting suite; dedicated support. The module list is commoditised and is not rowed separately.",
        tangible_outputs="Reporting suite for learner progress",
        report_included="Yes, as a reporting suite. A bespoke consultancy report is not described.",
        software_or_platform_access="Yes",
        source_url="https://www.educare.co.uk/save-money-with-educare",
        evidence_notes="Less than £2 per learner per course, and a 90 percent renewal claim, are marketing claims. A second example price seen in earlier search was not re-opened and is not used.",
        analysis_likely_strategic_purpose="compliance",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="Renewal, or a larger quote as pupil numbers rise",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="Compliance e-learning is an annual licence from a few hundred pounds, not a workshop fee.",
    ),
    prod(
        organisation_name="High Speed Training",
        product_name="Education safeguarding catalogue",
        product_category=F,
        target_buyer="Individuals and school teams buying one place per learner",
        target_sector="Early years, schools and colleges",
        problem_solved="Short online safeguarding certificates aligned to KCSIE",
        format="On-demand course, one learner per purchase",
        live_or_on_demand="On demand",
        duration="Safeguarding Children in Education is 2 to 3 hours. Other course lengths were not all opened.",
        expert_live_hours_if_published="None. Online only.",
        learner_total_hours_if_published="2 to 3 hours for Safeguarding Children in Education",
        price_ex_vat="On the KCSIE 2026 page: introduction level 1 £31 + VAT; advanced level 2 £40 + VAT; designated safeguarding lead level 3 £65 + VAT; safeguarding children in education £31 + VAT; Prevent £20 + VAT; safeguarding for governors £31 + VAT; harmful sexual behaviour in schools £25 + VAT; safeguarding essentials level 1 £35 + VAT; safer recruitment in education £31 + VAT; safer recruitment £31 + VAT. Courses listed without a figure on that page are NOT PUBLISHED.",
        group_price="10 or more courses 10 percent off; 50 or more 20 percent; 100 or more 30 percent; 500 or more 40 percent. Mix and match. Invoice for 5 or more courses, 30-day terms.",
        what_is_included="For the education course: six modules; optional early years section; 20-question assessment at 80 percent with free retakes; digital certificate the same day; printed certificate posted; 2 CPD points; City and Guilds Assured; access after completion; management suite for team buyers. Recommended renewal 3 years, though the certificate has no expiry date. Last audited 30 September 2026. Other catalogue modules are commoditised.",
        tangible_outputs="Certificate and, for teams, a management-suite record",
        report_included="Team progress via the management suite. A consultancy report is not included.",
        assessment_or_certificate="Yes",
        software_or_platform_access="Management suite for team orders",
        source_url="https://www.highspeedtraining.co.uk/campaign/kcsie/",
        evidence_notes="The education course page confirms 2 to 3 hours, the audit date, CPD points and the bulk ladder. Its £31 + VAT also appears on the KCSIE campaign page.",
        analysis_likely_strategic_purpose="compliance",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="More seats, a higher-level course, or the INSET pack. The INSET pack price was not published on the campaign page.",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="Commodity safeguarding sits at £20 to £65 plus VAT per person, with automatic bulk discounts.",
    ),
    prod(
        organisation_name="NSPCC Learning",
        product_name="Safeguarding training for schools, academies and colleges",
        product_category=F,
        target_buyer="Staff and volunteers who need a full introduction",
        target_sector="Schools, academies and colleges",
        problem_solved="Introductory child protection knowledge for education settings",
        format="E-learning",
        live_or_on_demand="On demand",
        duration="3 hours. Five modules of about 30 to 45 minutes.",
        learner_total_hours_if_published="3 hours",
        price_ex_vat="£35 per person. VAT status NOT PUBLISHED.",
        what_is_included="Branching primary, secondary and college scenarios; quizzes; certificate; repeat access for one year; completion reports for team buyers. Last updated April 2024. Role-specific courses for governors, designated leads and SEND are signposted and not separately priced here.",
        tangible_outputs="Downloadable certificate and team completion reports",
        report_included="Completion reports for licence buyers",
        assessment_or_certificate="Yes. Certificate of achievement.",
        software_or_platform_access="Hosted on NSPCC Learning, or on a customer's LMS by enquiry",
        source_url="https://learning.nspcc.org.uk/training/child-protection-schools",
        evidence_notes="Volume discounts were not on this page. The refresher page does publish a volume table.",
        analysis_likely_strategic_purpose="compliance",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="Refresher, role-specific modules, or consultancy",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="A charity's three-hour school course is £35 per person, close to the commercial catalogue floor.",
    ),
    prod(
        organisation_name="NSPCC Learning",
        product_name="Safeguarding refresher for schools",
        product_category=F,
        target_buyer="Staff who have already completed a full school safeguarding course",
        target_sector="Schools, academies and colleges",
        problem_solved="Annual refresh of safeguarding knowledge",
        format="E-learning",
        live_or_on_demand="On demand",
        duration="90 minutes",
        learner_total_hours_if_published="90 minutes",
        price_ex_vat="£25 per person for 1 to 9 places. VAT status NOT PUBLISHED.",
        group_price="10 to 49 places £22.50; 50 to 99 £21.25; 100 to 999 £20. Per person. VAT status NOT PUBLISHED.",
        what_is_included="Short refresh of roles, abuse indicators, reporting and recording; certificate; signposted resources",
        tangible_outputs="Certificate",
        assessment_or_certificate="Yes",
        source_url="https://learning.nspcc.org.uk/training/refresher-safeguarding-in-education",
        analysis_likely_strategic_purpose="retention",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="Full course for new staff, or other role courses",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="A refresher is priced below the full course and has a published volume ladder down to £20.",
    ),
    prod(
        organisation_name="nasen",
        product_name="Core and Plus membership",
        product_category=G,
        target_buyer="Individuals working with children and young people with SEND",
        target_sector="Schools and other education settings",
        problem_solved="Entry to nasen resources, with a paid tier for extra content and one academy course",
        format="Membership",
        duration="Plus is per year. Core term length is NOT PUBLISHED on this page.",
        price_ex_vat="Core free. Plus £19.99 per year. VAT status NOT PUBLISHED.",
        membership_price="£19.99 per year for Plus",
        free_trial_or_free_entry="Core membership is free",
        what_is_included="Plus upgrade list includes a nasen Academy licence, a nasen Academy course, welcome pack, policy updates, e-badge, member blogs, nasen Connect and pre-sale event access",
        tangible_outputs="Member resources and one academy course on Plus",
        software_or_platform_access="nasen Academy access on Plus",
        community_access="Yes",
        next_obvious_paid_step="Organisational nasen Academy or the recognised practitioner programme",
        source_url="https://nasen.org.uk/why-join",
        analysis_likely_strategic_purpose="lead gen",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="Academy subscription or the £500 programme",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="A free membership with a £19.99 upsell is the front of a SEND catalogue.",
    ),
    prod(
        organisation_name="nasen",
        product_name="nasen Academy organisation licence",
        product_category=G,
        target_buyer="Schools, trusts, early years and specialist settings",
        target_sector="Schools and trusts",
        problem_solved="Whole-staff SEND e-learning and completion tracking",
        format="Annual platform licence",
        live_or_on_demand="On demand",
        price_ex_vat="Plans start from £375 + VAT per year. Higher tiers and MAT-wide prices are on request.",
        membership_price="From £375 + VAT per year",
        what_is_included="On-demand modules; engagement dashboard; induction and progression tracking. The module list is commoditised.",
        tangible_outputs="Dashboard of completion and engagement",
        report_included="Dashboard reporting. A written consultancy report is not described.",
        software_or_platform_access="Yes",
        source_url="https://www.wholeschoolsend.org.uk/page/nasen-academy-form",
        evidence_notes="Larger-team prices were not published.",
        analysis_likely_strategic_purpose="recurring revenue",
        analysis_likely_cost_to_serve="low",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="A larger tier, or the recognised programme for individuals",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="Specialist SEND e-learning for an organisation starts at £375 plus VAT a year.",
    ),
    prod(
        organisation_name="nasen",
        product_name="Recognised Teacher or Practitioner of SEND",
        product_category=G,
        target_buyer="Teachers and practitioners who want a nasen recognition",
        target_sector="Schools and other settings",
        problem_solved="A structured SEND programme ending in a professional artefact",
        format="On-demand modules plus required live sessions",
        live_or_on_demand="Both",
        duration="12 months' access",
        expert_live_hours_if_published="Two live sessions are required for the certificate. Length of each session is NOT PUBLISHED.",
        price_ex_vat="£500. VAT status NOT PUBLISHED.",
        what_is_included="Three modules; guided reflection; a professional artefact such as an intervention, assessment tool, lesson-plan template or learning resource; extra introductory webcasts; teacher and practitioner routes use different session series. Bulk price on request.",
        tangible_outputs="Professional artefact and a certificate if both live sessions are attended",
        toolkit_or_templates="The participant builds an artefact. A finished template pack is not the product.",
        assessment_or_certificate="Certificate requires attendance at both live sessions",
        implementation_support="Live tutorials on the artefact. Not done-for-you.",
        done_for_you_element="No",
        source_url="https://www.wholeschoolsend.org.uk/page/nasen-recognised-teacherpractitioner-send-programme",
        evidence_notes="Teacher and practitioner purchases are separate checkout links at the same published £500.",
        analysis_likely_strategic_purpose="capability building",
        analysis_likely_cost_to_serve="medium",
        analysis_likely_scalability="medium",
        analysis_likely_route_to_next_sale="Organisation academy licence",
        analysis_similarity_to_four_corners="medium",
        analysis_what_four_corners_can_learn="A year of blended SEND learning with a tangible artefact is £500, with VAT unstated.",
    ),
    prod(
        organisation_name="Autism Education Trust",
        product_name="Licensed professional development programme",
        product_category=G,
        target_buyer="Local authorities, schools, trusts and training organisations that want to deliver the programme",
        target_sector="Education settings for ages 0 to 25",
        problem_solved="A licensed autism education programme and frameworks, delivered locally",
        format="Licence, then face-to-face or virtual delivery by a partner",
        live_or_on_demand="Partner delivery. National on-demand price NOT PUBLISHED.",
        price_ex_vat=NP,
        what_is_included="Partners receive training materials, an autism competency framework, autism standards and practical resources, and the right to deliver in a local area. They pay a licence and may charge delegates or settings. Licence fee and delegate fees are NOT PUBLISHED. Strategic local-authority support is a further enquiry.",
        tangible_outputs="Frameworks and standards for partners. A delegate certificate is described as CPD certified. A national price for that certificate is NOT PUBLISHED.",
        toolkit_or_templates="Yes, for licensed partners",
        source_url="https://www.autismeducationtrust.org.uk/become-aet-partner-educational-setting-not-profit-or-private-training-partner",
        evidence_notes="Do not use a partner's local price as the national fee. The public training page says more than 110 partners deliver the programme and tells buyers to contact a local partner.",
        analysis_likely_strategic_purpose="scalable IP",
        analysis_likely_cost_to_serve="medium",
        analysis_likely_scalability="high",
        analysis_likely_route_to_next_sale="Strategic support for a local authority, price NOT PUBLISHED",
        analysis_similarity_to_four_corners="low",
        analysis_what_four_corners_can_learn="A national programme can have no public price because partners set the delegate fee.",
    ),
]

src("EduCare", "Online learning service for schools", "https://www.educare.co.uk/save-money-with-educare", "official_site", "From £410 for up to 50 pupils and 40-plus courses")
src("High Speed Training", "Education safeguarding catalogue", "https://www.highspeedtraining.co.uk/campaign/kcsie/", "official_site", "KCSIE 2026 course price ladder")
src("High Speed Training", "Education safeguarding catalogue", "https://www.highspeedtraining.co.uk/courses/safeguarding/safeguarding-children-education/", "official_site", "2 to 3 hours, audit date, bulk discounts")
src("High Speed Training", "Organisation", "https://find-and-update.company-information.service.gov.uk/company/06428976", "companies_house", "Candidate HIGH SPEED TRAINING LIMITED. Number not printed on the course site.", notes="Not recorded as a confirmed match.")
src("NSPCC Learning", "Safeguarding training for schools, academies and colleges", "https://learning.nspcc.org.uk/training/child-protection-schools", "official_site", "£35 and 3 hours")
src("NSPCC Learning", "Safeguarding refresher for schools", "https://learning.nspcc.org.uk/training/refresher-safeguarding-in-education", "official_site", "£25 and volume bands")
src("NSPCC Learning", "Organisation", "https://findthatcharity.uk/orgid/GB-CHC-216401", "regulator", "Charity 216401 and nspcc.org.uk", notes="Charity Commission-derived record")
src("nasen", "Core and Plus membership", "https://nasen.org.uk/why-join", "official_site", "Core free and Plus £19.99")
src("nasen", "nasen Academy organisation licence", "https://www.wholeschoolsend.org.uk/page/nasen-academy-form", "official_site", "From £375 + VAT per year")
src("nasen", "Recognised Teacher or Practitioner of SEND", "https://www.wholeschoolsend.org.uk/page/nasen-recognised-teacherpractitioner-send-programme", "official_site", "£500 and 12 months")
src("nasen", "Organisation", "https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/charity-details/1007023/full-print", "regulator", "Charity 1007023 and company 02674379")
src("Autism Education Trust", "Licensed professional development programme", "https://www.autismeducationtrust.org.uk/become-aet-partner-educational-setting-not-profit-or-private-training-partner", "official_site", "Licence model. Fees absent.")
src("Autism Education Trust", "Licensed professional development programme", "https://www.autismeducationtrust.org.uk/expert-led-autism-training", "official_site", "Delivery by local partners")


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
