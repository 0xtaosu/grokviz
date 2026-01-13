"""Mock email generator for testing GrokViz workflow."""

import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MockEmailGenerator:
    """Generate realistic mock Grok daily emails for testing."""

    def generate_json_attachment(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate realistic JSON data for Grok daily report.

        Args:
            date: Report date (default: today)

        Returns:
            JSON data structure
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        return {
            "date": date,
            "consensus_opportunities": [
                {
                    "name": "Bitcoin ETF Inflows Continue",
                    "logic": "Sustained institutional demand driving price momentum",
                    "evidence": "BlackRock IBIT saw $500M inflow on Jan 12, marking 3-day streak",
                    "heat_score": 85
                },
                {
                    "name": "Ethereum Shanghai Upgrade Success",
                    "logic": "Successful network upgrade boosts confidence",
                    "evidence": "Staking withdrawals processed smoothly, network stability maintained",
                    "heat_score": 78
                },
                {
                    "name": "Stablecoin Market Cap Growth",
                    "logic": "Growing stablecoin supply indicates capital inflow to crypto",
                    "evidence": "Total stablecoin market cap reached $140B, up 8% MoM",
                    "heat_score": 72
                }
            ],
            "non_consensus_opportunities": [
                {
                    "name": "Layer 2 TVL Explosion",
                    "logic": "User migration to L2s accelerating despite low mainstream awareness",
                    "evidence": "Arbitrum TVL up 40% in 2 weeks, but search interest remains flat",
                    "heat_score": 82
                },
                {
                    "name": "DeFi Real Yield Protocols",
                    "logic": "Revenue-generating protocols gaining traction quietly",
                    "evidence": "GMX generated $2.5M fees last week, distributed to token holders",
                    "heat_score": 76
                },
                {
                    "name": "Emerging Market Crypto Adoption",
                    "logic": "Retail adoption in developing countries accelerating",
                    "evidence": "Nigeria and India seeing 300% YoY growth in P2P trading volume",
                    "heat_score": 70
                }
            ],
            "macro_indicators": {
                "btc_dominance": 52.3,
                "fear_greed_index": 68,
                "total_market_cap": "2.1T",
                "defi_tvl": "85B",
                "nft_volume_24h": "45M"
            }
        }

    def generate_html_body(self, json_data: Dict[str, Any]) -> str:
        """
        Generate HTML email body from JSON data.

        Args:
            json_data: Report data

        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   padding: 30px; text-align: center; color: white; }}
        .content {{ padding: 20px; max-width: 800px; margin: 0 auto; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ font-size: 24px; font-weight: bold; margin-bottom: 15px;
                         border-left: 4px solid #667eea; padding-left: 15px; }}
        .opportunity {{ background: #f7f7f7; padding: 15px; margin: 10px 0;
                       border-radius: 8px; }}
        .opp-name {{ font-size: 18px; font-weight: bold; color: #667eea; }}
        .opp-logic {{ margin: 8px 0; color: #555; }}
        .opp-evidence {{ font-style: italic; color: #777; font-size: 14px; }}
        .heat-score {{ display: inline-block; background: #ff6b6b; color: white;
                      padding: 3px 10px; border-radius: 12px; font-size: 12px;
                      font-weight: bold; }}
        .macro {{ background: #e3f2fd; padding: 15px; border-radius: 8px; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Grok Crypto Daily Digest</h1>
        <p>{json_data['date']}</p>
    </div>

    <div class="content">
        <div class="section">
            <div class="section-title">📊 共识机会 | Consensus Opportunities</div>
"""

        for opp in json_data['consensus_opportunities']:
            html += f"""
            <div class="opportunity">
                <div class="opp-name">{opp['name']}
                    <span class="heat-score">🔥 {opp['heat_score']}</span>
                </div>
                <div class="opp-logic"><strong>逻辑:</strong> {opp['logic']}</div>
                <div class="opp-evidence"><strong>证据:</strong> {opp['evidence']}</div>
            </div>
"""

        html += """
        </div>

        <div class="section">
            <div class="section-title">💎 非共识机会 | Non-Consensus Opportunities</div>
"""

        for opp in json_data['non_consensus_opportunities']:
            html += f"""
            <div class="opportunity">
                <div class="opp-name">{opp['name']}
                    <span class="heat-score">💡 {opp['heat_score']}</span>
                </div>
                <div class="opp-logic"><strong>逻辑:</strong> {opp['logic']}</div>
                <div class="opp-evidence"><strong>证据:</strong> {opp['evidence']}</div>
            </div>
"""

        macro = json_data['macro_indicators']
        html += f"""
        </div>

        <div class="section">
            <div class="section-title">📈 市场宏观 | Macro Indicators</div>
            <div class="macro">
                <p><strong>BTC Dominance:</strong> {macro.get('btc_dominance', 'N/A')}%</p>
                <p><strong>Fear & Greed Index:</strong> {macro.get('fear_greed_index', 'N/A')}</p>
                <p><strong>Total Market Cap:</strong> ${macro.get('total_market_cap', 'N/A')}</p>
                <p><strong>DeFi TVL:</strong> ${macro.get('defi_tvl', 'N/A')}</p>
                <p><strong>NFT Volume (24h):</strong> ${macro.get('nft_volume_24h', 'N/A')}</p>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Powered by Grok AI | Daily Crypto Intelligence</p>
        <p>This is an automated report. For more information, visit our website.</p>
    </div>
</body>
</html>
"""
        return html

    def generate_mock_email(
        self,
        include_json: bool = True,
        include_html: bool = True,
        date: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Generate a complete mock email with attachments.

        Args:
            include_json: Include JSON attachment
            include_html: Include HTML body
            date: Report date (default: today)

        Returns:
            MIME multipart email message
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Generate data
        json_data = self.generate_json_attachment(date)

        # Create email
        msg = MIMEMultipart("mixed")
        msg["From"] = "grok@example.com"
        msg["Subject"] = f"Grok Crypto Daily Digest - {date}"
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        # Add HTML body
        if include_html:
            html_body = self.generate_html_body(json_data)
            html_part = MIMEText(html_body, "html", "utf-8")
            msg.attach(html_part)
        else:
            # Plain text fallback
            text_part = MIMEText(f"Grok Daily Report - {date}\n\nSee attachment for details.", "plain")
            msg.attach(text_part)

        # Add JSON attachment
        if include_json:
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            json_part = MIMEBase("application", "json")
            json_part.set_payload(json_str.encode("utf-8"))
            encoders.encode_base64(json_part)
            json_part.add_header(
                "Content-Disposition",
                f"attachment; filename=grok_daily_{date}.json"
            )
            msg.attach(json_part)

        return msg

    def send_mock_email_to_inbox(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        to_email: str,
        include_json: bool = True,
        include_html: bool = True
    ) -> None:
        """
        Send mock email to actual inbox for integration testing.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
            to_email: Recipient email address
            include_json: Include JSON attachment
            include_html: Include HTML body

        Raises:
            Exception: If email sending fails
        """
        msg = self.generate_mock_email(include_json, include_html)
        msg["To"] = to_email

        try:
            logger.info(f"Sending mock email to {to_email}")

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            logger.info("Mock email sent successfully")

        except Exception as e:
            logger.error(f"Failed to send mock email: {e}")
            raise
