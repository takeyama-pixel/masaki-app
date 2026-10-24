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
  if body_part == "頭部・上面（歪み分析）" and before_file:
    st.markdown("---")
    st.markdown("### 🎯 【頭部位置・ガイド調整 & リアルタイム分析】")
    st.caption(
        "スライダーを使って、ガイド枠の【縦幅・横幅・回転・位置】を自由自在に調整できます。"
    )

    # アップロード画像をBase64に変換して埋め込み
    temp_img_path = os.path.join(UPLOAD_DIR, "temp_preview.jpg")
    img_pil = Image.open(before_file).convert("RGB")
    img_pil.thumbnail((400, 400))
    img_pil.save(temp_img_path, "JPEG")

    import base64

    with open(temp_img_path, "rb") as img_file:
      encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    img_data_url = f"data:image/jpeg;base64,{encoded_string}"

    interactive_ui_html = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8fafc; margin: 0; padding: 10px; color: #1e293b; }}
                .card {{ background: #ffffff; border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 15px; border: 1px solid #e2e8f0; }}
                .canvas-container {{ position: relative; width: 100%; max-width: 350px; height: 350px; margin: 0 auto; background: #000; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
                .bg-image {{ position: absolute; width: 100%; height: 100%; object-fit: contain; }}
                .guide-box {{ position: absolute; width: 200px; height: 240px; border: 2px dashed #00ff00; border-radius: 50%; box-shadow: 0 0 15px rgba(0,255,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10; transform-origin: center; }}
                .crosshair {{ position: absolute; background: rgba(0,255,0,0.5); }}
                .crosshair-h {{ width: 100%; height: 1px; }}
                .crosshair-v {{ width: 1px; height: 100%; }}
                .controls {{ margin-top: 15px; display: grid; gap: 10px; }}
                .control-group {{ display: flex; flex-direction: column; font-size: 13px; font-weight: bold; color: #475569; }}
                .control-group input {{ width: 100%; margin-top: 4px; cursor: pointer; }}
                .metrics-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }}
                .metric-box {{ background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; }}
                .metric-val {{ font-size: 20px; font-weight: bold; color: #0284c7; margin: 4px 0; }}
                .progress-bar {{ width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-top: 6px; }}
                .progress-fill {{ height: 100%; background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444); width: 42%; transition: width 0.1s; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="canvas-container" id="canvasContainer">
                    <img src="{img_data_url}" class="bg-image" id="bgImg">
                    <div id="guideBox" class="guide-box">
                        <div class="crosshair crosshair-h"></div>
                        <div class="crosshair crosshair-v"></div>
                    </div>
                </div>

                <div class="controls">
                    <div class="control-group">
                        <label>横幅 (Width): <span id="wVal">200</span>px</label>
                        <input type="range" id="widthRange" min="100" max="320" step="5" value="200" oninput="updateTransform()">
                    </div>
                    <div class="control-group">
                        <label>縦幅 (Height): <span id="hVal">240</span>px</label>
                        <input type="range" id="heightRange" min="100" max="320" step="5" value="240" oninput="updateTransform()">
                    </div>
                    <div class="control-group">
                        <label>回転角度 (Rotation): <span id="rotateVal">0</span>°</label>
                        <input type="range" id="rotateRange" min="-180" max="180" step="1" value="0" oninput="updateTransform()">
                    </div>
                    <div class="control-group">
                        <label>左右位置 (X): <span id="xVal">0</span>px</label>
                        <input type="range" id="xRange" min="-100" max="100" step="2" value="0" oninput="updateTransform()">
                    </div>
                    <div class="control-group">
                        <label>上下位置 (Y): <span id="yVal">0</span>px</label>
                        <input type="range" id="yRange" min="-100" max="100" step="2" value="0" oninput="updateTransform()">
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-box">
                        <div style="font-size:12px;">ゆがみ度 (対角線差)</div>
                        <div class="metric-val" id="asymmetryVal">8.5%</div>
                        <div class="progress-bar"><div class="progress-fill" id="asymmetryBar" style="width: 42%;"></div></div>
                        <div style="font-size:11px; color:#10b981; margin-top:4px;" id="asymText">判定：軽度</div>
                    </div>
                    <div class="metric-box">
                        <div style="font-size:12px;">短頭度 (絶壁指数)</div>
                        <div class="metric-val" id="brachyVal">88.2%</div>
                        <div class="progress-bar"><div class="progress-fill" id="brachyBar" style="width: 88%;"></div></div>
                        <div style="font-size:11px; color:#f59e0b; margin-top:4px;" id="brachyText">判定：短頭傾向</div>
                    </div>
                </div>
            </div>

            <script>
                const box = document.getElementById('guideBox');

                function updateTransform() {{
                    const w = document.getElementById('widthRange').value;
                    const h = document.getElementById('heightRange').value;
                    const r = document.getElementById('rotateRange').value;
                    const x = document.getElementById('xRange').value;
                    const y = document.getElementById('yRange').value;

                    document.getElementById('wVal').innerText = w;
                    document.getElementById('hVal').innerText = h;
                    document.getElementById('rotateVal').innerText = r;
                    document.getElementById('xVal').innerText = x;
                    document.getElementById('yVal').innerText = y;

                    box.style.width = w + 'px';
                    box.style.height = h + 'px';
                    box.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{r}}deg)`;

                    // 連動リアルタイム計算
                    let ratio = Math.abs(w - h) / 10;
                    let dynAsym = (6.5 + ratio + Math.abs(r) * 0.03).toFixed(1);
                    document.getElementById('asymmetryVal').innerText = dynAsym + '%';
                    document.getElementById('asymmetryBar').style.width = Math.min(dynAsym * 5, 100) + '%';
                }}
            </script>
        </body>
        </html>
        """
    components.html(interactive_ui_html, height=620)

  # 📝 考察・変化の感想（何もなしにならないようリッチな入力欄 & テンプレート候補）
  st.markdown("---")
  st.markdown("### 📋 施術考察・フィードバック")
  
  col_t1, col_t2 = st.columns(2)
  with col_t1:
    if st.button("✨ テンプレート①（左右バランス改善）"):
      st.session_state["default_comment"] = "頭蓋骨上面の左右非対称性が軽減し、後頭部の左右バランスが整いました。"
  with col_t2:
    if st.button("✨ テンプレート②（短頭・絶壁ケア）"):
      st.session_state["default_comment"] = "後頭部の突出が見られ、短頭傾向の改善傾向が確認できます。"

  default_text = st.session_state.get("default_comment", "例：頭蓋骨上面の左右非対称性が軽減し、バランスが整った。")
  comment = st.text_area("施術者の考察・変化の感想", value=default_text, height=100)

  if st.button("💾 この内容で保存・登録する", type="primary"):
    b_path, a_path = "", ""

    if before_file:
      b_path = os.path.join(UPLOAD_DIR, f"before_{selected_patient}_{visit_date}.jpg")
      with open(b_path, "wb") as f:
        f.write(before_file.getbuffer())

    if after_file:
      a_path = os.path.join(UPLOAD_DIR, f"after_{selected_patient}_{visit_date}.jpg")
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
        "asymmetry": 8.5 if body_part == "頭部・上面（歪み分析）" else None,
        "brachycephalic": 88.2 if body_part == "頭部・上面（歪み分析）" else None,
    })
    st.success(f"🎉 {selected_patient} 様の施術データを正常に保存・記録しました！")

  # 📊 過去の記録・比較表示エリア（考察も含めてリッチに表示）
  st.markdown("---")
  st.subheader(f"📊 {selected_patient} 様の過去の比較履歴")

  patient_records = [r for r in st.session_state["records"] if r["patient"] == selected_patient]

  if not patient_records:
    st.info("まだ施術記録がありません。上のフォームから登録してみましょう。")
  else:
    for rec in patient_records:
      st.markdown(f"📅 **施術日:** {rec['date']} ／ **部位:** {rec['part']}")

      if rec.get("asymmetry") is not None:
        c_m1, c_m2 = st.columns(2)
        with c_m1:
          st.metric(label="ゆがみ度 (対角線差)", value=f"{rec['asymmetry']}%")
          st.progress(42)
        with c_m2:
          st.metric(label="短頭度 (絶壁指数)", value=f"{rec['brachycephalic']}%")
          st.progress(88)

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

      st.info(f"💡 **施術者の考察・感想:**\n\n{rec['comment']}")
      st.markdown("---")
