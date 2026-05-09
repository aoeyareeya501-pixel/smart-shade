"""
Color Comparison Web Application for Packaging Quality Control
- Upload 2 images (Customer CI vs Production)
- Compare colors using Delta E
- Export data to n8n webhook
"""

import streamlit as st
import requests
from PIL import Image
from datetime import datetime
import json
import pandas as pd
import numpy as np
from streamlit_image_coordinates import streamlit_image_coordinates

import color_utils as cu


# Page config
st.set_page_config(
    page_title="Color Comparison Tool",
    page_icon="🎨",
    layout="wide"
)

# Initialize session state
if 'image1' not in st.session_state:
    st.session_state.image1 = None
if 'image2' not in st.session_state:
    st.session_state.image2 = None
if 'color1' not in st.session_state:
    st.session_state.color1 = None
if 'color2' not in st.session_state:
    st.session_state.color2 = None
if 'filename1' not in st.session_state:
    st.session_state.filename1 = None
if 'filename2' not in st.session_state:
    st.session_state.filename2 = None
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = None
if 'prev_filename1' not in st.session_state:
    st.session_state.prev_filename1 = None
if 'prev_filename2' not in st.session_state:
    st.session_state.prev_filename2 = None


def create_color_swatch(rgb, size=(100, 100)):
    """Create a color swatch image"""
    img = Image.new('RGB', size, color=rgb)
    return img


def send_to_n8n(webhook_url, data):
    """Send data to n8n webhook and wait for AI analysis response"""
    try:
        response = requests.post(webhook_url, json=data, timeout=60)
        response.raise_for_status()

        # Parse response from n8n (after AI analysis)
        response_data = response.json()
        return True, "ส่งข้อมูลสำเร็จ!", response_data
    except requests.exceptions.Timeout:
        return False, "หมดเวลารอ response จาก n8n (60 วินาที)", None
    except requests.exceptions.RequestException as e:
        return False, f"เกิดข้อผิดพลาด: {str(e)}", None
    except json.JSONDecodeError:
        return False, "ไม่สามารถอ่าน response จาก n8n ได้", None


# Main UI
st.title("🎨 เครื่องมือเปรียบเทียบสี (Color Comparison Tool)")
st.markdown("สำหรับเปรียบเทียบค่าสี CI ของลูกค้ากับสีที่ผลิตได้")

st.divider()

# Sidebar settings
with st.sidebar:
    st.header("⚙️ การตั้งค่า")

    delta_method = st.selectbox(
        "วิธีคำนวณ Delta E",
        ["DE2000", "DE76"],
        help="CIEDE2000 แม่นยำกว่า แต่ DE76 คำนวณเร็วกว่า"
    )

    delta_cap = st.slider(
        "Delta E Cap",
        min_value=10.0,
        max_value=100.0,
        value=50.0,
        step=1.0,
        help="ค่า Delta E ที่ถือว่าสีต่างกันอย่างสิ้นเชิง"
    )

    sampling_method = st.radio(
        "วิธีการเลือกสี",
        ["สีเฉลี่ยของรูปทั้งหมด", "คลิกเลือกจุดบนรูป"],
        help="เลือกสีเฉลี่ยทั้งรูป หรือคลิกเลือกจุดที่ต้องการเปรียบเทียบ"
    )

    sample_size = st.slider(
        "ขนาดพื้นที่สุ่มสี (pixels)",
        min_value=1,
        max_value=20,
        value=5,
        step=2,
        help="ขนาดพื้นที่เฉลี่ยรอบจุดที่คลิก"
    )

    st.divider()

    st.subheader("🔗 n8n Webhook")
    webhook_url = st.text_input(
        "Webhook URL",
        placeholder="https://your-n8n.com/webhook/...",
        help="URL ของ n8n webhook สำหรับส่งข้อมูล"
    )

