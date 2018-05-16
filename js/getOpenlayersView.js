(function (){
    for(var key in window) {
        var value = window[key];
        if (value instanceof L.Map) {
            mapBounds = value.getBounds().toBBoxString();
        }
    }
    return mapBounds;
}());

