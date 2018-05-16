(function (){
    var lyrs = [];
    var groupedLyrs = [];
    for (var key in window) {
        var value = window[key];
        if (value instanceof ol.Map) {
            var map = value;
            var layers = map.getLayers();
            layers.forEach(function(layer) {
                if (layer instanceof ol.layer.Tile) {
                    var source = layer.getSource();
                    var xyzLyr = getTiledLayer(source);
                    lyrs.push(['xyz', xyzLyr[0], xyzLyr[1]]);
                } else if (layer instanceof ol.layer.Vector) {
                    lyrs.push(['vector', getJSON(layer)]);
                } else {
                    console.log("Unsupported layer type")
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
    var source = lyr.getSource();
    var features = source.getFeatures();
    var geoJsonWriter = new ol.format.GeoJSON();
    var geoJSON = geoJsonWriter.writeFeatures(features);
    return geoJSON;
}