# Upload section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 รูปที่ 1: CI ของลูกค้า")
    uploaded_file1 = st.file_uploader(
        "อัพโหลดรูปภาพ CI ของลูกค้า",
        type=['png', 'jpg', 'jpeg'],
        key="upload1"
    )

    if uploaded_file1:
        # Clear AI response if file changed
        if st.session_state.prev_filename1 != uploaded_file1.name:
            st.session_state.ai_response = None
            st.session_state.prev_filename1 = uploaded_file1.name

        st.session_state.image1 = Image.open(uploaded_file1).convert('RGB')
        st.session_state.filename1 = uploaded_file1.name

        if sampling_method == "สีเฉลี่ยของรูปทั้งหมด":
            st.image(st.session_state.image1, caption="รูปภาพ CI ของลูกค้า", use_container_width=True)
            st.session_state.color1 = cu.get_dominant_color(st.session_state.image1)
        else:
            st.write("👇 คลิกบนรูปเพื่อเลือกสี")
            coords1 = streamlit_image_coordinates(
                st.session_state.image1,
                key="img1_click"
            )

            if coords1:
                x, y = coords1['x'], coords1['y']
                st.session_state.color1 = cu.get_color_at_point(
                    st.session_state.image1, x, y, sample_size
                )
                st.success(f"เลือกตำแหน่ง: ({x}, {y})")

with col2:
    st.subheader("📸 รูปที่ 2: สีที่ผลิตได้")
    uploaded_file2 = st.file_uploader(
        "อัพโหลดรูปภาพสีที่ผลิตได้",
        type=['png', 'jpg', 'jpeg'],
        key="upload2"
    )

    if uploaded_file2:
        # Clear AI response if file changed
        if st.session_state.prev_filename2 != uploaded_file2.name:
            st.session_state.ai_response = None
            st.session_state.prev_filename2 = uploaded_file2.name

        st.session_state.image2 = Image.open(uploaded_file2).convert('RGB')
        st.session_state.filename2 = uploaded_file2.name

        if sampling_method == "สีเฉลี่ยของรูปทั้งหมด":
            st.image(st.session_state.image2, caption="รูปภาพสีที่ผลิตได้", use_container_width=True)
            st.session_state.color2 = cu.get_dominant_color(st.session_state.image2)
        else:
            st.write("👇 คลิกบนรูปเพื่อเลือกสี")
            coords2 = streamlit_image_coordinates(
                st.session_state.image2,
                key="img2_click"
            )

            if coords2:
                x, y = coords2['x'], coords2['y']
                st.session_state.color2 = cu.get_color_at_point(
                    st.session_state.image2, x, y, sample_size
                )
                st.success(f"เลือกตำแหน่ง: ({x}, {y})")

st.divider()

