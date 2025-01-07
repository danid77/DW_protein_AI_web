import subprocess
import sys
import os
import shutil
import json
import pandas as pd
from datetime import datetime

# 인풋 경로 설정
def createInputFolder(job):
    current_time = datetime.now().strftime("%Y%m%d_%Hh_%Mm_%Ss")
    input_file_path = os.path.join(f"/opt/git_tools/_development/DW_protein_AI_web/dw_ai_protein_web/datas/inputs/{job}/{current_time}")
    if not os.path.exists(input_file_path):
        os.makedirs(input_file_path)
    origin_output_dir = f"/opt/git_tools/_development/DW_protein_AI_web/dw_ai_protein_web/datas/outputs/{job}/{current_time}_result"
    return input_file_path, origin_output_dir

# 압축 
def makeZip(outfoler):
    # 압축 파일 저장 경로와 이름 (zip 형식)
    output_zip_file = f"{outfoler}.zip"
    shutil.make_archive(
        base_name=output_zip_file.replace(".zip", ""),  # 확장자 제외한 이름
        format="zip",  # 압축 형식
        root_dir=outfoler  # 압축 대상 폴더
    )
    print(f"압축 완료: {output_zip_file}")
    # # 압축 대상 폴더 삭제
    # if os.path.exists(outfoler):
    #     shutil.rmtree(outfoler)
    #     print(f"폴더 삭제 완료: {outfoler}")
    # else:
    #     print(f"폴더가 존재하지 않습니다: {outfoler}")
    
    return output_zip_file

# boltz 인풋파일 생성
def boltzInputDataGenerate(job, datas, folder_path):
    boltz_input_file = f"{folder_path}/{job}.fasta"
    
    print("boltz_input_file")
    print(datas)
    
    # 알파벳 리스트 생성
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alphabet_idx = 0  # 알파벳 인덱스 초기화

    with open(boltz_input_file, "w") as fasta:
        for data in datas:
            for _ in range(data['Copies']):  # Copies 수만큼 반복
                if alphabet_idx >= len(alphabet):  # 알파벳이 다 쓰이면 종료
                    break
                current_alphabet = alphabet[alphabet_idx]  # 현재 알파벳 선택
                alphabet_idx += 1  # 다음 알파벳으로 이동

                if data['Entity'] == 'Protein':
                    print("protein")
                    fasta.write(f">{current_alphabet}|protein|\n")
                    fasta.write(f"{data['Content']}\n")
                elif data['Entity'] == 'Ligand':
                    print("ligand")
                    fasta.write(f">{current_alphabet}|smiles|\n")
                    fasta.write(f"{data['Content']}\n")
    return boltz_input_file

def runBoltz(input_path, output_path):
    if not input_path or not output_path:
        print("Error: Both input and output paths must be provided.")
        sys.exit(1)
    
    recycling_steps = 3
    sampling_steps = 200
    num_workers = 4
    
    # Boltz 실행 명령어 구성
    run = [
        "/opt/anaconda3/envs/boltz/bin/boltz",
        "predict",
        f"{input_path}",
        "--out_dir", f"{output_path}/",
        "--cache", "/opt/git_tools/boltz/model/",
        "--recycling_steps", str(recycling_steps),
        "--sampling_steps", str(sampling_steps),
        "--diffusion_samples", "5",
        "--num_workers", str(num_workers),
        "--use_msa_server"
    ]
     # 계산 시작 시간 기록
    start_time = datetime.now()
    print(f"Boltz 계산 중... 잠시만 기다려 주세요. (시작 시간: {start_time})")

    # Boltz 실행
    result_boltz = subprocess.run(run, capture_output=True, text=True)

    # 계산 종료 시간 기록
    end_time = datetime.now()

    if result_boltz.returncode != 0:
        print("Boltz 실행 중 오류가 발생했습니다.")
        print(f"오류 메시지: {result_boltz.stderr}")
    else:
        elapsed_time = end_time - start_time
        print(f"결과는 {output_path}에서 저장되었습니다!")
        print(f"결과 파일은 boltz_results_[input 파일 이름]/predictions/[input 파일 이름] 내에 .cif 형태로 저장되었습니다!")
        print(f"총 소요 시간: {elapsed_time}")

        # 결과 디렉토리에서 스코어 추출 및 CSV 저장
        # 입력 파일 이름에서 확장자 제거
        input_basename = os.path.splitext(os.path.basename(input_path))[0]
        predictions_folder = os.path.join(output_path, f"boltz_results_{input_basename}/predictions/{input_basename}")
        
        if not os.path.exists(predictions_folder):
            print(f"예상된 결과 폴더가 없습니다: {predictions_folder}")
        else:
            score_files = [f for f in os.listdir(predictions_folder) if f.startswith("confidence_") and f.endswith(".json")]
            
            if not score_files:
                print("스코어 파일이 발견되지 않았습니다.")
            else:
                # 주요 스코어 추출
                data = []
                for score_file in score_files:
                    score_path = os.path.join(predictions_folder, score_file)
                    with open(score_path, "r") as f:
                        json_data = json.load(f)
                    
                    # 주요 스코어 추출
                    confidence_score = json_data.get("confidence_score")
                    ptm = json_data.get("ptm")
                    iptm = json_data.get("iptm")
                    ligand_iptm = json_data.get("ligand_iptm")
                    complex_plddt = json_data.get("complex_plddt")
                    complex_iplddt = json_data.get("complex_iplddt")
                    
                    # 데이터 추가
                    data.append({
                        "File": score_file,
                        "Confidence Score": confidence_score,
                        "PTM": ptm,
                        "IPTM": iptm,
                        "Ligand IPTM": ligand_iptm,
                        "Complex pLDDT": complex_plddt,
                        "Complex ipLDDT": complex_iplddt,
                    })

                # DataFrame으로 변환 및 반올림
                df = pd.DataFrame(data)
                df = df.round(3)  # 소수점 세 자리로 반올림

                # CSV 저장
                csv_path = os.path.join(predictions_folder, "scores_summary.csv")
                df.to_csv(csv_path, index=False)
                print(f"스코어 요약이 CSV 파일로 저장되었습니다: {csv_path}")
    
    return predictions_folder

