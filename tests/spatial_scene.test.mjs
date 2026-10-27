import test from 'node:test';
import assert from 'node:assert/strict';

function classList() {
  const items = new Set();
  return {
    toggle(name, enabled) {
      if (enabled) items.add(name);
      else items.delete(name);
    },
    contains: (name) => items.has(name),
  };
}

function element(dataset = {}) {
  const callbacks = new Map();
  const attributes = {};
  return {
    dataset, classList: classList(), hidden: false, textContent: '',
    attributes,
    setAttribute(key, value) { attributes[key] = value; },
    addEventListener(name, fn) { callbacks.set(name, fn); },
    click() {
      const callback = callbacks.get('click');
      assert.ok(callback, 'real click handler must be installed');
      callback();
    },
  };
}

function fixture() {
  const screens = [
    ...Array.from({ length: 3 }, () => element({ spatialCategory: 'service' })),
    ...Array.from({ length: 3 }, () => element({ spatialCategory: 'evidence' })),
    ...Array.from({ length: 3 }, () => element({ spatialCategory: 'research' })),
  ];
  const rows = screens.map(s => element({ spatialCategory: s.dataset.spatialCategory }));
  const filters = ['all', 'service', 'evidence', 'research'].map(
    spatialFilter => element({ spatialFilter })
  );
  const scene = element();
  const directory = element();
  directory.hidden = true;
  const toggle = element();
  const count = element();
  const body = element();

  globalThis.document = {
    body,
    querySelector(selector) {
      return new Map([
        ['#spatial-scene', scene],
        ['#spatial-directory', directory],
        ['#spatial-mode', toggle],
        ['#spatial-count', count],
      ]).get(selector) ?? null;
    },
    querySelectorAll(selector) {
      return new Map([
        ['.spatial-monitor[data-spatial-category]', screens],
        ['#spatial-directory tr[data-spatial-category]', rows],
        ['button[data-spatial-filter]', filters],
      ]).get(selector) ?? [];
    },
  };
  return { screens, rows, filters, scene, directory, toggle, count, body };
}

test('spatial browse filters dim rather than remove scene screens, and list shows selected links', async () => {
  const h = fixture();
  await import('../site/spatial.mjs?test=filter');
  assert.equal(h.count.textContent, '9 / 9 displays');
  assert.equal(h.scene.hidden, false);
  assert.equal(h.directory.hidden, true);
  assert.equal(h.filters[0].attributes['aria-pressed'], 'true');

  h.filters[2].click();
  assert.equal(h.count.textContent, '3 / 9 displays');
  assert.equal(h.screens.filter(s => s.classList.contains('is-muted')).length, 6);
  assert.equal(h.filters[2].attributes['aria-pressed'], 'true');
  assert.equal(h.filters[0].attributes['aria-pressed'], 'false');
  assert.equal(h.rows.filter(r => r.hidden).length, 6);

  h.toggle.click();
  assert.equal(h.scene.hidden, true);
  assert.equal(h.directory.hidden, false);
  assert.equal(h.toggle.attributes['aria-expanded'], 'true');
  assert.equal(h.toggle.textContent, 'Spatial view');
  assert.equal(h.body.classList.contains('spatial-list-open'), true);

  h.filters[0].click();
  assert.equal(h.rows.filter(r => r.hidden).length, 0);
  assert.equal(h.count.textContent, '9 / 9 displays');

  h.toggle.click();
  assert.equal(h.scene.hidden, false);
  assert.equal(h.directory.hidden, true);
  assert.equal(h.toggle.attributes['aria-expanded'], 'false');
  assert.equal(h.body.classList.contains('spatial-list-open'), false);
});

test('malformed scene does not crash or alter native screen links', async () => {
  const h = fixture();
  globalThis.document.querySelectorAll = () => [];
  await import('../site/spatial.mjs?test=malformed');
  assert.equal(h.scene.hidden, false);
  assert.equal(h.directory.hidden, true);
  assert.equal(h.toggle.textContent, '');
});
