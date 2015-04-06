/* Copyright (c) 2006-2012 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the 2-clause BSD license.
 * See license.txt in the OpenLayers distribution or repository for the
 * full text of the license. */

/**
 * @requires OpenLayers/Layer/XYZ.js
 * http://emap.ngii.go.kr:8082/proxy/proxy.jsp?url=http://210.117.198.62:8081/korean_map_tile/L${z}/${x}/${y}.png
 * http://emap.ngii.go.kr:8082/proxy/proxy.jsp?url=http://210.117.198.62:8081/korean_map_tile/L12/167/3828.png
 */

OpenLayers.Layer.NgiiStreet = OpenLayers.Class(OpenLayers.Layer.XYZ, {

    name: "NgiiStreet", 
    url: [
    "http://emap.ngii.go.kr:8082/proxy/proxy.jsp?url=http://210.117.198.62:8081/korean_map_tile/L${z}/${x}/${y}.png"
    ],
  resolutions: [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25],
  attribution: '<a href="http://emap.ngii.go.kr:8082/" target="_blank" style="text-decoration: none !important;"><span style="display: inline; font-family: Tahoma,sans-serif !important; font-size: 9px !important; font-weight: bold !important; font-style: normal !important; color: #009BC8 !important; text-decoration: none !important;">'
    + '바로e맵©2015</span></a>',
  sphericalMercator: false,
  buffer: 0,
  numZoomLevels: 14,
  minResolution: 0.25,
  maxResolution: 1954.597389,
  units: "m",
  projection: new OpenLayers.Projection("EPSG:9020203"),
  displayOutsideMaxExtent: false,
  maxExtent: new OpenLayers.Bounds(-200000.0, -28024123.62 , 31824123.62, 4000000.0),
    initialize: function(name, options) {
    if (!options) options = {resolutions: [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25]};
    else if (!options.resolutions) options.resolutions = [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25];
        var newArgs = [name, null, options];
        OpenLayers.Layer.XYZ.prototype.initialize.apply(this, newArgs);
    },
    clone: function(obj) {
        if (obj == null) {
            obj = new OpenLayers.Layer.NgiiStreet(
                this.name, this.getOptions());
        }
        obj = OpenLayers.Layer.XYZ.prototype.clone.apply(this, [obj]);
        return obj;
    },

  getXYZ: function(bounds) {
        var res = this.getServerResolution();
        var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round((bounds.bottom - this.maxExtent.bottom) / (res * this.tileSize.h));
        var z = this.getServerZoom() + 6;
        z = this.fillzero(z, 2);

        if (this.wrapDateLine) {
            var limit = Math.pow(2, z);
            x = ((x % limit) + limit) % limit;
        }

        return {'x': x, 'y': y, 'z': z};
    },
    
    fillzero: function(n, digits) { 
        var zero = '';
        n = n.toString();
        if (digits > n.length) {
          for (var i = 0; digits - n.length > i; i++) {
            zero += '0';
          }
        }
      return zero + n;
    },
      
    CLASS_NAME: "OpenLayers.Layer.NgiiStreet"
});
