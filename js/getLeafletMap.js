(function (){
    lyrs = []
    for(var key in window) {
        var value = window[key];
        if (value instanceof L.Map) {
            for(var lyr in value._layers) {
                if (value._layers[lyr] instanceof L.TileLayer) {
                    console.log('tile');
                    xyzLyr = getXYZ(value._layers[lyr]);
                    lyrs.push(['xyz', xyzLyr[0], xyzLyr[1]]);
                } else if (value._layers[lyr] instanceof L.Path) {
                    console.log('vector');
                    lyrs.push(['vector', getJSON(value._layers[lyr])]);
                } else {
                    console.log('other');
                    console.log(value._layers[lyr]);
                }
            }
        }
    }
    return lyrs;
}());

function getXYZ(lyr) {
    return [lyr._url, lyr.options];
}

function getMarker(lyr) {
    return lyr._latlng;
}

function getPolyline(lyr) {
    return lyr._latlngs;
}

function getJSON(lyr) {
    return JSON.stringify(lyr.toGeoJSON());
}
