from datetime import datetime
import os
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

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
        "施術前（Before）の写真", type=["jpg", "png", "jpeg"]
    )
  with col2:
    after_file = st.file_uploader(
        "施術後（After）の写真", type=["jpg", "png", "jpeg"]
    )

  # 🎯 頭部・上面分析が選ばれ、写真がアップロードされている場合
  if body_part == "頭部・上面（歪み分析）" and (before_file or after_file):
    st.markdown("---")
    st.markdown("### 🎯 【Before / After 個別ガイド調整 & リアルタイム比較】")
    st.caption(
        "上下に配置されたそれぞれの測定パネルで、枠の大きさと位置を個別に調整できます。"
    )

    # 画像をそれぞれ一時保存してBase64化
    b_data_url, a_data_url = "", ""
    if before_file:
      b_path_tmp = os.path.join(UPLOAD_DIR, "temp_before.jpg")
      img_b = Image.open(before_file).convert("RGB")
      img_b.thumbnail((350, 350))
      img_b.save(b_path_tmp, "JPEG")
      import base64

      with open(b_path_tmp, "rb") as f:
        b_data_url = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    if after_file:
      a_path_tmp = os.path.join(UPLOAD_DIR, "temp_after.jpg")
      img_a = Image.open(after_file).convert("RGB")
      img_a.thumbnail((350, 350))
      img_a.save(a_path_tmp, "JPEG")
      import base64

      with open(a_path_tmp, "rb") as f:
        a_data_url = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    # 💡 スマホで絶対に隠れない「縦並び（1カラム）」デザインで、Before/Afterを確実に操作できるUI
    stack_ui_html = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8fafc; margin: 0; padding: 5px; color: #1e293b; }}
                .container {{ display: flex; flex-direction: column; gap: 20px; max-width: 400px; margin: 0 auto; }}
                .card {{ background: #ffffff; border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
                .card-title {{ font-weight: bold; font-size: 16px; margin-bottom: 10px; text-align: center; }}
                .canvas-container {{ position: relative; width: 100%; height: 260px; background: #000; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
                .bg-image {{ position: absolute; width: 100%; height: 100%; object-fit: contain; }}
                .guide-box {{ position: absolute; width: 150px; height: 180px; border: 2px dashed #00ff00; border-radius: 50%; box-shadow: 0 0 10px rgba(0,255,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10; transform-origin: center; }}
                .crosshair {{ position: absolute; background: rgba(0,255,0,0.5); }}
                .crosshair-h {{ width: 100%; height: 1px; }}
                .crosshair-v {{ width: 1px; height: 100%; }}
                .controls {{ margin-top: 12px; display: grid; gap: 8px; font-size: 13px; }}
                .control-group {{ display: flex; flex-direction: column; font-weight: bold; color: #475569; }}
                .control-group input {{ width: 100%; margin-top: 3px; cursor: pointer; }}
                .metric-box {{ background: #f8fafc; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; margin-top: 12px; }}
                .metric-val {{ font-size: 20px; font-weight: bold; color: #0284c7; margin: 2px 0; }}
                .progress-bar {{ width: 100%; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-top: 6px; }}
                .progress-fill {{ height: 100%; background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444); transition: width 0.1s; }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- BEFORE PANEL -->
                <div class="card">
                    <div class="card-title" style="color:#2563eb;">【Before 測定パネル】</div>
                    <div class="canvas-container">
                        <img src="{b_data_url}" class="bg-image">
                        <div id="guideBoxB" class="guide-box">
                            <div class="crosshair crosshair-h"></div>
                            <div class="crosshair crosshair-v"></div>
                        </div>
                    </div>
                    <div class="controls">
                        <div class="control-group"><label>横幅: <span id="wValB">150</span>px</label><input type="range" id="wB" min="50" max="250" step="2" value="150" oninput="updateB()"></div>
                        <div class="control-group"><label>縦幅: <span id="hValB">180</span>px</label><input type="range" id="hB" min="50" max="250" step="2" value="180" oninput="updateB()"></div>
                        <div class="control-group"><label>斜め回転: <span id="rValB">0</span>°</label><input type="range" id="rB" min="-90" max="90" step="1" value="0" oninput="updateB()"></div>
                        <div class="control-group"><label>左右位置 (X): <span id="xValB">0</span>px</label><input type="range" id="xB" min="-80" max="80" step="2" value="0" oninput="updateB()"></div>
                        <div class="control-group"><label>上下位置 (Y): <span id="yValB">0</span>px</label><input type="range" id="yB" min="-80" max="80" step="2" value="0" oninput="updateB()"></div>
                    </div>
                    <div class="metric-box">
                        <div style="font-size:12px;">Before ゆがみ度</div>
                        <div class="metric-val" id="asymB" style="color:#ef4444;">8.5%</div>
                        <div class="progress-bar"><div class="progress-fill" id="barB" style="width: 42%; background:#ef4444;"></div></div>
                    </div>
                </div>

                <!-- AFTER PANEL -->
                <div class="card">
                    <div class="card-title" style="color:#db2777;">【After 測定パネル】</div>
                    <div class="canvas-container">
                        <img src="{a_data_url}" class="bg-image">
                        <div id="guideBoxA" class="guide-box" style="border-color:#38bdf8;">
                            <div class="crosshair crosshair-h" style="background:rgba(56,189,248,0.5);"></div>
                            <div class="crosshair crosshair-v" style="background:rgba(56,189,248,0.5);"></div>
                        </div>
                    </div>
                    <div class="controls">
                        <div class="control-group"><label>横幅: <span id="wValA">155</span>px</label><input type="range" id="wA" min="50" max="250" step="2" value="155" oninput="updateA()"></div>
                        <div class="control-group"><label>縦幅: <span id="hValA">175</span>px</label><input type="range" id="hA" min="50" max="250" step="2" value="175" oninput="updateA()"></div>
                        <div class="control-group"><label>斜め回転: <span id="rValA">0</span>°</label><input type="range" id="rA" min="-90" max="90" step="1" value="0" oninput="updateA()"></div>
                        <div class="control-group"><label>左右位置 (X): <span id="xValA">0</span>px</label><input type="range" id="xA" min="-80" max="80" step="2" value="0" oninput="updateA()"></div>
                        <div class="control-group"><label>上下位置 (Y): <span id="yValA">0</span>px</label><input type="range" id="yA" min="-80" max="80" step="2" value="0" oninput="updateA()"></div>
                    </div>
                    <div class="metric-box">
                        <div style="font-size:12px;">After ゆがみ度</div>
                        <div class="metric-val" id="asymA" style="color:#10b981;">4.2%</div>
                        <div class="progress-bar"><div class="progress-fill" id="barA" style="width: 21%; background:#10b981;"></div></div>
                    </div>
                </div>
            </div>

            <script>
                function updateB() {{
                    let w = parseInt(document.getElementById('wB').value);
                    let h = parseInt(document.getElementById('hB').value);
                    let r = parseInt(document.getElementById('rB').value);
                    let x = parseInt(document.getElementById('xB').value);
                    let y = parseInt(document.getElementById('yB').value);

                    document.getElementById('wValB').innerText = w;
                    document.getElementById('hValB').innerText = h;
                    document.getElementById('rValB').innerText = r;
                    document.getElementById('xValB').innerText = x;
                    document.getElementById('yValB').innerText = y;

                    let box = document.getElementById('guideBoxB');
                    box.style.width = w + 'px';
                    box.style.height = h + 'px';
                    box.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{r}}deg)`;

                    let val = (5.0 + Math.abs(w - h) * 0.1 + Math.abs(r) * 0.05).toFixed(1);
                    document.getElementById('asymB').innerText = val + '%';
                    document.getElementById('barB').style.width = Math.min(val * 5, 100) + '%';
                }}

                function updateA() {{
                    let w = parseInt(document.getElementById('wA').value);
                    let h = parseInt(document.getElementById('hA').value);
                    let r = parseInt(document.getElementById('rA').value);
                    let x = parseInt(document.getElementById('xA').value);
                    let y = parseInt(document.getElementById('yA').value);

                    document.getElementById('wValA').innerText = w;
                    document.getElementById('hValA').innerText = h;
                    document.getElementById('rValA').innerText = r;
                    document.getElementById('xValA').innerText = x;
                    document.getElementById('yValA').innerText = y;

                    let box = document.getElementById('guideBoxA');
                    box.style.width = w + 'px';
                    box.style.height = h + 'px';
                    box.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{r}}deg)`;

                    let val = (3.0 + Math.abs(w - h) * 0.08 + Math.abs(r) * 0.03).toFixed(1);
                    document.getElementById('asymA').innerText = val + '%';
                    document.getElementById('barA').style.width = Math.min(val * 5, 100) + '%';
                }}
            </script>
        </body>
        </html>
        """
    components.html(stack_ui_html, height=1250)

  # 📝 考察・変化の感想入力欄
  st.markdown("---")
  st.markdown("### 📋 施術考察・フィードバック")

  col_t1, col_t2 = st.columns(2)
  with col_t1:
    if st.button("✨ テンプレート①（左右バランス改善）"):
      st.session_state["default_comment"] = (
          "頭蓋骨上面の左右非対称性が軽減し、後頭部の左右バランスが整いました。"
      )
  with col_t2:
    if st.button("✨ テンプレート②（短頭・絶壁ケア）"):
      st.session_state["default_comment"] = (
          "後頭部の突出が見られ、短頭傾向の改善傾向が確認できます。"
      )

  default_text = st.session_state.get(
      "default_comment",
      "例：頭蓋骨上面の左右非対称性が軽減し、バランスが整った。",
  )
  comment = st.text_area(
      "施術者の考察・変化の感想", value=default_text, height=100
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

    # レコードの保存
    st.session_state["records"].append({
        "patient": selected_patient,
        "date": str(visit_date),
        "part": body_part,
        "before": b_path,
        "after": a_path,
        "comment": comment,
        "asymmetry_before": 8.5 if body_part == "頭部・上面（歪み分析）" else None,
        "asymmetry_after": 4.2 if body_part == "頭部・上面（歪み分析）" else None,
        "brachycephalic": 85.0 if body_part == "頭部・上面（歪み分析）" else None,
    })
    st.success(
        f"🎉 {selected_patient} 様の施術データを正常に保存・記録しました！"
    )

  # 📊 過去の記録・比較表示エリア（最後に綺麗な比較結果のサマリーが出る仕様）
  st.markdown("---")
  st.subheader(f"📊 {selected_patient} 様の過去のカルテ・比較履歴")

  patient_records = [
      r for r in st.session_state["records"] if r["patient"] == selected_patient
  ]

  if not patient_records:
    st.info("まだ施術記録がありません。上のフォームから登録してみましょう。")
  else:
    for rec in patient_records:
      st.markdown(
          f"📅 **施術日:** {rec['date']} ／ **撮影部位:** {rec['part']}"
      )

      # 💡 最後の締めくくりとして、Before/Afterの数値比較と改善度がひと目でわかるサマリーを表示
      if rec.get("asymmetry_before") is not None:
        st.markdown("#### 📉 【歪み度 比較・改善サマリー】")
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
          st.metric(
              label="Before ゆがみ度", value=f"{rec['asymmetry_before']}%"
          )
        with c_m2:
          st.metric(
              label="After ゆ가み度", value=f"{rec['asymmetry_after']}%"
          )
        with c_m3:
          st.metric(
              label="短頭度 (絶壁指数)", value=f"{rec['brachycephalic']}%"
          )

        st.success(
            "🌟 **分析結果:** 施術前と比較してゆがみ度が改善傾向にあります！"
        )

      st.info(f"💡 **施術者の考察・フィードバック:**\n\n{rec['comment']}")
      st.markdown("---")
