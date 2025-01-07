from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 메인 페이지
    # alphafold
    path('alphaFold/', views.alphafoldPage, name='alphafold_page'),  # Alphafold 페이지
    path('alphaFoldResult/', views.alphafoldResultPage, name='alphafold_result_page'),  # Alphafold 결과 페이지
    path('runJobAlphafold/', views.runJobAlphafold, name='runJobAlphafold'),  # 서비스 호출을 뷰에서 처리
    path('getFilesAlphafold/', views.getFilesAlphafold, name='getFilesAlphafold'),  # 서비스 호출을 뷰에서 처리
    path('visualizePymolAlphafold/', views.visualizePymolAlphafold, name='visualizePymolAlphafold'),  # 서비스 호출을 뷰에서 처리
    path('downloadAlphafoldResultFile/', views.downloadAlphafoldResultFile, name='downloadAlphafoldResultFile'),  # 서비스 호출을 뷰에서 처리
    # chai_lab
    path('chaiLab/', views.chaiLabPage, name='chai_lab_page'),  # Chai-lab 페이지
    path('chaiLabResult/', views.chaiLabResultPage, name='chai_lab_result_page'),  # Chai-lab 결과 페이지
    path('runJobChai/', views.runJobChai, name='runJobChai'),  # 서비스 호출을 뷰에서 처리
    path('getFilesChai/', views.getFilesChai, name='getFilesChai'),  # 서비스 호출을 뷰에서 처리
    path('visualizePymolChai/', views.visualizePymolChai, name='visualizePymolChai'),  # 서비스 호출을 뷰에서 처리
    path('downloadChaiResultFile/', views.downloadChaiResultFile, name='downloadChaiResultFile'),  # 서비스 호출을 뷰에서 처리
    # boltz
    path('boltz/', views.boltzPage, name='boltz_page'),  # Chai-lab 페이지
    path('boltzResult/', views.boltzResultPage, name='boltz_result_page'),  # Chai-lab 결과 페이지
    path('runJobBoltz/', views.runJobBoltz, name='runJobBoltz'),  # 서비스 호출을 뷰에서 처리
    path('getFilesBoltz/', views.getFilesBoltz, name='getFilesBoltz'),
    path('visualizePymolBoltz/', views.visualizePymolBoltz, name='visualizePymolBoltz'),
    path('downloadBoltzResultFile/', views.downloadBoltzResultFile, name='downloadBoltzResultFile'),
]