# Color comparison section
if st.session_state.color1 and st.session_state.color2:
    st.header("📊 ผลการเปรียบเทียบสี")

    rgb1 = st.session_state.color1
    rgb2 = st.session_state.color2

    # Calculate color values
    lab1 = cu.rgb_to_lab(*rgb1)
    lab2 = cu.rgb_to_lab(*rgb2)
    lch1 = cu.rgb_to_lch(*rgb1)
    lch2 = cu.rgb_to_lch(*rgb2)

    # Calculate Delta E
    similarity, delta_e = cu.similarity_percent(
        rgb1, rgb2,
        method=delta_method,
        cap=delta_cap
    )

    # Display color swatches
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("สี CI ลูกค้า")
        st.image(create_color_swatch(rgb1), caption=f"RGB: {rgb1}")
        st.write(f"**HEX:** {cu.rgb_to_hex(*rgb1)}")
        st.write(f"**L:** {lab1[0]:.2f}")
        st.write(f"**a:** {lab1[1]:.2f}")
        st.write(f"**b:** {lab1[2]:.2f}")

    with col2:
        st.subheader("สีที่ผลิตได้")
        st.image(create_color_swatch(rgb2), caption=f"RGB: {rgb2}")
        st.write(f"**HEX:** {cu.rgb_to_hex(*rgb2)}")
        st.write(f"**L:** {lab2[0]:.2f}")
        st.write(f"**a:** {lab2[1]:.2f}")
        st.write(f"**b:** {lab2[2]:.2f}")

    with col3:
        st.subheader("ผลการเปรียบเทียบ")

        # Delta E indicator
        if delta_e < 1:
            status = "🟢 ผ่าน (ดีเยี่ยม)"
            color = "green"
        elif delta_e < 2:
            status = "🟡 ผ่าน (ดี)"
            color = "orange"
        elif delta_e < 5:
            status = "🟠 เฝ้าระวัง"
            color = "orange"
        else:
            status = "🔴 ไม่ผ่าน"
            color = "red"

        st.metric("Delta E", f"{delta_e:.3f}", status)
        st.metric("ความคล้ายคลึง", f"{similarity:.2f}%")

        st.write(f"**ΔL:** {abs(lab2[0] - lab1[0]):.2f}")
        st.write(f"**Δa:** {abs(lab2[1] - lab1[1]):.2f}")
        st.write(f"**Δb:** {abs(lab2[2] - lab1[2]):.2f}")

    st.divider()

    # Detailed comparison table
    st.subheader("📋 ตารางเปรียบเทียบโดยละเอียด")

    comparison_data = {
        "คุณสมบัติ": ["RGB", "HEX", "L", "a", "b", "C (Chroma)", "H (Hue)"],
        "CI ลูกค้า": [
            f"rgb{rgb1}",
            cu.rgb_to_hex(*rgb1),
            f"{lab1[0]:.2f}",
            f"{lab1[1]:.2f}",
            f"{lab1[2]:.2f}",
            f"{lch1[1]:.2f}",
            f"{lch1[2]:.2f}°"
        ],
        "สีที่ผลิต": [
            f"rgb{rgb2}",
            cu.rgb_to_hex(*rgb2),
            f"{lab2[0]:.2f}",
            f"{lab2[1]:.2f}",
            f"{lab2[2]:.2f}",
            f"{lch2[1]:.2f}",
            f"{lch2[2]:.2f}°"
        ],
        "ความแตกต่าง (Δ)": [
            "-",
            "-",
            f"{abs(lab2[0] - lab1[0]):.2f}",
            f"{abs(lab2[1] - lab1[1]):.2f}",
            f"{abs(lab2[2] - lab1[2]):.2f}",
            f"{abs(lch2[1] - lch1[1]):.2f}",
            f"{abs(lch2[2] - lch1[2]):.2f}°"
        ]
    }

    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)

    # Display AI Analysis Result (if available)
    if st.session_state.ai_response:
        st.divider()

        # AI Analysis Header with animation
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🤖 ผลการวิเคราะห์จาก AI</h2>
        </div>
        """, unsafe_allow_html=True)

        ai_resp = st.session_state.ai_response

        if isinstance(ai_resp, dict):
            # Row 1: Summary and Status
            col_summary, col_status = st.columns([2, 1])

            with col_summary:
                if "summary" in ai_resp and ai_resp['summary']:
                    st.info(f"📊 **สรุป**\n\n{ai_resp['summary']}")

            with col_status:
                if "quality_status" in ai_resp:
                    status_text = ai_resp['quality_status']
                    if status_text == "ผ่าน":
                        st.success(f"### ✅ {status_text}")
                    elif status_text == "เฝ้าระวัง":
                        st.warning(f"### ⚠️ {status_text}")
                    else:
                        st.error(f"### ❌ {status_text}")

                if "risk_level" in ai_resp:
                    risk = ai_resp['risk_level']
                    risk_icons = {"ต่ำ": "🟢", "กลาง": "🟡", "สูง": "🔴"}
                    st.metric("ระดับความเสี่ยง", f"{risk_icons.get(risk, '⚪')} {risk}")

            st.markdown("")

            # Row 2: Recommendations and Color Adjustments
            col_rec, col_adj = st.columns([1, 1])

            with col_rec:
                if "recommendations" in ai_resp and ai_resp['recommendations']:
                    st.markdown("### 💡 คำแนะนำ")
                    for i, rec in enumerate(ai_resp['recommendations'], 1):
                        st.markdown(f"**{i}.** {rec}")

            with col_adj:
                if "color_adjustments" in ai_resp and ai_resp['color_adjustments']:
                    st.markdown("### 🎨 การปรับค่าสีที่แนะนำ")
                    adj = ai_resp['color_adjustments']

                    adj_col1, adj_col2, adj_col3 = st.columns(3)
                    with adj_col1:
                        if "L" in adj and adj['L']:
                            st.metric("L", adj['L'], help="Lightness")
                    with adj_col2:
                        if "a" in adj and adj['a']:
                            st.metric("a", adj['a'], help="Red/Green")
                    with adj_col3:
                        if "b" in adj and adj['b']:
                            st.metric("b", adj['b'], help="Yellow/Blue")

            # Notes
            if "notes" in ai_resp and ai_resp['notes']:
                st.markdown("")
                st.info(f"📝 **หมายเหตุ:** {ai_resp['notes']}")

            # Full JSON data
            with st.expander("🔍 ดูข้อมูล JSON ทั้งหมด"):
                st.json(ai_resp)
        else:
            st.info(str(ai_resp))

    st.divider()

    # Export to n8n
    st.subheader("📤 ส่งข้อมูลไปยัง n8n")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.info(f"**Webhook URL:** {webhook_url if webhook_url else 'ยังไม่ได้กำหนด'}")

    with col2:
        if st.button("📨 ส่งข้อมูล", type="primary", disabled=not webhook_url):
            # Prepare data for webhook
            webhook_data = {
                "timestamp": datetime.now().isoformat(),
                "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "files": {
                    "customer_ci": st.session_state.filename1,
                    "production": st.session_state.filename2
                },
                "colors": {
                    "customer_ci": {
                        "rgb": list(rgb1),
                        "hex": cu.rgb_to_hex(*rgb1),
                        "lab": {
                            "L": round(lab1[0], 2),
                            "a": round(lab1[1], 2),
                            "b": round(lab1[2], 2)
                        },
                        "lch": {
                            "L": round(lch1[0], 2),
                            "C": round(lch1[1], 2),
                            "H": round(lch1[2], 2)
                        }
                    },
                    "production": {
                        "rgb": list(rgb2),
                        "hex": cu.rgb_to_hex(*rgb2),
                        "lab": {
                            "L": round(lab2[0], 2),
                            "a": round(lab2[1], 2),
                            "b": round(lab2[2], 2)
                        },
                        "lch": {
                            "L": round(lch2[0], 2),
                            "C": round(lch2[1], 2),
                            "H": round(lch2[2], 2)
                        }
                    }
                },
                "comparison": {
                    "delta_e": round(delta_e, 3),
                    "similarity_percent": round(similarity, 2),
                    "method": delta_method,
                    "delta_L": round(abs(lab2[0] - lab1[0]), 2),
                    "delta_a": round(abs(lab2[1] - lab1[1]), 2),
                    "delta_b": round(abs(lab2[2] - lab1[2]), 2),
                    "status": status
                },
                "settings": {
                    "delta_cap": delta_cap,
                    "sampling_method": sampling_method,
                    "sample_size": sample_size
                }
            }

            # Show loading spinner while waiting for AI analysis
            with st.spinner("🤖 กำลังส่งข้อมูลและรอผลการวิเคราะห์จาก AI..."):
                success, message, ai_response = send_to_n8n(webhook_url, webhook_data)

            if success:
                st.success(message)

                # Store AI response in session state
                if ai_response:
                    st.session_state.ai_response = ai_response
                    st.balloons()  # Celebration animation
                    st.rerun()  # Refresh to show AI response

                with st.expander("📤 ดูข้อมูลที่ส่งไป"):
                    st.json(webhook_data)
            else:
                st.error(message)

    # Download JSON button
    st.download_button(
        label="💾 ดาวน์โหลดข้อมูล JSON",
        data=json.dumps({
            "timestamp": datetime.now().isoformat(),
            "files": {
                "customer_ci": st.session_state.filename1,
                "production": st.session_state.filename2
            },
            "comparison": {
                "delta_e": round(delta_e, 3),
                "similarity_percent": round(similarity, 2),
                "customer_ci_lab": {"L": round(lab1[0], 2), "a": round(lab1[1], 2), "b": round(lab1[2], 2)},
                "production_lab": {"L": round(lab2[0], 2), "a": round(lab2[1], 2), "b": round(lab2[2], 2)}
            }
        }, indent=2, ensure_ascii=False),
        file_name=f"color_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

else:
    st.info("👆 กรุณาอัพโหลดรูปภาพทั้งสองรูปเพื่อเริ่มการเปรียบเทียบ")

# Footer
st.divider()
st.caption("🎨 Color Comparison Tool for Packaging Quality Control | Made with Streamlit")
