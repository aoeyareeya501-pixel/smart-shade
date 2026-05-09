# 🎨 Color Comparison Tool for Packaging Quality Control

เครื่องมือเปรียบเทียบค่าสีสำหรับควบคุมคุณภาพในไลน์การผลิตกล่องและแพ็คเกจ

## คุณสมบัติ

- ✅ อัพโหลดรูปภาพ 2 รูปเพื่อเปรียบเทียบสี (CI ลูกค้า vs สีที่ผลิต)
- ✅ คำนวณ Delta E (CIEDE2000 และ ΔE76)
- ✅ แสดงค่า L, a, b (LAB color space)
- ✅ แสดงค่า L, C, H (LCH color space)
- ✅ เลือกสีโดยการคลิกบนรูปภาพ หรือคำนวณสีเฉลี่ยของรูปทั้งหมด
- ✅ **วิเคราะห์ผลด้วย AI** - ส่งข้อมูลไปวิเคราะห์และรับคำแนะนำจาก AI
- ✅ แสดงผลการวิเคราะห์แบบ real-time พร้อม UI ที่สวยงาม
- ✅ ส่งข้อมูลไปยัง n8n webhook สำหรับบันทึกและ automation
- ✅ ดาวน์โหลดข้อมูลเป็นไฟล์ JSON

## การติดตั้ง

### 1. แตกไฟล์โปรเจค

แตกไฟล์ zip ที่ได้รับแล้วเปิด Terminal/Command Prompt ไปที่โฟลเดอร์โปรเจค

```bash
cd path/to/smart-shade
```

### 2. สร้าง Virtual Environment (แนะนำ)

```bash
python3 -m venv venv
source venv/bin/activate  # สำหรับ Mac/Linux
# หรือ
venv\Scripts\activate  # สำหรับ Windows
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

## การใช้งาน

### รันแอปพลิเคชัน

```bash
streamlit run app.py
```

แอปจะเปิดใน browser ที่ `http://localhost:8501`

### วิธีการใช้งาน

1. **อัพโหลดรูปภาพ**
   - อัพโหลดรูปภาพ CI ของลูกค้าที่ช่องซ้าย
   - อัพโหลดรูปภาพสีที่ผลิตได้ที่ช่องขวา

2. **เลือกวิธีการสุ่มสี** (ที่ Sidebar)
   - **สีเฉลี่ยของรูปทั้งหมด**: ระบบจะคำนวณสีเฉลี่ยของรูปทั้งหมด
   - **คลิกเลือกจุดบนรูป**: คลิกบนรูปภาพเพื่อเลือกจุดที่ต้องการเปรียบเทียบ

3. **ดูผลการเปรียบเทียบ**
   - ค่า Delta E (ความแตกต่างของสี)
   - ค่า L, a, b (LAB color space)
   - ตารางเปรียบเทียบโดยละเอียด

4. **ส่งข้อมูลไปวิเคราะห์ด้วย AI** (ตัวเลือกเสริม)
   - กรอก Webhook URL ของ n8n ที่เชื่อมต่อกับ AI ที่ Sidebar
   - กดปุ่ม "📨 ส่งข้อมูล"
   - รอสักครู่ ระบบจะแสดงผลการวิเคราะห์จาก AI:
     - 📊 สรุปผลการวิเคราะห์
     - ✅ สถานะคุณภาพ (ผ่าน/เฝ้าระวัง/ไม่ผ่าน)
     - 🎯 ระดับความเสี่ยง
     - 💡 คำแนะนำในการปรับปรุง
     - 🎨 ค่าสีที่ควรปรับ (L, a, b)
   - **หมายเหตุ**: ถ้าไม่มี n8n+AI หรือไม่ต้องการใช้ ข้ามขั้นตอนนี้ได้

5. **ดาวน์โหลดข้อมูล**
   - กดปุ่ม "💾 ดาวน์โหลดข้อมูล JSON" เพื่อบันทึกผลลัพธ์

## การตีความค่า Delta E

| Delta E | ความหมาย |
|---------|---------|
| 0 - 1.0 | ไม่สามารถสังเกตความแตกต่างได้ด้วยตาเปล่า |
| 1.0 - 2.0 | แทบไม่สังเกตเห็นความแตกต่าง |
| 2.0 - 3.5 | สังเกตเห็นความแตกต่างได้เล็กน้อย |
| 3.5 - 5.0 | สังเกตเห็นความแตกต่างได้ชัดเจน |
| > 5.0 | สีต่างกันอย่างเห็นได้ชัด |

## โครงสร้างโปรเจค

```
smart-shade/
├── app.py                      # Streamlit application หลัก
├── color_utils.py              # Functions สำหรับแปลงสีและคำนวณ Delta E
├── requirements.txt            # Python dependencies
├── README.md                   # คู่มือการใช้งาน
├── AI_RESPONSE_FORMAT.md       # โครงสร้าง JSON ที่ AI ต้องส่งกลับ
├── n8n_setup_guide.md          # คู่มือตั้งค่า n8n สำหรับ AI integration
└── .gitignore                  # ไฟล์ที่ไม่ต้อง track
```

## 🤖 AI Integration (ตัวเลือกเสริม)

แอปนี้รองรับการวิเคราะห์ผลด้วย AI ผ่าน n8n workflow ที่สามารถเชื่อมต่อกับ:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic Claude
- Google Gemini
- หรือ AI อื่นๆ ที่รองรับใน n8n

### คู่มือการตั้งค่า AI Integration

