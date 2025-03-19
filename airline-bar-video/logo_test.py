import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageEnhance

# 设置好工作目录
logos_dir = 'logos'

# 创建图像
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_title('Logo Test')

# 测试一些基本的logo
test_logos = [
    'logos/american-airlines-2013-now.jpg',
    'logos/delta-air-lines-2007-now.jpg',
    'logos/southwest-airlines-2014-now.png',
    'logos/klm-1999-now.png'
]

# 处理logo
for i, logo_path in enumerate(test_logos):
    if os.path.exists(logo_path):
        print(f"Loading logo: {logo_path}")
        img = plt.imread(logo_path)
        
        # 创建一个ImageEnhance对象来增强图像
        if logo_path.endswith('.png') and img.shape[2] == 4:  # RGBA图像
            # 分离通道处理
            image = Image.fromarray((img * 255).astype(np.uint8))
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
            
            # 增强图像
            enhancer = ImageEnhance.Sharpness(rgb)
            rgb = enhancer.enhance(1.5)
            
            # 合并回RGBA
            r, g, b = rgb.split()
            image = Image.merge('RGBA', (r, g, b, a))
            img = np.array(image) / 255.0
        else:
            # 处理RGB图像
            image = Image.fromarray((img * 255).astype(np.uint8))
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            img = np.array(image) / 255.0
        
        # 创建OffsetImage对象
        imagebox = OffsetImage(img, zoom=0.5)
        
        # 放置图像
        y_pos = 8 - i * 2
        ab = AnnotationBbox(imagebox, (5, y_pos), frameon=True)
        ax.add_artist(ab)
        
        # 添加文字标签
        ax.text(2, y_pos, os.path.basename(logo_path), va='center')
    else:
        print(f"Logo not found: {logo_path}")

# 添加网格线便于识别
ax.grid(True)

# 保存图像
output_path = 'logo_test.png'
plt.savefig(output_path, dpi=150)
print(f"Saved test image to {output_path}")
plt.close() 