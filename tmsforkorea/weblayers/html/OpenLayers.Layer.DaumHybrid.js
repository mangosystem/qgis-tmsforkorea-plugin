/* Copyright (c) 2006-2012 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the 2-clause BSD license.
 * See license.txt in the OpenLayers distribution or repository for the
 * full text of the license. */

/**
 * @requires OpenLayers/Layer/XYZ.js
 */

OpenLayers.Layer.DaumHybrid = OpenLayers.Class(OpenLayers.Layer.XYZ, {

    name: "Kakao Hybrid Map",
    url: [
    "http://map0.daumcdn.net/map_hybrid/2012tlq/L${z}/${y}/${x}.png",
    "http://map1.daumcdn.net/map_hybrid/2012tlq/L${z}/${y}/${x}.png",
    "http://map2.daumcdn.net/map_hybrid/2012tlq/L${z}/${y}/${x}.png",
    "http://map3.daumcdn.net/map_hybrid/2012tlq/L${z}/${y}/${x}.png"
    ],
  resolutions: [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25],
  attribution: '<a target="_blank" href="http://map.kakao.com/" title="Kakao 지도로 보시려면 클릭하세요." style="float: left; width: 32px; height: 10px;">'
    + '<img style="float: left; width: 32px; height: 10px; border: medium none;" src="https://t1.daumcdn.net/mapjsapi/images/2x/m_bi_b.png" alt="Kakao 지도로 이동"></a>',
  sphericalMercator: false,
  buffer: 1,
  numZoomLevels: 14,
  minResolution: 0.25,
  maxResolution: 2048,
  units: "m",
  projection: new OpenLayers.Projection("EPSG:5181"),
  displayOutsideMaxExtent: true,
  maxExtent: new OpenLayers.Bounds(-30000, -60000, 494288, 988576),
    initialize: function(name, options) {
    if (!options) options = {resolutions: [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25]};
    else if (!options.resolutions) options.resolutions = [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25];
        var newArgs = [name, null, options];
        OpenLayers.Layer.XYZ.prototype.initialize.apply(this, newArgs);
    },
    clone: function(obj) {
        if (obj == null) {
            obj = new OpenLayers.Layer.DaumHybrid(
                this.name, this.getOptions());
        }
        obj = OpenLayers.Layer.XYZ.prototype.clone.apply(this, [obj]);
        return obj;
    },

  getXYZ: function(bounds) {
        var res = this.getServerResolution();
        var x = Math.round((bounds.left - this.maxExtent.left) /
            (res * this.tileSize.w));
        var y = Math.round((bounds.bottom - this.maxExtent.bottom) /
            (res * this.tileSize.h));
        var z = this.numZoomLevels - this.getServerZoom();

        if (this.wrapDateLine) {
            var limit = Math.pow(2, z);
            x = ((x % limit) + limit) % limit;
        }

        return {'x': x, 'y': y, 'z': z};
    },
  
    CLASS_NAME: "OpenLayers.Layer.DaumHybrid"
});
