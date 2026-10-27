import test from 'node:test';
import assert from 'node:assert/strict';

function node(data = {}, value = '') {
  const attrs = {};
  const listeners = new Map();
  const classes = new Set();
  return {
    dataset: data,
    textContent: value,
    value: '',
    attrs,
    tagName: 'DIV',
    getAttribute(key) { return attrs[key] ?? ''; },
    setAttribute(key, val) { attrs[key] = String(val); },
    classList: {
      toggle(name, active) { if (active) classes.add(name); else classes.delete(name); },
      contains(name) { return classes.has(name); },
    },
    addEventListener(type, fn) { listeners.set(type, fn); },
    emit(type, payload) {
      assert.ok(listeners.has(type), `no listener for ${type}`);
      listeners.get(type)(payload);
    },
    focus() { globalThis.document.activeElement = this; },
    querySelectorAll(selector) {
      assert.equal(selector, 'li[data-showroom-group]');
      return this.listEntries;
    },
  };
}

function fixture() {
  const numbers = [5, 5, 5, 4, 4, 4, 3];
  const screens = [];
  const entries = [];
  const groups = [];
  for (let lane = 0; lane < 7; lane++) {
    const group = node();
    group.listEntries = [];
    for (let item = 0; item < numbers[lane]; item++) {
      const status = lane === 1 ? 'planned' : 'public';
      const data = { showroomGroup: String(lane), showroomState: status };
      const content = lane === 1 ? `Agent challenge ${item}` : `Evidence ${lane} item ${item}`;
      const screen = node(data, content);
      screen.setAttribute('aria-label', content);
      screens.push(screen);
      const entry = node(data, content);
      entries.push(entry);
      group.listEntries.push(entry);
    }
    groups.push(group);
  }
  const statusButtons = ['all','public','planned'].map(ebStatus => node({ ebStatus }));
  const groupButtons = ['all','0','1','2','3','4','5','6'].map(ebGroup => node({ ebGroup }));
  const root = node(), search = node(), counter = node(), stage = node();
  const sidebar = node(), mobile = node();
  const selectors = new Map([
    ['#eb-showroom', root], ['#eb-search', search], ['#eb-total', counter],
    ['#eb-stage', stage], ['.eb-side', sidebar], ['#eb-mobile-list', mobile],
  ]);
  const selectAll = new Map([
    ['.eb-display[data-showroom-group]', screens],
    ['.eb-list-group li[data-showroom-group]', entries],
    ['.eb-list-group', groups],
    ['[data-eb-status]', statusButtons],
    ['[data-eb-group]', groupButtons],
  ]);
  const keyListeners = new Map();
  globalThis.document = {
    activeElement: null,
    querySelector(selector) { return selectors.get(selector) ?? null; },
    querySelectorAll(selector) { return selectAll.get(selector) ?? []; },
    addEventListener(type, fn) { keyListeners.set(type, fn); },
    keyDown(key) {
      const event = { key, preventDefault() { this.prevented = true; } };
      keyListeners.get('keydown')(event);
      return event;
    },
  };
  return { screens, entries, groups, statusButtons, groupButtons,
           root, search, counter, stage, sidebar, mobile };
}

test('30 screens and 7 aisles filter by group/status and remain in place', async () => {
  const f = fixture();
  await import('../site/showroom.mjs?case=filters');
  assert.equal(f.counter.textContent, '30 / 30');
  f.statusButtons[2].emit('click');
  assert.equal(f.counter.textContent, '5 / 30');
  assert.equal(f.screens.filter(x => x.classList.contains('eb-dimmed')).length, 25);
  assert.equal(f.entries.filter(x => x.classList.contains('eb-filtered-out')).length, 25);
  assert.equal(f.statusButtons[2].attrs['aria-pressed'], 'true');
  f.groupButtons[2].emit('click');
  assert.equal(f.counter.textContent, '5 / 30');
  f.groupButtons[3].emit('click');
  assert.equal(f.counter.textContent, '0 / 30');
  f.statusButtons[0].emit('click');
  assert.equal(f.counter.textContent, '5 / 30');
  f.groupButtons[0].emit('click');
  assert.equal(f.counter.textContent, '30 / 30');
  assert.equal(f.screens.filter(x => x.classList.contains('eb-dimmed')).length, 0);
});

test('search and / shortcut expose accessible list; Escape dismisses', async () => {
  const f = fixture();
  await import('../site/showroom.mjs?case=access');
  f.search.value = 'Agent challenge 3';
  f.search.emit('input');
  assert.equal(f.counter.textContent, '1 / 30');
  f.search.value = '';
  f.search.emit('input');
  assert.equal(f.counter.textContent, '30 / 30');
  const key = globalThis.document.keyDown('/');
  assert.equal(key.prevented, true);
  assert.equal(f.sidebar.classList.contains('eb-open'), true);
  assert.equal(f.mobile.attrs['aria-expanded'], 'true');
  assert.equal(globalThis.document.activeElement, f.search);
  globalThis.document.keyDown('Escape');
  assert.equal(f.sidebar.classList.contains('eb-open'), false);
  assert.equal(f.mobile.attrs['aria-expanded'], 'false');
});

test('unavailable DOM parts cause safe no-op rather than partial behavior', async () => {
  fixture();
  globalThis.document.querySelectorAll = () => [];
  await import('../site/showroom.mjs?case=incomplete');
});
