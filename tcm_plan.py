import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(16, 5))

# 已占用的大厅
ax.add_patch(patches.Rectangle((0, 0), 16, 12, edgecolor='black', facecolor='#e0e0e0'))
ax.text(8, 6, 'Existing Hall\n(16x12)', ha='center', va='center', fontsize=11, weight='bold')

# 南侧核心区 (Y: 0 到 6，进深压缩至6M)
ax.add_patch(patches.Rectangle((16, 0), 8, 6, edgecolor='black', facecolor='#d4edda'))
ax.text(20, 3, 'Pharmacy / Dispensing\n(8x6)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((24, 0), 8, 6, edgecolor='black', facecolor='#cce5ff'))
ax.text(28, 3, 'TCM Clinics\n(8x6)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((32, 0), 8, 6, edgecolor='black', facecolor='#fff3cd'))
ax.text(36, 3, 'Health Edu & Lounge\n(8x6)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((40, 0), 12, 6, edgecolor='black', facecolor='#f8d7da'))
ax.text(46, 3, 'Comprehensive Therapy\n(12x6)', ha='center', va='center', fontsize=9)

# 北侧辅助区 (Y: 9 到 12，进深维持3M)
ax.add_patch(patches.Rectangle((16, 9), 8, 3, edgecolor='black', facecolor='#a3cfbb'))
ax.text(20, 10.5, 'Decoction / Prep\n(8x3)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((24, 9), 8, 3, edgecolor='black', facecolor='#9ec5fe'))
ax.text(28, 10.5, 'Restrooms\n(8x3)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((32, 9), 8, 3, edgecolor='black', facecolor='#ffe69c'))
ax.text(36, 10.5, 'Aux / Storage\n(8x3)', ha='center', va='center', fontsize=9)

ax.add_patch(patches.Rectangle((40, 9), 12, 3, edgecolor='black', facecolor='#f1aeb5'))
ax.text(46, 10.5, 'Staff Rest & Locker\n(12x3)', ha='center', va='center', fontsize=9)

# 中部走廊 (Y: 6 到 9，宽度拓宽至3M)
ax.add_patch(patches.Rectangle((16, 6), 36, 3, edgecolor='none', facecolor='#f8f9fa'))
ax.text(34, 7.5, 'Main Corridor (Width: 3M)', ha='center', va='center', fontsize=10, weight='bold', color='#6c757d')

# 坐标轴与图表设置
ax.set_xlim(0, 52)
ax.set_ylim(0, 12)
ax.set_aspect('equal')
ax.set_title('TCM Center - Layout with 3M Corridor', fontsize=14, weight='bold', pad=15)
ax.set_xlabel('Length (M)')
ax.set_ylabel('Width (M)')

# 标注横向柱网轴线
ax.axhline(y=9, xmin=16/52, xmax=1, color='red', linestyle='--', linewidth=1.5, alpha=0.6)
ax.text(52.5, 9, 'Column Axis\n(3M from North)', color='red', va='center', fontsize=9)

plt.tight_layout()
plt.show()