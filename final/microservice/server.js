const express = require('express');
const fs = require('fs');

const app = express();

// Define a route to handle image requests
app.get('/image', (req, res) => {
    // Read the image file from the file system
    fs.readFile(`${process.cwd()}/../backend/media/generated/${req.query.filename}`, (err, data) => {
        if (err) {
            console.error(err);
            res.status(500).send('Internal Server Error');
            return;
        }
        res.setHeader('Content-Disposition', 'attachment; filename="' + req.query.filename + '"');
        res.contentType('image/jpeg');
        res.send(data);
    });
});

// Define a route to handle PDF requests
app.get('/pdf', (req, res) => {
    // Read the PDF file from the file system
    fs.readFile(`${process.cwd()}/../backend/media/generated/${req.query.filename}`, (err, data) => {
        if (err) {
            console.error(err);
            res.status(500).send('Internal Server Error');
            return;
        }
        res.setHeader('Content-Disposition', 'attachment; filename="' + req.query.filename + '"');
        res.contentType('application/pdf');
        res.send(data);
    });
});

app.get('/dxf', (req, res) => {
    // Read the DXF file from the file system
    fs.readFile(`${process.cwd()}/../backend/media/clothesdata/${req.query.filename}/${req.query.filename}.dxf`, (err, data) => {
        if (err) {
            console.error(err);
            res.status(500).send('Internal Server Error');
            return;
        }
        // Set Content-Disposition header to make the browser download the DXF file
        res.setHeader('Content-Disposition', 'attachment; filename="' + req.query.filename + '"');
        res.contentType('application/octet-stream'); // Set content type for DXF file
        res.send(data);
    });
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
