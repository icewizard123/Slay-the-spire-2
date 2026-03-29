const test = require('node:test');
const assert = require('node:assert/strict');

const {
  INFLUENCE_MAX,
  INFLUENCE_MIN,
  InfluenceResource,
} = require('../src/exiled_prince/influenceResource');
const { InfluenceHUD } = require('../src/exiled_prince/influenceHUD');

function createEventBusRecorder() {
  const events = [];
  return {
    events,
    emit(name, payload) {
      events.push({ name, payload });
    },
  };
}

test('Influence clamps between 0 and 10 on gain/spend', () => {
  const model = new InfluenceResource({ ownerId: 'player' });

  model.gainInfluence(100);
  assert.equal(model.current, INFLUENCE_MAX);

  const spent = model.spendInfluence(999);
  assert.equal(spent, false);
  assert.equal(model.current, INFLUENCE_MAX);

  model.spendInfluence(10);
  assert.equal(model.current, INFLUENCE_MIN);
});

test('canSpendInfluence reflects available value', () => {
  const model = new InfluenceResource({ ownerId: 'player', initialValue: 3 });

  assert.equal(model.canSpendInfluence(2), true);
  assert.equal(model.canSpendInfluence(3), true);
  assert.equal(model.canSpendInfluence(4), false);
  assert.equal(model.canSpendInfluence(-1), false);
});

test('gain/spend emit event bus payloads per contract', () => {
  const eventBus = createEventBusRecorder();
  const model = new InfluenceResource({
    ownerId: 'player',
    eventBus,
    clock: () => 12345,
    frameProvider: () => 77,
  });

  const gained = model.gainInfluence(4, 'card:TACTICAL_BRIEFING', ['card', 'resource']);
  assert.equal(gained, 4);

  const spent = model.spendInfluence(2, 'card:COMPEL', ['card', 'resource']);
  assert.equal(spent, true);

  assert.equal(eventBus.events.length, 2);

  const gainEvent = eventBus.events[0];
  assert.equal(gainEvent.name, 'OnInfluenceGained');
  assert.deepEqual(gainEvent.payload, {
    source_id: 'card:TACTICAL_BRIEFING',
    target_id: 'player',
    event_type: 'OnInfluenceGained',
    value: 4,
    tags: ['card', 'resource'],
    timestamp: 12345,
    combat_seed_frame: 77,
  });

  const spendEvent = eventBus.events[1];
  assert.equal(spendEvent.name, 'OnInfluenceSpent');
  assert.deepEqual(spendEvent.payload, {
    source_id: 'card:COMPEL',
    target_id: 'player',
    event_type: 'OnInfluenceSpent',
    value: 2,
    tags: ['card', 'resource'],
    timestamp: 12345,
    combat_seed_frame: 77,
  });
});

test('HUD updates immediately when influence value changes', () => {
  const frames = [];
  const model = new InfluenceResource({ ownerId: 'player' });
  const hud = new InfluenceHUD({
    influenceResource: model,
    render: (frame) => frames.push(frame),
  });

  assert.equal(frames.at(-1).text, 'Influence 0/10');

  model.gainInfluence(3);
  assert.equal(frames.at(-1).text, 'Influence 3/10');

  model.spendInfluence(2);
  assert.equal(frames.at(-1).text, 'Influence 1/10');

  hud.destroy();
});

test('save/load preserves current influence', () => {
  const model = new InfluenceResource({ ownerId: 'player' });
  model.gainInfluence(7);

  const snapshot = model.toSaveSnapshot();
  const restored = new InfluenceResource({ ownerId: 'player', initialValue: 0 });
  restored.loadFromSnapshot(snapshot);

  assert.equal(restored.current, 7);
});
