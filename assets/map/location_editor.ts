import maplibregl from "maplibre-gl"


class LocationEditor {

    map: maplibregl.Map
    marker: maplibregl.Marker
    formLatitudeInput: HTMLInputElement
    formLongitudeInput: HTMLInputElement

    constructor(map: maplibregl.Map) {
        this.map = map

        const map_el = document.getElementById('map')
        if (map_el && map_el.dataset.markerForm) {
            this.formLatitudeInput = document.getElementById(map_el.dataset.markerLat || '')!
            this.formLongitudeInput = document.getElementById(map_el.dataset.markerLong || '')!

            if (this.formLatitudeInput && this.formLongitudeInput) this.doShit()
        }
    }

    getInitialPos(): [number, number] {
        let initialLat = 52.0411
        let initialLong = -2.375416

        if (this.formLatitudeInput.value != '') {
            initialLat = Number(this.formLatitudeInput.value)
        }

        if (this.formLongitudeInput.value != '') {
            initialLong = Number(this.formLongitudeInput.value)
        }

        return [initialLong, initialLat]
    }

    onDragEnd({target}) {
        const lngLat = target.getLngLat()
        document.getElementById('id_lat')!.value = lngLat.lat.toFixed(13)
        document.getElementById('id_long')!.value = lngLat.lng.toFixed(13)
    }

    doShit() {
        this.marker = new maplibregl.Marker({draggable: true})
        .setLngLat(this.getInitialPos())
        .addTo(this.map);
        this.marker.on('dragend', this.onDragEnd);

        this.map.jumpTo({
            center: this.getInitialPos(),
            zoom: 17
        })
    }

}


export default LocationEditor