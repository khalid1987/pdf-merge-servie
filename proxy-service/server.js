const express = require('express');
const FormData = require('form-data');
const axios = require('axios');

const app = express();
app.use(express.json({ limit: '50mb' }));

app.post('/merge', async (req, res) => {
  try {
    const { files } = req.body;
    
    if (!files || !Array.isArray(files) || files.length < 2) {
      return res.status(400).json({ error: 'Need at least 2 files with base64 data' });
    }

    // Create form data
    const form = new FormData();
    
    files.forEach((file, index) => {
      const buffer = Buffer.from(file.data, 'base64');
      form.append('fileInput', buffer, {
        filename: file.filename || `file${index + 1}.pdf`,
        contentType: 'application/pdf'
      });
    });

    // Call Stirling PDF
    const response = await axios.post(
      'http://stirling-pdf:8080/api/v1/general/merge-pdfs',
      form,
      {
        headers: form.getHeaders(),
        responseType: 'arraybuffer'
      }
    );

    // Return merged PDF as base64
    const mergedPdf = Buffer.from(response.data).toString('base64');
    
    res.json({
      success: true,
      data: mergedPdf,
      mimeType: 'application/pdf',
      filename: 'merged.pdf',
      size: response.data.length
    });

  } catch (error) {
    console.error('Merge error:', error.message);
    if (error.response) {
      console.error('Stirling response status:', error.response.status);
      console.error('Stirling response data:', error.response.data);
    }
    res.status(500).json({ 
      error: 'Merge failed', 
      details: error.message,
      stirlingStatus: error.response?.status,
      stirlingError: error.response?.data?.toString()
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'pdf-merge-proxy' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`PDF Merge Proxy listening on port ${PORT}`);
});