📚 **อ่านคู่มือฉบับเต็มได้ที่:**
- `AI_RESPONSE_FORMAT.md` - โครงสร้าง JSON ที่ AI ต้องส่งกลับ
- `n8n_setup_guide.md` - วิธีตั้งค่า n8n workflow ทีละขั้นตอน

### ผลลัพธ์ที่ได้จาก AI

เมื่อส่งข้อมูลไป AI จะวิเคราะห์และส่งกลับมาด้วย:
1. **สรุปผลการวิเคราะห์** - คำอธิบายโดยละเอียดเกี่ยวกับความแตกต่างของสี
2. **สถานะคุณภาพ** - ผ่าน / เฝ้าระวัง / ไม่ผ่าน
3. **ระดับความเสี่ยง** - ต่ำ / กลาง / สูง
4. **คำแนะนำ** - ข้อเสนอแนะในการปรับปรุงคุณภาพสี
5. **ค่าสีที่ควรปรับ** - การปรับค่า L, a, b ที่แนะนำ

### Quick Start: ตั้งค่า AI ด้วย n8n

```
Workflow Structure:
Webhook → AI Node → Code (Parse JSON) → Respond to Webhook
```

ดูรายละเอียดเพิ่มเติมใน `n8n_setup_guide.md`

---

## 📡 n8n Webhook Integration

### ตัวอย่างข้อมูลที่ส่งไปยัง webhook:

```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "upload_date": "2024-01-15 10:30:00",
  "files": {
    "customer_ci": "ci_sample.jpg",
    "production": "production_sample.jpg"
  },
  "colors": {
    "customer_ci": {
      "rgb": [59, 130, 246],
      "hex": "#3B82F6",
      "lab": {
        "L": 54.29,
        "a": 10.52,
        "b": -60.83
      }
    },
    "production": {
      "rgb": [60, 131, 245],
      "hex": "#3C83F5",
      "lab": {
        "L": 54.50,
        "a": 10.30,
        "b": -60.50
      }
    }
  },
  "comparison": {
    "delta_e": 0.523,
    "similarity_percent": 98.95,
    "method": "DE2000",
    "delta_L": 0.21,
    "delta_a": 0.22,
    "delta_b": 0.33,
    "status": "🟢 ผ่าน (ดีเยี่ยม)"
  }
}
```

### การตั้งค่า n8n (ถ้าต้องการใช้งาน webhook)

**หมายเหตุ**: การใช้ n8n เป็น **ตัวเลือกเสริม** ไม่บังคับ แอปสามารถใช้งานได้ปกติโดยไม่ต้องมี n8n

#### ถ้าคุณต้องการเชื่อมต่อกับ n8n:

1. **ติดตั้ง n8n** (ถ้ายังไม่มี):
   ```bash
   npm install -g n8n
   n8n start
   ```
   หรือใช้ n8n cloud: https://n8n.io

2. **สร้าง Webhook workflow**:
   - สร้าง Webhook node (HTTP Method: POST)
   - เพิ่ม "Respond to Webhook" node
   - เชื่อมต่อทั้งสอง node
   - ตั้งค่า Webhook node → Respond: "Using Respond to Webhook Node"
   - กด **Active** (สำคัญ!)

3. **คัดลอก Production Webhook URL**:
   - คลิกที่ Webhook node
   - คัดลอก URL (เช่น `https://your-n8n.com/webhook/smart-shade`)

4. **วาง URL ในแอป**:
   - เปิดแอป Streamlit
   - วาง URL ในช่อง "Webhook URL" ที่ Sidebar
   - เมื่อกดปุ่ม "📨 ส่งข้อมูล" ข้อมูลจะถูกส่งไปยัง n8n

#### ตัวอย่างการใช้งานใน n8n:
- บันทึกข้อมูลลง Google Sheets
- ส่ง notification ผ่าน Line/Slack เมื่อค่า Delta E เกินเกณฑ์
- บันทึกข้อมูลลง Database (MySQL, PostgreSQL, MongoDB)
- สร้างรายงานอัตโนมัติและส่ง Email
- Export ข้อมูลไปยังระบบ ERP/MES

## เทคโนโลยีที่ใช้

- **Streamlit**: Web framework สำหรับ Python
- **Pillow (PIL)**: การประมวลผลรูปภาพ
- **streamlit-image-coordinates**: สำหรับการคลิกเลือกสีบนรูปภาพ
- **Requests**: สำหรับส่งข้อมูลไปยัง webhook
- **Pandas**: สำหรับจัดการและแสดงข้อมูลในรูปแบบตาราง

## การ Deploy

### Deploy บน Local Network (สำหรับใช้ในโรงงาน)

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

เครื่องอื่นในเครือข่ายเดียวกันสามารถเข้าถึงได้ที่ `http://<your-ip>:8501`

### Deploy บน Streamlit Cloud (ฟรี)

1. Push โค้ดขึ้น GitHub repository
2. ไปที่ [share.streamlit.io](https://share.streamlit.io)
3. เชื่อมต่อ GitHub repository
4. Deploy!

### Deploy บน Server (Docker)

สร้างไฟล์ `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build และรัน:

```bash
docker build -t color-comparison-tool .
docker run -p 8501:8501 color-comparison-tool
```

## License

สามารถใช้งานได้อย่างอิสระ

## ติดต่อและแจ้งปัญหา

หากพบปัญหาหรือต้องการความช่วยเหลือ สามารถติดต่อได้ที่ [เพิ่ม contact ของคุณที่นี่]
