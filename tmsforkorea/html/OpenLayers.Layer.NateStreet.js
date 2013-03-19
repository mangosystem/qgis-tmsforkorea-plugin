/* Copyright (c) 2006-2012 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the 2-clause BSD license.
 * See license.txt in the OpenLayers distribution or repository for the
 * full text of the license. */

/**
 * @requires OpenLayers/Layer/XYZ.js
 */

OpenLayers.Layer.NateStreet = OpenLayers.Class(OpenLayers.Layer.XYZ, {

    name: "NateStreetMap",
    url: [
        "http://map1.nateimg.co.kr/v3/L${z}/R${y}/C${x}.png?v=20120515",
        "http://map2.nateimg.co.kr/v3/L${z}/R${y}/C${x}.png?v=20120515",
        "http://map3.nateimg.co.kr/v3/L${z}/R${y}/C${x}.png?v=20120515"
    ],
    
    resolutions: [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5],
    attribution: '<a target="_blank" href="http://map.nate.com" '
        + 'style="float: left; width: 65px; height: 25px; cursor: pointer; background-image: url(http://www.tmap.co.kr/tmap2/images/common/logo_tmap.gif); background-repeat: no-repeat no-repeat; " '
        + 'title="Nate 지도로 보시려면 클릭하세요."></a>' 
        + '© SK PLANET',
    
    sphericalMercator: false,
    buffer: 0,
    numZoomLevels: 12,
    minResolution: 0.5,
    maxResolution: 1024,
    units: "m",
    
    // "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 +ellps=bessel +units=m +no_defs +towgs84=-146.43,507.89,681.46"
    projection: new OpenLayers.Projection("EPSG:5178"),
    displayOutsideMaxExtent: false,
    maxExtent: new OpenLayers.Bounds(-400000, -100000, 1000000, 1300000),
    
    initialize: function(name, options) {
        if (!options) options = {resolutions: [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5]};
        else if (!options.resolutions) options.resolutions = [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5];
        var newArgs = [name, null, options];
        OpenLayers.Layer.XYZ.prototype.initialize.apply(this, newArgs);
    },
    
    clone: function(obj) {
        if (obj == null) {
            obj = new OpenLayers.Layer.NateStreet(
                this.name, this.getOptions());
        }
        obj = OpenLayers.Layer.XYZ.prototype.clone.apply(this, [obj]);
        return obj;
    },

    getXYZ: function(bounds) {
        var res = this.getServerResolution();
        var x = Math.floor((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.floor((this.maxExtent.top - bounds.bottom) / (res * this.tileSize.h));
        var z = this.getServerZoom();
        
        /* Naver & Daum
        var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round((bounds.bottom - this.maxExtent.bottom) / (res * this.tileSize.h));
        */
        
        /* Olleh
        var x = Math.floor((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.floor((this.maxExtent.top - bounds.bottom) / (res * this.tileSize.h));
        */
        
        var uz = z > 9 ? z : "0" + z;
        
        var sx = parseInt(x).toString(16);
        var ux = Array(9 - sx.length).join("0") + sx;
        
        var sy = parseInt(y).toString(16);
        var uy = Array(9 - sy.length).join("0") + sy;
        
        return {'x': ux, 'y': uy, 'z': uz};
    },
    
    CLASS_NAME: "OpenLayers.Layer.NateStreet"
});
