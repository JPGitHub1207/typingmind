#!/usr/bin/env python3
"""Phase 4 model benchmarks. Not evidence of what education buyers pay."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("batch1", HERE / "build_competitor_batch1.py")
batch1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch1)

NP = batch1.NP
V = "2026-10-05"
M = "Model benchmark"
row = batch1.row


def org(**kw):
    kw.setdefault("competitor_class", M)
    kw.setdefault("direct_adjacent_or_model_benchmark", M)
    kw.setdefault("country", "United Kingdom")
    kw.setdefault("last_verified_date", V)
    kw.setdefault("education_markets", "Not an education specialist. Do not use these prices as education buyer evidence.")
    return row(batch1.ORG_FIELDS, **kw)


def product(**kw):
    kw.setdefault("competitor_class", M)
    kw.setdefault("verified_date", V)
    return row(batch1.PRODUCT_FIELDS, **kw)


ORGS = [
    org(
        organisation_name="Gripped",
        website="https://gripped.io/",
        legal_company_name=NP,
        company_number=NP,
        organisation_type="B2B demand-generation agency",
        primary_market="Series A and B SaaS and tech companies, often £2m to £20m ARR",
        target_customer="B2B SaaS marketing leaders who need pipeline, not an education provider",
        core_positioning="Retainer demand generation. Two official pages publish different floors. Ad spend is extra. Not an education price.",
        homepage_headline="B2B marketing services pricing for SaaS and tech",
        strapline="Transparent pricing that scales with scope.",
        repeated_buzzwords="pipeline; retainer; demand generation; sprint",
        core_services="Paid media; SEO; content; conversion; marketing operations",
        education_services="None published",
        commercial_services="Demand generation for SaaS",
        training_services=NP,
        consultancy="The lowest tier is strategic guidance plus separately priced projects",
        coaching=NP,
        implementation="Channel execution starts at the middle tier",
        managed_service="The top tier is an outsourced marketing team",
        fractional_service="The lowest tier is closer to guidance than to a full department",
        software_platform="Works with the client's HubSpot or Salesforce. Software is not included.",
        named_partners=NP,
        technology_partners=NP,
        named_clients=NP,
        named_education_clients=NP,
        free_offers="30-minute session described as advice with no pitch",
        newsletter=NP,
        community=NP,
        why_relevant_to_four_corners="A published three-tier retainer with ad spend, websites and an onboarding fee kept outside the monthly number. The two pages do not agree on the floor.",
    ),
    org(
        organisation_name="Greenlight Web",
        website="https://www.greenlightweb.co.uk/",
        legal_company_name=NP,
        company_number=NP,
        organisation_type="outsourced marketing department",
        primary_market="B2B, professional services, engineering and manufacturing",
        target_customer="Owner-managed B2B firms that want hours, not a channel menu",
        core_positioning="One monthly fee buys a cap of hours and access to every service. This is not Greenlight Digital, and it is not an education price.",
        homepage_headline="Your outsourced marketing department",
        strapline="Predictable, fixed price monthly marketing.",
        repeated_buzzwords="hours; outsourced marketing department; account manager",
        core_services="Strategy; SEO; content; web; paid media; email; design",
        education_services="None on the pages reviewed",
        commercial_services="Flexible hours across the service list",
        training_services=NP,
        consultancy="Strategy is inside the hours",
        coaching=NP,
        implementation="The team does the work inside the hour cap",
        managed_service="Yes",
        fractional_service=NP,
        software_platform=NP,
        named_partners=NP,
        technology_partners=NP,
        named_clients=NP,
        named_education_clients=NP,
        free_offers=NP,
        newsletter=NP,
        community=NP,
        why_relevant_to_four_corners="The clearest published hour caps near Four Corners' test fees: £2,000 for up to 25 hours, £3,500 for up to 45, £5,000 for up to 75. VAT and the minimum term length are not published. Company number not matched. GREENLIGHT UK LIMITED 03567949 is a different firm.",
    ),
    org(
        organisation_name="Spectra Media",
        website="https://www.spectra.media/",
        legal_company_name=NP,
        company_number=NP,
        organisation_type="outsourced marketing department",
        primary_market="Businesses that want a full marketing team on a retainer",
        target_customer="Established businesses ready for a 12-month plan. Sector is not limited to education.",
        core_positioning="Every tier includes every service. Price rises with pace and automation. A results guarantee sits on a 12-month term.",
        homepage_headline="It's not what it costs. It's what it returns.",
        strapline="Guarantee-backed retainers from £3k a month.",
        repeated_buzzwords="results guarantee; pace; qualified enquiries; 12-month",
        core_services="Strategy; content; social; SEO; design; ads; automation from the middle tier",
        education_services="None published",
        commercial_services="Outsourced marketing department",
        training_services=NP,
        consultancy="Quarterly strategy on the entry tier. Monthly senior strategy from the middle tier.",
        coaching=NP,
        implementation="Delivery is inside the fee",
        managed_service="Yes",
        fractional_service="A lighter in-house support offer exists. Its fee is NOT PUBLISHED.",
        software_platform=NP,
        named_partners=NP,
        technology_partners=NP,
        named_clients=NP,
        named_education_clients=NP,
        free_offers="Free 30-minute call",
        newsletter=NP,
        community=NP,
        why_relevant_to_four_corners="Good/better/best where the menu does not change and the pace does. Not an education price. Hours are not published.",
    ),
    org(
        organisation_name="Digital Litmus",
        website="https://www.digitallitmus.com/",
        legal_company_name=NP,
        company_number=NP,
        organisation_type="B2B growth and RevOps consultancy",
        primary_market="Ambitious B2B companies",
        target_customer="B2B teams that want to buy capacity as points and spend them on marketing or HubSpot",
        core_positioning="Points-based growth programmes, 90-day sprints, and separate HubSpot and RevOps floors. A 2025 pricing PDF. Not an education price.",
        homepage_headline="Pricing guide 2025",
        strapline="Connected sales and marketing.",
        repeated_buzzwords="points; 90 day sprints; HubSpot; RevOps",
        core_services="Growth programmes; websites; HubSpot; RevOps",
        education_services="None in the pricing PDF",
        commercial_services="Marketing, sales enablement and revenue operations",
        training_services="HubSpot training and workshops are listed. A standalone course price is NOT PUBLISHED.",
        consultancy="Strategist allocates points",
        coaching=NP,
        implementation="HubSpot onboarding and set-up are priced separately",
        managed_service="Growth programmes and RevOps as a service",
        fractional_service=NP,
        software_platform="HubSpot. Licence cost NOT PUBLISHED as included.",
        named_partners=NP,
        technology_partners="HubSpot",
        named_clients="Recent B2B clients are named in the PDF only as a heading. The names were not in the text extract.",
        named_education_clients=NP,
        free_offers="Request a free assessment",
        newsletter=NP,
        community=NP,
        why_relevant_to_four_corners="The worked example of points, sprints and a separate RevOps retainer. The PDF does not say the four example package prices are monthly.",
    ),
]

PRODUCTS = [
    product(
        organisation_name="Gripped",
        product_name="Strategic guidance tier",
        product_category="monthly retainer",
        target_customer="B2B SaaS teams with in-house marketers",
        target_role="Marketing leaders",
        problem_solved="The team wants senior direction and occasional projects, not a full department.",
        product_description="Monthly strategic guidance and access to a specialist. Projects priced separately. Quarterly strategy sessions, planning, roadmapping.",
        format="Monthly retainer",
        live_or_on_demand="live",
        price="From £3,500 per month, plus project fees, on the pricing page. The FAQ says single-channel work typically starts around £4,000 to £6,000 per month.",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from monthly retainer",
        reporting_frequency="Quarterly strategy sessions on this tier",
        done_for_you_included="Projects are extra",
        source_url="https://gripped.io/pricing/",
        evidence_notes="Pricing page and FAQ both fetched 5 October 2026. They are not the same floor. Do not average them.",
        analysis_lesson_for_four_corners="Judgement: a guidance retainer can sit near £3,500 to £6,000 before any channel work is included.",
    ),
    product(
        organisation_name="Gripped",
        product_name="One or two channel execution",
        product_category="monthly retainer",
        target_customer="Teams that need a specialist channel",
        target_role="Marketing leaders",
        problem_solved="One or two channels need execution, not a whole department.",
        product_description="Channel strategy, campaign execution, performance analysis, monthly strategy reviews.",
        format="Monthly retainer",
        live_or_on_demand="done for the client",
        price="From £7,500 per month on the pricing page",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from monthly retainer",
        reporting_frequency="Monthly strategy reviews",
        done_for_you_included="Yes, for the chosen channels",
        source_url="https://gripped.io/pricing/",
        evidence_notes="Ad spend is not included.",
    ),
    product(
        organisation_name="Gripped",
        product_name="Full demand generation",
        product_category="managed service",
        target_customer="Teams that want an outsourced marketing engine",
        target_role="Marketing leaders",
        problem_solved="Strategy, paid media, content, SEO and conversion need one team.",
        product_description="Monthly planning, multi-channel campaigns, content, paid media management, marketing operations, sales alignment, weekly syncs, monthly strategy reviews. 30-day sprints and 90-day objectives are described for plans generally.",
        format="Monthly retainer",
        live_or_on_demand="done for the client",
        price="From £15,000 per month on the pricing page. The FAQ says comprehensive programmes go up to £15,000 to £20,000+ per month.",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from monthly retainer",
        minimum_term="FAQ: usually 3 months, then a rolling contract with 3 months' notice. The pricing page does not repeat the notice period.",
        reporting_frequency="Weekly syncs and monthly strategy reviews",
        account_management="Dedicated marketing account manager and strategist",
        dashboard_included="Reporting is included. A product name for the dashboard is NOT PUBLISHED.",
        done_for_you_included="Yes",
        source_url="https://gripped.io/pricing/",
        evidence_notes="Onboarding fee is typically charged. Amount NOT PUBLISHED. Paid media budgets and full website rebuilds are extra. Basic website refresh £18,000 to £45,000. Full redesign £45,000 to £150,000+.",
        analysis_lesson_for_four_corners="Judgement: £8,000 a month is below this agency's published full-service floor. Do not infer an education buyer will pay £15,000.",
    ),
    product(
        organisation_name="Greenlight Web",
        product_name="Outsourced marketing packages",
        product_category="monthly retainer",
        target_customer="B2B and professional-services firms",
        target_role="Owners",
        problem_solved="The buyer wants one team and a fixed monthly cost, and wants to point the hours at whatever is urgent.",
        product_description="Three caps. Every service is available on each. A dedicated account manager, monthly planning and reporting. New website builds are quoted separately. Minimum terms are agreed upfront. The length is not published.",
        format="Monthly hour cap",
        live_or_on_demand="done for the client",
        price="£2,000 per month for up to 25 hours. £3,500 per month for up to 45 hours. £5,000 per month for up to 75 hours.",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="good/better/best by hour cap",
        expert_live_hours="Caps of 25, 45 and 75 hours a month. The page does not say these are all senior hours.",
        account_management="Dedicated account manager",
        reporting_frequency="Monthly planning and reporting. A meeting count is NOT PUBLISHED.",
        done_for_you_included="Yes, inside the hours",
        source_url="https://www.greenlightweb.co.uk/marketing/full-service/",
        evidence_notes="Fetched 5 October 2026. A blog narrative that mentions an £8,000 full-service package is describing other agencies, not this price list. A £1,000 tier appeared in a search snippet and was not on this page.",
        analysis_lesson_for_four_corners="Judgement: these hour caps are the closest published capacity model to the £2,000 test. They are not education prices, and £4,000 and £8,000 are not tiers here.",
    ),
    product(
        organisation_name="Spectra Media",
        product_name="Establish",
        product_category="monthly retainer",
        target_customer="Businesses that want a full service at a steady pace",
        target_role="Owners and marketing leads",
        problem_solved="Foundations and a professional presence, without custom automation.",
        product_description="Every service from day one: strategy, content, social, SEO, design and ads. Quarterly strategy, monthly reporting, one point of contact, 12-month results guarantee.",
        format="Monthly retainer",
        live_or_on_demand="done for the client",
        price="From £3,000 per month",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from monthly retainer",
        minimum_term="12 months, with a month-six checkpoint and no penalty if agreed leading indicators are missed",
        reporting_frequency="Monthly reporting and quarterly strategy",
        account_management="One point of contact",
        done_for_you_included="Yes",
        source_url="https://www.spectra.media/pricing/",
        evidence_notes="Ad spend is paid by the client to the platforms. Print is at cost. Hours NOT PUBLISHED. Guarantee: if agreed enquiry targets are missed they keep working at their cost. A separate page illustrates £3,000 a month against £36,000 over 12 months.",
        analysis_lesson_for_four_corners="Judgement: £3,000 is this firm's published floor for a full menu. Pace, not the menu, is what the next tier adds.",
    ),
    product(
        organisation_name="Spectra Media",
        product_name="Grow",
        product_category="monthly retainer",
        target_customer="Businesses that want more output and automation",
        target_role="Owners and marketing leads",
        problem_solved="The entry pace is too slow, or lead capture needs a built system.",
        product_description="Everything in Establish, plus more shipped each month, custom marketing automation, monthly senior strategy and faster turnaround.",
        format="Monthly retainer",
        live_or_on_demand="done for the client",
        price="From £6,000 per month",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from monthly retainer",
        minimum_term="12 months with a month-six checkpoint",
        source_url="https://www.spectra.media/pricing/",
        evidence_notes="Automation is the capability the £3,000 tier does not include.",
    ),
    product(
        organisation_name="Spectra Media",
        product_name="Scale",
        product_category="monthly retainer",
        target_customer="Businesses that want the fastest pace and an embedded lead",
        target_role="Leadership teams",
        problem_solved="The work needs a named strategic lead and board reporting.",
        product_description="Fastest pace, advanced automation, experimentation and attribution, a named strategic lead, dedicated resource, in-house print at cost, board-ready monthly reporting.",
        format="Monthly retainer",
        live_or_on_demand="done for the client",
        price="From £12,000. The tier heading does not repeat 'per month'. Establish and Grow do.",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from monthly retainer. The per-month wording is explicit on the two lower tiers only.",
        minimum_term="12 months with a month-six checkpoint",
        reporting_frequency="Board-ready monthly reporting",
        source_url="https://www.spectra.media/pricing/",
        analysis_lesson_for_four_corners="Judgement: an embedded strategic lead appears at the top from-price, not inside the £3,000 tier.",
    ),
    product(
        organisation_name="Digital Litmus",
        product_name="Example growth packages",
        product_category="points",
        target_customer="B2B companies buying a growth programme",
        target_role="Marketing and sales leaders",
        problem_solved="The buyer wants to choose capacity and move points between activities.",
        product_description="Example packages in a 2025 PDF: Starter 64 points £5,800; Grow 80 points £7,200 with an asterisk; Accelerate 102 points £9,200; MAX 163 points £14,700. Inclusions scale from a blueprint and two blogs to fuller content, campaigns and HubSpot management. The asterisk is not explained in the text extract.",
        format="Points package, spent in 90-day sprints",
        live_or_on_demand="done for the client",
        price="£5,800; £7,200; £9,200; £14,700",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="points",
        programme_length="90-day sprints. Points can be adjusted after a sprint.",
        account_management="Dedicated account manager",
        reporting_frequency="Quarterly strategic review on the examples. Dashboard reporting on the higher examples.",
        source_url="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf",
        evidence_notes="The four prices are not printed with 'per month'. Continuous-improvement lines elsewhere in the PDF are per month. Do not convert these four into monthly fees.",
        analysis_lesson_for_four_corners="Judgement: points let the buyer change the work without a new quote. The missing per-month label is a reason not to compare them with a monthly partnership.",
    ),
    product(
        organisation_name="Digital Litmus",
        product_name="Continuous improvement",
        product_category="monthly retainer",
        target_customer="B2B companies with a site that needs ongoing improvement",
        target_role="Marketing leads",
        problem_solved="The site needs a monthly points allowance after launch.",
        product_description="15 points £1,500 per month; 25 points £2,375 per month; 35 points £3,150 per month; 50 points £4,250 per month.",
        format="Monthly points",
        live_or_on_demand="done for the client",
        price="£1,500 to £4,250 per month",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="points",
        source_url="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf",
        evidence_notes="These lines do say p/m. They sit under website continuous improvement.",
    ),
    product(
        organisation_name="Digital Litmus",
        product_name="HubSpot onboarding and RevOps",
        product_category="implementation and retainer",
        target_customer="B2B companies buying HubSpot or revenue operations",
        target_role="Revenue and marketing operations leads",
        problem_solved="The CRM needs a set-up, or sales and marketing operations need a monthly service.",
        product_description="Onboarding starting at £2,000. Hub set-up starting at £3,000. RevOps starting at £1,500 per month. Website builds are separate: £8,500, £10,500, £17,500 and £23,500 by page count.",
        format="Project plus an optional monthly service",
        live_or_on_demand="done for the client",
        price="From £2,000 onboarding. From £3,000 hub set-up. From £1,500 per month RevOps.",
        VAT_wording="VAT status NOT PUBLISHED",
        price_mechanism="from fixed project, and a from monthly retainer",
        source_url="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf",
        analysis_lesson_for_four_corners="Judgement: implementation is a project floor, and the ongoing RevOps fee starts lower than the growth-package examples.",
    ),
]


def append(name, fields, new_rows):
    path = HERE / name
    import csv
    with path.open(newline="", encoding="utf-8") as f:
        existing = list(csv.DictReader(f))
    if name == "competitor_organisations.csv":
        seen = {r["organisation_name"] for r in existing}
        new_rows = [r for r in new_rows if r["organisation_name"] not in seen]
    if name == "competitor_products.csv":
        seen = {(r["organisation_name"], r["product_name"]) for r in existing}
        new_rows = [r for r in new_rows if (r["organisation_name"], r["product_name"]) not in seen]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_MINIMAL, extrasaction="ignore")
        writer.writeheader()
        for item in existing + new_rows:
            writer.writerow(item)
    print(f"{name}: +{len(new_rows)} -> {len(existing) + len(new_rows)}")


def main():
    append("competitor_organisations.csv", batch1.ORG_FIELDS, ORGS)
    append("competitor_products.csv", batch1.PRODUCT_FIELDS, PRODUCTS)
    prices = [
        row(batch1.PRICE_FIELDS, organisation="Gripped", product="Retainers", pricing_model="good/better/best", price="Pricing page from £3,500, £7,500 and £15,000 per month. FAQ from about £4,000-£6,000 to £15,000-£20,000+.", what_customer_thinks_they_are_buying="Pipeline capacity", what_appears_to_drive_price="Scope, channels and complexity", hours_or_capacity_if_published=NP, exclusions="Paid media budgets. Full website rebuilds. Third-party tools.", ad_spend_extra="Yes. LinkedIn minimum recommended £5,000 a month. Google £3,000 to £5,000.", software_extra="Client buys tools", minimum_term="FAQ: usually 3 months, then 3 months' notice", cancellation_terms_if_published="3 months' notice either side. No mid-contract pause.", upsell_logic="Judgement: start on a channel and add scope. Onboarding fee amount NOT PUBLISHED.", source="https://gripped.io/pricing/"),
        row(batch1.PRICE_FIELDS, organisation="Greenlight Web", product="Outsourced marketing packages", pricing_model="good/better/best", price="£2,000 / £3,500 / £5,000 per month", what_customer_thinks_they_are_buying="A block of team hours and every service", what_appears_to_drive_price="The hour cap, not the menu", hours_or_capacity_if_published="Up to 25, 45 or 75 hours", exclusions="New website builds", ad_spend_extra=NP, minimum_term="Agreed upfront. Length NOT PUBLISHED.", source="https://www.greenlightweb.co.uk/marketing/full-service/"),
        row(batch1.PRICE_FIELDS, organisation="Spectra Media", product="Establish, Grow, Scale", pricing_model="good/better/best", price="From £3,000, from £6,000, and from £12,000 per month. Scale's heading omits the words per month.", what_customer_thinks_they_are_buying="Pace and, from £6,000, automation", what_appears_to_drive_price="How much is shipped, plus automation and a named lead at the top", hours_or_capacity_if_published=NP, exclusions="Ad spend paid to platforms. Print at cost.", ad_spend_extra="Yes", minimum_term="12 months", cancellation_terms_if_published="Month-six checkpoint. No penalty if agreed leading indicators are missed.", upsell_logic="Judgement: the menu stays. The buyer pays for speed and automation.", source="https://www.spectra.media/pricing/"),
        row(batch1.PRICE_FIELDS, organisation="Digital Litmus", product="Points and RevOps", pricing_model="points", price="Example packages £5,800 to £14,700 without a per-month label. Continuous improvement £1,500 to £4,250 per month. RevOps from £1,500 per month.", what_customer_thinks_they_are_buying="A bag of points, or a RevOps retainer", what_appears_to_drive_price="How many points, and whether the work is a project or a month", source="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf"),
    ]
    ladders = [
        row(batch1.LADDER_FIELDS, organisation_name="Gripped", step_1="30-minute session", step_2="Onboarding fee. Amount NOT PUBLISHED.", step_3="From £3,500 or, on the FAQ, about £4,000 to £6,000 a month", step_4="From £7,500 a month for one or two channels", step_5="From £15,000 a month for full demand generation", step_6="Website project £18,000 to £150,000+", evidence="Pricing page and FAQ, 5 October 2026.", likely_commercial_logic="Judgement: they refuse a pilot because the data needs a quarter. The notice period protects that."),
        row(batch1.LADDER_FIELDS, organisation_name="Spectra Media", step_1="Free 30-minute call", step_2="One-off project, quoted, no guarantee", step_3="Establish from £3,000 a month", step_4="Grow from £6,000 a month", step_5="Scale from £12,000", step_6=NP, evidence="Pricing page 5 October 2026.", likely_commercial_logic="Judgement: the guarantee is the reason for 12 months. Projects are the door for buyers who will not sign that term."),
        row(batch1.LADDER_FIELDS, organisation_name="Digital Litmus", step_1="Free assessment", step_2="Discovery session", step_3="Points package or a website project", step_4="90-day sprint", step_5="Adjust points up or down", step_6="RevOps from £1,500 a month or HubSpot set-up from £2,000", evidence="2025 pricing PDF, fetched 5 October 2026.", likely_commercial_logic="Judgement: points make expansion a settings change. The sprint review is the commercial moment."),
    ]
    frees = [
        row(batch1.FREE_FIELDS, organisation="Gripped", free_offer="30-minute session", format="Call", what_customer_receives="Advice. The page says no pitch and no obligation.", estimated_effort_to_supplier="30 minutes. Preparation NOT PUBLISHED.", CTA="Book", next_paid_step="A retainer. They say they do not offer a trial.", source="https://gripped.io/pricing/"),
        row(batch1.FREE_FIELDS, organisation="Spectra Media", free_offer="30-minute strategy call", format="Call", what_customer_receives="A later scoped quote", estimated_effort_to_supplier="30 minutes plus a quote", CTA="Book a strategy call", next_paid_step="Establish from £3,000 a month, or a one-off project", source="https://www.spectra.media/pricing/"),
        row(batch1.FREE_FIELDS, organisation="Digital Litmus", free_offer="Free assessment", format="Request. The assessment method is NOT PUBLISHED.", what_customer_receives="NOT PUBLISHED", estimated_effort_to_supplier=NP, CTA="Request free assessment", next_paid_step="A scoped growth programme", source="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf"),
    ]
    ops = [
        row(batch1.OPS_FIELDS, organisation_name="Gripped", competitor_class=M, who_leads_client_relationship="Dedicated account lead", account_manager_model="Account manager and strategist", strategist_model="Same pair lead sprints", specialist_network="In-house paid media, SEO, creative, martech and web", freelancers_or_partners="Deeper positioning can be referred out", in_house_or_outsourced="Described as in-house specialists", meeting_rhythm="Weekly or bi-weekly, plus quarterly business reviews", planning_cycle="30-day sprints and 90-day objectives. Onboarding is about four weeks.", reporting_rhythm="Pipeline, revenue influenced, cost per opportunity", onboarding="Week 1 discovery, week 2 strategy, week 3 build, week 4 launch", reviews="Quarterly business reviews", client_approvals="Messaging approved before it goes live", project_management="Account lead", escalation=NP, qa=NP, source="https://gripped.io/pricing/", verified_date=V),
        row(batch1.OPS_FIELDS, organisation_name="Greenlight Web", competitor_class=M, who_leads_client_relationship="Dedicated account manager", account_manager_model="One manager owns delivery and coordinates specialists", strategist_model="Planning sits with the account manager", specialist_network="Multi-disciplinary team inside the hour cap", freelancers_or_partners=NP, in_house_or_outsourced="One agency team", meeting_rhythm="Regular check-ins. Count NOT PUBLISHED.", planning_cycle="Monthly work plan", reporting_rhythm="Monthly", onboarding=NP, reviews="Performance reviews", client_approvals=NP, project_management="Account manager", escalation=NP, qa=NP, source="https://www.greenlightweb.co.uk/marketing/full-service/", verified_date=V),
        row(batch1.OPS_FIELDS, organisation_name="Spectra Media", competitor_class=M, who_leads_client_relationship="One point of contact on Establish. Named strategic lead on Scale.", account_manager_model="Single contact, then an embedded lead at the top tier", strategist_model="Quarterly on Establish. Monthly senior strategy on Grow.", specialist_network=NP, freelancers_or_partners=NP, in_house_or_outsourced="Their team. Print can be in-house at cost.", meeting_rhythm=NP, planning_cycle="12-month term. Month-six checkpoint.", reporting_rhythm="Monthly. Board-ready on Scale. Shared dashboard on the guarantee page.", onboarding="Targets agreed in writing before work starts", reviews="Month six", client_approvals=NP, project_management=NP, escalation=NP, qa="Targets tracked on qualified enquiries", source="https://www.spectra.media/pricing/", verified_date=V),
        row(batch1.OPS_FIELDS, organisation_name="Digital Litmus", competitor_class=M, who_leads_client_relationship="Dedicated strategist and account manager", account_manager_model="Dedicated account manager on the example packages", strategist_model="Strategist agrees how points are spent", specialist_network="Growth, web and HubSpot specialists", freelancers_or_partners=NP, in_house_or_outsourced="Their team", meeting_rhythm=NP, planning_cycle="90-day sprints", reporting_rhythm="Quarterly strategic review", onboarding="Discovery, then a costed programme", reviews="After each sprint", client_approvals=NP, project_management=NP, escalation=NP, qa=NP, source="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf", verified_date=V),
    ]
    langs = [
        row(batch1.LANG_FIELDS, organisation="Gripped", competitor_class=M, headline="Transparent pricing that scales with your growth", strapline="Outsourced marketing team at the top tier", CTA="30-minute session", short_phrase="flat retainer", repeated_buzzword="pipeline", outcome_language="pipeline and revenue", trust_language="SaaS specialist", risk_reduction_language="no percentage of ad spend", managed_service_language="we become your outsourced marketing team", partnership_language="partner, not a vendor charging by the hour", differentiation_language="not a jack of all trades", source="https://gripped.io/pricing/"),
        row(batch1.LANG_FIELDS, organisation="Greenlight Web", competitor_class=M, headline="Your outsourced marketing department", strapline="Fixed monthly cost", CTA=NP, short_phrase="up to 25 hours", repeated_buzzword="hours", outcome_language="enquiries and revenue", trust_language="one accountable team", risk_reduction_language="fixed cost", managed_service_language="outsourced marketing department", partnership_language="extension of your business", differentiation_language="hours, not a rigid package", source="https://www.greenlightweb.co.uk/marketing/full-service/"),
        row(batch1.LANG_FIELDS, organisation="Spectra Media", competitor_class=M, headline="It's not what it costs. It's what it returns.", strapline="Results guaranteed on plans", CTA="Book a 30-minute call", short_phrase="from £3k a month", repeated_buzzword="guarantee", outcome_language="qualified enquiries", trust_language="targets in writing", risk_reduction_language="we keep working at our cost; month-six exit", managed_service_language="every service included", partnership_language="one point of contact", differentiation_language="pace, not a different menu", source="https://www.spectra.media/pricing/"),
        row(batch1.LANG_FIELDS, organisation="Digital Litmus", competitor_class=M, headline="Points-based pricing", strapline="90-day sprints", CTA="Request a free assessment", short_phrase="adjust the points", repeated_buzzword="points", outcome_language="leads and sales", trust_language="HubSpot specialists since 2015", risk_reduction_language="points can move down after a sprint", managed_service_language="growth programme", partnership_language="in partnership with you", differentiation_language="not a run-of-the-mill agency", source="https://www.digitallitmus.com/hubfs/Sales%20Collateral/PDFs/Digital%20Litmus%20Pricing.pdf"),
    ]
    experts = [
        row(batch1.EXPERT_FIELDS, organisation="Gripped", model_name="In-house specialist bench", how_experts_are_used="Paid media, SEO, creative, martech and web sit behind one account lead. Deeper brand work can be referred.", promise_to_expert=NP, promise_to_client="The buyer is not shuffled to juniors. That is a claim.", how_work_is_allocated="Account lead pulls specialists in", quality_control="Client approves messaging before launch", what_four_corners_can_learn="Judgement: the client meets one lead. Specialists are a bench, not a menu of freelancers the client manages.", source="https://gripped.io/frequently-asked-questions/", verified_date=V),
        row(batch1.EXPERT_FIELDS, organisation="The Stickman Consultancy", model_name="Already recorded in the school batch", how_experts_are_used="See the school row.", promise_to_expert=NP, promise_to_client=NP, how_work_is_allocated=NP, quality_control=NP, what_four_corners_can_learn="Not a benchmark row.", source="https://thestickmanconsultancy.co.uk/our-services/strategic-marketing-plan/", verified_date=V),
    ]
    # Do not add a duplicate Stickman expert row.
    experts = [e for e in experts if e["organisation"] != "The Stickman Consultancy"]
    append("pricing_models.csv", batch1.PRICE_FIELDS, prices)
    append("product_ladders.csv", batch1.LADDER_FIELDS, ladders)
    append("free_offers.csv", batch1.FREE_FIELDS, frees)
    append("operating_models.csv", batch1.OPS_FIELDS, ops)
    append("competitor_language.csv", batch1.LANG_FIELDS, langs)
    append("expert_network_models.csv", batch1.EXPERT_FIELDS, experts)


if __name__ == "__main__":
    main()
