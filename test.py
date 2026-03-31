import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import time
import math

# ================= 1. 核心参数配置 =================
AMAP_KEY = 'e5ed0b10440dd15c1d7e217443fad499'
LOCATION = '117.188738,39.14901'  # 天津三岔河口大致坐标 (经度,纬度)
RADIUS = '3000'                # 搜索半径 3000米
POI_TYPE = '090100|090200|090300|090400|090500'     # 090000 代表“医疗保健服务”

# ================= 2. 坐标转换核心算法 (GCJ-02 转 WGS-84) =================
pi = 3.1415926535897932384626  # 圆周率
a = 6378245.0                  # 卫星椭球坐标投影轴
ee = 0.00669342162296594323    # 偏心率平方

def out_of_china(lng, lat):
    # 判断是否在国内，不在国内不做转换
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

# ================= 3. 数据抓取模块 =================
def fetch_medical_pois():
    poi_list = []
    page = 1
    print(f"开始抓取高德医疗 POI 数据，分类代码为: {POI_TYPE} ...")
    
    while True:
        url = "https://restapi.amap.com/v3/place/around"
        # 使用 params 字典传参，requests 库会自动把 '|' 安全地转化为 '%7C'
        params = {
            'key': AMAP_KEY,
            'location': LOCATION,
            'radius': RADIUS,
            'types': POI_TYPE,
            'offset': 20,
            'page': page,
            'extensions': 'all'
        }
        
        try:
            response = requests.get(url, params=params)
            res = response.json()
            
            # 【关键修改】如果被拒绝，把高德的报错信息直接打印出来
            if res.get('status') == '0':
                print(f"\n❌ 高德 API 拒绝了请求！\n错误代码 (infocode): {res.get('infocode')}\n错误原因 (info): {res.get('info')}\n")
                break
                
            if res.get('status') == '1' and int(res.get('count', 0)) > 0:
                pois = res['pois']
                if not pois:
                    break
                for p in pois:
                    loc = p.get('location', '').split(',')
                    if len(loc) == 2:
                        lng_gcj, lat_gcj = float(loc[0]), float(loc[1])
                        lng_wgs, lat_wgs = gcj02_to_wgs84(lng_gcj, lat_gcj)
                        
                        poi_list.append({
                            'name': p.get('name', ''),
                            'type': p.get('type', ''),
                            'lng': lng_wgs,
                            'lat': lat_wgs
                        })
                print(f"  ✓ 第 {page} 页抓取成功，本页获取 {len(pois)} 条数据")
                page += 1
                time.sleep(0.2)
            else:
                break
                
        except Exception as e:
            print(f"❌ 抓取发生网络或解析错误: {e}")
            break
            
    print(f"抓取结束，共获取 {len(poi_list)} 个设施。")
    return poi_list

# ================= 4. 热力图生成模块 =================
def generate_heatmap(poi_data):
    if not poi_data:
        print("没有数据，无法生成热力图。")
        return
        
    df = pd.DataFrame(poi_data)
    
    # 解析设定的中心点坐标，并将其也转换为 WGS-84
    base_loc = LOCATION.split(',')
    base_lng_wgs, base_lat_wgs = gcj02_to_wgs84(float(base_loc[0]), float(base_loc[1]))
    
    # 初始化地图
    m = folium.Map(location=[base_lat_wgs, base_lng_wgs], zoom_start=14, tiles='CartoDB positron')
    
    # 标记设计基地
    folium.Marker(
        location=[base_lat_wgs, base_lng_wgs],
        popup='设计基地：三岔河口',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # 提取热力数据
    heat_data = [[row['lat'], row['lng']] for index, row in df.iterrows()]
    
    # 绘制热力图
    HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
    
    output_file = '三岔河口_医疗资源热力图_精准版.html'
    m.save(output_file)
    print(f"热力图已生成！请打开文件：{output_file}")

# ================= 5. 执行程序 =================
if __name__ == '__main__':
# 1. 获取清洗及转换坐标后的数据
    data = fetch_medical_pois()
    
    if data:
        # 2. 持久化保存为 CSV 文件
        df = pd.DataFrame(data)
        csv_filename = f'三岔河口_医疗POI_{RADIUS}m_WGS84.csv'
        # 使用 utf-8-sig 编码，防止在 Excel 中打开时中文字符乱码
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"原始数据已持久化保存至：{csv_filename}")
        
        # 3. 生成可视化热力图
        generate_heatmap(data)
    else:
        print("未抓取到有效数据，停止执行保存与渲染。")