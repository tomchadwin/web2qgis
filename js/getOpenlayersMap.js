(function (){
    var lyrs = [];
    var groupedLyrs = [];
    for (var key in window) {
        var value = window[key];
        if (value instanceof ol.Map) {
            var map = value;
            var layers = map.getLayers();
            /*for (var lyr in layers) {
                var layer = layers[lyr];
                if (layer instanceof L.LayerGroup) {
                    var group = layer;
                    group.eachLayer(function(layer) {
                        groupedLyrs.push(group.getLayerId(layer));
                    })
                }
            }*/
            layers.forEach(function(layer) {
                if (layer instanceof ol.layer.Tile) {
                    console.log("xyz")
                    var source = layer.getSource();
                    var xyzLyr = getTiledLayer(source);
                    lyrs.push(['xyz', xyzLyr[0], xyzLyr[1]]);
                } else {
                    //console.log("**" + layer + "**")
                }
            })
        }
    }
    return lyrs;
}());

function getTiledLayer(source) {
    var url = source.getUrls()[0];
    var options = source.getProperties();
    return [url, options];
}

function getJSON(lyr) {
    var geoJSON = lyr.toGeoJSON();
    var serializedGeoJSON = JSON.stringify(geoJSON);
    return serializedGeoJSON;
}
