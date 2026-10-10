import './styles.css';
import { api, formatMoney } from './api.js';

const app = document.querySelector('#app');
const state = { page: 'overview', tools: [], pricing: [], compare: null, negotiation: null };
const esc = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

function shell(content) {
  app.innerHTML = `
    <aside class="sidebar">
      <a class="brand" href="#overview"><span class="brand-mark">S</span><span>SaaS<span class="brand-light">Optima</span></span></a>
      <div class="nav-label">WORKSPACE</div>
      <nav>${[['overview','Overview'],['tools','SaaS tools'],['pricing','Pricing'],['compare','Compare'],['overlap','Overlap'],['negotiation','Negotiation']].map(([key,label]) => `<a class="nav-item ${state.page===key?'active':''}" href="#${key}"><span class="nav-dot"></span>${label}</a>`).join('')}</nav>
      <div class="side-bottom"><span class="status-dot"></span><span id="backend-status">Checking backend…</span></div>
    </aside>
    <main class="main"><header class="topbar"><div><div class="eyebrow">SAAS SPEND MANAGEMENT</div><h1>${pageTitle(state.page)}</h1></div><button class="icon-button" id="refresh" title="Refresh data" aria-label="Refresh data">↻</button></header><section class="content">${content}</section></main>`;
  app.querySelector('#refresh')?.addEventListener('click', () => renderPage(state.page));
  api.health().then(() => setBackendStatus(true)).catch(() => setBackendStatus(false));
}

function setBackendStatus(ok) {
  const el = document.querySelector('#backend-status');
  if (el) el.textContent = ok ? 'Backend connected' : 'Backend offline';
  const dot = document.querySelector('.status-dot');
  if (dot) dot.classList.toggle('offline', !ok);
}

function pageTitle(page) {
  return ({ overview: 'Overview', tools: 'SaaS tools', pricing: 'Pricing', compare: 'Compare tools', overlap: 'Feature overlap', negotiation: 'Negotiation' })[page] || 'Overview';
}

function loading(label = 'Loading data…') { return `<div class="state-card"><span class="spinner"></span><span>${esc(label)}</span></div>`; }
function empty(message) { return `<div class="state-card empty"><span class="empty-icon">○</span><strong>No results yet</strong><span>${esc(message)}</span></div>`; }
function errorBox(error, retry) { return `<div class="error-box"><div><strong>Couldn’t load this data</strong><p>${esc(error.message || error)}</p></div><button class="button secondary" id="retry">Try again</button></div>`; }
function bindRetry(render) { document.querySelector('#retry')?.addEventListener('click', render); }
function stat(label, value, note) { return `<article class="stat-card"><span class="stat-label">${esc(label)}</span><strong class="stat-value">${esc(value)}</strong><span class="stat-note">${esc(note)}</span></article>`; }

async function renderPage(page = 'overview') {
  state.page = page;
  if (page === 'overview') return renderOverview();
  if (page === 'tools') return renderTools();
  if (page === 'pricing') return renderPricing();
  if (page === 'compare') return renderCompare();
  if (page === 'overlap') return renderOverlap();
  if (page === 'negotiation') return renderNegotiation();
  return renderOverview();
}

async function renderOverview() {
  shell(loading('Loading your workspace…'));
  try {
    const [tools, pricing] = await Promise.all([api.tools(), api.pricing()]);
    state.tools = tools; state.pricing = pricing;
    const monthly = pricing.filter((item) => item.billing_period?.toLowerCase() === 'monthly');
    const total = monthly.reduce((sum, item) => sum + Number(item.price || 0), 0);
    shell(`<div class="welcome"><div><div class="eyebrow light">YOUR SOFTWARE, UNDER CONTROL</div><h2>Make every SaaS dollar count.</h2><p>Review your tools, compare plans, and find opportunities to save.</p><a class="button white" href="#tools">Explore your tools <span>→</span></a></div><div class="welcome-art"><span>✳</span><i></i><b></b></div></div>
      <div class="stat-grid">${stat('Tracked tools', tools.length, 'Connected to your catalog')}${stat('Pricing records', pricing.length, 'Across all available plans')}${stat('Listed monthly prices', formatMoney(total), `${monthly.length} monthly plans in the catalog`)}</div>
      <div class="section-heading"><div><h2>Get started</h2><p>Explore the data available from your backend.</p></div></div>
      <div class="shortcut-grid"><a class="shortcut" href="#tools"><span class="shortcut-icon purple">▦</span><strong>Browse tools</strong><span>See categories, features, and listed prices</span><b>Open tools →</b></a><a class="shortcut" href="#pricing"><span class="shortcut-icon orange">＄</span><strong>Review pricing</strong><span>Compare plans and billing periods</span><b>View pricing →</b></a><a class="shortcut" href="#compare"><span class="shortcut-icon green">⇄</span><strong>Compare two tools</strong><span>See feature overlap and price differences</span><b>Start comparing →</b></a></div>
      <p class="note">Savings and recommendations appear when the backend has enough pricing data to calculate them.</p>`);
  } catch (error) { shell(errorBox(error, renderOverview)); bindRetry(renderOverview); }
}

