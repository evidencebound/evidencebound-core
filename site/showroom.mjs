/* EvidenceBound original showroom controls; no external dependencies.
   Native anchors, HTML headings and canonical metadata work without JS. */
const root = document.querySelector('#eb-showroom');
const search = document.querySelector('#eb-search');
const counter = document.querySelector('#eb-total');
const stage = document.querySelector('#eb-stage');
const sidebar = document.querySelector('.eb-side');
const mobile = document.querySelector('#eb-mobile-list');
const screens = [...document.querySelectorAll('.eb-display[data-showroom-group]')];
const listEntries = [...document.querySelectorAll('.eb-list-group li[data-showroom-group]')];
const groups = [...document.querySelectorAll('.eb-list-group')];
const statusButtons = [...document.querySelectorAll('[data-eb-status]')];
const groupButtons = [...document.querySelectorAll('[data-eb-group]')];
const nightButtons = [...document.querySelectorAll('[data-eb-night-toggle]')];

if (root && search && counter && stage && sidebar && mobile &&
    screens.length === 30 && listEntries.length === 30 &&
    statusButtons.length === 3 && groupButtons.length === 8) {
  let chosenStatus = 'all';
  let chosenGroup = 'all';

  function isMatch(el, needle) {
    const groupMatches = chosenGroup === 'all' || el.dataset.showroomGroup === chosenGroup;
    const statusMatches = chosenStatus === 'all' || el.dataset.showroomState === chosenStatus;
    const textMatches = !needle || (el.textContent || '').toLocaleLowerCase().includes(needle) ||
      (el.getAttribute('aria-label') || '').toLocaleLowerCase().includes(needle);
    return groupMatches && statusMatches && textMatches;
  }

  function apply() {
    const needle = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const screen of screens) {
      const match = isMatch(screen, needle);
      screen.classList.toggle('eb-dimmed', !match);
      screen.setAttribute('aria-label',
        screen.getAttribute('aria-label')?.replace(/ \[filtered\]$/, '') +
        (!match ? ' [filtered]' : ''));
      if (match) count++;
    }
    for (const item of listEntries) {
      item.classList.toggle('eb-filtered-out', !isMatch(item, needle));
    }
    for (const group of groups) {
      group.classList.toggle('eb-filtered-empty',
        ![...group.querySelectorAll('li[data-showroom-group]')].some(
          item => !item.classList.contains('eb-filtered-out')
        ));
    }
    for (const button of statusButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.ebStatus === chosenStatus));
    }
    for (const button of groupButtons) {
      button.setAttribute('aria-pressed', String(button.dataset.ebGroup === chosenGroup));
    }
    counter.textContent = `${count} / ${screens.length}`;
  }

  for (const button of statusButtons) {
    button.addEventListener('click', () => {
      chosenStatus = button.dataset.ebStatus;
      apply();
    });
  }
  for (const button of groupButtons) {
    button.addEventListener('click', () => {
      chosenGroup = button.dataset.ebGroup;
      apply();
    });
  }
  for (const button of nightButtons) {
    button.addEventListener('click', () => {
      const next = !document.body.classList.contains('eb-night');
      document.body.classList.toggle('eb-night', next);
      for (const peer of nightButtons) {
        peer.setAttribute('aria-pressed', String(next));
        peer.textContent = next ? 'Day view' : 'Night view';
      }
    });
  }
  search.addEventListener('input', apply);

  function openList(shouldOpen) {
    sidebar.classList.toggle('eb-open', shouldOpen);
    mobile.setAttribute('aria-expanded', String(shouldOpen));
    mobile.textContent = shouldOpen ? 'Close list' : 'List · 30';
    if (shouldOpen) search.focus();
  }
  mobile.addEventListener('click', () => {
    openList(!sidebar.classList.contains('eb-open'));
  });
  document.addEventListener('keydown', event => {
    const editable = document.activeElement &&
      ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);
    if (event.key === '/' && !editable) {
      event.preventDefault();
      openList(true);
      search.focus();
    }
    if (event.key === 'Escape') {
      if (sidebar.classList.contains('eb-open')) {
        openList(false);
        mobile.focus();
      } else if (editable && search.value) {
        search.value = '';
        apply();
      }
    }
  });
  apply();
}
