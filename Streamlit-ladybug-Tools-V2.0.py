import ladybug.analysisperiod as ap
import ladybug.epw as epw_module
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import ladybug_charts
import ladybug.windrose as wr
import pandas as pd
import math
import zipfile
import requests
import io
import tempfile
import httpx
from ratelimit import limits, sleep_and_retry

# Function to map a value between two ranges to a new range
def map_value(value, old_min, old_max, new_min, new_max):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def map_temperature_to_color(temperature, min_temp, max_temp, color_scheme):
    if color_scheme == 1:
        r = int(map_value(temperature, min_temp, max_temp, 0, 240))
        g = int(map_value(temperature, min_temp, max_temp, 0, 240))
        b = int(map_value(temperature, min_temp, max_temp, 0, 240))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 2:
        r = int(map_value(temperature, min_temp, max_temp, 65, 255))
        g = int(map_value(temperature, min_temp, max_temp, 65, 65))
        b = int(map_value(temperature, min_temp, max_temp, 255, 65))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 3:
        r = int(map_value(temperature, min_temp, max_temp, 238, 255))
        g = int(map_value(temperature, min_temp, max_temp, 105, 245))
        b = int(map_value(temperature, min_temp, max_temp, 131, 228))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 4:
        r = int(map_value(temperature, min_temp, max_temp, 151, 255))
        g = int(map_value(temperature, min_temp, max_temp, 92, 173))
        b = int(map_value(temperature, min_temp, max_temp, 141, 188))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 5:
        r = int(map_value(temperature, min_temp, max_temp, 34, 149))
        g = int(map_value(temperature, min_temp, max_temp, 87, 209))
        b = int(map_value(temperature, min_temp, max_temp, 126, 204))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 6:
        r = int(map_value(temperature, min_temp, max_temp, 185, 117))
        g = int(map_value(temperature, min_temp, max_temp, 255, 121))
        b = int(map_value(temperature, min_temp, max_temp, 252, 231))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 7:
        r = int(map_value(temperature, min_temp, max_temp, 26, 229))
        g = int(map_value(temperature, min_temp, max_temp, 18, 229))
        b = int(map_value(temperature, min_temp, max_temp, 11, 203))
        return f'rgb({r}, {g}, {b})'
    elif color_scheme == 8:
        r = int(map_value(temperature, min_temp, max_temp, 109, 238))
        g = int(map_value(temperature, min_temp, max_temp, 159, 222))
        b = int(map_value(temperature, min_temp, max_temp, 217, 236))
        return f'rgb({r}, {g}, {b})'


st.header("Visualization of Climate Data and Passive Strategies Online")
st.subheader("气象数据与被动策略在线可视化")

httpx.verify = False
# 获取仓库中的文件夹列表
folder_mapping = {
    "CHN_AN": "安徽省",
    "CHN_BJ": "北京市",
    "CHN_SH": "上海市",
    "CHN_CQ": "重庆市",
    "CHN_FJ": "福建省",
    "CHN_GD": "广东省",
    "CHN_GS": "甘肃省",
    "CHN_XJ": "新疆维吾尔自治区",
    "CHN_SN": "陕西省",
    "CHN_GX": "广西壮族自治区",
    "CHN_GZ": "贵州省",
    "CHN_HA": "河南省",
    "CHN_HB": "湖北省",
    "CHN_HE": "河北省",
    "CHN_HI": "海南省",
    "HKG": "香港特别行政区",
    "CHN_HL": "黑龙江省",
    "CHN_HN": "湖南省",
    "CHN_JL": "吉林省",
    "CHN_JS": "江苏省",
    "CHN_JX": "江西省",
    "CHN_LN": "辽宁省",
    "MAC": "澳门特别行政区",
    "CHN_NM": "内蒙古自治区",
    "CHN_NX": "宁夏回族自治区",
    "CHN_QH": "青海省",
    "CHN_SC": "四川省",
    "CHN_SD": "山东省",
    "CHN_SX": "山西省",
    "CHN_TJ": "天津市",
    "TWN": "台湾省",
    "CHN_XZ": "西藏自治区",
    "CHN_YN": "云南省",
    "CHN_ZJ": "浙江省"
}

repo_url = "https://api.github.com/repos/Zoumachuan/CHN_EPW/contents/CHN_EPW"
response = requests.get(repo_url, verify=False)

# 添加调试输出以检查response内容
print("Response status code:", response.status_code)
print("Response content:", response.content)

# 检查响应状态码
if response.status_code != 200:
    st.write(f"Failed to retrieve data from GitHub API. Status code: {response.status_code}")
else:
    response_json = response.json()
    folder_list = [item["name"] for item in response_json if item["type"] == "dir"]

# 进行名称替换
folder_list_replaced = [folder_mapping.get(folder, folder) for folder in folder_list]

# 创建一个下拉框选择文件夹
selected_folder_index = st.selectbox("Select a province/选择省份", range(len(folder_list_replaced)), format_func=lambda i: folder_list_replaced[i])

# 检查选择的文件是否为zip格式
if selected_file.endswith(".zip"):
    # 读取zip文件
    zip_file_url = f"https://github.com/Zoumachuan/CHN_EPW/raw/main/CHN_EPW/{original_selected_folder}/{selected_file}"
    zip_data = requests.get(zip_file_url, verify=False).content

    # 创建一个字节流对象
    zip_data = io.BytesIO(zip_data)

    # 解压缩zip文件
    with zipfile.ZipFile(zip_data, "r") as zip_ref:
        # 获取zip文件中所有的文件
        zip_files = zip_ref.namelist()

        # 获取所有以".epw"结尾的文件
        epw_files = [file for file in zip_files if file.endswith(".epw")]

        # 创建一个下拉框选择epw文件
        selected_epw = st.selectbox("Select an EPW file/选择您需要的EPW文件", epw_files)

        # 解压缩选中的epw文件到内存中
        epw_data = zip_ref.read(selected_epw)

        # 保存解压后的epw数据到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".epw") as temp_file:
            temp_file.write(epw_data)
            temp_file_path = temp_file.name

        # 加载解压后的epw文件
        epw = epw_module.EPW(temp_file_path)

        # 显示成功提示信息
        st.success("EPW file read successfully!/已成功读取您选择的EPW文件")

    # 添加一个下载按钮，用于下载zip文件
    st.download_button(
        label="Download EPW file",
        data=zip_data.getvalue(),
        file_name=selected_file,
        mime="application/zip"
    )
else:
    # 显示错误提示信息
    st.error("Invalid file format. Please select a ZIP file.")

uploaded_file = st.file_uploader("Upload an EPW file/或者上传您自己的epw文件，格式为.epw", type="epw")

# 如果有文件上传，使用上传的文件作为EPW文件
if uploaded_file is not None:
    # 读取上传的EPW文件
    epw_data = uploaded_file.read()

    # 保存上传的EPW数据到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epw") as temp_file:
        temp_file.write(epw_data)
        temp_file_path = temp_file.name

    # 加载上传的EPW文件
    epw = epw_module.EPW(temp_file_path)
    

    # 显示成功提示信息
    st.success("Your EPW file uploaded successfully!/已成功读取您上传的EPW文件")


st.subheader('您当前读取的数据是：' + str(epw))

slider1 = st.slider("Start month/起始月份", 1, 12, key=1)
i = slider1
slider2 = st.slider("End month/终止月份", 1, 12, key=2)
j = slider2
color_scheme = st.slider("Color Scheme/色卡选择", 1, 8, key=3)

range_select = ap.AnalysisPeriod(st_month=i, end_month=j)  # Range for selected months
range_full = ap.AnalysisPeriod(st_month=1, end_month=12)    # Range for full year
range_day = ap.AnalysisPeriod(st_month=i, st_day=1, end_month=j, end_day=31)  # Range for selected days within selected months
range_hr = ap.AnalysisPeriod(st_month=1, st_day=1,st_hour=0,end_month=12, end_day=31,end_hour=23)

