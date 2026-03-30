const INFLUENCE_MIN = 0;
const INFLUENCE_MAX = 10;

function clampInfluence(value) {
  if (!Number.isFinite(value)) {
    throw new TypeError(`Influence value must be a finite number, received: ${value}`);
  }

  return Math.min(INFLUENCE_MAX, Math.max(INFLUENCE_MIN, Math.trunc(value)));
}

class InfluenceResource {
  constructor({
    ownerId,
    initialValue = INFLUENCE_MIN,
    eventBus,
    clock = () => Date.now(),
    frameProvider = () => 0,
  } = {}) {
    if (!ownerId) {
      throw new Error('InfluenceResource requires ownerId');
    }

    this.ownerId = ownerId;
    this.max = INFLUENCE_MAX;
    this.min = INFLUENCE_MIN;
    this.current = clampInfluence(initialValue);
    this._eventBus = eventBus;
    this._clock = clock;
    this._frameProvider = frameProvider;
    this._listeners = new Set();
  }

  canSpendInfluence(amount) {
    if (!Number.isFinite(amount) || amount < 0) {
      return false;
    }

    return this.current >= Math.trunc(amount);
  }

  gainInfluence(amount, sourceId = this.ownerId, tags = []) {
    return this._changeInfluence(Math.max(0, Math.trunc(amount)), sourceId, 'OnInfluenceGained', tags);
  }

  spendInfluence(amount, sourceId = this.ownerId, tags = []) {
    const spendAmount = Math.max(0, Math.trunc(amount));
    if (!this.canSpendInfluence(spendAmount)) {
      return false;
    }

    this._changeInfluence(-spendAmount, sourceId, 'OnInfluenceSpent', tags);
    return true;
  }

  toSaveSnapshot() {
    return { influence: this.current };
  }

  loadFromSnapshot(snapshot = {}) {
    this.current = clampInfluence(snapshot.influence ?? INFLUENCE_MIN);
    this._notify();
  }

  subscribe(listener) {
    this._listeners.add(listener);
    listener(this.getViewModel());

    return () => this._listeners.delete(listener);
  }

  getViewModel() {
    return {
      current: this.current,
      max: this.max,
    };
  }

  _changeInfluence(delta, sourceId, eventType, tags) {
    const before = this.current;
    const after = clampInfluence(before + delta);
    const appliedDelta = after - before;

    if (appliedDelta === 0) {
      return 0;
    }

    this.current = after;
    this._notify();
    this._emit({
      source_id: sourceId,
      target_id: this.ownerId,
      event_type: eventType,
      value: Math.abs(appliedDelta),
      tags,
      timestamp: this._clock(),
      combat_seed_frame: this._frameProvider(),
    });

    return appliedDelta;
  }

  _notify() {
    const viewModel = this.getViewModel();
    this._listeners.forEach((listener) => listener(viewModel));
  }

  _emit(payload) {
    if (!this._eventBus || typeof this._eventBus.emit !== 'function') {
      return;
    }

    this._eventBus.emit(payload.event_type, payload);
  }
}

module.exports = {
  INFLUENCE_MIN,
  INFLUENCE_MAX,
  InfluenceResource,
  clampInfluence,
};
