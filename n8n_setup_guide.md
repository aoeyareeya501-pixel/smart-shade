# 🔧 คู่มือตั้งค่า n8n สำหรับ Smart Shade App

## 📊 Workflow Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    n8n Workflow                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [Webhook]  ← รับข้อมูลจาก Smart Shade App              │
│       ↓                                                     │
│  2. [AI Node]  ← วิเคราะห์สี Delta E                       │
│       ↓                                                     │
│  3. [Code]     ← แปลง string JSON → object                 │
│       ↓                                                     │
│  4. [Respond to Webhook] ← ส่งกลับไป App                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 การตั้งค่าแต่ละ Node

### Node 1: Webhook (รับข้อมูล)

**Settings:**
- HTTP Method: `POST`
- Path: `/color-analysis` (หรือชื่ออื่นที่ต้องการ)
- **Response Mode: `When Last Node Finishes`** ← สำคัญมาก!

**ทำไมต้องเป็น "When Last Node Finishes"?**
- เพื่อให้ workflow รอให้ AI วิเคราะห์เสร็จก่อน จึงส่ง response กลับ
- ถ้าเป็น "Immediately" App จะได้ response เปล่าทันที

---

### Node 2: AI Agent / OpenAI / Claude

**ข้อมูลที่ App ส่งมา:**
```javascript
{
  "timestamp": "2025-10-31T...",
  "colors": {
    "customer_ci": {
      "rgb": [120, 80, 160],
      "lab": {"L": 45.23, "a": 35.12, "b": -25.45}
    },
    "production": {
      "rgb": [125, 75, 155],
      "lab": {"L": 43.74, "a": 30.50, "b": -26.64}
    }
  },
  "comparison": {
    "delta_e": 2.958,
    "delta_L": 1.49,
    "delta_a": 4.62,
    "delta_b": 1.19,
    "status": "🟠 เฝ้าระวัง"
  }
}
```

**Prompt สำหรับ AI:**

```
คุณเป็นผู้เชี่ยวชาญควบคุมคุณภาพสีในอุตสาหกรรมบรรจุภัณฑ์

วิเคราะห์ข้อมูลสีและ return JSON เท่านั้น:

{
  "summary": "สรุปผลการวิเคราะห์",
  "quality_status": "ผ่าน | เฝ้าระวัง | ไม่ผ่าน",
  "risk_level": "ต่ำ | กลาง | สูง",
  "recommendations": ["คำแนะนำ 1", "คำแนะนำ 2"],
  "color_adjustments": {
    "L": "ค่าที่ควรปรับ",
    "a": "ค่าที่ควรปรับ",
    "b": "ค่าที่ควรปรับ"
  },
  "notes": "หมายเหตุเพิ่มเติม"
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
- Customer CI Lab: L={{ $json.colors.customer_ci.lab.L }}, a={{ $json.colors.customer_ci.lab.a }}, b={{ $json.colors.customer_ci.lab.b }}
- Production Lab: L={{ $json.colors.production.lab.L }}, a={{ $json.colors.production.lab.a }}, b={{ $json.colors.production.lab.b }}

คำแนะนำ color_adjustments:
- ถ้า Production > Customer → ใส่เครื่องหมาย "-" (ลดลง)
- ถ้า Production < Customer → ใส่เครื่องหมาย "+" (เพิ่มขึ้น)
- ระบุค่าความแตกต่างที่วัดได้ (เช่น "+2.5 หน่วย")

วิเคราะห์เป็นภาษาไทย และ return เฉพาะ JSON object เท่านั้น (ห้ามใส่ markdown หรือข้อความอื่น)
```

**Output ที่ได้จาก AI จะเป็น:**
```json
[
  {
    "output": "{\"summary\":\"...\",\"quality_status\":\"เฝ้าระวัง\",...}"
  }
]
```

---

### Node 3: Code (Parse JSON String)

**JavaScript Code:**