# Add a selectbox to select temperature type
temperature_type = st.selectbox("Select Data Type/选择可视化内容", ["Passive Strategies/被动策略","Dry Bulb Temperature/干球温度", "Dew Point Temperature/露点温度", "Relative Humidity/相对湿度", "Wind Speed/风速","Wind Rose/风玫瑰图","Direct Normal Rad/直接法线辐射","Diffuse Horizontal Rad/散射水平辐射","Global Horizontal Rad/全球水平辐射","Direct Normal Ill/直接法线照度","Diffuse Horizontal Ill/散射水平照度","Global Horizontal Ill/全球水平照度","Total Sky Cover/天空覆盖量"])
#-------------------------------------------------------------
if temperature_type == "Passive Strategies/被动策略":
    # 定义状态名称和颜色
    states = [
        "Comfort/舒适时段",
        "Sun Shading of windows/窗户遮阳",
        "High Thermal Mass/高热质量",
        "High Thermal Mass Night Flushed/高热质量+夜间通风",
        "Direct Evaporative Cooling/直接蒸发冷却",
        "Two-Stage Evaporative Cooling/双级蒸发冷却",
        "Natural Ventilation Cooling/自然通风冷却",
        "Fan-Forced Ventilation Cooling/风扇通风冷却",
        "Internal Heating Gain/内部加热增益",
        "Humidification Only/仅加湿",
        "Dehumidification Only/仅除湿",
        "Cooling add Dehumidification if needed/制冷除湿",
        "Heating add Humidification if needed/加热增湿",
    ]
    colors = [
        "blue",
        "lightblue",
        "cyan",
        "green",
        "lightgreen",
        "lime",
        "yellow",
        "lightgrey",
        "khaki",
        "orange",
        "darkorange",
        "orange",
        "purple",
    ]
    
    # 初始化状态计数和焓比累计
    state_counts = [0] * len(states)
    total_h_sum = 0
    total_h_count = 0
    total_tw_sum = 0
    total_tw_count = 0
    
    # 初始化湿球温度范围计数
    tw_ranges = [0, 0, 0, 0, 0]  # 0-10, 10-20, 20-30, 30-40, 40+
    
    # 初始化焓比范围计数
    h_ranges = [0, 0, 0, 0, 0]  # 0-10, 10-30, 30-50, 50-70, 70+
    
    # 常数和计算
    R = 287.05  # 气体常数，单位 J/(kg*K)
    P = 101.325  # 标准大气压，单位 KPa
    
    # 计算每个小时的热湿状态，并分配到不同状态
    for i in range(8760):  # 假设共有8760个小时的数据
        # 获取干球温度、相对湿度、露点温度（假设获取方法如下）
        t_drybulb = epw.dry_bulb_temperature[i]
        rh_percentage = epw.relative_humidity[i] / 100.0
        t_dewpoint = epw.dew_point_temperature[i]
    
        # 计算饱和水蒸气压
        e = 6.1078 * math.pow(10, (7.5 * t_drybulb / (t_drybulb + 237.3) - 1))
    
        # 计算含湿量
        d = 0.622 * (rh_percentage * e) / (P - rh_percentage * e)
    
        # 计算湿球温度
        tw = (
            t_drybulb * math.atan(0.152 * math.sqrt(rh_percentage * 100 + 8.3136))
            + math.atan(t_drybulb + rh_percentage)
            - math.atan(rh_percentage * 100 - 1.6763)
            + 0.00391838 * math.pow(rh_percentage * 100, 1.5) * math.atan(0.0231 * rh_percentage * 100)
            - 4.686
        )
    
        # 计算焓比
        h = 1.006 * t_drybulb + (2501 + 1.86 * t_drybulb) * d
    
        # 累计焓比和湿球温度
        total_h_sum += h
        total_h_count += 1
        total_tw_sum += tw
        total_tw_count += 1
    
        # 根据湿球温度范围计数
        if 0 <= tw < 10:
            tw_ranges[0] += 1
        elif 10 <= tw < 20:
            tw_ranges[1] += 1
        elif 20 <= tw < 30:
            tw_ranges[2] += 1
        elif 30 <= tw < 40:
            tw_ranges[3] += 1
        elif tw >= 40:
            tw_ranges[4] += 1
    
        # 根据焓比范围计数
        if  h < 10:
            h_ranges[0] += 1
        elif 10 <= h < 30:
            h_ranges[1] += 1
        elif 30 <= h < 50:
            h_ranges[2] += 1
        elif 50 <= h < 70:
            h_ranges[3] += 1
        elif h >= 70:
            h_ranges[4] += 1
    
        # 根据条件将小时分配到不同状态
        if rh_percentage < 0.8 and tw < 17 and 20 < t_drybulb < 24:
            state_counts[0] += 1  # Comfort
    
        if rh_percentage > 0.8 and tw > 17 and 20 < t_drybulb :
            state_counts[1] += 1  # Sun Shading of windows
    
        if -4 < t_dewpoint < 18 and tw < 21.5 and rh_percentage < 0.8 and 20 < t_drybulb < 32.5:
            state_counts[2] += 1  # High Thermal Mass
    
        if -4 < t_dewpoint < 18 and t_drybulb > 20 and rh_percentage < 0.8 and tw < 23:
            state_counts[3] += 1  # High Thermal Mass Night Flushed
    
        if 9 < tw < 18 and t_drybulb > 20 and rh_percentage < 0.8:
            state_counts[4] += 1  # Direct Evaporative Cooling
    
        if 9 < tw < 22 and t_drybulb > 20 and rh_percentage < 0.8 and t_dewpoint < 12:
            state_counts[5] += 1  # Two-Stage Evaporative Cooling
    
        if 20 < t_drybulb < 26.5 and -5 < t_dewpoint and 0.15 < rh_percentage < 0.9 and tw < 23:
            state_counts[6] += 1  # Natural Ventilation Cooling
    
        if 20 < t_drybulb < 28 and -5 < t_dewpoint and 0.15 < rh_percentage < 0.9 and tw < 23:
            state_counts[7] += 1  # Fan-Forced Ventilation Cooling
    
        if 12.5 < t_drybulb < 20:
            state_counts[8] += 1  # Internal Heating Gain
    
        if t_dewpoint < -4 and 20 < t_drybulb < 24:
            state_counts[9] += 1  # Humidification Only
    
        if rh_percentage > 0.8 and tw > 17 and 20 < t_drybulb < 24:
            state_counts[10] += 1  # Dehumidification Only
    
        if t_drybulb > 24:
            state_counts[11] += 1  # Cooling add Dehumidification if needed
    
        if t_drybulb < 20:
            state_counts[12] += 1  # Heating add Humidification if needed
    
    # 计算分布比例
    total_hours = 8760  # 假设共有8760个小时的数据
    state_distribution = [count for count in state_counts]
    
    # 创建彩色条
    fig = go.Figure(data=[go.Bar(x=state_distribution, y=states, orientation="h", marker_color=colors)])
    
    # 设置图表布局
    fig.update_layout(
        title="Passive Strategies/被动策略",
        xaxis_title="Hour Count/占比小时数",
        yaxis_title="States/策略",
        yaxis_categoryorder="total ascending",
    )
    
    # 计算焓比平均值并输出
    #average_h = total_h_sum / total_h_count
    #st.write(f"Average Enthalpy: {average_h:.2f} kJ/kg")
    
    # 计算湿球温度平均值并输出
    #average_tw = total_tw_sum / total_tw_count
    #st.write(f"Average Wet Bulb Temperature: {average_tw:.2f} °C")
    
    # 绘制图表
    st.plotly_chart(fig, use_container_width=True)
    # 策略介绍
    st.markdown("**Comfort/舒适时段**")
    st.markdown("代表着温度与湿度均较为合适，人能够感觉很舒适的时段")
    st.markdown("**Sun Shading of windows/窗户遮阳**")
    st.markdown("指的是在建筑物中使用遮阳装置来控制太阳光线进入窗户的现象。在绿色建筑领域，这是一种被动性策略，用于优化室内环境、减少能源消耗和提高室内舒适度。遮阳装置可以采用多种形式，如百叶窗、遮阳帘、太阳帽、外部遮阳板等，它们的设计目的是在不妨碍自然采光的前提下，减少室内的过度阳光照射。通过合理设计和放置遮阳装置，可以有效地阻挡或分散进入室内的直射阳光，减少室内温度升高，降低空调负荷，从而减少能源消耗。")
    st.markdown("**High Thermal Mass/高热质量**")
    st.markdown("指的是建筑材料或结构具有较高的热容量，能够吸收和储存热量，并在需要时释放热量。这种设计策略旨在平衡室内温度，减少温度波动，提高室内舒适度，同时减少能源消耗。高热质量的材料，如混凝土、砖块和石头，能够缓冲室内外温度变化，降低冷暖空调的需求。")
    st.markdown("**High Thermal Mass Night Flushed/高热质量+夜间通风**")
    st.markdown("指的是在夜间利用高热质量材料进行通风（或通风冷却）。这种策略利用夜晚较低的温度来冷却高热质量建筑元素（例如墙壁、地板等），以在白天释放储存在材料中的冷量，从而减少白天的冷却需求。这有助于降低能源消耗，提高建筑的能效性能。")
    st.markdown("**Direct Evaporative Cooling/直接蒸发冷却**")
    st.markdown("指的是热空气通过将水蒸发成水蒸气的过程来降低温度。当热空气通过湿润的材料或介质（例如湿润的棉帘或湿润的过滤器）时，热量从空气中转移到水分，将热空气冷却下来。这种冷却方法适用于干燥的气候，因为它依赖于空气中的干燥度来实现蒸发效果。直接蒸发冷却是一种相对节能的方法，因为它不需要大量的能源来运行，相对于传统的冷气调节系统，它具有更低的能源消耗。然而，它的有效性会受到环境湿度的影响，因此在湿度较高的地区效果可能不如在干燥地区显著。")
    st.markdown("**Two-Stage Evaporative Cooling/双级蒸发冷却**")
    st.markdown("指的是空气首先通过一个湿润的介质，如湿润的过滤器，以实现初始的蒸发冷却。然后，冷却的空气进一步经过第二个冷却阶段，这个阶段通常使用冷却冷却介质，如冷冻盘管或冷却媒体，以进一步降低温度。这种双级方法能够在更广泛的气候条件下实现较低的室内温度，而不会像传统的单级蒸发冷却那样受到湿度的限制。双级蒸发冷却通常比单级蒸发冷却更复杂，但在需要更大冷却效果的情况下，它可以提供更好的性能。这种技术可以在需要控制室内温度的建筑物和设施中使用，以减少能源消耗并提高舒适度。")
    st.markdown("**Natural Ventilation Cooling/自然通风冷却**")
    st.markdown("指的是通过建筑的设计和布局，以及利用自然风的流动来实现室内的通风和冷却效果，而不需要使用机械通风或空调系统。自然通风冷却的关键是充分利用外部自然风，通过在建筑中设置通风口、窗户、通风塔等来引导冷空气进入，排出热空气。这种策略在合适的气候条件下可以非常有效，特别是在夜间或早晨时，当室外温度较低时，可以开启窗户，引入凉爽的空气，并将热空气排出。这种方法可以降低室内温度，提高室内空气质量，减少能源消耗。自然通风冷却适用于一些气候条件较为温和的地区，但在极端高温或高湿度的环境下效果可能有限。在设计和实施自然通风冷却时，需要考虑建筑朝向、通风口位置、建筑内部布局等因素，以实现最佳效果并确保舒适度。")
    st.markdown("**Fan-Forced Ventilation Cooling/风扇通风冷却**")
    st.markdown("指的是利用风扇的力量，将室外空气引入建筑内部，以降低室内温度并改善空气质量。在这种技术中，风扇被用来推动新鲜的室外空气进入建筑内部，将室内热空气和污浊的空气排出。这样的通风过程有助于将热量从建筑内部带走，从而实现冷却效果。通常，这种方法适用于气温相对较低的时候，例如早晨和晚上，以充分利用室外空气的凉爽。风扇强制通风冷却可以是一种有效的方法，尤其是在没有其他高级冷却系统的情况下。它通常适用于小型建筑物或需要临时降温的情况。但是，这种方法可能受到室外气温和湿度的限制，因此在炎热潮湿的气候条件下效果可能有限。")
    st.markdown("**Internal Heating Gain/内部加热增益**")
    st.markdown("指的是建筑内部产生的热量，通常是由人体、电子设备、照明等活动和设备所产生的热量。在建筑物内部，这些活动和设备会释放热能，导致室内温度升高。内部加热增益是建筑能量分析和热舒适性评估中的一个重要因素。了解内部加热增益有助于设计和操作建筑的暖通空调系统，以确保室内温度和舒适度在合理范围内，同时最小化能源消耗。合理管理内部加热增益可以减少对冷暖空调系统的需求，从而提高建筑的能效性能。")
    st.markdown("**Humidification Only/仅加湿**")
    st.markdown("指的是一种空气处理或气候控制系统，其主要功能是向室内环境中添加水分，以提高空气的湿度水平。这种系统适用于干燥的气候或季节，当室内空气湿度过低时，可能会影响舒适性和健康。在干燥的冬季或干旱的气候条件下，室内空气中的湿度可能降低到不适宜的水平，可能导致皮肤干燥、喉咙不适甚至加剧传染病的传播。通过加湿系统，可以向室内引入适量的水分，从而提高空气湿度，创造更为舒适的居住或工作环境。这种类型的系统通常会使用加湿器、蒸发器等设备来实现，可以通过控制设备的运行时间和湿度设置来维持所需的室内湿度水平。值得注意的是，过度加湿也可能导致其他问题，如霉菌生长和空气质量下降，因此需要合理的控制和监测。")
    st.markdown("**Dehumidification Only/仅除湿**")
    st.markdown("指的是一种空气处理系统或气候控制策略，其主要目标是降低室内空气的湿度水平。这种系统通常在潮湿的环境中使用，以确保室内空气湿度保持在舒适和健康的范围内。潮湿的气候或环境可能导致室内空气中的湿度过高，这可能会导致不适、霉菌生长以及其他室内环境问题。通过使用除湿系统，可以从室内空气中去除多余的水分，从而降低湿度水平。这种类型的系统通常使用除湿器等设备来实现，通过控制设备的运行时间和湿度设置，可以维持所需的室内湿度水平。同时，需要注意的是，过度除湿也可能导致空气过于干燥，可能引发皮肤干燥和其他不适问题，因此需要合理控制和监测除湿过程。")
    st.markdown("**Cooling add Dehumidification if needed/制冷除湿**")
    st.markdown("指的是一种空调系统运行模式或策略，意味着系统会首先进行冷却操作，如果需要的话，还会在此基础上添加除湿操作。在某些气候条件下，空气可能同时潮湿和温暖，这会导致室内不仅感觉闷热，还感觉不舒适。因此，空调系统需要同时降低温度和湿度，以提供更舒适的室内环境。其工作原理是，首先通过冷却操作降低空气温度，然后在冷却的基础上，如果室内湿度仍然过高，系统会启动除湿操作，以去除室内空气中的多余水分，从而提高舒适性。这种策略在炎热潮湿的气候中特别有用，可以有效地控制室内的温度和湿度，提供更为舒适的居住和工作环境。")
    st.markdown("**Heating add Humidification if needed/加热增湿**")
    st.markdown("指的是一种暖气系统的运行模式或策略，意味着系统会在加热的基础上，如果需要的话，还会添加加湿操作。在一些寒冷干燥的气候条件下，暖气运行可能会导致室内空气的湿度降低，使空气变得干燥。过于干燥的空气可能引起皮肤干燥、喉咙不适，甚至影响呼吸道健康。其工作原理是，在进行暖气加热的同时，如果室内湿度仍然过低，系统会启动加湿操作，向室内引入适量的水分，从而提高空气湿度水平，创造更为舒适的居住环境。")
    # 展示比湿范围内分布数量的表格
    #tw_ranges_labels = [
    #    "0-10 °C",
    #    "10-20 °C",
    #    "20-30 °C",
    #    "30-40 °C",
    #    "40+ °C",
    #]
    #tw_ranges_table = np.column_stack((tw_ranges_labels, tw_ranges))
    #st.table(tw_ranges_table)
    
    
    # 展示比焓范围内分布数量的表格
    #h_ranges_labels = [
    #   "比焓范围",
    #    "10- kJ/kg",
    #    "10-30 kJ/kg",
    #    "30-50 kJ/kg",
    #    "50-70 kJ/kg",
    #    "70+ kJ/kg",
    #]
    #h_ranges_values = [
    #    "小时数",
    #    h_ranges[0],
    #    h_ranges[1],
    #    h_ranges[2],
    #    h_ranges[3],
    #    h_ranges[4]
    #]
    #h_ranges_table = np.column_stack((h_ranges_labels, h_ranges_values))
    #st.table(h_ranges_table)
