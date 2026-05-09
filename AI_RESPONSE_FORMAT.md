# AI Response JSON Structure

## 📋 โครงสร้าง JSON ที่ n8n ต้องส่งกลับมา

n8n workflow ต้อง return JSON ในรูปแบบนี้:

```json
{
  "summary": "ข้อความสรุปผลการวิเคราะห์",
  "quality_status": "ผ่าน | เฝ้าระวัง | ไม่ผ่าน",
  "risk_level": "ต่ำ | กลาง | สูง",
  "recommendations": [
    "คำแนะนำข้อที่ 1",
    "คำแนะนำข้อที่ 2",
    "คำแนะนำข้อที่ 3"
  ],
  "color_adjustments": {
    "L": "+2.5 หน่วย",
    "a": "-1.2 หน่วย",
    "b": "+0.8 หน่วย"
  },
  "notes": "หมายเหตุเพิ่มเติม (optional)"
}
```

---

## 📝 รายละเอียดแต่ละ Field

### 1. `summary` (string, required)
สรุปผลการวิเคราะห์โดยรวม

**ตัวอย่าง:**
```json
"summary": "ค่า Delta E อยู่ที่ 3.45 ซึ่งอยู่ในเกณฑ์เฝ้าระวัง สีที่ผลิตได้มีความแตกต่างจากสี CI ในระดับปานกลาง"
```

---

### 2. `quality_status` (string, required)
สถานะคุณภาพ มี 3 ค่า:
- `"ผ่าน"` - แสดงเป็นกล่องสีเขียว ✅
- `"เฝ้าระวัง"` - แสดงเป็นกล่องสีเหลือง ⚠️
- `"ไม่ผ่าน"` - แสดงเป็นกล่องสีแดง ❌

**ตัวอย่าง:**
```json
"quality_status": "เฝ้าระวัง"
```

**เงื่อนไขแนะนำ:**
- `Delta E < 1.0` → "ผ่าน"
- `1.0 ≤ Delta E < 5.0` → "เฝ้าระวัง"
- `Delta E ≥ 5.0` → "ไม่ผ่าน"

---

### 3. `risk_level` (string, required)
ระดับความเสี่ยง มี 3 ค่า:
- `"ต่ำ"` - แสดง 🟢
- `"กลาง"` - แสดง 🟡
- `"สูง"` - แสดง 🔴

**ตัวอย่าง:**
```json
"risk_level": "กลาง"
```

---

### 4. `recommendations` (array of strings, optional)
รายการคำแนะนำสำหรับการปรับปรุง แสดงเป็น bullet list

**ตัวอย่าง:**
```json
"recommendations": [
  "ปรับสูตรสีโดยเพิ่มปริมาณสีแดงเล็กน้อย",
  "ตรวจสอบความสม่ำเสมอของการผสมสี",
  "ควรทดสอบซ้ำอีก 1-2 ครั้งเพื่อยืนยันผล"
]
```

---

### 5. `color_adjustments` (object, optional)
ค่าที่แนะนำให้ปรับ L, a, b

**รูปแบบ:**
```json
"color_adjustments": {
  "L": "+2.5 หน่วย",    // เพิ่ม/ลด ความสว่าง
  "a": "-1.2 หน่วย",    // เพิ่ม/ลด แดง-เขียว
  "b": "+0.8 หน่วย"     // เพิ่ม/ลด เหลือง-น้ำเงิน
}
```

**หมายเหตุ:**
- ใส่เครื่องหมาย `+` หรือ `-` ชัดเจน
- ถ้าไม่ต้องปรับค่าใด สามารถใส่ `"ไม่ต้องปรับ"` หรือไม่ใส่ field นั้นก็ได้

**ตัวอย่าง:**
```json
"color_adjustments": {
  "L": "-2.0 หน่วย",
  "a": "+1.5 หน่วย",
  "b": "ไม่ต้องปรับ"
}
```

---

### 6. `notes` (string, optional)
หมายเหตุหรือข้อมูลเพิ่มเติม

**ตัวอย่าง:**
```json
"notes": "แนะนำให้บันทึกค่านี้เป็น reference สำหรับการผลิตครั้งต่อไป"
```

---

## 🎯 ตัวอย่าง JSON ครบทุก Field

### ตัวอย่างที่ 1: กรณีผ่านเกณฑ์
```json
{
  "summary": "ค่า Delta E อยู่ที่ 0.85 ซึ่งอยู่ในเกณฑ์ดีเยี่ยม สีที่ผลิตได้ใกล้เคียงกับสี CI ของลูกค้ามาก",
  "quality_status": "ผ่าน",
  "risk_level": "ต่ำ",
  "recommendations": [
    "คงสูตรสีนี้ไว้สำหรับการผลิตต่อไป",
    "บันทึกค่าสีเป็น standard reference"
  ],
  "color_adjustments": {
    "L": "ไม่ต้องปรับ",
    "a": "ไม่ต้องปรับ",
    "b": "ไม่ต้องปรับ"
  },
  "notes": "ผลลัพธ์อยู่ในเกณฑ์มาตรฐานสากล"
}
```

