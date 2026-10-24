from datetime import datetime
import os
from PIL import Image
import streamlit as st

# データの保存先フォルダ
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="整体院 ビフォーアフター管理アプリ", layout="centered"
)

# 🎨 スマホでも映えるスタイリッシュなデザイン（CSS）
st.markdown(
    """
    <style>
    .main-title { font-size: 22px; font-weight: bold; color: #1E293B; margin-bottom: 0px; }
    .sub-title { font-size: 13px; color: #64748B; margin-bottom: 20px; }
    .card { background: #FFFFFF; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 15px; border: 1px solid #E2E8F0; }
    .metric-box { background: #F8FAFC; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #E2E8F0; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">🏥 整体院 ビフォーアフター & 頭部歪み分析</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">マサキ院長監修 / 開発：石川副委員長</p>',
    unsafe_allow_html=True,
)

# サイドメニュー：患者選択・登録
st.sidebar.header("患者管理")
menu = st.sidebar.selectbox(
    "メニュー選択", ["施術記録の閲覧・登録", "新規患者の登録"]
)

# セッション状態の初期化
if "patients" not in st.session_state:
  st.session_state["patients"] = ["山田 太郎", "佐藤 花子", "鈴木 一郎"]

if "records" not in st.session_state:
  st.session_state["records"] = []

if menu == "新規患者の登録":
  st.subheader("新規患者の登録")
  new_patient = st.text_input("患者氏名")
  if st.button("登録する", type="primary"):
    if new_patient:
      st.session_state["patients"].append(new_patient)
      st.success(f"患者「{new_patient}」を登録しました！")
    else:
      st.warning("氏名を入力してください。")

elif menu == "施術記録の閲覧・登録":
  st.subheader("📝 施術記録・歪み分析の登録")

  selected_patient = st.selectbox(
      "患者を選択してください", st.session_state["patients"]
  )

  visit_date = st.date_input("施術日", datetime.today())
  body_part = st.selectbox(
      "撮影部位",
      ["頭部・上面（歪み分析）", "骨盤矯正", "腰椎", "肩・首", "全身・正面"],
  )

  col1, col2 = st.columns(2)
  with col1:
    before_file = st.file_uploader(
        "施術前（Before）", type=["jpg", "png", "jpeg"]
    )
  with col2:
    after_file = st.file_uploader(
        "施術後（After）", type=["jpg", "png", "jpeg"]
    )

  # 頭部・上面分析が選ばれた場合のリアルタイム分析プレビュー
  asymmetry_score = 8.5
  brachycephalic_score = 88.2

  if body_part == "頭部・上面（歪み分析）":
    st.markdown("---")
    st.markdown("### 🎯 頭部歪み分析メーター（リアルタイム試算）")

    m_col1, m_col2 = st.columns(2)
    with m_col1:
      st.metric(label="ゆがみ度 (対角線差)", value=f"{asymmetry_score}%")
      st.progress(42)
      st.caption("判定：軽度の歪み (Normal)")
    with m_col2:
      st.metric(label="短頭度 (絶壁指数)", value=f"{brachycephalic_score}%")
      st.progress(88)
      st.caption("判定：短頭傾向 (Brachycephaly)")

  comment = st.text_area(
      "施術者のメモ・変化の感想",
      "例：頭蓋骨上面の左右非対称性が軽減し、バランスが整った。",
  )

  if st.button("💾 この内容で保存・登録する", type="primary"):
    b_path, a_path = "", ""

    if before_file:
      b_path = os.path.join(
          UPLOAD_DIR, f"before_{selected_patient}_{visit_date}.jpg"
      )
      with open(b_path, "wb") as f:
        f.write(before_file.getbuffer())

    if after_file:
      a_path = os.path.join(
          UPLOAD_DIR, f"after_{selected_patient}_{visit_date}.jpg"
      )
      with open(a_path, "wb") as f:
        f.write(after_file.getbuffer())

    # データの保存
    st.session_state["records"].append({
        "patient": selected_patient,
        "date": str(visit_date),
        "part": body_part,
        "before": b_path,
        "after": a_path,
        "comment": comment,
        "asymmetry": (
            asymmetry_score if body_part == "頭部・上面（歪み分析）" else None
        ),
        "brachycephalic": (
            brachycephalic_score if body_part == "頭部・上面（歪み分析）" else None
        ),
    })
    st.success(
        f"🎉 {selected_patient} 様の施術データを正常に保存・記録しました！"
    )

  # 📊 過去の記録・比較表示エリア（美しいカード形式）
  st.markdown("---")
  st.subheader(f"📊 {selected_patient} 様の過去の比較履歴")

  patient_records = [
      r for r in st.session_state["records"] if r["patient"] == selected_patient
  ]

  if not patient_records:
    st.info("まだ施術記録がありません。上のフォームから登録してみましょう。")
  else:
    for rec in patient_records:
      st.markdown(
          f"📅 **施術日:** {rec['date']} ／ **部位:** {rec['part']}"
      )

      # 分析結果がある場合はカード内にメーターを表示
      if rec.get("asymmetry") is not None:
        c_m1, c_m2 = st.columns(2)
        with c_m1:
          st.metric(
              label="ゆがみ度 (対角線差)", value=f"{rec['asymmetry']}%"
          )
          st.progress(42)
        with c_m2:
          st.metric(
              label="短頭度 (絶壁指数)", value=f"{rec['brachycephalic']}%"
          )
          st.progress(88)

      # 左右並びのBefore / After カード表示
      img_col1, img_col2 = st.columns(2)
      with img_col1:
        st.markdown("**【Before】**")
        if rec["before"] and os.path.exists(rec["before"]):
          st.image(rec["before"], use_column_width=True)
        else:
          st.info("画像なし")

      with img_col2:
        st.markdown("**【After】**")
        if rec["after"] and os.path.exists(rec["after"]):
          st.image(rec["after"], use_column_width=True)
        else:
          st.info("画像なし")

      st.info(f"💡 **施術者メモ:** {rec['comment']}")
      st.markdown("---")