#-------------------------------------------------------------
elif temperature_type == "Dry Bulb Temperature/干球温度":
    #dry_bulb_temps
    #<settings
    dry_bulb_temps_select = epw.dry_bulb_temperature.filter_by_analysis_period(range_select)
    dry_bulb_temps_full = epw.dry_bulb_temperature.filter_by_analysis_period(range_full)
    dry_bulb_temps_day = epw.dry_bulb_temperature.filter_by_analysis_period(range_day)
    
    temperature_values_select = dry_bulb_temps_select.values
    temperature_values_full = dry_bulb_temps_full.values
    temperature_values_day = dry_bulb_temps_day.values
    
    min_temp_select = np.min(temperature_values_select)
    max_temp_select = np.max(temperature_values_select)
    min_temp_full = np.min(temperature_values_full)
    max_temp_full = np.max(temperature_values_full)
    
    color_values_select = [map_temperature_to_color(temp, min_temp_select, max_temp_select, color_scheme) for temp in temperature_values_select]
    color_values_day = [map_temperature_to_color(temp, min_temp_select, max_temp_select, color_scheme) for temp in temperature_values_day]
    color_values_full = [map_temperature_to_color(temp, min_temp_full, max_temp_full, color_scheme) for temp in temperature_values_full]
    
    #settings>
    
    #fig_dry1
    fig_dry1 = go.Figure(data=[go.Bar(x=list(range(len(temperature_values_select))), y=temperature_values_select, marker_color=color_values_select)])
    fig_dry1.update_layout(
        title=f"Hourly Dry Bulb Temperature from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Dry Bulb Temperature (°C)"
    )
    bar_width = 0.05
    fig_dry1.update_traces(marker=dict(line=dict(width=bar_width)))

    # Add legend to fig_dry1
    legend_labels_dry1 = np.linspace(min_temp_select, max_temp_select, num=8)
    legend_labels_dry1 = [round(label, 2) for label in legend_labels_dry1]
    fig_dry1.update_layout(legend_title="Temperature (°C)")
    fig_dry1.update_traces(legendgroup="temp_legend_dry1", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}°C")
    for i, label in enumerate(legend_labels_dry1):
        fig_dry1.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_temp_select, max_temp_select, color_scheme)), name=f"{label}°C", hoverinfo="name"))
    
    st.plotly_chart(fig_dry1, use_container_width=True)
    
    #fig_dry2
    # Assuming your dry_bulb_temps_day is a DataFrame with a DatetimeIndex
    df_day = pd.DataFrame({"Temperature": temperature_values_day}, index=dry_bulb_temps_day.datetimes)
    daily_averages = df_day.resample('D').mean()
    min_temp_daily_avg = daily_averages.min().iloc[0]  # Minimum value for the daily average
    max_temp_daily_avg = daily_averages.max().iloc[0]  # Maximum value for the daily average
    color_values_day = [map_temperature_to_color(temp, min_temp_daily_avg, max_temp_daily_avg, color_scheme) for temp in daily_averages["Temperature"]]
    
    fig_dry2 = go.Figure(data=[go.Bar(x=daily_averages.index.dayofyear, y=daily_averages["Temperature"], marker_color=color_values_day)])  # Use color_values_day here
    fig_dry2.update_layout(
        title=f"Daily Dry Bulb Temperature from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Dry Bulb Temperature (°C)"
    )
    
    # Add legend to fig_dry2 (with filtering functionality)
    legend_labels_dry2 = np.linspace(min_temp_daily_avg, max_temp_daily_avg, num=8)
    legend_labels_dry2 = [round(label, 2) for label in legend_labels_dry2]
    fig_dry2.update_layout(legend_title="Temperature (°C)")
    fig_dry2.update_traces(legendgroup="temp_legend_dry2", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}°C")
    for i, label in enumerate(legend_labels_dry2):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_dry2.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_temp_daily_avg, max_temp_daily_avg, color_scheme)), name=f"{label}°C", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_dry2, use_container_width=True)
    
    #fig_dry3
    # Calculate monthly average temperatures using Pandas
    df = pd.DataFrame({"Temperature": temperature_values_full})
    df["Month"] = pd.to_datetime(dry_bulb_temps_full.datetimes).month
    monthly_averages = df.groupby("Month")["Temperature"].mean()
    
    # Calculate average temperature for each month
    full_year_monthly_averages = [monthly_averages[month] for month in range(1, 13)]
    
    # Map average temperatures to colors
    min_avg_temp = min(full_year_monthly_averages)
    max_avg_temp = max(full_year_monthly_averages)
    avg_color_values = [map_temperature_to_color(temp, min_avg_temp, max_avg_temp, color_scheme) for temp in full_year_monthly_averages]
    
    fig_dry3 = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages, marker_color=avg_color_values)])
    fig_dry3.update_layout(
        title="Monthly Average Dry Bulb Temperature",
        xaxis_title="Month",
        yaxis_title="Average Dry Bulb Temperature (°C)"
    )
    
    # Force x-axis tick labels to display all months
    fig_dry3.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_dry3
    legend_labels_dry3 = np.linspace(min_temp_full, max_temp_full, num=8)
    legend_labels_dry3 = [round(label, 2) for label in legend_labels_dry3]
    fig_dry3.update_layout(legend_title="Temperature (°C)")
    fig_dry3.update_traces(legendgroup="temp_legend_dry3", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}°C")
    for i, label in enumerate(legend_labels_dry3):
        visible = True if i == 0 else "legendonly"
        fig_dry3.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_temp_full, max_temp_full, color_scheme)), name=f"{label}°C", hoverinfo="name"))
    
    st.plotly_chart(fig_dry3, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Dew Point Temperature/露点温度":
 # dew_point_temps
    #<settings
    dew_point_temps_select = epw.dew_point_temperature.filter_by_analysis_period(range_select)
    dew_point_temps_full = epw.dew_point_temperature.filter_by_analysis_period(range_full)
    dew_point_temps_day = epw.dew_point_temperature.filter_by_analysis_period(range_day)
    
    temperature_values_select = dew_point_temps_select.values
    temperature_values_full = dew_point_temps_full.values
    temperature_values_day = dew_point_temps_day.values
    
    min_temp_select = np.min(temperature_values_select)
    max_temp_select = np.max(temperature_values_select)
    min_temp_full = np.min(temperature_values_full)
    max_temp_full = np.max(temperature_values_full)
    
    color_values_select = [map_temperature_to_color(temp, min_temp_select, max_temp_select, color_scheme) for temp in temperature_values_select]
    color_values_day = [map_temperature_to_color(temp, min_temp_select, max_temp_select, color_scheme) for temp in temperature_values_day]
    color_values_full = [map_temperature_to_color(temp, min_temp_full, max_temp_full, color_scheme) for temp in temperature_values_full]
    #settings>
    
    # fig_dew1
    fig_dew1 = go.Figure(data=[go.Bar(x=list(range(len(temperature_values_select))), y=temperature_values_select, marker_color=color_values_select)])
    fig_dew1.update_layout(
        title=f"Hourly Dew Point Temperature from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Dew Point Temperature (°C)"
    )
    bar_width = 0.05
    fig_dew1.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_dew1
    legend_labels_dew1 = np.linspace(min_temp_select, max_temp_select, num=8)
    legend_labels_dew1 = [round(label, 2) for label in legend_labels_dew1]
    fig_dew1.update_layout(legend_title="Temperature (°C)")
    fig_dew1.update_traces(legendgroup="temp_legend_dew1", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}°C")
    for i, label in enumerate(legend_labels_dew1):
        fig_dew1.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_temp_select, max_temp_select, color_scheme)), name=f"{label}°C", hoverinfo="name"))
    
    st.plotly_chart(fig_dew1, use_container_width=True)
    
    # fig_dew2
    # Assuming your dew_point_temps_day is a DataFrame with a DatetimeIndex
    df_day_dew = pd.DataFrame({"Temperature": temperature_values_day}, index=dew_point_temps_day.datetimes)
    daily_averages_dew = df_day_dew.resample('D').mean()
    min_temp_daily_avg_dew = daily_averages_dew.min().iloc[0]  # Minimum value for the daily average
    max_temp_daily_avg_dew = daily_averages_dew.max().iloc[0]  # Maximum value for the daily average
    color_values_day_dew = [map_temperature_to_color(temp, min_temp_daily_avg_dew, max_temp_daily_avg_dew, color_scheme) for temp in daily_averages_dew["Temperature"]]
    
    fig_dew2 = go.Figure(data=[go.Bar(x=daily_averages_dew.index.dayofyear, y=daily_averages_dew["Temperature"], marker_color=color_values_day_dew)])  # Use color_values_day_dew here
    fig_dew2.update_layout(
        title=f"Daily Dew Point Temperature from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Dew Point Temperature (°C)"
    )
    
    # Add legend to fig_dew2 (with filtering functionality)
    legend_labels_dew2 = np.linspace(min_temp_daily_avg_dew, max_temp_daily_avg_dew, num=8)
    legend_labels_dew2 = [round(label, 2) for label in legend_labels_dew2]
    fig_dew2.update_layout(legend_title="Temperature (°C)")
    fig_dew2.update_traces(legendgroup="temp_legend_dew2", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}°C")
    for i, label in enumerate(legend_labels_dew2):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_dew2.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_temp_daily_avg_dew, max_temp_daily_avg_dew, color_scheme)), name=f"{label}°C", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_dew2, use_container_width=True)
    
    # fig_dew3
    # Calculate monthly average temperatures using Pandas
    df_dew = pd.DataFrame({"Temperature": temperature_values_full})
    df_dew["Month"] = pd.to_datetime(dew_point_temps_full.datetimes).month
    monthly_averages_dew = df_dew.groupby("Month")["Temperature"].mean()
    
    # Calculate average temperature for each month
    full_year_monthly_averages_dew = [monthly_averages_dew[month] for month in range(1, 13)]
    
    # Map average temperatures to colors
    min_avg_temp_dew = min(full_year_monthly_averages_dew)
    max_avg_temp_dew = max(full_year_monthly_averages_dew)
    avg_color_values_dew = [map_temperature_to_color(temp, min_avg_temp_dew, max_avg_temp_dew, color_scheme) for temp in full_year_monthly_averages_dew]
    
    fig_dew3 = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_dew, marker_color=avg_color_values_dew)])
    fig_dew3.update_layout(
        title="Monthly Average Dew Point Temperature",
        xaxis_title="Month",
        yaxis_title="Average Dew Point Temperature (°C)"
    )
    
    # Force x-axis tick labels to display all months
    fig_dew3.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_dew3
    legend_labels_dew3 = np.linspace(min_temp_full, max_temp_full, num=8)
    legend_labels_dew3 = [round(label, 2) for label in legend_labels_dew3]
    fig_dew3.update_layout(legend_title="Temperature (°C)")
    fig_dew3.update_traces(legendgroup="temp_legend_dew3", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}°C")
    for i, label in enumerate(legend_labels_dew3):
        visible = True if i == 0 else "legendonly"
        fig_dew3.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_temp_full, max_temp_full, color_scheme)), name=f"{label}°C", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_dew3, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Relative Humidity/相对湿度":
    #relative_humidity
    #<settings
    relative_humidity_select = epw.relative_humidity.filter_by_analysis_period(range_select)
    relative_humidity_full = epw.relative_humidity.filter_by_analysis_period(range_full)
    relative_humidity_day = epw.relative_humidity.filter_by_analysis_period(range_day)
    
    humidity_values_select = relative_humidity_select.values
    humidity_values_full = relative_humidity_full.values
    humidity_values_day = relative_humidity_day.values
    
    min_humidity_select = np.min(humidity_values_select)
    max_humidity_select = np.max(humidity_values_select)
    min_humidity_full = np.min(humidity_values_full)
    max_humidity_full = np.max(humidity_values_full)
    
    color_values_select_humidity = [map_temperature_to_color(humidity, min_humidity_select, max_humidity_select, color_scheme) for humidity in humidity_values_select]
    color_values_day_humidity = [map_temperature_to_color(humidity, min_humidity_select, max_humidity_select, color_scheme) for humidity in humidity_values_day]
    color_values_full_humidity = [map_temperature_to_color(humidity, min_humidity_full, max_humidity_full, color_scheme) for humidity in humidity_values_full]
    #settings>
    
    #fig_humidity1
    fig_humidity1 = go.Figure(data=[go.Bar(x=list(range(len(humidity_values_select))), y=humidity_values_select, marker_color=color_values_select_humidity)])
    fig_humidity1.update_layout(
        title=f"Hourly Relative Humidity from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Relative Humidity"
    )
    bar_width = 0.05
    fig_humidity1.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_humidity1
    legend_labels_humidity1 = np.linspace(min_humidity_select, max_humidity_select, num=8)
    legend_labels_humidity1 = [round(label, 2) for label in legend_labels_humidity1]
    fig_humidity1.update_layout(legend_title="Relative Humidity (%)")
    fig_humidity1.update_traces(legendgroup="humidity_legend1", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}%")
    for i, label in enumerate(legend_labels_humidity1):
        fig_humidity1.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_humidity_select, max_humidity_select, color_scheme)), name=f"{label}%", hoverinfo="name"))
    
    st.plotly_chart(fig_humidity1, use_container_width=True)
    
    #fig_humidity2
    # Assuming your relative_humidity_day is a DataFrame with a DatetimeIndex
    df_day_humidity = pd.DataFrame({"Humidity": humidity_values_day}, index=relative_humidity_day.datetimes)
    daily_averages_humidity = df_day_humidity.resample('D').mean()
    min_humidity_daily_avg = daily_averages_humidity.min().iloc[0]  # Minimum value for the daily average
    max_humidity_daily_avg = daily_averages_humidity.max().iloc[0]  # Maximum value for the daily average
    color_values_day_humidity = [map_temperature_to_color(humidity, min_humidity_daily_avg, max_humidity_daily_avg, color_scheme) for humidity in daily_averages_humidity["Humidity"]]
    
    fig_humidity2 = go.Figure(data=[go.Bar(x=daily_averages_humidity.index.dayofyear, y=daily_averages_humidity["Humidity"], marker_color=color_values_day_humidity)])  # Use color_values_day_humidity here
    fig_humidity2.update_layout(
        title=f"Daily Relative Humidity from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Relative Humidity (%)"
    )
    
    # Add legend to fig_humidity2 (with filtering functionality)
    legend_labels_humidity2 = np.linspace(min_humidity_daily_avg, max_humidity_daily_avg, num=8)
    legend_labels_humidity2 = [round(label, 2) for label in legend_labels_humidity2]
    fig_humidity2.update_layout(legend_title="Relative Humidity (%)")
    fig_humidity2.update_traces(legendgroup="humidity_legend2", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}%")
    for i, label in enumerate(legend_labels_humidity2):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_humidity2.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_humidity_daily_avg, max_humidity_daily_avg, color_scheme)), name=f"{label}%", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_humidity2, use_container_width=True)
    
    
    #fig_humidity3
    # Calculate monthly average relative humidities using Pandas
    df_humidity = pd.DataFrame({"Humidity": humidity_values_full})
    df_humidity["Month"] = pd.to_datetime(relative_humidity_full.datetimes).month
    monthly_averages_humidity = df_humidity.groupby("Month")["Humidity"].mean()
    
    # Calculate average relative humidity for each month
    full_year_monthly_averages_humidity = [monthly_averages_humidity[month] for month in range(1, 13)]
    
    # Map average relative humidities to colors using the same color scheme
    min_avg_humidity = min(full_year_monthly_averages_humidity)
    max_avg_humidity = max(full_year_monthly_averages_humidity)
    avg_color_values_humidity = [map_temperature_to_color(humidity, min_avg_humidity, max_avg_humidity, color_scheme) for humidity in full_year_monthly_averages_humidity]
    
    fig_humidity3 = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_humidity, marker_color=avg_color_values_humidity)])
    fig_humidity3.update_layout(
        title="Monthly Average Relative Humidity",
        xaxis_title="Month",
        yaxis_title="Average Relative Humidity (%)"
    )
    
    # Force x-axis tick labels to display all months
    fig_humidity3.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_humidity3
    legend_labels_humidity3 = np.linspace(min_avg_humidity, max_avg_humidity, num=8)
    legend_labels_humidity3 = [round(label, 2) for label in legend_labels_humidity3]
    fig_humidity3.update_layout(legend_title="Relative Humidity (%)")
    fig_humidity3.update_traces(legendgroup="humidity_legend3", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}%")
    for i, label in enumerate(legend_labels_humidity3):
        fig_humidity3.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_avg_humidity, max_avg_humidity, color_scheme)), name=f"{label}%", hoverinfo="name"))
    
    st.plotly_chart(fig_humidity3, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Wind Speed/风速":
    #wind_speed
    #<settings
    wind_speed_select = epw.wind_speed.filter_by_analysis_period(range_select)
    wind_speed_full = epw.wind_speed.filter_by_analysis_period(range_full)
    wind_speed_day = epw.wind_speed.filter_by_analysis_period(range_day)
    
    speed_values_select = wind_speed_select.values
    speed_values_full = wind_speed_full.values
    speed_values_day = wind_speed_day.values
    
    min_speed_select = np.min(speed_values_select)
    max_speed_select = np.max(speed_values_select)
    min_speed_full = np.min(speed_values_full)
    max_speed_full = np.max(speed_values_full)
    
    color_values_select_speed = [map_temperature_to_color(speed, min_speed_select, max_speed_select, color_scheme) for speed in speed_values_select]
    color_values_day_speed = [map_temperature_to_color(speed, min_speed_select, max_speed_select, color_scheme) for speed in speed_values_day]
    color_values_full_speed = [map_temperature_to_color(speed, min_speed_full, max_speed_full, color_scheme) for speed in speed_values_full]
    #settings>
    
    #fig_speed1
    fig_speed1 = go.Figure(data=[go.Bar(x=list(range(len(speed_values_select))), y=speed_values_select, marker_color=color_values_select_speed)])
    fig_speed1.update_layout(
        title=f"Hourly Wind Speed from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Wind Speed (m/s)"
    )
    bar_width = 0.05
    fig_speed1.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_speed1
    legend_labels_speed1 = np.linspace(min_speed_select, max_speed_select, num=8)
    legend_labels_speed1 = [round(label, 2) for label in legend_labels_speed1]
    fig_speed1.update_layout(legend_title="Wind Speed (m/s)")
    fig_speed1.update_traces(legendgroup="speed_legend1", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} m/s")
    for i, label in enumerate(legend_labels_speed1):
        fig_speed1.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_speed_select, max_speed_select, color_scheme)), name=f"{label} m/s", hoverinfo="name"))
    
    st.plotly_chart(fig_speed1, use_container_width=True)
    
    #fig_speed2
    # Assuming your wind_speed_day is a DataFrame with a DatetimeIndex
    df_day_speed = pd.DataFrame({"Speed": speed_values_day}, index=wind_speed_day.datetimes)
    daily_averages_speed = df_day_speed.resample('D').mean()
    min_speed_daily_avg = daily_averages_speed.min().iloc[0]  # Minimum value for the daily average
    max_speed_daily_avg = daily_averages_speed.max().iloc[0]  # Maximum value for the daily average
    color_values_day_speed = [map_temperature_to_color(speed, min_speed_daily_avg, max_speed_daily_avg, color_scheme) for speed in daily_averages_speed["Speed"]]
    
    fig_speed2 = go.Figure(data=[go.Bar(x=daily_averages_speed.index.dayofyear, y=daily_averages_speed["Speed"], marker_color=color_values_day_speed)])  # Use color_values_day_speed here
    fig_speed2.update_layout(
        title=f"Daily Wind Speed from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Wind Speed (m/s)"
    )
    
    # Add legend to fig_speed2 (with filtering functionality)
    legend_labels_speed2 = np.linspace(min_speed_daily_avg, max_speed_daily_avg, num=8)
    legend_labels_speed2 = [round(label, 2) for label in legend_labels_speed2]
    fig_speed2.update_layout(legend_title="Wind Speed (m/s)")
    fig_speed2.update_traces(legendgroup="speed_legend2", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} m/s")
    for i, label in enumerate(legend_labels_speed2):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_speed2.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_speed_daily_avg, max_speed_daily_avg, color_scheme)), name=f"{label} m/s", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_speed2, use_container_width=True)
    
    #fig_speed3
    # Calculate monthly average wind speeds using Pandas
    df_speed = pd.DataFrame({"Speed": speed_values_full})
    df_speed["Month"] = pd.to_datetime(wind_speed_full.datetimes).month
    monthly_averages_speed = df_speed.groupby("Month")["Speed"].mean()
    
    # Calculate average wind speed for each month
    full_year_monthly_averages_speed = [monthly_averages_speed[month] for month in range(1, 13)]
    
    # Map average wind speeds to colors using the same color scheme
    min_avg_speed = min(full_year_monthly_averages_speed)
    max_avg_speed = max(full_year_monthly_averages_speed)
    avg_color_values_speed = [map_temperature_to_color(speed, min_avg_speed, max_avg_speed, color_scheme) for speed in full_year_monthly_averages_speed]
    
    fig_speed3 = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_speed, marker_color=avg_color_values_speed)])
    fig_speed3.update_layout(
        title="Monthly Average Wind Speed",
        xaxis_title="Month",
        yaxis_title="Average Wind Speed (m/s)"
    )
    
    # Force x-axis tick labels to display all months
    fig_speed3.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_speed3
    legend_labels_speed3 = np.linspace(min_avg_speed, max_avg_speed, num=8)
    legend_labels_speed3 = [round(label, 2) for label in legend_labels_speed3]
    fig_speed3.update_layout(legend_title="Wind Speed (m/s)")
    fig_speed3.update_traces(legendgroup="speed_legend3", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} m/s")
    for i, label in enumerate(legend_labels_speed3):
        fig_speed3.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_avg_speed, max_avg_speed, color_scheme)), name=f"{label} m/s", hoverinfo="name"))
    
    st.plotly_chart(fig_speed3, use_container_width=True)    

