import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import { mdToPdf } from 'md-to-pdf';

// Start server + add functionalities
const app = express()
const port = 3000
app.use(bodyParser.urlencoded({extended: true}))
app.use(bodyParser.json())

// Convert to PDF utility function
const convertToPdf = async (filePath: string) => {
  return await mdToPdf({ path: filePath}).catch(console.error)
};

// Set API endpoint
app.post('/convert', async (req, res) => {
  if (req.body.text == "") {
    res.status(400).send("The is no text in the request")
  } 

  console.log(`🔌 Converting MarkDown file to PDF...`)

  console.log(`📚 Creating temporary MarkDown file (temp.md)...`)
  fs.writeFileSync(".temp/temp.md", req.body.text)

  console.log("🛠 Converting to PDF...")
  const pdf = await convertToPdf(".temp/temp.md")

  // Check conversion status
  if (pdf) {
    res.contentType('application/pdf')
    res.send(pdf.content)
    console.log("✅ Document exported successfully")
  } else {
    console.log("❌ Error occurred while exporting PDF")
    res.status(500).send("Cannot export to PDF document")
  }
})

// Start listening on port 3000!
app.listen(port, () => {
  console.log(`CONVERSION_SERVER_READY`)
})