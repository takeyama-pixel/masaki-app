import streamlit as st
from datetime import datetime
import os

# データの保存先フォルダ
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("整体院 ビフォーアフター管理アプリ (初回デモ版)")
st.write("マサキ医院長向け / 開発：石川副委員長")

# サイドメニュー：患者選択・登録
st.sidebar.header("患者管理")
menu = st.sidebar.selectbox("メニュー選択", ["施術記録の閲覧・登録", "新規患者の登録"])

# 仮の患者データ（本来はDBやファイルで管理）
if "patients" not in st.session_state:
    st.session_state["patients"] = ["山田 太郎", "佐藤 花子", "鈴木 一郎"]

if "records" not in st.session_state:
    st.session_state["records"] = []

if menu == "新規患者の登録":
    st.subheader("新規患者の登録")
    new_patient = st.text_input("患者氏名")
    if st.button("登録する"):
        if new_patient:
            st.session_state["patients"].append(new_patient)
            st.success(f"患者「{new_patient}」を登録しました！")
        else:
            st.warning("氏名を入力してください。")

elif menu == "施術記録の閲覧・登録":
    st.subheader("ビフォーアフター記録")
    
    # 患者選択
    selected_patient = st.selectbox("患者を選択してください", st.session_state["patients"])
    
    with st.form("record_form"):
        st.write(f"**対象患者:** {selected_patient}")
        visit_date = st.date_input("施術日", datetime.today())
        body_part = st.selectbox("撮影部位", ["骨盤矯正", "腰椎", "肩・首", "全身・正面"])
        
        col1, col2 = st.columns(2)
        with col1:
            before_file = st.file_uploader("施術前（Before）の写真", type=["jpg", "png", "jpeg"])
        with col2:
            after_file = st.file_uploader("施術後（After）の写真", type=["jpg", "png", "jpeg"])
            
        comment = st.text_area("施術者のメモ・変化の感想", "例：骨盤の高さが揃い、前屈時の痛みが軽減した。")
        
        submitted = st.form_submit_button("この内容で保存・登録")
        
        if submitted:
            # 画像の保存処理（簡易版）
            b_path, a_path = "", ""
            if before_file:
                b_path = os.path.join(UPLOAD_DIR, f"before_{selected_patient}_{visit_date}.jpg")
                with open(b_path, "wb") as f:
                    f.write(before_file.getbuffer())
            if after_file:
                a_path = os.path.join(UPLOAD_DIR, f"after_{selected_patient}_{visit_date}.jpg")
                with open(a_path, "wb") as f:
                    f.write(after_file.getbuffer())
            
            st.session_state["records"].append({
                "patient": selected_patient,
                "date": visit_date,
                "part": body_part,
                "before": b_path,
                "after": a_path,
                "comment": comment
            })
            st.success("施術データを保存しました！")

    # 過去の記録・比較表示エリア
    st.markdown("---")
    st.subheader(f"📊 {selected_patient} 様の過去の比較履歴")
    
    # 該当患者の記録をフィルタリング
    patient_records = [r for r in st.session_state["records"] if r["patient"] == selected_patient]
    
    if not patient_records:
        st.info("まだ施術記録がありません。上のフォームから登録してみましょう。")
    else:
        for rec in patient_records:
            st.markdown(f"**施術日:** {rec['date']} ／ **部位:** {rec['part']}")
            c1, c2 = st.columns(2)
            with c1:
                st.text("【Before】")
                if rec["before"]:
                    st.image(rec["before"], use_column_width=True)
                else:
                    st.write("画像なし")
            with c2:
                st.text("【After】")
                if rec["after"]:
                    st.image(rec["after"], use_column_width=True)
                else:
                    st.write("画像なし")
            st.info(f"**メモ:** {rec['comment']}")
            st.markdown("---")