#-------------------------------------------------------------
elif temperature_type == "Wind Rose/风玫瑰图":
    month=ap.AnalysisPeriod(st_month=i,end_month=j)
    a = epw.wind_direction.filter_by_analysis_period(month)
    b = epw.wind_speed.filter_by_analysis_period(month)
    windRose= wr.WindRose(a,b,8)
    figure = ladybug_charts.to_figure.wind_rose(windRose)
    figure.update_layout(title= "Windrose From Month "+ str(i) +" To Month "+ str(j))
    st.plotly_chart(figure, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Direct Normal Rad/直接法线辐射":
    # direct_normal_rad
    #<settings
    direct_normal_rad_select = epw.direct_normal_radiation.filter_by_analysis_period(range_select)
    direct_normal_rad_full = epw.direct_normal_radiation.filter_by_analysis_period(range_full)
    direct_normal_rad_day = epw.direct_normal_radiation.filter_by_analysis_period(range_day)
    
    radiation_values_select = direct_normal_rad_select.values
    radiation_values_full = direct_normal_rad_full.values
    radiation_values_day = direct_normal_rad_day.values
    
    min_rad_select = np.min(radiation_values_select)
    max_rad_select = np.max(radiation_values_select)
    min_rad_full = np.min(radiation_values_full)
    max_rad_full = np.max(radiation_values_full)
    
    color_values_select = [map_temperature_to_color(rad, min_rad_select, max_rad_select, color_scheme) for rad in radiation_values_select]
    color_values_day = [map_temperature_to_color(rad, min_rad_select, max_rad_select, color_scheme) for rad in radiation_values_day]
    color_values_full = [map_temperature_to_color(rad, min_rad_full, max_rad_full, color_scheme) for rad in radiation_values_full]
    #settings>
    
    # fig_rad1
    fig_rad1 = go.Figure(data=[go.Bar(x=list(range(len(radiation_values_select))), y=radiation_values_select, marker_color=color_values_select)])
    fig_rad1.update_layout(
        title=f"Hourly Direct Normal Radiation from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Direct Normal Radiation (W/m²)"
    )
    bar_width = 0.05
    fig_rad1.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_rad1
    legend_labels_rad1 = np.linspace(min_rad_select, max_rad_select, num=8)
    legend_labels_rad1 = [round(label, 2) for label in legend_labels_rad1]
    fig_rad1.update_layout(legend_title="Radiation (W/m²)")
    fig_rad1.update_traces(legendgroup="temp_legend_rad1", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad1):
        fig_rad1.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_select, max_rad_select, color_scheme)), name=f"{label} W/m²", hoverinfo="name"))
    
    st.plotly_chart(fig_rad1, use_container_width=True)
    
    # fig_rad2
    # Assuming your direct_normal_rad_day is a DataFrame with a DatetimeIndex
    df_day_rad = pd.DataFrame({"Radiation": radiation_values_day}, index=direct_normal_rad_day.datetimes)
    daily_averages_rad = df_day_rad.resample('D').mean()
    min_rad_daily_avg = daily_averages_rad.min().iloc[0]  # Minimum value for the daily average
    max_rad_daily_avg = daily_averages_rad.max().iloc[0]  # Maximum value for the daily average
    color_values_day_rad = [map_temperature_to_color(rad, min_rad_daily_avg, max_rad_daily_avg, color_scheme) for rad in daily_averages_rad["Radiation"]]
    
    fig_rad2 = go.Figure(data=[go.Bar(x=daily_averages_rad.index.dayofyear, y=daily_averages_rad["Radiation"], marker_color=color_values_day_rad)])  # Use color_values_day_rad here
    fig_rad2.update_layout(
        title=f"Daily Direct Normal Radiation from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Direct Normal Radiation (W/m²)"
    )
    
    # Add legend to fig_rad2 (with filtering functionality)
    legend_labels_rad2 = np.linspace(min_rad_daily_avg, max_rad_daily_avg, num=8)
    legend_labels_rad2 = [round(label, 2) for label in legend_labels_rad2]
    fig_rad2.update_layout(legend_title="Radiation (W/m²)")
    fig_rad2.update_traces(legendgroup="temp_legend_rad2", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad2):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_rad2.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_daily_avg, max_rad_daily_avg, color_scheme)), name=f"{label} W/m²", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_rad2, use_container_width=True)
    
    # fig_rad3
    # Calculate monthly average radiation using Pandas
    df_rad = pd.DataFrame({"Radiation": radiation_values_full})
    df_rad["Month"] = pd.to_datetime(direct_normal_rad_full.datetimes).month
    monthly_averages_rad = df_rad.groupby("Month")["Radiation"].mean()
    
    # Calculate average radiation for each month
    full_year_monthly_averages_rad = [monthly_averages_rad[month] for month in range(1, 13)]
    
    # Map average radiation to colors
    min_avg_rad = min(full_year_monthly_averages_rad)
    max_avg_rad = max(full_year_monthly_averages_rad)
    avg_color_values_rad = [map_temperature_to_color(rad, min_avg_rad, max_avg_rad, color_scheme) for rad in full_year_monthly_averages_rad]
    
    fig_rad3 = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_rad, marker_color=avg_color_values_rad)])
    fig_rad3.update_layout(
        title="Monthly Average Direct Normal Radiation",
        xaxis_title="Month",
        yaxis_title="Average Direct Normal Radiation (W/m²)"
    )
    
    # Force x-axis tick labels to display all months
    fig_rad3.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_rad3
    legend_labels_rad3 = np.linspace(min_rad_full, max_rad_full, num=8)
    legend_labels_rad3 = [round(label, 2) for label in legend_labels_rad3]
    fig_rad3.update_layout(legend_title="Radiation (W/m²)")
    fig_rad3.update_traces(legendgroup="temp_legend_rad3", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad3):
        visible = True if i == 0 else "legendonly"
        fig_rad3.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_full, max_rad_full, color_scheme)), name=f"{label} W/m²", hoverinfo="name"))
    
    st.plotly_chart(fig_rad3, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Diffuse Horizontal Rad/散射水平辐射":
    # diffuse_horizontal_rad
    #<settings
    diffuse_horizontal_rad_select = epw.diffuse_horizontal_radiation.filter_by_analysis_period(range_select)
    diffuse_horizontal_rad_full = epw.diffuse_horizontal_radiation.filter_by_analysis_period(range_full)
    diffuse_horizontal_rad_day = epw.diffuse_horizontal_radiation.filter_by_analysis_period(range_day)
    
    radiation_values_select_diffuse = diffuse_horizontal_rad_select.values
    radiation_values_full_diffuse = diffuse_horizontal_rad_full.values
    radiation_values_day_diffuse = diffuse_horizontal_rad_day.values
    
    min_rad_select_diffuse = np.min(radiation_values_select_diffuse)
    max_rad_select_diffuse = np.max(radiation_values_select_diffuse)
    min_rad_full_diffuse = np.min(radiation_values_full_diffuse)
    max_rad_full_diffuse = np.max(radiation_values_full_diffuse)
    
    color_values_select_diffuse = [map_temperature_to_color(rad, min_rad_select_diffuse, max_rad_select_diffuse, color_scheme) for rad in radiation_values_select_diffuse]
    color_values_day_diffuse = [map_temperature_to_color(rad, min_rad_select_diffuse, max_rad_select_diffuse, color_scheme) for rad in radiation_values_day_diffuse]
    color_values_full_diffuse = [map_temperature_to_color(rad, min_rad_full_diffuse, max_rad_full_diffuse, color_scheme) for rad in radiation_values_full_diffuse]
    #settings>
    
    # fig_rad1_diffuse
    fig_rad1_diffuse = go.Figure(data=[go.Bar(x=list(range(len(radiation_values_select_diffuse))), y=radiation_values_select_diffuse, marker_color=color_values_select_diffuse)])
    fig_rad1_diffuse.update_layout(
        title=f"Hourly Diffuse Horizontal Radiation from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Diffuse Horizontal Radiation (W/m²)"
    )
    bar_width = 0.05
    fig_rad1_diffuse.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_rad1_diffuse
    legend_labels_rad1_diffuse = np.linspace(min_rad_select_diffuse, max_rad_select_diffuse, num=8)
    legend_labels_rad1_diffuse = [round(label, 2) for label in legend_labels_rad1_diffuse]
    fig_rad1_diffuse.update_layout(legend_title="Radiation (W/m²)")
    fig_rad1_diffuse.update_traces(legendgroup="temp_legend_rad1_diffuse", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad1_diffuse):
        fig_rad1_diffuse.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_select_diffuse, max_rad_select_diffuse, color_scheme)), name=f"{label} W/m²", hoverinfo="name"))
    
    st.plotly_chart(fig_rad1_diffuse, use_container_width=True)
    
    # fig_rad2_diffuse
    # Assuming your diffuse_horizontal_rad_day is a DataFrame with a DatetimeIndex
    df_day_rad_diffuse = pd.DataFrame({"Radiation": radiation_values_day_diffuse}, index=diffuse_horizontal_rad_day.datetimes)
    daily_averages_rad_diffuse = df_day_rad_diffuse.resample('D').mean()
    min_rad_daily_avg_diffuse = daily_averages_rad_diffuse.min().iloc[0]  # Minimum value for the daily average
    max_rad_daily_avg_diffuse = daily_averages_rad_diffuse.max().iloc[0]  # Maximum value for the daily average
    color_values_day_rad_diffuse = [map_temperature_to_color(rad, min_rad_daily_avg_diffuse, max_rad_daily_avg_diffuse, color_scheme) for rad in daily_averages_rad_diffuse["Radiation"]]
    
    fig_rad2_diffuse = go.Figure(data=[go.Bar(x=daily_averages_rad_diffuse.index.dayofyear, y=daily_averages_rad_diffuse["Radiation"], marker_color=color_values_day_rad_diffuse)])  # Use color_values_day_rad_diffuse here
    fig_rad2_diffuse.update_layout(
        title=f"Daily Diffuse Horizontal Radiation from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Diffuse Horizontal Radiation (W/m²)"
    )
    
    # Add legend to fig_rad2_diffuse (with filtering functionality)
    legend_labels_rad2_diffuse = np.linspace(min_rad_daily_avg_diffuse, max_rad_daily_avg_diffuse, num=8)
    legend_labels_rad2_diffuse = [round(label, 2) for label in legend_labels_rad2_diffuse]
    fig_rad2_diffuse.update_layout(legend_title="Radiation (W/m²)")
    fig_rad2_diffuse.update_traces(legendgroup="temp_legend_rad2_diffuse", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad2_diffuse):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_rad2_diffuse.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_daily_avg_diffuse, max_rad_daily_avg_diffuse, color_scheme)), name=f"{label} W/m²", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_rad2_diffuse, use_container_width=True)
    
    # fig_rad3_diffuse
    # Calculate monthly average radiation using Pandas
    df_rad_diffuse = pd.DataFrame({"Radiation": radiation_values_full_diffuse})
    df_rad_diffuse["Month"] = pd.to_datetime(diffuse_horizontal_rad_full.datetimes).month
    monthly_averages_rad_diffuse = df_rad_diffuse.groupby("Month")["Radiation"].mean()
    
    # Calculate average radiation for each month
    full_year_monthly_averages_rad_diffuse = [monthly_averages_rad_diffuse[month] for month in range(1, 13)]
    
    # Map average radiation to colors
    min_avg_rad_diffuse = min(full_year_monthly_averages_rad_diffuse)
    max_avg_rad_diffuse = max(full_year_monthly_averages_rad_diffuse)
    avg_color_values_rad_diffuse = [map_temperature_to_color(rad, min_avg_rad_diffuse, max_avg_rad_diffuse, color_scheme) for rad in full_year_monthly_averages_rad_diffuse]
    
    fig_rad3_diffuse = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_rad_diffuse, marker_color=avg_color_values_rad_diffuse)])
    fig_rad3_diffuse.update_layout(
        title="Monthly Average Diffuse Horizontal Radiation",
        xaxis_title="Month",
        yaxis_title="Average Diffuse Horizontal Radiation (W/m²)"
    )
    
    # Force x-axis tick labels to display all months
    fig_rad3_diffuse.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_rad3_diffuse
    legend_labels_rad3_diffuse = np.linspace(min_rad_full_diffuse, max_rad_full_diffuse, num=8)
    legend_labels_rad3_diffuse = [round(label, 2) for label in legend_labels_rad3_diffuse]
    fig_rad3_diffuse.update_layout(legend_title="Radiation (W/m²)")
    fig_rad3_diffuse.update_traces(legendgroup="temp_legend_rad3_diffuse", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad3_diffuse):
        visible = True if i == 0 else "legendonly"
        fig_rad3_diffuse.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_full_diffuse, max_rad_full_diffuse, color_scheme)), name=f"{label} W/m²", hoverinfo="name"))
    
    st.plotly_chart(fig_rad3_diffuse, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Global Horizontal Rad/全球水平辐射":
    # global_horizontal_rad
    #<settings
    global_horizontal_rad_select = epw.global_horizontal_radiation.filter_by_analysis_period(range_select)
    global_horizontal_rad_full = epw.global_horizontal_radiation.filter_by_analysis_period(range_full)
    global_horizontal_rad_day = epw.global_horizontal_radiation.filter_by_analysis_period(range_day)
    
    radiation_values_select_global = global_horizontal_rad_select.values
    radiation_values_full_global = global_horizontal_rad_full.values
    radiation_values_day_global = global_horizontal_rad_day.values
    
    min_rad_select_global = np.min(radiation_values_select_global)
    max_rad_select_global = np.max(radiation_values_select_global)
    min_rad_full_global = np.min(radiation_values_full_global)
    max_rad_full_global = np.max(radiation_values_full_global)
    
    color_values_select_global = [map_temperature_to_color(rad, min_rad_select_global, max_rad_select_global, color_scheme) for rad in radiation_values_select_global]
    color_values_day_global = [map_temperature_to_color(rad, min_rad_select_global, max_rad_select_global, color_scheme) for rad in radiation_values_day_global]
    color_values_full_global = [map_temperature_to_color(rad, min_rad_full_global, max_rad_full_global, color_scheme) for rad in radiation_values_full_global]
    #settings>
    
    # fig_rad1_global
    fig_rad1_global = go.Figure(data=[go.Bar(x=list(range(len(radiation_values_select_global))), y=radiation_values_select_global, marker_color=color_values_select_global)])
    fig_rad1_global.update_layout(
        title=f"Hourly Global Horizontal Radiation from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Global Horizontal Radiation (W/m²)"
    )
    bar_width = 0.05
    fig_rad1_global.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_rad1_global
    legend_labels_rad1_global = np.linspace(min_rad_select_global, max_rad_select_global, num=8)
    legend_labels_rad1_global = [round(label, 2) for label in legend_labels_rad1_global]
    fig_rad1_global.update_layout(legend_title="Radiation (W/m²)")
    fig_rad1_global.update_traces(legendgroup="temp_legend_rad1_global", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad1_global):
        fig_rad1_global.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_select_global, max_rad_select_global, color_scheme)), name=f"{label} W/m²", hoverinfo="name"))
    
    st.plotly_chart(fig_rad1_global, use_container_width=True)
    
    # fig_rad2_global
    # Assuming your global_horizontal_rad_day is a DataFrame with a DatetimeIndex
    df_day_rad_global = pd.DataFrame({"Radiation": radiation_values_day_global}, index=global_horizontal_rad_day.datetimes)
    daily_averages_rad_global = df_day_rad_global.resample('D').mean()
    min_rad_daily_avg_global = daily_averages_rad_global.min().iloc[0]  # Minimum value for the daily average
    max_rad_daily_avg_global = daily_averages_rad_global.max().iloc[0]  # Maximum value for the daily average
    color_values_day_rad_global = [map_temperature_to_color(rad, min_rad_daily_avg_global, max_rad_daily_avg_global, color_scheme) for rad in daily_averages_rad_global["Radiation"]]
    
    fig_rad2_global = go.Figure(data=[go.Bar(x=daily_averages_rad_global.index.dayofyear, y=daily_averages_rad_global["Radiation"], marker_color=color_values_day_rad_global)])  # Use color_values_day_rad_global here
    fig_rad2_global.update_layout(
        title=f"Daily Global Horizontal Radiation from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Global Horizontal Radiation (W/m²)"
    )
    
    # Add legend to fig_rad2_global (with filtering functionality)
    legend_labels_rad2_global = np.linspace(min_rad_daily_avg_global, max_rad_daily_avg_global, num=8)
    legend_labels_rad2_global = [round(label, 2) for label in legend_labels_rad2_global]
    fig_rad2_global.update_layout(legend_title="Radiation (W/m²)")
    fig_rad2_global.update_traces(legendgroup="temp_legend_rad2_global", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad2_global):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_rad2_global.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_daily_avg_global, max_rad_daily_avg_global, color_scheme)), name=f"{label} W/m²", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_rad2_global, use_container_width=True)
    
    # fig_rad3_global
    # Calculate monthly average radiation using Pandas
    df_rad_global = pd.DataFrame({"Radiation": radiation_values_full_global})
    df_rad_global["Month"] = pd.to_datetime(global_horizontal_rad_full.datetimes).month
    monthly_averages_rad_global = df_rad_global.groupby("Month")["Radiation"].mean()
    
    # Calculate average radiation for each month
    full_year_monthly_averages_rad_global = [monthly_averages_rad_global[month] for month in range(1, 13)]
    
    # Map average radiation to colors
    min_avg_rad_global = min(full_year_monthly_averages_rad_global)
    max_avg_rad_global = max(full_year_monthly_averages_rad_global)
    avg_color_values_rad_global = [map_temperature_to_color(rad, min_avg_rad_global, max_avg_rad_global, color_scheme) for rad in full_year_monthly_averages_rad_global]
    
    fig_rad3_global = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_rad_global, marker_color=avg_color_values_rad_global)])
    fig_rad3_global.update_layout(
        title="Monthly Average Global Horizontal Radiation",
        xaxis_title="Month",
        yaxis_title="Average Global Horizontal Radiation (W/m²)"
    )
    
    # Force x-axis tick labels to display all months
    fig_rad3_global.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_rad3_global
    legend_labels_rad3_global = np.linspace(min_rad_full_global, max_rad_full_global, num=8)
    legend_labels_rad3_global = [round(label, 2) for label in legend_labels_rad3_global]
    fig_rad3_global.update_layout(legend_title="Radiation (W/m²)")
    fig_rad3_global.update_traces(legendgroup="temp_legend_rad3_global", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} W/m²")
    for i, label in enumerate(legend_labels_rad3_global):
        visible = True if i == 0 else "legendonly"
        fig_rad3_global.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_rad_full_global, max_rad_full_global, color_scheme)), name=f"{label} W/m²", hoverinfo="name"))
    
    st.plotly_chart(fig_rad3_global, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Direct Normal Ill/直接法线照度": 
    # direct_normal_ill
    #<settings
    direct_normal_ill_select = epw.direct_normal_illuminance.filter_by_analysis_period(range_select)
    direct_normal_ill_full = epw.direct_normal_illuminance.filter_by_analysis_period(range_full)
    direct_normal_ill_day = epw.direct_normal_illuminance.filter_by_analysis_period(range_day)
    
    illuminance_values_select_direct = direct_normal_ill_select.values
    illuminance_values_full_direct = direct_normal_ill_full.values
    illuminance_values_day_direct = direct_normal_ill_day.values
    
    min_ill_select_direct = np.min(illuminance_values_select_direct)
    max_ill_select_direct = np.max(illuminance_values_select_direct)
    min_ill_full_direct = np.min(illuminance_values_full_direct)
    max_ill_full_direct = np.max(illuminance_values_full_direct)
    
    color_values_select_direct = [map_temperature_to_color(ill, min_ill_select_direct, max_ill_select_direct, color_scheme) for ill in illuminance_values_select_direct]
    color_values_day_direct = [map_temperature_to_color(ill, min_ill_select_direct, max_ill_select_direct, color_scheme) for ill in illuminance_values_day_direct]
    color_values_full_direct = [map_temperature_to_color(ill, min_ill_full_direct, max_ill_full_direct, color_scheme) for ill in illuminance_values_full_direct]
    #settings>
    
    # fig_ill1_direct
    fig_ill1_direct = go.Figure(data=[go.Bar(x=list(range(len(illuminance_values_select_direct))), y=illuminance_values_select_direct, marker_color=color_values_select_direct)])
    fig_ill1_direct.update_layout(
        title=f"Hourly Direct Normal Illuminance from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Direct Normal Illuminance (lux)"
    )
    bar_width = 0.05
    fig_ill1_direct.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_ill1_direct
    legend_labels_ill1_direct = np.linspace(min_ill_select_direct, max_ill_select_direct, num=8)
    legend_labels_ill1_direct = [round(label, 2) for label in legend_labels_ill1_direct]
    fig_ill1_direct.update_layout(legend_title="Illuminance (lux)")
    fig_ill1_direct.update_traces(legendgroup="temp_legend_ill1_direct", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill1_direct):
        fig_ill1_direct.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_select_direct, max_ill_select_direct, color_scheme)), name=f"{label} lux", hoverinfo="name"))
    
    st.plotly_chart(fig_ill1_direct, use_container_width=True)
    
    # fig_ill2_direct
    # Assuming your direct_normal_ill_day is a DataFrame with a DatetimeIndex
    df_day_ill_direct = pd.DataFrame({"Illuminance": illuminance_values_day_direct}, index=direct_normal_ill_day.datetimes)
    daily_averages_ill_direct = df_day_ill_direct.resample('D').mean()
    min_ill_daily_avg_direct = daily_averages_ill_direct.min().iloc[0]  # Minimum value for the daily average
    max_ill_daily_avg_direct = daily_averages_ill_direct.max().iloc[0]  # Maximum value for the daily average
    color_values_day_ill_direct = [map_temperature_to_color(ill, min_ill_daily_avg_direct, max_ill_daily_avg_direct, color_scheme) for ill in daily_averages_ill_direct["Illuminance"]]
    
    fig_ill2_direct = go.Figure(data=[go.Bar(x=daily_averages_ill_direct.index.dayofyear, y=daily_averages_ill_direct["Illuminance"], marker_color=color_values_day_ill_direct)])  # Use color_values_day_ill_direct here
    fig_ill2_direct.update_layout(
        title=f"Daily Direct Normal Illuminance from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Direct Normal Illuminance (lux)"
    )
    
    # Add legend to fig_ill2_direct (with filtering functionality)
    legend_labels_ill2_direct = np.linspace(min_ill_daily_avg_direct, max_ill_daily_avg_direct, num=8)
    legend_labels_ill2_direct = [round(label, 2) for label in legend_labels_ill2_direct]
    fig_ill2_direct.update_layout(legend_title="Illuminance (lux)")
    fig_ill2_direct.update_traces(legendgroup="temp_legend_ill2_direct", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill2_direct):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_ill2_direct.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_daily_avg_direct, max_ill_daily_avg_direct, color_scheme)), name=f"{label} lux", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_ill2_direct, use_container_width=True)
    
    # fig_ill3_direct
    # Calculate monthly average illuminance using Pandas
    df_ill_direct = pd.DataFrame({"Illuminance": illuminance_values_full_direct})
    df_ill_direct["Month"] = pd.to_datetime(direct_normal_ill_full.datetimes).month
    monthly_averages_ill_direct = df_ill_direct.groupby("Month")["Illuminance"].mean()
    
    # Calculate average illuminance for each month
    full_year_monthly_averages_ill_direct = [monthly_averages_ill_direct[month] for month in range(1, 13)]
    
    # Map average illuminance to colors
    min_avg_ill_direct = min(full_year_monthly_averages_ill_direct)
    max_avg_ill_direct = max(full_year_monthly_averages_ill_direct)
    avg_color_values_ill_direct = [map_temperature_to_color(ill, min_avg_ill_direct, max_avg_ill_direct, color_scheme) for ill in full_year_monthly_averages_ill_direct]
    
    fig_ill3_direct = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_ill_direct, marker_color=avg_color_values_ill_direct)])
    fig_ill3_direct.update_layout(
        title="Monthly Average Direct Normal Illuminance",
        xaxis_title="Month",
        yaxis_title="Average Direct Normal Illuminance (lux)"
    )
    
    # Force x-axis tick labels to display all months
    fig_ill3_direct.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_ill3_direct
    legend_labels_ill3_direct = np.linspace(min_ill_full_direct, max_ill_full_direct, num=8)
    legend_labels_ill3_direct = [round(label, 2) for label in legend_labels_ill3_direct]
    fig_ill3_direct.update_layout(legend_title="Illuminance (lux)")
    fig_ill3_direct.update_traces(legendgroup="temp_legend_ill3_direct", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill3_direct):
        visible = True if i == 0 else "legendonly"
        fig_ill3_direct.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_full_direct, max_ill_full_direct, color_scheme)), name=f"{label} lux", hoverinfo="name"))
    
    st.plotly_chart(fig_ill3_direct, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Diffuse Horizontal Ill/散射水平照度": 
    # diffuse_horizontal_ill
    #<settings
    diffuse_horizontal_ill_select = epw.diffuse_horizontal_illuminance.filter_by_analysis_period(range_select)
    diffuse_horizontal_ill_full = epw.diffuse_horizontal_illuminance.filter_by_analysis_period(range_full)
    diffuse_horizontal_ill_day = epw.diffuse_horizontal_illuminance.filter_by_analysis_period(range_day)
    
    illuminance_values_select_diffuse = diffuse_horizontal_ill_select.values
    illuminance_values_full_diffuse = diffuse_horizontal_ill_full.values
    illuminance_values_day_diffuse = diffuse_horizontal_ill_day.values
    
    min_ill_select_diffuse = np.min(illuminance_values_select_diffuse)
    max_ill_select_diffuse = np.max(illuminance_values_select_diffuse)
    min_ill_full_diffuse = np.min(illuminance_values_full_diffuse)
    max_ill_full_diffuse = np.max(illuminance_values_full_diffuse)
    
    color_values_select_diffuse = [map_temperature_to_color(ill, min_ill_select_diffuse, max_ill_select_diffuse, color_scheme) for ill in illuminance_values_select_diffuse]
    color_values_day_diffuse = [map_temperature_to_color(ill, min_ill_select_diffuse, max_ill_select_diffuse, color_scheme) for ill in illuminance_values_day_diffuse]
    color_values_full_diffuse = [map_temperature_to_color(ill, min_ill_full_diffuse, max_ill_full_diffuse, color_scheme) for ill in illuminance_values_full_diffuse]
    #settings>
    
    # fig_ill1_diffuse
    fig_ill1_diffuse = go.Figure(data=[go.Bar(x=list(range(len(illuminance_values_select_diffuse))), y=illuminance_values_select_diffuse, marker_color=color_values_select_diffuse)])
    fig_ill1_diffuse.update_layout(
        title=f"Hourly Diffuse Horizontal Illuminance from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Diffuse Horizontal Illuminance (lux)"
    )
    bar_width = 0.05
    fig_ill1_diffuse.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_ill1_diffuse
    legend_labels_ill1_diffuse = np.linspace(min_ill_select_diffuse, max_ill_select_diffuse, num=8)
    legend_labels_ill1_diffuse = [round(label, 2) for label in legend_labels_ill1_diffuse]
    fig_ill1_diffuse.update_layout(legend_title="Illuminance (lux)")
    fig_ill1_diffuse.update_traces(legendgroup="temp_legend_ill1_diffuse", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill1_diffuse):
        fig_ill1_diffuse.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_select_diffuse, max_ill_select_diffuse, color_scheme)), name=f"{label} lux", hoverinfo="name"))
    
    st.plotly_chart(fig_ill1_diffuse, use_container_width=True)
    
    # fig_ill2_diffuse
    # Assuming your diffuse_horizontal_ill_day is a DataFrame with a DatetimeIndex
    df_day_ill_diffuse = pd.DataFrame({"Illuminance": illuminance_values_day_diffuse}, index=diffuse_horizontal_ill_day.datetimes)
    daily_averages_ill_diffuse = df_day_ill_diffuse.resample('D').mean()
    min_ill_daily_avg_diffuse = daily_averages_ill_diffuse.min().iloc[0]  # Minimum value for the daily average
    max_ill_daily_avg_diffuse = daily_averages_ill_diffuse.max().iloc[0]  # Maximum value for the daily average
    color_values_day_ill_diffuse = [map_temperature_to_color(ill, min_ill_daily_avg_diffuse, max_ill_daily_avg_diffuse, color_scheme) for ill in daily_averages_ill_diffuse["Illuminance"]]
    
    fig_ill2_diffuse = go.Figure(data=[go.Bar(x=daily_averages_ill_diffuse.index.dayofyear, y=daily_averages_ill_diffuse["Illuminance"], marker_color=color_values_day_ill_diffuse)])  # Use color_values_day_ill_diffuse here
    fig_ill2_diffuse.update_layout(
        title=f"Daily Diffuse Horizontal Illuminance from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Diffuse Horizontal Illuminance (lux)"
    )
    
    # Add legend to fig_ill2_diffuse (with filtering functionality)
    legend_labels_ill2_diffuse = np.linspace(min_ill_daily_avg_diffuse, max_ill_daily_avg_diffuse, num=8)
    legend_labels_ill2_diffuse = [round(label, 2) for label in legend_labels_ill2_diffuse]
    fig_ill2_diffuse.update_layout(legend_title="Illuminance (lux)")
    fig_ill2_diffuse.update_traces(legendgroup="temp_legend_ill2_diffuse", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill2_diffuse):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_ill2_diffuse.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_daily_avg_diffuse, max_ill_daily_avg_diffuse, color_scheme)), name=f"{label} lux", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_ill2_diffuse, use_container_width=True)
    
    # fig_ill3_diffuse
    # Calculate monthly average illuminance using Pandas
    df_ill_diffuse = pd.DataFrame({"Illuminance": illuminance_values_full_diffuse})
    df_ill_diffuse["Month"] = pd.to_datetime(diffuse_horizontal_ill_full.datetimes).month
    monthly_averages_ill_diffuse = df_ill_diffuse.groupby("Month")["Illuminance"].mean()
    
    # Calculate average illuminance for each month
    full_year_monthly_averages_ill_diffuse = [monthly_averages_ill_diffuse[month] for month in range(1, 13)]
    
    # Map average illuminance to colors
    min_avg_ill_diffuse = min(full_year_monthly_averages_ill_diffuse)
    max_avg_ill_diffuse = max(full_year_monthly_averages_ill_diffuse)
    avg_color_values_ill_diffuse = [map_temperature_to_color(ill, min_avg_ill_diffuse, max_avg_ill_diffuse, color_scheme) for ill in full_year_monthly_averages_ill_diffuse]
    
    fig_ill3_diffuse = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_ill_diffuse, marker_color=avg_color_values_ill_diffuse)])
    fig_ill3_diffuse.update_layout(
        title="Monthly Average Diffuse Horizontal Illuminance",
        xaxis_title="Month",
        yaxis_title="Average Diffuse Horizontal Illuminance (lux)"
    )
    
    # Force x-axis tick labels to display all months
    fig_ill3_diffuse.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_ill3_diffuse
    legend_labels_ill3_diffuse = np.linspace(min_ill_full_diffuse, max_ill_full_diffuse, num=8)
    legend_labels_ill3_diffuse = [round(label, 2) for label in legend_labels_ill3_diffuse]
    fig_ill3_diffuse.update_layout(legend_title="Illuminance (lux)")
    fig_ill3_diffuse.update_traces(legendgroup="temp_legend_ill3_diffuse", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill3_diffuse):
        visible = True if i == 0 else "legendonly"
        fig_ill3_diffuse.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_full_diffuse, max_ill_full_diffuse, color_scheme)), name=f"{label} lux", hoverinfo="name"))
    
    st.plotly_chart(fig_ill3_diffuse, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Global Horizontal Ill/全球水平照度":
    # global_horizontal_ill
    #<settings
    global_horizontal_ill_select = epw.global_horizontal_illuminance.filter_by_analysis_period(range_select)
    global_horizontal_ill_full = epw.global_horizontal_illuminance.filter_by_analysis_period(range_full)
    global_horizontal_ill_day = epw.global_horizontal_illuminance.filter_by_analysis_period(range_day)
    
    illuminance_values_select_global = global_horizontal_ill_select.values
    illuminance_values_full_global = global_horizontal_ill_full.values
    illuminance_values_day_global = global_horizontal_ill_day.values
    
    min_ill_select_global = np.min(illuminance_values_select_global)
    max_ill_select_global = np.max(illuminance_values_select_global)
    min_ill_full_global = np.min(illuminance_values_full_global)
    max_ill_full_global = np.max(illuminance_values_full_global)
    
    color_values_select_global = [map_temperature_to_color(ill, min_ill_select_global, max_ill_select_global, color_scheme) for ill in illuminance_values_select_global]
    color_values_day_global = [map_temperature_to_color(ill, min_ill_select_global, max_ill_select_global, color_scheme) for ill in illuminance_values_day_global]
    color_values_full_global = [map_temperature_to_color(ill, min_ill_full_global, max_ill_full_global, color_scheme) for ill in illuminance_values_full_global]
    #settings>
    
    # fig_ill1_global
    fig_ill1_global = go.Figure(data=[go.Bar(x=list(range(len(illuminance_values_select_global))), y=illuminance_values_select_global, marker_color=color_values_select_global)])
    fig_ill1_global.update_layout(
        title=f"Hourly Global Horizontal Illuminance from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Global Horizontal Illuminance (lux)"
    )
    bar_width = 0.05
    fig_ill1_global.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_ill1_global
    legend_labels_ill1_global = np.linspace(min_ill_select_global, max_ill_select_global, num=8)
    legend_labels_ill1_global = [round(label, 2) for label in legend_labels_ill1_global]
    fig_ill1_global.update_layout(legend_title="Illuminance (lux)")
    fig_ill1_global.update_traces(legendgroup="temp_legend_ill1_global", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill1_global):
        fig_ill1_global.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_select_global, max_ill_select_global, color_scheme)), name=f"{label} lux", hoverinfo="name"))
    
    st.plotly_chart(fig_ill1_global, use_container_width=True)
    
    # fig_ill2_global
    # Assuming your global_horizontal_ill_day is a DataFrame with a DatetimeIndex
    df_day_ill_global = pd.DataFrame({"Illuminance": illuminance_values_day_global}, index=global_horizontal_ill_day.datetimes)
    daily_averages_ill_global = df_day_ill_global.resample('D').mean()
    min_ill_daily_avg_global = daily_averages_ill_global.min().iloc[0]  # Minimum value for the daily average
    max_ill_daily_avg_global = daily_averages_ill_global.max().iloc[0]  # Maximum value for the daily average
    color_values_day_ill_global = [map_temperature_to_color(ill, min_ill_daily_avg_global, max_ill_daily_avg_global, color_scheme) for ill in daily_averages_ill_global["Illuminance"]]
    
    fig_ill2_global = go.Figure(data=[go.Bar(x=daily_averages_ill_global.index.dayofyear, y=daily_averages_ill_global["Illuminance"], marker_color=color_values_day_ill_global)])  # Use color_values_day_ill_global here
    fig_ill2_global.update_layout(
        title=f"Daily Global Horizontal Illuminance from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Global Horizontal Illuminance (lux)"
    )
    
    # Add legend to fig_ill2_global (with filtering functionality)
    legend_labels_ill2_global = np.linspace(min_ill_daily_avg_global, max_ill_daily_avg_global, num=8)
    legend_labels_ill2_global = [round(label, 2) for label in legend_labels_ill2_global]
    fig_ill2_global.update_layout(legend_title="Illuminance (lux)")
    fig_ill2_global.update_traces(legendgroup="temp_legend_ill2_global", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill2_global):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_ill2_global.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_daily_avg_global, max_ill_daily_avg_global, color_scheme)), name=f"{label} lux", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_ill2_global, use_container_width=True)
    
    # fig_ill3_global
    # Calculate monthly average illuminance using Pandas
    df_ill_global = pd.DataFrame({"Illuminance": illuminance_values_full_global})
    df_ill_global["Month"] = pd.to_datetime(global_horizontal_ill_full.datetimes).month
    monthly_averages_ill_global = df_ill_global.groupby("Month")["Illuminance"].mean()
    
    # Calculate average illuminance for each month
    full_year_monthly_averages_ill_global = [monthly_averages_ill_global[month] for month in range(1, 13)]
    
    # Map average illuminance to colors
    min_avg_ill_global = min(full_year_monthly_averages_ill_global)
    max_avg_ill_global = max(full_year_monthly_averages_ill_global)
    avg_color_values_ill_global = [map_temperature_to_color(ill, min_avg_ill_global, max_avg_ill_global, color_scheme) for ill in full_year_monthly_averages_ill_global]
    
    fig_ill3_global = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_ill_global, marker_color=avg_color_values_ill_global)])
    fig_ill3_global.update_layout(
        title="Monthly Average Global Horizontal Illuminance",
        xaxis_title="Month",
        yaxis_title="Average Global Horizontal Illuminance (lux)"
    )
    
    # Force x-axis tick labels to display all months
    fig_ill3_global.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_ill3_global
    legend_labels_ill3_global = np.linspace(min_ill_full_global, max_ill_full_global, num=8)
    legend_labels_ill3_global = [round(label, 2) for label in legend_labels_ill3_global]
    fig_ill3_global.update_layout(legend_title="Illuminance (lux)")
    fig_ill3_global.update_traces(legendgroup="temp_legend_ill3_global", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f} lux")
    for i, label in enumerate(legend_labels_ill3_global):
        visible = True if i == 0 else "legendonly"
        fig_ill3_global.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_ill_full_global, max_ill_full_global, color_scheme)), name=f"{label} lux", hoverinfo="name"))
    
    st.plotly_chart(fig_ill3_global, use_container_width=True)
