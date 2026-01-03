from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import time
import json
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于会话加密

# 数据文件路径
USER_RECORDS_FILE = 'user_records.json'  # 存储用户所有答题记录

# 按拼音排序的用户列表
PRESET_USERS = [
    "陈柏坤", "程瑶", "高冬东", "黄秋秋", "蒋琼明",
    "蓝声宁", "李达耀", "陆海平", "邱晓娟", "孙彦增",
    "韦春晓", "韦静月", "魏蔚", "徐艳霞", "杨再智",
    "张坤鹏", "张志雄", "周英明"
]

# 党史知识题库
QUESTIONS = [
    {
        "id": 1,
        "question": "中共一大召开的时间是？",
        "options": ["1921年7月1日", "1921年7月23日", "1921年8月1日", "1922年7月23日"],
        "answer": 1
    },
    {
        "id": 2,
        "question": "中共一大的召开地点最初在哪里？",
        "options": ["北京", "上海", "武汉", "广州"],
        "answer": 1
    },
    {
        "id": 3,
        "question": "中共一大有多少名代表参加？",
        "options": ["12人", "13人", "15人", "20人"],
        "answer": 1
    },
    {
        "id": 4,
        "question": "《共产党宣言》最早传入中国的时间是？",
        "options": ["1899年2月", "1917年10月", "1920年8月", "1921年7月"],
        "answer": 0
    },
    {
        "id": 5,
        "question": "最早将《共产党宣言》全文翻译成中文的是？",
        "options": ["李大钊", "陈独秀", "陈望道", "毛泽东"],
        "answer": 2
    },
    {
        "id": 6,
        "question": "古田会议召开于何时？",
        "options": ["1928年12月", "1929年12月28日至29日", "1930年1月", "1931年11月"],
        "answer": 1
    },
    {
        "id": 7,
        "question": "\"支部建在连上\"这一原则确立于哪次会议？",
        "options": ["八七会议", "三湾改编", "古田会议", "遵义会议"],
        "answer": 1
    },
    {
        "id": 8,
        "question": "红军长征开始和结束的时间分别是？",
        "options": ["1934年9月，1935年10月", "1934年10月，1936年10月", "1935年1月，1936年10月", "1935年10月，1936年10月"],
        "answer": 1
    },
    {
        "id": 9,
        "question": "红军三大主力大会师的时间是？",
        "options": ["1935年10月", "1936年10月9日", "1936年10月22日", "1937年7月"],
        "answer": 1
    },
    {
        "id": 10,
        "question": "红军长征的总长度约为？",
        "options": ["约25000里", "约32500公里", "约8000公里", "约15000里"],
        "answer": 0
    },
    {
        "id": 11,
        "question": "毛泽东《论持久战》发表于何时？",
        "options": ["1937年7月", "1938年5月", "1939年9月", "1940年1月"],
        "answer": 1
    },
    {
        "id": 12,
        "question": "百团大战发生于哪一时间段？",
        "options": ["1939年底至1940年初", "1940年8月至1941年1月", "1941年1月至1941年8月", "1942年5月至1943年2月"],
        "answer": 1
    },
    {
        "id": 13,
        "question": "中国抗日战争历时多少年？",
        "options": ["8年", "10年", "14年", "15年"],
        "answer": 2
    },
    {
        "id": 14,
        "question": "遵义会议召开的时间是？",
        "options": ["1934年12月", "1935年1月15日至17日", "1935年2月", "1935年3月"],
        "answer": 1
    },
    {
        "id": 15,
        "question": "四渡赤水中的第三次渡河发生在何时？",
        "options": ["1935年1月29日", "1935年2月20日", "1935年3月16日", "1935年3月21日至22日"],
        "answer": 2
    },
    {
        "id": 16,
        "question": "解放军将红旗插上南京总统府的时间是？",
        "options": ["1949年4月21日", "1949年4月24日凌晨", "1949年5月27日", "1949年10月1日"],
        "answer": 1
    },
    {
        "id": 17,
        "question": "下列哪一项不属于解放战争中的\"三大战役\"？",
        "options": ["辽沈战役", "淮海战役", "平津战役", "渡江战役"],
        "answer": 3
    },
    {
        "id": 18,
        "question": "上海解放的时间是？",
        "options": ["1949年4月21日至5月27日", "1949年5月12日至6月2日", "1949年5月27日", "1949年6月2日"],
        "answer": 1
    },
    {
        "id": 19,
        "question": "\"两个务必\"是在哪次会议上提出的？",
        "options": ["中共七大", "七届二中全会", "中共八大", "七届三中全会"],
        "answer": 1
    },
    {
        "id": 20,
        "question": "中华人民共和国成立的时间是？",
        "options": ["1949年9月21日", "1949年10月1日", "1949年12月26日", "1950年1月1日"],
        "answer": 1
    }
]

