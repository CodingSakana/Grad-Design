import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_purified_daycare_plan():
    fig, ax = plt.subplots(figsize=(10, 18))
    
    # 空间配色方案
    c_corridor = '#E0E0E0'  # 走廊及连廊
    c_active = '#FFE0B2'    # 活跃社交 (South)
    c_quiet = '#B3E5FC'     # 休息与静区 (North)
    c_service = '#CFD8DC'   # 医疗与卫生辅助
    
    def add_space(x, y, w, h, name, color, fontsize=9):
        ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor=color))
        ax.text(x + w/2, y + h/2, f"{name}\n({w}x{h}m)", ha='center', va='center', fontsize=fontsize)

    # ==========================================
    # 1. South Block (16m x 24m) - 活跃社交
    # ==========================================
    # 东侧 (8m)
    add_space(8, 0, 8, 16, "Multi-purpose Hall", c_active, 11)
    add_space(8, 16, 8, 8, "Dining Hall", c_active, 10)
    # 中部 (3m)
    add_space(5, 0, 3, 24, "Main Corridor\n(South)", c_corridor, 10)
    # 西侧 (5m)
    add_space(0, 0, 5, 8, "Arts & Crafts", c_active)
    add_space(0, 8, 5, 8, "Reading & Game", c_active)
    add_space(0, 16, 5, 4, "Kitchenette", c_service)
    add_space(0, 20, 5, 4, "Staff / Storage", c_service)

    # ==========================================
    # 2. TCM Intersection & Link (12m 跨度)
    # ==========================================
    # 仅保留日间照料的 3m 宽过境走廊
    add_space(5, 24, 3, 12, "Transit Link\n(Through TCM)", c_corridor, 9)
    
    # TCM 主建筑体块示意 (用绿色虚线框出)
    tcm_box = patches.Rectangle((-6, 24), 28, 12, fill=False, edgecolor='#2E7D32', 
                                linestyle='--', linewidth=2.5, zorder=0)
    ax.add_patch(tcm_box)
    ax.text(23, 30, "Independent TCM Block\n(Medical Services)", color='#2E7D32', weight='bold', va='center')

    # ==========================================
    # 3. North Block (16m x 28m) - 专业护理与静养
    # ==========================================
    # 东侧核心大空间 (8m)
    add_space(8, 36, 8, 12, "Daytime Nap Room A\n(Beds)", c_quiet, 10) 
    add_space(8, 48, 8, 8, "Quiet Lounge\n(Recliners/Reading)", c_quiet, 9) 
    add_space(8, 56, 8, 8, "Medical & Nurse Clinic", c_service, 10)
    
    # 中部走廊 (3m)
    add_space(5, 36, 3, 28, "Main Corridor\n(North)", c_corridor, 10)

    # 西侧辅助带 (5m)
    add_space(0, 36, 5, 12, "Rehab Gym", c_service, 10) # 靠近连廊，方便TCM转诊康复
    add_space(0, 48, 5, 8, "Assisted Bathing", c_service)
    add_space(0, 56, 5, 4, "Accessible WC", c_service)
    add_space(0, 60, 5, 4, "Sensory /\nCounseling", c_quiet, 8) # 新增心理/感官室

    # ==========================================
    # 结构柱网线 (8m 基准)
    # ==========================================
    grid_kwargs = {'linestyle': ':', 'color': 'red', 'alpha': 0.7, 'linewidth': 1.5}
    
    # 南北贯通的 8m 中轴柱线
    ax.plot([8, 8], [0, 24], **grid_kwargs)
    ax.plot([8, 8], [36, 64], **grid_kwargs)
    
    # 边柱线
    for x in [0, 16]:
        ax.plot([x, x], [0, 24], **grid_kwargs)
        ax.plot([x, x], [36, 64], **grid_kwargs)

    # ==========================================
    # 渲染设置
    # ==========================================
    ax.set_xlim(-8, 28)
    ax.set_ylim(-2, 68)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.text(17, 66, "N ▲", fontsize=16, weight='bold', color='#333333')
    plt.title("Purified Day Care Plan (64m Length)", fontsize=15, weight='bold', pad=20)
    
    legend_handles = [
        patches.Patch(color=c_active, label='Active Zone (South)'),
        patches.Patch(color=c_quiet, label='Quiet/Rest Zone (North)'),
        patches.Patch(color=c_service, label='Care & Support'),
        patches.Patch(color=c_corridor, label='Continuous Circulation'),
        plt.Line2D([0], [0], color='#2E7D32', linestyle='--', linewidth=2, label='External TCM Block'),
        plt.Line2D([0], [0], color='red', linestyle=':', label='8m Column Line')
    ]
    ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1), frameon=False, fontsize=10)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    draw_purified_daycare_plan()