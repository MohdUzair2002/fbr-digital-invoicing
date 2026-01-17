import streamlit as st
import zipfile
import sqlite3
import json
import requests
import bcrypt
from datetime import datetime, date
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
from openpyxl import load_workbook

import base64
import time
from functools import lru_cache

# PDF header utilities for QR and logo
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader


# Enhanced CSS Styling with Stunning Dark Theme
def load_css():
    st.markdown(
        """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        --error-gradient: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        --dark-bg: #0f172a;
        --dark-card: #1e293b;
        --dark-card-hover: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --border-color: #475569;
        --shadow-color: rgba(0, 0, 0, 0.3);
    }
    
    /* Main App Styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
        background: var(--dark-bg);
    }
    
    /* Stunning Header with Glassmorphism */
    .custom-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        backdrop-filter: blur(20px);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .custom-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    .custom-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-align: center;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        font-family: 'Inter', sans-serif;
    }
    
    .custom-header p {
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        font-size: 1.2rem;
        margin-top: 1rem;
        font-weight: 400;
    }
    
    /* Stunning Card Styling with Glassmorphism */
    .custom-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
        margin-bottom: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .custom-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .custom-card:hover::before {
        opacity: 1;
    }
    
    /* Stunning Action Cards with Neon Effects */
    .action-card {
        background: linear-gradient(135deg, rgba(240, 147, 251, 0.9) 0%, rgba(245, 87, 108, 0.9) 100%);
        backdrop-filter: blur(20px);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.2);
    }
    
    .action-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .action-card:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 20px 40px rgba(245, 87, 108, 0.4);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    .action-card:hover::before {
        left: 100%;
    }
    
    .action-card h3 {
        margin: 0 0 1rem 0;
        font-size: 1.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .action-card p {
        margin: 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Stunning Stats Cards with Glow Effects */
    .stats-card {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.9) 0%, rgba(0, 242, 254, 0.9) 100%);
        backdrop-filter: blur(20px);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.2);
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(79, 172, 254, 0.3);
    }
    
    .stats-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: rotate 4s linear infinite;
        pointer-events: none;
    }
    
    .stats-number {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        position: relative;
        z-index: 1;
    }
    
    .stats-label {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* Stunning Success/Error Cards */
    .success-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-left: 5px solid #10b981;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .error-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(220, 38, 38, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-left: 5px solid #ef4444;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Enhanced Form Elements */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .stTextArea > div > div {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Stunning Button Enhancements */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Enhanced Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        backdrop-filter: blur(20px);
    }
    
    .css-1d391kg .css-1d391kg {
        color: var(--text-primary);
    }
    
    /* Stunning Navigation Breadcrumb */
    .nav-breadcrumb {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
        backdrop-filter: blur(20px);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        font-size: 0.9rem;
        color: var(--text-secondary);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    /* Enhanced Table Styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Stunning Progress Bar */
    .stProgress > div > div {
        background: var(--primary-gradient);
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        text-align: center;
        border-left: 4px solid #667eea;
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Stunning Upload Zone */
    .uploadedFile {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
    }
    
    /* Stunning Footer */
    .footer {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        backdrop-filter: blur(20px);
        color: white;
        padding: 3rem;
        text-align: center;
        border-radius: 20px;
        margin-top: 3rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Enhanced Animation Classes */
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-up {
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .slideIn {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .shake {
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Loading States */
    .loading {
        position: relative;
        overflow: hidden;
    }
    
    .loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: loading 1.5s infinite;
    }
    
    @keyframes loading {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Enhanced Mobile Responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .custom-header {
            padding: 2rem 1rem;
            margin-bottom: 1rem;
        }
        
        .custom-header h1 {
            font-size: 2rem;
        }
        
        .custom-header p {
            font-size: 1rem;
        }
        
        .custom-card {
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .action-card {
            padding: 1.5rem;
        }
        
        .action-card h3 {
            font-size: 1.2rem;
        }
        
        .stats-card {
            padding: 1.5rem;
        }
        
        .stats-number {
            font-size: 2.5rem;
        }
        
        .stats-label {
            font-size: 0.9rem;
        }
        
        .nav-breadcrumb {
            padding: 1rem;
            font-size: 0.8rem;
        }
        
        .footer {
            padding: 2rem 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .custom-header h1 {
            font-size: 1.5rem;
        }
        
        .custom-card {
            padding: 1rem;
        }
        
        .stats-number {
            font-size: 2rem;
        }
        
        .action-card h3 {
            font-size: 1rem;
        }
    }
    
    /* Stunning Background Pattern */
    .stApp {
        background: var(--dark-bg);
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(79, 172, 254, 0.1) 0%, transparent 50%);
        background-size: 100% 100%, 100% 100%, 100% 100%;
        background-attachment: fixed;
    }
    
    /* Add floating particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(102, 126, 234, 0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(118, 75, 162, 0.3), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(79, 172, 254, 0.3), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(240, 147, 251, 0.3), transparent),
            radial-gradient(2px 2px at 160px 30px, rgba(245, 87, 108, 0.3), transparent);
        background-repeat: repeat;
        background-size: 200px 200px;
        animation: float 20s infinite linear;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        100% { transform: translateY(-100px) rotate(360deg); }
    }
    
    /* Enhanced Header */
    .stApp > header {
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Fix Text Visibility Issues */
    .custom-card h1, .custom-card h2, .custom-card h3, .custom-card h4, .custom-card h5, .custom-card h6 {
        color: var(--text-primary) !important;
    }
    
    .custom-card p, .custom-card span, .custom-card div {
        color: var(--text-primary) !important;
    }
    
    .custom-card strong {
        color: var(--text-primary) !important;
    }
    
    /* Fix Streamlit default text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-primary) !important;
    }
    
    /* Fix form labels */
    .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label, .stDateInput label {
        color: var(--text-primary) !important;
    }
    
    /* Fix sidebar text */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: var(--text-primary) !important;
    }
    
    .css-1d391kg p, .css-1d391kg span, .css-1d391kg div {
        color: var(--text-primary) !important;
    }
    
    /* Fix dataframe text */
    .dataframe th, .dataframe td {
        color: var(--text-primary) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    /* Fix info boxes */
    .stAlert {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-primary) !important;
    }
    
    .stAlert p {
        color: var(--text-primary) !important;
    }
    
    /* Fix expander text */
    .streamlit-expanderHeader {
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent {
        color: var(--text-primary) !important;
    }
    
    /* Fix metric text */
    .metric-container {
        color: var(--text-primary) !important;
    }
    
    .metric-container .metric-value {
        color: var(--text-primary) !important;
    }
    
    .metric-container .metric-label {
        color: var(--text-secondary) !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    /* Fix more Streamlit components */
    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input {
        color: var(--text-primary) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    .stTextArea > div > div > textarea {
        color: var(--text-primary) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    .stNumberInput > div > div > input {
        color: var(--text-primary) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    /* Fix radio buttons */
    .stRadio > div > label {
        color: var(--text-primary) !important;
    }
    
    /* Fix checkboxes */
    .stCheckbox > div > label {
        color: var(--text-primary) !important;
    }
    
    /* Fix file uploader */
    .stFileUploader > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Fix progress bar text */
    .stProgress > div > div > div {
        color: var(--text-primary) !important;
    }
    
    /* Fix tabs */
    .stTabs > div > div > div > button {
        color: var(--text-primary) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    .stTabs > div > div > div > button[aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
    }
    
    /* Additional text visibility fixes */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown p {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown strong {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown ul, .stMarkdown ol {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown li {
        color: var(--text-primary) !important;
    }
    
    /* Fix info and warning boxes */
    .stAlert[data-testid="alert"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-primary) !important;
    }
    
    .stAlert[data-testid="alert"] p {
        color: var(--text-primary) !important;
    }
    
    /* Fix expander content */
    .streamlit-expanderContent p {
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent h1, .streamlit-expanderContent h2, .streamlit-expanderContent h3, 
    .streamlit-expanderContent h4, .streamlit-expanderContent h5, .streamlit-expanderContent h6 {
        color: var(--text-primary) !important;
    }
    
    /* Fix sidebar content */
    .css-1d391kg .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .css-1d391kg .stMarkdown p {
        color: var(--text-primary) !important;
    }
    
    .css-1d391kg .stMarkdown h1, .css-1d391kg .stMarkdown h2, .css-1d391kg .stMarkdown h3, 
    .css-1d391kg .stMarkdown h4, .css-1d391kg .stMarkdown h5, .css-1d391kg .stMarkdown h6 {
        color: var(--text-primary) !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

def validate_invoice_api(invoice_data, bearer_token):
    """Send invoice data to FBR validation API endpoint"""
    try:
        api_url = "https://gw.fbr.gov.pk/di_data/v1/di/validateinvoicedata_sb"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        print(invoice_data)
        response = requests.post(api_url, json=invoice_data, headers=headers)
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


def post_invoice_api(invoice_data, bearer_token):
    """Send invoice data to FBR post API endpoint"""
    try:
        api_url = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        response = requests.post(api_url, json=invoice_data, headers=headers)
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


# Enhanced Components
def create_header(title, subtitle=""):
    st.markdown(
        f"""
    <div class="custom-header fade-in">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_action_card(title, description, icon="🚀"):
    return st.markdown(
        f"""
    <div class="action-card slide-up">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_stats_card(number, label):
    return st.markdown(
        f"""
    <div class="stats-card">
        <p class="stats-number">{number}</p>
        <p class="stats-label">{label}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

def get_seller_count():
    """Get total number of registered sellers"""
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sellers")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def create_success_message(message, details=None):
    """Enhanced success message with optional details"""
    st.markdown(
        f"""
    <div class="success-card" style="animation: slideIn 0.5s ease-out;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.2rem;">✅</span>
            <strong>Success:</strong> {message}
        </div>
        {f'<div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">{details}</div>' if details else ''}
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_error_message(message, details=None, suggestions=None):
    """Enhanced error message with helpful suggestions"""
    suggestions_html = ""
    if suggestions:
        suggestions_html = f"""
        <div style="margin-top: 0.5rem;">
            <strong>💡 Suggestions:</strong>
            <ul style="margin: 0.25rem 0; padding-left: 1.5rem;">
                {''.join([f'<li>{suggestion}</li>' for suggestion in suggestions])}
            </ul>
        </div>
        """
    
    st.markdown(
        f"""
    <div class="error-card" style="animation: shake 0.5s ease-in-out;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.2rem;">❌</span>
            <strong>Error:</strong> {message}
        </div>
        {f'<div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">{details}</div>' if details else ''}
        {suggestions_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_warning_message(message, details=None):
    """Create warning message"""
    st.markdown(
        f"""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-left: 5px solid #f59e0b; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.2rem;">⚠️</span>
            <strong>Warning:</strong> {message}
        </div>
        {f'<div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">{details}</div>' if details else ''}
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_info_message(message, details=None):
    """Create info message"""
    st.markdown(
        f"""
    <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                border-left: 5px solid #3b82f6; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.2rem;">ℹ️</span>
            <strong>Info:</strong> {message}
        </div>
        {f'<div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">{details}</div>' if details else ''}
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_nav_breadcrumb(current_page):
    breadcrumbs = {
        "dashboard": "🏠 Dashboard",
        "invoice_method_selection": "🏠 Dashboard > 🎯 Invoice Method",
        "search_seller": "🏠 Dashboard > 🔍 Search Seller",
        "excel_seller_search": "🏠 Dashboard > 📊 Excel Upload > 🔍 Search Seller",
        "invoice": "🏠 Dashboard > 🧾 Create Invoice",
        "excel_invoice": "🏠 Dashboard > 📊 Excel Processing",
        "update": "🏠 Dashboard > ✏️ Update Seller",
    }

    breadcrumb = breadcrumbs.get(current_page, "🏠 Dashboard")
    
    # Add clickable navigation
    nav_parts = breadcrumb.split(" > ")
    clickable_nav = []
    
    for i, part in enumerate(nav_parts):
        if i == len(nav_parts) - 1:  # Last item (current page)
            clickable_nav.append(f'<span style="color: #667eea; font-weight: bold;">{part}</span>')
        else:
            clickable_nav.append(f'<span style="color: #6b7280;">{part}</span>')
    
    clickable_breadcrumb = " > ".join(clickable_nav)
    
    st.markdown(
        f"""
    <div class="nav-breadcrumb" style="cursor: pointer; padding: 1.5rem; border-radius: 15px; 
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
                backdrop-filter: blur(20px); margin-bottom: 2rem; font-size: 0.9rem; 
                color: var(--text-secondary); border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);">
        <strong>📍 You are here:</strong> {clickable_breadcrumb}
        <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748b;">
            💡 Click any section above to navigate quickly
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Password Authentication (keeping original logic)
# hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())

# Enhanced Password Authentication with dual login
hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())


def check_password():
    """Returns True if the user entered the correct password (admin or guest)."""
    if "password_ok" not in st.session_state:
        st.session_state.password_ok = False
        st.session_state.user_type = None
        st.session_state.guest_seller_id = None
        st.session_state.guest_seller_data = None

    if st.session_state.password_ok:
        return True

    # Enhanced login form with user type selection
    st.markdown(
        """
    <div style="text-align: center; padding: 3rem;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 3rem; border-radius: 20px; color: white; max-width: 500px; 
                    margin: 0 auto; box-shadow: 0 15px 35px rgba(0,0,0,0.2);">
            <h1 style="margin-bottom: 2rem;">🔐 Invoice Management System</h1>
            <p style="opacity: 0.9; margin-bottom: 2rem;">Secure Access Portal</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # User type selection
    st.markdown("### 👤 Select Login Type")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="custom-card" style="text-align: center;">
            <h4>🛡️ Admin Access</h4>
            <p>Full system access including seller management</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="custom-card" style="text-align: center;">
            <h4>👤 Guest Access</h4>
            <p>Invoice creation only with your NTN/CNIC</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    login_type = st.radio(
        "Choose your access level:", ["Admin", "Guest"], horizontal=True
    )

    with st.form("login_form"):
        st.markdown("### 🛡️ Authentication Required")

        if login_type == "Admin":
            pw = st.text_input(
                "🔑 Enter admin password",
                type="password",
                placeholder="Enter admin password",
            )
            submit_label = "🚀 Admin Login"
        else:
            pw = st.text_input(
                "🆔 Enter your NTN/CNIC",
                placeholder="Enter your registered NTN/CNIC number",
            )
            submit_label = "👤 Guest Login"

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button(submit_label, use_container_width=True)

        if submit:
            if login_type == "Admin":
                # Admin login check
                if bcrypt.checkpw(pw.encode(), hashed_pw):
                    st.session_state.password_ok = True
                    st.session_state.user_type = "admin"
                    st.rerun()
                else:
                    create_error_message("Invalid admin password. Please try again.")

            else:
                # Guest login check - validate NTN/CNIC against database
                if pw.strip():
                    conn = sqlite3.connect("sellers.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT * FROM sellers WHERE seller_ntn_cnic = ?", (pw.strip(),)
                    )
                    seller = cursor.fetchone()
                    conn.close()

                    if seller:
                        st.session_state.password_ok = True
                        st.session_state.user_type = "guest"
                        st.session_state.guest_seller_id = seller[0]
                        st.session_state.guest_seller_data = seller
                        create_success_message(
                            f"Welcome {seller[2]}! Guest access granted."
                        )
                        st.rerun()
                    else:
                        create_error_message(
                            "NTN/CNIC not found. Please contact administrator to register your business."
                        )
                else:
                    create_error_message("Please enter your NTN/CNIC number.")

    return False


# Enhanced main dashboard with role-based access
def show_dashboard():
    user_type = st.session_state.get("user_type", "admin")

    if user_type == "guest":
        show_guest_dashboard()
        return

    # Original admin dashboard code (keep existing implementation)
    create_nav_breadcrumb("dashboard")
    create_header(
        "Professional Invoice Management System",
        "Streamlined FBR invoice processing with modern interface",
    )
    
    # Add quick navigation
    create_quick_nav()

    # Statistics Dashboard
    sellers = get_all_sellers()

    st.markdown("### 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_stats_card(len(sellers), "Total Sellers")
    with col2:
        create_stats_card("2", "Processing Methods")
    with col3:
        create_stats_card("100%", "FBR Compliance")
    with col4:
        create_stats_card("24/7", "System Availability")

    # Main Actions
    st.markdown("### 🎯 Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="custom-card" style="height: 200px;">
            <h3>🧾 Create Invoice</h3>
            <p>Generate FBR-compliant invoices using our advanced processing methods</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button(
            "🚀 Start Invoice Creation",
            type="primary",
            use_container_width=True,
            key="admin_invoice_btn",
        ):
            go_to_method_selection()
            st.rerun()

    with col2:
        st.markdown(
            """
        <div class="custom-card" style="height: 200px;">
            <h3>✏️ Update Seller</h3>
            <p>Modify existing seller information and authentication tokens</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button(
            "📝 Update Seller Info", use_container_width=True, key="admin_update_btn"
        ):
            go_to_search_seller("update")
            st.rerun()

    # Seller Registration Sidebar (Admin only)
    with st.sidebar:
        st.markdown("### ➕ Register New Seller")
        
        # Check current seller count
        current_seller_count = get_seller_count()
        max_sellers = 15
        remaining_slots = max_sellers - current_seller_count
        
        # Show capacity status
        if current_seller_count >= max_sellers:
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                        color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                <h4 style="margin: 0;">🚫 Registration Limit Reached</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Maximum {max_sellers} sellers allowed</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.warning(f"⚠️ You have reached the maximum limit of {max_sellers} sellers. Cannot register more sellers.")
        else:
            # Show remaining slots
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                <h4 style="margin: 0;">📊 Registration Capacity</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{remaining_slots} slots remaining ({current_seller_count}/{max_sellers})</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
            
            st.markdown("*Add new sellers to the system*")

            with st.form("seller_form"):
                seller_ntn_cnic = st.text_input(
                    "🆔 Seller NTN/CNIC", placeholder="Enter NTN or CNIC"
                )
                seller_business_name = st.text_input(
                    "🏢 Business Name", placeholder="Enter business name"
                )
                seller_province = st.selectbox(
                    "🌍 Province",
                    [
                        "",
                        "Sindh",
                        "Punjab",
                        "Khyber Pakhtunkhwa",
                        "Balochistan",
                        "Gilgit-Baltistan",
                        "Azad Kashmir",
                        "Islamabad Capital Territory",
                    ],
                )
                seller_address = st.text_area(
                    "📍 Address", placeholder="Enter complete address"
                )
                seller_address=seller_address
                bearer_token = st.text_input(
                    "🔑 Bearer Token", placeholder="Enter API bearer token", type="password"
                )

                submitted = st.form_submit_button(
                    "💾 Register Seller", use_container_width=True
                )

                if submitted:
                    # Double-check limit before registration
                    if get_seller_count() >= max_sellers:
                        create_error_message(
                            f"Registration failed: Maximum limit of {max_sellers} sellers reached",
                            details="Please contact the system administrator if you need to register more sellers."
                        )
                    elif (
                        seller_ntn_cnic
                        and seller_business_name
                        and seller_province
                        and seller_address
                        and bearer_token
                    ):
                        seller_data = {
                            "seller_ntn_cnic": seller_ntn_cnic,
                            "seller_business_name": seller_business_name,
                            "seller_province": seller_province,
                            "seller_address": seller_address,
                            "bearer_token": bearer_token,
                        }

                        seller_id = save_seller(seller_data)
                        create_success_message(
                            f"Seller registered successfully! ID: {seller_id}",
                            details=f"Remaining slots: {max_sellers - get_seller_count()}/{max_sellers}"
                        )
                        st.rerun()
                    else:
                        create_error_message("Please fill all required fields")

        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown(
            """
        <div style="height: 100px;"/>
        """,
            unsafe_allow_html=True,
        )

    # Sellers Table (existing code)
    st.markdown("### 📋 Registered Sellers")

    if sellers:
        df_data = []
        for seller in sellers:
            df_data.append(
                {
                    "ID": seller[0],
                    "NTN/CNIC": seller[1],
                    "Business Name": seller[2],
                    "Province": seller[3],
                    "Address": (
                        seller[4][:50] + "..." if len(seller[4]) > 50 else seller[4]
                    ),
                    "Created": seller[6] if len(seller) > 6 else "N/A",
                }
            )

        df = pd.DataFrame(df_data)

        

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "NTN/CNIC": st.column_config.TextColumn("NTN/CNIC", width="medium"),
                "Business Name": st.column_config.TextColumn(
                    "Business Name", width="large"
                ),
                "Province": st.column_config.TextColumn("Province", width="medium"),
                "Address": st.column_config.TextColumn("Address", width="large"),
                "Created": st.column_config.TextColumn("Created", width="medium"),
            },
        )

        st.markdown("</div>", unsafe_allow_html=True)
        st.info(
            "💡 Use the Quick Actions above to create invoices or update seller information"
        )
    else:
        st.markdown(
            """
        <div class="custom-card" style="text-align: center; padding: 3rem;">
            <h3>📝 No Sellers Registered</h3>
            <p>Get started by registering your first seller using the sidebar form</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# New Guest Dashboard
def show_guest_dashboard():
    guest_seller = st.session_state.guest_seller_data

    create_nav_breadcrumb("dashboard")
    create_header(f"Welcome {guest_seller[2]}", "Guest Invoice Creation Portal")

    # Guest info display
    st.markdown(
        f"""
    <div class="success-card">
        <h4>👤 Your Business Information</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem;">
            <div><strong>Business Name:</strong> {guest_seller[2]}</div>
            <div><strong>NTN/CNIC:</strong> {guest_seller[1]}</div>
            <div><strong>Province:</strong> {guest_seller[3]}</div>
        </div>
        <div style="margin-top: 1rem;">
            <strong>Address:</strong> {guest_seller[4]}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Guest actions (invoice creation only)
    st.markdown("### 🎯 Available Actions")

    st.markdown(
        """
    <div class="custom-card" style="text-align: center;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🧾</div>
        <h3>Create Invoice</h3>
        <p>Generate FBR-compliant invoices for your business</p>
        <p style="color: #6b7280; font-size: 0.9rem;">Choose between manual form entry or bulk Excel processing</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🚀 Start Invoice Creation",
        type="primary",
        use_container_width=True,
        key="guest_invoice_btn",
    ):
        go_to_method_selection()
        st.rerun()

    # Guest sidebar
    with st.sidebar:
        st.markdown("### 👤 Guest Session")
        st.markdown(f"**Logged in as:** {guest_seller[2]}")
        st.markdown(f"**NTN/CNIC:** {guest_seller[1]}")

        st.markdown("---")
        st.markdown("### ℹ️ Guest Limitations")
        st.info(
            "As a guest user, you can:\n- Create invoices\n- Use form and Excel methods\n- Download PDFs\n\nFor administrative access, contact the system administrator."
        )

        if st.button(
            "🚪 Logout", use_container_width=True, type="secondary", key="guest_logout"
        ):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# Enhanced search seller for guest users
def show_search_seller():
    user_type = st.session_state.get("user_type", "admin")

    if user_type == "guest":
        # Guest users automatically use their own seller data
        go_to_invoice_page(st.session_state.guest_seller_id)
        st.rerun()
        return

    # Original admin search functionality (keep existing code)
    purpose_title = (
        "Create Invoice"
        if st.session_state.search_purpose == "invoice"
        else "Update Seller"
    )
    create_nav_breadcrumb("search_seller")
    create_header(
        f"Find Seller - {purpose_title}", "Search through registered sellers to proceed"
    )

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("⬅️ Dashboard", use_container_width=True, key="search_dash_btn"):
            go_to_dashboard()
            st.rerun()

    st.markdown("### 🔍 Search Sellers")

    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input(
            "🔎 Search by NTN/CNIC, Business Name, or Province",
            placeholder="Type to search...",
            help="Enter any part of NTN/CNIC, business name, or province",
        )

    with col2:
        st.markdown("<div style='margin-top: 1.8rem;'>", unsafe_allow_html=True)
        search_button = st.button(
            "🔍 Search",
            type="primary",
            disabled=not search_term,
            key="admin_search_btn",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if search_term:
        with st.spinner("🔍 Searching sellers..."):
            sellers = search_sellers(search_term)

        if sellers:
            create_success_message(
                f"Found {len(sellers)} seller(s) matching your criteria"
            )

            st.markdown("### 📋 Search Results")

            for seller in sellers:
                st.markdown(
                    f"""
                <div class="custom-card slide-up">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{seller[2]}</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; color: #6b7280;">
                                <div><strong>NTN/CNIC:</strong> {seller[1]}</div>
                                <div><strong>Province:</strong> {seller[3]}</div>
                            </div>
                            <div style="margin-top: 0.5rem; color: #6b7280;">
                                <strong>Address:</strong> {seller[4][:80]}{'...' if len(seller[4]) > 80 else ''}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                action_label = (
                    "Create Invoice"
                    if st.session_state.search_purpose == "invoice"
                    else "Update Info"
                )
                action_icon = (
                    "🧾" if st.session_state.search_purpose == "invoice" else "✏️"
                )

                if st.button(
                    f"{action_icon} {action_label}",
                    key=f"admin_select_{seller[0]}",
                    use_container_width=True,
                ):
                    if st.session_state.search_purpose == "invoice":
                        go_to_invoice_page(seller[0])
                    else:
                        go_to_update_page(seller[0])
                    st.rerun()

                st.markdown(
                    "<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
            <div class="custom-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">🔍</div>
                <h3>No Results Found</h3>
                <p>No sellers found matching your search criteria. Try different terms or register a new seller.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
        <div class="custom-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔍</div>
            <h3>Enter Search Terms</h3>
            <p>Use the search box above to find sellers by NTN/CNIC, business name, or province</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# Initialize session state for processed invoices
if "processed_invoices" not in st.session_state:
    st.session_state.processed_invoices = []
if "validation_results" not in st.session_state:
    st.session_state.validation_results = []
if "posting_results" not in st.session_state:
    st.session_state.posting_results = []


# Enhanced excel seller search for guest users
def show_excel_seller_search():
    user_type = st.session_state.get("user_type", "admin")

    if user_type == "guest":
        # Guest users automatically use their own seller data for Excel processing
        go_to_excel_invoice(st.session_state.guest_seller_id)
        st.rerun()
        return

    # Original admin functionality (keep existing code)
    create_nav_breadcrumb("excel_seller_search")
    create_header(
        "Excel Processing - Select Seller", "Choose seller for bulk invoice processing"
    )

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button(
            "⬅️ Back to Methods", use_container_width=True, key="excel_back_btn"
        ):
            go_to_method_selection()
            st.rerun()

    st.markdown("### 🔍 Find Seller for Excel Processing")

    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input(
            "🔎 Search by NTN/CNIC, Business Name, or Province",
            placeholder="Type to search...",
            help="Find the seller for bulk Excel processing",
        )

    with col2:
        st.markdown("<div style='margin-top: 1.8rem;'>", unsafe_allow_html=True)
        search_button = st.button(
            "🔍 Search",
            type="primary",
            disabled=not search_term,
            key="excel_search_btn",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if search_term:
        with st.spinner("🔍 Searching sellers..."):
            sellers = search_sellers(search_term)

        if sellers:
            create_success_message(
                f"Found {len(sellers)} seller(s) for Excel processing"
            )

            st.markdown("### 📋 Available Sellers")

            for seller in sellers:
                st.markdown(
                    f"""
                <div class="custom-card slide-up">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{seller[2]}</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; color: #6b7280;">
                                <div><strong>NTN/CNIC:</strong> {seller[1]}</div>
                                <div><strong>Province:</strong> {seller[3]}</div>
                            </div>
                            <div style="margin-top: 0.5rem; color: #6b7280;">
                                <strong>Address:</strong> {seller[4][:80]}{'...' if len(seller[4]) > 80 else ''}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "📊 Start Excel Processing",
                    key=f"excel_process_{seller[0]}",
                    use_container_width=True,
                    type="primary",
                ):
                    go_to_excel_invoice(seller[0])
                    st.rerun()

                st.markdown(
                    "<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
            <div class="custom-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">📊</div>
                <h3>No Sellers Found</h3>
                <p>No sellers found matching your criteria. Please register sellers first or try different search terms.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
        <div class="custom-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3>Excel Bulk Processing</h3>
            <p>Select a seller to begin bulk invoice processing from Excel files</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# PDF Generation Function (keeping original functionality)
def generate_invoice_pdf(invoice_data, fbr_response=None):
    """Generate PDF invoice matching the exact FBR format from sample"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
    )

    # Get styles
    styles = getSampleStyleSheet()

    # Custom styles to match sample PDF exactly
    title_style = ParagraphStyle(
        "CustomTitle",
        fontName="Times-Italic",
        fontSize=16,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor=colors.black,
    )
    

    section_style = ParagraphStyle(
        "SectionHeader",
        fontName="Times-Bold",
        fontSize=12,
        spaceAfter=8,
        spaceBefore=16,
        textColor=colors.black,
        alignment=TA_LEFT,
    )

    # Story elements
    story = []

    # Title - exactly as in sample
    story.append(Paragraph("Sales Tax Invoice", title_style))
    story.append(Spacer(1, 6))

    # Seller Information Section
    story.append(Paragraph("Seller Information", section_style))

    # Clean seller address formatting
    seller_address = invoice_data.get("sellerAddress", "N/A")

    seller_info_data = [
        [
            Paragraph("<b>Business Name</b>", styles["Normal"]),
            Paragraph(invoice_data.get("sellerBusinessName", "N/A"), styles["Normal"]),
        ],
        [
            Paragraph("<b>Registration No.</b>", styles["Normal"]),
            Paragraph(invoice_data.get("sellerNTNCNIC", "N/A"), styles["Normal"]),
        ],
        [
            Paragraph("<b>Address</b>", styles["Normal"]),
            Paragraph(seller_address, styles["Normal"]),
        ],
    ]

    seller_table = Table(seller_info_data, colWidths=[1.5 * inch, 4.5 * inch])
    seller_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    story.append(seller_table)
    story.append(Spacer(1, 12))

    # Buyer Information Section
    story.append(Paragraph("Buyer Information", section_style))

    # Handle buyer registration display
    buyer_display_name = invoice_data.get("buyerBusinessName", "N/A")
    # if invoice_data.get("buyerRegistrationType") == "Unregistered":
    #     buyer_display_name = "Un-Registered"

    buyer_reg_no = invoice_data.get("buyerNTNCNIC", "")
    # if not buyer_reg_no or invoice_data.get("buyerRegistrationType") == "Unregistered":
    #     buyer_reg_no = "9999999"

    buyer_info_data = [
        [
            Paragraph("<b>Business Name</b>", styles["Normal"]),
            Paragraph(buyer_display_name, styles["Normal"]),
        ],
        [
            Paragraph("<b>Registration No.</b>", styles["Normal"]),
            Paragraph(buyer_reg_no, styles["Normal"]),
        ],
        [
            Paragraph("<b>Address</b>", styles["Normal"]),
            Paragraph(invoice_data.get("buyerAddress", "N/A"), styles["Normal"]),
        ],
    ]

    buyer_table = Table(buyer_info_data, colWidths=[1.5 * inch, 4.5 * inch])
    buyer_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    story.append(buyer_table)
    story.append(Spacer(1, 12))

    # Invoice Summary Section
    story.append(Paragraph("Invoice Summary", section_style))

    # Get FBR Invoice No from response if available
    fbr_invoice_no = "Pending"
    if fbr_response and isinstance(fbr_response, dict):
        if "invoiceNumber" in fbr_response:
            fbr_invoice_no = fbr_response["invoiceNumber"]
        elif "data" in fbr_response and fbr_response["data"]:
            fbr_invoice_no = fbr_response["data"].get("invoiceNumber", "Pending")

    summary_info_data = [
        [
            Paragraph("<b>FBR Invoice No.</b>", styles["Normal"]),
            Paragraph(fbr_invoice_no, styles["Normal"]),
        ],
        [
            Paragraph("<b>Date</b>", styles["Normal"]),
            Paragraph(
                invoice_data.get("invoiceDate", date.today().strftime("%Y-%m-%d")),
                styles["Normal"],
            ),
        ],
    ]

    summary_table = Table(summary_info_data, colWidths=[1.5 * inch, 4.5 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Details of Goods Section
    story.append(Paragraph("Details of Goods", title_style))

    # Items table header - exactly as in sample
    items_header = [
        "Description",
        "HS Code",
        "Qty",
        "Value",
        "Rate",
        "Sales Tax",
        "Amount",
    ]
    items_data = [items_header]

    total_value_excluding_st = 0
    total_sales_tax = 0
    total_amount = 0

    for item in invoice_data.get("items", []):
        qty = item.get("quantity", 0)
        value = float(item.get("valueSalesExcludingST", 0))
        rate = item.get("rate", "0")
        sales_tax = float(item.get("salesTaxApplicable", 0))
        amount = float(item.get("totalValues", 0))

        # Format rate exactly as in sample (18%)
        if not str(rate).endswith("%"):
            rate = f"{rate}%"

        # Format description - use "No details" if empty like sample
        description = item.get("productDescription", "No details")
        if not description.strip():
            description = "No details"

        items_data.append(
            [
                description,
                item.get("hsCode", ""),
                str(int(qty)),  # Remove decimal for quantity
                f"{value:,.2f}",  # Format with decimals
                rate,
                f"{sales_tax:,.2f}",  # Format with decimals
                f"{amount:,.2f}",  # Format with decimals
            ]
        )

        total_value_excluding_st += value
        total_sales_tax += sales_tax
        total_amount += amount

    # Create items table with exact column widths to match sample
    items_table = Table(
        items_data,
        colWidths=[
            1.4 * inch,
            0.9 * inch,
            0.5 * inch,
            0.7 * inch,
            0.6 * inch,
            0.8 * inch,
            0.8 * inch,
        ],
    )
    items_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),  # Bold headers
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Description left aligned
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),  # Numbers centered
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(items_table)
    story.append(Spacer(1, 16))

    # Summary totals - exactly as in sample format
    totals_data = [
        ["Value (Excluding Sales Tax)", f"{total_value_excluding_st:,.2f}"],
        ["Sales Tax", f"{total_sales_tax:,.2f}"],
        ["Value (Including Sales Tax)", f"{total_amount:,.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[2.5 * inch, 1.5 * inch])
    totals_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),  # Labels left aligned
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),  # Values right aligned
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.append(totals_table)

    # Header: FBR logo and QR code at top-right
    def draw_header(canvas, doc_obj):
        canvas.saveState()
        try:
            page_width, page_height = A4
            top_y = page_height - (doc_obj.topMargin * 0.5)
            right_x = page_width - doc_obj.rightMargin

            # Try multiple logo paths
            logo_paths = ["fbr_logo.png", "assets/fbr_logo.png"]
            logo_img = None
            for p in logo_paths:
                try:
                    logo_img = ImageReader(p)
                    break
                except Exception:
                    logo_img = None

            logo_width = 90
            logo_height = 36
            current_y = top_y
            if logo_img is not None:
                canvas.drawImage(
                    logo_img,
                    right_x-100- logo_width,
                    current_y-20 - logo_height,
                    width=82,
                    height=80,
                    preserveAspectRatio=True,
                    mask='auto',
                )
            else:
                canvas.setStrokeColor(colors.grey)
                canvas.rect(right_x - logo_width, current_y - logo_height, logo_width, logo_height, stroke=1, fill=0)
                canvas.setFont("Times-Bold", 10)
                canvas.drawRightString(right_x - 6, current_y - logo_height/2, "FBR")

            current_y = current_y - (logo_height + 8)

            # QR code value: prefer FBR invoice number; fallback to invoiceRefNo
            qr_value = fbr_invoice_no if fbr_invoice_no and fbr_invoice_no != "Pending" else str(invoice_data.get("invoiceRefNo", "N/A"))
            qr_size = 90
            qr_widget = qr.QrCodeWidget(qr_value)
            bounds = qr_widget.getBounds()
            width = (bounds[2] - bounds[0]) or 1.0
            height = (bounds[3] - bounds[1]) or 1.0
            sx = qr_size / width
            sy = (qr_size / height)
            drawing = Drawing(qr_size, qr_size, transform=[sx, 0, 0, sy, 0, 0])
            drawing.add(qr_widget)
            renderPDF.draw(drawing, canvas, right_x - qr_size, current_y - qr_size+70)

            canvas.setFont("Times-Roman", 8)
            caption = f"FBR Inv#: {fbr_invoice_no}" if fbr_invoice_no and fbr_invoice_no != "Pending" else f"Ref#: {invoice_data.get('invoiceRefNo', '')}"
            canvas.drawRightString(right_x-10, current_y - qr_size +70, caption)
        finally:
            canvas.restoreState()

    # Build PDF with header on all pages
    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buffer.seek(0)
    return buffer

# API call functions (keeping original functionality)
def validate_invoice_api(invoice_data, bearer_token):
    """Send invoice data to FBR validation API endpoint"""
    try:
        api_url = "https://gw.fbr.gov.pk/di_data/v1/di/validateinvoicedata_sb"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        print(invoice_data)
        response = requests.post(api_url, json=invoice_data, headers=headers)
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


def post_invoice_api(invoice_data, bearer_token):
    """Send invoice data to FBR post API endpoint"""
    try:
        api_url = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        response = requests.post(api_url, json=invoice_data, headers=headers)
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


# Database setup (keeping original logic)
def init_database():
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sellers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_ntn_cnic TEXT NOT NULL,
            seller_business_name TEXT NOT NULL,
            seller_province TEXT NOT NULL,
            seller_address TEXT NOT NULL,
            bearer_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """CREATE INDEX IF NOT EXISTS idx_seller_ntn_cnic ON sellers(seller_ntn_cnic)"""
    )
    cursor.execute(
        """CREATE INDEX IF NOT EXISTS idx_seller_business_name ON sellers(seller_business_name)"""
    )
    cursor.execute(
        """CREATE INDEX IF NOT EXISTS idx_seller_province ON sellers(seller_province)"""
    )

    conn.commit()
    conn.close()


# Database operations (keeping original functionality)
def save_seller(seller_data):
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sellers (seller_ntn_cnic, seller_business_name, seller_province, seller_address, bearer_token)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            seller_data["seller_ntn_cnic"],
            seller_data["seller_business_name"],
            seller_data["seller_province"],
            seller_data["seller_address"],
            seller_data["bearer_token"],
        ),
    )
    conn.commit()
    seller_id = cursor.lastrowid
    conn.close()
    return seller_id


def update_seller(seller_id, seller_data):
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE sellers 
        SET seller_ntn_cnic = ?, seller_business_name = ?, seller_province = ?, seller_address = ?, bearer_token = ?
        WHERE id = ?
    """,
        (
            seller_data["seller_ntn_cnic"],
            seller_data["seller_business_name"],
            seller_data["seller_province"],
            seller_data["seller_address"],
            seller_data["bearer_token"],
            seller_id,
        ),
    )
    conn.commit()
    conn.close()


def get_all_sellers():
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sellers ORDER BY created_at DESC")
    sellers = cursor.fetchall()
    conn.close()
    return sellers


def get_seller_by_id(seller_id):
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sellers WHERE id = ?", (seller_id,))
    seller = cursor.fetchone()
    conn.close()
    return seller


def search_sellers(search_term):
    conn = sqlite3.connect("sellers.db")
    cursor = conn.cursor()
    search_query = f"%{search_term.lower()}%"
    cursor.execute(
        """
        SELECT * FROM sellers 
        WHERE LOWER(seller_ntn_cnic) LIKE ? 
        OR LOWER(seller_business_name) LIKE ? 
        OR LOWER(seller_province) LIKE ?
        ORDER BY seller_business_name
    """,
        (search_query, search_query, search_query),
    )
    sellers = cursor.fetchall()
    conn.close()
    return sellers


# Initialize database
init_database()

# Streamlit app configuration
st.set_page_config(
    page_title="Professional Invoice Management",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

# Load CSS
load_css()

# Session state management
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_seller_id" not in st.session_state:
    st.session_state.selected_seller_id = None
if "search_purpose" not in st.session_state:
    st.session_state.search_purpose = None
if "invoice_method" not in st.session_state:
    st.session_state.invoice_method = None
if "excel_data" not in st.session_state:
    st.session_state.excel_data = None
if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {}
if "invoices_prepared" not in st.session_state:
    st.session_state.invoices_prepared = []


# Enhanced Navigation functions with better state management
def go_to_dashboard():
    st.session_state.page = "dashboard"
    st.session_state.selected_seller_id = None
    st.session_state.search_purpose = None
    st.session_state.invoice_method = None
    st.session_state.excel_data = None
    st.session_state.column_mapping = {}
    st.session_state.invoices_prepared = []
    st.session_state.processed_invoices = []
    st.session_state.validation_results = []
    st.session_state.posting_results = []

def create_quick_nav():
    """Create stunning quick navigation buttons for better UX"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%); 
                backdrop-filter: blur(20px); padding: 1.5rem; border-radius: 20px; margin-bottom: 2rem;
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <h4 style="color: white; margin: 0; font-size: 1.2rem; font-weight: 600;">🚀 Quick Navigation</h4>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Dashboard", key="quick_dash", use_container_width=True):
            go_to_dashboard()
            st.rerun()
    
    with col2:
        if st.button("🧾 Create Invoice", key="quick_invoice", use_container_width=True):
            go_to_method_selection()
            st.rerun()
    
    with col3:
        if st.button("📊 Excel Upload", key="quick_excel", use_container_width=True):
            go_to_excel_seller_search()
            st.rerun()
    
    with col4:
        if st.button("✏️ Update Seller", key="quick_update", use_container_width=True):
            go_to_search_seller("update")
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def go_to_method_selection():
    st.session_state.page = "invoice_method_selection"


def go_to_search_seller(purpose):
    st.session_state.page = "search_seller"
    st.session_state.search_purpose = purpose


def go_to_excel_seller_search():
    st.session_state.page = "excel_seller_search"


def go_to_invoice_page(seller_id):
    st.session_state.page = "invoice"
    st.session_state.selected_seller_id = seller_id
    # Always start from Step 1 and ensure form state exists
    st.session_state.invoice_step = 0
    if "invoice_form_data" not in st.session_state or not st.session_state.invoice_form_data:
        st.session_state.invoice_form_data = {
            "buyer_ntn_cnic": "",
            "buyer_business_name": "",
            "buyer_province": "",
            "buyer_address": "",
            "buyer_registration_type": "",
            "invoice_type": "Sale Invoice",
            "invoice_date": date.today(),
            "invoice_ref_no": "",
            "scenario_id": "",
            "hs_code": "",
            "product_description": "",
            "rate": "",
            "uom": "",
            "quantity": 1,
            "value_sales_excluding_st": 0.0,
            "sales_tax_applicable": 0.0,
            "further_tax": 0.0,
            "extra_tax": 0.0,
            "sales_tax_withheld": 0.0,
            "fed_payable": 0.0,
            "discount": 0.0,
            "sale_type": "",
            "sro_schedule_no": "",
            "sro_item_serial_no": "",
        }


def go_to_update_page(seller_id):
    st.session_state.page = "update"
    st.session_state.selected_seller_id = seller_id


def go_to_excel_invoice(seller_id):
    st.session_state.page = "excel_invoice"
    st.session_state.selected_seller_id = seller_id


# Auto-detection mapping for common column patterns
# FIXED: Updated COLUMN_MAPPINGS dictionary with better buyer_type detection

COLUMN_MAPPINGS = {
    # Buyer Information
    "buyer_reg_no": [
        "registration no",
        "buyer registration no",
        "buyerntnccnic",
        "buyerNTNCNIC",
        "buyer ntn",
        "buyer cnic",
        "ntn",
        "cnic",
        "registration number",
        "reg no",
        "buyer reg no",
    ],
    "buyer_name": [
        "name",
        "buyer name",
        "buyer business name",
        "business name",
        "buyerbusinessname",
        "customer name",
        "client name",
        "party name",
    ],
    # FIXED: Improved buyer_type detection with more patterns
    "buyer_type": [
        "buyerregistrationtype",
        "buyer registration type",
        "registration type",
        "buyer type",
        "type",
        "reg type",
        "registration status",
        "buyer status",
        "status",
        "unregistered",  # Added these common values
        "registered",
        "un-registered",
        "un registered",
        "registrationtype",
    ],
    "buyer_province": [
        "sale origination province",
        "buyer province",
        "province",
        "buyerprovince",
        "origination province",
        "buyer state",
        "state",
    ],
    "buyer_address": [
        "destination of supply",
        "buyer address",
        "address",
        "buyeraddress",
        "destination",
        "supply destination",
        "delivery address",
    ],
    # Invoice Details
    "invoice_date": [
        "document date",
        "invoice date",
        "date",
        "invoicedate",
        "doc date",
        "transaction date",
        "sale date",
    ],
    "invoice_ref": [
        "document number",
        "invoice reference no",
        "invoice ref no",
        "invoice number",
        "doc number",
        "ref no",
        "reference",
        "invoicerefno",
    ],
    "hs_code": [
        "hs code description",
        "hs code",
        "hscode",
        "commodity code",
        "product code",
        "item code",
    ],
    "product_desc": [
        "product description",
        "description",
        "item description",
        "productdescription",
        "product name",
        "item name",
        "goods description",
    ],
    # Item Values
    "quantity": ["quantity", "qty", "amount", "units", "pieces", "nos"],
    "uom": [
        "uom",
        "unit of measure",
        "unit",
        "measure",
        "units",
        "numbers, pieces, units",
        "kg",
        "pcs",
        "pieces",
    ],
    "rate": [
        "rate",
        "tax rate",
        "st rate",
        "sales tax rate",
        "%",
        "percentage",
        "tax percentage",
    ],
    "scenario_id": [
    "scenarioid",
    "scenario id",
    "scenario_id",
    "scenario",
    "scenario code",
    "fbr scenario",
    "sn code",
    "sn001",
    "sn002",
    "sn003",
],
    "value_excl_st": [
        "value of sales excluding sales tax",
        "value excluding sales tax",
        "value excl st",
        "base value",
        "taxable value",
        "net value",
        "valuesalesexcludingst",
        "amount before tax",
    ],
    "sales_tax": [
        "sales tax/fed in st mode",
        "sales tax",
        "st amount",
        "tax amount",
        "salestaxapplicable",
        "sales tax applicable",
        "tax",
    ],
    # Optional Fields
    "further_tax": ["further tax", "additional tax", "extra tax", "other tax"],
    "discount": ["discount", "rebate", "deduction", "less"],
    "sale_type": [
        "sale type",
        "transaction type",
        "saletype",
        "type of sale",
        "3rd schedule goods",
        "standard",
        "exempt",
    ],
}


# FIXED: Enhanced auto_detect_columns function with debug info
# FIXED: Simpler and more reliable approach

# FIXED: Simpler and more reliable approach

def read_excel_simple_preserve_zeros(uploaded_file):
    """
    Simple approach: Read Excel with pandas using string dtype
    This preserves leading zeros without complex openpyxl logic
    """
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read all sheets with string dtype
        df_dict = pd.read_excel(
            uploaded_file,
            sheet_name=None,
            dtype=str,  # Force all columns as string
            keep_default_na=False,
            na_values=[]
        )
        
        return df_dict
        
    except Exception as e:
        print(f"Error reading Excel: {e}")
        # Fallback: read normally
        uploaded_file.seek(0)
        return pd.read_excel(uploaded_file, sheet_name=None)


def restore_leading_zeros(value, expected_length=None):
    """
    Restore leading zeros ONLY if they were actually lost during Excel import
    NTN can be 7, 13 digits or CNIC can be 13 digits
    Don't pad if already in valid length
    """
    if value is None or value == "":
        return ""
    
    value_str = str(value).strip()
    
    # Valid NTN/CNIC lengths: 7, 13 digits
    valid_lengths = [7, 13]
    
    # If it's all digits and already valid length, keep as-is
    if value_str.isdigit() and len(value_str) in valid_lengths:
        return value_str
    
    # If it's all digits but wrong length, it might have lost leading zeros
    # Pad to 13 digits (most common for CNIC)
    if value_str.isdigit() and len(value_str) < 7:
        # Only pad if very short (definitely lost leading zeros)
        value_str = value_str.zfill(13)
    elif value_str.isdigit() and 7 < len(value_str) < 13:
        # Between 7 and 13, likely lost leading zeros
        value_str = value_str.zfill(13)
    
    return value_str


# FIXED: auto_detect_columns - keep it simple and working
def auto_detect_columns(df_columns):
    """Automatically detect and map Excel columns to required fields"""
    detected_mapping = {}
    df_columns_lower = [str(col).lower().strip() for col in df_columns]
    
    print(f"DEBUG - Available Excel columns: {df_columns}")
    print(f"DEBUG - Lowercase columns: {df_columns_lower}")

    for field_key, possible_names in COLUMN_MAPPINGS.items():
        best_match = None
        best_score = 0

        for col_idx, col_name in enumerate(df_columns_lower):
            for pattern in possible_names:
                pattern_lower = pattern.lower()

                # Exact match gets highest score
                if col_name == pattern_lower:
                    best_match = df_columns[col_idx]
                    best_score = 100
                    print(f"DEBUG - Exact match for {field_key}: '{best_match}'")
                    break

                # Partial match scoring
                if pattern_lower in col_name or col_name in pattern_lower:
                    score = len(set(pattern_lower.split()) & set(col_name.split())) * 10
                    if col_name.startswith(pattern_lower[:5]) or pattern_lower.startswith(col_name[:5]):
                        score += 5

                    if score > best_score:
                        best_match = df_columns[col_idx]
                        best_score = score

            if best_score >= 100:
                break

        if best_match and best_score >= 5:
            detected_mapping[field_key] = best_match
            print(f"DEBUG - Detected {field_key}: '{best_match}' (score: {best_score})")

    print(f"DEBUG - Total detected mappings: {len(detected_mapping)}")
    print(f"DEBUG - Final mapping: {detected_mapping}")
    return detected_mapping


# FIXED: process_excel_row_auto with proper zero handling
def process_excel_row_auto(row, mapping, seller, idx):
    """Process a single Excel row using auto-detected mapping"""
    try:
        # FIXED: Get NTN/CNIC - handle 7 or 13 digit formats
        ntn_col = mapping.get("buyer_reg_no", "")
        buyer_registration_no = ""
        
        if ntn_col:
            ntn_value = row.get(ntn_col, "")
            buyer_registration_no = str(ntn_value).strip() if ntn_value else ""
            
            # Check if it's numeric
            if buyer_registration_no.isdigit():
                current_len = len(buyer_registration_no)
                
                # Valid formats: 7 or 13 digits
                if current_len == 7 or current_len == 13:
                    # Already valid length, keep as-is
                    print(f"DEBUG Row {idx+1}: NTN/CNIC valid length: {current_len} digits")
                elif current_len < 7:
                    # Very short - probably lost leading zeros, pad to 13
                    buyer_registration_no = buyer_registration_no.zfill(13)
                    print(f"DEBUG Row {idx+1}: Restored leading zeros: '{buyer_registration_no}'")
                elif 7 < current_len < 13:
                    # Between 7-13 digits - likely lost leading zeros, pad to 13
                    buyer_registration_no = buyer_registration_no.zfill(13)
                    print(f"DEBUG Row {idx+1}: Padded to 13 digits: '{buyer_registration_no}'")
                else:
                    # More than 13 digits - keep as-is (might be correct)
                    print(f"DEBUG Row {idx+1}: NTN/CNIC is {current_len} digits")
            else:
                # Non-numeric (e.g., "Un-Register"), keep as-is
                print(f"DEBUG Row {idx+1}: Non-numeric NTN/CNIC: '{buyer_registration_no}'")
        
        print(f"DEBUG Row {idx+1}: Final NTN/CNIC = '{buyer_registration_no}' (len: {len(buyer_registration_no)})")
        
        # Extract other buyer info
        buyer_business_name = str(row.get(mapping.get("buyer_name", ""), "")).strip()
        
        # Registration type
        buyer_type_value = row.get(mapping.get("buyer_type", ""), "Unregistered")
        buyer_registration_type = str(buyer_type_value).strip()
        
        # Normalize the registration type
        buyer_registration_type_lower = buyer_registration_type.lower()
        if any(word in buyer_registration_type_lower for word in ["registered", "yes", "true", "1"]):
            buyer_registration_type = "Registered"
        elif any(word in buyer_registration_type_lower for word in ["unregistered", "un-registered", "un registered", "no", "false", "0"]):
            buyer_registration_type = "Unregistered"
        else:
            buyer_registration_type = "Unregistered"
        
        buyer_province_value = str(row.get(mapping.get("buyer_province", ""), "Sindh")).strip()
        buyer_address_value = str(row.get(mapping.get("buyer_address", ""), "N/A")).strip().replace("\n", " ")

        # Invoice details
        invoice_date_value = row.get(mapping.get("invoice_date", ""), date.today())
        if isinstance(invoice_date_value, str):
            try:
                invoice_date_value = pd.to_datetime(invoice_date_value).date()
            except:
                invoice_date_value = date.today()
        elif hasattr(invoice_date_value, "date"):
            invoice_date_value = invoice_date_value.date()

        invoice_ref_no = str(row.get(mapping.get("invoice_ref", ""), f"REF-{idx+1}")).strip()

        # Scenario ID and Item details
        scenario_id = str(row.get(mapping.get("scenario_id", ""), "SN002")).strip()
        if not scenario_id or scenario_id == "":
            scenario_id = "SN002"  # Default fallback
        
        hs_code_value = str(row.get(mapping.get("hs_code", ""), "")).strip()
        product_description = str(row.get(mapping.get("product_desc", ""), "No details")).strip()

        # Safe numeric conversions
        def safe_float_convert(value, default=0.0):
            try:
                if pd.isna(value) or value == "" or value is None:
                    return default
                return float(str(value).replace(",", "").replace("%", "").strip())
            except (ValueError, TypeError):
                return default

        quantity = safe_float_convert(row.get(mapping.get("quantity", ""), 1), 1.0)
        uom_value = str(row.get(mapping.get("uom", ""), "PCS")).strip()

        # Handle rate
        rate_raw = row.get(mapping.get("rate", ""), "18")
        rate_value = str(rate_raw).strip()
        if "%" not in rate_value:
            rate_clean = rate_value.replace("%", "").replace(" ", "")
            try:
                rate_num = float(rate_clean)
                rate_value = f"{rate_num}%"
            except:
                rate_value = "18%"

        value_excluding_st = safe_float_convert(row.get(mapping.get("value_excl_st", ""), 0))
        sales_tax_applicable = safe_float_convert(row.get(mapping.get("sales_tax", ""), 0))
        further_tax = safe_float_convert(row.get(mapping.get("further_tax", ""), 0))
        extra_tax = 0.0
        st_withheld = 0.0
        fed_payable = 0.0
        discount = safe_float_convert(row.get(mapping.get("discount", ""), 0))
        sale_type_value = str(row.get(mapping.get("sale_type", ""), "")).strip()

        # Calculate total
        total_values = (
            value_excluding_st
            + sales_tax_applicable
            + further_tax
            + extra_tax
            - discount
        )

        # Validation
        if value_excluding_st <= 0:
            return None, f"Row {idx+1}: Value excluding ST must be greater than 0"

        if not buyer_business_name:
            return None, f"Row {idx+1}: Buyer name is required"

        # Create invoice data structure
        invoice_data = {
            "sellerNTNCNIC": seller[1],
            "sellerBusinessName": seller[2],
            "sellerProvince": seller[3],
            "sellerAddress": seller[4],
            "invoiceType": "Sale Invoice",
            "invoiceDate": invoice_date_value.strftime("%Y-%m-%d"),
            "buyerNTNCNIC": buyer_registration_no,
            "buyerBusinessName": buyer_business_name,
            "buyerProvince": buyer_province_value,
            "buyerAddress": buyer_address_value,
            "buyerRegistrationType": buyer_registration_type,
            "invoiceRefNo": invoice_ref_no,
            "scenarioId": scenario_id,  # Use dynamic scenario ID from Excel
            "items": [
                {
                    "hsCode": hs_code_value,
                    "productDescription": product_description,
                    "rate": rate_value,
                    "uoM": uom_value,
                    "quantity": quantity,
                    "valueSalesExcludingST": value_excluding_st,
                    "salesTaxApplicable": sales_tax_applicable,
                    "furtherTax": further_tax,
                    "extraTax": extra_tax,
                    "salesTaxWithheldAtSource": st_withheld,
                    "fixedNotifiedValueOrRetailPrice": 0.00,
                    "fedPayable": fed_payable,
                    "discount": discount,
                    "totalValues": total_values,
                    "saleType": sale_type_value,
                    "sroScheduleNo": "",
                    "sroItemSerialNo": "",
                }
            ],
        }

        return {
            "row_number": idx + 1,
            "invoice_data": invoice_data,
            "buyer_name": buyer_business_name,
            "amount": total_values,
        }, None

    except Exception as e:
        print(f"DEBUG Row {idx+1} Error: {str(e)}")
        return None, f"Row {idx+1}: {str(e)}"







# ============================================================================
# UPDATE YOUR show_excel_invoice_auto() FUNCTION
# ============================================================================
# Replace the file reading section with this:


# Enhanced Pages
# def show_dashboard():
#     create_nav_breadcrumb('dashboard')
#     create_header("Professional Invoice Management System", "Streamlined FBR invoice processing with modern interface")

#     # Statistics Dashboard
#     sellers = get_all_sellers()

#     st.markdown("### 📊 System Overview")
#     col1, col2, col3, col4 = st.columns(4)

#     with col1:
#         create_stats_card(len(sellers), "Total Sellers")
#     with col2:
#         create_stats_card("2", "Processing Methods")
#     with col3:
#         create_stats_card("100%", "FBR Compliance")
#     with col4:
#         create_stats_card("24/7", "System Availability")

#     # Main Actions
#     st.markdown("### 🎯 Quick Actions")
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("""
#         <div class="custom-card">
#             <h3>🧾 Create Invoice</h3>
#             <p>Generate FBR-compliant invoices using our advanced processing methods</p>
#         </div>
#         """, unsafe_allow_html=True)
#         if st.button("🚀 Start Invoice Creation", type="primary", use_container_width=True):
#             go_to_method_selection()
#             st.rerun()

#     with col2:
#         st.markdown("""
#         <div class="custom-card">
#             <h3>✏️ Update Seller</h3>
#             <p>Modify existing seller information and authentication tokens</p>
#         </div>
#         """, unsafe_allow_html=True)
#         if st.button("📝 Update Seller Info", use_container_width=True):
#             go_to_search_seller('update')
#             st.rerun()

#     # Seller Registration Sidebar
#     with st.sidebar:
#         st.markdown("### ➕ Register New Seller")
#         st.markdown("*Add new sellers to the system*")

#         with st.form("seller_form"):
#             seller_ntn_cnic = st.text_input("🆔 Seller NTN/CNIC", placeholder="Enter NTN or CNIC")
#             seller_business_name = st.text_input("🏢 Business Name", placeholder="Enter business name")
#             seller_province = st.selectbox("🌍 Province", [
#                 "", "Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan",
#                 "Gilgit-Baltistan", "Azad Kashmir", "Islamabad Capital Territory"
#             ])
#             seller_address = st.text_area("📍 Address", placeholder="Enter complete address")
#             bearer_token = st.text_input("🔑 Bearer Token", placeholder="Enter API bearer token", type="password")

#             submitted = st.form_submit_button("💾 Register Seller", use_container_width=True)

#             if submitted:
#                 if seller_ntn_cnic and seller_business_name and seller_province and seller_address and bearer_token:
#                     seller_data = {
#                         'seller_ntn_cnic': seller_ntn_cnic,
#                         'seller_business_name': seller_business_name,
#                         'seller_province': seller_province,
#                         'seller_address': seller_address,
#                         'bearer_token': bearer_token
#                     }

#                     seller_id = save_seller(seller_data)
#                     create_success_message(f"Seller registered successfully! ID: {seller_id}")
#                     st.rerun()
#                 else:
#                     create_error_message("Please fill all required fields")

#     # Sellers Table
#     st.markdown("### 📋 Registered Sellers")

#     if sellers:
#         # Create enhanced table data
#         df_data = []
#         for seller in sellers:
#             df_data.append({
#                 'ID': seller[0],
#                 'NTN/CNIC': seller[1],
#                 'Business Name': seller[2],
#                 'Province': seller[3],
#                 'Address': seller[4][:50] + '...' if len(seller[4]) > 50 else seller[4],
#                 'Created': seller[6] if len(seller) > 6 else 'N/A'
#             })

#         df = pd.DataFrame(df_data)

#         # Display with enhanced styling
#         st.markdown("""
#         <div class="custom-card">
#         """, unsafe_allow_html=True)

#         st.dataframe(
#             df,
#             use_container_width=True,
#             hide_index=True,
#             column_config={
#                 "ID": st.column_config.NumberColumn("ID", width="small"),
#                 "NTN/CNIC": st.column_config.TextColumn("NTN/CNIC", width="medium"),
#                 "Business Name": st.column_config.TextColumn("Business Name", width="large"),
#                 "Province": st.column_config.TextColumn("Province", width="medium"),
#                 "Address": st.column_config.TextColumn("Address", width="large"),
#                 "Created": st.column_config.TextColumn("Created", width="medium")
#             }
#         )

#         st.markdown("</div>", unsafe_allow_html=True)
#         st.info("💡 Use the Quick Actions above to create invoices or update seller information")
#     else:
#         st.markdown("""
#         <div class="custom-card" style="text-align: center; padding: 3rem;">
#             <h3>📝 No Sellers Registered</h3>
#             <p>Get started by registering your first seller using the sidebar form</p>
#         </div>
#         """, unsafe_allow_html=True)


def show_method_selection():
    create_nav_breadcrumb("invoice_method_selection")
    create_header(
        "Select Invoice Creation Method",
        "Choose the best approach for your invoicing needs",
    )

    # Fixed button positioning with CSS
    st.markdown(
        """
    <style>
    .dashboard-button-container {
        display: flex;
        justify-content: flex-end;
        margin: -1rem 0 2rem 0;
        padding: 0;
    }
    .dashboard-button-container .stButton {
        width: 150px;
    }
    .dashboard-button-container .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .dashboard-button-container .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(239, 68, 68, 0.4);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="dashboard-button-container">', unsafe_allow_html=True)

    # Create columns for button positioning
    _, _, _, col_button = st.columns([2, 2, 1, 1])
    with col_button:
        if st.button("⬅️ Dashboard", key="dash_btn_method"):
            go_to_dashboard()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🎯 Choose Processing Method")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="custom-card" style="height: 600px;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📝</div>
                <h3 style="color: var(--text-primary);">Manual Form Entry</h3>
            </div>
            <div style="background: rgba(30, 41, 59, 0.6); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.1);">
                <h4 style="color: var(--text-primary);">✨ Features:</h4>
                <ul style="margin: 0; padding-left: 1.5rem; color: var(--text-primary);">
                    <li>Step-by-step form filling</li>
                    <li>Real-time validation</li>
                    <li>Single invoice creation</li>
                    <li>Immediate FBR feedback</li>
                    <li>PDF generation</li>
                </ul>
            </div>
            <div style="color: var(--text-secondary);">
                <strong style="color: var(--text-primary);">Best for:</strong> Individual invoices, detailed control, learning the system
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "📝 Use Form Method",
            type="primary",
            use_container_width=True,
            key="form_method_btn",
        ):
            st.session_state.invoice_method = "form"
            go_to_search_seller("invoice")
            st.rerun()

    with col2:
        st.markdown(
            """
        <div class="custom-card" style="height: 600px;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                <h3 style="color: var(--text-primary);">Excel File Upload</h3>
            </div>
            <div style="background: rgba(30, 41, 59, 0.6); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.1);">
                <h4 style="color: var(--text-primary);">🚀 Features:</h4>
                <ul style="margin: 0; padding-left: 1.5rem; color: var(--text-primary);">
                    <li>Bulk invoice processing</li>
                    <li>Smart column detection</li>
                    <li>Multiple invoices at once</li>
                    <li>Batch FBR submission</li>
                    <li>ZIP file PDF output</li>
                </ul>
            </div>
            <div style="color: var(--text-secondary);">
                <strong style="color: var(--text-primary);">Best for:</strong> High volume processing, bulk operations, efficiency
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "📊 Use Excel Method", use_container_width=True, key="excel_method_btn"
        ):
            st.session_state.invoice_method = "excel"
            go_to_excel_seller_search()
            st.rerun()

    # Comparison table
    st.markdown(
        """
        <div style="height: 100px;"/>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 Method Comparison")

    comparison_data = {
        "Feature": [
            "Speed",
            "Volume",
            "Learning Curve",
            "Flexibility",
            "Error Detection",
            "PDF Output",
        ],
        "Manual Form": [
            "Moderate",
            "Single Invoice",
            "Easy",
            "High",
            "Real-time",
            "Individual",
        ],
        "Excel Upload": [
            "Fast",
            "Bulk Processing",
            "Moderate",
            "Moderate",
            "Batch",
            "ZIP Archive",
        ],
    }

    comparison_df = pd.DataFrame(comparison_data)

    # st.markdown("""
    # <div class="custom-card">
    # """, unsafe_allow_html=True)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Feature": st.column_config.TextColumn("Feature", width="medium"),
            "Manual Form": st.column_config.TextColumn(
                "📝 Manual Form", width="medium"
            ),
            "Excel Upload": st.column_config.TextColumn(
                "📊 Excel Upload", width="medium"
            ),
        },
    )

    st.markdown("</div>", unsafe_allow_html=True)


# def show_search_seller():
#     purpose_title = "Create Invoice" if st.session_state.search_purpose == 'invoice' else "Update Seller"
#     create_nav_breadcrumb('search_seller')
#     create_header(f"Find Seller - {purpose_title}", "Search through registered sellers to proceed")

#     col1, col2 = st.columns([5, 1])
#     with col2:
#         if st.button("⬅️ Dashboard", use_container_width=True):
#             go_to_dashboard()
#             st.rerun()

#     st.markdown("### 🔍 Search Sellers")

#     col1, col2 = st.columns([4, 1])
#     with col1:
#         search_term = st.text_input(
#             "🔎 Search by NTN/CNIC, Business Name, or Province",
#             placeholder="Type to search...",
#             help="Enter any part of NTN/CNIC, business name, or province"
#         )

#     with col2:
#         st.markdown("<div style='margin-top: 1.8rem;'>", unsafe_allow_html=True)
#         search_button = st.button("🔍 Search", type="primary", disabled=not search_term)
#         st.markdown("</div>", unsafe_allow_html=True)

#     if search_term:
#         with st.spinner("🔍 Searching sellers..."):
#             sellers = search_sellers(search_term)

#         if sellers:
#             create_success_message(f"Found {len(sellers)} seller(s) matching your criteria")

#             st.markdown("### 📋 Search Results")

#             for seller in sellers:
#                 st.markdown(f"""
#                 <div class="custom-card slide-up">
#                     <div style="display: flex; justify-content: space-between; align-items: center;">
#                         <div style="flex: 1;">
#                             <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{seller[2]}</h4>
#                             <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; color: #6b7280;">
#                                 <div><strong>NTN/CNIC:</strong> {seller[1]}</div>
#                                 <div><strong>Province:</strong> {seller[3]}</div>
#                             </div>
#                             <div style="margin-top: 0.5rem; color: #6b7280;">
#                                 <strong>Address:</strong> {seller[4][:80]}{'...' if len(seller[4]) > 80 else ''}
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#                 """, unsafe_allow_html=True)

#                 action_label = "Create Invoice" if st.session_state.search_purpose == 'invoice' else "Update Info"
#                 action_icon = "🧾" if st.session_state.search_purpose == 'invoice' else "✏️"

#                 if st.button(f"{action_icon} {action_label}", key=f"select_{seller[0]}", use_container_width=True):
#                     if st.session_state.search_purpose == 'invoice':
#                         go_to_invoice_page(seller[0])
#                     else:
#                         go_to_update_page(seller[0])
#                     st.rerun()

#                 st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
#         else:
#             st.markdown("""
#             <div class="custom-card" style="text-align: center; padding: 3rem;">
#                 <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">🔍</div>
#                 <h3>No Results Found</h3>
#                 <p>No sellers found matching your search criteria. Try different terms or register a new seller.</p>
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.markdown("""
#         <div class="custom-card" style="text-align: center; padding: 3rem;">
#             <div style="font-size: 4rem; margin-bottom: 1rem;">🔍</div>
#             <h3>Enter Search Terms</h3>
#             <p>Use the search box above to find sellers by NTN/CNIC, business name, or province</p>
#         </div>
#         """, unsafe_allow_html=True)

# # Initialize session state for processed invoices
# if 'processed_invoices' not in st.session_state:
#     st.session_state.processed_invoices = []
# if 'validation_results' not in st.session_state:
#     st.session_state.validation_results = []
# if 'posting_results' not in st.session_state:
#     st.session_state.posting_results = []

# def show_excel_seller_search():
#     create_nav_breadcrumb('excel_seller_search')
#     create_header("Excel Processing - Select Seller", "Choose seller for bulk invoice processing")

#     col1, col2 = st.columns([5, 1])
#     with col2:
#         if st.button("⬅️ Back to Methods", use_container_width=True):
#             go_to_method_selection()
#             st.rerun()

#     st.markdown("### 🔍 Find Seller for Excel Processing")

#     col1, col2 = st.columns([4, 1])
#     with col1:
#         search_term = st.text_input(
#             "🔎 Search by NTN/CNIC, Business Name, or Province",
#             placeholder="Type to search...",
#             help="Find the seller for bulk Excel processing"
#         )

#     with col2:
#         st.markdown("<div style='margin-top: 1.8rem;'>", unsafe_allow_html=True)
#         search_button = st.button("🔍 Search", type="primary", disabled=not search_term)
#         st.markdown("</div>", unsafe_allow_html=True)

#     if search_term:
#         with st.spinner("🔍 Searching sellers..."):
#             sellers = search_sellers(search_term)

#         if sellers:
#             create_success_message(f"Found {len(sellers)} seller(s) for Excel processing")

#             st.markdown("### 📋 Available Sellers")

#             for seller in sellers:
#                 st.markdown(f"""
#                 <div class="custom-card slide-up">
#                     <div style="display: flex; justify-content: space-between; align-items: center;">
#                         <div style="flex: 1;">
#                             <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{seller[2]}</h4>
#                             <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; color: #6b7280;">
#                                 <div><strong>NTN/CNIC:</strong> {seller[1]}</div>
#                                 <div><strong>Province:</strong> {seller[3]}</div>
#                             </div>
#                             <div style="margin-top: 0.5rem; color: #6b7280;">
#                                 <strong>Address:</strong> {seller[4][:80]}{'...' if len(seller[4]) > 80 else ''}
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#                 """, unsafe_allow_html=True)

#                 if st.button("📊 Start Excel Processing", key=f"excel_{seller[0]}", use_container_width=True, type="primary"):
#                     go_to_excel_invoice(seller[0])
#                     st.rerun()

#                 st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
#         else:
#             st.markdown("""
#             <div class="custom-card" style="text-align: center; padding: 3rem;">
#                 <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">📊</div>
#                 <h3>No Sellers Found</h3>
#                 <p>No sellers found matching your criteria. Please register sellers first or try different search terms.</p>
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.markdown("""
#         <div class="custom-card" style="text-align: center; padding: 3rem;">
#             <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
#             <h3>Excel Bulk Processing</h3>
#             <p>Select a seller to begin bulk invoice processing from Excel files</p>
#         </div>
#         """, unsafe_allow_html=True)


# MAIN APPLICATION LOGIC
def main():
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "invoice_method_selection":
        show_method_selection()
    elif st.session_state.page == "excel_seller_search":
        show_excel_seller_search()
    elif st.session_state.page == "search_seller":
        show_search_seller()
    elif st.session_state.page == "update":
        show_update_seller()
    elif st.session_state.page == "invoice":
        show_invoice_form()
    elif st.session_state.page == "excel_invoice":
        show_excel_invoice_auto()
    else:
        show_dashboard()

    # Professional Footer
    st.markdown(
        """
    <div class="footer">
        <h3>Professional Invoice Management System</h3>
        <p>Streamlined FBR compliance • Advanced processing capabilities • Modern interface</p>
        <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
            Built with Streamlit • Powered by Python • Enhanced UI/UX
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def show_update_seller():
    seller = get_seller_by_id(st.session_state.selected_seller_id)

    if seller:
        create_nav_breadcrumb("update")
        create_header(
            f"Update Seller Information", f"Modifying details for {seller[2]}"
        )

        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("⬅️ Back to Search", use_container_width=True):
                go_to_search_seller("update")
                st.rerun()

        # Current info display
        st.markdown(
            f"""
        <div class="custom-card">
            <h4>📋 Current Information</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin-top: 1rem;">
                <div>
                    <strong>Business Name:</strong><br>
                    <span style="color: #6b7280;">{seller[2]}</span>
                </div>
                <div>
                    <strong>NTN/CNIC:</strong><br>
                    <span style="color: #6b7280;">{seller[1]}</span>
                </div>
                <div>
                    <strong>Province:</strong><br>
                    <span style="color: #6b7280;">{seller[3]}</span>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <strong>Address:</strong><br>
                <span style="color: #6b7280;">{seller[4]}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("### ✏️ Update Information")

        with st.form("update_seller_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                updated_ntn_cnic = st.text_input(
                    "🆔 Seller NTN/CNIC *", value=seller[1]
                )
                updated_business_name = st.text_input(
                    "🏢 Business Name *", value=seller[2]
                )

                provinces = [
                    "",
                    "Sindh",
                    "Punjab",
                    "Khyber Pakhtunkhwa",
                    "Balochistan",
                    "Gilgit-Baltistan",
                    "Azad Kashmir",
                    "Islamabad Capital Territory",
                ]
                current_province_index = 0
                if seller[3] in provinces:
                    current_province_index = provinces.index(seller[3])

                updated_province = st.selectbox(
                    "🌍 Province *", provinces, index=current_province_index
                )

            with col2:
                updated_address = st.text_area(
                    "📍 Address *", value=seller[4], height=100
                )
                updated_bearer_token = st.text_input(
                    "🔑 Bearer Token *", value=seller[5], type="password"
                )

            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                update_submitted = st.form_submit_button(
                    "💾 Update Seller", type="primary", use_container_width=True
                )

            if update_submitted:
                if (
                    updated_ntn_cnic
                    and updated_business_name
                    and updated_province
                    and updated_address
                    and updated_bearer_token
                ):
                    updated_seller_data = {
                        "seller_ntn_cnic": updated_ntn_cnic,
                        "seller_business_name": updated_business_name,
                        "seller_province": updated_province,
                        "seller_address": updated_address,
                        "bearer_token": updated_bearer_token,
                    }

                    update_seller(seller[0], updated_seller_data)
                    create_success_message("Seller information updated successfully!")

                    # Show updated info
                    st.markdown(
                        f"""
                    <div class="success-card">
                        <h4>✅ Updated Information</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                            <div><strong>Business Name:</strong> {updated_business_name}</div>
                            <div><strong>NTN/CNIC:</strong> {updated_ntn_cnic}</div>
                            <div><strong>Province:</strong> {updated_province}</div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    create_error_message("Please fill all required fields")
    else:
        st.error("Seller not found!")
        if st.button("⬅️ Back to Dashboard"):
            go_to_dashboard()
            st.rerun()


def process_invoice_submission(seller, form_data):
    """Process invoice submission with better error handling"""
    try:
        # Create invoice data structure
        invoice_data = {
            "sellerNTNCNIC": seller[1],
            "sellerBusinessName": seller[2],
            "sellerProvince": seller[3],
            "sellerAddress": seller[4],
            "invoiceType": form_data["invoice_type"],
            "invoiceDate": form_data["invoice_date"].strftime("%Y-%m-%d"),
            "buyerNTNCNIC": form_data["buyer_ntn_cnic"] or "9999999",
            "buyerBusinessName": form_data["buyer_business_name"],
            "buyerProvince": form_data["buyer_province"],
            "buyerAddress": form_data["buyer_address"],
            "buyerRegistrationType": form_data["buyer_registration_type"],
            "invoiceRefNo": form_data["invoice_ref_no"],
            "scenarioId": form_data["scenario_id"],
            "items": [
                {
                    "hsCode": form_data["hs_code"],
                    "productDescription": form_data["product_description"],
                    "rate": form_data["rate"],
                    "uoM": form_data["uom"],
                    "quantity": form_data["quantity"],
                    "valueSalesExcludingST": form_data["value_sales_excluding_st"],
                    "salesTaxApplicable": form_data["sales_tax_applicable"],
                    "furtherTax": form_data["further_tax"],
                    "extraTax": form_data["extra_tax"],
                    "salesTaxWithheldAtSource": form_data["sales_tax_withheld"],
                    "fixedNotifiedValueOrRetailPrice": 0.00,
                    "fedPayable": form_data["fed_payable"],
                    "discount": form_data["discount"],
                    "totalValues": (
                        form_data["value_sales_excluding_st"]
                        + form_data["sales_tax_applicable"]
                        + form_data["further_tax"]
                        + form_data["extra_tax"]
                        - form_data["discount"]
                    ),
                    "saleType": form_data["sale_type"],
                    "sroScheduleNo": form_data["sro_schedule_no"],
                    "sroItemSerialNo": form_data["sro_item_serial_no"],
                }
            ],
        }

        # Show processing status
        with st.spinner("🔄 Processing invoice..."):
            # First validate
            status_code, response = validate_invoice_api(invoice_data, seller[5])
            
            if status_code == 200:
                create_success_message("✅ FBR Validation Successful!")
                
                # Then post
                with st.spinner("📤 Posting to FBR..."):
                    status_code, response = post_invoice_api(invoice_data, seller[5])
                    
                    if status_code == 200:
                        create_success_message("🎉 Invoice posted successfully to FBR!")
                        
                        # Generate PDF
                        try:
                            pdf_buffer = generate_invoice_pdf(invoice_data, response)
                            invoice_filename = f"Invoice_{seller[1]}_{form_data['invoice_date'].strftime('%Y-%m-%d')}.pdf"

                            st.download_button(
                                label="📄 Download Invoice PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=invoice_filename,
                                mime="application/pdf",
                                type="secondary",
                            )
                            
                            # Reset form
                            st.session_state.invoice_step = 0
                            st.session_state.invoice_form_data = {}
                            
                        except Exception as e:
                            create_error_message(f"PDF generation failed: {str(e)}")
                    else:
                        create_error_message("❌ FBR posting failed")
                        if response:
                            st.json(response)
            else:
                create_error_message("❌ FBR validation failed")
                if response:
                    st.json(response)
                    
    except Exception as e:
        create_error_message(f"❌ Error processing invoice: {str(e)}")
        st.error("Please check your input and try again.")


# Replace the show_invoice_form() function with this corrected version
# Focus on the initialization and form data handling sections

def show_invoice_form():
    seller = get_seller_by_id(st.session_state.selected_seller_id)

    if seller:
        create_nav_breadcrumb("invoice")
        create_header(f"Create Invoice", f"Manual invoice creation for {seller[2]}")
        
        # Add quick navigation
        create_quick_nav()

        # Check user type to show appropriate back button
        user_type = st.session_state.get("user_type", "admin")

        col1, col2 = st.columns([5, 1])
        with col2:
            if user_type == "guest":
                if st.button(
                    "⬅️ Back", use_container_width=True, key="guest_invoice_back_btn"
                ):
                    go_to_dashboard()
                    st.rerun()
            else:
                if st.button(
                    "⬅️ Back to Search",
                    use_container_width=True,
                    key="admin_invoice_back_btn",
                ):
                    go_to_search_seller("invoice")
                    st.rerun()

        # Seller info display
        st.markdown(
            f"""
        <div class="success-card">
            <h4>🏢 Selected Seller</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem;">
                <div><strong>Name:</strong> {seller[2]}</div>
                <div><strong>NTN/CNIC:</strong> {seller[1]}</div>
                <div><strong>Province:</strong> {seller[3]}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # CRITICAL: Initialize form data with ALL required keys before any access
        if "invoice_form_data" not in st.session_state or not st.session_state.invoice_form_data:
            st.session_state.invoice_form_data = {
                "buyer_ntn_cnic": "",
                "buyer_business_name": "",
                "buyer_province": "",
                "buyer_address": "",
                "buyer_registration_type": "",
                "invoice_type": "Sale Invoice",
                "invoice_date": date.today(),
                "invoice_ref_no": "",
                "scenario_id": "",
                "hs_code": "",
                "product_description": "",
                "rate": "18%",
                "uom": "PCS",
                "quantity": 1,
                "value_sales_excluding_st": 0.0,
                "sales_tax_applicable": 0.0,
                "further_tax": 0.0,
                "extra_tax": 0.0,
                "sales_tax_withheld": 0.0,
                "fed_payable": 0.0,
                "discount": 0.0,
                "sale_type": "",
                "sro_schedule_no": "",
                "sro_item_serial_no": ""
            }

        # Reference the initialized form data
        form_data = st.session_state.invoice_form_data

        # Step-by-step form with progress
        st.markdown("### 📝 Invoice Creation Steps")
        
        # Progress indicator
        steps = ["Buyer Info", "Invoice Details", "Product Items", "Review & Submit"]
        current_step = st.session_state.get("invoice_step", 0)
        
        # Progress bar
        progress = st.progress((current_step + 1) / len(steps))
        st.markdown(f"**Step {current_step + 1} of {len(steps)}: {steps[current_step]}**")

        # Buyer Information
        st.markdown("#### 🛒 Step 1: Buyer Information")
        st.info("💡 Fill in the buyer's details. All fields marked with * are required.")
        
        # Safe access with default values
        invoice_type = st.selectbox(
            "📑 Invoice Type",
            ["Sale Invoice", "Credit Note", "Debit Note"],
            index=["Sale Invoice", "Credit Note", "Debit Note"].index(
                form_data.get("invoice_type", "Sale Invoice")
            ),
            help="Select the type of invoice you are creating",
        )

        invoice_date = st.date_input(
            "📅 Invoice Date", 
            value=form_data.get("invoice_date", date.today()) if isinstance(form_data.get("invoice_date"), date) else date.today()
        )

        invoice_ref_no = st.text_input(
            "🔢 Invoice Reference No *",
            value=form_data.get("invoice_ref_no", ""),
            placeholder="Enter reference number",
            help="Required: Enter your internal invoice reference number",
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            buyer_ntn_cnic = st.text_input(
                "🆔 Buyer NTN/CNIC", 
                value=form_data.get("buyer_ntn_cnic", ""),
                placeholder="Enter buyer NTN/CNIC",
                help="Enter the buyer's NTN or CNIC number"
            )
            buyer_business_name = st.text_input(
                "🏢 Buyer Business Name *", 
                value=form_data.get("buyer_business_name", ""),
                placeholder="Enter business name",
                help="Required: Enter the buyer's business name"
            )
            buyer_province = st.selectbox(
                "🌍 Buyer Province *",
                [
                    "",
                    "Sindh",
                    "Punjab", 
                    "Khyber Pakhtunkhwa",
                    "Balochistan",
                    "Gilgit-Baltistan",
                    "Azad Kashmir",
                    "Islamabad Capital Territory",
                ],
                index=["", "Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan",
                    "Gilgit-Baltistan", "Azad Kashmir", "Islamabad Capital Territory"].index(
                    form_data.get("buyer_province", "")
                ) if form_data.get("buyer_province", "") in ["", "Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan",
                    "Gilgit-Baltistan", "Azad Kashmir", "Islamabad Capital Territory"] else 0
            )
        
        with col2:
            buyer_address = st.text_input(
                "📍 Buyer Address *", 
                value=form_data.get("buyer_address", ""),
                placeholder="Enter buyer address",
                help="Required: Enter the buyer's complete address"
            )
            buyer_registration_type = st.selectbox(
                "📋 Registration Type *", 
                ["", "Unregistered", "Registered"],
                index=["", "Unregistered", "Registered"].index(
                    form_data.get("buyer_registration_type", "")
                ) if form_data.get("buyer_registration_type", "") in ["", "Unregistered", "Registered"] else 0
            )
        
        # Update session state after Step 1
        st.session_state.invoice_form_data.update({
            "buyer_ntn_cnic": buyer_ntn_cnic,
            "buyer_business_name": buyer_business_name,
            "buyer_province": buyer_province,
            "buyer_address": buyer_address,
            "buyer_registration_type": buyer_registration_type,
            "invoice_type": invoice_type,
            "invoice_date": invoice_date,
            "invoice_ref_no": invoice_ref_no,
        })

        # Invoice Information (Step 2)
        st.markdown("#### 📄 Step 2: Invoice Information")
        st.info("💡 Enter the invoice details and reference information.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pass
        
        with col2:
            scenario_id = st.text_input(
                "🎯 Scenario ID *", 
                value=form_data.get("scenario_id", ""),
                placeholder="Enter scenario ID (e.g., SN002)",
                help="Required: Enter the FBR scenario ID (e.g., SN002)"
            )
            sale_type = st.text_input(
                "🏪 Sale Type",
                value=form_data.get("sale_type", ""),
                placeholder="Optional sale type label"
            )
        
        st.session_state.invoice_form_data.update({
            "scenario_id": scenario_id,
            "sale_type": sale_type,
        })

        # Product Items (Step 3)
        st.markdown("#### 📦 Step 3: Product Items")
        st.info("💡 Enter the product details and pricing information.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hs_code = st.text_input(
                "🏷️ HS Code *", 
                value=form_data.get("hs_code", ""),
                placeholder="Enter HS code",
                help="Required: Enter the Harmonized System code"
            )
            product_description = st.text_input(
                "📝 Product Description *", 
                value=form_data.get("product_description", ""),
                placeholder="Enter product description",
                help="Required: Enter detailed product description"
            )
            rate = st.text_input(
                "📊 Tax Rate *", 
                value=form_data.get("rate", "18%"),
                placeholder="Enter tax rate (e.g., 18%)",
                help="Required: Enter the tax rate percentage"
            )
            uom = st.text_input(
                "📏 Unit of Measure *", 
                value=form_data.get("uom", "PCS"),
                placeholder="Enter unit of measure",
                help="Required: Enter unit of measure (e.g., PCS, KG, LTR)"
            )
        
        with col2:
            quantity = st.number_input(
                "🔢 Quantity *", 
                min_value=1, 
                value=int(form_data.get("quantity", 1)),
                help="Required: Enter the quantity"
            )
            value_sales_excluding_st = st.number_input(
                "💰 Value (Excluding Sales Tax) *", 
                min_value=0.0, 
                value=float(form_data.get("value_sales_excluding_st", 0.0)),
                help="Required: Enter the value excluding sales tax"
            )
            sales_tax_applicable = st.number_input(
                "🏛️ Sales Tax Applicable", 
                min_value=0.0, 
                value=float(form_data.get("sales_tax_applicable", 0.0))
            )
            further_tax = st.number_input(
                "➕ Further Tax", 
                min_value=0.0, 
                value=float(form_data.get("further_tax", 0.0))
            )
        
        # Additional fields
        col3, col4 = st.columns(2)
        with col3:
            extra_tax = st.number_input("📈 Extra Tax", min_value=0.0, value=float(form_data.get("extra_tax", 0.0)))
            sales_tax_withheld = st.number_input("⚖️ Sales Tax Withheld at Source", min_value=0.0, value=float(form_data.get("sales_tax_withheld", 0.0)))
            fed_payable = st.number_input("🏦 FED Payable", min_value=0.0, value=float(form_data.get("fed_payable", 0.0)))
        
        with col4:
            discount = st.number_input("💸 Discount", min_value=0.0, value=float(form_data.get("discount", 0.0)))
            sale_type_item = st.text_input("🏪 Sale Type", value=form_data.get("sale_type", ""), placeholder="Enter sale type")
            sro_schedule_no = st.text_input("📋 SRO Schedule No", value=form_data.get("sro_schedule_no", ""), placeholder="Enter SRO schedule number")
        
        sro_item_serial_no = st.text_input("🔢 SRO Item Serial No", value=form_data.get("sro_item_serial_no", ""), placeholder="Enter SRO item serial number")
        
        # Calculate total
        total_values = float(
            value_sales_excluding_st
            + sales_tax_applicable
            + further_tax
            + extra_tax
            - discount
        )
        
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
            <h3 style="margin: 0;">💰 Total Invoice Value</h3>
            <h2 style="margin: 0.5rem 0 0 0;">₨ {total_values:,.2f}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Update session state with product info
        st.session_state.invoice_form_data.update({
            "hs_code": hs_code,
            "product_description": product_description,
            "rate": rate,
            "uom": uom,
            "quantity": quantity,
            "value_sales_excluding_st": value_sales_excluding_st,
            "sales_tax_applicable": sales_tax_applicable,
            "further_tax": further_tax,
            "extra_tax": extra_tax,
            "sales_tax_withheld": sales_tax_withheld,
            "fed_payable": fed_payable,
            "discount": discount,
            "sale_type": sale_type_item,
            "sro_schedule_no": sro_schedule_no,
            "sro_item_serial_no": sro_item_serial_no
        })

        # Review and Submit (Step 4)
        st.markdown("#### ✅ Step 4: Review & Submit")
        st.info("💡 Review all information before submitting to FBR.")
        
        # Get latest form data
        form_data = st.session_state.invoice_form_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🛒 Buyer Information:**")
            st.write(f"• **Name:** {form_data.get('buyer_business_name', 'N/A')}")
            st.write(f"• **NTN/CNIC:** {form_data.get('buyer_ntn_cnic', 'N/A') or 'N/A'}")
            st.write(f"• **Province:** {form_data.get('buyer_province', 'N/A')}")
            st.write(f"• **Address:** {form_data.get('buyer_address', 'N/A')}")
            st.write(f"• **Type:** {form_data.get('buyer_registration_type', 'N/A')}")
            
            st.markdown("**📄 Invoice Information:**")
            st.write(f"• **Type:** {form_data.get('invoice_type', 'N/A')}")
            st.write(f"• **Date:** {form_data.get('invoice_date', 'N/A')}")
            st.write(f"• **Reference:** {form_data.get('invoice_ref_no', 'N/A')}")
            st.write(f"• **Scenario:** {form_data.get('scenario_id', 'N/A')}")
        
        with col2:
            st.markdown("**📦 Product Details:**")
            st.write(f"• **HS Code:** {form_data.get('hs_code', 'N/A')}")
            st.write(f"• **Description:** {form_data.get('product_description', 'N/A')}")
            st.write(f"• **Rate:** {form_data.get('rate', 'N/A')}")
            st.write(f"• **UOM:** {form_data.get('uom', 'N/A')}")
            st.write(f"• **Quantity:** {form_data.get('quantity', 'N/A')}")
            st.write(f"• **Value:** ₨ {form_data.get('value_sales_excluding_st', 0.0):,.2f}")
            
            st.markdown(f"**💰 Total Amount:** ₨ {total_values:,.2f}")

        # Action buttons
        st.markdown("### 🚀 Invoice Actions")

        col5, col6 = st.columns(2)

        with col5:
            if st.button(
                "✅ Validate Invoice", use_container_width=True, type="secondary"
            ):
                # Create invoice data structure from latest form data
                form_data = st.session_state.invoice_form_data
                
                invoice_data = {
                    "sellerNTNCNIC": seller[1],
                    "sellerBusinessName": seller[2],
                    "sellerProvince": seller[3],
                    "sellerAddress": seller[4],
                    "invoiceType": form_data.get("invoice_type", "Sale Invoice"),
                    "invoiceDate": form_data.get("invoice_date", date.today()).strftime("%Y-%m-%d"),
                    "buyerNTNCNIC": form_data.get("buyer_ntn_cnic", ""),
                    "buyerBusinessName": form_data.get("buyer_business_name", ""),
                    "buyerProvince": form_data.get("buyer_province", ""),
                    "buyerAddress": form_data.get("buyer_address", ""),
                    "buyerRegistrationType": form_data.get("buyer_registration_type", ""),
                    "invoiceRefNo": form_data.get("invoice_ref_no", ""),
                    "scenarioId": form_data.get("scenario_id", ""),
                    "items": [
                        {
                            "hsCode": form_data.get("hs_code", ""),
                            "productDescription": form_data.get("product_description", ""),
                            "rate": form_data.get("rate", ""),
                            "uoM": form_data.get("uom", ""),
                            "quantity": form_data.get("quantity", 1),
                            "valueSalesExcludingST": form_data.get("value_sales_excluding_st", 0.0),
                            "salesTaxApplicable": form_data.get("sales_tax_applicable", 0.0),
                            "furtherTax": form_data.get("further_tax", 0.0),
                            "extraTax": form_data.get("extra_tax", 0.0),
                            "salesTaxWithheldAtSource": form_data.get("sales_tax_withheld", 0.0),
                            "fixedNotifiedValueOrRetailPrice": 0.00,
                            "fedPayable": form_data.get("fed_payable", 0.0),
                            "discount": form_data.get("discount", 0.0),
                            "totalValues": total_values,
                            "saleType": form_data.get("sale_type", ""),
                            "sroScheduleNo": form_data.get("sro_schedule_no", ""),
                            "sroItemSerialNo": form_data.get("sro_item_serial_no", ""),
                        }
                    ],
                }

                # Local validation
                errors = []
                required_fields = [
                    (form_data.get("buyer_business_name"), "Buyer Business Name"),
                    (form_data.get("buyer_province"), "Buyer Province"),
                    (form_data.get("buyer_address"), "Buyer Address"),
                    (form_data.get("buyer_registration_type"), "Buyer Registration Type"),
                    (form_data.get("scenario_id"), "Scenario ID"),
                    (form_data.get("hs_code"), "HS Code"),
                    (form_data.get("product_description"), "Product Description"),
                    (form_data.get("rate"), "Tax Rate"),
                    (form_data.get("uom"), "Unit of Measure"),
                ]

                for field_value, field_name in required_fields:
                    if not field_value:
                        errors.append(f"{field_name} is required")

                if form_data.get("value_sales_excluding_st", 0.0) <= 0:
                    errors.append("Value (Excluding Sales Tax) must be greater than 0")

                if errors:
                    st.markdown(
                        """
                    <div class="error-card">
                        <h4>❌ Validation Failed</h4>
                        <ul style="margin: 0.5rem 0;">
                    """,
                        unsafe_allow_html=True,
                    )
                    for error in errors:
                        st.markdown(f"<li>{error}</li>", unsafe_allow_html=True)
                    st.markdown("</ul></div>", unsafe_allow_html=True)
                else:
                    # Call FBR validation API
                    with st.spinner("🔄 Validating with FBR API..."):
                        status_code, response = validate_invoice_api(
                            invoice_data, seller[5]
                        )

                        if status_code == 200:
                            create_success_message("✅ FBR Validation Successful!")
                            
                            st.session_state.validated_invoice_data = invoice_data
                            st.session_state.validated_invoice_response = response
                            
                            st.json(response)
                            
                            st.markdown("### 📄 Invoice PDF")
                            try:
                                pdf_buffer = generate_invoice_pdf(invoice_data, response)
                                invoice_filename = f"Invoice_{seller[1]}_{form_data.get('invoice_date', date.today()).strftime('%Y-%m-%d')}.pdf"

                                st.download_button(
                                    label="📄 Download Invoice PDF",
                                    data=pdf_buffer.getvalue(),
                                    file_name=invoice_filename,
                                    mime="application/pdf",
                                    type="secondary",
                                    key="validate_pdf_download"
                                )
                                
                                create_success_message(
                                    "PDF generated successfully! You can download it above or proceed to post to FBR."
                                )
                                
                            except Exception as e:
                                create_error_message(f"PDF generation failed: {str(e)}")
                            
                        else:
                            create_error_message("❌ FBR Validation Failed")
                            if response:
                                st.json(response)

        with col6:
            if st.button("📤 Post to FBR", use_container_width=True, type="primary"):
                form_data = st.session_state.invoice_form_data
                
                if hasattr(st.session_state, 'validated_invoice_data'):
                    invoice_data = st.session_state.validated_invoice_data
                else:
                    invoice_data = {
                        "sellerNTNCNIC": seller[1],
                        "sellerBusinessName": seller[2],
                        "sellerProvince": seller[3],
                        "sellerAddress": seller[4],
                        "invoiceType": form_data.get("invoice_type", "Sale Invoice"),
                        "invoiceDate": form_data.get("invoice_date", date.today()).strftime("%Y-%m-%d"),
                        "buyerNTNCNIC": form_data.get("buyer_ntn_cnic", ""),
                        "buyerBusinessName": form_data.get("buyer_business_name", ""),
                        "buyerProvince": form_data.get("buyer_province", ""),
                        "buyerAddress": form_data.get("buyer_address", ""),
                        "buyerRegistrationType": form_data.get("buyer_registration_type", ""),
                        "invoiceRefNo": form_data.get("invoice_ref_no", ""),
                        "scenarioId": form_data.get("scenario_id", ""),
                        "items": [
                            {
                                "hsCode": form_data.get("hs_code", ""),
                                "productDescription": form_data.get("product_description", ""),
                                "rate": form_data.get("rate", ""),
                                "uoM": form_data.get("uom", ""),
                                "quantity": form_data.get("quantity", 1),
                                "valueSalesExcludingST": form_data.get("value_sales_excluding_st", 0.0),
                                "salesTaxApplicable": form_data.get("sales_tax_applicable", 0.0),
                                "furtherTax": form_data.get("further_tax", 0.0),
                                "extraTax": form_data.get("extra_tax", 0.0),
                                "salesTaxWithheldAtSource": form_data.get("sales_tax_withheld", 0.0),
                                "fixedNotifiedValueOrRetailPrice": 0.00,
                                "fedPayable": form_data.get("fed_payable", 0.0),
                                "discount": form_data.get("discount", 0.0),
                                "totalValues": total_values,
                                "saleType": form_data.get("sale_type", ""),
                                "sroScheduleNo": form_data.get("sro_schedule_no", ""),
                                "sroItemSerialNo": form_data.get("sro_item_serial_no", ""),
                            }
                        ],
                    }

                required_fields = [
                    form_data.get("buyer_business_name"),
                    form_data.get("buyer_province"),
                    form_data.get("buyer_address"),
                    form_data.get("buyer_registration_type"),
                    form_data.get("scenario_id"),
                    form_data.get("hs_code"),
                    form_data.get("product_description"),
                    form_data.get("rate"),
                    form_data.get("uom"),
                ]

                if not all(required_fields) or form_data.get("value_sales_excluding_st", 0.0) <= 0:
                    create_error_message(
                        "Cannot post: Please validate the form first and fix all errors!"
                    )
                else:
                    with st.spinner("📤 Posting to FBR API..."):
                        status_code, response = post_invoice_api(
                            invoice_data, seller[5]
                        )

                        if status_code == 200:
                            create_success_message(
                                "✅ Invoice posted successfully to FBR!"
                            )
                            st.json(response)
                            
                            try:
                                pdf_buffer = generate_invoice_pdf(invoice_data, response)
                                invoice_filename = f"Invoice_Posted_{seller[1]}_{form_data.get('invoice_date', date.today()).strftime('%Y-%m-%d')}.pdf"

                                st.download_button(
                                    label="📄 Download Updated Invoice PDF (with FBR Data)",
                                    data=pdf_buffer.getvalue(),
                                    file_name=invoice_filename,
                                    mime="application/pdf",
                                    type="secondary",
                                    key="post_pdf_download"
                                )
                                
                                create_success_message(
                                    "Updated PDF with FBR confirmation generated!"
                                )

                            except Exception as e:
                                create_error_message(f"PDF generation failed: {str(e)}")
                            
                            # Reset form for next invoice
                            st.session_state.invoice_step = 0
                            st.session_state.invoice_form_data = {}

                        else:
                            create_error_message("❌ FBR post failed")
                            if response:
                                st.json(response)
    
    else:
        st.error("Seller not found!")
        if st.button("⬅️ Back to Dashboard"):
            go_to_dashboard()
            st.rerun()


def show_excel_invoice_auto():
    seller = get_seller_by_id(st.session_state.selected_seller_id)

    if not seller:
        st.error("Seller not found!")
        if st.button("⬅️ Back to Dashboard"):
            go_to_dashboard()
            st.rerun()
        return

    create_nav_breadcrumb("excel_invoice")
    create_header("Smart Excel Processing", f"Bulk invoice processing for {seller[2]}")

    # Check user type to show appropriate back button
    user_type = st.session_state.get("user_type", "admin")

    col1, col2 = st.columns([5, 1])
    with col2:
        if user_type == "guest":
            # Guest users go back to dashboard
            if st.button(
                "⬅️ Back", use_container_width=True, key="guest_excel_back_btn"
            ):
                go_to_dashboard()
                st.rerun()
        else:
            # Admin users go back to excel seller search
            if st.button(
                "⬅️ Back to Search", use_container_width=True, key="admin_excel_back_btn"
            ):
                go_to_excel_seller_search()
                st.rerun()

    # Display seller info
    st.markdown(
        f"""
    <div class="success-card">
        <h4>🏢 Processing for Seller</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem;">
            <div><strong>Name:</strong> {seller[2]}</div>
            <div><strong>NTN/CNIC:</strong> {seller[1]}</div>
            <div><strong>Province:</strong> {seller[3]}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Excel upload section
    st.markdown("### 📁 Smart Excel File Processing")

    st.markdown(
        """
    <div class="custom-card">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: var(--text-primary);">Auto-Detection Enabled</h3>
            <p style="color: var(--text-primary);">The system will automatically detect and map your Excel columns!</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "📂 Choose Excel file (.xlsx or .xls)",
        type=["xlsx", "xls"],
        help="Upload your Excel file with invoice data for automatic processing",
    )

    if uploaded_file is not None:
        try:
            # FIXED: Use simple string-based reading
            df_dict = read_excel_simple_preserve_zeros(uploaded_file)
            
            # Find main data sheet
            main_df = None
            sheet_name = None

            if isinstance(df_dict, dict):
                for name, sheet_df in df_dict.items():
                    if len(sheet_df) > 0:
                        cols_lower = [str(col).lower() for col in sheet_df.columns]
                        if any(
                            keyword in " ".join(cols_lower)
                            for keyword in [
                                "buyer",
                                "invoice",
                                "registration",
                                "name",
                                "amount",
                                "value",
                                "tax",
                            ]
                        ):
                            sheet_name = name
                            main_df = sheet_df
                            break

                if main_df is None:
                    for name, sheet_df in df_dict.items():
                        if len(sheet_df) > 0:
                            sheet_name = name
                            main_df = sheet_df
                            break
            else:
                main_df = df_dict
                sheet_name = "Main Sheet"

            if main_df is None or len(main_df) == 0:
                create_error_message("No data found in the Excel file")
                return

            create_success_message(
                f"File uploaded successfully! Found {len(main_df)} rows"
            )
            if sheet_name:
                st.info(f"📋 Using sheet: **{sheet_name}**")

            # Clean column names
            main_df.columns = [str(col).strip() for col in main_df.columns]
            
            # IMPORTANT: Keep data as strings for auto-detection
            main_df = main_df.astype(str)

            # Auto-detect columns
            st.markdown("### 🤖 Auto-Detection Results")
            with st.spinner("🔍 Analyzing your Excel columns..."):
                detected_mapping = auto_detect_columns(main_df.columns)

            if detected_mapping:
                create_success_message(
                    f"Automatically detected {len(detected_mapping)} column mappings!"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(
                        """
                        <div class="custom-card">
                            <h4 style="color: var(--text-primary);">🎯 Detected Mappings</h4>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    for field_key, excel_col in detected_mapping.items():
                        field_display = field_key.replace("_", " ").title()
                        st.markdown(f"**{field_display}:** {excel_col}")

                with col2:
                    st.markdown(
                        """
                        <div class="custom-card">
                            <h4 style="color: var(--text-primary);">📊 Detection Status</h4>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    required_fields = [
                        "buyer_name",
                        "hs_code",
                        "product_desc",
                        "value_excl_st",
                    ]
                    detected_required = [
                        field for field in required_fields if field in detected_mapping
                    ]

                    create_stats_card(
                        f"{len(detected_required)}/4", "Required Fields Detected"
                    )

                    if len(detected_required) < 4:
                        missing = [
                            field.replace("_", " ").title()
                            for field in required_fields
                            if field not in detected_mapping
                        ]
                        st.warning(f"⚠️ Missing: {', '.join(missing)}")
            else:
                st.markdown(
                    """
                <div class="custom-card" style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                    <h3>Auto-Detection Issue</h3>
                    <p>Could not auto-detect column mappings. Please check your Excel format.</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Show data preview
            st.markdown("### 📋 Data Preview")
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.dataframe(main_df.head(10), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if len(main_df) > 10:
                st.info(f"Showing first 10 rows. Total rows: {len(main_df)}")

            # Process data button
            if st.button(
                "🚀 Process Excel Data Automatically",
                type="primary",
                use_container_width=True,
            ):
                required_fields = ["buyer_name", "value_excl_st"]
                missing_required = [
                    field
                    for field in required_fields
                    if field not in detected_mapping or not detected_mapping[field]
                ]

                if missing_required:
                    missing_display = [
                        field.replace("_", " ").title() for field in missing_required
                    ]
                    create_error_message(
                        f"Cannot process: Missing required fields: {', '.join(missing_display)}"
                    )
                else:
                    processed_invoices = []
                    processing_errors = []

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for idx, (_, row) in enumerate(main_df.iterrows()):
                        status_text.text(f"Processing row {idx + 1} of {len(main_df)}")
                        progress_bar.progress((idx + 1) / len(main_df))

                        invoice_result, error = process_excel_row_auto(
                            row, detected_mapping, seller, idx
                        )

                        if invoice_result:
                            processed_invoices.append(invoice_result)
                        elif error:
                            processing_errors.append(error)

                    progress_bar.empty()
                    status_text.empty()

                    st.session_state.processed_invoices = processed_invoices

                    if processed_invoices:
                        create_success_message(
                            f"Successfully processed {len(processed_invoices)} invoices!"
                        )

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            create_stats_card(len(processed_invoices), "Total Invoices")
                        with col2:
                            total_amount = sum([inv["amount"] for inv in processed_invoices])
                            create_stats_card(f"₨ {total_amount:,.0f}", "Total Amount")
                        with col3:
                            create_stats_card(len(processing_errors), "Processing Errors")

                        if processing_errors:
                            with st.expander(
                                f"⚠️ Processing Errors ({len(processing_errors)})"
                            ):
                                for error in processing_errors:
                                    st.error(f"• {error}")
                    else:
                        create_error_message("No valid invoices could be processed")

        except Exception as e:
            create_error_message(f"Error reading Excel file: {str(e)}")
            st.info("Please ensure your file is a valid Excel (.xlsx or .xls) format")



   # Action buttons for processed invoices
    if st.session_state.processed_invoices:
        st.markdown("### 🚀 Bulk Invoice Actions")

        col5, col6, col7 = st.columns(3)

       # Add this at the top of your show_excel_invoice_auto() function after the seller check
        # Initialize comprehensive session state for PDF generation
        if "excel_validation_results" not in st.session_state:
            st.session_state.excel_validation_results = None
        if "excel_validated_zip_buffer" not in st.session_state:
            st.session_state.excel_validated_zip_buffer = None
        if "excel_validation_complete" not in st.session_state:
            st.session_state.excel_validation_complete = False

        # Then replace the validation button section with this corrected code:

        with col5:
            if st.button("✅ Validate All Invoices", use_container_width=True, key="excel_validate_all_btn"):
                validation_results = []

                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, invoice_item in enumerate(st.session_state.processed_invoices):
                    status_text.text(
                        f"Validating invoice {idx + 1} of {len(st.session_state.processed_invoices)}"
                    )
                    progress_bar.progress(
                        (idx + 1) / len(st.session_state.processed_invoices)
                    )

                    try:
                        status_code, response = validate_invoice_api(
                            invoice_item["invoice_data"], seller[5]
                        )
                        validation_results.append(
                            {
                                "row_number": invoice_item["row_number"],
                                "buyer_name": invoice_item["buyer_name"],
                                "invoice_data": invoice_item["invoice_data"],
                                "status_code": status_code,
                                "response": response,
                                "success": status_code == 200,
                            }
                        )
                    except Exception as e:
                        validation_results.append(
                            {
                                "row_number": invoice_item["row_number"],
                                "buyer_name": invoice_item["buyer_name"],
                                "invoice_data": invoice_item["invoice_data"],
                                "status_code": None,
                                "response": {"error": str(e)},
                                "success": False,
                            }
                        )

                progress_bar.empty()
                status_text.empty()

                # Store validation results in session state PERMANENTLY
                st.session_state.excel_validation_results = validation_results
                st.session_state.excel_validation_complete = True

                # Force rerun to display results
                st.rerun()

        # Display validation results if they exist (persistent across reruns)
        if st.session_state.excel_validation_complete and st.session_state.excel_validation_results:
            validation_results = st.session_state.excel_validation_results
            
            successful_validations = sum(1 for r in validation_results if r["success"])
            failed_validations = len(validation_results) - successful_validations

            # Display results
            st.markdown("### 📋 Validation Results")

            col_success, col_failed = st.columns(2)
            with col_success:
                create_stats_card(successful_validations, "Successful Validations")
            with col_failed:
                create_stats_card(failed_validations, "Failed Validations")

            if successful_validations > 0:
                create_success_message(
                    f"FBR Validation successful for {successful_validations} invoices!"
                )

                with st.expander(
                    f"✅ Successful Validations ({successful_validations})",
                    expanded=False,
                ):
                    for result in validation_results:
                        if result["success"]:
                            st.success(
                                f"**Row {result['row_number']} - {result['buyer_name']}** ✅"
                            )
                            st.json(result["response"])
                            st.divider()

            if failed_validations > 0:
                create_error_message(
                    f"FBR Validation failed for {failed_validations} invoices"
                )

                with st.expander(
                    f"❌ Validation Failures ({failed_validations})", expanded=False
                ):
                    for result in validation_results:
                        if not result["success"]:
                            st.error(
                                f"**Row {result['row_number']} - {result['buyer_name']}** ❌"
                            )
                            if result["status_code"]:
                                st.write(f"**Status Code:** {result['status_code']}")
                            st.json(result["response"])
                            st.divider()

            # PDF GENERATION SECTION - Persistent
            if successful_validations > 0:
                st.markdown("### 📄 Download Validated Invoices")
                
                pdf_col1, pdf_col2 = st.columns([2, 1])
                
                with pdf_col1:
                    if st.button(
                        "📦 Generate PDFs for Validated Invoices",
                        type="primary",
                        use_container_width=True,
                        key="generate_validated_pdfs_excel_btn"
                    ):
                        try:
                            with st.spinner("⏳ Generating PDF invoices..."):
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()

                                    successful_count = 0
                                    for idx, result in enumerate(validation_results):
                                        if result["success"]:
                                            successful_count += 1
                                            status_text.text(
                                                f"Generating PDF {successful_count} of {successful_validations}"
                                            )
                                            progress_bar.progress(successful_count / successful_validations)

                                            try:
                                                pdf_buffer = generate_invoice_pdf(
                                                    result["invoice_data"], result["response"]
                                                )
                                                safe_buyer_name = "".join(
                                                    c for c in result["buyer_name"]
                                                    if c.isalnum() or c in (" ", "-", "_")
                                                ).rstrip()
                                                filename = f"Invoice_Validated_Row_{result['row_number']}_{safe_buyer_name[:20]}.pdf"
                                                zip_file.writestr(filename, pdf_buffer.getvalue())
                                            except Exception as e:
                                                st.error(
                                                    f"Failed to generate PDF for row {result['row_number']}: {str(e)}"
                                                )

                                    progress_bar.empty()
                                    status_text.empty()

                                zip_buffer.seek(0)
                                st.session_state.excel_validated_zip_buffer = zip_buffer.getvalue()
                                
                        except Exception as e:
                            create_error_message(f"Error generating PDFs: {str(e)}")
                        create_success_message(f"Generated {successful_validations} validated PDF invoices!")

                
                # Show download button if ZIP has been generated (PERSISTENT)
                if st.session_state.excel_validated_zip_buffer:
                    st.success("✅ PDFs generated successfully! Download below:")
                    st.download_button(
                        label="⬇️ Download Validated Invoice PDFs (ZIP)",
                        data=st.session_state.excel_validated_zip_buffer,
                        file_name=f"Invoices_Validated_{seller[1]}_{date.today().strftime('%Y-%m-%d')}.zip",
                        mime="application/zip",
                        key="download_validated_pdfs_excel_btn",
                        use_container_width=True,
                        type="secondary"
                    )
                    
                    # Option to clear and regenerate
                    if st.button("🔄 Regenerate PDFs", key="regenerate_validated_pdfs_btn", help="Click to regenerate the PDF files"):
                        st.session_state.excel_validated_zip_buffer = None
                        st.rerun()
                       


        with col6:
            if st.button(
                "📤 Post All to FBR", use_container_width=True, type="primary"
            ):
                posting_results = []

                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, invoice_item in enumerate(st.session_state.processed_invoices):
                    status_text.text(
                        f"Posting invoice {idx + 1} of {len(st.session_state.processed_invoices)}"
                    )
                    progress_bar.progress(
                        (idx + 1) / len(st.session_state.processed_invoices)
                    )

                    try:
                        status_code, response = post_invoice_api(
                            invoice_item["invoice_data"], seller[5]
                        )
                        posting_results.append(
                            {
                                "row_number": invoice_item["row_number"],
                                "buyer_name": invoice_item["buyer_name"],
                                "invoice_data": invoice_item["invoice_data"],
                                "status_code": status_code,
                                "response": response,
                                "success": status_code == 200,
                            }
                        )
                    except Exception as e:
                        posting_results.append(
                            {
                                "row_number": invoice_item["row_number"],
                                "buyer_name": invoice_item["buyer_name"],
                                "invoice_data": invoice_item["invoice_data"],
                                "status_code": None,
                                "response": {"error": str(e)},
                                "success": False,
                            }
                        )

                progress_bar.empty()
                status_text.empty()

                st.session_state.posting_results = posting_results

                successful_posts = sum(1 for r in posting_results if r["success"])
                failed_posts = len(posting_results) - successful_posts

                st.markdown("### 📤 FBR Posting Results")

                col_success, col_failed = st.columns(2)
                with col_success:
                    create_stats_card(successful_posts, "Successfully Posted")
                with col_failed:
                    create_stats_card(failed_posts, "Failed Posts")

                if successful_posts > 0:
                    create_success_message(
                        f"{successful_posts} invoices posted successfully to FBR!"
                    )

                    with st.expander(
                        f"✅ Successfully Posted Invoices ({successful_posts})",
                        expanded=True,
                    ):
                        for result in posting_results:
                            if result["success"]:
                                st.success(
                                    f"**Row {result['row_number']} - {result['buyer_name']}** ✅"
                                )

                                invoice_number = "N/A"
                                if isinstance(result["response"], dict):
                                    if "invoiceNumber" in result["response"]:
                                        invoice_number = result["response"][
                                            "invoiceNumber"
                                        ]
                                    elif (
                                        "data" in result["response"]
                                        and result["response"]["data"]
                                    ):
                                        invoice_number = result["response"]["data"].get(
                                            "invoiceNumber", "N/A"
                                        )

                                st.write(f"**FBR Invoice Number:** {invoice_number}")
                                st.json(result["response"])
                                st.divider()

                if failed_posts > 0:
                    create_error_message(
                        f"{failed_posts} invoices failed to post to FBR"
                    )

                    with st.expander(
                        f"❌ Failed Posts ({failed_posts})", expanded=True
                    ):
                        for result in posting_results:
                            if not result["success"]:
                                st.error(
                                    f"**Row {result['row_number']} - {result['buyer_name']}** ❌"
                                )
                                if result["status_code"]:
                                    st.write(
                                        f"**Status Code:** {result['status_code']}"
                                    )
                                st.json(result["response"])
                                st.divider()

        with col7:
            if st.session_state.posting_results and any(
                r["success"] for r in st.session_state.posting_results
            ):
                if st.button("📄 Generate PDF Package (Posted)", use_container_width=True, key="post_pdf_excel"):
                    successful_posts = [
                        r for r in st.session_state.posting_results if r["success"]
                    ]

                    if successful_posts:
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(
                            zip_buffer, "w", zipfile.ZIP_DEFLATED
                        ) as zip_file:

                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            for idx, result in enumerate(successful_posts):
                                status_text.text(
                                    f"Generating PDF {idx + 1} of {len(successful_posts)}"
                                )
                                progress_bar.progress((idx + 1) / len(successful_posts))

                                try:
                                    pdf_buffer = generate_invoice_pdf(
                                        result["invoice_data"], result["response"]
                                    )
                                    print(result['invoice_data'])
                                    safe_buyer_name = "".join(
                                        c
                                        for c in result["buyer_name"]
                                        if c.isalnum() or c in (" ", "-", "_")
                                    ).rstrip()
                                    filename = f"Invoice_Posted_Row_{result['row_number']}_{safe_buyer_name[:20]}.pdf"
                                    zip_file.writestr(filename, pdf_buffer.getvalue())

                                except Exception as e:
                                    st.error(
                                        f"Failed to generate PDF for row {result['row_number']}: {str(e)}"
                                    )

                            progress_bar.empty()
                            status_text.empty()

                        zip_buffer.seek(0)

                        st.download_button(
                            label="📦 Download Posted Invoice PDFs (with FBR Data)",
                            data=zip_buffer.getvalue(),
                            file_name=f"Invoices_Posted_{seller[1]}_{date.today().strftime('%Y-%m-%d')}.zip",
                            mime="application/zip",
                            type="secondary",
                            key="post_pdf_download_excel"
                        )

                        create_success_message(
                            f"Generated {len(successful_posts)} posted PDF invoices with FBR confirmation!"
                        )
            else:
                st.info("📄 Validate and post invoices first to generate PDFs")

        
    # Show expected format when no file uploaded
    if uploaded_file is None:
        st.markdown("### 📋 Expected Excel Format")
        st.info(
            "🤖 **Smart Detection:** The system automatically recognizes these common column patterns:"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
            <div class="custom-card">
                <h4 style="color: var(--text-primary);">🔍 Auto-Detected Patterns</h4>
                <div style="font-size: 0.9rem; line-height: 1.6; color: var(--text-primary);">
                    <strong style="color: var(--text-primary);">Buyer Information:</strong><br>
                    • Registration No, Buyer Registration No, NTN, CNIC<br>
                    • Name, Buyer Name, Business Name, Customer Name<br>
                    • Type, Registration Type, Registered/Unregistered<br>
                    • Province, Buyer Province, State<br>
                    • Address, Buyer Address, Destination of Supply
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
            <div class="custom-card">
                <h4 style="color: var(--text-primary);">💰 Financial Fields</h4>
                <div style="font-size: 0.9rem; line-height: 1.6; color: var(--text-primary);">
                    <strong style="color: var(--text-primary);">Invoice & Values:</strong><br>
                    • Document Date, Invoice Date, Date<br>
                    • Document Number, Invoice Number, Reference<br>
                    • HS Code, Commodity Code, Product Code<br>
                    • Value Excluding Sales Tax, Base Value<br>
                    • Sales Tax, Tax Amount, ST Amount<br>
                    • Rate, Tax Rate, Percentage
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Sample data format
        st.markdown("### 📄 Sample Data Format")
        sample_data = {
            "invoiceType": ["Sale Invoice"],
            "invoiceDate": ["8/21/2025"],
            "buyerNTNC": ["Un-Register"],
            "buyerBusinessName": ["Un-Register"],
            "buyerProvince": ["Sindh"],
            "buyerAddress": ["Karachi"],
            "buyerRegistrationType": ["Unregistered"],
            "invoiceRefNo": ["SN002"],
            "scenarioId": ["0101.21"],
            "item_1_hsCode": ["Test Product"],
            "item_1_productDescription": ["18%"],
            "item_1_rate": ["Num"
            "bers, pieces, units"],
            "item_1_uoM": ["1"],
            "item_1_quantity": ["1000"],
            "item_1_valueSalesExcludingST": ["180"],
        }

        sample_df = pd.DataFrame(sample_data)

        st.markdown(
            """
        <div class="custom-card">
        """,
            unsafe_allow_html=True,
        )

        st.dataframe(sample_df, use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-top: 2rem;">
            <h3 style="margin: 0;">🎯 Ready to Process</h3>
            <p style="margin: 0.5rem 0 0 0;">Just upload your Excel file - the system will handle column detection automatically!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# Main execution
if check_password():
    main()
else:
    st.stop()