### ตัวอย่างที่ 2: กรณีเฝ้าระวัง
```json
{
  "summary": "ค่า Delta E อยู่ที่ 3.45 ซึ่งอยู่ในเกณฑ์เฝ้าระวัง สีที่ผลิตได้มีความแตกต่างจากสี CI ในระดับปานกลาง โดยเฉพาะค่าความสว่าง (L) และค่า a",
  "quality_status": "เฝ้าระวัง",
  "risk_level": "กลาง",
  "recommendations": [
    "ปรับสูตรสีโดยลดความสว่างลง 2 หน่วย",
    "เพิ่มปริมาณสีแดงเล็กน้อยเพื่อปรับค่า a",
    "ทดสอบซ้ำหลังปรับสูตรเพื่อยืนยันผล"
  ],
  "color_adjustments": {
    "L": "-2.0 หน่วย",
    "a": "+1.5 หน่วย",
    "b": "+0.3 หน่วย"
  },
  "notes": "แนะนำให้ติดตามผลอย่างใกล้ชิด และปรับปรุงกระบวนการผสมสี"
}
```

### ตัวอย่างที่ 3: กรณีไม่ผ่าน
```json
{
  "summary": "ค่า Delta E อยู่ที่ 7.82 ซึ่งสูงเกินเกณฑ์ที่กำหนด สีที่ผลิตได้แตกต่างจากสี CI ของลูกค้าอย่างมีนัยสำคัญ",
  "quality_status": "ไม่ผ่าน",
  "risk_level": "สูง",
  "recommendations": [
    "ต้องปรับสูตรสีใหม่ทั้งหมด",
    "ตรวจสอบวัตถุดิบที่ใช้ว่าถูกต้องหรือไม่",
    "ตรวจสอบเครื่องมือวัดสีว่ามีการ calibrate ล่าสุด",
    "ติดต่อฝ่ายควบคุมคุณภาพก่อนผลิตต่อ"
  ],
  "color_adjustments": {
    "L": "-5.2 หน่วย",
    "a": "+3.8 หน่วย",
    "b": "-2.1 หน่วย"
  },
  "notes": "⚠️ สีนี้ไม่ผ่านเกณฑ์ ห้ามนำไปผลิตจริง ต้องปรับปรุงก่อน"
}
```

---

## 🔧 วิธีต่อ n8n Workflow (Step-by-Step)

### Workflow ทั้งหมด:
```
1. Webhook (รับข้อมูลจาก App)
   ↓
2. AI Agent / OpenAI / Claude Node (วิเคราะห์สี)
   ↓
3. Code Node (แปลง string เป็น JSON object)
   ↓
4. Respond to Webhook (ส่งกลับไปยัง App)
```

---

### 1️⃣ Webhook Node
- **Webhook URL**: คัดลอก URL นี้ไปใส่ใน App
- **HTTP Method**: POST
- **Response Mode**: "When Last Node Finishes" (สำคัญ! ต้องเลือกแบบนี้)

---

### 2️⃣ AI Node (OpenAI / Claude / AI Agent)
**Prompt สำหรับ AI:**
```
คุณเป็นผู้เชี่ยวชาญควบคุมคุณภาพสีในอุตสาหกรรมบรรจุภัณฑ์

วิเคราะห์ข้อมูลสีและ return JSON เท่านั้น (ไม่ต้องมี markdown):
{
  "summary": "สรุป",
  "quality_status": "ผ่าน|เฝ้าระวัง|ไม่ผ่าน",
  "risk_level": "ต่ำ|กลาง|สูง",
  "recommendations": ["คำแนะนำ"],
  "color_adjustments": {"L": "ค่า", "a": "ค่า", "b": "ค่า"},
  "notes": "หมายเหตุ"
}

เกณฑ์การตัดสิน:
- Delta E < 1.0 → quality_status: "ผ่าน", risk_level: "ต่ำ"
- 1.0 ≤ Delta E < 5.0 → quality_status: "เฝ้าระวัง", risk_level: "กลาง"
- Delta E ≥ 5.0 → quality_status: "ไม่ผ่าน", risk_level: "สูง"

ข้อมูลที่ได้รับ:
- Delta E: {{ $json.comparison.delta_e }}
- ΔL: {{ $json.comparison.delta_L }}
- Δa: {{ $json.comparison.delta_a }}
- Δb: {{ $json.comparison.delta_b }}
- Status: {{ $json.comparison.status }}
- Customer CI (Lab): L={{ $json.colors.customer_ci.lab.L }}, a={{ $json.colors.customer_ci.lab.a }}, b={{ $json.colors.customer_ci.lab.b }}
- Production (Lab): L={{ $json.colors.production.lab.L }}, a={{ $json.colors.production.lab.a }}, b={{ $json.colors.production.lab.b }}

กรุณาวิเคราะห์และให้คำแนะนำเป็นภาษาไทย แนะนำค่า color_adjustments ที่ควรปรับ
Return เฉพาะ JSON object เท่านั้น ห้ามใส่ markdown หรือข้อความอื่น
```

---

### 3️⃣ Code Node (Parse AI Response)
**สำคัญมาก!** ใช้โค้ดนี้แปลง AI response:

```javascript
// รับ response จาก AI
const aiOutput = $input.first().json;

// ดึงข้อมูลจาก array และ parse JSON string
let parsedData;

if (Array.isArray(aiOutput)) {
  // กรณี AI return เป็น array
  const outputString = aiOutput[0].output;
  parsedData = JSON.parse(outputString);
} else if (typeof aiOutput.output === 'string') {
  // กรณี AI return เป็น object ที่มี output เป็น string
  parsedData = JSON.parse(aiOutput.output);
} else if (typeof aiOutput === 'string') {
  // กรณี AI return เป็น string ตรงๆ
  parsedData = JSON.parse(aiOutput);
} else {
  // กรณี AI return เป็น object ปกติ
  parsedData = aiOutput;
}

// จัดรูปแบบให้ตรงกับ structure ที่ App ต้องการ
return {
  json: {
    summary: parsedData.summary || "",
    quality_status: parsedData.quality_status || "เฝ้าระวัง",
    risk_level: parsedData.risk_level || "กลาง",
    recommendations: parsedData.recommendations || [],
    color_adjustments: parsedData.color_adjustments || {},
    notes: parsedData.notes || ""
  }
};
```

---

### 4️⃣ Respond to Webhook Node
- **Respond With**: "Using 'Respond to Webhook' Node"
- **Response Code**: 200
- **Response Body**: `{{ $json }}`

**หรือตั้งค่าแบบ manual:**
- Response Body: เลือก "Define Below"
- ใส่: `{{ JSON.stringify($json) }}`

---

## 📋 Checklist การตั้งค่า

- [ ] Webhook Node: เปิด "When Last Node Finishes"
- [ ] AI Node: ตรวจสอบว่า prompt ให้ return JSON เท่านั้น
- [ ] Code Node: ใส่โค้ด parse JSON string
- [ ] Respond to Webhook: ตั้งค่า response body = `{{ $json }}`
- [ ] ทดสอบ workflow ด้วยการกด "Execute Workflow"

---

## 🐛 การแก้ปัญหา

### ปัญหา: App รอ 60 วินาที แล้วหมดเวลา
**สาเหตุ:** Webhook Node ตั้งค่าเป็น "Immediately" แทนที่จะเป็น "When Last Node Finishes"
**แก้ไข:** ไปที่ Webhook Node → Respond → เปลี่ยนเป็น "When Last Node Finishes"

### ปัญหา: App แสดง error "ไม่สามารถอ่าน response จาก n8n ได้"
**สาเหตุ:** Code Node ไม่ได้ parse JSON string
**แก้ไข:** ตรวจสอบ Code Node ว่าใช้โค้ด parse ถูกต้อง

### ปัญหา: AI return markdown (```json...```)
**สาเหตุ:** AI ไม่เข้าใจ prompt
**แก้ไข:** เพิ่มในปลาย prompt: "Return เฉพาะ JSON object เท่านั้น ห้ามใส่ markdown"

---

## 📌 หมายเหตุสำคัญ

1. **Field ที่จำเป็น (Required):**
   - `summary`
   - `quality_status`
   - `risk_level`

2. **Field ที่ใส่หรือไม่ใส่ก็ได้ (Optional):**
   - `recommendations`
   - `color_adjustments`
   - `notes`

3. **App จะแสดงเฉพาะ field ที่มีค่า** ถ้า field ไหนไม่มีจะไม่แสดงใน UI

4. **ตัวอักษรภาษาไทย** ใช้ได้ปกติ ไม่ต้อง encode

5. **Timeout:** App รอ response สูงสุด 60 วินาที

---

## 🎨 ตัวอย่าง Prompt สำหรับ AI

```
คุณเป็นผู้เชี่ยวชาญด้านการควบคุมคุณภาพสีในอุตสาหกรรมบรรจุภัณฑ์

วิเคราะห์ข้อมูลสีต่อไปนี้และ return JSON ตาม structure:
{
  "summary": "ข้อความสรุปผลการวิเคราะห์",
  "quality_status": "ผ่าน | เฝ้าระวัง | ไม่ผ่าน",
  "risk_level": "ต่ำ | กลาง | สูง",
  "recommendations": ["คำแนะนำ"],
  "color_adjustments": {
    "L": "ค่าปรับ",
    "a": "ค่าปรับ",
    "b": "ค่าปรับ"
  },
  "notes": "หมายเหตุ"
}

เกณฑ์การตัดสิน:
- Delta E < 1.0 → ผ่าน (risk: ต่ำ)
- 1.0 ≤ Delta E < 5.0 → เฝ้าระวัง (risk: กลาง)
- Delta E ≥ 5.0 → ไม่ผ่าน (risk: สูง)

ข้อมูลที่ได้รับ:
- Delta E: {{$json.comparison.delta_e}}
- ΔL: {{$json.comparison.delta_L}}
- Δa: {{$json.comparison.delta_a}}
- Δb: {{$json.comparison.delta_b}}
- Status: {{$json.comparison.status}}

กรุณาวิเคราะห์และให้คำแนะนำเป็นภาษาไทย
```
