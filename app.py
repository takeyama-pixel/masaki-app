from datetime import datetime
import os
import cv2
import numpy as np
from PIL import Image
import streamlit as st

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("整体院 ビフォーアフター管理アプリ (頭部歪み分析対応)")
st.write("マサキ医院長向け / 開発：石川副委員長")

st.sidebar.header("患者管理")
menu = st.sidebar.selectbox(
    "メニュー選択", ["施術記録の閲覧・登録", "新規患者の登録"]
)

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
  st.subheader("ビフォーアフター & 歪み分析記録")

  selected_patient = st.selectbox(
      "患者を選択してください", st.session_state["patients"]
  )

  with st.form("record_form"):
    st.write(f"**対象患者:** {selected_patient}")
    visit_date = st.date_input("施術日", datetime.today())

    body_part = st.selectbox(
        "撮影部位",
        ["骨盤矯正", "腰椎", "肩・首", "全身・正面", "頭部・上面（歪み分析）"],
    )

    st.markdown("---")
    st.write("📸 **[頭部・上面分析] 自動中心検出モード稼働中**")
    st.caption("スマホで頭部が中央に来るように撮影してください。")

    col1, col2 = st.columns(2)
    with col1:
      before_file = st.file_uploader(
          "施術前（Before）の写真", type=["jpg", "png", "jpeg"]
      )
    with col2:
      after_file = st.file_uploader(
          "施術後（After）の写真", type=["jpg", "png", "jpeg"]
      )

    comment = st.text_area(
        "施術者のメモ・変化の感想",
        "例：頭蓋骨上面の左右非対称性が軽減し、バランスが整った。",
    )

    submitted = st.form_submit_button("この内容で保存・登録")

  if submitted:
    b_path, a_path = "", ""
    analysis_result = {}
    analyzed_image_path = ""

    if before_file:
      b_path = os.path.join(
          UPLOAD_DIR, f"before_{selected_patient}_{visit_date}.jpg"
      )
      with open(b_path, "wb") as f:
        f.write(before_file.getbuffer())

      if body_part == "頭部・上面（歪み分析）":
        try:
          image_pil = Image.open(b_path).convert("RGB")
          img_np = np.array(image_pil)
          h, w, _ = img_np.shape

          gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
          _, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)
          contours, _ = cv2.findContours(
              thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
          )

          if contours:
            img_center_x, img_center_y = w / 2, h / 2
            best_c = None
            min_score = float("inf")

            # 💡 魔法の改良：単に大きいだけでなく、「画像の中央付近に位置している輪郭」を頭部として採用する
            for c in contours:
              if cv2.contourArea(c) > (w * h * 0.05):  -  # ある程度の大きさがあるもの
                M = cv2.moments(c)
                if M["m00"] > 0:
                  cx = M["m10"] / M["m00"]
                  cy = M["m01"] / M["m00"]
                  # 画像中心からの距離をスコアにする（近いほど優秀）
                  distance_from_center = (cx - img_center_x) ** 2 + (
                      cy - img_center_y
                  ) ** 2
                  if distance_from_center < min_score:
                    min_score = distance_from_center
                    best_c = c

            if best_c is not None and len(best_c) >= 5:
              ellipse = cv2.fitEllipse(best_c)

              analyzed_img = img_np.copy()
              cv2.ellipse(analyzed_img, ellipse, (0, 255, 0), 3)

              center = (int(ellipse[0][0]), int(ellipse[0][1]))
              cv2.line(
                  analyzed_img,
                  (center[0], 0),
                  (center[0], analyzed_img.shape[0]),
                  (255, 0, 0),
                  2,
              )
              cv2.line(
                  analyzed_img,
                  (0, center[1]),
                  (analyzed_img.shape[1], center[1]),
                  (255, 0, 0),
                  2,
              )

              analyzed_image_path = os.path.join(
                  UPLOAD_DIR, f"analyzed_{selected_patient}_{visit_date}.jpg"
              )
              Image.fromarray(analyzed_img).save(analyzed_image_path)

              axes_ratio = (
                  min(ellipse[1]) / max(ellipse[1])
                  if max(ellipse[1]) > 0
                  else 1.0
              )
              asymmetry_score = round((1.0 - axes_ratio) * 100, 1)
              analysis_result["asymmetry_score"] = asymmetry_score
              analysis_result["analyzed_image"] = analyzed_image_path
        except Exception as e:
          analysis_result["error"] = str(e)

    if after_file:
      a_path = os.path.join(
          UPLOAD_DIR, f"after_{selected_patient}_{visit_date}.jpg"
      )
      with open(a_path, "wb") as f:
        f.write(after_file.getbuffer())

    st.session_state["records"].append({
        "patient": selected_patient,
        "date": visit_date,
        "part": body_part,
        "before": b_path,
        "after": a_path,
        "comment": comment,
        "analysis": analysis_result,
    })
    st.success("施術データおよび分析結果を保存しました！")

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
          f"**施術日:** {rec['date']} ／ **部位:** {rec['part']}"
      )

      if "analysis" in rec and rec["analysis"]:
        if "asymmetry_score" in rec["analysis"]:
          st.metric(
              label="頭部 上面歪み指数 (中心自動検出)",
              value=f"{rec['analysis']['asymmetry_score']} %",
          )

      c1, c2 = st.columns(2)
      with c1:
        st.text("【Before（中心自動検出・分析線入り）】")
        target_img = (
            rec["analysis"].get("analyzed_image")
            if (rec.get("analysis") and "analyzed_image" in rec["analysis"])
            else rec["before"]
        )
        if target_img and os.path.exists(target_img):
          st.image(target_img, use_column_width=True)
        else:
          st.write("画像なし")

      with c2:
        st.text("【After】")
        if rec["after"] and os.path.exists(rec["after"]):
          st.image(rec["after"], use_column_width=True)
        else:
          st.write("画像なし")

      st.info(f"**メモ:** {rec['comment']}")
      st.markdown("---")
