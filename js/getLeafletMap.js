(function (){
    var lyrs = [];
    var groupedLyrs = [];
    for (var key in window) {
        var value = window[key];
        if (value instanceof L.Map) {
            var map = value;
            var layers = map._layers;
            for (var lyr in layers) {
                var layer = layers[lyr];
                if (layer instanceof L.LayerGroup) {
                    var group = layer;
                    group.eachLayer(function(layer) {
                        groupedLyrs.push(group.getLayerId(layer));
                    })
                }
            }
            for (var lyr in layers) {
                var layer = layers[lyr];
                if (groupedLyrs.indexOf(layer._leaflet_id) != -1) {
                    // Skip members of feature collections
                } else if (layer instanceof L.TileLayer.WMS) {
                    var wmsLyr = getTiledLayer(layer);
                    lyrs.push(['wms', wmsLyr[0], wmsLyr[1], map.options.crs.code]);
                } else if (layer instanceof L.TileLayer) {
                    var xyzLyr = getTiledLayer(layer);
                    lyrs.push(['xyz', xyzLyr[0], xyzLyr[1]]);
                } else if (layer instanceof L.LayerGroup) {
                    geojsonLyr = getJSON(layer);
                    lyrStyle = getStyle(layer);
                    lyrs.push(['vector', geojsonLyr, lyrStyle]);
                } else if (!(layer instanceof L.SVG)) {
                    lyrs.push(['vector', getJSON(layer)]);
                } else {
                    console.log('other');
                }
            }
        }
    }
    return lyrs;
}());

function getTiledLayer(lyr) {
    var url = lyr._url;
    var options = lyr.options;
    return [url, options];
}

function getJSON(lyr) {
    var geoJSON = lyr.toGeoJSON();
    var serializedGeoJSON = JSON.stringify(geoJSON);
    return serializedGeoJSON;
}

function getStyle(layer) {
    var options = layer.options;
    var style = options['style'];
    var styleString = String(style);
    var ast = esprima.parse(styleString);
    return ast;
}