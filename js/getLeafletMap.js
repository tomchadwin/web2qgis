(function (){
    lyrs = [];
    groupedLyrs = [];
    for (var key in window) {
        var value = window[key];
        if (value instanceof L.Map) {
            for (var lyr in value._layers) {
                if (value._layers[lyr] instanceof L.LayerGroup) {
                    value._layers[lyr].eachLayer(function(layer) {
                        groupedLyrs.push(value._layers[lyr].getLayerId(layer));
                    })
                }
            }
            for (var lyr in value._layers) {
                if (groupedLyrs.indexOf(value._layers[lyr]._leaflet_id) != -1) {
                    // Skip members of feature collections
                } else if (value._layers[lyr] instanceof L.TileLayer) {
                    xyzLyr = getXYZ(value._layers[lyr]);
                    lyrs.push(['xyz', xyzLyr[0], xyzLyr[1]]);
                } else if (value._layers[lyr] instanceof L.LayerGroup) {
                    lyrs.push(['vector', getJSON(value._layers[lyr])]);
                } else if (!(value._layers[lyr] instanceof L.SVG)) {
                    lyrs.push(['vector', getJSON(value._layers[lyr])]);
                } else {
                    console.log('other');
                }
            }
        }
    }
    return lyrs;
}());

function getXYZ(lyr) {
    return [lyr._url, lyr.options];
}

function getJSON(lyr) {
    return JSON.stringify(lyr.toGeoJSON());
}
