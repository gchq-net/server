import './map.scss'
import maplibregl from 'maplibre-gl'
import LayerSwitcher from '@russss/maplibregl-layer-switcher'
import URLHash from '@russss/maplibregl-layer-switcher/urlhash'
import map_style from './style/map_style.ts'
import hexpansion_style from './hexpansion_style.json'

async function loadIcons(map: maplibregl.Map) {
    const ratio = Math.min(Math.round(window.devicePixelRatio), 2)

    const images = ['camping', 'no-access', 'water', 'tree']

    Promise.all(
        images
            .map((image) => async () => {
                const img = await map.loadImage(`/static/img/map/${image}.png`)
                map.addImage(image, img.data, { pixelRatio: ratio })
            })
            .map((f) => f())
    )
    /*
    const sdfs = ['parking']

    for (const sdf of sdfs) {
        const img = await map.loadImage(`/sdf/${sdf}.png`)
        map.addImage(sdf, img.data, { sdf: true })
    }
    */
}


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
        map_style.sources.openmaptiles = {
            type: 'vector',
            url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=nrMOzJ8R0LSjSCJC3WXz',
        }
        map_style.sources.hexpansions = {
            type: 'geojson',
            data: '/api/locations/my-finds/',
            attribution: '© GCHQ.NET 2024'
        }
        map_style.sources.villages = {
            type: 'geojson',
            data: '/static/villages.geojson',
        }
        map_style.glyphs = '/static/fonts/{fontstack}/{range}.pbf'
        
        this.layer_switcher.setInitialVisibility(map_style)
        this.map = new maplibregl.Map(
            this.url_hash.init({
                container: 'map',
                style: map_style,
                pitchWithRotate: false,
                dragRotate: false,
                attributionControl: false,
            }),
        )
        loadIcons(this.map)

        this.map.touchZoomRotate.disableRotation()

        this.map.addControl(new maplibregl.AttributionControl({
            compact: true
        }));

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