async function renderTools() {
  shell(loading('Loading tools…'));
  try {
    const tools = await api.tools(); state.tools = tools;
    if (!tools.length) return shell(empty('Add tools to the backend catalog to see them here.'));
    shell(`<div class="toolbar"><div><p class="muted">${tools.length} ${tools.length === 1 ? 'tool' : 'tools'} in your catalog</p></div><input class="search" id="tool-search" placeholder="Search tools or categories…" aria-label="Search tools" /></div><div class="table-wrap"><table><thead><tr><th>TOOL</th><th>CATEGORY</th><th>FEATURES</th><th>LISTED PRICE</th><th>WEBSITE</th></tr></thead><tbody id="tools-rows">${tools.map(toolRow).join('')}</tbody></table></div>`);
    const search = document.querySelector('#tool-search');
    search.addEventListener('input', () => {
      const term = search.value.trim().toLowerCase();
      document.querySelector('#tools-rows').innerHTML = tools.filter((t) => `${t.name} ${t.category}`.toLowerCase().includes(term)).map(toolRow).join('') || `<tr><td colspan="5" class="table-empty">No tools match “${esc(search.value)}”.</td></tr>`;
    });
  } catch (error) { shell(errorBox(error, renderTools)); bindRetry(renderTools); }
}
function toolRow(tool) { return `<tr><td><strong>${esc(tool.name)}</strong></td><td><span class="pill">${esc(tool.category)}</span></td><td>${(tool.features || []).slice(0,4).map((f) => `<span class="feature-tag">${esc(f)}</span>`).join(' ') || '—'}</td><td>${formatMoney(tool.price_inr, 'INR')}</td><td>${tool.url ? `<a class="text-link" href="${esc(tool.url)}" target="_blank" rel="noreferrer">Visit ↗</a>` : '—'}</td></tr>`; }

