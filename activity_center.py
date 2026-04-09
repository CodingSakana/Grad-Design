import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(16, 6))

# 1. 绘制底图柱网 (使用虚线，避免与实体墙线混淆)
for i in range(0, 49, 8):
    ax.axvline(x=i, color='gray', linestyle='--', linewidth=0.5, alpha=0.5, zorder=0)
for i in range(0, 17, 8):
    ax.axhline(y=i, color='gray', linestyle='--', linewidth=0.5, alpha=0.5, zorder=0)

# 2. 绘制功能色块 (无边框，仅填充颜色)
# 西侧静区
ax.add_patch(patches.Rectangle((0, 0), 16, 6, edgecolor='none', facecolor='#C5E0B4', zorder=1))
ax.text(8, 3, 'Chess & Recreation\n(96 sqm)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((0, 10), 16, 6, edgecolor='none', facecolor='#A9D18E', zorder=1))
ax.text(8, 13, 'Reading & Art Room\n(96 sqm)', ha='center', va='center', fontsize=9)

# 中部核心区
ax.add_patch(patches.Rectangle((16, 0), 8, 6, edgecolor='none', facecolor='#F8CBAD', zorder=1))
ax.text(20, 3, 'Health Station\n(48 sqm)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((24, 0), 8, 6, edgecolor='none', facecolor='#F8CBAD', zorder=1))
ax.text(28, 3, 'Public Services\n(48 sqm)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((16, 10), 16, 6, edgecolor='none', facecolor='#F4B183', zorder=1))
ax.text(24, 13, 'Main Lobby\n(96 sqm)', ha='center', va='center', fontsize=9)

# 东侧动区
ax.add_patch(patches.Rectangle((32, 0), 16, 16, edgecolor='none', facecolor='#9BC2E6', zorder=1))
ax.text(40, 5, 'Multi-purpose Hall\n(192 sqm)', ha='center', va='center', fontsize=10)

ax.add_patch(patches.Rectangle((40, 10), 8, 6, edgecolor='none', facecolor='#BDD7EE', zorder=1))
ax.text(44, 13, 'Storage\n(48 sqm)', ha='center', va='center', fontsize=9)

# 明确标识内部主走廊
ax.add_patch(patches.Rectangle((0, 6), 32, 4, edgecolor='none', facecolor='#f8f9fa', zorder=1))
ax.text(16, 8, 'Main Internal Corridor (Width: 4)', ha='center', va='center', fontsize=11, weight='bold', color='#6c757d')


# 3. 绘制实体墙线 (仅使用实线，并预留门洞和开放接口)
def draw_wall(x_coords, y_coords):
    ax.plot(x_coords, y_coords, color='black', linewidth=2.5, linestyle='-', zorder=3)

# 建筑外轮廓墙 (含出入口断点)
draw_wall([0, 20], [16, 16])   # 北墙左段
draw_wall([28, 48], [16, 16])  # 北墙右段 (预留8M北主入口)
draw_wall([0, 8], [0, 0])      # 南墙左段
draw_wall([10, 32], [0, 0])    # 南墙中段 (预留2M南接口1)
draw_wall([40, 48], [0, 0])    # 南墙右段 (预留8M南接口2)
draw_wall([0, 0], [0, 16])     # 西墙
draw_wall([48, 48], [0, 16])   # 东墙

# 内部空间分隔墙 (含门洞断点)
# 走廊北侧墙 (Y=10)
draw_wall([0, 16], [10, 10])   # 阅览室南墙
draw_wall([16, 20], [10, 10])  # 门厅南墙左
draw_wall([28, 32], [10, 10])  # 门厅南墙右 (门厅向走廊敞开大开口)

# 走廊南侧墙 (Y=6)
draw_wall([0, 8], [6, 6])      # 棋牌室北墙左
draw_wall([10, 16], [6, 6])    # 棋牌室北墙右 (预留门洞对齐南接口1)
draw_wall([16, 18], [6, 6])    
draw_wall([22, 24], [6, 6])    # 医疗驿站北门洞
draw_wall([24, 26], [6, 6])    
draw_wall([30, 32], [6, 6])    # 公共服务北门洞

# 垂直分隔墙
draw_wall([16, 16], [0, 6])    # 棋牌室与医疗分隔
draw_wall([16, 16], [10, 16])  # 阅览室与门厅分隔
draw_wall([24, 24], [0, 6])    # 医疗与服务分隔
draw_wall([32, 32], [0, 6])    # 中西部与大厅分隔 (下段)
draw_wall([32, 32], [10, 16])  # 中西部与大厅分隔 (上段)
draw_wall([40, 40], [10, 16])  # 大厅与储藏分隔
draw_wall([40, 48], [10, 10])  # 储藏室南墙


# 4. 标识出入口流线
ax.annotate('Main Entrance\n(North)', xy=(24, 16), xytext=(24, 19),
            arrowprops=dict(facecolor='#66B2FF', edgecolor='none', width=2, headwidth=7), 
            ha='center', va='bottom', fontsize=10, weight='bold')

ax.annotate('South Interface 1\n[8 - 10]', xy=(9, 0), xytext=(9, -3),
            arrowprops=dict(facecolor='#FF6666', edgecolor='none', width=2, headwidth=7), 
            ha='center', va='top', fontsize=10, weight='bold')

ax.annotate('South Interface 2\n[32 - 40]', xy=(36, 0), xytext=(36, -3),
            arrowprops=dict(facecolor='#FF6666', edgecolor='none', width=2, headwidth=7), 
            ha='center', va='top', fontsize=10, weight='bold')

# 5. 坐标轴与图表全局设置 (去除单位标注)
ax.set_xlim(-2, 50)
ax.set_ylim(-5, 22)
ax.set_aspect('equal')
ax.set_xticks(range(0, 49, 8))
ax.set_yticks(range(0, 17, 8))
ax.set_title('Community Center Layout (Walls & Corridor Highlighted)', fontsize=14, weight='bold', pad=15)
ax.set_xlabel('Length')
ax.set_ylabel('Width')

plt.tight_layout()
plt.show()