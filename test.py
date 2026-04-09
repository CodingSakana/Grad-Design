import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import time
import math
import logging
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path

# ================= 1. Configuration =================
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True, parents=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=f"{log_dir}/fetch_logs.log", filemode='a')
logger = logging.getLogger(__name__)

data_dir = Path("runtime_data")
data_dir.mkdir(exist_ok=True, parents=True)

AMAP_KEY = 'e5ed0b10440dd15c1d7e217443fad499'
LOCATION = '117.188622,39.149301'   # Tianjin Sancha River Estuary (Long, Lat)
RADIUS = 3000                       # Search radius in meters

# Define Different Functional Modules
POI_MODULES = {
    'Medical': {
        'types': '090102|090400|090202|090203|090205|090206|090207|090208|090100|090101',
        'tiers': {
            'Tier1': ['090102', '090400'],
            'Tier2': ['090202', '090203', '090205', '090206', '090207', '090208'],
            'Tier3': ['090100', '090101']
        },
        'styles': {
            'Tier1': ('green', 'medkit'),
            'Tier2': ('green', 'plus-square'),
            'Tier3': ('green', 'hospital-o'),
            'default': ('green', 'plus')
        }
    },

    'Accommodation': {
        'types': '100100|100101|100102|100103|100104|100105',
        'tiers': {
            'General': ['1001']  # 所有 1001 开头的都归为一类
        },
        'styles': {
            'General': ('green', 'building'),
            'default': ('green', 'building')
        }
    },
    'ScenicSpots': {
        'types': '110000',
        'tiers': {
            'General': ['11']
        },
        'styles': {
            'General': ('green', 'leaf'),
            'default': ('green', 'leaf')
        }
    }
    }



# ================= 2. Coordinate Transformation (GCJ-02 to WGS-84) =================
class CoordTransformer:
    PI = math.pi
    A = 6378245.0
    EE = 0.00669342162296594323

    @classmethod
    def out_of_china(cls, lng: float, lat: float) -> bool:
        """Checks if a point is outside mainland China."""
        return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)

    @classmethod
    def _transform_lat(cls, lng: float, lat: float) -> float:
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * cls.PI) + 20.0 * math.sin(2.0 * lng * cls.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * cls.PI) + 40.0 * math.sin(lat / 3.0 * cls.PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * cls.PI) + 320 * math.sin(lat * cls.PI / 30.0)) * 2.0 / 3.0
        return ret

    @classmethod
    def _transform_lng(cls, lng: float, lat: float) -> float:
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * cls.PI) + 20.0 * math.sin(2.0 * lng * cls.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * cls.PI) + 40.0 * math.sin(lng / 3.0 * cls.PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * cls.PI) + 300.0 * math.sin(lng / 30.0 * cls.PI)) * 2.0 / 3.0
        return ret

    @classmethod
    def gcj02_to_wgs84(cls, lng: float, lat: float) -> Tuple[float, float]:
        """Converts GCJ-02 coordinates (Mars coordinates) to WGS-84."""
        if cls.out_of_china(lng, lat):
            return lng, lat
        dlat = cls._transform_lat(lng - 105.0, lat - 35.0)
        dlng = cls._transform_lng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * cls.PI
        magic = math.sin(radlat)
        magic = 1 - cls.EE * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((cls.A * (1 - cls.EE)) / (magic * sqrtmagic) * cls.PI)
        dlng = (dlng * 180.0) / (cls.A / sqrtmagic * math.cos(radlat) * cls.PI)
        return lng * 2 - (lng + dlng), lat * 2 - (lat + dlat)

# ================= 3. Data Fetching Module =================
def fetch_poi_data(api_key: str, location: str, radius: int, poi_type: str) -> List[Dict]:
    """Fetches POI data from AMap around a specific location."""
    poi_list = []
    page = 1
    session = requests.Session()
    url = "https://restapi.amap.com/v5/place/around"
    
    logger.info(f"Starting POI fetch for type: {poi_type} at {location}")
    
    while True:
        params = {
            'key': api_key,
            'location': location,
            'radius': radius,
            'sortrule': 'weight',
            'types': poi_type,
            'page_size': 25,
            'page_num': page,
            'extensions': 'all'
        }
        
        try:
            response = session.get(url, params=params, timeout=10)
            res = response.json()
            
            if res.get('status') == '0':
                logger.error(f"AMap API Error! Code: {res.get('infocode')}, Info: {res.get('info')}")
                break
                
            if res.get('status') == '1' and int(res.get('count', 0)) > 0:
                pois = res.get('pois', [])
                if not pois:
                    break
                
                for p in pois:
                    loc_str = p.get('location', '').split(',')
                    if len(loc_str) == 2:
                        lng_gcj, lat_gcj = float(loc_str[0]), float(loc_str[1])
                        lng_wgs, lat_wgs = CoordTransformer.gcj02_to_wgs84(lng_gcj, lat_gcj)
                        
                        poi_list.append({
                            'id': p.get('id', ''),
                            'name': p.get('name', ''),
                            'type': p.get('type', ''),
                            'typecode': p.get('typecode', ''),
                            'lng': lng_wgs,
                            'lat': lat_wgs
                        })
                
                logger.info(f"Page {page} fetched successfully ({len(pois)} items)")
                page += 1
                time.sleep(0.2)  # Respect API rate limits
            else:
                break
                
        except Exception as e:
            logger.error(f"Network or parsing error occurred: {e}")
            break
            
    logger.info(f"Fetch completed. Total items: {len(poi_list)}")
    return poi_list

