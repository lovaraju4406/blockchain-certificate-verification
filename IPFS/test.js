import express from "express";
import { createHelia } from "helia";
import { unixfs } from "@helia/unixfs";
import multer from "multer";

const upload = multer();
const app = express();

const helia = await createHelia();
const fs = unixfs(helia);

console.log("🚀 Helia Node Started");

// ---------- UPLOAD (multipart/form-data) ---------- //
app.post("/upload", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.json({ Error: "No file uploaded" });
    }

    const cid = await fs.addBytes(req.file.buffer);

    res.json({ Success: cid.toString() });
  } catch (err) {
    res.json({ Error: err.message });
  }
});

// ---------- DOWNLOAD ---------- //
app.get("/download/:cid/:type", async (req, res) => {
  try {
    const { cid, type } = req.params;

    let data = [];
    for await (const chunk of fs.cat(cid)) {
      data.push(chunk);
    }

    const fileBuffer = Buffer.concat(data);
    const filename = `${cid.substring(0, 8)}.${type}`;

    res.setHeader("Content-Type", "application/octet-stream");
    res.setHeader("Content-Disposition", `inline; filename=${filename}`);

    res.send(fileBuffer);
  } catch (err) {
    res.json({ message: "Certificate not found " + err.message });
  }
});

// start
app.listen(5000, () => console.log("🔥 Server running on port 5000"));
