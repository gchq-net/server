import './map.scss'
import maplibregl from 'maplibre-gl'
import LayerSwitcher from '@russss/maplibregl-layer-switcher'
import URLHash from '@russss/maplibregl-layer-switcher/urlhash'
import map_style from './map_style.ts'
import hexpansion_style from './hexpansion_style.json'

class EventMap {
    layers: Record<string, string>
    map?: maplibregl.Map
    layer_switcher?: LayerSwitcher
    url_hash?: URLHash

    init() {
        this.layers = {
            Background: 'background_',
            Slope: 'slope',
            Hillshade: 'hillshade',
            'Aerial Imagery': 'ortho',
            Structures: 'structures_',
            Paths: 'paths_',
            'Buried Services': 'services_',
            Water: 'site_water_',
            Hexpansions: 'hexpansions',
            DKs: 'dk_',
            'NOC-Physical': 'noc_',
            Power: 'power_',
            Lighting: 'lighting_',
            Villages: 'villages_',
    
        }

        const layers_enabled = ['Background', 'Structures', 'Paths', 'Hexpansions']


        this.layer_switcher = new LayerSwitcher(this.layers, layers_enabled)

        this.url_hash = new URLHash(this.layer_switcher)
        this.layer_switcher.urlhash = this.url_hash

        map_style.layers = map_style.layers.concat(hexpansion_style.hexpansion_layers)

        this.layer_switcher.setInitialVisibility(map_style)
        this.map = new maplibregl.Map(
            this.url_hash.init({
                container: 'map',
                style: map_style,
                pitchWithRotate: false,
                dragRotate: false,
            })
        )

        this.map.touchZoomRotate.disableRotation()

        this.map.addControl(new maplibregl.NavigationControl(), 'top-right')

        this.map.addControl(
            new maplibregl.GeolocateControl({
                positionOptions: {
                    enableHighAccuracy: true,
                },
                trackUserLocation: true,
            })
        )

        this.map.addControl(
            new maplibregl.ScaleControl({
                maxWidth: 200,
                unit: 'metric',
            })
        )
    
        this.map.addControl(this.layer_switcher, 'top-right')
        this.url_hash.enable(this.map)
    }
}

const em = new EventMap()
window.em = em

if (document.readyState != 'loading') {
    em.init()
} else {
    document.addEventListener('DOMContentLoaded', em.init)
}
