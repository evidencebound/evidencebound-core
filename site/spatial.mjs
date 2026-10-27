/* Progressive enhancement for the EvidenceBound spatial display wall.
   Static anchors and all metadata remain available without JavaScript.
   No third-party dependencies, network calls, inline styling or persisted state. */
const scene = document.querySelector('#spatial-scene');
const directory = document.querySelector('#spatial-directory');
const toggle = document.querySelector('#spatial-mode');
const count = document.querySelector('#spatial-count');
const screens = [...document.querySelectorAll('.spatial-monitor[data-spatial-category]')];
const rows = [...document.querySelectorAll('#spatial-directory tr[data-spatial-category]')];
const filters = [...document.querySelectorAll('button[data-spatial-filter]')];

if (scene && directory && toggle && count && screens.length === 9 &&
    rows.length === screens.length && filters.length === 4) {
  let category = 'all';
  let listMode = false;

  function update() {
    let matching = 0;
    for (const screen of screens) {
      const match = category === 'all' || screen.dataset.spatialCategory === category;
      screen.classList.toggle('is-muted', !match);
      // In spatial mode dim instead of hiding screens; physical aisles do not jump.
      if (match) matching++;
    }
    for (const row of rows) {
      row.hidden = category !== 'all' && row.dataset.spatialCategory !== category;
    }
    for (const button of filters) {
      button.setAttribute('aria-pressed', String(button.dataset.spatialFilter === category));
    }
    count.textContent = `${matching} / ${screens.length} displays`;
    scene.hidden = listMode;
    directory.hidden = !listMode;
    toggle.setAttribute('aria-expanded', String(listMode));
    toggle.textContent = listMode ? 'Spatial view' : 'List view';
    document.body.classList.toggle('spatial-list-open', listMode);
  }

  for (const button of filters) {
    button.addEventListener('click', () => {
      category = button.dataset.spatialFilter;
      update();
    });
  }
  toggle.addEventListener('click', () => {
    listMode = !listMode;
    update();
  });
  update();
}
