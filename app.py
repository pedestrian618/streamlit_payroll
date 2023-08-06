import streamlit as st
import datetime

global_night_start = "22:00"
global_night_end = "05:00"
global_overtime_hours = 8

# 深夜時間が何時間か計算する関数


def night_time(start, end):
    # 22:00と翌5:00をdatetimeオブジェクトとして定義
    night_start = datetime.datetime.strptime(global_night_start, "%H:%M")
    night_end = datetime.datetime.strptime(
        global_night_end, "%H:%M")+datetime.timedelta(days=1)  # 翌日の5:00

    # 入力時間が深夜時間とまったく被らない場合は0を返す
    if end <= night_start or start >= night_end:
        return 0

    # 入力の開始/終了時刻が22:00より前の場合、22:00に修正
    if start < night_start:
        start = night_start
    # 入力の終了時刻が翌5:00より後の場合、翌5:00に修正
    if end > night_end:
        end = night_end

    # 被っている時間を計算
    overlap = ((end - start).seconds // 900) / 4  # 時間単位での差を計算

    # 被っている時間が0未満（被っていない場合）なら0を返す
    return max(0, overlap)

# 給与計算


def calculate_pay(start_time, end_time, break_time, night_break_time, hourly_wage):
    # datetimeオブジェクトを生成
    start_time = datetime.datetime.strptime(start_time, "%H:%M")
    end_time = datetime.datetime.strptime(end_time, "%H:%M")
    # end が startより小さい＝日を跨いでいるとして、endに一日追加する。
    if end_time < start_time:
        end_time = end_time + datetime.timedelta(days=1)

    # 総拘束時間を計算（15分単位）
    total_hours = ((end_time - start_time).seconds // 900) / 4

    # ベース給与の計算
    total_work_hours = total_hours-(break_time + night_break_time)
    base_pay = hourly_wage*total_work_hours

    # 法定時間外労働直を計算
    overtime_hours = max(total_work_hours - global_overtime_hours, 0)
    overtime_pay = overtime_hours*0.25*hourly_wage

    # 深夜労働時間を計算
    night_hours = night_time(start_time, end_time)
    night_work_hours = max(night_hours-night_break_time, 0)
    night_pay = night_work_hours*0.25*hourly_wage

    # 給与の計算
    total_pay = base_pay + overtime_pay + night_pay

    return {'total_pay': round(total_pay, 2),  # 総報酬額
            'base_pay': base_pay,
            'overtime_pay': overtime_pay,
            'night_pay': night_pay,
            'total_hours': total_hours,  # 総拘束時間
            'total_work_hours': total_work_hours,  # 総労働時間
            'overtime_hours': overtime_hours,  # 時間外労働時間
            'night_work_hours': night_work_hours,  # 深夜労働時間
            }


# UI
st.title("給与計算アプリ")

start_time = st.text_input('開始時刻を入力してください (半角、24時間形式でHH：MM)', value='10:00')
end_time = st.text_input('終了時刻を入力してください (半角、24時間形式でHH：MM)', value='18:00')
break_time = st.number_input(
    '休憩時間を入力してください（時間）:', min_value=0.0, step=0.25, value=1.0)
night_break_time = st.number_input(
    '深夜休憩時間を入力してください（時間）:', min_value=0.0, step=0.25)
hourly_wage = st.number_input(
    '時給を入力してください（円）:', min_value=0, step=100, value=1000)

if st.button('計算'):
    pay_info = calculate_pay(start_time, end_time, break_time,
                             night_break_time, hourly_wage)
    st.write(f"支払い額：{pay_info['total_pay']} 円")
    st.write(f"基本(時給*総労働時間)：{pay_info['base_pay']}円")
    st.write(f"時間外割増額(時給×時間外労働時間×0.25)：{pay_info['overtime_pay']}円")
    st.write(f"深夜時間増額(時給×深夜帯労働時間×0.25)：{pay_info['night_pay']}円 ")
    st.write(f"総拘束時間：{pay_info['total_hours']} 時間")
    st.write(f"総労働時間：{pay_info['total_work_hours']} 時間")
    st.write(f"時間外労働時間：{pay_info['overtime_hours']} 時間")
    st.write(
        f"深夜帯労働時間({global_night_start}~{global_night_end})：{pay_info['night_work_hours']} 時間")
