from django.shortcuts import render
from .models import Cooking_data
from .forms import ImageUploadForm
from .process import process_image
import random
from django.http import JsonResponse
import json

def cooking_data_list(request):
    cooking_data = Cooking_data.objects.all()
    return render(request, 'app1/cooking_data_list.html', {'cooking_data': cooking_data})

def upload_and_process_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 画像の処理
            processed_data = process_image(request.FILES['image'])

            # デバッグ用：生成されたURLリストをコンソールに出力
            # print("out_of_process;result_url", processed_data)
            return render(request, 'app1/result.html', {'data': processed_data})
    else:
        form = ImageUploadForm()
    return render(request, 'app1/upload.html', {'form': form})

def update_dish_color(request, dish_id):
    if request.method == 'POST':
        dish = Cooking_data.objects.get(id=dish_id)
        dish.red = random.randint(0, 255)
        dish.green = random.randint(0, 255)
        dish.blue = random.randint(0, 255)
        dish.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


from django.shortcuts import redirect

def reset_database(request):
    # 全ての料理データに対して初期値にリセット
    for dish in Cooking_data.objects.all():
        dish.red = dish.initial_red
        dish.green = dish.initial_green
        dish.blue = dish.initial_blue
        dish.save()

    # アップロードページにリダイレクト
    return redirect(upload_and_process_image)



from django.conf import settings
import os
from django.http import HttpResponseRedirect

def process_image_again(request):
    if request.method == 'POST':
        plate_image_url = request.POST.get('plate_image_url')
        image_relative_path = plate_image_url.replace(settings.MEDIA_URL, "")
        image_path = os.path.join(settings.MEDIA_ROOT, image_relative_path)

        processed_data = process_image(image_path)

            # デバッグ用：生成されたURLリストをコンソールに出力
            # print("out_of_process;result_url", processed_data)
        return render(request, 'app1/result.html', {'data': processed_data})

    # POSTリクエストでない場合は、アップロードページにリダイレクト
    return HttpResponseRedirect(upload_and_process_image)