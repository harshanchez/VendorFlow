"""Streamlit entry point for the VendorFlow P0 demonstration."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "src"))

from vendorflow.fixtures import (
    BUNDLED_DOCUMENTS,
    FIXTURE_LABELS,
    FORM_VENDORS,
    SPOT_CHECK_LABELS,
    SPOT_CHECK_VENDORS,
    bundled_document,
    documents_for,
)
from vendorflow.models import DocumentInput, PipelineRun, StageState
from vendorflow.persistence import (
    Repository,
    describe_supabase_error,
    persist_with_fallback,
    session_history,
    supabase_credentials,
)
from vendorflow.pipeline import run_pipeline

load_dotenv()

FIELD_KEYS = (
    "legal_name",
    "country",
    "state_code",
    "gstin",
    "pan",
    "bank_account_name",
    "bank_account_number",
    "ifsc",
    "contact_email",
    "vendor_category",
)


def widget_key(field: str) -> str:
    return f"vendorflow_{field}"


def initialise_state() -> None:
    defaults = {"country": "IN", "vendor_category": "goods"}
    for field in FIELD_KEYS:
        st.session_state.setdefault(widget_key(field), defaults.get(field, ""))
    st.session_state.setdefault("vendorflow_history", [])


def apply_interaction_polish() -> None:
    """Give the small Streamlit surface a clearer hierarchy and crisp controls."""
    st.markdown(
        """
        <style>
        [data-testid="stMainBlockContainer"] {
            max-width: 1180px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }
        [data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.035);
            border: 1px solid rgba(30, 41, 59, 0.12);
            border-radius: 12px;
            padding: 1rem 1.1rem;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }
        [data-testid="stTabs"] button[role="tab"] {
            border-radius: 8px 8px 0 0;
            font-weight: 600;
        }
        [data-testid="stForm"], [data-testid="stExpander"] {
            border: 1px solid rgba(30, 41, 59, 0.13);
            border-radius: 12px;
        }
        .stButton > button {
            transition: transform 160ms cubic-bezier(0.23, 1, 0.32, 1);
        }
        .stButton > button:active {
            transform: scale(0.97);
        }
        @media (hover: hover) and (pointer: fine) {
            .stButton > button:hover {
                transform: translateY(-1px);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_fixture(name: str) -> None:
    for field, value in FORM_VENDORS[name].items():
        st.session_state[widget_key(field)] = value
    st.session_state["vendorflow_selected_fixture"] = name


def form_payload() -> dict[str, str]:
    return {field: st.session_state[widget_key(field)] for field in FIELD_KEYS}


def repository() -> Repository:
    url, anon_key = supabase_credentials(st.secrets)
    return Repository(url=url, anon_key=anon_key)


def remote_history(repo: Repository) -> tuple[list[dict[str, Any]], str | None]:
    if not repo.configured:
        return [], None
    try:
        return repo.history(), None
    except Exception as exc:  # noqa: BLE001 - any remote client failure must use the honest fallback
        return [], describe_supabase_error(exc)


def combined_history(repo: Repository) -> tuple[list[dict[str, Any]], str | None]:
    remote, issue = remote_history(repo)
    session = session_history(st.session_state)
    remote_ids = {str(item.get("id")) for item in remote}
    return remote + [item for item in session if str(item.get("id")) not in remote_ids], issue


def render_live_run(run: PipelineRun) -> None:
    st.subheader("Live run")
    for stage in run.stages:
        state = "error" if stage.state == StageState.ERROR else "complete"
        with st.status(stage.label, expanded=False, state="running") as status:
            st.write(stage.detail)
            status.update(label=f"{stage.label} — {stage.state.value}", state=state, expanded=False)
    decision = run.decision
    if decision.status.value == "Approved":
        st.success(f"{decision.status}: {decision.summary}")
    elif decision.status.value == "Pending":
        st.warning(f"{decision.status}: {decision.summary}")
    else:
        st.error(f"{decision.status}: {decision.summary}")
    if decision.reason_codes:
        st.write("Reason codes: " + ", ".join(decision.reason_codes))
    if decision.follow_up:
        st.info(f"Follow-up draft (not sent): {decision.follow_up}")
    with st.expander("Decision reasoning", expanded=decision.status.value != "Approved"):
        st.dataframe(
            [
                {
                    "Check": check.check_id,
                    "Outcome": check.outcome.value,
                    "Reason code": check.reason_code or "—",
                    "Explanation": check.human_readable_reason,
                    "Follow-up": check.follow_up_action or "—",
                }
                for check in decision.checks
            ],
            width="stretch",
            hide_index=True,
        )
    st.caption("Demonstration policy only. Format checks are not GSTN, bank, or identity verification.")


def render_new_run(repo: Repository) -> None:
    st.subheader("New vendor onboarding run")
    st.caption("Load a fictional fixture, edit any field, then run the same form workflow used for manual intake.")
    buttons = st.columns(4)
    for column, name in zip(buttons, FIXTURE_LABELS, strict=True):
        if column.button(FIXTURE_LABELS[name], key=f"fixture_{name}", width="stretch"):
            load_fixture(name)

    spot_col, load_spot_col = st.columns((3, 1))
    with spot_col:
        spot_key = st.selectbox(
            "Spot-check vendor (10, one run each)",
            options=list(SPOT_CHECK_VENDORS),
            format_func=lambda key: SPOT_CHECK_LABELS[key],
            help="Each vendor has its own legal name and GSTIN, so it will not collide with the others. Running the same one twice is still a duplicate.",
        )
    with load_spot_col:
        st.write("")
        if st.button("Load selected vendor", width="stretch"):
            load_fixture(spot_key)

    with st.form("vendor_intake_form", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            st.text_input("Legal name", key=widget_key("legal_name"))
            st.selectbox("Country", ["IN"], key=widget_key("country"))
            st.text_input("State code", key=widget_key("state_code"), help="Two-digit GST state code, e.g. 29.")
            st.text_input("GSTIN", key=widget_key("gstin"), help="Format check only; no GSTN lookup.")
            st.text_input("PAN", key=widget_key("pan"), help="Format check only; no PAN lookup.")
        with right:
            st.text_input("Bank account name", key=widget_key("bank_account_name"))
            st.text_input("Bank account number", key=widget_key("bank_account_number"), type="password")
            st.text_input("IFSC", key=widget_key("ifsc"), help="Format check only; no bank lookup.")
            st.text_input("Contact email", key=widget_key("contact_email"))
            st.selectbox("Vendor category", ["goods", "services", "both"], key=widget_key("vendor_category"))
        upload = st.file_uploader("Optional supporting PDF", type=["pdf"], help="No PDF is required for approval.")
        use_local_pdf_test = st.checkbox(
            "Use local PDF test file (no file dialog)",
            help="Uses the fictional PDF in pdf_test. An uploaded PDF still takes precedence.",
        )
        selected_vendor = st.session_state.get("vendorflow_selected_fixture")
        if selected_vendor in SPOT_CHECK_VENDORS:
            st.caption(f"Bundled documents for {SPOT_CHECK_VENDORS[selected_vendor]['legal_name']}.")
        bundled_document_name = st.selectbox(
            "Or use a bundled fictional PDF",
            options=["none", *documents_for(selected_vendor)],
            format_func=lambda name: "No bundled document" if name == "none" else BUNDLED_DOCUMENTS[name]["label"],
            help="Uploaded PDFs take precedence. Load a spot-check vendor to get that vendor's matching and conflicting documents.",
        )
        submitted = st.form_submit_button("Run deterministic onboarding", type="primary")

    if not submitted:
        return
    if upload:
        document = DocumentInput(filename=upload.name, content=upload.getvalue())
    elif use_local_pdf_test:
        local_pdf = Path(__file__).parent / "pdf_test" / "VF-DEMO_Acme_matching_document.pdf"
        try:
            document = DocumentInput(filename=local_pdf.name, content=local_pdf.read_bytes())
        except FileNotFoundError:
            st.error("The local test PDF is missing. Generate it again in the pdf_test folder, then retry.")
            return
    elif bundled_document_name != "none":
        try:
            document = bundled_document(bundled_document_name)
        except FileNotFoundError:
            st.error("Bundled PDF fixtures are missing. Run `python scripts/make_demo_pdfs.py` once, then retry.")
            return
    else:
        document = None
    history, history_issue = combined_history(repo)
    if history_issue:
        st.warning(history_issue)
    run = run_pipeline(form_payload(), document=document, previous_submissions=history)
    outcome = persist_with_fallback(run, repo, st.session_state)
    st.session_state["vendorflow_last_run"] = run
    render_live_run(run)
    if outcome.stored_remotely:
        st.success(outcome.message)
    else:
        st.warning(outcome.message)


def render_overview(repo: Repository) -> None:
    st.subheader("Overview")
    history, issue = combined_history(repo)
    if issue:
        st.warning(issue)
    if not repo.configured:
        st.info("Supabase is not configured. Runs remain in this browser session until you add Streamlit secrets.")
    counts = Counter(item.get("status", "Unknown") for item in history)
    cols = st.columns(4)
    cols[0].metric("Total runs", len(history))
    cols[1].metric("Approved", counts["Approved"])
    cols[2].metric("Pending", counts["Pending"])
    cols[3].metric("Rejected", counts["Rejected"])
    st.caption("Counts reflect available synthetic demonstration history, not vendor performance KPIs.")


def render_history(repo: Repository) -> None:
    st.subheader("History")
    history, issue = combined_history(repo)
    if issue:
        st.warning(issue)
    if history:
        st.dataframe(history, width="stretch", hide_index=True)
    else:
        st.info("No runs yet. Use a fixture or enter a vendor in the New run tab.")


def main() -> None:
    st.set_page_config(page_title="VendorFlow", page_icon="📋", layout="wide")
    initialise_state()
    apply_interaction_polish()
    repo = repository()
    st.title("VendorFlow")
    st.caption("Demonstration policy — not a legal, tax, or bank verification product.")
    overview_tab, new_run_tab, live_run_tab, history_tab = st.tabs(["Overview", "New run", "Live run", "History"])
    with overview_tab:
        render_overview(repo)
    with new_run_tab:
        render_new_run(repo)
    with live_run_tab:
        latest = st.session_state.get("vendorflow_last_run")
        if latest:
            render_live_run(latest)
        else:
            st.info("Run a form submission to see its seven deterministic stages here.")
    with history_tab:
        render_history(repo)


if __name__ == "__main__":
    main()
