
# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
## TODO
if ! command -v conda &> /dev/null; then
    echo "[INFO] conda가 없습니다. Miniconda를 설치합니다."

    MINICONDA=Miniconda3-latest-Linux-x86_64.sh
    wget https://repo.anaconda.com/miniconda/$MINICONDA
    bash $MINICONDA -b -p $HOME/miniconda
    rm $MINICONDA

    export PATH="$HOME/miniconda/bin:$PATH"
    source "$HOME/miniconda/etc/profile.d/conda.sh"
else
    echo "[INFO] conda가 이미 설치되어 있습니다."
fi



# Conda 환경 생성 및 활성화
## TODO
if conda env list | grep -q "^myenv"; then
    echo "[INFO] myenv 환경이 이미 존재합니다."
else
    echo "[INFO] myenv 환경을 생성합니다."
    conda create -y -n myenv python=3.10
fi


source "$(conda info --base)/etc/profile.d/conda.sh"

conda activate myenv


## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi

# 필요한 패키지 설치
## TODO
echo "[INFO] 필요한 패키지 설치를 시작합니다."

python -m ensurepip --upgrade || true
python -m pip install --upgrade pip setuptools wheel

python -m pip install "mypy>=1.0"



# Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    ## TODO
    base="${file%.py}"          # 변수 끝에 패턴이 있으면 제거(.py가 제거됨)
    prob="${base#*_}"           # 변수 앞에서 패턴에 맞는 부분 제거(*: 아무 문자열, _: 언더바), submission 파일의 파일 형식의 앞부분이 제거되어 문항 번호만 남음

    echo "[INFO] 실행 중: $file (input: ${prob}_input → output: ${prob}_output)"

    python "$file" < "../input/${prob}_input" > "../output/${prob}_output"

done

# mypy 테스트 실행 및 mypy_log.txt 저장
## TODO
echo "[INFO] mypy 테스트를 실행합니다."

mypy *.py > ../mypy_log.txt 

# conda.yml 파일 생성
## TODO
echo "[INFO] conda 환경 정보를 conda.yml로 저장합니다."

conda env export -n myenv > ../conda.yml

# 가상환경 비활성화
## TODO
echo "[INFO] 가상환경을 비활성화합니다."

conda deactivate