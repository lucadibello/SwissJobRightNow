import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import { mdToPdf } from 'md-to-pdf';

// Start server + add functionalities
const app = express()
const port = 3000
app.use(bodyParser.urlencoded({extended: true}))
app.use(bodyParser.json())