import cv2
import numpy as np
from PIL import Image
import os
import uuid
from django.conf import settings
from .models import Cooking_data


def process_image(uploaded_image):
    # 画像をOpenCV形式で読み込む
    print(type(uploaded_image))
    cv2_image = Image.open(uploaded_image)
    cv2_image = np.array(cv2_image)
    cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)

    original_image = cv2_image
    # 画像を400x400ピクセルにリサイズ
    plate_height = original_image.shape[0]
    plate_width = original_image.shape[1]
    cv2_image = cv2.resize(original_image, (int(plate_width * 400 / plate_height), 400))

    # ここにお皿の色とサイズを決定するロジックを実装
    plate_color, plate_size, plate_rate = detect_plate_properties(cv2_image)
    print("plate_color:", plate_color)
    print("plate_size:", plate_size)
    print("plate_rate:", plate_rate ,"!!If this value is less than 0.1, Plate Detection doesn't wouk out!!")

    # データベースから料理データを取得
    dishes = Cooking_data.objects.all()
    # print("dishes", dishes.)
    selected_dishes = select_matching_dishes(dishes, plate_color, plate_size)
    print("selected_dishes:", selected_dishes)

    # OpenCVの画像（BGR）をRGBに変換
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

    # NumPy配列をPillowのImageオブジェクトに変換
    pil_image = Image.fromarray(rgb_image)
    resized_plate_image_url = save_image(pil_image, "plate")

    # 合成画像のデータを格納するリスト
    processed_images_data = []

    # # 合成画像のリスト
    # composite_images = []

    # composite_images_urls = []
    for dish in selected_dishes:
        # 各料理に対する合成画像を作成
        # 各料理に対する合成画像を作成する前に、plate_imageのコピーを作成
        plate_image_copy = pil_image.copy()
        dish_image_path = os.path.join(settings.STATICFILES_DIRS[0], f'images/cookingpicture/{dish.id}.png')
        composite_image = overlay_dish_on_plate(plate_rate, plate_image_copy, dish_image_path)

        # 合成画像を保存し、URLを取得
        composite_image_url = save_image(composite_image, dish.name)

        # 合成画像のデータをリストに追加
        processed_images_data.append({
            'id' : dish.id,
            'name': dish.name,
            'url': composite_image_url
        })

    return {
        'plate_image_url': resized_plate_image_url,
        'processed_images': processed_images_data
    }

def detect_plate_properties(image):
    # ここにお皿の色とサイズを測定するロジックを実装
    # 例: 平均色の抽出、輪郭の分析など
    # 返り値は (色, サイズ)

    # 画像をグレースケールに変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ガウシアンブラーを使用してノイズを軽減
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # エッジを検出
    edges = cv2.Canny(blurred, 50, 150)

    # 輪郭を検出
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 画像の中心座標を計算
    height, width = image.shape[:2]
    center_x = width // 2
    center_y = height // 2

    # 中心座標から一番近い輪郭を見つける
    min_distance = float('inf')
    closest_contour = None

    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            distance = np.sqrt((cX - center_x) ** 2 + (cY - center_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_contour = contour


    # 中心座標から等距離かつ輪郭より内側の8点を取得
    epsilon = 0.04 * cv2.arcLength(closest_contour, True)
    approx = cv2.approxPolyDP(closest_contour, epsilon, True)
    inner_points = []

    # approx が8未満の場合は、そのままの点の数を使用
    num_points = len(approx) if len(approx) < 8 else 8

    for i in range(num_points):
        x, y = approx[i][0]
        direction_x = x - center_x
        direction_y = y - center_y
        inner_x = int(center_x + 0.75 * direction_x)
        inner_y = int(center_y + 0.75 * direction_y)
        inner_points.append((inner_x, inner_y))

    # 8個の内側の点の色を抽出
    inner_colors = [image[y, x] for x, y in inner_points]

    # 8個の内側の点の色の平均を計算
    mean_color = np.mean(inner_colors, axis=0)

    # 平均色をBGRからRGBに変換
    mean_color = mean_color[[2, 1, 0]]

    # お皿の大きさを計算
    total_pixels = width * height
    plate_size = cv2.contourArea(closest_contour) / total_pixels

    # お皿の大きさカテゴリ
    big = 0.5
    medium = 0.35
    if plate_size >= big:
        plate_size_category = 3
    elif plate_size >= medium:
        plate_size_category = 2
    else:
        plate_size_category = 1

    color = mean_color.astype(int)
    size = plate_size_category
    plate_rate = plate_size
    return (color, size, plate_rate)

def select_matching_dishes(dishes, plate_color, plate_size):
    # 各料理とお皿の色の差異を計算し、差異が小さい順にソート
    matching_dishes = []
    for dish in dishes:
        # print("dish", type(dish.size_category))
        # print("plate_size", type(plate_size))
        if int(dish.size_category) == plate_size:
            dish_color = np.array([int(dish.red), int(dish.green), int(dish.blue)])
            # print("dish_color - plate_color" , dish_color - plate_color)
            color_difference = np.linalg.norm(dish_color - plate_color)
            matching_dishes.append((dish, color_difference))
    
    # 色の差異が小さい順にソート
    # print("matching_dishes", matching_dishes)
    matching_dishes.sort(key=lambda x: x[1])

    # 上位3つの料理を返却
    return [dish[0] for dish in matching_dishes[:3]]

def overlay_dish_on_plate(plate_rate, plate_image, dish_image_path):
    composite_image = plate_image
    # お皿の画像サイズを取得
    plate_width, plate_height = composite_image.size

    # 背景透過画像（料理の画像）を開く
    dish_image = Image.open(dish_image_path).convert("RGBA")

    # お皿のサイズに合わせて料理の画像を縮小
    # 料理画像をどれくらい縮小するか
    if plate_rate >= 0.5:
        scale_factor = plate_rate*1.1
    else:
        scale_factor = 0.4
    # scale_factor = 0.75  # 料理画像をどれくらい縮小するか
    new_dish_width = int(plate_width * scale_factor)
    new_dish_height = int(dish_image.height * new_dish_width / dish_image.width)
    resized_dish_image = dish_image.resize((new_dish_width, new_dish_height), Image.Resampling.LANCZOS)

    # 透明度情報を考慮して料理の画像をお皿の中央に貼り付ける
    x_start = (plate_width - new_dish_width) // 2
    y_start = (plate_height - new_dish_height) // 2
    composite_image.paste(resized_dish_image, (x_start, y_start), resized_dish_image)

    return composite_image

def save_image(image, name):
    # 一意のファイル名を生成
    filename = f"{name}_{uuid.uuid4()}.png"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    # 画像をファイルに保存
    image.save(filepath)

    # 保存された画像のURLを生成
    image_url = os.path.join(settings.MEDIA_URL, filename)
    return image_url