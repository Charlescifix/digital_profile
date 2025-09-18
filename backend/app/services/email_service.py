"""Email service for sending CV and notifications."""

import aiosmtplib
import aiofiles
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EmailService:
    """Service for sending emails with CV attachments."""
    
    def __init__(self):
        self.smtp_host = settings.EMAIL_SMTP_HOST
        self.smtp_port = settings.EMAIL_SMTP_PORT
        self.smtp_user = settings.EMAIL_SMTP_USER
        self.smtp_password = settings.EMAIL_SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachment_path: Optional[str] = None
    ) -> bool:
        """Send email with optional attachment."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachment if provided
            if attachment_path and Path(attachment_path).exists():
                async with aiofiles.open(attachment_path, mode='rb') as file:
                    attachment_data = await file.read()
                
                attachment = MIMEApplication(attachment_data, _subtype='pdf')
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename='Charles_Nwankpa_CV.pdf'
                )
                message.attach(attachment)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password,
            )
            
            logger.info("Email sent successfully", to_email=to_email, subject=subject)
            return True
            
        except Exception as e:
            logger.error("Error sending email", error=str(e), to_email=to_email)
            return False
    
    async def send_cv_email(
        self,
        to_email: str,
        name: str,
        company: Optional[str] = None,
        purpose: Optional[str] = None
    ) -> bool:
        """Send CV email to the requestor."""
        
        subject = "Charles Nwankpa - AI Product Engineer CV"
        
        # Generate personalized email content
        html_content = self._generate_cv_email_html(name, company, purpose)
        text_content = self._generate_cv_email_text(name, company, purpose)
        
        # Send email with CV attachment
        success = await self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachment_path=settings.CV_FILE_PATH
        )
        
        if success:
            logger.info("CV email sent", to_email=to_email, name=name, company=company)
        else:
            logger.error("Failed to send CV email", to_email=to_email, name=name)
        
        return success
    
    def _generate_cv_email_html(
        self,
        name: str,
        company: Optional[str] = None,
        purpose: Optional[str] = None
    ) -> str:
        """Generate HTML email content for CV delivery."""
        
        company_text = f" at {company}" if company else ""
        purpose_text = f"<p><strong>Your stated purpose:</strong> {purpose}</p>" if purpose else ""
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Charles Nwankpa - CV</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 14px; color: #64748b; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; margin: 10px 5px; }}
        .highlight {{ background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }}
        ul {{ padding-left: 0; }}
        li {{ list-style: none; margin: 8px 0; }}
        li:before {{ content: "✓"; color: #10b981; font-weight: bold; margin-right: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Charles Nwankpa</h1>
            <p>AI Product Engineer • Applied ML Engineer • RAG Systems Architect</p>
        </div>
        
        <div class="content">
            <h2>Dear {name},</h2>
            
            <p>Thank you for your interest in my AI/ML engineering services{company_text}.</p>
            
            {purpose_text}
            
            <p>As requested, please find my CV attached. This document outlines my experience in:</p>
            
            <ul>
                <li>Production ML/AI systems and enterprise architecture</li>
                <li>RAG architecture and LLM implementation</li>
                <li>Enterprise-grade solution development</li>
                <li>Strategic AI consulting and executive training</li>
                <li>FastAPI, Django, PostgreSQL, and AWS/GCP</li>
            </ul>
            
            <div class="highlight">
                <p><strong>What sets me apart:</strong> I bridge the gap between AI capability and business value through modular, scalable solutions that grow with your business.</p>
            </div>
            
            <h3>Next Steps:</h3>
            <p>I'd love to discuss how I can help transform your AI ambitions into production-ready solutions:</p>
            
            <div style="text-align: center; margin: 25px 0;">
                <a href="{settings.CALENDLY_URL}" class="btn">📅 Book Discovery Call</a>
                <a href="{settings.LINKEDIN_URL}" class="btn">💼 Connect on LinkedIn</a>
            </div>
            
            <p>Looking forward to exploring collaboration opportunities with you.</p>
            
            <p>Best regards,<br>
            <strong>Charles Nwankpa</strong><br>
            AI Product Engineer<br>
            📍 London, UK</p>
        </div>
        
        <div class="footer">
            <p>This email was sent in response to your CV request from charles-ai.up.railway.app</p>
            <p>Available for: Fractional AI/ML engineering • Strategic consulting • Executive training • Full-time opportunities</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_cv_email_text(
        self,
        name: str,
        company: Optional[str] = None,
        purpose: Optional[str] = None
    ) -> str:
        """Generate plain text email content for CV delivery."""
        
        company_text = f" at {company}" if company else ""
        purpose_text = f"Your stated purpose: {purpose}\\n\\n" if purpose else ""
        
        return f"""
Dear {name},

Thank you for your interest in my AI/ML engineering services{company_text}.

{purpose_text}As requested, please find my CV attached. This document outlines my experience in:

• Production ML/AI systems and enterprise architecture
• RAG architecture and LLM implementation  
• Enterprise-grade solution development
• Strategic AI consulting and executive training
• FastAPI, Django, PostgreSQL, and AWS/GCP

What sets me apart: I bridge the gap between AI capability and business value through modular, scalable solutions that grow with your business.

Next Steps:
- Book a discovery call: {settings.CALENDLY_URL}
- Connect on LinkedIn: {settings.LINKEDIN_URL}
- Explore my projects: https://charles-ai.up.railway.app

Looking forward to exploring collaboration opportunities with you.

Best regards,
Charles Nwankpa
AI Product Engineer
📍 London, UK

---
Available for: Fractional AI/ML engineering • Strategic consulting • Executive training • Full-time opportunities
        """
    
    async def send_admin_notification(
        self,
        lead_data: dict
    ) -> bool:
        """Send notification to admin about new CV request."""
        
        subject = f"New CV Request: {lead_data['name']} ({lead_data.get('company', 'No company')})"
        
        html_content = f"""
        <h2>New CV Request Received</h2>
        <p><strong>Name:</strong> {lead_data['name']}</p>
        <p><strong>Email:</strong> {lead_data['email']}</p>
        <p><strong>Phone:</strong> {lead_data['phone']}</p>
        <p><strong>Company:</strong> {lead_data.get('company', 'Not specified')}</p>
        <p><strong>Role:</strong> {lead_data.get('role', 'Not specified')}</p>
        <p><strong>Purpose:</strong> {lead_data.get('purpose', 'Not specified')}</p>
        <p><strong>IP Address:</strong> {lead_data.get('ip_address', 'Unknown')}</p>
        <p><strong>Timestamp:</strong> {lead_data.get('created_at', 'Unknown')}</p>
        """
        
        return await self._send_email(
            to_email=self.from_email,  # Send to admin
            subject=subject,
            html_content=html_content
        )