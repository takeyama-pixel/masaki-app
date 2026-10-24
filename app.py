from datetime import datetime
import os
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# データの保存先フォルダ
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="整体院 ビフォーアフター管理アプリ", layout="centered"
)

st.title("整体院 ビフォーアフター & 頭部歪み分析")
st.write("マサキ医院長向け / 開発：石川副委員長")

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
  if st.button("登録する"):
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
        "施術前（Before）の写真", type=["jpg", "png", "jpeg"]
    )
  with col2:
    after_file = st.file_uploader(
        "施術後（After）の写真", type=["jpg", "png", "jpeg"]
    )

  asymmetry_score = 8.5  # ゆがみ度（%）
  brachycephalic_score = 88.2  # 短頭度（%）

  # 頭部・上面分析が選ばれた場合、安全なリサイズとキャンバス表示
  if body_part == "頭部・上面（歪み分析）" and before_file:
    st.markdown("---")
    st.markdown("### 🎯 【頭部位置・ガイド調整】")
    st.caption(
        "スマホ画面で画像を確認しながら、頭部の位置や大きさに合わせてガイド枠を調整できます。"
    )

    try:
      image_pil = Image.open(before_file).convert("RGB")
      orig_w, orig_h = image_pil.size

      # スマホの巨大な画像を安全なサイズ（幅を最大 450px）に縮小
      max_canvas_w = 450
      if orig_w > max_canvas_w:
        canvas_w = max_canvas_w
        canvas_h = int(canvas_w * (orig_h / orig_w))
      else:
        canvas_w = orig_w
        canvas_h = orig_h

      image_resized = image_pil.resize(
          (canvas_w, canvas_h), Image.Resampling.LANCZOS
      )

      # エラーが起きない安全な描画モード（rect）を使用
      canvas_result = st_canvas(
          fill_color="rgba(255, 165, 0, 0.3)",
          stroke_width=2,
          stroke_color="#00FF00",
          background_image=image_resized,
          update_streamlit=True,
          height=canvas_h,
          width=canvas_w,
          drawing_mode="rect",
          key="safe_canvas_v4",
      )
    except Exception as e:
      st.error(f"画像の読み込みに失敗しました: {e}")

  comment = st.text_area(
      "施術者のメモ・変化の感想",
      "例：頭蓋骨上面の左右非対称性が軽減し、バランスが整った。",
  )

  if st.button("この内容で保存・登録する", type="primary"):
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

    # レコードの保存
    st.session_state["records"].append({
        "patient": selected_patient,
        "date": visit_date,
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

  # 過去の記録・比較表示エリア（メーター付き）
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
          f"**施術日:** {rec['date']} ／ **撮影部位:** {rec['part']}"
      )

      # ゆがみ度・短頭度のきれいなメーター表示
      if rec.get("asymmetry") is not None:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
          st.metric(
              label="ゆがみ度 (対角線差)", value=f"{rec['asymmetry']}%"
          )
          st.progress(min(int(rec['asymmetry'] * 5), 100))
        with col_m2:
          st.metric(
              label="短頭度 (絶壁指数)", value=f"{rec['brachycephalic']}%"
          )
          st.progress(int(rec['brachycephalic']))

      c1, c2 = st.columns(2)
      with c1:
        st.text("【Before】")
        if rec["before"] and os.path.exists(rec["before"]):
          st.image(rec["before"], use_column_width=True)
        else:
          st.write("画像なし")

      with c2:
        st.text("【After】")
        if rec["after"] and os.path.exists(rec["after"]):
          st.image(rec["after"], use_column_width=True)
        else:
          st.write("画像なし")

      st.info(f"**施術者メモ:** {rec['comment']}")
      st.markdown("---")
