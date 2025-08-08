import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Optional
import os

from app.core.security.config import settings

def create_otp_html_template(otp_code: str, otp_type: str, company_name: str = "Ваша Компания") -> str:
    
    if otp_type == "registration":
        title = "Добро пожаловать!"
        subtitle = "Подтвердите свою регистрацию"
        message = "Спасибо за регистрацию! Введите код ниже, чтобы подтвердить свой email:"
    else:
        title = "Код для входа"
        subtitle = "Войдите в свой аккаунт"
        message = "Используйте код ниже для входа в систему:"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333333;
                background-color: #f5f7fa;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            
            .header h1 {{
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 8px;
            }}
            
            .header p {{
                font-size: 16px;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .message {{
                font-size: 16px;
                color: #555555;
                margin-bottom: 30px;
                line-height: 1.7;
            }}
            
            .otp-container {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 12px;
                padding: 25px;
                margin: 30px 0;
                display: inline-block;
            }}
            
            .otp-code {{
                font-size: 36px;
                font-weight: bold;
                color: white;
                letter-spacing: 8px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .expiry-info {{
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
                margin: 25px 0;
                font-size: 14px;
                color: #856404;
            }}
            
            .security-notice {{
                background-color: #e8f4fd;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 25px 0;
                border-radius: 4px;
                text-align: left;
            }}
            
            .security-notice h3 {{
                color: #2980b9;
                font-size: 16px;
                margin-bottom: 8px;
            }}
            
            .security-notice p {{
                font-size: 14px;
                color: #555;
                line-height: 1.5;
            }}
            
            .footer {{
                background-color: #f8f9fa;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e9ecef;
            }}
            
            .footer p {{
                font-size: 14px;
                color: #6c757d;
                margin-bottom: 10px;
            }}
            
            .social-links {{
                margin-top: 20px;
            }}
            
            .social-links a {{
                display: inline-block;
                margin: 0 10px;
                color: #667eea;
                text-decoration: none;
                font-size: 14px;
            }}
            
            @media only screen and (max-width: 600px) {{
                .email-container {{
                    margin: 0;
                    border-radius: 0;
                }}
                
                .header {{
                    padding: 30px 20px;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .otp-code {{
                    font-size: 28px;
                    letter-spacing: 4px;
                }}
                
                .footer {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            
            <div class="content">
                <p class="message">{message}</p>
                
                <div class="otp-container">
                    <div class="otp-code">{otp_code}</div>
                </div>
                
                <div class="expiry-info">
                    <strong>⏰ Код действителен {settings.OTP_EXPIRE_MINUTES} минут</strong>
                </div>
                
                <div class="security-notice">
                    <h3>🔒 Безопасность</h3>
                    <p>
                        {"Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо." if otp_type == "registration" else "Если вы не пытались войти в систему, немедленно смените пароль и свяжитесь с нами."}
                    </p>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>{company_name}</strong></p>
                <p>Это автоматическое сообщение, не отвечайте на него.</p>
                <div class="social-links">
                    <a href="#" target="_blank">Техподдержка</a>
                    <a href="#" target="_blank">Политика конфиденциальности</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template

def send_email_html(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if text_body:
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(part1)
        
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part2)
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        if settings.SMTP_TLS:
            server.starttls()
            
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
        server.send_message(msg)
        server.quit()
        
        print(f"HTML Email успешно отправлен на {to_email}")
        return True
        
    except Exception as e:
        print(f"Ошибка отправки HTML email на {to_email}: {e}")
        return False

def send_otp_email(to_email: str, otp_code: str, otp_type: str, company_name: str = "Ваша Компания") -> bool:
    
    html_body = create_otp_html_template(otp_code, otp_type, company_name)
    
    if otp_type == "registration":
        subject = "Подтверждение регистрации"
        text_body = f"""
Добро пожаловать в {company_name}!

Для завершения регистрации введите код подтверждения: {otp_code}

Код действителен в течение {settings.OTP_EXPIRE_MINUTES} минут.

Если вы не регистрировались на нашем сайте, игнорируйте это сообщение.

--
{company_name}
Это автоматическое сообщение, не отвечайте на него.
        """
    else:
        subject = "Код для входа в систему"
        text_body = f"""
Код для входа в систему: {otp_code}

Код действителен в течение {settings.OTP_EXPIRE_MINUTES} минут.

Если вы не пытались войти в систему, немедленно смените пароль.

--
{company_name}
Это автоматическое сообщение, не отвечайте на него.
        """
    
    return send_email_html(to_email, subject, html_body, text_body)

def create_welcome_email_template(user_name: str, company_name: str = "Ваша Компания") -> str:
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Добро пожаловать!</title>
        <style>
            /* Стили аналогичные OTP письму */
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .email-container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 40px 30px; text-align: center; color: white; }}
            .content {{ padding: 40px 30px; }}
            .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>🎉 Добро пожаловать, {user_name}!</h1>
                <p>Ваш аккаунт успешно создан</p>
            </div>
            <div class="content">
                <p>Спасибо за регистрацию в {company_name}! Теперь вы можете пользоваться всеми возможностями нашего сервиса.</p>
                <a href="#" class="cta-button">Начать использование</a>
                <p>Если у вас есть вопросы, мы всегда готовы помочь!</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def create_password_change_email_template(otp_code: str, company_name: str = "Ваша Компания") -> str:
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Смена пароля</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f7fa; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); padding: 40px; text-align: center; color: white; }}
            .content {{ padding: 40px; text-align: center; }}
            .otp-code {{ font-size: 36px; font-weight: bold; color: #ff6b6b; letter-spacing: 8px; background: #fff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #ff6b6b; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Смена пароля</h1>
                <p>Подтвердите изменение пароля</p>
            </div>
            <div class="content">
                <p>Вы запросили смену пароля. Используйте код ниже для подтверждения:</p>
                <div class="otp-code">{otp_code}</div>
                <div class="warning">
                    <strong>⚠️ Безопасность:</strong><br>
                    Если вы не запрашивали смену пароля, немедленно свяжитесь с поддержкой.
                </div>
                <p>Код действителен {settings.OTP_EXPIRE_MINUTES} минут.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template


def send_otp_email_updated(to_email: str, otp_code: str, otp_type: str, company_name: str = "Ваша Компания") -> bool:
    """Обновленная функция отправки OTP с поддержкой password_change"""
    
    if otp_type == "password_change":
        html_body = create_password_change_email_template(otp_code, company_name)
        subject = "Подтверждение смены пароля"
        text_body = f"""
Код для смены пароля: {otp_code}

Если вы не запрашивали смену пароля, немедленно свяжитесь с поддержкой.

Код действителен {settings.OTP_EXPIRE_MINUTES} минут.
        """
    elif otp_type == "registration":
        html_body = create_otp_html_template(otp_code, otp_type, company_name)
        subject = "Подтверждение регистрации"
        text_body = f"""
Добро пожаловать в {company_name}!

Для завершения регистрации введите код подтверждения: {otp_code}

Код действителен в течение {settings.OTP_EXPIRE_MINUTES} минут.
        """
    else:  # login
        html_body = create_otp_html_template(otp_code, otp_type, company_name)
        subject = "Код для входа в систему"
        text_body = f"""
Код для входа в систему: {otp_code}

Код действителен в течение {settings.OTP_EXPIRE_MINUTES} минут.
        """
    
    return send_email_html(to_email, subject, html_body, text_body)