```javascript
// รับ response จาก AI Node
const aiOutput = $input.first().json;

// ดึงข้อมูลและแปลง JSON string → object
let parsedData;

try {
  if (Array.isArray(aiOutput)) {
    // กรณี AI return เป็น array (ตามตัวอย่างที่คุณส่งมา)
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
} catch (error) {
  // ถ้า parse ไม่ได้ ให้ return default
  return {
    json: {
      summary: "เกิดข้อผิดพลาดในการแปลงข้อมูล AI",
      quality_status: "เฝ้าระวัง",
      risk_level: "กลาง",
      recommendations: ["ตรวจสอบ AI response format"],
      color_adjustments: {},
      notes: `Error: ${error.message}`
    }
  };
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

**Output จาก Code Node:**
```json
{
  "summary": "การเปรียบเทียบสี...",
  "quality_status": "เฝ้าระวัง",
  "risk_level": "กลาง",
  "recommendations": ["ตรวจสอบ...", "ปรับค่า Lab..."],
  "color_adjustments": {
    "L": "-1.49",
    "a": "-4.62",
    "b": "-1.19"
  },
  "notes": "ค่าความแตกต่าง..."
}
```

---

### Node 4: Respond to Webhook

**Settings:**
- **Respond With**: "Using 'Respond to Webhook' Node"
- **Response Code**: 200
- **Response Body**: `{{ $json }}`

**หรือ:**
- Response Body: "Define Below"
- ใส่: `{{ JSON.stringify($json) }}`

---

## 🔍 การทดสอบ

### 1. ทดสอบใน n8n
1. คลิก "Execute Workflow" ใน n8n
2. ใช้ Postman หรือ curl ส่งข้อมูลทดสอบ:

```bash
curl -X POST https://your-n8n.com/webhook/color-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "comparison": {
      "delta_e": 2.958,
      "delta_L": 1.49,
      "delta_a": 4.62,
      "delta_b": 1.19
    },
    "colors": {
      "customer_ci": {"lab": {"L": 45.23, "a": 35.12, "b": -25.45}},
      "production": {"lab": {"L": 43.74, "a": 30.50, "b": -26.64}}
    }
  }'
```

3. ตรวจสอบ response ว่าได้ JSON object ที่ถูกต้อง

### 2. ทดสอบกับ Smart Shade App
1. นำ Webhook URL ไปใส่ใน App (Sidebar → n8n Webhook)
2. Upload รูป 2 รูป
3. กดปุ่ม "📨 ส่งข้อมูล"
4. ดูผลการวิเคราะห์ที่แสดงบน App

---

## ✅ Checklist

- [ ] Webhook Node: ตั้ง Response Mode = "When Last Node Finishes"
- [ ] AI Prompt: ให้ return JSON โดยไม่มี markdown
- [ ] Code Node: ใส่โค้ด parse JSON string → object
- [ ] Code Node: ใส่ try-catch เพื่อจัดการ error
- [ ] Respond to Webhook: ตั้งค่า response body = `{{ $json }}`
- [ ] ทดสอบด้วย curl หรือ Postman
- [ ] ทดสอบกับ App จริง

---

## 🐛 Troubleshooting

### ปัญหา: App รอ 60 วินาที แล้วหมดเวลา

**สาเหตุ:** Webhook ตั้งค่าผิด
```
Webhook Node → Settings → Response Mode → เปลี่ยนเป็น "When Last Node Finishes"
```

### ปัญหา: App แสดง "ไม่สามารถอ่าน response จาก n8n ได้"

**สาเหตุ:** Code Node ไม่ได้ parse JSON
- ตรวจสอบว่า Code Node มีโค้ด `JSON.parse()`
- ดู output ของ AI Node ว่าเป็น format ไหน

### ปัญหา: AI ใส่ markdown (```json...```)

**แก้ไข:** เพิ่มใน AI prompt:
```
Return เฉพาะ JSON object เท่านั้น
ห้ามใส่ ```json หรือ markdown ใดๆ
```

### ปัญหา: color_adjustments ไม่แสดงบน App

**ตรวจสอบ:**
1. ใน Code Node output ต้องมี field `color_adjustments`
2. ค่าต้องเป็น object เช่น `{"L": "+2.5", "a": "-1.2"}`
3. ดูใน Expander "ดูข้อมูล JSON ทั้งหมด" บน App

---

## 📊 ตัวอย่าง Response ที่ถูกต้อง

```json
{
  "summary": "ค่า Delta E อยู่ที่ 2.958 อยู่ในเกณฑ์เฝ้าระวัง",
  "quality_status": "เฝ้าระวัง",
  "risk_level": "กลาง",
  "recommendations": [
    "ตรวจสอบกระบวนการผลิต",
    "ปรับค่า Lab ให้ใกล้เคียงมากขึ้น"
  ],
  "color_adjustments": {
    "L": "-1.49 หน่วย",
    "a": "-4.62 หน่วย",
    "b": "-1.19 หน่วย"
  },
  "notes": "ควรปรับปรุงก่อนผลิตจำนวนมาก"
}
```

---

## 📞 ติดปัญหา?

1. ตรวจสอบ execution log ใน n8n
2. ดู error message ใน App
3. ทดสอบแต่ละ node ทีละตัว
4. ใช้ "Execute Workflow" ใน n8n เพื่อ debug
