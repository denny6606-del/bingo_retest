import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import pandas as pd
from collections import Counter

# ==================== 1. Firebase 初始化 ====================
if not firebase_admin._apps:
    try:
        if "firebase_creds" in st.secrets:
            creds_dict = json.loads(st.secrets["firebase_creds"])
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
        else:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Firebase 初始化失敗：{e}")

db = firestore.client()

# ==================== 2. Streamlit 介面配置 ====================
st.set_page_config(page_title="賓果大數據對撞艙", layout="wide")
st.title("🎯 賓果 BINGO BINGO 智能演算法戰術艙")

if st.sidebar.button("🔄 立即刷新雲端開獎數據"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=5)
def load_historical_data():
    try:
        docs = db.collection('bingo_history').order_by('issue', direction=firestore.Query.DESCENDING).limit(100).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error(f"讀取資料庫錯誤: {e}")
        return []

data = load_historical_data()
df = pd.DataFrame(data) if data else pd.DataFrame()

# ==================== 3. 全域最新開獎數據看板 ====================
if not df.empty:
    latest = data[0]
    current_issue_str = str(latest.get('issue', '---'))
    st.markdown(f"### 📡 官方即時連線：最新第 **{current_issue_str}** 期開獎")
    
    live_balls = sorted([int(b) for b in latest.get('numbers', [])])
    cols = st.columns(20)
    for i, ball_num in enumerate(live_balls):
        if i < len(cols):
            cols[i].markdown(
                f"<div style='text-align:center; background-color:#FF4B4B; color:white; "
                f"border-radius:50%; width:40px; height:40px; line-height:40px; "
                f"font-weight:bold; font-size:16px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>"
                f"{ball_num}</div>", 
                unsafe_allow_html=True
            )
else:
    st.warning("⏳ 正在等待雲端大數據對撞注入中...")
    st.stop()

st.markdown("---") 

# ==================== 4. 戰術功能分頁 ===================
tab1, tab2, tab3 = st.tabs(["🔥 雙線交錯打法 (升級)", "📊 開獎數據軌跡", "📊 數據效益分析"])

