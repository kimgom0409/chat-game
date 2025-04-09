# 필요한 라이브러리 가져오기
from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS 라이브러리 가져오기
import json
import os

# --- 설정 ---
DATA_FILE = 'game_data.json' # 게임 상태를 저장할 파일 이름

# --- Flask 앱 설정 ---
app = Flask(__name__)
CORS(app) # 모든 경로에 대해 CORS 활성화 (프론트엔드 요청 허용)

# --- 도우미 함수: 기본 게임 상태 가져오기 ---
# 자바스크립트의 기본 상태와 동일하게 정의합니다.
def get_default_game_state():
    return {
        "points": 0,
        "weapon": {"level": 1, "ap": 10, "crit": 5},
        "mission": {"chatsToday": 0, "targetChats": 5, "reward": 50, "completedToday": False},
        "boost": {"active": False, "endTime": 0, "multiplier": 2, "durationMinutes": 1, "cost": 200},
        "enemy": {"hp": 500, "maxHp": 500, "attackCost": 5},
        "lastLoginDate": None, # 첫 로드/저장 시 필요에 따라 설정됨
        "leaderboard": [],
        "chatHistory": []
    }

# --- API 경로 (라우트) ---

@app.route('/load', methods=['GET'])
def load_game():
    """
    /load 경로로 들어오는 GET 요청을 처리합니다.
    DATA_FILE에서 게임 상태를 읽어 반환합니다.
    파일이 없으면 기본 상태를 반환합니다.
    """
    try:
        if os.path.exists(DATA_FILE):
            # 파일이 존재하면 파일을 엽니다. utf-8 인코딩 사용.
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                game_state = json.load(f) # JSON 데이터를 파이썬 딕셔너리로 로드
                print(f"{DATA_FILE}에서 게임 상태 로드 완료")
                # 간단한 유효성 검사 (선택 사항이지만 권장)
                if not isinstance(game_state, dict) or 'points' not in game_state:
                     print(f"{DATA_FILE}에서 유효하지 않은 데이터 발견. 기본 상태 반환.")
                     game_state = get_default_game_state()
        else:
            # 파일이 존재하지 않으면 기본 상태 사용
            print(f"{DATA_FILE} 파일을 찾을 수 없음. 기본 상태 반환.")
            game_state = get_default_game_state()
            # 필요하다면 여기서 기본 상태를 즉시 파일에 저장할 수도 있습니다.
            # with open(DATA_FILE, 'w', encoding='utf-8') as f:
            #     json.dump(game_state, f, ensure_ascii=False, indent=4)
        return jsonify(game_state) # 게임 상태를 JSON 응답으로 반환
    except json.JSONDecodeError:
        # JSON 파일 디코딩 오류 처리
        print(f"{DATA_FILE} 파일의 JSON 디코딩 오류. 기본 상태 반환.")
        return jsonify(get_default_game_state()), 500 # 500 내부 서버 오류 코드 반환
    except Exception as e:
        # 기타 예외 처리
        print(f"로드 중 오류 발생: {e}")
        # 오류 발생 시 프론트엔드 문제 방지를 위해 기본 상태 반환
        return jsonify(get_default_game_state()), 500 # 500 내부 서버 오류 코드 반환

@app.route('/save', methods=['POST'])
def save_game():
    """
    /save 경로로 들어오는 POST 요청을 처리합니다.
    요청 본문(body)에서 JSON 형식의 게임 상태 데이터를 받아,
    간단히 유효성을 검사하고 DATA_FILE에 저장합니다.
    """
    try:
        game_state = request.get_json() # 요청 본문에서 JSON 데이터 가져오기

        # 기본 유효성 검사 (딕셔너리 형태인지 확인)
        if not game_state or not isinstance(game_state, dict):
            print("저장을 위해 유효하지 않은 데이터 수신.")
            # 400 잘못된 요청 코드 반환
            return jsonify({"status": "error", "message": "잘못된 데이터 형식"}), 400

        # 필요하다면 여기서 더 구체적인 키/타입 유효성 검사를 추가할 수 있습니다.

        # 파일을 쓰기 모드('w')로 열고 JSON 데이터를 저장합니다. utf-8 인코딩 사용.
        # ensure_ascii=False: 비 ASCII 문자(한글 등)를 그대로 저장
        # indent=4: 보기 좋게 4칸 들여쓰기
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_state, f, ensure_ascii=False, indent=4)
        print(f"게임 상태를 {DATA_FILE}에 저장 완료")
        # 성공 상태를 JSON 응답으로 반환
        return jsonify({"status": "success", "message": "게임 저장됨"})
    except Exception as e:
        # 저장 중 발생한 예외 처리
        print(f"저장 중 오류 발생: {e}")
        # 500 내부 서버 오류 코드 반환
        return jsonify({"status": "error", "message": "게임 저장 실패"}), 500

# --- 앱 실행 ---
if __name__ == '__main__':
    # host='0.0.0.0' : 서버를 로컬 네트워크에서 접근 가능하게 함
    # port=5000 : 개발 시 흔히 사용하는 포트 번호
    # debug=True : 개발 중 유용한 오류 메시지 제공 (실제 서비스 시에는 False로 변경)
    print(f"Flask 서버 시작 중. 데이터 파일: {DATA_FILE}")
    app.run(host='0.0.0.0', port=5000, debug=True)
