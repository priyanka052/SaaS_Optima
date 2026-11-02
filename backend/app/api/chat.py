"""Keyword-based SaaSOptima chatbot (no external AI/model required)."""

import re
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.models.negotiation import Negotiation
from app.ml.overlap import jaccard_similarity, parse_features
from app.api.compare import compare_tools
from app.api.negotiation import NegotiationRequest, start_negotiation
from app.api.evaluation import get_evaluation_summary

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

# In-memory chat context for the first prototype. It resets when the server restarts.
SESSIONS: dict[str, dict] = {}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = None


def find_tool_names(message: str, names: list[str]) -> list[str]:
    text = message.casefold()
    found = []
    for name in sorted(names, key=len, reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(name.casefold()) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.append(name)
    return found


def get_names() -> list[str]:
    with SessionLocal() as db:
        return [row[0] for row in db.query(Tool.name).order_by(Tool.name).all()]


def extract_budget(message: str, allow_bare_number: bool = False):
    num = r"([0-9][0-9,]*(?:\.[0-9]{1,2})?)"
    match = re.search(r"(?:budget|max(?:imum)?|under|up to|spend|limit)\D{0,20}₹?\s*" + num, message, re.I)
    if not match and allow_bare_number:
        match = re.search(r"₹?\s*" + num, message, re.I)
    return float(match.group(1).replace(",", "")) if match else None


def currency_for(tool_name: str) -> str:
    with SessionLocal() as db:
        tool = db.query(Tool).filter(Tool.name.ilike(tool_name)).first()
        if tool:
            item = db.query(Pricing).filter(Pricing.tool_id == tool.id).first()
            if item and item.currency:
                return item.currency.upper()
            if tool.price_inr is not None:
                return "INR"
    return "the price record's currency"


def run_negotiation(tool_name: str, budget: float, state: dict) -> str:
    try:
        result = start_negotiation(
            NegotiationRequest(tool_name=tool_name, buyer_budget=budget)
        )
    except HTTPException as exc:
        return f"I couldn't start the negotiation: {exc.detail}"
    except Exception:
        return "The negotiation could not start because of a backend error. Please try again."

    state["last_tool"] = result.get("tool_name", tool_name)
    state["last_negotiation_id"] = result.get("negotiation_id")
    state["pending"] = None
    status = (result.get("status") or "unknown").title()
    currency = result.get("currency") or ""
    final_price = result.get("final_price")
    final_text = f" Final price: {currency} {final_price:.2f}." if final_price is not None else " No final price was agreed."
    return (
        f"Negotiation for {result.get('tool_name', tool_name)}: {status}."
        f" Base price: {currency} {result['base_price']:.2f}."
        f"{final_text} Reported savings: {result.get('savings_percent', 0):.2f}%."
        f" Deal score: {result.get('deal_score', 0):.2f}."
        f" Saved negotiation ID: {result.get('negotiation_id')}."
    )


@router.post("")
def chat(request: ChatRequest):
    message = request.message.strip()
    session_id = request.session_id or str(uuid4())
    state = SESSIONS.setdefault(session_id, {
        "last_tool": None, "pending": None, "pending_tool": None,
        "suggestions": [], "last_negotiation_id": None,
    })
    text = message.casefold()
    mentioned = find_tool_names(message, get_names())

    if text in {"cancel", "never mind", "nevermind", "start over"}:
        state["pending"] = None
        state["pending_tool"] = None
        reply = "Cancelled. You can ask for pricing, compare tools, find alternatives, negotiate, or view history."
        return {"session_id": session_id, "reply": reply, "intent": "cancel"}

    # Follow-up for a negotiation whose tool name or budget was missing.
    if state["pending"] == "negotiate_tool":
        if not mentioned:
            reply = "Which SaaS tool do you want to negotiate for? Please use a name from the catalog."
            return {"session_id": session_id, "reply": reply, "intent": "clarification"}
        state["pending_tool"] = mentioned[0]
        state["last_tool"] = mentioned[0]
        state["pending"] = "negotiate_budget"
        reply = f"What is your maximum budget in {currency_for(mentioned[0])}? Type an amount like 270."
        return {"session_id": session_id, "reply": reply, "intent": "clarification"}

    if state["pending"] == "negotiate_budget":
        budget = extract_budget(message, allow_bare_number=True)
        if budget is None or budget <= 0:
            reply = "Please enter a positive budget amount, such as 270, or type 'cancel'."
            return {"session_id": session_id, "reply": reply, "intent": "clarification"}
        tool_name = state["pending_tool"] or state["last_tool"]
        reply = run_negotiation(tool_name, budget, state)
        return {"session_id": session_id, "reply": reply, "intent": "negotiate", "negotiation_id": state["last_negotiation_id"]}

    if re.match(r"^(hi|hello|hey)\b", text):
        reply = "Hi! I'm the SaaSOptima helper. Try 'price of Slack', 'compare Slack and Microsoft Teams', 'alternatives to Slack', 'negotiate Slack', 'show history', or 'evaluation metrics'."
        return {"session_id": session_id, "reply": reply, "intent": "greeting"}

    if "help" in text or "what can you do" in text:
        reply = "I can list SaaS tools, show recorded prices, compare two tools, find feature alternatives, start a negotiation, show negotiation history, and summarize evaluation metrics."
        return {"session_id": session_id, "reply": reply, "intent": "help"}

    # Negotiation. The next message can supply the budget.
    if any(word in text for word in ("negotiate", "negotiation", "discount", "counteroffer", "counter offer")):
        tool_name = mentioned[0] if mentioned else state["last_tool"]
        if not tool_name:
            state["pending"] = "negotiate_tool"
            return {"session_id": session_id, "reply": "Which SaaS tool do you want to negotiate for?", "intent": "clarification"}
        state["last_tool"] = tool_name
        budget = extract_budget(message)
        if budget is None:
            state["pending"] = "negotiate_budget"
            state["pending_tool"] = tool_name
            reply = f"What is your maximum budget in {currency_for(tool_name)}? Type an amount like 270."
            return {"session_id": session_id, "reply": reply, "intent": "clarification"}
        if budget <= 0:
            return {"session_id": session_id, "reply": "Please provide a positive budget amount.", "intent": "clarification"}
        return {"session_id": session_id, "reply": run_negotiation(tool_name, budget, state), "intent": "negotiate", "negotiation_id": state["last_negotiation_id"]}

    # Compare two named tools, or use the previous tool for a follow-up.
    if "compare" in text or "difference between" in text:
        targets = mentioned[:2]
        if len(targets) == 1 and state["last_tool"] and targets[0].casefold() != state["last_tool"].casefold():
            targets = [state["last_tool"], targets[0]]
        elif not targets and state["last_tool"] and state["suggestions"]:
            index = 1 if "second" in text else 0
            targets = [state["last_tool"], state["suggestions"][index]]
        if len(targets) < 2:
            if targets:
                state["last_tool"] = targets[0]
                state["pending"] = "compare_tool"
                state["pending_tool"] = targets[0]
                reply = f"Which tool should I compare with {targets[0]}?"
            else:
                reply = "Which two SaaS tools should I compare? For example, 'compare Slack and Microsoft Teams'."
            return {"session_id": session_id, "reply": reply, "intent": "clarification"}
        try:
            result = compare_tools(targets[0], targets[1])
        except HTTPException as exc:
            return {"session_id": session_id, "reply": f"I couldn't compare those tools: {exc.detail}", "intent": "compare"}
        a, b = result["tool_a"], result["tool_b"]
        state["last_tool"] = a["name"]
        lines = [f"{a['name']} vs {b['name']}: {result['overlap']['similarity']}% recorded feature similarity."]
        common = result["overlap"].get("common_features", [])
        lines.append("Shared features: " + (", ".join(common[:5]) if common else "none recorded") + ".")
        ca, cb = (a.get("currency") or "").upper(), (b.get("currency") or "").upper()
        if a.get("price") is not None and b.get("price") is not None:
            lines.append(f"Recorded prices: {a['name']} {ca} {a['price']}; {b['name']} {cb} {b['price']}.")
            if not ca or ca != cb:
                lines.append("Currencies differ or are missing, so I won't say which is cheaper.")
            else:
                recommendation = result.get("recommendation", {})
                if recommendation.get("cheaper_tool"):
                    lines.append(f"Lower recorded price: {recommendation['cheaper_tool']} (difference {ca} {recommendation['potential_monthly_savings']}).")
        return {"session_id": session_id, "reply": " ".join(lines), "intent": "compare"}

    # Complete a previously requested comparison.
    if state["pending"] == "compare_tool":
        if not mentioned:
            return {"session_id": session_id, "reply": "Please enter the second tool's name, or type cancel.", "intent": "clarification"}
        first, second = state["pending_tool"], mentioned[0]
        state["pending"] = None
        state["pending_tool"] = None
        try:
            result = compare_tools(first, second)
            common = result["overlap"].get("common_features", [])
            return {"session_id": session_id, "reply": f"{first} vs {second}: {result['overlap']['similarity']}% recorded feature similarity. Shared features: {', '.join(common[:5]) if common else 'none recorded'}.", "intent": "compare"}
        except HTTPException as exc:
            return {"session_id": session_id, "reply": f"I couldn't compare those tools: {exc.detail}", "intent": "compare"}

    # Alternatives based on catalog feature similarity.
    if any(word in text for word in ("alternative", "similar", "overlap", "replacement")):
        tool_name = mentioned[0] if mentioned else state["last_tool"]
        if not tool_name:
            return {"session_id": session_id, "reply": "Which tool do you want alternatives for?", "intent": "clarification"}
        with SessionLocal() as db:
            source = db.query(Tool).filter(Tool.name.ilike(tool_name)).first()
            if not source:
                return {"session_id": session_id, "reply": f"I couldn't find {tool_name} in the catalog.", "intent": "alternatives"}
            source_features = {x.strip().casefold() for x in parse_features(source.features or "") if x.strip()}
            results = []
            for candidate in db.query(Tool).filter(Tool.id != source.id).all():
                features = {x.strip().casefold() for x in parse_features(candidate.features or "") if x.strip()}
                score = jaccard_similarity(source_features, features)
                if score > 0:
                    results.append((score, candidate.name))
        results.sort(reverse=True)
        state["last_tool"] = source.name
        state["suggestions"] = [name for _, name in results[:3]]
        reply = "Alternatives with overlapping recorded features: " + (", ".join(f"{name} ({score * 100:.1f}%)" for score, name in results[:3]) if results else "none found") + ". Similarity is based on the current catalog, not a guarantee of equivalent plans."
        return {"session_id": session_id, "reply": reply, "intent": "alternatives", "suggestions": state["suggestions"]}

    # Pricing lookup.
    if any(word in text for word in ("price", "pricing", "cost", "how much", "subscription")):
        tool_name = mentioned[0] if mentioned else state["last_tool"]
        if not tool_name:
            return {"session_id": session_id, "reply": "Which tool's recorded price do you want to check?", "intent": "clarification"}
        with SessionLocal() as db:
            tool = db.query(Tool).filter(Tool.name.ilike(tool_name)).first()
            if not tool:
                return {"session_id": session_id, "reply": f"I couldn't find {tool_name} in the catalog.", "intent": "pricing"}
            rows = db.query(Pricing).filter(Pricing.tool_id == tool.id).order_by(Pricing.price.asc()).limit(5).all()
            state["last_tool"] = tool.name
            if rows:
                details = "; ".join(f"{row.plan}: {row.currency} {row.price:.2f} (billing period recorded as {row.billing_period})" for row in rows)
                reply = f"Recorded pricing for {tool.name}: {details}. Verify source and billing terms before purchasing."
            elif tool.price_inr is not None:
                reply = f"No plan pricing records found. The catalog has a legacy reference price of INR {tool.price_inr:.2f}; verify it before purchasing."
            else:
                reply = f"No pricing records are available for {tool.name}."
        return {"session_id": session_id, "reply": reply, "intent": "pricing"}

    if "history" in text or "past deal" in text or "previous negotiation" in text:
        with SessionLocal() as db:
            rows = db.query(Negotiation).order_by(Negotiation.id.desc()).limit(5).all()
            reply = "No saved negotiations yet." if not rows else "Latest negotiations: " + "; ".join(f"ID {r.id}: {r.tool_name}, {r.status}, final price {r.final_price if r.final_price is not None else 'not finalized'}" for r in rows) + "."
        return {"session_id": session_id, "reply": reply, "intent": "history"}

    if any(word in text for word in ("evaluation", "metrics", "success rate", "average savings")):
        with SessionLocal() as db:
            result = get_evaluation_summary(db)
        reply = f"Metrics: {result['total_negotiations']} total; {result['accepted_negotiations']} accepted; {result['rejected_negotiations']} rejected; success rate {result['success_rate_percent']}%; average savings {result['average_savings_percent'] if result['average_savings_percent'] is not None else 'N/A'}%; average deal score {result['average_deal_score'] if result['average_deal_score'] is not None else 'N/A'}; average turns {result['average_turns_per_negotiation']}."
        return {"session_id": session_id, "reply": reply, "intent": "evaluation", "data": result}

    if any(word in text for word in ("list tools", "list saas tools", "show tools", "available tools", "tool catalog", "catalog")):
        with SessionLocal() as db:
            rows = db.query(Tool).order_by(Tool.name.asc()).limit(15).all()
            names = [row.name for row in rows]
        return {"session_id": session_id, "reply": "Tools in the catalog: " + (", ".join(names) if names else "none found") + (". Showing up to 15; ask for a specific tool for details."), "intent": "catalog"}

    if mentioned:
        state["last_tool"] = mentioned[0]
        return {"session_id": session_id, "reply": f"I found {mentioned[0]}. Ask for its price, alternatives, a comparison, or a negotiation.", "intent": "tool_context", "tool_name": mentioned[0]}

    return {"session_id": session_id, "reply": "I didn't understand that request. Try 'price of Slack', 'compare Slack and Microsoft Teams', 'alternatives to Slack', 'negotiate Slack', 'show history', or 'evaluation metrics'.", "intent": "fallback"}