async function renderPricing() {
  shell(loading('Loading pricing…'));
  try {
    const [pricing, tools] = await Promise.all([api.pricing(), api.tools()]); state.pricing = pricing; state.tools = tools;
    if (!pricing.length) return shell(empty('No pricing records are available. Check that pricing data is seeded in the backend.'));
    const names = new Map(tools.map((tool) => [tool.id, tool.name]));
    shell(`<div class="toolbar"><p class="muted">Pricing data returned by the backend</p><input class="search" id="pricing-search" placeholder="Search tool or plan…" aria-label="Search pricing" /></div><div class="table-wrap"><table><thead><tr><th>TOOL</th><th>PLAN</th><th>PRICE</th><th>BILLING</th><th>SOURCE</th><th>UPDATED</th></tr></thead><tbody id="pricing-rows">${pricing.map((item) => pricingRow(item,names)).join('')}</tbody></table></div><p class="note">Prices are shown in the currency returned by the backend; different currencies are not added together.</p>`);
    document.querySelector('#pricing-search').addEventListener('input', (event) => {
      const term = event.target.value.toLowerCase();
      document.querySelector('#pricing-rows').innerHTML = pricing.filter((item) => `${names.get(item.tool_id) || ''} ${item.plan}`.toLowerCase().includes(term)).map((item) => pricingRow(item,names)).join('') || `<tr><td colspan="6" class="table-empty">No plans match “${esc(event.target.value)}”.</td></tr>`;
    });
  } catch (error) { shell(errorBox(error, renderPricing)); bindRetry(renderPricing); }
}
function pricingRow(item,names) { return `<tr><td><strong>${esc(names.get(item.tool_id) || `Tool #${item.tool_id}`)}</strong></td><td>${esc(item.plan)}</td><td class="price">${formatMoney(item.price,item.currency)}</td><td><span class="pill">${esc(item.billing_period)}</span></td><td>${item.source_url ? `<a class="text-link" href="${esc(item.source_url)}" target="_blank" rel="noreferrer">Source ↗</a>` : esc(item.source || '—')}</td><td>${item.last_updated ? esc(new Date(item.last_updated).toLocaleDateString()) : '—'}</td></tr>`; }

async function renderCompare() {
  shell(loading('Loading tools for comparison…'));
  try {
    const tools = await api.tools(); state.tools = tools;
    if (tools.length < 2) return shell(empty('At least two tools are needed to compare.'));
    const options = tools.map((tool) => `<option value="${esc(tool.name)}">${esc(tool.name)}</option>`).join('');
    shell(`<div class="panel"><div class="section-heading"><div><h2>Compare two tools</h2><p>Compare feature overlap, monthly price, and the backend’s cheaper option.</p></div></div><form id="compare-form" class="form-grid"><label>First tool<select name="tool_a">${options}</select></label><label>Second tool<select name="tool_b">${tools.length > 1 ? tools.slice(1).map((tool) => `<option value="${esc(tool.name)}">${esc(tool.name)}</option>`).join('') : options}</select></label><div class="form-action"><button class="button primary" type="submit">Compare tools <span>→</span></button></div></form><div id="compare-result"></div></div>`);
    document.querySelector('#compare-form').addEventListener('submit', async (event) => {
      event.preventDefault(); const data = new FormData(event.currentTarget); const a = data.get('tool_a'); const b = data.get('tool_b'); const result = document.querySelector('#compare-result');
      if (a === b) { result.innerHTML = `<div class="error-box"><p>Please select two different tools.</p></div>`; return; }
      result.innerHTML = loading('Comparing tools…');
      try { state.compare = await api.compare(a,b); result.innerHTML = renderCompareResult(state.compare); }
      catch (error) { result.innerHTML = errorBox(error, () => event.currentTarget.requestSubmit()); bindRetry(() => document.querySelector('#compare-form').requestSubmit()); }
    });
  } catch (error) { shell(errorBox(error, renderCompare)); bindRetry(renderCompare); }
}
function renderCompareResult(data) {
  const a = data.tool_a, b = data.tool_b, overlap = data.overlap || {}, rec = data.recommendation || {};
  return `<div class="result-block"><div class="compare-cards"><article class="compare-card"><span class="eyebrow">TOOL A</span><h3>${esc(a.name)}</h3><p>${esc(a.category)}</p><strong>${formatMoney(a.price,a.currency)}</strong><small>${esc(a.plan || 'Monthly price')}</small></article><div class="versus">VS</div><article class="compare-card"><span class="eyebrow">TOOL B</span><h3>${esc(b.name)}</h3><p>${esc(b.category)}</p><strong>${formatMoney(b.price,b.currency)}</strong><small>${esc(b.plan || 'Monthly price')}</small></article></div><div class="result-summary"><div><span>Feature similarity</span><strong>${esc(overlap.similarity ?? 0)}%</strong></div><div><span>Potential monthly difference</span><strong>${rec.potential_monthly_savings == null ? '—' : formatMoney(rec.potential_monthly_savings, a.currency || b.currency)}</strong></div><div><span>Lower-priced tool</span><strong>${esc(rec.cheaper_tool || 'Not available')}</strong></div></div><div class="feature-columns"><div><h4>Shared features</h4>${featureList(overlap.common_features)}</div><div><h4>Only in ${esc(a.name)}</h4>${featureList(overlap.unique_features_a)}</div><div><h4>Only in ${esc(b.name)}</h4>${featureList(overlap.unique_features_b)}</div></div></div>`;
}
function featureList(items = []) { return items.length ? `<ul class="feature-list">${items.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : `<p class="muted">No features listed.</p>`; }

async function renderOverlap() {
  shell(loading('Finding overlapping tools…'));
  try {
    const overlaps = await api.overlap();
    if (!overlaps.length) return shell(empty('No tool pairs with overlapping features were returned.'));
    shell(`<div class="toolbar"><p class="muted">${overlaps.length} tool pairs found</p><label class="threshold">Minimum similarity <input id="threshold" type="number" min="0" max="100" value="0" /> %</label></div><div class="overlap-grid" id="overlap-rows">${overlaps.map(overlapCard).join('')}</div>`);
    document.querySelector('#threshold').addEventListener('change', async (event) => {
      const wrap = document.querySelector('#overlap-rows'); wrap.innerHTML = loading('Updating results…');
      try { const rows = await api.overlap(Math.max(0,Math.min(100,Number(event.target.value)||0))); wrap.innerHTML = rows.length ? rows.map(overlapCard).join('') : `<div class="state-card empty">No pairs meet this threshold.</div>`; }
      catch (error) { wrap.innerHTML = `<div class="error-box">${esc(error.message)}</div>`; }
    });
  } catch (error) { shell(errorBox(error, renderOverlap)); bindRetry(renderOverlap); }
}
function overlapCard(item) { return `<article class="overlap-card"><div class="overlap-top"><span class="pill purple-pill">${esc(item.similarity)}% similar</span><span class="muted">MONTHLY</span></div><h3>${esc(item.tool_a)} <span>↔</span> ${esc(item.tool_b)}</h3><div class="price-pair"><div><small>${esc(item.tool_a)}</small><strong>${formatMoney(item.price_a)}</strong></div><div><small>${esc(item.tool_b)}</small><strong>${formatMoney(item.price_b)}</strong></div></div><div class="recommendation"><span>Lower-priced option</span><strong>${esc(item.recommended_tool || 'Unavailable')}</strong>${item.potential_monthly_savings == null ? '' : `<small>Difference: ${formatMoney(item.potential_monthly_savings)}</small>`}</div></article>`; }

async function renderNegotiation() {
  shell(loading('Loading tools…'));
  try {
    const tools = await api.tools(); state.tools = tools;
    if (!tools.length) return shell(empty('Add tools and pricing to the backend before starting a negotiation.'));
    shell(`<div class="panel"><div class="section-heading"><div><h2>Start a negotiation</h2><p>Choose a tool and set your budget. The backend will run and save the negotiation.</p></div></div><form id="negotiation-form" class="form-grid"><label>Tool<select name="tool_name" required>${tools.map((t) => `<option value="${esc(t.name)}">${esc(t.name)}</option>`).join('')}</select></label><label>Your monthly budget<input name="buyer_budget" type="number" min="1" step="0.01" placeholder="e.g. 2500" required /></label><label>Maximum discount<input name="max_discount_percent" type="number" min="0" max="50" value="20" /></label><label>Maximum rounds<input name="max_rounds" type="number" min="1" max="20" value="6" /></label><label class="wide">Required features <span class="label-hint">Optional, separate items with commas</span><input name="required_features" placeholder="e.g. SSO, audit logs, analytics" /></label><div class="form-action"><button class="button primary" type="submit">Start negotiation <span>→</span></button></div></form><div id="negotiation-result">${state.negotiation ? renderNegotiationResult(state.negotiation) : ''}</div></div>`);
    document.querySelector('#negotiation-form').addEventListener('submit', async (event) => {
      event.preventDefault(); const form = new FormData(event.currentTarget); const result = document.querySelector('#negotiation-result');
      const body = { tool_name: form.get('tool_name'), buyer_budget: Number(form.get('buyer_budget')), max_discount_percent: Number(form.get('max_discount_percent') || 20), max_rounds: Number(form.get('max_rounds') || 6), required_features: String(form.get('required_features') || '').split(',').map((x) => x.trim()).filter(Boolean) };
      result.innerHTML = loading('Negotiation agents are working…');
      try { state.negotiation = await api.negotiate(body); result.innerHTML = renderNegotiationResult(state.negotiation); }
      catch (error) { result.innerHTML = errorBox(error, () => document.querySelector('#negotiation-form').requestSubmit()); bindRetry(() => document.querySelector('#negotiation-form').requestSubmit()); }
    });
  } catch (error) { shell(errorBox(error, renderNegotiation)); bindRetry(renderNegotiation); }
}
function renderNegotiationResult(data) {
  const amount = data.final_price == null ? 'No final price' : formatMoney(data.final_price,data.currency);
  return `<div class="neg-result"><div class="result-heading"><div><span class="eyebrow">NEGOTIATION RESULT · #${esc(data.negotiation_id)}</span><h3>${esc(data.tool_name)} <span class="pill">${esc(data.status)}</span></h3></div><strong class="final-price">${amount}</strong></div><div class="result-summary"><div><span>Base price</span><strong>${formatMoney(data.base_price,data.currency)}</strong></div><div><span>Buyer budget</span><strong>${formatMoney(data.buyer_budget,data.currency)}</strong></div><div><span>Savings</span><strong>${data.savings_percent == null ? '—' : `${esc(data.savings_percent)}%`}</strong></div><div><span>Deal score</span><strong>${data.deal_score == null ? '—' : esc(data.deal_score)}</strong></div></div>${data.history?.length ? `<h4>Negotiation activity</h4><ol class="history-list">${data.history.map((item) => `<li><span>${esc(item.agent || 'Agent')}</span><strong>${esc(item.action || 'Action')}</strong>${item.offer == null ? '' : `<span>${formatMoney(item.offer,data.currency)}</span>`}</li>`).join('')}</ol>` : ''}</div>`;
}

window.addEventListener('hashchange', () => renderPage(location.hash.slice(1) || 'overview'));
renderPage(location.hash.slice(1) || 'overview');
