"""
图片预处理脚本 - 去除背景生成透明PNG
用法:
  python process_images.py          # 基础模式（纯色背景）
  python process_images.py --ai     # AI智能抠图（推荐）
"""
import os
import sys
from PIL import Image, ImageFilter


def remove_background_simple(input_path, output_path, threshold=200):
    """基础背景去除：基于亮度+饱和度阈值"""
    img = Image.open(input_path).convert('RGBA')
    data = img.getdata()

    new_data = []
    for r, g, b, a in data:
        brightness = (r + g + b) / 3
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        saturation = (max_c - min_c) / max_c if max_c > 0 else 0

        if brightness > threshold and saturation < 0.2:
            edge_factor = (brightness - threshold) / 30
            alpha = max(0, int(255 * (1 - min(1, edge_factor))))
            new_data.append((r, g, b, alpha))
        else:
            new_data.append((r, g, b, 255))

    img.putdata(new_data)
    alpha = img.split()[-1]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1))
    img.putalpha(alpha)
    img.save(output_path, 'PNG')
    print(f'  处理完成: {os.path.basename(output_path)}')


def remove_background_ai(input_path, output_path):
    """AI智能抠图（rembg）"""
    try:
        from rembg import remove
    except ImportError:
        print('错误: 未安装 rembg，请先运行: pip install rembg')
        sys.exit(1)

    print(f'  AI抠图中: {os.path.basename(input_path)} ...')
    input_img = Image.open(input_path)
    output_img = remove(input_img)
    output_img.save(output_path, 'PNG')
    print(f'  处理完成: {os.path.basename(output_path)}')


def crop_to_content(image_path, padding=10):
    """裁剪到内容区域"""
    img = Image.open(image_path)
    bbox = img.getbbox()
    if bbox:
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(img.width, bbox[2] + padding)
        bottom = min(img.height, bbox[3] + padding)
        img.crop((left, top, right, bottom)).save(image_path)


def main():
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    use_ai = '--ai' in sys.argv

    images = [
        ('pet_stand', '站立'),
        ('pet_sit', '坐姿'),
        ('pet_lie', '趴卧'),
    ]

    mode = 'AI智能抠图' if use_ai else '基础亮度抠图'
    print(f'开始处理图片（{mode}）')
    print('-' * 40)

    processed = 0
    for name, label in images:
        src_jpg = os.path.join(assets_dir, f'{name}.jpg')
        src_png = os.path.join(assets_dir, f'{name}.png')
        dst = os.path.join(assets_dir, f'{name}.png')

        src = src_jpg if os.path.exists(src_jpg) else (src_png if os.path.exists(src_png) else None)
        
        if src:
            print(f'[{label}]')
            if use_ai:
                remove_background_ai(src, dst)
            else:
                remove_background_simple(src, dst, threshold=200)
            crop_to_content(dst)
            processed += 1
        else:
            print(f'[{label}] 跳过（无原图）')
        print()

    # 生成托盘图标
    stand_path = os.path.join(assets_dir, 'pet_stand.png')
    if os.path.exists(stand_path):
        img = Image.open(stand_path)
        size = max(img.width, img.height)
        square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        square.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
        square.resize((32, 32), Image.LANCZOS).save(
            os.path.join(assets_dir, 'tray_icon.ico'), 
            format='ICO', sizes=[(32, 32), (16, 16)]
        )
        print('托盘图标已生成')

    print('-' * 40)
    print(f'完成！共处理 {processed} 张图片')
    if not use_ai and processed > 0:
        print('\n💡 背景复杂的话试试AI抠图:')
        print('   pip install rembg')
        print('   python process_images.py --ai')


if __name__ == '__main__':
    main()
