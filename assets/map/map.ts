import './map.scss'
import maplibregl, { StyleSpecification } from 'maplibre-gl'
import LayerSwitcher from '@russss/maplibregl-layer-switcher'
import URLHash from '@russss/maplibregl-layer-switcher/urlhash'
import map_style from './style/map_style.ts'
import hexpansion_style from './hexpansion_style.json'
import LocationEditor from './location_editor.ts'

async function loadIcons(map: maplibregl.Map) {
    const ratio = Math.min(Math.round(window.devicePixelRatio), 2)
    const images = ['camping', 'no-access', 'water', 'tree', 'gchqnethq', 'gchqnetscoreboard']

    Promise.all(
        images
            .map((image) => async () => {
                const img = await map.loadImage(`/static/img/map/${image}.png`)
                map.addImage(image, img.data, { pixelRatio: ratio })
            })
            .map((f) => f())
    )
}

function buildMapStyle(layers: Record<string, string>, hexpansionEndpoint: string): maplibregl.StyleSpecification {
    map_style.layers = map_style.layers.concat(hexpansion_style.hexpansion_layers)
    map_style.sources.openmaptiles = {
        type: 'vector',
        url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=nrMOzJ8R0LSjSCJC3WXz',
    }
    map_style.sources.hexpansions = {
        type: 'geojson',
        data: hexpansionEndpoint,
        attribution: '© GCHQ.NET 2024'
    }
    map_style.sources.villages = {
        type: 'geojson',
        data: '/api/locations/villages/',
    }
    map_style.sources.gchqnethq = {
        type: 'geojson',
        data: {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "Point", "coordinates": [-2.3755269, 52.0412778]}
                }
            ],
        }
    }
    map_style.sources.gchqnetscoreboard = {
        type: 'geojson',
        data: {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "Point", "coordinates": [-2.3772806057248, 52.0422999931301]}
                }
            ],
        }
    }
    map_style.glyphs = '/static/fonts/{fontstack}/{range}.pbf'
    return map_style
}


class EventMap {
    layers: Record<string, string>
    map?: maplibregl.Map
    map_el: HTMLElement
    style: StyleSpecification
    options: maplibregl.MapOptions
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
            'GCHQ.NET': 'hexpansions',
            DKs: 'dk_',
            'NOC-Physical': 'noc_',
            Power: 'power_',
            Lighting: 'lighting_',
            Villages: 'villages_',
    
        }

        this.map_el = document.getElementById('map')

        const layers_enabled = ['Background', 'Structures', 'Paths', 'GCHQ.NET']

        this.layer_switcher = new LayerSwitcher(this.layers, layers_enabled)

        let hexpansion_endpoint = '/api/locations/my-finds/'
        if (this.map_el.dataset.locationGeoEndpoint) {
            hexpansion_endpoint = this.map_el.dataset.locationGeoEndpoint
        }

        this.style = buildMapStyle(this.layers, hexpansion_endpoint)

        this.options = {
            container: 'map',
            style: this.style,
            pitchWithRotate: false,
            dragRotate: false,
            attributionControl: false,
        }

        if(this.map_el.dataset.urlhash !== undefined){
            this.url_hash = new URLHash(this.layer_switcher)
            this.layer_switcher.urlhash = this.url_hash
            this.options = this.url_hash.init(this.options)
            
        } else {
            if (this.map_el.dataset.zoom !== undefined)
            this.options.zoom = Number(this.map_el.dataset.zoom);

            if (this.map_el.dataset.lat !== undefined && this.map_el.dataset.long !== undefined)
            this.options.center = [
                Number(this.map_el.dataset.long),
                Number(this.map_el.dataset.lat)
            ];
        }
        
        this.layer_switcher.setInitialVisibility(this.style)
        this.map = new maplibregl.Map(
            this.options,
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
        if (this.url_hash !== undefined) this.url_hash.enable(this.map)

        new LocationEditor(this.map)
    }
}

const em = new EventMap()
window.em = em

if (document.readyState != 'loading') {
    em.init()
} else {
    document.addEventListener('DOMContentLoaded', em.init)
}