# 核心交錯邏輯運算
current_issue_int = int(current_issue_str)
base_10 = (current_issue_int // 10) * 10
age = current_issue_int % 10  # 當前這組球走到第幾期 (0-9)

def generate_10_stars(target_base_issue):
    df_past = df[df['issue'].astype(int) <= target_base_issue]
    if len(df_past) >= 24:
        past_balls = [n for sub in df_past.head(24)['numbers'] for n in sub]
        counts = Counter(past_balls)
        return sorted([item[0] for item in counts.most_common(10)])
    return []

current_10_stars = generate_10_stars(base_10)
prev_10_stars = generate_10_stars(base_10 - 10)
next_10_stars = generate_10_stars(base_10 + 10)

# -------------------- 分頁一：雙線交錯打法 --------------------
with tab1:
    st.subheader("⚔️ 雙線交錯重疊戰術盤")
    st.markdown("第一組數據維持 10 期。**每逢第 8、9 期，第二組伏擊數據會提早現身**；第 10 期結束後，第一組下退至歷史區。")
    st.info(f"當前此組已執行： **{age + 1} / 10 期**")

    st.markdown(f"### 🛡️ 第一組：主力鎖定大盤 <small style='color:#FF4B4B;'>[適用期別：{base_10} ➔ {base_10+9} 期]</small>", unsafe_allow_html=True)
    if current_10_stars:
        cols_10 = st.columns(10)
        for idx, num in enumerate(current_10_stars):
            cols_10[idx].markdown(f"<div style='text-align:center; background-color:#E65100; color:white; border-radius:5px; padding: 10px; font-weight:bold; font-size:20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{num}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if age >= 7:
        st.markdown(f"### ⚡ 第二組：次世代伏擊大盤 <small style='color:#01579B;'>[偵測到第 8 期！提早現身伏擊下個週期]</small>", unsafe_allow_html=True)
        cols_next = st.columns(10)
        for idx, num in enumerate(next_10_stars):
            cols_next[idx].markdown(f"<div style='text-align:center; background-color:#01579B; color:white; border-radius:5px; padding: 10px; font-weight:bold; font-size:20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{num}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"### 🔘 歷史觀測下退組 <small style='color:#888888;'>[歷史期別：{base_10-10} ➔ {base_10-1} 期]</small>", unsafe_allow_html=True)
    if prev_10_stars:
        cols_prev = st.columns(10)
        for idx, num in enumerate(prev_10_stars):
            cols_prev[idx].markdown(f"<div style='text-align:center; background-color:#555555; color:#BBBBBB; border-radius:5px; padding: 10px; font-weight:bold; font-size:20px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);'>{num}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 當前 24 期 1~80 號精細 8 分區熱度偏態圖")
    if len(df) >= 24:
        balls_24 = [n for sub in df.head(24)['numbers'] for n in sub]
        intervals_8 = {"01-10 一區": 0, "11-20 二區": 0, "21-30 三區": 0, "31-40 四區": 0, "41-50 五區": 0, "51-60 六區": 0, "61-70 七區": 0, "71-80 八區": 0}
        for b in balls_24:
            if 1 <= b <= 10: intervals_8["01-10 一區"] += 1
            elif 11 <= b <= 20: intervals_8["11-20 二區"] += 1
            elif 21 <= b <= 30: intervals_8["21-30 三區"] += 1
            elif 31 <= b <= 40: intervals_8["31-40 四區"] += 1
            elif 41 <= b <= 50: intervals_8["41-50 五區"] += 1
            elif 51 <= b <= 60: intervals_8["51-60 六區"] += 1
            elif 61 <= b <= 70: intervals_8["61-70 七區"] += 1
            elif 71 <= b <= 80: intervals_8["71-80 八區"] += 1
        st.bar_chart(pd.Series(intervals_8))

# -------------------- 分頁二：開獎數據軌跡 --------------------
with tab2:
    st.subheader("📊 近 50 期大數據開獎軌跡")
    df_display = df[['issue', 'numbers']].copy()
    df_display.columns = ['開獎期別', '20顆開獎球號組合']
    st.dataframe(df_display, use_container_width=True, height=400)

# -------------------- 分頁三：數據效益分析 --------------------
with tab3:
    st.subheader("📊 數據效益分析與精準自動兌獎")
    
    left_side, right_side = st.columns([3, 2])
    with left_side:
        st.markdown(f"#### 📡 當前核心推薦 vs 實時開獎")
        st.write(f"**當前核心推薦 (10星)：** `{current_10_stars}`")
        st.write(f"**最新實時開獎 (20星)：** `{live_balls}`")
        hit_current = sorted(list(set(current_10_stars) & set(live_balls)))
        st.success(f"🎯 本期即時精準命中 **{len(hit_current)}** 顆球！ 命中號碼：`{hit_current}`")

    with right_side:
        st.markdown("#### ⏳ 雙線交錯計數器")
        st.progress((age + 1) / 10)
        c_metric1, c_metric2 = st.columns(2)
        c_metric1.metric(label="🔥 第一組生命進度", value=f"{age + 1} / 10 期", delta="滿10期後下退")
        if age >= 7:
            c_metric2.metric(label="⚡ 第二組伏擊狀態", value="已現身", delta="提早兩期曝光", delta_color="normal")
        else:
            c_metric2.metric(label="⚡ 第二組伏擊狀態", value="潛伏中", delta="第8期準時解鎖", delta_color="inverse")

    # 💡 重新補回歷史推薦球號對獎表格
    st.markdown("---")
    st.subheader("🔘 歷史推薦球號數據與自動兌獎看板")
    
    history_records = []
    all_issues_sorted = sorted(df['issue'].astype(int).unique(), reverse=True)
    
    checked_bases = []
    for iss in all_issues_sorted:
        base = (iss // 10) * 10
        if base < base_10 and base not in checked_bases:
            checked_bases.append(base)
            if len(checked_bases) >= 6:  # 展示過去 6 大週期的對獎成果
                break
                
    for paste_base in checked_bases:
        rec_10_stars = generate_10_stars(paste_base)
        if not rec_10_stars:
            continue
            
        # 抓出這個 10 期大週期的所有實際開獎號碼
        df_period = df[(df['issue'].astype(int) >= paste_base) & (df['issue'].astype(int) < paste_base + 10)]
        
        period_hits = []
        for _, row in df_period.iterrows():
            actual_balls = row['numbers']
            hit_count = len(set(rec_10_stars) & set(actual_balls))
            period_hits.append(hit_count)
            
        if period_hits:
            max_hit = max(period_hits)
            avg_hit = sum(period_hits) / len(period_hits)
            history_records.append({
                "歷史週期區間": f"{paste_base} ~ {paste_base+9} 期",
                "歷史推薦 10 星號碼": str(rec_10_stars),
                "🔥 單期最高命中": f"{max_hit} 顆球",
                "📊 週期平均命中": f"{avg_hit:.1f} 顆"
            })
            
    if history_records:
        st.dataframe(pd.DataFrame(history_records), use_container_width=True)
    else:
        st.info("📊 雲端大數據正在動態生成歷史對獎報表，請稍候...")

    # 勝率百分比區塊
    st.markdown("---")
    st.markdown("### 📈 本套演算法歷史實測精準勝率分布 (中五～中十趴數統計)")
    
    total_games = 0
    hit_counts_distribution = {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
    
    for i in range(len(df) - 24):
        test_issue = int(df.iloc[i]['issue'])
        actual_balls = df.iloc[i]['numbers']
        t_base = (test_issue // 10) * 10
        sim_10_stars = generate_10_stars(t_base)
        
        if sim_10_stars:
            total_games += 1
            hits = len(set(sim_10_stars) & set(actual_balls))
            for k in hit_counts_distribution.keys():
                if hits >= k:
                    hit_counts_distribution[k] += 1
                    
    if total_games > 0:
        win_cols = st.columns(6)
        for idx, k in enumerate(sorted(hit_counts_distribution.keys())):
            percentage = (hit_counts_distribution[k] / total_games) * 100
            win_cols[idx].metric(
                label=f"🎯 中 {k} 顆勝率", 
                value=f"{percentage:.1f} %", 
                delta=f"共 {hit_counts_distribution[k]} 期"
            )