import subprocess
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# 활동 기록 로깅 함수
def log_activity(action, details):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # audit.log 파일에 기록
    with open('./audit.log', 'a') as log_file:
        log_file.write(f"{timestamp} - {action}: {details}\n")

# 사용자 추가 (POST /users)
@app.route('/users', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if username and password:
        try:
            subprocess.run(['htpasswd', '-b', '/home/ubuntu/hw_1/htpasswd', username, password], check=True)
            log_activity('USER_ADD', f"User {username} added.")
            return jsonify({"message": f"User {username} added successfully"}), 201
        except subprocess.CalledProcessError:
            return jsonify({"error": "Failed to add user"}), 500
    else:
        return jsonify({"error": "Username and password are required"}), 400

# 사용자 조회 (GET /users)
@app.route('/users', methods=['GET'])
def list_users():
    try:
        users = subprocess.run(['cat', '/home/ubuntu/hw_1/htpasswd'], capture_output=True, text=True)
        return jsonify({"users": users.stdout.splitlines()}), 200
    except subprocess.CalledProcessError:
        return jsonify({"error": "Failed to retrieve users"}), 500

# 사용자 삭제 (DELETE /users/<user>)
@app.route('/users/<user>', methods=['DELETE'])
def delete_user(user):
    try:
        subprocess.run(['htpasswd', '-D', '/home/ubuntu/hw_1/htpasswd', user], check=True)
        log_activity('USER_DELETE', f"User {user} deleted.")
        return jsonify({"message": f"User {user} deleted successfully"}), 200
    except subprocess.CalledProcessError:
        return jsonify({"error": f"Failed to delete user {user}"}), 500

# 이미지 목록 조회 (GET /images)
@app.route('/images', methods=['GET'])
def list_images():
    result = subprocess.run(['curl', 'http://localhost:5000/v2/_catalog'], capture_output=True, text=True)
    return jsonify({"repositories": result.stdout}), 200

# 특정 이미지 삭제 (DELETE /images/<name>)
@app.route('/images/<name>', methods=['DELETE'])
def delete_image(name):
    try:
        subprocess.run(['docker', 'rmi', f'localhost:5000/{name}'], check=True)
        log_activity('DELETE', f"Image {name} deleted from registry.")
        return jsonify({"message": f"Image {name} deleted successfully"}), 200
    except subprocess.CalledProcessError:
        return jsonify({"error": f"Failed to delete image {name}"}), 500

# 특정 이미지의 태그 조회 (GET /images/<name>/tags)
@app.route('/images/<name>/tags', methods=['GET'])
def get_image_tags(name):
    result = subprocess.run(['curl', f'http://localhost:5000/v2/{name}/tags/list'], capture_output=True, text=True)
    return jsonify({"tags": result.stdout}), 200

# 특정 이미지의 태그 삭제 (DELETE /images/<name>/tags/<tag>)
@app.route('/images/<name>/tags/<tag>', methods=['DELETE'])
def delete_image_tag(name, tag):
    subprocess.run(['curl', '-X', 'DELETE', f'http://localhost:5000/v2/{name}/manifests/{tag}'])
    log_activity('TAG_DELETE', f"Tag {tag} for image {name} deleted.")
    return jsonify({"message": f"Tag {tag} for image {name} deleted successfully"}), 200

# 사용자 별 조회
@app.route('/audit/user', methods=['GET'])
def audit_user():
    user = request.args.get('user')
    if user:  # 'user' 파라미터가 있을 때만 이 함수 실행
        try:
            with open('./audit.log', 'r') as log_file:
                logs = log_file.readlines()
                user_logs = [log for log in logs if log and user in log]  # user가 포함된 로그만 필터링

            if not user_logs:
                return jsonify({"message": f"No activity found for user {user}."}), 200
            
            return jsonify({"audit": user_logs}), 200
        except FileNotFoundError:
            return jsonify({"error": "Audit log file not found"}), 500
    else:
        return jsonify({"error": "User parameter is required"}), 400

# 이미지 별 조회
@app.route('/audit/image', methods=['GET'])
def audit_image():
    image = request.args.get('image')
    if image:  # 'image' 파라미터가 있을 때만 이 함수 실행
        try:
            with open('./audit.log', 'r') as log_file:
                logs = log_file.readlines()
                image_logs = [log for log in logs if log and image in log]  # image가 포함된 로그만 필터링

            if not image_logs:
                return jsonify({"message": f"No activity found for image {image}."}), 200

            return jsonify({"audit": image_logs}), 200
        except FileNotFoundError:
            return jsonify({"error": "Audit log file not found"}), 500
    else:
        return jsonify({"error": "Image parameter is required"}), 400

# 이미지 푸시 (POST /images/<image_name>/push)
@app.route('/images/<image_name>/push', methods=['POST'])
def push_image(image_name):
    tag = request.args.get('tag', 'latest')
    subprocess.run(['docker', 'tag', f'{image_name}:{tag}', f'localhost:5000/{image_name}:{tag}'])
    subprocess.run(['docker', 'push', f'localhost:5000/{image_name}:{tag}'])
    
    # 활동 기록 남기기
    log_activity('PUSH', f"Image {image_name} with tag {tag} pushed to registry.")
    
    return jsonify({"message": f"Image {image_name} pushed successfully"}), 200

# 이미지 풀 (GET /images/<image_name>/pull)
@app.route('/images/<image_name>/pull', methods=['GET'])
def pull_image(image_name):
    tag = request.args.get('tag', 'latest')
    subprocess.run(['docker', 'pull', f'localhost:5000/{image_name}:{tag}'])
    
    # 활동 기록 남기기
    log_activity('PULL', f"Image {image_name} with tag {tag} pulled from registry.")
    
    return jsonify({"message": f"Image {image_name} pulled successfully"}), 200

# 이미지 태그 수정 (POST /images/<image_name>/tags/<old_tag>/update)
@app.route('/images/<image_name>/tags/<old_tag>/update', methods=['POST'])
def update_tag(image_name, old_tag):
    new_tag = request.args.get('new_tag', 'latest')
    subprocess.run(['docker', 'tag', f'localhost:5000/{image_name}:{old_tag}', f'localhost:5000/{image_name}:{new_tag}'])
    
    # 활동 기록 남기기
    log_activity('TAG_UPDATE', f"Tag {old_tag} updated to {new_tag} for image {image_name}.")
    
    return jsonify({"message": f"Tag {old_tag} updated to {new_tag} for image {image_name}"}), 200

@app.route('/v2/', methods=['GET'])
def registry_version():
    try:
        result = subprocess.run(
            ['curl', 'http://registry:5000/v2/'],  # Docker Registry에 연결하여 버전 정보 요청
            capture_output=True, text=True
        )
        
        # 결과가 정상적으로 반환되었는지 확인
        if result.returncode == 0:
            return jsonify({"message": "Registry API is accessible", "version": result.stdout.strip()}), 200
        else:
            # 오류 발생 시 stderr 출력
            return jsonify({"error": f"Failed to get version info from registry: {result.stderr}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v2/<name>/manifests/<reference>', methods=['GET', 'PUT'])
def handle_manifest(name, reference):
    if request.method == 'GET':
        try:
            # 이미지 매니페스트 조회
            result = subprocess.run(['curl', f'http://localhost:5000/v2/{name}/manifests/{reference}'], capture_output=True, text=True)
            if result.returncode == 0:
                return jsonify({"manifest": result.stdout}), 200
            else:
                return jsonify({"error": "Failed to fetch manifest"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'PUT':
        # 매니페스트 업로드
        manifest = request.json.get('manifest')
        if not manifest:
            return jsonify({"error": "Manifest content is required"}), 400

        try:
            # 매니페스트 업로드
            subprocess.run(['curl', '-X', 'PUT', f'http://localhost:5000/v2/{name}/manifests/{reference}', '--data', manifest], check=True)
            return jsonify({"message": f"Manifest for {name}:{reference} uploaded successfully"}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({"error": str(e)}), 500

@app.route('/v2/<name>/blobs/<digest>', methods=['GET'])
def get_blob(name, digest):
    try:
        # 레이어 파일 다운로드
        result = subprocess.run(['curl', f'http://localhost:5000/v2/{name}/blobs/{digest}'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"blob": result.stdout}), 200
        else:
            return jsonify({"error": "Failed to fetch blob"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