# ================= 4. Map Generation Module =================
def generate_heatmap(poi_data: List[Dict], center_location: str, output_file: str, tier_defs: Dict, style_defs: Dict):
    """Generates a Folium map with categorized markers using dynamic rules."""
    if not poi_data:
        logger.warning(f"No data for {output_file}, skipping.")
        return
        
    df = pd.DataFrame(poi_data)
    base_loc = [float(x) for x in center_location.split(',')]
    base_lng_wgs, base_lat_wgs = CoordTransformer.gcj02_to_wgs84(base_loc[0], base_loc[1])
    
    # Initialize map
    m = folium.Map(location=[base_lat_wgs, base_lng_wgs], zoom_start=14, tiles='CartoDB positron')
    
    # Dynamic style mapping
    def get_style(typecode: str) -> Tuple[str, str]:
        if not typecode: return style_defs.get('default', ('gray', 'info-sign'))
        
        for tier_name, codes in tier_defs.items():
            if any(typecode.startswith(c) for c in codes):
                return style_defs.get(tier_name, style_defs['default'])
        
        return style_defs['default']
    
    site_html = """
    <div style="
        width: 20px; 
        height: 20px; 
        background-color: #E74C3C; 
        border-radius: 50%; 
        border: 3px solid white; 
        box-shadow: 0 0 10px rgba(0,0,0,0.5);">
    </div>
    """

    # Mark the center
    folium.Marker(
        location=[base_lat_wgs, base_lng_wgs],
        popup='Project Site: Sancha River Estuary',
        tooltip='Project Site: Sancha River Estuary',
        # icon=folium.Icon(color='white', icon_color='gray', icon='circle-o', prefix='fa')
        icon=folium.DivIcon(html=site_html)
    ).add_to(m)
    
    # Add markers for each POI
    for _, row in df.iterrows():
        color, icon_name = get_style(str(row.get('typecode', '')))
        
        # Mapping tier colors to standard HEX for CircleMarker
        hex_colors = {
            'green': '#27AE60',
            'orange': '#E67E22',
            'red': '#C0392B',
            'purple': '#8E44AD',
            'blue': '#2980B9',
            'cadetblue': '#5D6D7E'
        }
        marker_color = hex_colors.get(color, '#3498DB')

        # Styled Popup HTML
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 150px;">
            <strong style="color: {marker_color}; font-size: 14px;">{row['name']}</strong><br>
            <hr style="margin: 5px 0;">
            <span style="font-size: 12px; color: #555;">类型: {row['type']}</span><br>
            <span style="font-size: 11px; color: #888;">代码: {row.get('typecode', '')}</span>
        </div>
        """

        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=6,                # 增大半径使其易于点击
            color=marker_color,      # 边框颜色
            weight=1,                # 细边框
            fill=True,
            fill_color=marker_color, # 填充对应的梯队颜色
            fill_opacity=0.4,        # 较低的透明度，保持轻盈感
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['name']      # 悬浮显示名称
        ).add_to(m)

    # Prepare heat data
    heat_data = df[['lat', 'lng']].values.tolist()
    
    # Add HeatMap (optional: keep it for density visualization)
    HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
    
    m.save(output_file)
    logger.info(f"Map with markers generated successfully: {output_file}")

# ================= 5. Main Execution =================
if __name__ == '__main__':
    current_date = datetime.now().strftime("%Y%m%d")
    
    for module_name, config in POI_MODULES.items():
        logger.info(f"========== Processing Module: {module_name} ==========")
        csv_filename = f'poi_{module_name}_{RADIUS}m_{current_date}.csv'
        csv_path = data_dir / csv_filename
        
        data = []
        
        # 1. Caching logic
        if csv_path.exists():
            df_cached = pd.read_csv(csv_path)
            if 'typecode' in df_cached.columns:
                logger.info(f"Cache hit for {module_name}. Loading.")
                data = df_cached.to_dict('records')
        
        # 2. Fetch data if no valid cache
        if not data:
            raw_results = []
            all_types = config['types'].split('|')
            logger.info(f"Batch fetching {len(all_types)} categories for {module_name}.")
            
            for idx, t in enumerate(all_types):
                logger.info(f"[{idx+1}/{len(all_types)}] Fetching: {t}")
                type_data = fetch_poi_data(AMAP_KEY, LOCATION, RADIUS, t)
                raw_results.extend(type_data)
                time.sleep(0.3)

            if raw_results:
                unique_data = {}
                for item in raw_results:
                    key = item.get('id') or f"{item['name']}_{item['lng']}_{item['lat']}"
                    if key not in unique_data:
                        unique_data[key] = item
                data = list(unique_data.values())
                
                pd.DataFrame(data).to_csv(csv_path, index=False, encoding='utf-8-sig')
                logger.info(f"Saved {len(data)} unique items for {module_name}.")
        
        # 3. Generate Visualizations per Tier
        if data:
            for tier_name, codes in config['tiers'].items():
                tier_data = [
                    item for item in data 
                    if any(str(item.get('typecode', '')).startswith(c) for c in codes)
                ]
                
                if tier_data:
                    html_file = f'map_{module_name}_{tier_name}_{current_date}.html'
                    generate_heatmap(tier_data, LOCATION, html_file, config['tiers'], config['styles'])
                    logger.info(f"Generated: {html_file} ({len(tier_data)} points)")
        else:
            logger.error(f"No data for module {module_name}.")
