import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_siba_logo(output_path):
    fig, ax = plt.subplots(figsize=(3.0, 1.2), dpi=300)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 12)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Draw Dharma Chakra (Wheel of Law emblem) in Gold/Amber
    center = (5, 6)
    radius = 4.2
    # Outer circle
    circle_out = patches.Circle(center, radius, ec="#d97706", fc="none", lw=2.0)
    ax.add_patch(circle_out)
    # Inner circle
    circle_in = patches.Circle(center, 1.2, ec="#d97706", fc="#d97706", lw=1.0)
    ax.add_patch(circle_in)
    
    # 8 Spokes
    for angle in np.linspace(0, 2*np.pi, 9)[:-1]:
        x_end = center[0] + radius * np.cos(angle)
        y_end = center[1] + radius * np.sin(angle)
        ax.plot([center[0], x_end], [center[1], y_end], color="#d97706", lw=1.4)

    # Outer decorative rim dots
    for angle in np.linspace(0, 2*np.pi, 25)[:-1]:
        xd = center[0] + (radius + 0.5) * np.cos(angle)
        yd = center[1] + (radius + 0.5) * np.sin(angle)
        ax.plot(xd, yd, marker='o', markersize=1.2, color="#b45309")

    # Text "SIBA" bold navy
    ax.text(11, 7.2, "SIBA", fontsize=18, fontweight='heavy', color="#0f172a", va='center')
    # Text "CAMPUS" subtitle
    ax.text(11.2, 4.2, "CAMPUS", fontsize=8, fontweight='bold', color="#475569", va='center')
    # Thin underline
    ax.plot([11, 28], [3.2, 3.2], color="#cbd5e1", lw=0.8)
    # Sri Lanka text
    ax.text(11.2, 2.0, "SRI LANKA", fontsize=5.5, fontweight='bold', color="#94a3b8", va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', transparent=False)
    plt.close()
    print(f"SIBA logo created at: {output_path}")

if __name__ == "__main__":
    generate_siba_logo(r"d:\FinalProject 2026\vehicle_damade_dash_cloned\reports\siba_logo.png")
