class InfluenceHUD {
  constructor({ influenceResource, render }) {
    if (!influenceResource || typeof influenceResource.subscribe !== 'function') {
      throw new Error('InfluenceHUD requires a subscribable influenceResource');
    }

    if (typeof render !== 'function') {
      throw new Error('InfluenceHUD requires a render callback');
    }

    this._render = render;
    this._unsubscribe = influenceResource.subscribe(({ current, max }) => {
      this._render(this._format(current, max));
    });
  }

  destroy() {
    if (this._unsubscribe) {
      this._unsubscribe();
      this._unsubscribe = null;
    }
  }

  _format(current, max) {
    return {
      label: 'Influence',
      current,
      max,
      text: `Influence ${current}/${max}`,
    };
  }
}

module.exports = {
  InfluenceHUD,
};
