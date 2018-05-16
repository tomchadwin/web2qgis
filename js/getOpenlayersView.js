(function (){
    for(var key in window) {
        var value = window[key];
        if (value instanceof ol.Map) {
            var map = value;
            mapBounds = map.getView().calculateExtent(map.getSize());
        }
    }
    return mapBounds;
}());

