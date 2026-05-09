"""
Email service for VitaChain using Brevo API
"""

import httpx
import os
from typing import Optional
from datetime import datetime, timedelta
import secrets
import urllib.parse

from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import EmailRequest, VerificationEmailData, UserRole, MagicLinkEmailData, PasswordResetEmailData


class EmailService:
    """Email service using Brevo API"""
    
    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.base_url = "https://api.brevo.com/v3"
        self.timeout = 30.0
        
    async def send_verification_email(self, email_data: VerificationEmailData) -> bool:
        """
        Send verification email to user
        
        Args:
            email_data: Verification email data
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create email content with professional template
            html_content = self._create_verification_template(email_data)
            
            email_request = EmailRequest(
                to=[{"email": email_data.recipient_email}],
                subject="Verify your VitaChain account",
                html_content=html_content
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    headers={"api-key": self.api_key},
                    json=email_request.dict(exclude_none=True)
                )
                
                if response.status_code == 201:
                    logger.info(
                        "Verification email sent successfully",
                        email=email_data.recipient_email,
                        role=email_data.role
                    )
                    return True
                else:
                    logger.error(
                        "Failed to send verification email",
                        status_code=response.status_code,
                        response_text=response.text,
                        email=email_data.recipient_email
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(
                "Email service timeout",
                email=email_data.recipient_email
            )
            return False
        except Exception as e:
            logger.error(
                "Email service error",
                error=str(e),
                email=email_data.recipient_email
            )
            return False
    
    async def send_magic_link_email(self, email_data: MagicLinkEmailData) -> bool:
        """
        Send magic link email to user
        
        Args:
            email_data: Magic link email data
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create email content with magic link template
            html_content = self._create_magic_link_template(email_data)
            
            email_request = EmailRequest(
                to=[{"email": email_data.recipient_email}],
                subject="VitaChain - Votre lien de connexion magique",
                html_content=html_content
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    headers={"api-key": self.api_key},
                    json=email_request.dict(exclude_none=True)
                )
                
                if response.status_code == 201:
                    logger.info(
                        "Magic link email sent successfully",
                        email=email_data.recipient_email,
                        role=email_data.role
                    )
                    return True
                else:
                    logger.error(
                        "Failed to send magic link email",
                        status_code=response.status_code,
                        response_text=response.text,
                        email=email_data.recipient_email
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(
                "Email service timeout for magic link",
                email=email_data.recipient_email
            )
            return False
        except Exception as e:
            logger.error(
                "Email service error for magic link",
                error=str(e),
                email=email_data.recipient_email
            )
            return False
    
    def _create_verification_template(self, data: VerificationEmailData) -> str:
        """
        Create professional email template for Moroccan market
        
        Args:
            data: Verification email data
            
        Returns:
            HTML email template
        """
        # Professional template with Arabic/French support for Moroccan market
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VitaChain - Verify Your Account</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .tagline {{
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #27ae60;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 12px;
                    margin-top: 30px;
                }}
                .role-badge {{
                    background-color: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🌱 VitaChain</div>
                    <div class="tagline">La chaîne agri-alimentaire marocaine</div>
                </div>
                
                <div class="content">
                    <h2>Bienvenue {data.user_name}!</h2>
                    
                    <p>Merci de vous être inscrit sur VitaChain en tant que 
                    <span class="role-badge">{data.role}</span>.</p>
                    
                    <p>Pour activer votre compte et accéder à notre plateforme, 
                    veuillez cliquer sur le bouton ci-dessous pour vérifier votre adresse email:</p>
                    
                    <div style="text-align: center;">
                        <a href="{data.verification_link}" class="button">
                            Vérifier mon email
                        </a>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>Ce lien expirera dans 24 heures</li>
                        <li>Si vous n'avez pas créé de compte VitaChain, ignorez cet email</li>
                        <li>Assurez-vous que votre email reste sécurisé</li>
                    </ul>
                    
                    <p>Une fois votre email vérifié, vous pourrez:</p>
                    <ul>
                        {self._get_role_benefits(data.role)}
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par VitaChain.</p>
                    <p>© 2026 VitaChain. Tous droits réservés.</p>
                    <p>Marché marocain • Solutions agricoles intelligentes</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template
    
    def _get_role_benefits(self, role: UserRole) -> str:
        """Get role-specific benefits for email template"""
        benefits = {
            UserRole.FARMER: """
                <li>Enregistrer vos dispositifs IoT KATARA</li>
                <li>Surveiller vos cultures en temps réel</li>
                <li>Recevoir des recommandations agronomiques</li>
                <li>Vendre vos produits sur FARMARKET</li>
            """,
            UserRole.RESTAURANT: """
                <li>Acheter des produits agricoles directement</li>
                <li>Vendre vos repas invendus sur SECONDSERVE</li>
                <li>Gérer les réservations et codes de retrait</li>
                <li>Accéder aux solutions IoT BOTABA9A</li>
            """,
            UserRole.CITIZEN: """
                <li>Découvrir des repas disponibles près de chez vous</li>
                <li>Réserver et collecter des repas à prix réduit</li>
                <li>Soutenir la réduction du gaspillage alimentaire</li>
                <li>Accéder aux offres locales</li>
            """,
            UserRole.ADMIN: """
                <li>Gérer les utilisateurs et leurs permissions</li>
                <li>Surveiller la santé du système</li>
                <li>Accéder aux statistiques de la plateforme</li>
                <li>Administrer tous les modules VitaChain</li>
            """
        }
        return benefits.get(role, "")
    
    def _create_magic_link_template(self, data: MagicLinkEmailData) -> str:
        """
        Create magic link email template for passwordless authentication
        
        Args:
            data: Magic link email data
            
        Returns:
            HTML email template
        """
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VitaChain - Lien de Connexion Magique</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .tagline {{
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .magic-button {{
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 18px 35px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    margin: 25px 0;
                    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
                    transition: all 0.3s ease;
                }}
                .magic-button:hover {{
                    background-color: #2980b9;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
                }}
                .security-info {{
                    background-color: #ecf0f1;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #3498db;
                }}
                .expiry-warning {{
                    color: #e74c3c;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 12px;
                    margin-top: 30px;
                }}
                .role-badge {{
                    background-color: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .icon {{
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icon">🔐</div>
                    <div class="logo">🌱 VitaChain</div>
                    <div class="tagline">La chaîne agri-alimentaire marocaine</div>
                </div>
                
                <div class="content">
                    <h2>Bonjour {data.user_name}!</h2>
                    
                    <p>Vous avez demandé une connexion sécurisée sans mot de passe sur VitaChain 
                    en tant que <span class="role-badge">{data.role}</span>.</p>
                    
                    <p>Cliquez sur le bouton ci-dessous pour vous connecter instantanément:</p>
                    
                    <div style="text-align: center;">
                        <a href="{data.magic_link}" class="magic-button" id="magic-link-button">
                            🔗 Me connecter maintenant
                        </a>
                    </div>
                    
                    <div class="security-info">
                        <h3>🛡️ Informations de sécurité</h3>
                        <ul>
                            <li><strong class="expiry-warning">Ce lien expirera dans {data.expires_in_minutes} minutes</strong></li>
                            <li>Ce lien ne peut être utilisé qu'une seule fois</li>
                            <li>Si vous n'avez pas demandé cette connexion, ignorez cet email</li>
                            <li>Ne partagez jamais ce lien avec d'autres personnes</li>
                        </ul>
                    </div>
                    
                    <p><strong>Après votre connexion, vous pourrez:</strong></p>
                    <ul>
                        {self._get_role_benefits(data.role)}
                    </ul>
                    
                    <p><em>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur:</em></p>
                    <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px;">
                        {data.magic_link}
                    </p>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par VitaChain.</p>
                    <p>© 2026 VitaChain. Tous droits réservés.</p>
                    <p>Marché marocain • Solutions agricoles intelligentes</p>
                    <p>Pour toute assistance, contactez notre support technique.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template
    
    async def send_password_reset_email(self, email_data: PasswordResetEmailData) -> bool:
        """
        Send password reset email to user
        
        Args:
            email_data: Password reset email data
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create email content with password reset template
            html_content = self._create_password_reset_template(email_data)
            
            email_request = EmailRequest(
                to=[{"email": email_data.recipient_email}],
                subject="VitaChain - Réinitialisation de votre mot de passe",
                html_content=html_content
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    headers={"api-key": self.api_key},
                    json=email_request.dict(exclude_none=True)
                )
                
                if response.status_code == 201:
                    logger.info(
                        "Password reset email sent successfully",
                        email=email_data.recipient_email,
                        role=email_data.role
                    )
                    return True
                else:
                    logger.error(
                        "Failed to send password reset email",
                        status_code=response.status_code,
                        response_text=response.text,
                        email=email_data.recipient_email
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(
                "Email service timeout for password reset",
                email=email_data.recipient_email
            )
            return False
        except Exception as e:
            logger.error(
                "Email service error for password reset",
                error=str(e),
                email=email_data.recipient_email
            )
            return False
    
    def _create_password_reset_template(self, data: PasswordResetEmailData) -> str:
        """
        Create password reset email template
        
        Args:
            data: Password reset email data
            
        Returns:
            HTML email template
        """
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VitaChain - Réinitialisation du mot de passe</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .tagline {{
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .reset-button {{
                    display: inline-block;
                    background-color: #e74c3c;
                    color: white;
                    padding: 18px 35px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    margin: 25px 0;
                    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
                    transition: all 0.3s ease;
                }}
                .reset-button:hover {{
                    background-color: #c0392b;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
                }}
                .security-info {{
                    background-color: #fef5e7;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #e74c3c;
                }}
                .expiry-warning {{
                    color: #e74c3c;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 12px;
                    margin-top: 30px;
                }}
                .role-badge {{
                    background-color: #e74c3c;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .icon {{
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
                .password-requirements {{
                    background-color: #ecf0f1;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .password-requirements ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .password-requirements li {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icon">🔐</div>
                    <div class="logo">🌱 VitaChain</div>
                    <div class="tagline">La chaîne agri-alimentaire marocaine</div>
                </div>
                
                <div class="content">
                    <h2>Bonjour {data.user_name}!</h2>
                    
                    <p>Vous avez demandé la réinitialisation de votre mot de passe VitaChain 
                    pour votre compte <span class="role-badge">{data.role}</span>.</p>
                    
                    <p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe:</p>
                    
                    <div style="text-align: center;">
                        <a href="{data.reset_link}" class="reset-button" id="reset-password-button">
                            🔑 Réinitialiser mon mot de passe
                        </a>
                    </div>
                    
                    <div class="security-info">
                        <h3>🛡️ Informations de sécurité importantes</h3>
                        <ul>
                            <li><strong class="expiry-warning">Ce lien expirera dans {data.expires_in_hours} heure</strong></li>
                            <li>Ce lien ne peut être utilisé qu'une seule fois</li>
                            <li>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email</li>
                            <li>Ne partagez jamais ce lien avec d'autres personnes</li>
                        </ul>
                    </div>
                    
                    <div class="password-requirements">
                        <h3>📝 Exigences pour le nouveau mot de passe:</h3>
                        <ul>
                            <li>✅ Au moins 8 caractères</li>
                            <li>✅ Au moins une lettre majuscule (A-Z)</li>
                            <li>✅ Au moins une lettre minuscule (a-z)</li>
                            <li>✅ Au moins un chiffre (0-9)</li>
                            <li>💡 Recommandé: Caractères spéciaux (!@#$%^&*)</li>
                        </ul>
                    </div>
                    
                    <p><em>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur:</em></p>
                    <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px;">
                        {data.reset_link}
                    </p>
                    
                    <p><strong>Après la réinitialisation:</strong></p>
                    <ul>
                        {self._get_role_benefits(data.role)}
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par VitaChain.</p>
                    <p>© 2026 VitaChain. Tous droits réservés.</p>
                    <p>Marché marocain • Solutions agricoles intelligentes</p>
                    <p>Pour toute assistance, contactez notre support technique.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template


# Global email service instance
email_service = EmailService()
