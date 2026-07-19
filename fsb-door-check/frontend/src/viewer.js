// xeokit viewer 封装 — IFC 加载 + 拾取 + 高亮 + X-ray + 楼层隔离
// 对应 docs/CONTRACT.md §5 高亮映射规则
// xeokit 2.6.x 用 WebIFCLoaderPlugin + ES module 本地加载(绕开 CDN Tracking Prevention)

import * as xeokit from '../lib/xeokit-sdk.es.min.js';

const STATUS_COLORS = {
  pass:       [0.133, 0.773, 0.369],
  fail:       [0.937, 0.267, 0.267],
  unknown:    [0.918, 0.702, 0.031],
  overridden: [0.231, 0.510, 0.965],
};

const XEOKIT_WASM_PATH = '/lib/';

export class IfcViewer {
  constructor(canvasId) {
    this.canvasId = canvasId;
    if (!xeokit || !xeokit.Viewer) {
      throw new Error('xeokit SDK not loaded (import failed). Check /lib/xeokit-sdk.es.min.js');
    }
    if (!xeokit.WebIFCLoaderPlugin) {
      throw new Error('xeokit.WebIFCLoaderPlugin not found in this xeokit version.');
    }
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      throw new Error(`canvas #${canvasId} not found in DOM`);
    }
    this.viewer = new xeokit.Viewer({
      canvasId,
      transparent: true,
    });
    this.scene = this.viewer.scene;
    this.cameraFlight = this.viewer.cameraFlight;
    this._doorIds = new Set();
    this._storeyIds = new Set();
    this.onPick = null;
    this._setupPicking();
  }

  async loadIfcUrl(url) {
    console.log('[viewer] loadIfcUrl start, url=', url);
    let webIFCLoader;
    try {
      webIFCLoader = new xeokit.WebIFCLoaderPlugin(this.viewer, {
        wasmPath: XEOKIT_WASM_PATH,
      });
      console.log('[viewer] WebIFCLoaderPlugin created');
    } catch (e) {
      console.error('[viewer] WebIFCLoaderPlugin ctor failed:', e);
      throw new Error(`WebIFCLoaderPlugin ctor: ${e.message}`);
    }
    let model;
    try {
      model = webIFCLoader.load({ id: 'ifcModel', src: url, edges: true });
      console.log('[viewer] load() returned, typeof=', typeof model,
        'isPromise=', !!(model && typeof model.then === 'function'),
        'hasOn=', !!(model && typeof model.on === 'function'),
        'loaded=', !!(model && model.loaded));
    } catch (e) {
      console.error('[viewer] load() threw:', e);
      throw new Error(`WebIFCLoaderPlugin.load threw: ${e.message}`);
    }
    if (model && typeof model.then === 'function') {
      console.log('[viewer] awaiting model promise...');
      try {
        await model;
        console.log('[viewer] await model done');
      } catch (e) {
        console.error('[viewer] await model failed:', e);
        throw new Error(`await model: ${e.message || e}`);
      }
    } else if (model && typeof model.on === 'function') {
      console.log('[viewer] waiting for model.on("loaded")...');
      await new Promise((resolve, reject) => {
        let settled = false;
        const done = () => { if (!settled) { settled = true; resolve(); } };
        if (model.loaded) { console.log('[viewer] model already loaded'); done(); return; }
        model.on('loaded', () => { console.log('[viewer] model loaded event'); done(); });
        model.on('error', (err) => {
          console.error('[viewer] model error event:', err);
          if (!settled) { settled = true; reject(new Error(`model load error: ${err}`)); }
        });
        setTimeout(() => { if (!settled) { console.warn('[viewer] load timeout 30s, continuing'); done(); } }, 30000);
      });
    } else {
      console.warn('[viewer] model is neither Promise nor EventEmitter, assuming sync load');
    }
    try {
      this._indexDoorsAndStoreys();
    } catch (e) {
      console.warn('[viewer] _indexDoorsAndStoreys error:', e);
    }
    try {
      if (this.viewer.cameraFlight && typeof this.viewer.cameraFlight.flyTo === 'function') {
        this.viewer.cameraFlight.flyTo(this.viewer.scene);
        console.log('[viewer] flyTo done');
      } else {
        console.warn('[viewer] cameraFlight.flyTo not available');
      }
    } catch (e) {
      console.warn('[viewer] flyTo error:', e);
    }
    const objCount = Object.keys(this.viewer.scene.objects).length;
    console.log('[viewer] loadIfcUrl done, scene.objects count=', objCount);
    if (objCount === 0) {
      console.error('[viewer] WARNING: no objects in scene after load — IFC parsing likely failed');
    }
  }

  _indexDoorsAndStoreys() {
    this._doorIds = new Set();
    this._storeyIds = new Set();
    const metaScene = this.viewer.metaScene;
    const metaObjects = metaScene ? metaScene.metaObjects : null;
    const objects = this.viewer.scene.objects;
    for (const id in objects) {
      const meta = metaObjects && metaObjects[id];
      if (meta) {
        if (meta.type === 'IfcDoor') this._doorIds.add(id);
        if (meta.type === 'IfcBuildingStorey') this._storeyIds.add(id);
      }
    }
    console.log(`[viewer] indexed ${this._doorIds.size} doors, ${this._storeyIds.size} storeys, ${Object.keys(objects).length} total objects`);
  }

  _setupPicking() {
    const input = (this.scene && this.scene.input) || this.viewer.input;
    if (!input || typeof input.on !== 'function') {
      console.warn('[viewer] input not available (xeokit 2.x API), picking disabled');
      return;
    }
    input.on('mouseclicked', (coords) => {
      const hit = this.viewer.scene.pick({ canvasPos: coords });
      if (hit && hit.entity && hit.entity.id) {
        const gid = hit.entity.id;
        if (this.onPick) this.onPick(gid);
      }
    });
  }

  getDoorIds() {
    return Array.from(this._doorIds);
  }

  setNonDoorsXrayed(alpha = 0.5) {
    const objects = this.viewer.scene.objects;
    for (const id in objects) {
      const obj = objects[id];
      if (!this._doorIds.has(id)) {
        obj.xrayed = true;
        if (obj.xrayMaterial) obj.xrayMaterial.alpha = alpha;
      } else {
        obj.xrayed = false;
      }
    }
  }

  colorizeByStatus(results) {
    for (const r of results) {
      const gid = r.door_global_id;
      const status = r.status;
      const obj = this.viewer.scene.objects[gid];
      if (!obj) continue;
      const color = STATUS_COLORS[status];
      if (!color) continue;
      obj.colorize = color;
      if (status === 'pass') {
        obj.xrayed = true;
        if (obj.xrayMaterial) obj.xrayMaterial.alpha = 0.3;
      } else {
        obj.xrayed = false;
      }
    }
  }

  resetDoorColors() {
    for (const id of this._doorIds) {
      const obj = this.viewer.scene.objects[id];
      if (obj) {
        obj.colorize = null;
        obj.xrayed = true;
        if (obj.xrayMaterial) obj.xrayMaterial.alpha = 0.3;
      }
    }
  }

  highlightDoor(globalId) {
    const obj = this.viewer.scene.objects[globalId];
    if (obj) {
      obj.selected = true;
      obj.xrayed = false;
    }
  }

  unhighlightAll() {
    for (const id in this.viewer.scene.objects) {
      this.viewer.scene.objects[id].selected = false;
    }
  }

  flyTo(globalId) {
    const obj = this.viewer.scene.objects[globalId];
    if (obj) {
      this.viewer.cameraFlight.flyTo([obj]);
    }
  }

  isolateStorey(storeyId) {
    const metaScene = this.viewer.metaScene;
    const metaObjects = metaScene ? metaScene.metaObjects : null;
    const objects = this.viewer.scene.objects;
    const visibleIds = new Set();
    if (storeyId !== null && metaObjects) {
      const collect = (parentId) => {
        visibleIds.add(parentId);
        const children = metaObjects[parentId];
        if (children && children.children) {
          for (const c of children.children) collect(c.id);
        }
      };
      collect(storeyId);
    }
    for (const id in objects) {
      objects[id].visible = (storeyId === null || visibleIds.has(id));
    }
  }

  showAllStoreys() {
    const objects = this.viewer.scene.objects;
    for (const id in objects) {
      objects[id].visible = true;
    }
  }
}

export const STATUS_COLOR_HEX = {
  pass: '#22c55e',
  fail: '#ef4444',
  unknown: '#eab308',
  overridden: '#3b82f6',
};