#-------------------------------------------------------------
elif temperature_type == "Total Sky Cover/天空覆盖量":
    # total_sky_cover
    #<settings
    total_sky_cover_select = epw.total_sky_cover.filter_by_analysis_period(range_select)
    total_sky_cover_full = epw.total_sky_cover.filter_by_analysis_period(range_full)
    total_sky_cover_day = epw.total_sky_cover.filter_by_analysis_period(range_day)
    
    sky_cover_values_select = total_sky_cover_select.values
    sky_cover_values_full = total_sky_cover_full.values
    sky_cover_values_day = total_sky_cover_day.values
    
    min_cover_select = np.min(sky_cover_values_select)
    max_cover_select = np.max(sky_cover_values_select)
    min_cover_full = np.min(sky_cover_values_full)
    max_cover_full = np.max(sky_cover_values_full)
    
    color_values_select = [map_temperature_to_color(cover, min_cover_select, max_cover_select, color_scheme) for cover in sky_cover_values_select]
    color_values_day = [map_temperature_to_color(cover, min_cover_select, max_cover_select, color_scheme) for cover in sky_cover_values_day]
    color_values_full = [map_temperature_to_color(cover, min_cover_full, max_cover_full, color_scheme) for cover in sky_cover_values_full]
    #settings>
    
    # fig_cover1
    fig_cover1 = go.Figure(data=[go.Bar(x=list(range(len(sky_cover_values_select))), y=sky_cover_values_select, marker_color=color_values_select)])
    fig_cover1.update_layout(
        title=f"Hourly Total Sky Cover from Month {i} to Month {j}",
        xaxis_title="Hour",
        yaxis_title="Total Sky Cover"
    )
    bar_width = 0.05
    fig_cover1.update_traces(marker=dict(line=dict(width=bar_width)))
    
    # Add legend to fig_cover1
    legend_labels_cover1 = np.linspace(min_cover_select, max_cover_select, num=8)
    legend_labels_cover1 = [round(label, 2) for label in legend_labels_cover1]
    fig_cover1.update_layout(legend_title="Total Sky Cover")
    fig_cover1.update_traces(legendgroup="temp_legend_cover1", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}")
    for i, label in enumerate(legend_labels_cover1):
        fig_cover1.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_cover_select, max_cover_select, color_scheme)), name=f"{label}", hoverinfo="name"))
    
    st.plotly_chart(fig_cover1, use_container_width=True)
    
    # fig_cover2
    # Assuming your total_sky_cover_day is a DataFrame with a DatetimeIndex
    df_day_cover = pd.DataFrame({"Sky Cover": sky_cover_values_day}, index=total_sky_cover_day.datetimes)
    daily_averages_cover = df_day_cover.resample('D').mean()
    min_cover_daily_avg = daily_averages_cover.min().iloc[0]  # Minimum value for the daily average
    max_cover_daily_avg = daily_averages_cover.max().iloc[0]  # Maximum value for the daily average
    color_values_day_cover = [map_temperature_to_color(cover, min_cover_daily_avg, max_cover_daily_avg, color_scheme) for cover in daily_averages_cover["Sky Cover"]]
    
    fig_cover2 = go.Figure(data=[go.Bar(x=daily_averages_cover.index.dayofyear, y=daily_averages_cover["Sky Cover"], marker_color=color_values_day_cover)])  # Use color_values_day_cover here
    fig_cover2.update_layout(
        title=f"Daily Total Sky Cover from Month {slider1} to Month {slider2}",  # Use slider1 and slider2 here
        xaxis_title="Day",
        yaxis_title="Daily Average Total Sky Cover"
    )
    
    # Add legend to fig_cover2 (with filtering functionality)
    legend_labels_cover2 = np.linspace(min_cover_daily_avg, max_cover_daily_avg, num=8)
    legend_labels_cover2 = [round(label, 2) for label in legend_labels_cover2]
    fig_cover2.update_layout(legend_title="Total Sky Cover")
    fig_cover2.update_traces(legendgroup="temp_legend_cover2", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}")
    for i, label in enumerate(legend_labels_cover2):
        visible = True if i == 0 else "legendonly"  # Show the first legend item by default, others are hidden
        fig_cover2.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_cover_daily_avg, max_cover_daily_avg, color_scheme)), name=f"{label}", hoverinfo="name", visible=visible))
    
    st.plotly_chart(fig_cover2, use_container_width=True)
    
    # fig_cover3
    # Calculate monthly average sky cover using Pandas
    df_cover = pd.DataFrame({"Sky Cover": sky_cover_values_full})
    df_cover["Month"] = pd.to_datetime(total_sky_cover_full.datetimes).month
    monthly_averages_cover = df_cover.groupby("Month")["Sky Cover"].mean()
    
    # Calculate average sky cover for each month
    full_year_monthly_averages_cover = [monthly_averages_cover[month] for month in range(1, 13)]
    
    # Map average sky cover to colors
    min_avg_cover = min(full_year_monthly_averages_cover)
    max_avg_cover = max(full_year_monthly_averages_cover)
    avg_color_values_cover = [map_temperature_to_color(cover, min_avg_cover, max_avg_cover, color_scheme) for cover in full_year_monthly_averages_cover]
    
    fig_cover3 = go.Figure(data=[go.Bar(x=list(range(1, 13)), y=full_year_monthly_averages_cover, marker_color=avg_color_values_cover)])
    fig_cover3.update_layout(
        title="Monthly Average Total Sky Cover",
        xaxis_title="Month",
        yaxis_title="Average Total Sky Cover"
    )
    
    # Force x-axis tick labels to display all months
    fig_cover3.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Add legend to fig_cover3
    legend_labels_cover3 = np.linspace(min_cover_full, max_cover_full, num=8)
    legend_labels_cover3 = [round(label, 2) for label in legend_labels_cover3]
    fig_cover3.update_layout(legend_title="Total Sky Cover")
    fig_cover3.update_traces(legendgroup="temp_legend_cover3", showlegend=True, hoverinfo="skip", name="", hovertemplate="%{y:.2f}")
    for i, label in enumerate(legend_labels_cover3):
        visible = True if i == 0 else "legendonly"
        fig_cover3.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=map_temperature_to_color(label, min_cover_full, max_cover_full, color_scheme)), name=f"{label}", hoverinfo="name"))
    
    st.plotly_chart(fig_cover3, use_container_width=True)