# Alphafold 
def alphafoldInputDataGenerate(job, datas, folder_path):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alphabet_idx = 0

    sequences = []  # JSON 데이터를 위한 시퀀스 리스트

    for data in datas:
        for _ in range(data['Copies']):
            if alphabet_idx >= len(alphabet):
                break
            current_alphabet = alphabet[alphabet_idx]
            alphabet_idx += 1

            if data['Entity'] == 'Protein':
                sequences.append({
                    "protein": {
                        "id": current_alphabet,
                        "sequence": data['Content']
                    }
                })
            elif data['Entity'] == 'Ligand':
                sequences.append({
                    "ligand": {
                        "id": current_alphabet,
                        "smiles": data['Content']
                    }
                })

    # JSON 생성
    json_data = {
        "name": job,
        "sequences": sequences,
        "modelSeeds": [1],
        "dialect": "alphafold3",
        "version": 1
    }

    # JSON 파일 저장
    json_file = f"{folder_path}/{job}.json"
    with open(json_file, "w") as json_out:
        json.dump(json_data, json_out, indent=4)

    return json_file

# 전역 변수로 컨테이너 ID를 저장
container_id = None

def cleanup_container(signum, frame):
    """SIGINT 신호를 처리해서 도커 컨테이너 종료"""
    global container_id
    if container_id:
        try:
            print(f"\nStopping container {container_id}...")
            subprocess.run(["docker", "stop", container_id], check=False)
            subprocess.run(["docker", "rm", container_id], check=False)
            print(f"Container {container_id} has been stopped and removed.")
        except Exception as e:
            print(f"Error while stopping container {container_id}: {e}")
    else:
        print("No active container to stop.")

def runAlphafold(input_path, output_path):
    if not input_path or not output_path:
        print("Error: Both input and output paths must be provided.")
        sys.exit(1)
        
    global container_id
    try:
        run = [
            "docker", "run", "-d",
            "--volume", f"{input_path}:/root/af_input",
            "--volume", f"{output_path}:/root/af_output",
            "--volume", "/opt/git_tools/alphafold3/models/:/root/models",
            "--volume", "/data0/AF3DB/:/root/public_databases",
            "--gpus", "device=3",
            "alphafold3",
            "python", "run_alphafold.py",
            "--input_dir=/root/af_input",
            "--model_dir=/root/models",
            "--output_dir=/root/af_output"
        ]
        result = subprocess.run(run, stdout=subprocess.PIPE, text=True, check=True)
        
        container_id = result.stdout.strip()  # 실행된 컨테이너 ID 가져오기
        print(f"Started container with ID: {container_id}")
        
        # 컨테이너 실행 상태 유지
        subprocess.run(["docker", "logs", "-f", container_id])
    except Exception as e:
        print(f"Error occurred during AF3 execution: {e}")
        raise
    finally:
        cleanup_container(None, None)
        



def chaiInputDataGenerate(job, datas, folder_path):
    chai_input_file = f"{folder_path}/{job}.fasta"
    
    print("chai_input_file")
    print(datas)
    
    # 알파벳 리스트 생성
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alphabet_idx = 0  # 알파벳 인덱스 초기화

    with open(chai_input_file, "w") as fasta:
        for data in datas:
            for _ in range(data['Copies']):  # Copies 수만큼 반복
                if alphabet_idx >= len(alphabet):  # 알파벳이 다 쓰이면 종료
                    break
                current_alphabet = alphabet[alphabet_idx]  # 현재 알파벳 선택
                alphabet_idx += 1  # 다음 알파벳으로 이동

                if data['Entity'] == 'Protein':
                    # print("protein")
                    fasta.write(f">protein|name=chain_{current_alphabet}\n")  
                    fasta.write(f"{data['Content']}\n")
                elif data['Entity'] == 'Ligand':
                    # print("ligand")
                    fasta.write(f">ligand|name=smiles{current_alphabet}\n")  
                    fasta.write(f"{data['Content']}\n")
                    
    return chai_input_file

def runChai(input_path, output_path):
    if not input_path or not output_path:
        print("Error: Both input and output paths must be provided.")
        sys.exit(1)
    
    output_path_final = f"{output_path}_chai_result"
    
    chai_run = [
        "/opt/anaconda3/envs/chai-lab/bin/python",
        "/opt/git_tools/chai-lab/web_run.py",
        input_path,
        output_path_final
    ]
    print("chai_run")
    chai_run = subprocess.run(chai_run, capture_output=True, text=True, check=True)
    return output_path_final
    