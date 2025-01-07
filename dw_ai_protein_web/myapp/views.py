from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from django.http import FileResponse
from pymol import cmd
import subprocess


from . import services
# Create your views here.

def home(request):
    return render(request, 'myapp/home.html')



def alphafoldPage(request):
    return render(request, 'myapp/alphafold_page.html')

def alphafoldResultPage(request):
    return render(request, 'myapp/alphafold_result_page.html')

def runJobAlphafold(request):
    if request.method == "POST":
        try:
            # 요청에서 JSON 데이터 파싱
            datas = json.loads(request.body)
            
            job = "alphafold3"
            input_folder_path, origin_output_dir = services.createInputFolder(job)
            origin_output_path = Path(origin_output_dir + "_alphafold3")
            
            current_output_path = origin_output_path.name
            parent_output_path = origin_output_path.parent

            print("current_output_path : ",current_output_path)
            print("parent_output_path : ",parent_output_path)
            print("origin_output_path : ",origin_output_path)
            
            alphafold_input_file = services.alphafoldInputDataGenerate(job=current_output_path, datas=datas, folder_path=input_folder_path)
            print(input_folder_path)
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                result_Alphafold = executor.submit(services.runAlphafold, input_folder_path, parent_output_path)
                request.session['Alphafold_result_path'] = str(origin_output_path)
                
            # 처리 결과 반환
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def getFilesAlphafold(request):
    folder_path = request.session.get('Alphafold_result_path')  # PyMOL 파일이 저장된 경로
    print(folder_path)
    try:
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for f in filenames:
                if f.endswith(('.pdb', '.cif')):
                    # 상대 경로로 추가
                    files.append(os.path.relpath(os.path.join(root, f), start=folder_path))
        print(files)
        return JsonResponse({"files": files})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def visualizePymolAlphafold(request):
    file_name = request.GET.get('file_name')  # 파일 이름 가져오기
    folder_path = request.session.get('Alphafold_result_path')

    if not folder_path or not file_name:
        return JsonResponse({"error": "파일 경로나 파일 이름이 제공되지 않았습니다."}, status=400)

    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path):
        return JsonResponse({"error": "파일이 존재하지 않습니다."}, status=404)

    # 파일 읽어서 반환
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/plain')
    
def downloadAlphafoldResultFile(request):
    # """
    # 특정 경로의 파일을 다운로드하는 뷰.
    # """
    result_folder = request.session.get("Alphafold_result_path")
    print("파일 다운로드 경로 : ",result_folder)
    output_zip_file = services.makeZip(result_folder)
    # 파일이 존재하는지 확인
    if not os.path.exists(output_zip_file):
        raise Http404("파일이 존재하지 않습니다.")

    # 파일 이름만 추출
    file_name = os.path.basename(output_zip_file)

    # 파일 응답 반환
    return FileResponse(open(output_zip_file, 'rb'), as_attachment=True, filename=file_name)



def chaiLabPage(request):
    return render(request, 'myapp/chai_lab_page.html')

def chaiLabResultPage(request):
    return render(request, 'myapp/chai_lab_result_page.html')

def runJobChai(request):
    if request.method == "POST":
        try:
            # 요청에서 JSON 데이터 파싱
            datas = json.loads(request.body)
            # 데이터 출력 (디버깅용)
            # print("Received data:", datas)
            
            job = "chailab"
            input_file_path, origin_output_dir = services.createInputFolder(job)
            chai_input_file = services.chaiInputDataGenerate(job, datas, input_file_path)

            with ThreadPoolExecutor(max_workers=4) as executor:
                result_chai = executor.submit(services.runChai, chai_input_file, origin_output_dir)
                print(result_chai.result())
                request.session['chai_result_path'] = result_chai.result()
                
            # 처리 결과 반환
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def getFilesChai(request):
    folder_path = request.session.get('chai_result_path')  # PyMOL 파일이 저장된 경로
    try:
        files = [f for f in os.listdir(folder_path) if f.endswith(('.cif'))]
        return JsonResponse({"files": files})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def visualizePymolChai(request):
    file_name = request.GET.get('file_name')  # 파일 이름 가져오기
    folder_path = request.session.get('chai_result_path')

    if not folder_path or not file_name:
        return JsonResponse({"error": "파일 경로나 파일 이름이 제공되지 않았습니다."}, status=400)

    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path):
        return JsonResponse({"error": "파일이 존재하지 않습니다."}, status=404)

    # 파일 읽어서 반환
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/plain')

def downloadChaiResultFile(request):
    """
    특정 경로의 파일을 다운로드하는 뷰.
    """
    result_folder = request.session.get("chai_result_path")
    print(result_folder)
    output_zip_file = services.makeZip(result_folder)
    # 파일이 존재하는지 확인
    if not os.path.exists(output_zip_file):
        raise Http404("파일이 존재하지 않습니다.")

    # 파일 이름만 추출
    file_name = os.path.basename(output_zip_file)

    # 파일 응답 반환
    return FileResponse(open(output_zip_file, 'rb'), as_attachment=True, filename=file_name)



def boltzPage(request):
    return render(request, 'myapp/boltz_page.html')

def runJobBoltz(request):
    if request.method == "POST":
        try:
            # 요청에서 JSON 데이터 파싱
            datas = json.loads(request.body)
            # 데이터 출력 (디버깅용)
            # print("Received data:", datas)
            
            job = "boltz"
            input_file_path, origin_output_dir = services.createInputFolder(job)
            boltz_input_file = services.boltzInputDataGenerate(job, datas, input_file_path)

            with ThreadPoolExecutor(max_workers=4) as executor:
                result_boltz = executor.submit(services.runBoltz, boltz_input_file, origin_output_dir)
                request.session['boltz_result_path'] = result_boltz.result()
                
            # 처리 결과 반환
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def boltzResultPage(request):
    return render(request, 'myapp/boltz_result_page.html')

def getFilesBoltz(request):
    folder_path = request.session.get('boltz_result_path')  # PyMOL 파일이 저장된 경로
    try:
        files = [f for f in os.listdir(folder_path) if f.endswith(('.pdb', '.cif'))]
        return JsonResponse({"files": files})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def visualizePymolBoltz(request):
    file_name = request.GET.get('file_name')  # 파일 이름 가져오기
    folder_path = request.session.get('boltz_result_path')

    if not folder_path or not file_name:
        return JsonResponse({"error": "파일 경로나 파일 이름이 제공되지 않았습니다."}, status=400)

    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path):
        return JsonResponse({"error": "파일이 존재하지 않습니다."}, status=404)

    # 파일 읽어서 반환
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/plain')
    
def downloadBoltzResultFile(request):
    """
    특정 경로의 파일을 다운로드하는 뷰.
    """
    folder_path = request.session.get("boltz_result_path")
    print(folder_path)
    result_folder = "/".join(folder_path.split('/')[:-3])
    print(result_folder)
    output_zip_file = services.makeZip(result_folder)
    # 파일이 존재하는지 확인
    if not os.path.exists(output_zip_file):
        raise Http404("파일이 존재하지 않습니다.")

    # 파일 이름만 추출
    file_name = os.path.basename(output_zip_file)

    # 파일 응답 반환
    return FileResponse(open(output_zip_file, 'rb'), as_attachment=True, filename=file_name)