# 从文件加载用户所有记录
def load_user_records():
    if os.path.exists(USER_RECORDS_FILE):
        try:
            with open(USER_RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # 如果文件损坏，尝试备份并重新创建
            try:
                if os.path.exists(USER_RECORDS_FILE):
                    backup_file = USER_RECORDS_FILE + '.backup'
                    os.rename(USER_RECORDS_FILE, backup_file)
                return []
            except:
                return []
    return []

# 保存用户所有记录到文件
def save_user_records(records):
    try:
        with open(USER_RECORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False

# 获取用户今日剩余答题次数
def get_remaining_attempts(username):
    today = date.today().isoformat()  # 获取今天的日期，格式为YYYY-MM-DD
    
    # 从user_records.json中获取用户今日的答题记录
    user_records = load_user_records()
    today_results_count = 0
    for record in user_records:
        # 从时间戳中提取日期部分
        timestamp = record.get('timestamp', '')
        if timestamp and record['username'] == username:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                result_date = dt.date().isoformat()
                if result_date == today:
                    today_results_count += 1
            except:
                # 如果时间戳解析失败，跳过该记录
                continue
    
    # 返回剩余次数，确保不会返回负数
    return max(0, 3 - today_results_count)

# 增加用户今日答题次数
def increment_daily_attempts(username):
    # 这个函数现在只用于检查是否还有剩余次数
    # 实际的计数由get_remaining_attempts函数通过user_records.json计算
    remaining = get_remaining_attempts(username)
    if remaining <= 0:
        return -1  # 表示没有剩余次数
    return remaining - 1  # 返回更新后的剩余次数



@app.route('/')
def index():
    return render_template('login.html', users=PRESET_USERS)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username in PRESET_USERS:
        session['username'] = username
        return redirect(url_for('show_rankings'))
    return redirect(url_for('index'))

@app.route('/rankings')
def show_rankings():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # 获取用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    
    # 从user_records.json中获取所有用户记录
    user_records = load_user_records()
    
    # 筛选今天的结果
    today = date.today().isoformat()
    today_results = []
    for record in user_records:
        # 从时间戳中提取日期部分
        timestamp = record.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                result_date = dt.date().isoformat()
                if result_date == today:
                    today_results.append(record)
            except:
                # 如果时间戳解析失败，跳过该记录
                continue
    
    # 确保每个用户只保留最佳成绩
    user_best_scores = {}
    for record in today_results:
        username = record['username']
        # 如果用户没有记录，或者当前记录比已有记录更好，则更新
        if (username not in user_best_scores or 
            record['score'] > user_best_scores[username]['score'] or 
            (record['score'] == user_best_scores[username]['score'] and record['total_time'] < user_best_scores[username]['total_time'])):
            user_best_scores[username] = record
    
    # 转换为列表并排序
    results = list(user_best_scores.values())
    sorted_results = sorted(results, key=lambda x: (-x['score'], x['total_time']))
    
    # 格式化所有结果的时间
    formatted_results = []
    for i, result in enumerate(sorted_results):
        # 解析时间戳
        timestamp = result.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                formatted_timestamp = dt.strftime('%m-%d %H:%M')
            except:
                formatted_timestamp = timestamp
        else:
            formatted_timestamp = ''
        
        formatted_result = {
            'rank': i + 1,
            'username': result['username'],
            'score': result['score'],
            'total_time': result['total_time'],
            'minutes': int(result['total_time'] // 60),
            'seconds': int(result['total_time'] % 60),
            'milliseconds': int((result['total_time'] % 1) * 1000),  # 添加毫秒部分
            'timestamp': formatted_timestamp,
            'is_current_user': result['username'] == session['username']
        }
        formatted_results.append(formatted_result)
    
    return render_template('rankings.html', 
                          username=session['username'],
                          remaining_attempts=remaining_attempts,
                          rankings=formatted_results)

@app.route('/quiz')
def quiz():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # 检查用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    if remaining_attempts <= 0:
        return render_template('no_attempts.html', 
                              username=session['username'],
                              remaining_attempts=0)
    
    # 预先减少一次答题机会，确保用户开始答题时就计数
    remaining_attempts = increment_daily_attempts(session['username'])
    if remaining_attempts < 0:  # 如果increment返回负数，说明已经没有机会了
        return render_template('no_attempts.html', 
                              username=session['username'],
                              remaining_attempts=0)
    
    # 记录开始时间
    session['start_time'] = time.time()
    
    # 随机打乱题目顺序
    shuffled_questions = random.sample(QUESTIONS, len(QUESTIONS))
    session['questions'] = shuffled_questions
    session['current_question'] = 0
    session['answers'] = []
    session['score'] = 0
    
    return render_template('quiz.html', 
                          username=session['username'],
                          remaining_attempts=remaining_attempts,
                          question=shuffled_questions[0],
                          question_number=1,
                          total_questions=len(shuffled_questions))

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    if remaining_attempts <= 0:
        return jsonify({'error': 'no_attempts', 'message': '今日答题次数已用完'}), 403
    
    answer = int(request.form.get('answer'))
    current_question = session['current_question']
    questions = session['questions']
    
    # 检查答案
    correct = answer == questions[current_question]['answer']
    if correct:
        session['score'] += 1
    
    session['answers'].append({
        'question_id': questions[current_question]['id'],
        'user_answer': answer,
        'correct': correct
    })
    
    # 移动到下一题或结束
    if current_question < len(questions) - 1:
        session['current_question'] += 1
        next_question = questions[session['current_question']]
        return jsonify({
            'next_question': True,
            'question': next_question,
            'question_number': session['current_question'] + 1,
            'total_questions': len(questions)
        })
    else:
        # 计算总用时
        end_time = time.time()
        total_time = end_time - session['start_time']
        
        # 获取当前剩余答题次数
        remaining_attempts = get_remaining_attempts(session['username'])
        
        # 从文件加载用户所有记录
        user_records = load_user_records()
        
        # 创建新的用户记录
        new_record = {
            'username': session['username'],
            'score': session['score'],
            'total_time': total_time,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存到用户所有记录中
        user_records.append(new_record)
        save_user_records(user_records)
        
        # 从user_records中计算排行榜
        # 筛选今天的结果
        today = date.today().isoformat()
        today_results = []
        for record in user_records:
            # 从时间戳中提取日期部分
            timestamp = record.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    result_date = dt.date().isoformat()
                    if result_date == today:
                        today_results.append(record)
                except:
                    # 如果时间戳解析失败，跳过该记录
                    continue
        
        # 确保每个用户只保留最佳成绩
        user_best_scores = {}
        for record in today_results:
            username = record['username']
            # 如果用户没有记录，或者当前记录比已有记录更好，则更新
            if (username not in user_best_scores or 
                record['score'] > user_best_scores[username]['score'] or 
                (record['score'] == user_best_scores[username]['score'] and record['total_time'] < user_best_scores[username]['total_time'])):
                user_best_scores[username] = record
        
        # 转换为列表并排序
        results = list(user_best_scores.values())
        sorted_results = sorted(results, key=lambda x: (-x['score'], x['total_time']))
        
        # 找到当前用户的排名
        user_rank = sorted_results.index(next(r for r in sorted_results if r['username'] == session['username'])) + 1
        
        # 将结果保存到session中
        session['final_score'] = session['score']
        session['final_time'] = total_time
        session['final_rank'] = user_rank
        
        return jsonify({
            'finished': True,
            'score': session['score'],
            'total_questions': len(questions),
            'total_time': total_time,
            'rank': user_rank,
            'results': sorted_results,
            'remaining_attempts': remaining_attempts
        })

@app.route('/no_attempts')
def no_attempts():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # 获取用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    
    return render_template('no_attempts.html', 
                          username=session['username'],
                          remaining_attempts=remaining_attempts)

@app.route('/api/rankings')
def get_rankings():
    # 从user_records.json中获取所有用户记录
    user_records = load_user_records()
    
    # 筛选今天的结果
    today = date.today().isoformat()
    today_results = []
    for record in user_records:
        # 从时间戳中提取日期部分
        timestamp = record.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                result_date = dt.date().isoformat()
                if result_date == today:
                    today_results.append(record)
            except:
                # 如果时间戳解析失败，跳过该记录
                continue
    
    # 确保每个用户只保留最佳成绩
    user_best_scores = {}
    for record in today_results:
        username = record['username']
        # 如果用户没有记录，或者当前记录比已有记录更好，则更新
        if (username not in user_best_scores or 
            record['score'] > user_best_scores[username]['score'] or 
            (record['score'] == user_best_scores[username]['score'] and record['total_time'] < user_best_scores[username]['total_time'])):
            user_best_scores[username] = record
    
    # 转换为列表并排序
    results = list(user_best_scores.values())
    sorted_results = sorted(results, key=lambda x: (-x['score'], x['total_time']))
    
    # 格式化结果
    formatted_results = []
    for i, result in enumerate(sorted_results):
        formatted_results.append({
            'rank': i + 1,
            'username': result['username'],
            'score': result['score'],
            'total_time': result['total_time']
        })
    
    return jsonify({'rankings': formatted_results})

@app.route('/api/rankings/check')
def check_rankings_update():
    # 从user_records.json中获取所有用户记录
    user_records = load_user_records()
    
    # 筛选今天的结果
    today = date.today().isoformat()
    today_results = []
    for record in user_records:
        # 从时间戳中提取日期部分
        timestamp = record.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                result_date = dt.date().isoformat()
                if result_date == today:
                    today_results.append(record)
            except:
                # 如果时间戳解析失败，跳过该记录
                continue
    
    # 返回结果数量和最新结果的时间戳
    if today_results:
        latest_timestamp = max(record['timestamp'] for record in today_results)
        return jsonify({
            'count': len(today_results),
            'latest_timestamp': latest_timestamp
        })
    else:
        return jsonify({
            'count': 0,
            'latest_timestamp': None
        })

@app.route('/results')
def show_results():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # 获取用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    
    # 从user_records.json中获取所有用户记录
    user_records = load_user_records()
    
    # 筛选今天的结果
    today = date.today().isoformat()
    today_results = []
    for record in user_records:
        # 从时间戳中提取日期部分
        timestamp = record.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                result_date = dt.date().isoformat()
                if result_date == today:
                    today_results.append(record)
            except:
                # 如果时间戳解析失败，跳过该记录
                continue
    
    # 确保每个用户只保留最佳成绩
    user_best_scores = {}
    for record in today_results:
        username = record['username']
        if username not in user_best_scores:
            user_best_scores[username] = record
        else:
            # 如果新成绩更好（得分更高或得分相同但时间更短），则替换
            current_best = user_best_scores[username]
            if (record['score'] > current_best['score'] or 
                (record['score'] == current_best['score'] and record['total_time'] < current_best['total_time'])):
                user_best_scores[username] = record
    
    # 转换为列表并排序（按得分降序，时间升序）
    best_results = list(user_best_scores.values())
    sorted_results = sorted(best_results, key=lambda x: (-x['score'], x['total_time']))
    
    # 只返回前10名
    top_results = sorted_results[:10]
    
    # 格式化结果，添加排名
    formatted_results = []
    for i, result in enumerate(top_results):
        # 解析时间戳
        timestamp = result.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                formatted_timestamp = dt.strftime('%m-%d %H:%M')
            except:
                formatted_timestamp = timestamp
        else:
            formatted_timestamp = ''
        
        formatted_results.append({
            'rank': i + 1,
            'username': result['username'],
            'score': result['score'],
            'total_time': result['total_time'],
            'timestamp': formatted_timestamp,
            'is_current_user': 'username' in session and result['username'] == session['username']
        })
    
    # 获取当前用户的最新成绩
    current_user_results = [r for r in today_results if r['username'] == session['username']]
    current_user_score = 0
    current_user_time = 0
    current_user_rank = 0
    if current_user_results:
        # 找出当前用户的最佳成绩
        best_user_result = min(current_user_results, key=lambda x: (-x['score'], x['total_time']))
        current_user_score = best_user_result['score']
        current_user_time = best_user_result['total_time']
        
        # 计算当前用户的排名
        for i, result in enumerate(sorted_results):
            if result['username'] == session['username']:
                current_user_rank = i + 1
                break
    
    # 格式化当前用户的用时
    current_user_minutes = int(current_user_time // 60)
    current_user_seconds = int(current_user_time % 60)
    current_user_milliseconds = int((current_user_time % 1) * 1000)  # 添加毫秒部分
    
    # 格式化排名列表中的用时
    for item in formatted_results:
        item['minutes'] = int(item['total_time'] // 60)
        item['seconds'] = int(item['total_time'] % 60)
        item['milliseconds'] = int((item['total_time'] % 1) * 1000)  # 添加毫秒部分
    return render_template('results.html', 
                          username=session['username'],
                          score=current_user_score,
                          total_questions=20,  # 总共有20道题
                          minutes=current_user_minutes,
                          seconds=current_user_seconds,
                          milliseconds=current_user_milliseconds,  # 添加毫秒变量
                          rank=current_user_rank,
                          remaining_attempts=remaining_attempts,
                          rankings=formatted_results)

@app.route('/user_records')
def show_user_records():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # 获取用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    
    # 从文件加载用户所有记录
    user_records = load_user_records()
    
    # 筛选当前用户的记录
    current_user_records = [record for record in user_records if record['username'] == session['username']]
    
    # 按时间降序排序（最新的在前面）
    sorted_records = sorted(current_user_records, key=lambda x: x['timestamp'], reverse=True)
    
    # 找出最佳成绩（先按得分降序，再按时间升序）
    best_record = None
    if sorted_records:
        best_record = min(sorted_records, key=lambda x: (-x['score'], x['total_time']))
    
    # 格式化时间
    formatted_records = []
    for i, record in enumerate(sorted_records):
        # 解析时间戳
        timestamp = record.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_timestamp = timestamp
        else:
            formatted_timestamp = ''
        
        # 判断是否为最佳成绩
        is_best = best_record and record['score'] == best_record['score'] and record['total_time'] == best_record['total_time']
        
        formatted_record = {
            'id': i + 1,
            'username': record['username'],
            'score': record['score'],
            'total_time': record['total_time'],
            'minutes': int(record['total_time'] // 60),
            'seconds': int(record['total_time'] % 60),
            'milliseconds': int((record['total_time'] % 1) * 1000),  # 添加毫秒部分
            'timestamp': formatted_timestamp,
            'is_best': is_best
        }
        formatted_records.append(formatted_record)
    
    return render_template('user_records.html', 
                          username=session['username'],
                          remaining_attempts=remaining_attempts,
                          records=formatted_records)

@app.route('/api/attempts/check')
def check_attempts():
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 获取用户今日剩余答题次数
    remaining_attempts = get_remaining_attempts(session['username'])
    
    return jsonify({
        'remaining_attempts': remaining_attempts
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 从环境变量获取端口，默认为5000
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)