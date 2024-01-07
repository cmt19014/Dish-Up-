from django.shortcuts import render
from .models import Cooking_data
from .forms import ImageUploadForm
from .process import process_image

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